"""Security utilities and dependencies."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.models import get_db
from app.services.auth_service import AuthService
from app.services.crypto_service import crypto_service


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> str:
    """Dependency to verify JWT token and return user."""
    auth_service = AuthService(db)
    token_data = auth_service.verify_token(credentials.credentials)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify encryption key is set
    if crypto_service._encryption_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired, please login again",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data.sub


def require_initialized(db: Session = Depends(get_db)) -> bool:
    """Dependency to check if system is initialized."""
    auth_service = AuthService(db)
    if not auth_service.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System not initialized. Please set up master password first.",
        )
    return True
