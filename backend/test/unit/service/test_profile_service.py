from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.schema.profile_item import ProfileItemCreate, ProfileItemUpdate
from src.service import profile_service


@pytest.mark.unit
class TestProfileService:
    def test_create_profile_item_success(self, test_db_session, create_user):
        user = create_user()

        item_data = ProfileItemCreate(
            label="趣味", value="プログラミング", display_order=1
        )

        result = profile_service.create_profile_item(
            test_db_session, user.user_id, item_data
        )

        assert result.user_id == user.user_id
        assert result.label == "趣味"
        assert result.value == "プログラミング"
        assert result.display_order == 1
        assert result.profile_item_id is not None

    def test_update_profile_item_success(
        self, test_db_session, create_user, create_profile_item
    ):
        user = create_user()
        profile_item = create_profile_item(
            user.user_id, label="趣味", value="読書", display_order=1
        )

        update_data = ProfileItemUpdate(value="プログラミング", display_order=2)

        result = profile_service.update_profile_item(
            test_db_session,
            user.user_id,
            str(profile_item.profile_item_id),
            update_data,
        )

        assert result.label == "趣味"  # 変更されない
        assert result.value == "プログラミング"  # 更新される
        assert result.display_order == 2  # 更新される

    def test_update_profile_item_not_found(self, test_db_session, create_user):
        user = create_user()
        fake_item_id = str(uuid4())

        update_data = ProfileItemUpdate(value="新しい値")

        with pytest.raises(HTTPException) as exc_info:
            profile_service.update_profile_item(
                test_db_session, user.user_id, fake_item_id, update_data
            )

        assert exc_info.value.status_code == 404
        assert "Profile item not found" in str(exc_info.value.detail)

    def test_update_profile_item_invalid_uuid(self, test_db_session, create_user):
        user = create_user()
        invalid_id = "invalid-uuid"

        update_data = ProfileItemUpdate(value="新しい値")

        with pytest.raises(HTTPException) as exc_info:
            profile_service.update_profile_item(
                test_db_session, user.user_id, invalid_id, update_data
            )

        assert exc_info.value.status_code == 404

    def test_update_profile_item_wrong_user(
        self, test_db_session, create_user, create_profile_item
    ):
        user1 = create_user(user_id="user1")
        user2 = create_user(user_id="user2")
        profile_item = create_profile_item(user1.user_id, label="趣味", value="読書")

        update_data = ProfileItemUpdate(value="プログラミング")

        with pytest.raises(HTTPException) as exc_info:
            profile_service.update_profile_item(
                test_db_session,
                user2.user_id,
                str(profile_item.profile_item_id),
                update_data,
            )

        assert exc_info.value.status_code == 404

    def test_delete_profile_item_success(
        self, test_db_session, create_user, create_profile_item
    ):
        user = create_user()
        profile_item = create_profile_item(user.user_id, label="趣味", value="読書")

        result = profile_service.delete_profile_item(
            test_db_session, user.user_id, str(profile_item.profile_item_id)
        )

        assert result == {"ok": True}

        # アイテムが削除されていることを確認
        with pytest.raises(HTTPException):
            profile_service.update_profile_item(
                test_db_session,
                user.user_id,
                str(profile_item.profile_item_id),
                ProfileItemUpdate(value="test"),
            )

    def test_delete_profile_item_not_found(self, test_db_session, create_user):
        user = create_user()
        fake_item_id = str(uuid4())

        with pytest.raises(HTTPException) as exc_info:
            profile_service.delete_profile_item(
                test_db_session, user.user_id, fake_item_id
            )

        assert exc_info.value.status_code == 404

    def test_delete_profile_item_wrong_user(
        self, test_db_session, create_user, create_profile_item
    ):
        user1 = create_user(user_id="user1")
        user2 = create_user(user_id="user2")
        profile_item = create_profile_item(user1.user_id, label="趣味", value="読書")

        with pytest.raises(HTTPException) as exc_info:
            profile_service.delete_profile_item(
                test_db_session, user2.user_id, str(profile_item.profile_item_id)
            )

        assert exc_info.value.status_code == 404

    def test_get_profile_item_internal_function(
        self, test_db_session, create_user, create_profile_item
    ):
        user = create_user()
        profile_item = create_profile_item(user.user_id, label="趣味", value="読書")

        # _get_profile_item関数をテスト（内部関数だが重要な機能）
        result = profile_service._get_profile_item(
            test_db_session, user.user_id, profile_item.profile_item_id
        )

        assert result.profile_item_id == profile_item.profile_item_id
        assert result.user_id == user.user_id

    def test_get_profile_item_with_string_uuid(
        self, test_db_session, create_user, create_profile_item
    ):
        user = create_user()
        profile_item = create_profile_item(user.user_id, label="趣味", value="読書")

        # 文字列UUIDでのテスト
        result = profile_service._get_profile_item(
            test_db_session, user.user_id, str(profile_item.profile_item_id)
        )

        assert result.profile_item_id == profile_item.profile_item_id

    def test_create_multiple_profile_items(self, test_db_session, create_user):
        user = create_user()

        items_data = [
            ProfileItemCreate(label="趣味", value="読書", display_order=1),
            ProfileItemCreate(label="好きな食べ物", value="寿司", display_order=2),
            ProfileItemCreate(label="特技", value="プログラミング", display_order=3),
        ]

        created_items = []
        for item_data in items_data:
            result = profile_service.create_profile_item(
                test_db_session, user.user_id, item_data
            )
            created_items.append(result)

        assert len(created_items) == 3
        for i, item in enumerate(created_items):
            assert item.user_id == user.user_id
            assert item.display_order == i + 1

    def test_update_profile_item_partial_update(
        self, test_db_session, create_user, create_profile_item
    ):
        user = create_user()
        profile_item = create_profile_item(
            user.user_id, label="趣味", value="読書", display_order=1
        )

        # 値のみ更新
        update_data = ProfileItemUpdate(value="プログラミング")
        result = profile_service.update_profile_item(
            test_db_session,
            user.user_id,
            str(profile_item.profile_item_id),
            update_data,
        )

        assert result.label == "趣味"  # 変更されない
        assert result.value == "プログラミング"  # 更新される
        assert result.display_order == 1  # 変更されない

    def test_profile_item_create_with_all_fields(self, test_db_session, create_user):
        user = create_user()

        item_data = ProfileItemCreate(
            label="詳細な趣味", value="プログラミングと読書", display_order=5
        )

        result = profile_service.create_profile_item(
            test_db_session, user.user_id, item_data
        )

        assert result.label == "詳細な趣味"
        assert result.value == "プログラミングと読書"
        assert result.display_order == 5
