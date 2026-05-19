import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.models import Policy, PolicyTimeline, Source
from ...services.policy_service import (
    create_policy,
    get_policy_by_id,
    list_policies,
    update_policy,
    delete_policy,
)
from ...tasks.celery_app import trigger_ai_processing, get_process_status
from ...schemas.policies import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    PolicyListResponse,
    TimelineCreate,
    TimelineResponse,
    SourceCreate,
    SourceResponse,
    AIProcessRequest,
    AIProcessStatus,
)
from ..deps import get_current_user, require_editor, require_admin

router = APIRouter(prefix="/admin/policies", tags=["admin-policies"])


@router.get("", response_model=PolicyListResponse)
def list_all_policies(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    published_status: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_editor),
):
    pub = published_status if published_status else None
    return list_policies(db, page=page, limit=limit, status=status, published_status=pub)


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_new_policy(data: PolicyCreate, db: Session = Depends(get_db), user=Depends(require_editor)):
    policy = create_policy(db, data, user_id=user.id)
    return get_policy_by_id(db, policy.id)


@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy_detail(policy_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(require_editor)):
    policy = get_policy_by_id(db, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Kebijakan tidak ditemukan")
    return policy


@router.put("/{policy_id}", response_model=PolicyResponse)
def update_existing_policy(policy_id: uuid.UUID, data: PolicyUpdate, db: Session = Depends(get_db), user=Depends(require_editor)):
    policy = update_policy(db, policy_id, data, reviewer_id=user.id)
    if not policy:
        raise HTTPException(status_code=404, detail="Kebijakan tidak ditemukan")
    return get_policy_by_id(db, policy_id)


@router.patch("/{policy_id}/publish", response_model=PolicyResponse)
def publish_policy(policy_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(require_admin)):
    policy = update_policy(db, policy_id, PolicyUpdate(published_status="published"), reviewer_id=user.id)
    if not policy:
        raise HTTPException(status_code=404, detail="Kebijakan tidak ditemukan")
    return get_policy_by_id(db, policy_id)


@router.patch("/{policy_id}/archive", response_model=PolicyResponse)
def archive_policy(policy_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(require_admin)):
    policy = update_policy(db, policy_id, PolicyUpdate(published_status="archived"), reviewer_id=user.id)
    if not policy:
        raise HTTPException(status_code=404, detail="Kebijakan tidak ditemukan")
    return get_policy_by_id(db, policy_id)


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_policy(policy_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(require_admin)):
    if not delete_policy(db, policy_id):
        raise HTTPException(status_code=404, detail="Kebijakan tidak ditemukan")


# === Timeline endpoints ===

@router.post("/{policy_id}/timelines", response_model=TimelineResponse, status_code=status.HTTP_201_CREATED)
def add_timeline(policy_id: uuid.UUID, data: TimelineCreate, db: Session = Depends(get_db), user=Depends(require_editor)):
    policy = db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Kebijakan tidak ditemukan")
    timeline = PolicyTimeline(policy_id=policy_id, **data.model_dump())
    db.add(timeline)
    db.commit()
    db.refresh(timeline)
    return timeline


@router.put("/{policy_id}/timelines/{timeline_id}", response_model=TimelineResponse)
def update_timeline(policy_id: uuid.UUID, timeline_id: uuid.UUID, data: TimelineCreate, db: Session = Depends(get_db), user=Depends(require_editor)):
    timeline = db.get(PolicyTimeline, timeline_id)
    if not timeline or timeline.policy_id != policy_id:
        raise HTTPException(status_code=404, detail="Timeline tidak ditemukan")
    for key, value in data.model_dump().items():
        setattr(timeline, key, value)
    db.commit()
    db.refresh(timeline)
    return timeline


@router.delete("/{policy_id}/timelines/{timeline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timeline(policy_id: uuid.UUID, timeline_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(require_editor)):
    timeline = db.get(PolicyTimeline, timeline_id)
    if not timeline or timeline.policy_id != policy_id:
        raise HTTPException(status_code=404, detail="Timeline tidak ditemukan")
    db.delete(timeline)
    db.commit()


# === Source endpoints ===

@router.post("/{policy_id}/sources", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def add_source(policy_id: uuid.UUID, data: SourceCreate, db: Session = Depends(get_db), user=Depends(require_editor)):
    policy = db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Kebijakan tidak ditemukan")
    source = Source(policy_id=policy_id, **data.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.put("/{policy_id}/sources/{source_id}", response_model=SourceResponse)
def update_source(policy_id: uuid.UUID, source_id: uuid.UUID, data: SourceCreate, db: Session = Depends(get_db), user=Depends(require_editor)):
    source = db.get(Source, source_id)
    if not source or source.policy_id != policy_id:
        raise HTTPException(status_code=404, detail="Sumber tidak ditemukan")
    for key, value in data.model_dump().items():
        setattr(source, key, value)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/{policy_id}/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(policy_id: uuid.UUID, source_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(require_editor)):
    source = db.get(Source, source_id)
    if not source or source.policy_id != policy_id:
        raise HTTPException(status_code=404, detail="Sumber tidak ditemukan")
    db.delete(source)
    db.commit()


# === AI Processing ===

@router.post("/{policy_id}/process", response_model=AIProcessStatus)
def process_policy_with_ai(policy_id: uuid.UUID, data: AIProcessRequest, db: Session = Depends(get_db), user=Depends(require_editor)):
    policy = db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Kebijakan tidak ditemukan")
    task = trigger_ai_processing(policy_id, force=data.force)
    return AIProcessStatus(policy_id=policy_id, status="processing", message=task.id)


@router.get("/{policy_id}/process/status", response_model=AIProcessStatus)
def get_ai_process_status(policy_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(require_editor)):
    status_info = get_process_status(policy_id)
    return AIProcessStatus(**status_info)