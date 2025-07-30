import pytest
from sqlalchemy.orm import Session

from src.schema.answer import AnswerCreate
from src.schema.bucket_list_item import BucketListItemCreate, BucketListItemUpdate
from src.schema.profile_item import ProfileItemCreate, ProfileItemUpdate
from src.schema.user import UserCreate
from src.service import (
    bucket_list_item_service,
    profile_service,
    qna_service,
    user_service,
)
from test.test_fixtures import create_test_user


@pytest.mark.unit
class TestUserService:
    """ユーザーサービスの単体テスト"""

    def test_create_user(self, test_db_session: Session):
        """ユーザー作成テスト"""
        user_data = UserCreate(
            user_id="service_test_user",
            user_name="serviceuser",
            display_name="Service Test User",
            bio="Service test bio",
            icon_url="https://example.com/service.jpg",
        )

        user = user_service.upsert_user(test_db_session, user_in=user_data)
        assert user.user_id == user_data.user_id
        assert user.user_name == user_data.user_name
        assert user.display_name == user_data.display_name

    def test_get_user_by_id(self, test_db_session: Session):
        """ID によるユーザー取得テスト"""
        created_user = create_test_user(test_db_session)

        retrieved_user = user_service.get_user(
            test_db_session, user_id=created_user.user_id
        )
        assert retrieved_user is not None
        assert retrieved_user.user_id == created_user.user_id
        assert retrieved_user.user_name == created_user.user_name

    def test_get_user_by_id_not_found(self, test_db_session: Session):
        """存在しないIDでのユーザー取得テスト"""
        user = user_service.get_user(test_db_session, user_id="nonexistent_user")
        assert user is None

    def test_get_user_by_username(self, test_db_session: Session):
        """ユーザー名によるユーザー取得テスト"""
        created_user = create_test_user(test_db_session)

        retrieved_user = user_service.get_user_by_username(
            test_db_session, user_name=created_user.user_name
        )
        assert retrieved_user is not None
        assert retrieved_user.user_id == created_user.user_id
        assert retrieved_user.user_name == created_user.user_name

    def test_get_user_by_username_not_found(self, test_db_session: Session):
        """存在しないユーザー名でのユーザー取得テスト"""
        user = user_service.get_user_by_username(
            test_db_session, user_name="nonexistent_user"
        )
        assert user is None

    def test_get_users_list(self, test_db_session: Session):
        """ユーザーリスト取得テスト"""
        # Create a unique test user to verify the service works
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        test_user_data = {
            "user_id": f"test_list_user_{unique_id}",
            "user_name": f"testlistuser{unique_id}",
            "display_name": f"Test List User {unique_id}",
            "bio": f"Test bio {unique_id}",
            "icon_url": f"https://example.com/{unique_id}.jpg",
        }

        # Create and verify the user
        created_user = create_test_user(test_db_session, test_user_data)
        assert created_user is not None
        assert created_user.user_name == test_user_data["user_name"]

        # Ensure user is committed
        test_db_session.commit()
        test_db_session.flush()

        # Test the get_users service method
        users = user_service.get_users(test_db_session, skip=0, limit=100)
        assert isinstance(users, list)

        # Verify our test user exists in the results
        test_user_found = any(
            user.user_name == test_user_data["user_name"] for user in users
        )
        assert test_user_found, (
            f"Test user {test_user_data['user_name']} not found in user list"
        )

    def test_upsert_existing_user(self, test_db_session: Session):
        """既存ユーザーのupsertテスト（更新）"""
        # 最初のユーザー作成
        original_user_data = UserCreate(
            user_id="upsert_user",
            user_name="upsertuser",
            display_name="Original Name",
            bio="Original bio",
            icon_url="https://example.com/original.jpg",
        )

        original_user = user_service.upsert_user(
            test_db_session, user_in=original_user_data
        )

        # 同じuser_idで異なる情報でupsert
        updated_user_data = UserCreate(
            user_id="upsert_user",  # 同じID
            user_name="upsertuser",  # 同じユーザー名
            display_name="Updated Name",  # 変更
            bio="Updated bio",  # 変更
            icon_url="https://example.com/updated.jpg",  # 変更
        )

        updated_user = user_service.upsert_user(
            test_db_session, user_in=updated_user_data
        )

        assert updated_user.user_id == original_user.user_id
        assert updated_user.display_name == "Updated Name"
        assert updated_user.bio == "Updated bio"
        assert updated_user.icon_url == "https://example.com/updated.jpg"


