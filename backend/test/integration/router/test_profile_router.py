import uuid

import pytest
from fastapi import status


@pytest.mark.integration
class TestProfileRouter:
    def test_update_profile_item_success(
        self, client, test_db_session, create_user, create_profile_item, csrf_headers
    ):
        user = create_user(user_id="update_user", user_name="updateuser")

        profile_item = create_profile_item(user.user_id, "元のラベル", "元の値", 1)
        update_data = {
            "value": "更新された値",
        }

        response = client.put(
            f"/users/{user.user_id}/profile-items/{profile_item.profile_item_id}",
            json=update_data,
            headers=csrf_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["label"] == "元のラベル"
        assert response_data["value"] == "更新された値"
        assert response_data["displayOrder"] == 1

    def test_update_profile_item_not_found(self, client, create_user, csrf_headers):
        user = create_user(user_id="no_item_user", user_name="noitemuser")

        update_data = {"value": "新しい値"}
        fake_item_id = str(uuid.uuid4())

        response = client.put(
            f"/users/{user.user_id}/profile-items/{fake_item_id}",
            json=update_data,
            headers=csrf_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_profile_item_wrong_user(
        self, client, test_db_session, create_user, create_profile_item, csrf_headers
    ):
        user1 = create_user(user_id="user1", user_name="user1")
        user2 = create_user(user_id="user2", user_name="user2")

        profile_item = create_profile_item(
            user1.user_id, "User1のアイテム", "User1の値", 1
        )

        update_data = {
            "value": "悪意のある値",
        }

        # user2としてuser1のアイテムを更新しようとする
        response = client.put(
            f"/users/{user2.user_id}/profile-items/{profile_item.profile_item_id}",
            json=update_data,
            headers=csrf_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
