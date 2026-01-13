"""Tests for tags API endpoints."""
import pytest


class TestTagsList:
    """Test cases for GET /api/tags endpoint."""

    def test_list_tags_empty(self, client, auth_headers):
        """Test listing tags when empty."""
        response = client.get("/api/tags", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_tags_unauthorized(self, client, initialized_system):
        """Test listing tags without authentication."""
        response = client.get("/api/tags")

        assert response.status_code == 401


class TestTagCreate:
    """Test cases for POST /api/tags endpoint."""

    def test_create_tag_minimal(self, client, auth_headers):
        """Test creating tag with minimal data."""
        response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Test Tag"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Tag"
        assert "id" in data
        assert "color" in data  # Default color
        assert data["account_count"] == 0

    def test_create_tag_with_color(self, client, auth_headers):
        """Test creating tag with custom color."""
        response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Colored Tag", "color": "#ff5733"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Colored Tag"
        assert data["color"] == "#ff5733"

    def test_create_tag_duplicate_name(self, client, auth_headers):
        """Test creating tag with duplicate name."""
        # Create first tag
        client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Duplicate Tag"}
        )

        # Try to create duplicate
        response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Duplicate Tag"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"]

    def test_create_tag_unauthorized(self, client, initialized_system):
        """Test creating tag without authentication."""
        response = client.post(
            "/api/tags",
            json={"name": "Test Tag"}
        )

        assert response.status_code == 401


class TestTagGet:
    """Test cases for GET /api/tags/{id} endpoint."""

    def test_get_tag_success(self, client, auth_headers):
        """Test getting tag by ID."""
        # Create tag
        create_response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Get Test Tag"}
        )
        tag_id = create_response.json()["id"]

        # Get tag
        response = client.get(
            f"/api/tags/{tag_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Test Tag"

    def test_get_tag_not_found(self, client, auth_headers):
        """Test getting non-existent tag."""
        response = client.get(
            "/api/tags/non-existent-id",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestTagUpdate:
    """Test cases for PUT /api/tags/{id} endpoint."""

    def test_update_tag_name(self, client, auth_headers):
        """Test updating tag name."""
        # Create tag
        create_response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Original Name"}
        )
        tag_id = create_response.json()["id"]

        # Update tag
        response = client.put(
            f"/api/tags/{tag_id}",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_tag_color(self, client, auth_headers):
        """Test updating tag color."""
        # Create tag
        create_response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Color Tag"}
        )
        tag_id = create_response.json()["id"]

        # Update color
        response = client.put(
            f"/api/tags/{tag_id}",
            headers=auth_headers,
            json={"color": "#00ff00"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["color"] == "#00ff00"

    def test_update_tag_duplicate_name(self, client, auth_headers):
        """Test updating tag to duplicate name."""
        # Create two tags
        client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Tag One"}
        )
        create_response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Tag Two"}
        )
        tag_id = create_response.json()["id"]

        # Try to update to duplicate name
        response = client.put(
            f"/api/tags/{tag_id}",
            headers=auth_headers,
            json={"name": "Tag One"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"]

    def test_update_tag_not_found(self, client, auth_headers):
        """Test updating non-existent tag."""
        response = client.put(
            "/api/tags/non-existent-id",
            headers=auth_headers,
            json={"name": "Updated"}
        )

        assert response.status_code == 404


class TestTagDelete:
    """Test cases for DELETE /api/tags/{id} endpoint."""

    def test_delete_tag_success(self, client, auth_headers):
        """Test deleting tag."""
        # Create tag
        create_response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Delete Tag"}
        )
        tag_id = create_response.json()["id"]

        # Delete tag
        response = client.delete(
            f"/api/tags/{tag_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Tag deleted successfully"

        # Verify deleted
        get_response = client.get(
            f"/api/tags/{tag_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_tag_not_found(self, client, auth_headers):
        """Test deleting non-existent tag."""
        response = client.delete(
            "/api/tags/non-existent-id",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestTagAccountRelation:
    """Test cases for tag-account relationships."""

    def test_account_with_tags(self, client, auth_headers):
        """Test creating account with tags."""
        # Create tags
        tag1_response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Tag A"}
        )
        tag2_response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Tag B"}
        )
        tag1_id = tag1_response.json()["id"]
        tag2_id = tag2_response.json()["id"]

        # Create account with tags
        response = client.post(
            "/api/accounts",
            headers=auth_headers,
            json={
                "email": "tagged@example.com",
                "tag_ids": [tag1_id, tag2_id]
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["tags"]) == 2

    def test_filter_by_tag(self, client, auth_headers):
        """Test filtering accounts by tag."""
        # Create tag
        tag_response = client.post(
            "/api/tags",
            headers=auth_headers,
            json={"name": "Filter Tag"}
        )
        tag_id = tag_response.json()["id"]

        # Create accounts
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "tagged@example.com", "tag_ids": [tag_id]}
        )
        client.post(
            "/api/accounts",
            headers=auth_headers,
            json={"email": "untagged@example.com"}
        )

        # Filter by tag
        response = client.get(
            "/api/accounts",
            headers=auth_headers,
            params={"tag_ids": tag_id}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["email"] == "tagged@example.com"
