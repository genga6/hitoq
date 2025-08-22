import pytest
from fastapi import status

from src.main import app
from src.router.user_router import get_current_user_optional

# User クラスのimportは不要（create_userヘルパーを使用）


@pytest.mark.integration
class TestUserRouter:
    def test_upsert_user_create_new(self, client, test_db_session, csrf_headers):
        user_data = {
            "user_id": "new_router_user",
            "user_name": "newrouteruser",
            "display_name": "New Router User",
            "bio": "Created via router test",
            "icon_url": "https://example.com/router_avatar.jpg",
        }

        response = client.post("/users", json=user_data, headers=csrf_headers)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        assert response_data["userId"] == "new_router_user"
        assert response_data["userName"] == "newrouteruser"
        assert response_data["displayName"] == "New Router User"
        assert response_data["bio"] == "Created via router test"

    def test_upsert_user_update_existing(
        self, client, test_db_session, create_user, csrf_headers
    ):
        create_user(
            user_id="existing_router_user",
            user_name="existingrouteruser",
            display_name="Old Display Name",
            bio="Old bio",
        )

        update_data = {
            "user_id": "existing_router_user",
            "user_name": "existingrouteruser",
            "display_name": "Updated Display Name",
            "bio": "Updated bio via router",
            "icon_url": "https://example.com/updated_avatar.jpg",
        }

        response = client.post("/users", json=update_data, headers=csrf_headers)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        assert response_data["displayName"] == "Updated Display Name"
        assert response_data["bio"] == "Updated bio via router"
        assert response_data["iconUrl"] == "https://example.com/updated_avatar.jpg"

    def test_read_all_users(self, client, test_db_session, create_users):
        create_users(3)

        response = client.get("/users")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) >= 3

        user_ids = [user["userId"] for user in response_data]
        assert "bulk_user_0" in user_ids
        assert "bulk_user_1" in user_ids
        assert "bulk_user_2" in user_ids

    def test_read_all_users_pagination(self, client, test_db_session, create_users):
        create_users(15)

        response_page1 = client.get("/users?skip=0&limit=10")
        assert response_page1.status_code == status.HTTP_200_OK
        page1_data = response_page1.json()
        assert len(page1_data) == 10

        # 次のページ
        response_page2 = client.get("/users?skip=10&limit=10")
        assert response_page2.status_code == status.HTTP_200_OK
        page2_data = response_page2.json()
        assert len(page2_data) >= 5  # 残りのユーザー + 既存のユーザー

        # ページ間でユーザーが重複していないことを確認
        page1_user_ids = {user["userId"] for user in page1_data}
        page2_user_ids = {user["userId"] for user in page2_data}
        overlap = page1_user_ids.intersection(page2_user_ids)
        assert len(overlap) == 0

    def test_discover_users_random(self, client, test_db_session, create_users):
        def override_get_current_user_optional(request=None, db=None):
            return None

        app.dependency_overrides[get_current_user_optional] = (
            override_get_current_user_optional
        )

        create_users(5)

        try:
            response = client.get("/users/discover?type=random&limit=3")

            assert response.status_code == status.HTTP_200_OK
        finally:
            app.dependency_overrides.pop(get_current_user_optional, None)
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) <= 3

        for user in response_data:
            assert "userId" in user
            assert "userName" in user
            assert "displayName" in user

    def test_discover_users_activity(self, client, test_db_session, create_users):
        def override_get_current_user_optional(request=None, db=None):
            return None

        app.dependency_overrides[get_current_user_optional] = (
            override_get_current_user_optional
        )

        create_users(3)

        try:
            response = client.get("/users/discover?type=activity&limit=5")

            assert response.status_code == status.HTTP_200_OK
        finally:
            app.dependency_overrides.pop(get_current_user_optional, None)
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) <= 5

    def test_discover_users_mixed(self, client, test_db_session, create_users):
        def override_get_current_user_optional(request=None, db=None):
            return None

        app.dependency_overrides[get_current_user_optional] = (
            override_get_current_user_optional
        )

        create_users(4)

        try:
            response = client.get("/users/discover")  # デフォルトは recommend

            assert response.status_code == status.HTTP_200_OK
        finally:
            app.dependency_overrides.pop(get_current_user_optional, None)
        response_data = response.json()

        assert isinstance(response_data, list)

    def test_discover_users_invalid_type(self, client):
        response = client.get("/users/discover?type=invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_discover_users_invalid_limit(self, client):
        response = client.get("/users/discover?limit=100")  # 50が上限

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_users_by_display_name(self, client, test_db_session, create_user):
        # 特定の表示名でユーザーを作成
        create_user(user_id="search1", user_name="search1", display_name="John Smith")
        create_user(user_id="search2", user_name="search2", display_name="Jane Smith")
        create_user(user_id="search3", user_name="search3", display_name="Bob Johnson")

        response = client.get("/users/search/users?q=Smith")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert len(response_data) == 2
        display_names = [user["displayName"] for user in response_data]
        assert "John Smith" in display_names
        assert "Jane Smith" in display_names

    def test_search_users_no_results(self, client, test_db_session):
        response = client.get("/users/search/users?q=NonExistentUser")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert len(response_data) == 0

    def test_upsert_user_invalid_data(self, client, csrf_headers):
        invalid_data = {
            "user_id": "",  # 空のuser_id
            "user_name": "testuser",
            "display_name": "Test User",
        }

        response = client.post("/users", json=invalid_data, headers=csrf_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_upsert_user_missing_required_fields(self, client, csrf_headers):
        incomplete_data = {
            "user_id": "test_user",
            # user_name と display_name が不足
        }

        response = client.post("/users", json=incomplete_data, headers=csrf_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
