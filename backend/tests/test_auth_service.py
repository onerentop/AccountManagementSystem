"""Tests for authentication service."""
import pytest
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.services.crypto_service import crypto_service
from app.models import SystemConfig


class TestAuthServiceInitialization:
    """Test cases for system initialization."""

    def test_is_initialized_false(self, db: Session):
        """Test is_initialized returns False for new system."""
        auth_service = AuthService(db)
        assert auth_service.is_initialized() is False

    def test_is_initialized_true_after_setup(self, db: Session):
        """Test is_initialized returns True after setup."""
        auth_service = AuthService(db)
        auth_service.setup_master_password("TestPassword123!")

        assert auth_service.is_initialized() is True

    def test_setup_master_password(self, db: Session):
        """Test master password setup."""
        auth_service = AuthService(db)
        result = auth_service.setup_master_password("SecurePassword!")

        assert result is True

        # Verify configs are stored
        hash_config = db.query(SystemConfig).filter_by(
            key=AuthService.CONFIG_KEY_PASSWORD_HASH
        ).first()
        assert hash_config is not None

        salt_config = db.query(SystemConfig).filter_by(
            key=AuthService.CONFIG_KEY_ENCRYPTION_SALT
        ).first()
        assert salt_config is not None

    def test_setup_raises_if_already_initialized(self, db: Session):
        """Test setup raises ValueError if already initialized."""
        auth_service = AuthService(db)
        auth_service.setup_master_password("FirstPassword!")

        with pytest.raises(ValueError) as exc_info:
            auth_service.setup_master_password("SecondPassword!")

        assert "already initialized" in str(exc_info.value)


class TestAuthServiceLogin:
    """Test cases for login functionality."""

    def test_verify_master_password_success(self, db: Session):
        """Test password verification with correct password."""
        auth_service = AuthService(db)
        password = "TestPassword123!"
        auth_service.setup_master_password(password)

        # Clear encryption key to simulate fresh state
        crypto_service.clear_encryption_key()

        assert auth_service.verify_master_password(password) is True

    def test_verify_master_password_failure(self, db: Session):
        """Test password verification with wrong password."""
        auth_service = AuthService(db)
        auth_service.setup_master_password("CorrectPassword!")

        assert auth_service.verify_master_password("WrongPassword!") is False

    def test_login_success(self, db: Session):
        """Test successful login returns token."""
        auth_service = AuthService(db)
        password = "TestPassword123!"
        auth_service.setup_master_password(password)

        # Clear encryption key
        crypto_service.clear_encryption_key()

        token = auth_service.login(password)

        assert token is not None
        assert len(token) > 0

    def test_login_failure(self, db: Session):
        """Test login with wrong password returns None."""
        auth_service = AuthService(db)
        auth_service.setup_master_password("CorrectPassword!")

        token = auth_service.login("WrongPassword!")

        assert token is None

    def test_login_sets_encryption_key(self, db: Session):
        """Test login sets the encryption key."""
        auth_service = AuthService(db)
        password = "TestPassword123!"
        auth_service.setup_master_password(password)

        # Clear key
        crypto_service.clear_encryption_key()
        assert crypto_service._encryption_key is None

        # Login should set key
        auth_service.login(password)
        assert crypto_service._encryption_key is not None


class TestAuthServiceLogout:
    """Test cases for logout functionality."""

    def test_logout_clears_encryption_key(self, db: Session):
        """Test logout clears the encryption key."""
        auth_service = AuthService(db)
        password = "TestPassword123!"
        auth_service.setup_master_password(password)

        # Verify key is set
        assert crypto_service._encryption_key is not None

        # Logout
        auth_service.logout()

        assert crypto_service._encryption_key is None


class TestAuthServiceToken:
    """Test cases for token verification."""

    def test_verify_token_success(self, db: Session):
        """Test token verification with valid token."""
        auth_service = AuthService(db)
        password = "TestPassword123!"
        auth_service.setup_master_password(password)

        token = auth_service.login(password)
        token_data = auth_service.verify_token(token)

        assert token_data is not None
        assert token_data.sub == "master"

    def test_verify_token_invalid(self, db: Session):
        """Test token verification with invalid token."""
        auth_service = AuthService(db)

        token_data = auth_service.verify_token("invalid-token")

        assert token_data is None


class TestAuthServicePasswordChange:
    """Test cases for password change functionality."""

    def test_change_password_success(self, db: Session):
        """Test successful password change."""
        auth_service = AuthService(db)
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"

        auth_service.setup_master_password(old_password)

        result = auth_service.change_master_password(old_password, new_password)

        assert result is True

        # Verify old password no longer works
        assert auth_service.verify_master_password(old_password) is False

        # Verify new password works
        assert auth_service.verify_master_password(new_password) is True

    def test_change_password_wrong_current(self, db: Session):
        """Test password change with wrong current password."""
        auth_service = AuthService(db)
        auth_service.setup_master_password("CurrentPassword!")

        result = auth_service.change_master_password("WrongPassword!", "NewPassword!")

        assert result is False
