from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.schema.profile_item import ProfileItemUpdate
from src.service import profile_service


@pytest.mark.unit
class TestProfileService:
    def test_update_profile_item_success(
        self, test_db_session, create_user, create_profile_item
    ):
        user = create_user()
        profile_item = create_profile_item(
            user.user_id, label="趣味", value="読書", display_order=1
        )

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
