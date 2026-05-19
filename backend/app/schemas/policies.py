from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field


# === Auth ===

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str | None = None
    role: str
    is_active: bool


# === Category ===

class CategoryCreate(BaseModel):
    slug: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: str | None = None


class CategoryResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


# === Source ===

class SourceCreate(BaseModel):
    source_type: str = Field(..., pattern="^(official|news)$")
    title: str = Field(..., max_length=500)
    url: str
    snippet: str | None = Field(None, max_length=500)
    published_date: date | None = None
    site_name: str | None = None
    verification_status: str = Field("needs_verification", pattern="^(verified|needs_verification|unverifiable)$")


class SourceResponse(BaseModel):
    id: UUID
    source_type: str
    title: str
    url: str
    snippet: str | None = None
    published_date: date | None = None
    site_name: str | None = None
    verification_status: str = "needs_verification"

    model_config = {"from_attributes": True}


# === Timeline ===

class TimelineCreate(BaseModel):
    date: date
    title: str = Field(..., max_length=200)
    description: str | None = None
    sort_order: int = 0


class TimelineResponse(BaseModel):
    id: UUID
    date: date
    title: str
    description: str | None = None
    sort_order: int = 0

    model_config = {"from_attributes": True}


# === Policy ===

POLICY_STATUSES = ["wacana", "draf", "dibahas", "disahkan", "berlaku", "ditunda", "dibatalkan"]
PUBLISHED_STATUSES = ["draft", "published", "archived"]


class PolicyCreate(BaseModel):
    title: str = Field(..., max_length=500)
    summary_30sec: str | None = None
    summary_long: str | None = None
    simple_explanation: str | None = None
    impact_explanation: str | None = None
    affected_groups: str | None = None
    government_claim: str | None = None
    public_criticism: str | None = None
    source_confidence: str = Field("medium", pattern="^(high|medium|low)$")
    verification_status: str = Field("needs_verification", pattern="^(verified|needs_verification|unverifiable)$")
    status: str = Field("wacana", pattern=f"^({'|'.join(POLICY_STATUSES)})$")
    primary_category_id: UUID | None = None
    category_ids: list[UUID] = []


class PolicyUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    slug: str | None = None
    summary_30sec: str | None = None
    summary_long: str | None = None
    simple_explanation: str | None = None
    impact_explanation: str | None = None
    affected_groups: str | None = None
    government_claim: str | None = None
    public_criticism: str | None = None
    source_confidence: str | None = Field(None, pattern="^(high|medium|low)$")
    verification_status: str | None = Field(None, pattern="^(verified|needs_verification|unverifiable)$")
    status: str | None = Field(None, pattern=f"^({'|'.join(POLICY_STATUSES)})$")
    primary_category_id: UUID | None = None
    category_ids: list[UUID] | None = None
    published_status: str | None = Field(None, pattern=f"^({'|'.join(PUBLISHED_STATUSES)})$")


class PolicyResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    summary_30sec: str | None = None
    summary_long: str | None = None
    simple_explanation: str | None = None
    impact_explanation: str | None = None
    affected_groups: str | None = None
    government_claim: str | None = None
    public_criticism: str | None = None
    source_confidence: str = "medium"
    verification_status: str = "needs_verification"
    status: str
    primary_category: CategoryResponse | None = None
    categories: list[CategoryResponse] = []
    timelines: list[TimelineResponse] = []
    sources: list[SourceResponse] = []
    published_status: str
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PolicyListItem(BaseModel):
    id: UUID
    title: str
    slug: str
    status: str
    summary_30sec: str | None = None
    primary_category: CategoryResponse | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PolicyListItem(BaseModel):
    id: UUID
    title: str
    slug: str
    status: str
    summary_30sec: str | None = None
    primary_category: CategoryResponse | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PolicyListResponse(BaseModel):
    items: list[PolicyListItem]
    total: int
    page: int
    limit: int
    pages: int


# === Search ===

class SearchResponse(BaseModel):
    items: list[PolicyListItem]
    total: int
    query: str


# === AI Processing ===

class AIProcessRequest(BaseModel):
    force: bool = False


class AIProcessStatus(BaseModel):
    policy_id: UUID
    status: str
    message: str | None = None