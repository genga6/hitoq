import pytest
from fastapi import status


@pytest.mark.integration
class TestByUsernameRouter:
    def test_read_user_by_username(self, client, create_user):
        create_user(
            user_id="test_user_by_username",
            user_name="testusername",
            display_name="Test User",
            bio="Test bio for username lookup",
        )

        response = client.get("/by-username/testusername")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["userId"] == "test_user_by_username"
        assert response_data["userName"] == "testusername"
        assert response_data["displayName"] == "Test User"
        assert response_data["bio"] == "Test bio for username lookup"

    def test_read_user_by_username_not_found(self, client):
        response = client.get("/by-username/nonexistentuser")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert response_data["detail"] == "User not found"

    def test_read_messages_by_username(self, client, create_user):
        # ユーザーを作成
        create_user(
            user_id="message_test_user",
            user_name="messageuser",
            display_name="Message User",
        )
        create_user(
            user_id="sender_user",
            user_name="senderuser",
            display_name="Sender User",
        )

        response = client.get("/by-username/messageuser/messages")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        if len(response_data) > 0:
            message = response_data[0]
            assert "messageId" in message
            assert "content" in message
            assert "fromUserId" in message
            assert "toUserId" in message

    def test_read_messages_by_username_user_not_found(self, client):
        response = client.get("/by-username/nonexistentuser/messages")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert response_data["detail"] == "User not found"

    def test_read_qna_by_username(
        self, client, create_user, create_question, create_answer
    ):
        # ユーザーを作成
        user = create_user(
            user_id="qna_test_user",
            user_name="qnauser",
            display_name="QnA User",
        )

        # 質問を作成
        question = create_question(text="Test question", category_id="personality")

        # 回答を作成
        create_answer(
            user_id=user.user_id,
            question_id=question.question_id,
            answer_text="Test answer",
        )

        response = client.get("/by-username/qnauser/qna")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert "userAnswerGroups" in response_data
        assert "categories" in response_data

        assert isinstance(response_data["userAnswerGroups"], list)
        assert isinstance(response_data["categories"], dict)

    def test_read_qna_by_username_user_not_found(self, client):
        response = client.get("/by-username/nonexistentuser/qna")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert response_data["detail"] == "User not found"

    def test_read_profile_items_by_username(
        self, client, create_user, create_profile_item
    ):
        # ユーザーを作成
        user = create_user(
            user_id="profile_test_user",
            user_name="profileuser",
            display_name="Profile User",
        )

        # プロフィールアイテムを作成
        create_profile_item(user.user_id, "Test Label", "Test Value", 1)

        response = client.get("/by-username/profileuser/profile-items")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        if len(response_data) > 0:
            profile_item = response_data[0]
            assert "profileItemId" in profile_item
            assert "label" in profile_item
            assert "value" in profile_item
            assert profile_item["label"] == "Test Label"
            assert profile_item["value"] == "Test Value"

    def test_read_profile_items_by_username_user_not_found(self, client):
        response = client.get("/by-username/nonexistentuser/profile-items")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert response_data["detail"] == "User not found"

    def test_read_profile_items_by_username_empty_result(self, client, create_user):
        # プロフィールアイテムを持たないユーザーを作成
        create_user(
            user_id="empty_profile_user",
            user_name="emptyprofile",
            display_name="Empty Profile User",
        )

        response = client.get("/by-username/emptyprofile/profile-items")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == 0
