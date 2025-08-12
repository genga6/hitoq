from unittest.mock import Mock, patch

import pytest

from src.db.tables import User
from src.schema.user import UserCreate, UserUpdate
from src.service.user_service import UserService


class TestUserService:
    @pytest.fixture
    def mock_session(self):
        return Mock()

    @pytest.fixture
    def user_service(self):
        return UserService()

    def test_create_user_success(self, user_service, mock_session):
        """ユーザー作成成功"""
        # データ準備
        user_data = UserCreate(
            twitter_user_id="123456789", username="test_user", display_name="Test User"
        )

        # モック設定
        mock_session.query().filter().first.return_value = None  # 既存ユーザーなし
        created_user = User(id=1, **user_data.dict())

        with patch("src.service.user_service.User", return_value=created_user):
            result = user_service.create_user(mock_session, user_data)

        assert result.username == "test_user"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_user_duplicate_fails(self, user_service, mock_session):
        """重複ユーザー作成エラー"""
        user_data = UserCreate(
            twitter_user_id="123456789", username="test_user", display_name="Test"
        )
        mock_session.query().filter().first.return_value = User(
            id=1
        )  # 既存ユーザーあり

        with pytest.raises(ValueError):
            user_service.create_user(mock_session, user_data)

    @pytest.mark.parametrize("user_id,exists", [(1, True), (999, False)])
    def test_get_user_by_id(self, user_service, mock_session, user_id, exists):
        """IDでユーザー取得"""
        if exists:
            mock_session.query().filter().first.return_value = User(
                id=user_id, username="test"
            )
        else:
            mock_session.query().filter().first.return_value = None

        result = user_service.get_user_by_id(mock_session, user_id)

        if exists:
            assert result is not None
            assert result.id == user_id
        else:
            assert result is None

    @pytest.mark.parametrize(
        "username,valid",
        [
            ("test_user", True),
            ("user123", True),
            ("", False),
            ("user space", False),
            ("user-dash", False),
        ],
    )
    def test_validate_username(self, user_service, username, valid):
        """ユーザー名検証"""
        result = user_service._validate_username_format(username)
        assert result == valid

    def test_update_user(self, user_service, mock_session):
        """ユーザー更新"""
        user = User(id=1, display_name="Old Name")
        mock_session.query().filter().first.return_value = user

        update_data = UserUpdate(display_name="New Name")
        result = user_service.update_user(mock_session, 1, update_data)

        assert result.display_name == "New Name"
        mock_session.commit.assert_called_once()

    def test_delete_user(self, user_service, mock_session):
        """ユーザー削除"""
        user = User(id=1)
        mock_session.query().filter().first.return_value = user

        result = user_service.delete_user(mock_session, 1)

        assert result is True
        mock_session.delete.assert_called_once_with(user)
        mock_session.commit.assert_called_once()


@pytest.mark.unit
class TestUserValidation:
    @pytest.mark.parametrize(
        "display_name,expected",
        [
            ("Normal Name", "Normal Name"),
            ("  Spaces  ", "Spaces"),
            ("", ""),
            ("A" * 100, "A" * 50),
        ],
    )
    def test_sanitize_display_name(self, display_name, expected):
        """表示名サニタイゼーション"""
        service = UserService()
        result = service._sanitize_display_name(display_name)
        assert result == expected
