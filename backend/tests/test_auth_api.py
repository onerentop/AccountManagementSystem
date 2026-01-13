"""Tests for authentication API endpoints."""
import pytest


class TestAuthStatus:
    """Test cases for /api/auth/status endpoint."""

    def test_status_not_initialized(self, client):
        """Test system status when not initialized."""
        response = client.get("/api/auth/status")

        assert response.status_code == 200
        data = response.json()
        assert data["is_initialized"] is False
        assert data["is_locked"] is True

    def test_status_after_setup(self, client, initialized_system):
        """Test system status after initialization."""
        response = client.get("/api/auth/status")

        assert response.status_code == 200
        data = response.json()
        assert data["is_initialized"] is True
        assert data["is_locked"] is False  # Unlocked after setup


class TestAuthSetup:
    """Test cases for /api/auth/setup endpoint."""

    def test_setup_success(self, client):
        """Test successful master password setup."""
        response = client.post(
            "/api/auth/setup",
            json={"password": "SecurePassword123!", "confirm_password": "SecurePassword123!"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Master password set successfully"

    def test_setup_already_initialized(self, client, initialized_system):
        """Test setup when system is already initialized."""
        response = client.post(
            "/api/auth/setup",
            json={"password": "AnotherPassword456!", "confirm_password": "AnotherPassword456!"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "already initialized" in data["detail"]


class TestAuthLogin:
    """Test cases for /api/auth/login endpoint."""

    def test_login_success(self, client, initialized_system):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={"password": initialized_system["password"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "expires_in" in data
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client, initialized_system):
        """Test login with wrong password."""
        response = client.post(
            "/api/auth/login",
            json={"password": "WrongPassword!"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Incorrect password" in data["detail"]

    def test_login_not_initialized(self, client):
        """Test login when system is not initialized."""
        response = client.post(
            "/api/auth/login",
            json={"password": "AnyPassword123!"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "not initialized" in data["detail"]


class TestAuthLogout:
    """Test cases for /api/auth/logout endpoint."""

    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post("/api/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

    def test_logout_unauthorized(self, client, initialized_system):
        """Test logout without authentication."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 401


class TestAuthLock:
    """Test cases for /api/auth/lock endpoint."""

    def test_lock_success(self, client, auth_headers):
        """Test successful application lock."""
        response = client.post("/api/auth/lock", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Application locked"

    def test_lock_unauthorized(self, client, initialized_system):
        """Test lock without authentication."""
        response = client.post("/api/auth/lock")

        assert response.status_code == 401


class TestPasswordChange:
    """Test cases for /api/auth/password endpoint."""

    def test_change_password_success(self, client, auth_headers, initialized_system):
        """Test successful password change."""
        response = client.put(
            "/api/auth/password",
            headers=auth_headers,
            json={
                "current_password": initialized_system["password"],
                "new_password": "NewSecurePassword456!",
                "confirm_password": "NewSecurePassword456!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"

        # Verify can login with new password
        login_response = client.post(
            "/api/auth/login",
            json={"password": "NewSecurePassword456!"}
        )
        assert login_response.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        """Test password change with wrong current password."""
        response = client.put(
            "/api/auth/password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword!",
                "new_password": "NewPassword456!",
                "confirm_password": "NewPassword456!"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "incorrect" in data["detail"].lower()

    def test_change_password_unauthorized(self, client, initialized_system):
        """Test password change without authentication."""
        response = client.put(
            "/api/auth/password",
            json={
                "current_password": initialized_system["password"],
                "new_password": "NewPassword456!"
            }
        )

        assert response.status_code == 401
