import uuid
from celery import Celery
from ..core.config import Settings

settings = Settings()

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
)


@celery_app.task(bind=True)
def process_policy_ai(self, policy_id: str, force: bool = False):
    from ..core.database import SessionLocal
    from ..models.models import Policy
    from .ai_processor import (
        summarize_policy,
        classify_category,
        detect_status,
        extract_timeline,
        explain_impact,
        generate_simple_explanation,
    )
    from ..services.policy_service import update_policy, get_policy_by_id
    from ..schemas.policies import PolicyUpdate, TimelineCreate

    db = SessionLocal()
    try:
        policy = get_policy_by_id(db, uuid.UUID(policy_id))
        if not policy:
            return {"status": "error", "message": "Policy not found"}

        sources = policy.sources if policy.sources else []
        sources_text = "\n".join([f"- {s.title} ({s.url})" for s in sources])

        summarize_policy(policy.title, sources)

        if not policy.summary_30sec or force:
            summary = summarize_policy(policy.title, sources)
            policy.summary_30sec = summary

        if not policy.simple_explanation or force:
            explanation = generate_simple_explanation(policy.title, sources)
            policy.simple_explanation = explanation

        if not policy.impact_explanation or force:
            impact = explain_impact(policy.title, sources)
            policy.impact_explanation = impact

        if not policy.status or policy.status == "wacana" or force:
            detected = detect_status(policy.title, sources_text)
            if detected in ["wacana", "draf", "dibahas", "disahkan", "berlaku", "ditunda", "dibatalkan"]:
                policy.status = detected

        db.commit()

    finally:
        db.close()

    return {"status": "completed", "policy_id": policy_id}


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