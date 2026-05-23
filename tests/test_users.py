import pytest


class TestCreateUser:
    def test_create_user_success(self, client, sample_user_payload):
        response = client.post("/api/v1/users/", json=sample_user_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user_payload["username"]
        assert data["email"] == sample_user_payload["email"]
        assert data["role"] == "user"
        assert data["active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_user_duplicate_username(self, client, created_user, sample_user_payload):
        payload = {**sample_user_payload, "email": "other@example.com"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 409
        assert "username" in response.json()["detail"].lower()

    def test_create_user_duplicate_email(self, client, created_user, sample_user_payload):
        payload = {**sample_user_payload, "username": "otherusername"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 409
        assert "email" in response.json()["detail"].lower()

    def test_create_user_invalid_email(self, client, sample_user_payload):
        payload = {**sample_user_payload, "email": "not-an-email"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 422

    def test_create_user_invalid_role(self, client, sample_user_payload):
        payload = {**sample_user_payload, "role": "superadmin"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 422

    def test_create_user_username_too_short(self, client, sample_user_payload):
        payload = {**sample_user_payload, "username": "ab"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 422

    def test_create_user_username_invalid_chars(self, client, sample_user_payload):
        payload = {**sample_user_payload, "username": "user name!"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 422

    def test_create_user_username_normalized_to_lowercase(self, client, sample_user_payload):
        payload = {**sample_user_payload, "username": "TestUser123"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 201
        assert response.json()["username"] == "testuser123"

    def test_create_user_admin_role(self, client, sample_user_payload):
        payload = {**sample_user_payload, "role": "admin"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 201
        assert response.json()["role"] == "admin"

    def test_create_user_missing_required_fields(self, client):
        response = client.post("/api/v1/users/", json={"username": "onlyusername"})
        assert response.status_code == 422


class TestGetUser:
    def test_get_user_success(self, client, created_user):
        user_id = created_user["id"]
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    def test_get_user_not_found(self, client):
        response = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_get_user_returns_all_fields(self, client, created_user):
        response = client.get(f"/api/v1/users/{created_user['id']}")
        data = response.json()
        for field in ["id", "username", "email", "first_name", "last_name", "role", "active", "created_at", "updated_at"]:
            assert field in data


class TestListUsers:
    def test_list_users_empty(self, client):
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["users"] == []

    def test_list_users_returns_created(self, client, created_user):
        response = client.get("/api/v1/users/")
        data = response.json()
        assert data["total"] == 1
        assert data["users"][0]["id"] == created_user["id"]

    def test_list_users_pagination(self, client, client_with_multiple_users):
        response = client.get("/api/v1/users/?skip=0&limit=2")
        data = response.json()
        assert len(data["users"]) == 2
        assert data["total"] == 3

    def test_list_users_skip(self, client, client_with_multiple_users):
        response = client.get("/api/v1/users/?skip=2&limit=10")
        data = response.json()
        assert len(data["users"]) == 1

    @pytest.fixture
    def client_with_multiple_users(self, client):
        users = [
            {"username": "user1", "email": "u1@example.com", "first_name": "A", "last_name": "B"},
            {"username": "user2", "email": "u2@example.com", "first_name": "C", "last_name": "D"},
            {"username": "user3", "email": "u3@example.com", "first_name": "E", "last_name": "F"},
        ]
        for u in users:
            client.post("/api/v1/users/", json=u)


class TestUpdateUser:
    def test_update_user_success(self, client, created_user):
        user_id = created_user["id"]
        response = client.put(f"/api/v1/users/{user_id}", json={"first_name": "Updated"})
        assert response.status_code == 200
        assert response.json()["first_name"] == "Updated"

    def test_update_user_partial(self, client, created_user):
        user_id = created_user["id"]
        response = client.put(f"/api/v1/users/{user_id}", json={"role": "guest"})
        data = response.json()
        assert data["role"] == "guest"
        assert data["username"] == created_user["username"]

    def test_update_user_not_found(self, client):
        response = client.put(
            "/api/v1/users/00000000-0000-0000-0000-000000000000",
            json={"first_name": "Ghost"},
        )
        assert response.status_code == 404

    def test_update_user_duplicate_username(self, client, created_user):
        client.post("/api/v1/users/", json={
            "username": "seconduser",
            "email": "second@example.com",
            "first_name": "B",
            "last_name": "C",
        })
        response = client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"username": "seconduser"},
        )
        assert response.status_code == 409

    def test_update_user_duplicate_email(self, client, created_user):
        client.post("/api/v1/users/", json={
            "username": "seconduser",
            "email": "second@example.com",
            "first_name": "B",
            "last_name": "C",
        })
        response = client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"email": "second@example.com"},
        )
        assert response.status_code == 409

    def test_update_user_updated_at_changes(self, client, created_user):
        user_id = created_user["id"]
        response = client.put(f"/api/v1/users/{user_id}", json={"first_name": "New"})
        assert response.json()["updated_at"] >= created_user["updated_at"]

    def test_update_user_deactivate(self, client, created_user):
        user_id = created_user["id"]
        response = client.put(f"/api/v1/users/{user_id}", json={"active": False})
        assert response.json()["active"] is False


class TestDeleteUser:
    def test_delete_user_success(self, client, created_user):
        user_id = created_user["id"]
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204

    def test_delete_user_not_found_after_delete(self, client, created_user):
        user_id = created_user["id"]
        client.delete(f"/api/v1/users/{user_id}")
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 404

    def test_delete_user_not_found(self, client):
        response = client.delete("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_delete_removes_from_list(self, client, created_user):
        client.delete(f"/api/v1/users/{created_user['id']}")
        response = client.get("/api/v1/users/")
        assert response.json()["total"] == 0


class TestHealthCheck:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
