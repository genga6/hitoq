import os
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.session import get_db
from src.db.tables import Base
from src.main import app


@pytest.fixture(scope="session")
def test_db_engine():
    """テスト用SQLiteデータベースエンジンを作成"""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)

    yield engine

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """各テスト関数用のデータベースセッションを作成"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_db_session) -> Generator[TestClient, None, None]:
    """テスト用のFastAPIクライアントを作成"""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """テスト用ユーザーデータ"""
    return {
        "user_id": "test_user_123",
        "user_name": "testuser",
        "display_name": "Test User",
        "bio": "Test bio",
        "icon_url": "https://example.com/icon.jpg",
    }


@pytest.fixture
def sample_profile_item_data():
    """テスト用プロフィールアイテムデータ"""
    return {"label": "Favorite Food", "value": "Sushi", "display_order": 1}


@pytest.fixture
def sample_bucket_list_item_data():
    """テスト用バケットリストアイテムデータ"""
    return {"content": "Visit Japan", "is_completed": False, "display_order": 1}


@pytest.fixture
def sample_answer_data():
    """テスト用回答データ"""
    return {"answer_text": "I love programming!"}


@pytest.fixture
def mock_jwt_token():
    """テスト用JWTトークン（実際の認証はスキップ）"""
    return "test_jwt_token_123"


@pytest.fixture
def authenticated_headers(mock_jwt_token):
    """認証済みリクエスト用ヘッダー"""
    return {"Authorization": f"Bearer {mock_jwt_token}"}
