"""Pydantic schemas for accounts."""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class TagBase(BaseModel):
    """Base schema for tags."""

    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#6366f1", pattern=r"^#[0-9A-Fa-f]{6}$")


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TagResponse(TagBase):
    """Schema for tag response."""

    id: str
    created_at: datetime
    account_count: int = 0

    class Config:
        from_attributes = True


class TagBrief(BaseModel):
    """Brief tag info for account response."""

    id: str
    name: str
    color: str

    class Config:
        from_attributes = True


class AccountBase(BaseModel):
    """Base schema for accounts."""

    email: EmailStr
    note: Optional[str] = None
    sub2api: bool = False
    source: Optional[str] = Field(None, max_length=50)
    browser: Optional[str] = Field(None, max_length=50)
    gpt_membership: Optional[str] = Field(None, max_length=20)
    family_group: Optional[str] = Field(None, max_length=100)
    recovery_email: Optional[EmailStr] = None
    custom_fields: Optional[Dict[str, str]] = Field(default_factory=dict)


class AccountCreate(AccountBase):
    """Schema for creating an account."""

    password: Optional[str] = None
    totp_secret: Optional[str] = None
    tag_ids: List[str] = Field(default_factory=list)


class AccountUpdate(BaseModel):
    """Schema for updating an account."""

    email: Optional[EmailStr] = None
    password: Optional[str] = None
    note: Optional[str] = None
    sub2api: Optional[bool] = None
    source: Optional[str] = Field(None, max_length=50)
    browser: Optional[str] = Field(None, max_length=50)
    gpt_membership: Optional[str] = Field(None, max_length=20)
    family_group: Optional[str] = Field(None, max_length=100)
    recovery_email: Optional[EmailStr] = None
    totp_secret: Optional[str] = None
    tag_ids: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, str]] = None


class AccountResponse(AccountBase):
    """Schema for account response (password hidden)."""

    id: str
    has_password: bool
    has_totp: bool
    tags: List[TagBrief] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountDetailResponse(AccountResponse):
    """Schema for account detail with decrypted sensitive data."""

    password: Optional[str] = None
    totp_secret: Optional[str] = None


class AccountListResponse(BaseModel):
    """Schema for paginated account list."""

    items: List[AccountResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AccountImportRequest(BaseModel):
    """Schema for import request."""

    conflict_strategy: str = Field(default="skip", pattern=r"^(skip|overwrite|merge)$")


class AccountImportResult(BaseModel):
    """Schema for import result."""

    total: int
    imported: int
    skipped: int
    errors: List[str]


class AccountExportRequest(BaseModel):
    """Schema for export request."""

    format: str = Field(default="excel", pattern=r"^(excel|csv|json)$")
    include_password: bool = False
    account_ids: Optional[List[str]] = None


class BatchDeleteRequest(BaseModel):
    """Schema for batch delete request."""

    account_ids: List[str] = Field(..., min_length=1)


class BatchTagsRequest(BaseModel):
    """Schema for batch tags update request."""

    account_ids: List[str] = Field(..., min_length=1)
    tag_ids: List[str] = Field(default_factory=list)


class BatchUpdateRequest(BaseModel):
    """Schema for batch update request."""

    account_ids: List[str] = Field(..., min_length=1)
    # Include optional update fields
    email: Optional[EmailStr] = None
    note: Optional[str] = None
    sub2api: Optional[bool] = None
    source: Optional[str] = Field(None, max_length=50)
    browser: Optional[str] = Field(None, max_length=50)
    gpt_membership: Optional[str] = Field(None, max_length=20)
    family_group: Optional[str] = Field(None, max_length=100)
    recovery_email: Optional[EmailStr] = None
    tag_ids: Optional[List[str]] = None
