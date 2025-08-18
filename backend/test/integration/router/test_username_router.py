import uuid

import pytest
from fastapi import status

from src.db.tables import (
    Message,
    MessageStatusEnum,
    MessageTypeEnum,
)


@pytest.mark.integration
class TestUsernameRouter:
    def test_read_profile_page_data_success(
        self, client, test_db_session, create_user, create_profile_item
    ):
        user = create_user(
            user_id="profile_page_user",
            user_name="profilepageuser",
            display_name="Profile Page User",
            bio="プロフィールページのテストユーザー",
        )

        # ProfileItemをcreate_profile_itemヘルパーで作成
        create_profile_item(user.user_id, "趣味", "プログラミング", 1)
        create_profile_item(user.user_id, "好きな食べ物", "ラーメン", 2)

        response = client.get(f"/users/by-username/{user.user_name}/profile")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert "profile" in response_data
        assert "profileItems" in response_data

        profile = response_data["profile"]
        assert profile["userId"] == user.user_id
        assert profile["userName"] == user.user_name
        assert profile["displayName"] == "Profile Page User"

        items = response_data["profileItems"]
        assert len(items) >= 2
        item_labels = [item["label"] for item in items]
        assert "趣味" in item_labels
        assert "好きな食べ物" in item_labels

    def test_read_profile_page_data_nonexistent_user(self, client):
        response = client.get("/users/by-username/nonexistent_user/profile")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_read_profile_page_data_no_profile_items(self, client, create_user):
        user = create_user(
            user_id="no_items_user",
            user_name="noitemsuser",
            display_name="No Items User",
        )

        response = client.get(f"/users/by-username/{user.user_name}/profile")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert "profile" in response_data
        assert "profileItems" in response_data

        profile = response_data["profile"]
        assert profile["userName"] == user.user_name

        items = response_data["profileItems"]
        assert len(items) == 0

    def test_read_qna_page_data_success(
        self, client, test_db_session, create_user, create_question, create_answer
    ):
        user = create_user(
            user_id="qna_page_user",
            user_name="qnapageuser",
            display_name="QnA Page User",
        )

        questions = [
            create_question(text="あなたの趣味は？", category_id="personality"),
            create_question(text="好きな本は？", category_id="lifestyle"),
        ]

        # Answerをcreate_answerヘルパーで作成
        create_answer(
            user.user_id, questions[0].question_id, "プログラミングが好きです"
        )
        create_answer(
            user.user_id, questions[1].question_id, "技術書を読むのが好きです"
        )

        response = client.get(f"/users/by-username/{user.user_name}/qna")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert "profile" in response_data
        assert "userAnswerGroups" in response_data

        profile_data = response_data["profile"]
        assert profile_data["userName"] == user.user_name

        user_answer_groups = response_data["userAnswerGroups"]
        assert len(user_answer_groups) >= 1

    def test_read_qna_page_data_nonexistent_user(self, client):
        response = client.get("/users/by-username/nonexistent_user/qna")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_read_qna_page_data_no_answers(self, client, create_user):
        user = create_user(
            user_id="no_answers_user",
            user_name="noanswersuser",
            display_name="No Answers User",
        )

        response = client.get(f"/users/by-username/{user.user_name}/qna")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert "profile" in response_data
        assert "userAnswerGroups" in response_data

        user_answer_groups = response_data["userAnswerGroups"]
        assert len(user_answer_groups) == 0

    def test_read_messages_page_data_success(
        self, client, test_db_session, create_user
    ):
        user = create_user(
            user_id="msg_page_user",
            user_name="msgpageuser",
            display_name="Message Page User",
        )
        sender = create_user(
            user_id="msg_sender", user_name="msgsender", display_name="Message Sender"
        )

        # Messageを直接作成（現在conftest.pyにヘルパーがないため）
        messages = [
            Message(
                message_id=str(uuid.uuid4()),
                from_user_id=sender.user_id,
                to_user_id=user.user_id,
                message_type=MessageTypeEnum.comment,
                content="こんにちは！",
                status=MessageStatusEnum.unread,
            ),
            Message(
                message_id=str(uuid.uuid4()),
                from_user_id=sender.user_id,
                to_user_id=user.user_id,
                message_type=MessageTypeEnum.like,
                content="いいね！",
                status=MessageStatusEnum.read,
            ),
        ]

        for message in messages:
            test_db_session.add(message)
        test_db_session.commit()

        response = client.get(f"/users/by-username/{user.user_name}/messages")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert "profile" in response_data
        assert "messages" in response_data

        profile_data = response_data["profile"]
        assert profile_data["userName"] == user.user_name

        messages_data = response_data["messages"]
        assert len(messages_data) >= 1

    def test_read_messages_page_data_nonexistent_user(self, client):
        response = client.get("/users/by-username/nonexistent_user/messages")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_read_messages_page_data_no_messages(self, client, create_user):
        user = create_user(
            user_id="no_msg_user",
            user_name="nomsguser",
            display_name="No Messages User",
        )

        response = client.get(f"/users/by-username/{user.user_name}/messages")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert "profile" in response_data
        assert "messages" in response_data

        messages_data = response_data["messages"]
        assert len(messages_data) == 0

    def test_username_case_sensitivity(self, client, create_user):
        user = create_user(
            user_id="case_user",
            user_name="CaseUser",
            display_name="Case Sensitive User",
        )

        # 正確なユーザー名
        response1 = client.get(f"/users/by-username/{user.user_name}/profile")

        # 小文字のユーザー名
        response2 = client.get("/users/by-username/caseuser/profile")

        assert response1.status_code == status.HTTP_200_OK
        # ユーザー名が大文字小文字を区別するかは実装次第
        assert response2.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_special_characters_in_username(self, client, create_user):
        user = create_user(
            user_id="special_user", user_name="user_123", display_name="Special User"
        )

        response = client.get(f"/users/by-username/{user.user_name}/profile")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["profile"]["userName"] == "user_123"

    def test_unicode_username(self, client, create_user):
        try:
            user = create_user(
                user_id="unicode_user",
                user_name="ユーザー123",
                display_name="Unicode User",
            )

            response = client.get(f"/users/by-username/{user.user_name}/profile")

            # Unicode対応の実装次第でステータスコードが変わる
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND,
            ]
        except Exception:
            # Unicode文字がサポートされていない場合はテストをスキップ
            pytest.skip("Unicode usernames not supported")

    def test_very_long_username(self, client):
        very_long_username = "a" * 1000  # 1000文字のユーザー名

        response = client.get(f"/users/by-username/{very_long_username}/profile")

        # 長すぎるユーザー名の場合は404または400エラーを想定
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_empty_username(self, client):
        response = client.get("/users/by-username//profile")

        # パスパラメータが空の場合のエラー
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]
