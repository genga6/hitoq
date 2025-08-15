import os
import tempfile
import uuid
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.session import get_db
from src.db.tables import Answer, Base, ProfileItem, Question, User
from src.main import app
from src.service.config_manager import ConfigManager


@pytest.fixture(scope="session")
def test_db_engine():
    # テスト用インメモリSQLiteでPostgreSQLの振る舞いをエミュレート
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        # PostgreSQLとの互換性を高めるためのPRAGMA設定
        poolclass=None,
    )

    Base.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )

    # トランザクションベースのテストセッション
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(test_db_session) -> Generator[TestClient, None, None]:
    # router テストでは実際のAPIエンドポイントをテストするため、
    # 環境変数を事前に設定してからアプリをインポートする

    # 必要な環境変数を設定（GitHub Actions用）
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    os.environ.setdefault("SECRET_KEY", "test_secret_key_for_jwt")
    os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key")
    os.environ.setdefault("TWITTER_CLIENT_ID", "test_client_id")
    os.environ.setdefault("TWITTER_CLIENT_SECRET", "test_client_secret")
    os.environ.setdefault("ENVIRONMENT", "testing")
    os.environ.setdefault("SESSION_SECRET_KEY", "test_session_secret")
    os.environ.setdefault("DB_USER", "test_user")
    os.environ.setdefault("DB_PASSWORD", "test_password")
    os.environ.setdefault("DB_HOST", "localhost")
    os.environ.setdefault("DB_PORT", "5432")
    os.environ.setdefault("DB_NAME", "test_db")

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
def create_user(test_db_session):
    created_users: list = []

    def _create_user(
        user_id: str | None = None,
        user_name: str | None = None,
        display_name: str | None = None,
        **kwargs,
    ):
        user_num = len(created_users) + 1
        user_data = {
            "user_id": user_id or f"test_user_{user_num}",
            "user_name": user_name or f"testuser{user_num}",
            "display_name": display_name or f"Test User {user_num}",
            **kwargs,
        }

        user = User(**user_data)
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        created_users.append(user)
        return user

    return _create_user


@pytest.fixture
def create_users(create_user):
    def _create_users(count: int, **common_kwargs):
        users = []
        for i in range(count):
            user_kwargs = {
                "user_id": f"bulk_user_{i}",
                "user_name": f"bulkuser{i}",
                "display_name": f"Bulk User {i}",
                **common_kwargs,
            }
            users.append(create_user(**user_kwargs))
        return users

    return _create_users


@pytest.fixture
def sample_user_data():
    return {
        "user_id": "test_user_123",
        "user_name": "testuser",
        "display_name": "Test User",
        "bio": "Test bio",
        "icon_url": "https://example.com/icon.jpg",
    }


@pytest.fixture
def create_profile_item(test_db_session):
    created_items: list = []

    def _create_profile_item(
        user_id: str,
        label: str | None = None,
        value: str | None = None,
        display_order: int | None = None,
        **kwargs,
    ):
        item_num = len(created_items) + 1
        item_data = {
            "profile_item_id": uuid.uuid4(),
            "user_id": user_id,
            "label": label or f"Test Label {item_num}",
            "value": value or f"Test Value {item_num}",
            "display_order": display_order or item_num,
            **kwargs,
        }

        profile_item = ProfileItem(**item_data)
        test_db_session.add(profile_item)
        test_db_session.commit()
        test_db_session.refresh(profile_item)
        created_items.append(profile_item)
        return profile_item

    return _create_profile_item


@pytest.fixture
def sample_profile_item_data():
    return {"label": "Favorite Food", "value": "Sushi", "display_order": 1}


@pytest.fixture
def sample_answer_data():
    return {"answer_text": "I love programming!"}


@pytest.fixture
def mock_jwt_token():
    return "test_jwt_token_123"


@pytest.fixture
def authenticated_headers(mock_jwt_token):
    return {"Authorization": f"Bearer {mock_jwt_token}"}


@pytest.fixture
def clean_db(test_db_session):
    for table in reversed(Base.metadata.sorted_tables):
        test_db_session.execute(table.delete())
    test_db_session.commit()

    yield

    for table in reversed(Base.metadata.sorted_tables):
        test_db_session.execute(table.delete())
    test_db_session.commit()


@pytest.fixture(autouse=True)
def clean_environment():
    original_env = os.environ.copy()
    os.environ.update(
        {
            "DATABASE_URL": "sqlite:///:memory:",
            "TEST_DATABASE_URL": "sqlite:///:memory:",
            "SECRET_KEY": "test_secret_key_for_jwt",
            "JWT_SECRET_KEY": "test_secret_key",
            "TWITTER_CLIENT_ID": "test_client_id",
            "TWITTER_CLIENT_SECRET": "test_client_secret",
            "ENVIRONMENT": "testing",
            "SESSION_SECRET_KEY": "test_session_secret",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "test_db",
        }
    )

    yield

    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def config_manager():
    return ConfigManager()


@pytest.fixture
def sample_versions_data():
    return {
        "versions": {"profile_labels": "v2.0", "questions": "v1.5"},
        "migrations": {
            "profile_labels": [
                {
                    "version": "v2.0",
                    "mappings": {"old_label": "new_label", "趣味": "エンタメ"},
                }
            ]
        },
    }


@pytest.fixture
def temp_config_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_yaml_content():
    return {
        "category": "性格・特徴",
        "questions": [
            "あなたの性格を教えてください",
            "趣味は何ですか",
            "好きな食べ物は何ですか",
        ],
    }


@pytest.fixture
def create_question(test_db_session):
    def _create_question(category_id="personality", text="テスト質問", display_order=1):
        question = Question(
            category_id=category_id, text=text, display_order=display_order
        )
        test_db_session.add(question)
        test_db_session.commit()
        test_db_session.refresh(question)
        return question

    return _create_question


@pytest.fixture
def create_answer(test_db_session):
    def _create_answer(user_id, question_id, answer_text="テスト回答"):
        answer = Answer(
            user_id=user_id, question_id=question_id, answer_text=answer_text
        )
        test_db_session.add(answer)
        test_db_session.commit()
        test_db_session.refresh(answer)
        return answer

    return _create_answer
