"""Database models and session management."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    LargeBinary,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# Association table for many-to-many relationship between accounts and tags
account_tags = Table(
    "account_tags",
    Base.metadata,
    Column("account_id", String(36), ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Account(Base):
    """Account model for storing Google account credentials."""

    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_encrypted: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sub2api: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gpt_membership: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    family_group: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    recovery_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    totp_secret_encrypted: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=account_tags, back_populates="accounts", lazy="selectin"
    )


class Tag(Base):
    """Tag model for categorizing accounts."""

    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship
    accounts: Mapped[List["Account"]] = relationship(
        "Account", secondary=account_tags, back_populates="tags", lazy="selectin"
    )


class SystemConfig(Base):
    """System configuration storage."""

    __tablename__ = "system_config"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database engine and session
engine = create_engine(
    f"sqlite:///{settings.DATABASE_PATH}",
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
