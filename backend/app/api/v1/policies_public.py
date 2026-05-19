import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.models import Policy
from ...services.policy_service import (
    create_policy,
    get_policy_by_slug,
    get_policy_by_id,
    list_policies,
    update_policy,
    delete_policy,
    search_policies,
)
from ...schemas.policies import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    PolicyListResponse,
    PolicyListItem,
    SearchResponse,
)
from ..deps import get_current_user, require_admin

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("", response_model=PolicyListResponse)
def list_public_policies(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    category: str | None = None,
    sort: str = Query("updated_at"),
    db: Session = Depends(get_db),
):
    return list_policies(db, page=page, limit=limit, status=status, category_slug=category, sort_by=sort)


@router.get("/search", response_model=SearchResponse)
def search_public_policies(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    result = search_policies(db, query=q, page=page, limit=limit)
    return SearchResponse(items=result.items, total=result.total, query=q)


@router.get("/{slug}", response_model=PolicyResponse)
def get_public_policy(slug: str, db: Session = Depends(get_db)):
    policy = get_policy_by_slug(db, slug)
    if not policy or policy.published_status != "published":
        raise HTTPException(status_code=404, detail="Kebijakan tidak ditemukan")
    return policy