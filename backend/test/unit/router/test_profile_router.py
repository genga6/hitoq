import uuid

import pytest
from fastapi import status


@pytest.mark.integration
class TestProfileRouter:
    def test_create_profile_item_success(self, client, test_db_session, create_user):
        user = create_user(user_id="profile_user", user_name="profileuser")

        item_data = {"label": "趣味", "value": "プログラミング", "display_order": 1}

        response = client.post(f"/users/{user.user_id}/profile-items", json=item_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        assert response_data["label"] == "趣味"
        assert response_data["value"] == "プログラミング"
        assert response_data["display_order"] == 1
        assert "profile_item_id" in response_data

    def test_create_profile_item_nonexistent_user(self, client):
        item_data = {"label": "趣味", "value": "読書", "display_order": 1}

        response = client.post("/users/nonexistent_user/profile-items", json=item_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_profile_item_invalid_data(self, client, create_user):
        user = create_user(user_id="invalid_profile_user", user_name="invaliduser")

        invalid_data = {"label": "", "value": "some value", "display_order": 1}

        response = client.post(
            f"/users/{user.user_id}/profile-items", json=invalid_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_profile_item_success(
        self, client, test_db_session, create_user, create_profile_item
    ):
        user = create_user(user_id="update_user", user_name="updateuser")

        profile_item = create_profile_item(user.user_id, "元のラベル", "元の値", 1)

        update_data = {
            "label": "更新されたラベル",
            "value": "更新された値",
            "display_order": 2,
        }

        response = client.put(
            f"/users/{user.user_id}/profile-items/{profile_item.profile_item_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["label"] == "更新されたラベル"
        assert response_data["value"] == "更新された値"
        assert response_data["display_order"] == 2

    def test_update_profile_item_not_found(self, client, create_user):
        user = create_user(user_id="no_item_user", user_name="noitemuser")

        update_data = {"label": "新しいラベル", "value": "新しい値", "display_order": 1}

        fake_item_id = str(uuid.uuid4())
        response = client.put(
            f"/users/{user.user_id}/profile-items/{fake_item_id}", json=update_data
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_profile_item_wrong_user(
        self, client, test_db_session, create_user, create_profile_item
    ):
        user1 = create_user(user_id="user1", user_name="user1")
        user2 = create_user(user_id="user2", user_name="user2")

        profile_item = create_profile_item(
            user1.user_id, "User1のアイテム", "User1の値", 1
        )

        update_data = {
            "label": "悪意のある更新",
            "value": "悪意のある値",
            "display_order": 1,
        }

        # user2としてuser1のアイテムを更新しようとする
        response = client.put(
            f"/users/{user2.user_id}/profile-items/{profile_item.profile_item_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_profile_item_success(
        self, client, test_db_session, create_user, create_profile_item
    ):
        user = create_user(user_id="delete_user", user_name="deleteuser")

        profile_item = create_profile_item(user.user_id, "削除対象", "削除される値", 1)

        response = client.delete(
            f"/users/{user.user_id}/profile-items/{profile_item.profile_item_id}"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 削除されたことを確認（ProfileItem importを使用して直接チェック）
        from src.db.tables import ProfileItem

        deleted_item = test_db_session.get(ProfileItem, profile_item.profile_item_id)
        assert deleted_item is None

    def test_delete_profile_item_not_found(self, client, create_user):
        user = create_user(user_id="no_delete_user", user_name="nodeleteuser")

        fake_item_id = str(uuid.uuid4())
        response = client.delete(f"/users/{user.user_id}/profile-items/{fake_item_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_profile_item_wrong_user(
        self, client, test_db_session, create_user, create_profile_item
    ):
        user1 = create_user(user_id="owner_user", user_name="owneruser")
        user2 = create_user(user_id="other_user", user_name="otheruser")

        profile_item = create_profile_item(
            user1.user_id, "保護されたアイテム", "削除されない値", 1
        )

        # user2としてuser1のアイテムを削除しようとする
        response = client.delete(
            f"/users/{user2.user_id}/profile-items/{profile_item.profile_item_id}"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # アイテムが削除されていないことを確認（ProfileItem importを使用して直接チェック）
        from src.db.tables import ProfileItem

        existing_item = test_db_session.get(ProfileItem, profile_item.profile_item_id)
        assert existing_item is not None

    def test_profile_item_validation_missing_fields(self, client, create_user):
        user = create_user(user_id="validation_user", user_name="validationuser")

        incomplete_data = {"label": "テストラベル"}

        response = client.post(
            f"/users/{user.user_id}/profile-items", json=incomplete_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
