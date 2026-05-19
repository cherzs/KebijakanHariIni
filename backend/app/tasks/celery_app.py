import uuid
import logging
from celery import Celery
from ..core.config import Settings

settings = Settings()

logger = logging.getLogger(__name__)

celery_app = Celery(
    "kawalkebijakan",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)


@celery_app.task(bind=True)
def process_policy_ai(self, policy_id: str, force: bool = False):
    from ..core.database import SessionLocal
    from ..models.models import Policy
    from ..services.ai_processor import (
        summarize_policy,
        classify_category,
        detect_status,
        explain_impact,
        generate_simple_explanation,
    )

    db = SessionLocal()
    try:
        policy = db.get(Policy, uuid.UUID(policy_id))
        if not policy:
            return {"status": "error", "message": "Policy not found"}

        sources = policy.sources if policy.sources else []
        sources_text = "\n".join([f"- {s.title} ({s.url})" for s in sources])

        if not policy.summary_30sec or force:
            policy.summary_30sec = summarize_policy(policy.title, sources)

        if not policy.simple_explanation or force:
            policy.simple_explanation = generate_simple_explanation(policy.title, sources)

        if not policy.impact_explanation or force:
            policy.impact_explanation = explain_impact(policy.title, sources)

        db.commit()
        return {"status": "completed", "policy_id": policy_id}

    except Exception as e:
        logger.error(f"AI processing error for policy {policy_id}: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def run_rss_scraper(self):
    from ..core.database import SessionLocal
    from ..scrapers.rss_scraper import RSSScraper

    db = SessionLocal()
    try:
        scraper = RSSScraper()
        results = scraper.scrape_all(db)
        logger.info(f"RSS scrape results: {results}")
        return {"status": "completed", "results": results}
    except Exception as e:
        logger.error(f"RSS scraper error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def run_jdih_setneg_scraper(self):
    from ..core.database import SessionLocal
    from ..scrapers.jdih_scraper import JDIHSetnegScraper

    db = SessionLocal()
    try:
        scraper = JDIHSetnegScraper()
        results = scraper.scrape_regulations(db)
        logger.info(f"JDIH Setneg scrape results: {results}")
        return {"status": "completed", "results": results}
    except Exception as e:
        logger.error(f"JDIH Setneg scraper error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def run_jdih_bpk_scraper(self):
    from ..core.database import SessionLocal
    from ..scrapers.jdih_bpk_scraper import JDIHBPKScraper

    db = SessionLocal()
    try:
        scraper = JDIHBPKScraper()
        results = scraper.scrape_regulations(db)
        logger.info(f"JDIH BPK scrape results: {results}")
        return {"status": "completed", "results": results}
    except Exception as e:
        logger.error(f"JDIH BPK scraper error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def run_dpr_scraper(self):
    from ..core.database import SessionLocal
    from ..scrapers.dpr_scraper import DPRProlegnasScraper

    db = SessionLocal()
    try:
        scraper = DPRProlegnasScraper()
        results = scraper.scrape_prolegnas(db)
        logger.info(f"DPR scrape results: {results}")
        return {"status": "completed", "results": results}
    except Exception as e:
        logger.error(f"DPR scraper error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def run_kementerian_scraper(self):
    from ..core.database import SessionLocal
    from ..scrapers.kementerian_scraper import KementerianScraper

    db = SessionLocal()
    try:
        scraper = KementerianScraper()
        results = scraper.scrape_all(db)
        logger.info(f"Kementerian scrape results: {results}")
        return {"status": "completed", "results": results}
    except Exception as e:
        logger.error(f"Kementerian scraper error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def cluster_and_create_drafts(self):
    from ..core.database import SessionLocal
    from ..models.models import User
    from ..services.pipeline import process_unprocessed_documents
    from sqlalchemy import select

    db = SessionLocal()
    try:
        admin = db.execute(select(User).where(User.role == "admin").limit(1)).scalar_one_or_none()
        admin_id = admin.id if admin else None

        policies = process_unprocessed_documents(db, admin_user_id=admin_id)
        logger.info(f"Created {len(policies)} draft policies from clustering")

        policy_ids = [str(p.id) for p in policies]
        return {"status": "completed", "drafts_created": len(policies), "policy_ids": policy_ids}
    except Exception as e:
        logger.error(f"Clustering error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def run_full_pipeline(self):
    results = {}

    scraper_tasks = [
        ("rss", run_rss_scraper),
        ("jdih_setneg", run_jdih_setneg_scraper),
        ("jdih_bpk", run_jdih_bpk_scraper),
        ("dpr", run_dpr_scraper),
        ("kementerian", run_kementerian_scraper),
    ]

    for name, task_func in scraper_tasks:
        try:
            task = task_func.delay()
            results[name] = {"task_id": task.id, "status": "dispatched"}
        except Exception as e:
            results[name] = {"status": "error", "message": str(e)}

    try:
        cluster_task = cluster_and_create_drafts.delay()
        results["clustering"] = {"task_id": cluster_task.id, "status": "dispatched"}
    except Exception as e:
        results["clustering"] = {"status": "error", "message": str(e)}

    return {"status": "dispatched", "results": results}


def trigger_ai_processing(policy_id: uuid.UUID, force: bool = False):
    task = process_policy_ai.delay(str(policy_id), force=force)
    return task


def get_process_status(policy_id: uuid.UUID) -> dict:
    from ..core.database import SessionLocal
    from ..models.models import Policy

    db = SessionLocal()
    try:
        policy = db.get(Policy, policy_id)
        if not policy:
            return {"policy_id": str(policy_id), "status": "not_found", "message": None}
        has_content = bool(policy.summary_30sec or policy.simple_explanation)
        return {
            "policy_id": str(policy_id),
            "status": "completed" if has_content else "pending",
            "message": None,
        }
    finally:
        db.close()