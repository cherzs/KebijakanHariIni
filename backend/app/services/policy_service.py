import uuid
import re
from datetime import datetime, timezone
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, selectinload
from ..models.models import Policy, Category, Source, PolicyTimeline, PolicyCategory, User
from ..schemas.policies import PolicyCreate, PolicyUpdate, PolicyListResponse, PolicyListItem


def generate_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug[:200]


def get_or_create_slug(db: Session, title: str) -> str:
    base_slug = generate_slug(title)
    slug = base_slug
    counter = 1
    while db.execute(select(Policy).where(Policy.slug == slug)).scalar_one_or_none():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def create_policy(db: Session, data: PolicyCreate, user_id: uuid.UUID) -> Policy:
    slug = get_or_create_slug(db, data.title)
    policy = Policy(
        title=data.title,
        slug=slug,
        summary_30sec=data.summary_30sec,
        summary_long=data.summary_long,
        simple_explanation=data.simple_explanation,
        impact_explanation=data.impact_explanation,
        affected_groups=data.affected_groups,
        government_claim=data.government_claim,
        public_criticism=data.public_criticism,
        source_confidence=data.source_confidence,
        verification_status=data.verification_status,
        status=data.status,
        primary_category_id=data.primary_category_id,
        created_by=user_id,
    )
    db.add(policy)
    db.flush()

    if data.category_ids:
        for cat_id in data.category_ids:
            db.add(PolicyCategory(policy_id=policy.id, category_id=cat_id))

    db.commit()
    db.refresh(policy)
    return policy


def get_policy_by_slug(db: Session, slug: str) -> Policy | None:
    return db.execute(
        select(Policy)
        .where(Policy.slug == slug)
        .options(
            selectinload(Policy.primary_category),
            selectinload(Policy.categories),
            selectinload(Policy.timelines),
            selectinload(Policy.sources),
        )
    ).scalar_one_or_none()


def get_policy_by_id(db: Session, policy_id: uuid.UUID) -> Policy | None:
    return db.execute(
        select(Policy)
        .where(Policy.id == policy_id)
        .options(
            selectinload(Policy.primary_category),
            selectinload(Policy.categories),
            selectinload(Policy.timelines),
            selectinload(Policy.sources),
        )
    ).scalar_one_or_none()


def list_policies(
    db: Session,
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
    category_slug: str | None = None,
    published_status: str | None = "published",
    sort_by: str = "updated_at",
) -> PolicyListResponse:
    query = select(Policy)
    if published_status:
        query = query.where(Policy.published_status == published_status)

    if status:
        query = query.where(Policy.status == status)
    if category_slug:
        category_subq = select(Category.id).where(Category.slug == category_slug)
        query = query.where(
            or_(
                Policy.primary_category_id.in_(category_subq),
                Policy.id.in_(
                    select(PolicyCategory.policy_id).where(
                        PolicyCategory.category_id.in_(category_subq)
                    )
                ),
            )
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = db.execute(count_q).scalar() or 0

    order_col = getattr(Policy, sort_by, Policy.updated_at).desc()
    items = (
        db.execute(
            query.order_by(order_col)
            .offset((page - 1) * limit)
            .limit(limit)
            .options(selectinload(Policy.primary_category))
        )
        .scalars()
        .all()
    )

    return PolicyListResponse(
        items=[PolicyListItem.model_validate(p, from_attributes=True) for p in items],
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit if total > 0 else 0,
    )


def update_policy(db: Session, policy_id: uuid.UUID, data: PolicyUpdate, reviewer_id: uuid.UUID | None = None) -> Policy | None:
    policy = db.get(Policy, policy_id)
    if not policy:
        return None

    update_data = data.model_dump(exclude_unset=True, exclude={"category_ids"})

    if data.slug is not None:
        update_data["slug"] = get_or_create_slug(db, data.slug)

    for key, value in update_data.items():
        setattr(policy, key, value)

    if data.published_status == "published" and not policy.published_at:
        policy.published_at = datetime.now(timezone.utc)

    if reviewer_id:
        policy.reviewed_by = reviewer_id

    if data.category_ids is not None:
        db.query(PolicyCategory).filter(PolicyCategory.policy_id == policy_id).delete()
        for cat_id in data.category_ids:
            db.add(PolicyCategory(policy_id=policy_id, category_id=cat_id))

    db.commit()
    db.refresh(policy)
    return policy


def delete_policy(db: Session, policy_id: uuid.UUID) -> bool:
    policy = db.get(Policy, policy_id)
    if not policy:
        return False
    db.delete(policy)
    db.commit()
    return True


def search_policies(db: Session, query: str, page: int = 1, limit: int = 20) -> PolicyListResponse:
    search_str = f"%{query}%"
    base_q = select(Policy).where(Policy.published_status == "published").where(
        or_(
            Policy.title.ilike(search_str),
            Policy.summary_30sec.ilike(search_str),
            Policy.simple_explanation.ilike(search_str),
        )
    )

    count_q = select(func.count()).select_from(base_q.subquery())
    total = db.execute(count_q).scalar() or 0

    items_q = (
        base_q.order_by(Policy.updated_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .options(selectinload(Policy.primary_category))
    )
    results = db.execute(items_q).scalars().all()

    return PolicyListResponse(
        items=[PolicyListItem.model_validate(p, from_attributes=True) for p in results],
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit if total > 0 else 0,
    )


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()