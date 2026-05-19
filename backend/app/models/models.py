import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Date, Integer, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="viewer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'editor', 'viewer')", name="ck_user_role"),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    summary_30sec: Mapped[str | None] = mapped_column(Text)
    summary_long: Mapped[str | None] = mapped_column(Text)
    simple_explanation: Mapped[str | None] = mapped_column(Text)
    impact_explanation: Mapped[str | None] = mapped_column(Text)
    affected_groups: Mapped[str | None] = mapped_column(Text)
    government_claim: Mapped[str | None] = mapped_column(Text)
    public_criticism: Mapped[str | None] = mapped_column(Text)
    source_confidence: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False, default="needs_verification")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="wacana")
    primary_category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    published_status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    primary_category: Mapped[Category | None] = relationship()
    categories: Mapped[list["Category"]] = relationship(secondary="policy_categories", back_populates="policies")
    timelines: Mapped[list["PolicyTimeline"]] = relationship(back_populates="policy", cascade="all, delete-orphan")
    sources: Mapped[list["Source"]] = relationship(back_populates="policy", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('wacana','draf','dibahas','disahkan','berlaku','ditunda','dibatalkan')",
            name="ck_policy_status",
        ),
        CheckConstraint(
            "published_status IN ('draft','published','archived')",
            name="ck_policy_published_status",
        ),
        CheckConstraint(
            "source_confidence IN ('high','medium','low')",
            name="ck_source_confidence",
        ),
        CheckConstraint(
            "verification_status IN ('verified','needs_verification','unverifiable')",
            name="ck_verification_status",
        ),
        Index("idx_policies_status", "status"),
        Index("idx_policies_published", "published_status"),
        Index("idx_policies_published_at", "published_at"),
    )


class PolicyCategory(Base):
    __tablename__ = "policy_categories"

    policy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("policies.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)


class PolicyTimeline(Base):
    __tablename__ = "policy_timelines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    policy: Mapped["Policy"] = relationship(back_populates="timelines")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    snippet: Mapped[str | None] = mapped_column(Text)
    published_date: Mapped[datetime | None] = mapped_column(Date)
    site_name: Mapped[str | None] = mapped_column(String(200))
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False, default="needs_verification")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    policy: Mapped["Policy"] = relationship(back_populates="sources")

    __table_args__ = (
        CheckConstraint("source_type IN ('official', 'news')", name="ck_source_type"),
        CheckConstraint(
            "verification_status IN ('verified','needs_verification','unverifiable')",
            name="ck_source_verification",
        ),
    )


class RawDocument(Base):
    __tablename__ = "raw_documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    site_name: Mapped[str | None] = mapped_column(String(200))
    title: Mapped[str | None] = mapped_column(String(500))
    content_text: Mapped[str | None] = mapped_column(Text)
    snippet: Mapped[str | None] = mapped_column(Text)
    published_date: Mapped[datetime | None] = mapped_column(Date)
    metadata_json: Mapped[str | None] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    policy_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("policies.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    __table_args__ = (
        Index("idx_raw_docs_processed", "processed"),
        Index("idx_raw_docs_source_url", "source_url", unique=True),
    )


Category.policies = relationship("Policy", secondary="policy_categories", back_populates="categories")