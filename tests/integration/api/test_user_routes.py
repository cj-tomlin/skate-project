"""
Integration tests for user API routes.
"""

from fastapi.testclient import TestClient

from app.domain.users.models.user import User


class TestUserRoutes:
    """Test suite for user API routes."""

    def test_get_users(
        self, client: TestClient, admin_client: TestClient, user_factory
    ):
        """Test getting all users (admin only)."""
        # Create some test users
        users = [user_factory(), user_factory(), user_factory()]

        # Test with unauthenticated client
        response = client.get("/api/v1/users/users")
        assert response.status_code == 401

        # Test with authenticated admin client
        response = admin_client.get("/api/v1/users/users")
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "items" in data
        assert "total" in data
        assert data["total"] >= len(users)  # May include other users from fixtures

    def test_get_user_by_id(
        self, client: TestClient, authenticated_client: TestClient, regular_user: User
    ):
        """Test getting a user by ID."""
        user_id = regular_user.id

        # Test with unauthenticated client
        response = client.get(f"/api/v1/users/users/{user_id}")
        assert response.status_code == 401

        # Test with authenticated client
        response = authenticated_client.get(f"/api/v1/users/users/{user_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify user data
        assert data["id"] == user_id
        assert data["username"] == regular_user.username
        assert data["email"] == regular_user.email
        assert "hashed_password" not in data  # Ensure sensitive data is not returned

    def test_get_user_by_id_not_found(self, authenticated_client: TestClient):
        """Test getting a non-existent user by ID."""
        response = authenticated_client.get("/api/v1/users/users/9999")
        assert response.status_code == 404

    def test_create_user(self, client: TestClient):
        """Test creating a new user."""
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }

        response = client.post("/api/v1/users/users", json=user_data)
        assert response.status_code == 201
        data = response.json()

        # Verify user data
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "password" not in data  # Ensure password is not returned
        assert "hashed_password" not in data  # Ensure hashed password is not returned

    def test_create_user_duplicate_username(
        self, client: TestClient, regular_user: User
    ):
        """Test creating a user with a duplicate username."""
        user_data = {
            "username": regular_user.username,  # Duplicate username
            "email": "unique@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }

        response = client.post("/api/v1/users/users", json=user_data)
        assert response.status_code == 400
        data = response.json()
        assert "username" in data["detail"].lower()  # Error message mentions username

    def test_create_user_duplicate_email(self, client: TestClient, regular_user: User):
        """Test creating a user with a duplicate email."""
        user_data = {
            "username": "uniqueuser",
            "email": regular_user.email,  # Duplicate email
            "password": "Password123!",
            "confirm_password": "Password123!",
        }

        response = client.post("/api/v1/users/users", json=user_data)
        assert response.status_code == 400
        data = response.json()
        assert "email" in data["detail"].lower()  # Error message mentions email

    def test_update_user(self, authenticated_client: TestClient, regular_user: User):
        """Test updating a user."""
        user_id = regular_user.id
        update_data = {"username": "updateduser", "bio": "Updated bio for testing"}

        response = authenticated_client.put(
            f"/api/v1/users/users/{user_id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()

        # Verify updated data
        assert data["username"] == update_data["username"]
        assert data["bio"] == update_data["bio"]
        assert data["id"] == user_id

    def test_update_other_user_forbidden(
        self, authenticated_client: TestClient, user_factory
    ):
        """Test updating another user (should be forbidden)."""
        # Create another user
        other_user = user_factory()

        update_data = {
            "username": "hacker",
            "bio": "I shouldn't be able to update this",
        }

        response = authenticated_client.put(
            f"/api/v1/users/users/{other_user.id}", json=update_data
        )
        assert response.status_code == 403

    def test_delete_user(self, admin_client: TestClient, user_factory):
        """Test deleting a user (admin only)."""
        # Create a user to delete
        user_to_delete = user_factory()

        response = admin_client.delete(f"/api/v1/users/users/{user_to_delete.id}")
        assert response.status_code == 204

        # Verify user is deleted
        response = admin_client.get(f"/api/v1/users/users/{user_to_delete.id}")
        assert response.status_code == 404

    def test_delete_user_forbidden(
        self, authenticated_client: TestClient, user_factory
    ):
        """Test deleting a user without admin privileges (should be forbidden)."""
        # Create a user to delete
        user_to_delete = user_factory()

        response = authenticated_client.delete(
            f"/api/v1/users/users/{user_to_delete.id}"
        )
        assert response.status_code == 403

    def test_get_current_user(
        self, authenticated_client: TestClient, regular_user: User
    ):
        """Test getting the current authenticated user."""
        response = authenticated_client.get("/api/v1/users/users/me")
        assert response.status_code == 200
        data = response.json()

        # Verify user data
        assert data["id"] == regular_user.id
        assert data["username"] == regular_user.username
        assert data["email"] == regular_user.email
