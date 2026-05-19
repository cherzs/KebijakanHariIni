from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ...core.database import get_db
from ...api.deps import require_admin
from ...models.models import RawDocument, ScrapeLog
from ...tasks.celery_app import (
    run_rss_scraper,
    run_jdih_setneg_scraper,
    run_jdih_bpk_scraper,
    run_dpr_scraper,
    run_kementerian_scraper,
    cluster_and_create_drafts,
    run_full_pipeline,
)

router = APIRouter(prefix="/internal/scrape", tags=["internal-scraping"])


@router.post("/rss")
def trigger_rss_scrape(user=Depends(require_admin)):
    task = run_rss_scraper.delay()
    return {"status": "dispatched", "task_id": task.id, "scraper": "rss"}


@router.post("/jdih-setneg")
def trigger_jdih_setneg_scrape(user=Depends(require_admin)):
    task = run_jdih_setneg_scraper.delay()
    return {"status": "dispatched", "task_id": task.id, "scraper": "jdih_setneg"}


@router.post("/jdih-bpk")
def trigger_jdih_bpk_scrape(user=Depends(require_admin)):
    task = run_jdih_bpk_scraper.delay()
    return {"status": "dispatched", "task_id": task.id, "scraper": "jdih_bpk"}


@router.post("/dpr-prolegnas")
def trigger_dpr_scrape(user=Depends(require_admin)):
    task = run_dpr_scraper.delay()
    return {"status": "dispatched", "task_id": task.id, "scraper": "dpr_prolegnas"}


@router.post("/kementerian")
def trigger_kementerian_scrape(user=Depends(require_admin)):
    task = run_kementerian_scraper.delay()
    return {"status": "dispatched", "task_id": task.id, "scraper": "kementerian"}


@router.post("/all")
def trigger_all_scrapers(user=Depends(require_admin)):
    task = run_full_pipeline.delay()
    return {"status": "dispatched", "task_id": task.id, "scraper": "full_pipeline"}


@router.post("/cluster")
def trigger_clustering(user=Depends(require_admin)):
    task = cluster_and_create_drafts.delay()
    return {"status": "dispatched", "task_id": task.id, "step": "cluster_and_create_drafts"}


@router.get("/raw-documents")
def list_raw_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    processed: bool | None = None,
    source_type: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    query = db.query(RawDocument)
    if processed is not None:
        query = query.filter(RawDocument.processed == processed)
    if source_type:
        query = query.filter(RawDocument.source_type == source_type)

    total = query.count()
    items = query.order_by(RawDocument.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": [
            {
                "id": str(item.id),
                "source_url": item.source_url,
                "source_type": item.source_type,
                "title": item.title,
                "site_name": item.site_name,
                "snippet": item.snippet[:100] if item.snippet else None,
                "published_date": item.published_date.isoformat() if item.published_date else None,
                "processed": item.processed,
                "policy_id": str(item.policy_id) if item.policy_id else None,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ],
    }


@router.get("/logs")
def list_scrape_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    total = db.query(ScrapeLog).count()
    logs = db.query(ScrapeLog).order_by(desc(ScrapeLog.started_at)).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": [
            {
                "id": str(log.id),
                "scraper_name": log.scraper_name,
                "status": log.status,
                "items_found": log.items_found,
                "items_saved": log.items_saved,
                "items_skipped": log.items_skipped,
                "error_message": log.error_message,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "finished_at": log.finished_at.isoformat() if log.finished_at else None,
            }
            for log in logs
        ],
    }


@router.get("/stats")
def scrape_stats(db: Session = Depends(get_db), user=Depends(require_admin)):
    total_documents = db.query(func.count(RawDocument.id)).scalar() or 0
    processed_documents = db.query(func.count(RawDocument.id)).filter(RawDocument.processed == True).scalar() or 0
    unprocessed_documents = db.query(func.count(RawDocument.id)).filter(RawDocument.processed == False).scalar() or 0

    source_type_counts = dict(
        db.query(RawDocument.source_type, func.count(RawDocument.id))
        .group_by(RawDocument.source_type)
        .all()
    )

    recent_scrapes = db.query(ScrapeLog).order_by(desc(ScrapeLog.started_at)).limit(5).all()

    return {
        "total_documents": total_documents,
        "processed_documents": processed_documents,
        "unprocessed_documents": unprocessed_documents,
        "by_source_type": source_type_counts,
        "recent_scrapes": [
            {
                "scraper_name": log.scraper_name,
                "status": log.status,
                "items_found": log.items_found,
                "items_saved": log.items_saved,
                "started_at": log.started_at.isoformat() if log.started_at else None,
            }
            for log in recent_scrapes
        ],
    }