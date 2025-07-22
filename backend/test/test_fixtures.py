import pytest
from sqlalchemy.orm import Session

from src.schema.user import UserCreate
from src.service import user_service


def create_test_user(db: Session, user_data: dict | None = None):
    """テスト用ユーザーを作成し、作成されたユーザー情報を返す"""
    if user_data is None:
        user_data = {
            "user_id": "test_user_123",
            "user_name": "testuser",
            "display_name": "Test User",
            "bio": "Test bio",
            "icon_url": "https://example.com/icon.jpg",
        }

    user_create = UserCreate(**user_data)
    user = user_service.upsert_user(db, user_in=user_create)
    return user


def create_multiple_test_users(db: Session, count: int = 3) -> list:
    """複数のテストユーザーを作成"""
    users = []
    for i in range(count):
        user_data = {
            "user_id": f"test_user_{i}",
            "user_name": f"testuser{i}",
            "display_name": f"Test User {i}",
            "bio": f"Test bio {i}",
            "icon_url": f"https://example.com/icon{i}.jpg",
        }
        user = create_test_user(db, user_data)
        users.append(user)
    return users


@pytest.fixture
def test_user_in_db(test_db_session, sample_user_data):
    """データベースにテストユーザーを作成するフィクスチャ"""
    return create_test_user(test_db_session, sample_user_data)


@pytest.fixture
def multiple_test_users_in_db(test_db_session):
    """データベースに複数のテストユーザーを作成するフィクスチャ"""
    return create_multiple_test_users(test_db_session, 5)
