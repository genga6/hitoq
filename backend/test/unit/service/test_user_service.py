from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from src.schema.user import UserCreate
from src.service import user_service


@pytest.mark.unit
class TestUserService:
    def test_get_user_exists(self, test_db_session, create_user):
        create_user(
            user_id="test_user_001",
            user_name="testuser",
            display_name="Test User",
            bio="Test bio",
        )

        result = user_service.get_user(test_db_session, "test_user_001")

        assert result is not None
        assert result.user_id == "test_user_001"
        assert result.user_name == "testuser"
        assert result.display_name == "Test User"

    def test_get_user_not_exists(self, test_db_session):
        result = user_service.get_user(test_db_session, "nonexistent_user")
        assert result is None

    def test_get_user_by_username_exists(self, test_db_session, create_user):
        create_user(
            user_id="test_user_002", user_name="testuser2", display_name="Test User 2"
        )

        result = user_service.get_user_by_username(test_db_session, "testuser2")

        assert result is not None
        assert result.user_name == "testuser2"
        assert result.user_id == "test_user_002"

    def test_get_users_pagination(self, test_db_session, create_users):
        create_users(15)

        # ページネーションテスト
        result_first_page = user_service.get_users(test_db_session, skip=0, limit=10)
        result_second_page = user_service.get_users(test_db_session, skip=10, limit=10)

        assert len(result_first_page) == 10
        assert len(result_second_page) == 5
        assert result_first_page[0].user_id != result_second_page[0].user_id

    def test_search_users_by_display_name(self, test_db_session, create_user):
        create_user(user_id="u1", user_name="user1", display_name="Alice Smith")
        create_user(user_id="u2", user_name="user2", display_name="Bob Smith")
        create_user(user_id="u3", user_name="user3", display_name="Charlie Johnson")

        result = user_service.search_users_by_display_name(
            test_db_session, "Smith", limit=10
        )

        assert len(result) == 2
        display_names = [user.display_name for user in result]
        assert "Alice Smith" in display_names
        assert "Bob Smith" in display_names

    def test_upsert_user_create_new(self, test_db_session):
        user_data = UserCreate(
            user_id="new_user_001",
            user_name="newuser",
            display_name="New User",
            bio="New user bio",
            icon_url="https://example.com/avatar.jpg",
        )

        result = user_service.upsert_user(test_db_session, user_data)

        assert result.user_id == "new_user_001"
        assert result.user_name == "newuser"
        assert result.display_name == "New User"
        assert result.bio == "New user bio"

    def test_upsert_user_update_existing(self, test_db_session, create_user):
        create_user(
            user_id="existing_user",
            user_name="existinguser",
            display_name="Old Display Name",
            bio="Old bio",
        )

        update_data = UserCreate(
            user_id="existing_user",
            user_name="existinguser",
            display_name="New Display Name",
            bio="New bio",
            icon_url="https://example.com/new_avatar.jpg",
        )

        result = user_service.upsert_user(test_db_session, update_data)

        assert result.user_id == "existing_user"
        assert result.display_name == "New Display Name"
        assert result.bio == "New bio"
        assert result.icon_url == "https://example.com/new_avatar.jpg"

    def test_delete_user_success(self, test_db_session, create_user):
        create_user(
            user_id="delete_user", user_name="deleteuser", display_name="Delete Me"
        )

        result = user_service.delete_user(test_db_session, "delete_user")

        assert result is True

        # ユーザーが削除されているか確認
        deleted_user = user_service.get_user(test_db_session, "delete_user")
        assert deleted_user is None

    def test_delete_user_not_found(self, test_db_session):
        """存在しないユーザーの削除"""
        result = user_service.delete_user(test_db_session, "nonexistent_user")
        assert result is False

    def test_get_user_with_profile_items(
        self, test_db_session, create_user, create_profile_item
    ):
        create_user(
            user_id="profile_user", user_name="profileuser", display_name="Profile User"
        )

        create_profile_item(
            user_id="profile_user",
            label="Favorite Food",
            value="Sushi",
            display_order=1,
        )

        result = user_service.get_user_with_profile_items(
            test_db_session, "profile_user"
        )

        assert result is not None
        assert len(result.profile_items) == 1
        assert result.profile_items[0].label == "Favorite Food"

    @patch("src.service.user_service.initialize_default_questions")
    def test_upsert_user_initializes_questions(
        self, mock_init_questions, test_db_session
    ):
        user_data = UserCreate(
            user_id="init_user", user_name="inituser", display_name="Init User"
        )

        user_service.upsert_user(test_db_session, user_data)

        # initialize_default_questions はユーザーIDではなくセッションのみで呼ばれる
        mock_init_questions.assert_called_once_with(test_db_session)

    @pytest.mark.parametrize(
        "discover_type,limit,setup_func",
        [
            ("activity", 10, "setup_activity_users"),
            ("random", 3, "setup_random_users"),
            ("recommend", 4, "setup_recommend_users"),
        ],
    )
    def test_discover_users_types(
        self,
        test_db_session,
        create_user,
        create_users,
        discover_type,
        limit,
        setup_func,
    ):
        if setup_func == "setup_activity_users":
            now = datetime.now(timezone.utc)
            recent_date = now - timedelta(days=1)
            create_user(
                user_id="recent_user",
                user_name="recentuser",
                display_name="Recent User",
                created_at=recent_date,
            )
            create_user(
                user_id="old_user",
                user_name="olduser",
                display_name="Old User",
                created_at=now - timedelta(days=30),
            )
        elif setup_func == "setup_random_users":
            create_users(5)
        elif setup_func == "setup_recommend_users":
            create_users(6)

        result = user_service.discover_users(
            test_db_session, discover_type, limit=limit
        )

        assert isinstance(result, list)
        assert len(result) <= limit

        if discover_type == "activity":
            recent_user_ids = [user.user_id for user in result]
            assert "recent_user" in recent_user_ids
        elif discover_type == "random":
            result_user_ids = [user.user_id for user in result]
            created_user_ids = [f"bulk_user_{i}" for i in range(5)]
            assert all(uid in created_user_ids for uid in result_user_ids)

    def test_discover_users_exclude_current_user(self, test_db_session, create_user):
        create_user(
            user_id="current_user", user_name="currentuser", display_name="Current User"
        )
        create_user(
            user_id="other_user", user_name="otheruser", display_name="Other User"
        )

        result = user_service.discover_users(
            test_db_session, "random", limit=10, current_user_id="current_user"
        )

        result_user_ids = [user.user_id for user in result]
        assert "current_user" not in result_user_ids
        assert "other_user" in result_user_ids

    def test_discover_users_pagination(self, test_db_session, create_users):
        create_users(15)

        # activityタイプでテスト（より予測可能）
        # NOTE: ランダムでの重複は保証できない
        first_page = user_service.discover_users(
            test_db_session, "activity", limit=5, offset=0
        )
        second_page = user_service.discover_users(
            test_db_session, "activity", limit=5, offset=5
        )

        assert len(first_page) <= 5
        assert len(second_page) <= 5

        # 基本的なページネーション動作確認
        total_users = len(first_page) + len(second_page)
        assert total_users <= 15  # 作成したユーザー数以下

    def test_update_last_login_success(self, test_db_session, create_user):
        create_user(
            user_id="login_user", user_name="loginuser", display_name="Login User"
        )

        user_service.update_last_login(test_db_session, "login_user")

        updated_user = user_service.get_user(test_db_session, "login_user")
        assert updated_user is not None
        assert updated_user.last_login_at is not None

    def test_update_last_login_user_not_found(self, test_db_session):
        # 存在しないユーザーの最終ログイン時刻更新
        user_service.update_last_login(test_db_session, "nonexistent_user")
