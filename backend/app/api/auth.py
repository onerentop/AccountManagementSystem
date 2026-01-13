"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models import get_db
from app.schemas import (
    MasterPasswordSetup,
    LoginRequest,
    LoginResponse,
    PasswordChange,
    SystemStatus,
)
from app.services.auth_service import AuthService
from app.utils.security import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/status", response_model=SystemStatus)
async def get_system_status(db: Session = Depends(get_db)):
    """Check if the system is initialized and locked status."""
    auth_service = AuthService(db)
    from app.services.crypto_service import crypto_service

    return SystemStatus(
        is_initialized=auth_service.is_initialized(),
        is_locked=crypto_service._encryption_key is None,
    )


@router.post("/setup", status_code=status.HTTP_201_CREATED)
async def setup_master_password(
    data: MasterPasswordSetup,
    db: Session = Depends(get_db),
):
    """Set up the initial master password."""
    auth_service = AuthService(db)

    if auth_service.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System is already initialized",
        )

    try:
        auth_service.setup_master_password(data.password)
        return {"message": "Master password set successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login with master password."""
    auth_service = AuthService(db)

    if not auth_service.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System not initialized. Please set up master password first.",
        )

    token = auth_service.login(data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    return LoginResponse(
        access_token=token,
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout and clear session."""
    auth_service = AuthService(db)
    auth_service.logout()
    return {"message": "Logged out successfully"}


@router.post("/lock")
async def lock(_: str = Depends(get_current_user)):
    """Lock the application (clear encryption key)."""
    from app.services.crypto_service import crypto_service
    crypto_service.clear_encryption_key()
    return {"message": "Application locked"}


@router.put("/password")
async def change_password(
    data: PasswordChange,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the master password."""
    auth_service = AuthService(db)

    if not auth_service.change_master_password(data.current_password, data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    return {"message": "Password changed successfully"}