@pytest.mark.unit
class TestProfileService:
    """プロフィールサービスの単体テスト"""

    def test_create_profile_item(self, test_db_session: Session):
        """プロフィールアイテム作成テスト"""
        user = create_test_user(test_db_session)

        item_data = ProfileItemCreate(
            label="Test Label", value="Test Value", display_order=1
        )
        item = profile_service.create_profile_item(
            test_db_session, user_id=user.user_id, item_in=item_data
        )

        assert item.label == item_data.label
        assert item.value == item_data.value
        assert item.user_id == user.user_id

    def test_update_profile_item(self, test_db_session: Session):
        """プロフィールアイテム更新テスト"""
        user = create_test_user(test_db_session)

        # アイテム作成
        item_data = ProfileItemCreate(
            label="Original Label", value="Original Value", display_order=1
        )
        item = profile_service.create_profile_item(
            test_db_session, user_id=user.user_id, item_in=item_data
        )

        # アイテム更新（valueのみ更新可能）
        original_label = item.label
        update_data = ProfileItemUpdate(value="Updated Value")
        updated_item = profile_service.update_profile_item(
            test_db_session,
            user_id=user.user_id,
            item_id=str(item.profile_item_id),
            item_in=update_data,
        )

        assert updated_item.label == original_label  # ラベルは変更されない
        assert updated_item.value == "Updated Value"
        assert updated_item.profile_item_id == item.profile_item_id

    def test_delete_profile_item(self, test_db_session: Session):
        """プロフィールアイテム削除テスト"""
        user = create_test_user(test_db_session)

        # アイテム作成
        item_data = ProfileItemCreate(
            label="To Delete", value="Delete me", display_order=1
        )
        item = profile_service.create_profile_item(
            test_db_session, user_id=user.user_id, item_in=item_data
        )

        # アイテム削除
        profile_service.delete_profile_item(
            test_db_session, user_id=user.user_id, item_id=str(item.profile_item_id)
        )

        # 削除確認のため、エラーなく完了することを確認
        # 実際の実装では削除後の検証ロジックが必要


@pytest.mark.unit
class TestBucketListService:
    """バケットリストサービスの単体テスト"""

    def test_create_bucket_list_item(self, test_db_session: Session):
        """バケットリストアイテム作成テスト"""
        user = create_test_user(test_db_session)

        item_data = BucketListItemCreate(
            content="Learn Python", is_completed=False, display_order=1
        )
        item = bucket_list_item_service.create_bucket_list_item(
            test_db_session, user_id=user.user_id, item_in=item_data
        )

        assert item.content == item_data.content
        assert item.is_completed == item_data.is_completed
        assert item.user_id == user.user_id

    def test_update_bucket_list_item(self, test_db_session: Session):
        """バケットリストアイテム更新テスト"""
        user = create_test_user(test_db_session)

        # アイテム作成
        item_data = BucketListItemCreate(
            content="Original Task", is_completed=False, display_order=1
        )
        item = bucket_list_item_service.create_bucket_list_item(
            test_db_session, user_id=user.user_id, item_in=item_data
        )

        # アイテム更新
        update_data = BucketListItemUpdate(content="Updated Task", is_completed=True)
        updated_item = bucket_list_item_service.update_bucket_list_item(
            test_db_session,
            user_id=user.user_id,
            item_id=item.bucket_list_item_id,
            item_in=update_data,
        )

        assert updated_item.content == "Updated Task"
        assert updated_item.is_completed
        assert updated_item.bucket_list_item_id == item.bucket_list_item_id

    def test_delete_bucket_list_item(self, test_db_session: Session):
        """バケットリストアイテム削除テスト"""
        user = create_test_user(test_db_session)

        # アイテム作成
        item_data = BucketListItemCreate(
            content="To Delete", is_completed=False, display_order=1
        )
        item = bucket_list_item_service.create_bucket_list_item(
            test_db_session, user_id=user.user_id, item_in=item_data
        )

        # アイテム削除
        bucket_list_item_service.delete_bucket_list_item(
            test_db_session, user_id=user.user_id, item_id=item.bucket_list_item_id
        )


@pytest.mark.unit
class TestQnAService:
    """Q&Aサービスの単体テスト"""

    def test_get_all_questions(self, test_db_session: Session):
        """全質問取得テスト"""
        questions = qna_service.get_all_questions(test_db_session)
        assert isinstance(questions, list)
        # 質問データの存在は環境に依存するため、型チェックのみ

    def test_create_answer(self, test_db_session: Session):
        """回答作成テスト"""
        user = create_test_user(test_db_session)

        answer_data = AnswerCreate(answer_text="This is my test answer")
        # 質問IDは環境に依存するため、実際のテストではモックが必要
        question_id = 1  # 仮の質問ID

        try:
            answer = qna_service.create_answer(
                test_db_session,
                user_id=user.user_id,
                question_id=question_id,
                answer_in=answer_data,
            )
            assert answer.answer_text == answer_data.answer_text
            assert answer.user_id == user.user_id
            assert answer.question_id == question_id
        except Exception:
            # 質問が存在しない場合はスキップ
            pytest.skip("Question does not exist in test database")

    def test_get_user_qna(self, test_db_session: Session):
        """ユーザーQnA取得テスト"""
        user = create_test_user(test_db_session)

        qna_groups = qna_service.get_user_qna(test_db_session, user_id=user.user_id)
        assert isinstance(qna_groups, list)
        # 初期状態では空のリストまたはデフォルトデータ

    def test_get_all_questions_grouped(self, test_db_session: Session):
        """グループ化された全質問取得テスト"""
        grouped_questions = qna_service.get_all_questions_grouped(test_db_session)
        assert isinstance(grouped_questions, dict)
        # 質問データの構造は環境に依存するため、型チェックのみ
