"""Pydantic schemas for authentication."""
from pydantic import BaseModel, Field, field_validator

from app.config import settings


class MasterPasswordSetup(BaseModel):
    """Schema for initial master password setup."""

    password: str = Field(..., min_length=settings.MASTER_PASSWORD_MIN_LENGTH)
    confirm_password: str = Field(..., min_length=settings.MASTER_PASSWORD_MIN_LENGTH)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < settings.MASTER_PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {settings.MASTER_PASSWORD_MIN_LENGTH} characters")
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_upper and has_lower and has_digit):
            raise ValueError("Password must contain uppercase, lowercase, and digit")
        return v


class LoginRequest(BaseModel):
    """Schema for login request."""

    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Schema for login response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordChange(BaseModel):
    """Schema for changing master password."""

    current_password: str
    new_password: str = Field(..., min_length=settings.MASTER_PASSWORD_MIN_LENGTH)
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class TokenData(BaseModel):
    """Schema for JWT token data."""

    sub: str
    exp: int


class SystemStatus(BaseModel):
    """Schema for system status."""

    is_initialized: bool
    is_locked: bool
