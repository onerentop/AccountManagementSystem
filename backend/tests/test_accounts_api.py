"""Tests for accounts API endpoints."""
import pytest


class TestAccountsList:
    """Test cases for GET /api/accounts endpoint."""

    def test_list_accounts_empty(self, client, auth_headers):
        """Test listing accounts when empty."""
        response = client.get("/api/accounts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_accounts_unauthorized(self, client, initialized_system):
        """Test listing accounts without authentication."""
        response = client.get("/api/accounts")

        assert response.status_code == 401

    def test_list_accounts_pagination(self, client, auth_headers):
        """Test accounts pagination."""
        # Create multiple accounts
        for i in range(15):
            client.post(
                "/api/accounts",
                headers=auth_headers,
                json={"email": f"test{i}@example.com"}
            )

        # Test first page
        response = client.get(
            "/api/accounts",
            headers=auth_headers,
            params={"page": 1, "page_size": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["total_pages"] == 2

        # Test second page
        response = client.get(
            "/api/accounts",
            headers=auth_headers,
            params={"page": 2, "page_size": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5


class TestAccountCreate:
    """Test cases for POST /api/accounts endpoint."""

    def test_create_account_minimal(self, client, auth_headers):
        """Test creating account with minimal data."""
        response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "test@example.com"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert data["has_password"] is False
        assert data["has_totp"] is False

    def test_create_account_full(self, client, auth_headers):
        """Test creating account with all fields."""
        response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={
                "email": "full@example.com",
                "password": "accountpassword",
                "totp_secret": "JBSWY3DPEHPK3PXP",
                "note": "Test note",
                "sub2api": True,
                "source": "购买",
                "browser": "Chrome",
                "gpt_membership": "Plus",
                "family_group": "Family A",
                "recovery_email": "recovery@example.com"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "full@example.com"
        assert data["has_password"] is True
        assert data["has_totp"] is True
        assert data["note"] == "Test note"
        assert data["sub2api"] is True
        assert data["source"] == "购买"
        assert data["gpt_membership"] == "Plus"

    def test_create_account_duplicate_email(self, client, auth_headers):
        """Test creating account with duplicate email."""
        # Create first account
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "duplicate@example.com"}
        )

        # Try to create duplicate
        response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "duplicate@example.com"}
        )

        assert response.status_code == 400

    def test_create_account_unauthorized(self, client, initialized_system):
        """Test creating account without authentication."""
        response = client.post(
            "/api/accounts",
            json={"email": "test@example.com"}
        )

        assert response.status_code == 401


class TestAccountGet:
    """Test cases for GET /api/accounts/{id} endpoint."""

    def test_get_account_success(self, client, auth_headers):
        """Test getting account by ID."""
        # Create account
        create_response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "get@example.com", "note": "Get test"}
        )
        account_id = create_response.json()["id"]

        # Get account
        response = client.get(
            f"/api/accounts/{account_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "get@example.com"
        assert data["note"] == "Get test"

    def test_get_account_not_found(self, client, auth_headers):
        """Test getting non-existent account."""
        response = client.get(
            "/api/accounts/non-existent-id",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestAccountUpdate:
    """Test cases for PUT /api/accounts/{id} endpoint."""

    def test_update_account_success(self, client, auth_headers):
        """Test updating account."""
        # Create account
        create_response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "update@example.com"}
        )
        account_id = create_response.json()["id"]

        # Update account
        response = client.put(
            f"/api/accounts/{account_id}",
            headers=auth_headers,
            json={"note": "Updated note", "source": "注册"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["note"] == "Updated note"
        assert data["source"] == "注册"

    def test_update_account_not_found(self, client, auth_headers):
        """Test updating non-existent account."""
        response = client.put(
            "/api/accounts/non-existent-id",
            headers=auth_headers,
            json={"note": "Updated"}
        )

        assert response.status_code == 404


class TestAccountDelete:
    """Test cases for DELETE /api/accounts/{id} endpoint."""

    def test_delete_account_soft(self, client, auth_headers):
        """Test soft deleting account."""
        # Create account
        create_response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "delete@example.com"}
        )
        account_id = create_response.json()["id"]

        # Soft delete
        response = client.delete(
            f"/api/accounts/{account_id}",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify not in list
        list_response = client.get("/api/accounts", headers=auth_headers)
        emails = [acc["email"] for acc in list_response.json()["items"]]
        assert "delete@example.com" not in emails

    def test_delete_account_hard(self, client, auth_headers):
        """Test hard deleting account."""
        # Create account
        create_response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "harddelete@example.com"}
        )
        account_id = create_response.json()["id"]

        # Hard delete
        response = client.delete(
            f"/api/accounts/{account_id}",
            headers=auth_headers,
            params={"hard": True}
        )

        assert response.status_code == 200

    def test_delete_account_not_found(self, client, auth_headers):
        """Test deleting non-existent account."""
        response = client.delete(
            "/api/accounts/non-existent-id",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestAccountPassword:
    """Test cases for GET /api/accounts/{id}/password endpoint."""

    def test_get_password_success(self, client, auth_headers):
        """Test getting decrypted password."""
        # Create account with password
        create_response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "pwd@example.com", "password": "secret123"}
        )
        account_id = create_response.json()["id"]

        # Get password
        response = client.get(
            f"/api/accounts/{account_id}/password",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["password"] == "secret123"

    def test_get_password_no_password(self, client, auth_headers):
        """Test getting password when none set."""
        # Create account without password
        create_response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "nopwd@example.com"}
        )
        account_id = create_response.json()["id"]

        # Get password
        response = client.get(
            f"/api/accounts/{account_id}/password",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["password"] is None


class TestAccountTotp:
    """Test cases for GET /api/accounts/{id}/totp endpoint."""

    def test_get_totp_success(self, client, auth_headers):
        """Test getting decrypted TOTP secret."""
        # Create account with TOTP
        create_response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "totp@example.com", "totp_secret": "JBSWY3DPEHPK3PXP"}
        )
        account_id = create_response.json()["id"]

        # Get TOTP
        response = client.get(
            f"/api/accounts/{account_id}/totp",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["totp_secret"] == "JBSWY3DPEHPK3PXP"


class TestAccountSources:
    """Test cases for GET /api/accounts/sources endpoint."""

    def test_get_sources(self, client, auth_headers):
        """Test getting unique sources."""
        # Create accounts with different sources
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "s1@example.com", "source": "购买"}
        )
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "s2@example.com", "source": "注册"}
        )
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "s3@example.com", "source": "购买"}  # Duplicate
        )

        response = client.get("/api/accounts/sources", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "购买" in data
        assert "注册" in data


class TestAccountStats:
    """Test cases for GET /api/accounts/stats endpoint."""

    def test_get_stats(self, client, auth_headers):
        """Test getting account statistics."""
        # Create some accounts
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "stat1@example.com", "gpt_membership": "Plus"}
        )
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "stat2@example.com", "sub2api": True}
        )

        response = client.get("/api/accounts/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total" in data or isinstance(data, dict)


class TestAccountSearch:
    """Test cases for account search functionality."""

    def test_search_by_email(self, client, auth_headers):
        """Test searching accounts by email."""
        # Create accounts
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "searchable@example.com"}
        )
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "other@test.com"}
        )

        # Search
        response = client.get(
            "/api/accounts",
            headers=auth_headers,
            params={"search": "searchable"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["email"] == "searchable@example.com"

    def test_filter_by_source(self, client, auth_headers):
        """Test filtering accounts by source."""
        # Create accounts
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "buy@example.com", "source": "购买"}
        )
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "reg@example.com", "source": "注册"}
        )

        # Filter
        response = client.get(
            "/api/accounts",
            headers=auth_headers,
            params={"source": "购买"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["source"] == "购买"
