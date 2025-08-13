from unittest.mock import patch

import pytest
from fastapi import status

from src.db.tables import User


@pytest.mark.integration
class TestUserRouter:
    """ユーザールーターの統合テスト"""

    def test_upsert_user_create_new(self, client, test_db_session):
        """新規ユーザー作成のテスト"""
        user_data = {
            "user_id": "new_router_user",
            "user_name": "newrouteruser",
            "display_name": "New Router User",
            "bio": "Created via router test",
            "icon_url": "https://example.com/router_avatar.jpg",
        }

        response = client.post("/users", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        assert response_data["user_id"] == "new_router_user"
        assert response_data["user_name"] == "newrouteruser"
        assert response_data["display_name"] == "New Router User"
        assert response_data["bio"] == "Created via router test"

    def test_upsert_user_update_existing(self, client, test_db_session):
        """既存ユーザー更新のテスト"""
        # 既存ユーザーを作成
        existing_user = User(
            user_id="existing_router_user",
            user_name="existingrouteruser",
            display_name="Old Display Name",
            bio="Old bio",
        )
        test_db_session.add(existing_user)
        test_db_session.commit()

        # 更新データ
        update_data = {
            "user_id": "existing_router_user",
            "user_name": "existingrouteruser",
            "display_name": "Updated Display Name",
            "bio": "Updated bio via router",
            "icon_url": "https://example.com/updated_avatar.jpg",
        }

        response = client.post("/users", json=update_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        assert response_data["display_name"] == "Updated Display Name"
        assert response_data["bio"] == "Updated bio via router"
        assert response_data["icon_url"] == "https://example.com/updated_avatar.jpg"

    def test_read_all_users(self, client, test_db_session):
        """全ユーザー取得のテスト"""
        # テストユーザーを作成
        users = []
        for i in range(3):
            user = User(
                user_id=f"list_user_{i}",
                user_name=f"listuser{i}",
                display_name=f"List User {i}",
            )
            users.append(user)
            test_db_session.add(user)
        test_db_session.commit()

        response = client.get("/users")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) >= 3

        user_ids = [user["user_id"] for user in response_data]
        assert "list_user_0" in user_ids
        assert "list_user_1" in user_ids
        assert "list_user_2" in user_ids

    def test_read_all_users_pagination(self, client, test_db_session):
        """ユーザー取得のページネーションテスト"""
        # 複数のユーザーを作成
        for i in range(15):
            user = User(
                user_id=f"page_user_{i:02d}",
                user_name=f"pageuser{i:02d}",
                display_name=f"Page User {i:02d}",
            )
            test_db_session.add(user)
        test_db_session.commit()

        # 最初のページ
        response_page1 = client.get("/users?skip=0&limit=10")
        assert response_page1.status_code == status.HTTP_200_OK
        page1_data = response_page1.json()
        assert len(page1_data) == 10

        # 次のページ
        response_page2 = client.get("/users?skip=10&limit=10")
        assert response_page2.status_code == status.HTTP_200_OK
        page2_data = response_page2.json()
        assert len(page2_data) >= 5  # 新しく作成した5つ + 既存のユーザー

        # ページ間でユーザーが重複していないことを確認
        page1_user_ids = {user["user_id"] for user in page1_data}
        page2_user_ids = {user["user_id"] for user in page2_data}
        overlap = page1_user_ids.intersection(page2_user_ids)
        assert len(overlap) == 0

    @patch("src.router.user_router.get_current_user_optional")
    def test_discover_users_random(self, mock_auth, client, test_db_session):
        """ランダムユーザー発見のテスト"""
        mock_auth.return_value = None

        # テストユーザーを作成
        for i in range(5):
            user = User(
                user_id=f"discover_user_{i}",
                user_name=f"discoveruser{i}",
                display_name=f"Discover User {i}",
            )
            test_db_session.add(user)
        test_db_session.commit()

        response = client.get("/users/discover?type=random&limit=3")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) <= 3

        for user in response_data:
            assert "user_id" in user
            assert "user_name" in user
            assert "display_name" in user

    @patch("src.router.user_router.get_current_user_optional")
    def test_discover_users_activity(self, mock_auth, client, test_db_session):
        """アクティブユーザー発見のテスト"""
        mock_auth.return_value = None

        # テストユーザーを作成
        for i in range(3):
            user = User(
                user_id=f"active_user_{i}",
                user_name=f"activeuser{i}",
                display_name=f"Active User {i}",
            )
            test_db_session.add(user)
        test_db_session.commit()

        response = client.get("/users/discover?type=activity&limit=5")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) <= 5

    @patch("src.router.user_router.get_current_user_optional")
    def test_discover_users_mixed(self, mock_auth, client, test_db_session):
        """混合ユーザー発見のテスト（デフォルト）"""
        mock_auth.return_value = None

        # テストユーザーを作成
        for i in range(4):
            user = User(
                user_id=f"mixed_user_{i}",
                user_name=f"mixeduser{i}",
                display_name=f"Mixed User {i}",
            )
            test_db_session.add(user)
        test_db_session.commit()

        response = client.get("/users/discover")  # デフォルトは mixed

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)

    def test_discover_users_invalid_type(self, client):
        """無効なdiscovery typeのテスト"""
        response = client.get("/users/discover?type=invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_discover_users_invalid_limit(self, client):
        """無効なlimitのテスト"""
        response = client.get("/users/discover?limit=100")  # 50が上限

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_users_by_display_name(self, client, test_db_session):
        """表示名でユーザー検索のテスト"""
        # 検索用テストユーザーを作成
        search_users = [
            User(user_id="search1", user_name="search1", display_name="John Smith"),
            User(user_id="search2", user_name="search2", display_name="Jane Smith"),
            User(user_id="search3", user_name="search3", display_name="Bob Johnson"),
        ]
        for user in search_users:
            test_db_session.add(user)
        test_db_session.commit()

        response = client.get("/users/search?display_name=Smith")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert len(response_data) == 2
        display_names = [user["display_name"] for user in response_data]
        assert "John Smith" in display_names
        assert "Jane Smith" in display_names

    def test_search_users_no_results(self, client, test_db_session):
        """ユーザー検索で結果なしのテスト"""
        response = client.get("/users/search?display_name=NonExistentUser")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert len(response_data) == 0

    def test_upsert_user_invalid_data(self, client):
        """無効なデータでのユーザー作成テスト"""
        invalid_data = {
            "user_id": "",  # 空のuser_id
            "user_name": "testuser",
            "display_name": "Test User",
        }

        response = client.post("/users", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_upsert_user_missing_required_fields(self, client):
        """必須フィールドが不足している場合のテスト"""
        incomplete_data = {
            "user_id": "test_user",
            # user_name と display_name が不足
        }

        response = client.post("/users", json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
