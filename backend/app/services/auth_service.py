"""Authentication service for managing master password and sessions."""
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models import SystemConfig
from app.schemas import TokenData
from app.services.crypto_service import crypto_service


class AuthService:
    """Service for authentication operations."""

    CONFIG_KEY_PASSWORD_HASH = "master_password_hash"
    CONFIG_KEY_ENCRYPTION_SALT = "encryption_salt"
    CONFIG_KEY_INITIALIZED = "is_initialized"

    def __init__(self, db: Session):
        self.db = db

    def is_initialized(self) -> bool:
        """Check if the system has been initialized with a master password."""
        config = self.db.query(SystemConfig).filter_by(key=self.CONFIG_KEY_INITIALIZED).first()
        return config is not None and config.value == "true"

    def setup_master_password(self, password: str) -> bool:
        """Set up the initial master password."""
        if self.is_initialized():
            raise ValueError("System is already initialized")

        # Generate salt and hash password
        salt = crypto_service.generate_salt()
        password_hash = crypto_service.hash_password(password)

        # Store in database
        configs = [
            SystemConfig(key=self.CONFIG_KEY_PASSWORD_HASH, value=password_hash),
            SystemConfig(key=self.CONFIG_KEY_ENCRYPTION_SALT, value=base64.b64encode(salt).decode()),
            SystemConfig(key=self.CONFIG_KEY_INITIALIZED, value="true"),
        ]

        for config in configs:
            self.db.merge(config)
        self.db.commit()

        # Set up encryption key
        encryption_key = crypto_service.derive_key(password, salt)
        crypto_service.set_encryption_key(encryption_key)

        return True

    def verify_master_password(self, password: str) -> bool:
        """Verify the master password."""
        config = self.db.query(SystemConfig).filter_by(key=self.CONFIG_KEY_PASSWORD_HASH).first()
        if not config:
            return False

        return crypto_service.verify_password(password, config.value)

    def login(self, password: str) -> Optional[str]:
        """Authenticate and return JWT token."""
        if not self.verify_master_password(password):
            return None

        # Get salt and derive encryption key
        salt_config = self.db.query(SystemConfig).filter_by(key=self.CONFIG_KEY_ENCRYPTION_SALT).first()
        if not salt_config:
            return None

        salt = base64.b64decode(salt_config.value)
        encryption_key = crypto_service.derive_key(password, salt)
        crypto_service.set_encryption_key(encryption_key)

        # Generate JWT token (use timezone-aware datetime)
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        token_data = {
            "sub": "master",
            "exp": expire,
            "iat": now,
        }

        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    def logout(self) -> None:
        """Clear the encryption key and invalidate session."""
        crypto_service.clear_encryption_key()

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token and return token data."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return TokenData(sub=payload["sub"], exp=int(payload["exp"]))
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def change_master_password(self, current_password: str, new_password: str) -> bool:
        """Change the master password and re-encrypt all data."""
        if not self.verify_master_password(current_password):
            return False

        # Get current salt and key
        salt_config = self.db.query(SystemConfig).filter_by(key=self.CONFIG_KEY_ENCRYPTION_SALT).first()
        if not salt_config:
            return False

        old_salt = base64.b64decode(salt_config.value)
        old_key = crypto_service.derive_key(current_password, old_salt)

        # Generate new salt and key
        new_salt = crypto_service.generate_salt()
        new_key = crypto_service.derive_key(new_password, new_salt)
        new_password_hash = crypto_service.hash_password(new_password)

        # Re-encrypt all sensitive data
        from app.models import Account

        crypto_service.set_encryption_key(old_key)
        accounts = self.db.query(Account).filter_by(is_deleted=False).all()

        # Decrypt with old key and encrypt with new key
        for account in accounts:
            if account.password_encrypted:
                plaintext = crypto_service.decrypt(account.password_encrypted)
                crypto_service.set_encryption_key(new_key)
                account.password_encrypted = crypto_service.encrypt(plaintext)
                crypto_service.set_encryption_key(old_key)

            if account.totp_secret_encrypted:
                plaintext = crypto_service.decrypt(account.totp_secret_encrypted)
                crypto_service.set_encryption_key(new_key)
                account.totp_secret_encrypted = crypto_service.encrypt(plaintext)
                crypto_service.set_encryption_key(old_key)

        # Update configs
        self.db.query(SystemConfig).filter_by(key=self.CONFIG_KEY_PASSWORD_HASH).update({"value": new_password_hash})
        self.db.query(SystemConfig).filter_by(key=self.CONFIG_KEY_ENCRYPTION_SALT).update(
            {"value": base64.b64encode(new_salt).decode()}
        )

        self.db.commit()

        # Set new encryption key
        crypto_service.set_encryption_key(new_key)

        return True
