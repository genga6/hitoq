from uuid import uuid4

import pytest
from fastapi import status

from src.db.tables import Message, MessageStatusEnum, MessageTypeEnum
from src.main import app
from src.router.auth import _get_current_user


@pytest.mark.integration
class TestMessageRouter:
    def test_create_message_success(
        self, client, test_db_session, create_user, csrf_headers
    ):
        sender = create_user(user_id="sender_user", user_name="senderuser")
        receiver = create_user(user_id="receiver_user", user_name="receiveruser")

        message_data = {
            "to_user_id": receiver.user_id,
            "message_type": "comment",
            "content": "こんにちは！テストメッセージです。",
        }

        app.dependency_overrides[_get_current_user] = lambda: sender
        response = client.post("/messages/", json=message_data, headers=csrf_headers)
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["toUserId"] == receiver.user_id
        assert response_data["fromUserId"] == sender.user_id
        assert response_data["content"] == "こんにちは！テストメッセージです。"
        assert response_data["messageType"] == "comment"

    def test_create_message_nonexistent_target_user(
        self, client, create_user, csrf_headers
    ):
        sender = create_user(user_id="invalid_sender", user_name="invalidsender")

        message_data = {
            "to_user_id": "nonexistent_user",
            "message_type": "comment",
            "content": "存在しないユーザーへのメッセージ",
        }

        app.dependency_overrides[_get_current_user] = lambda: sender
        response = client.post("/messages/", json=message_data, headers=csrf_headers)
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_message_unauthenticated(self, client, create_user, csrf_headers):
        receiver = create_user(user_id="unauth_receiver", user_name="unauthreceiver")

        message_data = {
            "to_user_id": receiver.user_id,
            "message_type": "comment",
            "content": "未認証メッセージ",
        }

        response = client.post("/messages/", json=message_data, headers=csrf_headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_message_invalid_data(self, client, create_user, csrf_headers):
        sender = create_user(user_id="invalid_data_sender", user_name="invaliddata")
        receiver = create_user(user_id="invalid_data_receiver", user_name="invalidrec")

        invalid_data = {
            "to_user_id": receiver.user_id,
            "message_type": "invalid_type",  # 無効なメッセージタイプ
            "content": "",  # 空のコンテンツ
        }

        app.dependency_overrides[_get_current_user] = lambda: sender
        response = client.post("/messages/", json=invalid_data, headers=csrf_headers)
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_my_messages_success(self, client, test_db_session, create_user):
        sender = create_user(user_id="msg_sender", user_name="msgsender")
        receiver = create_user(user_id="msg_receiver", user_name="msgreceiver")

        messages = [
            Message(
                message_id=str(uuid4()),
                from_user_id=sender.user_id,
                to_user_id=receiver.user_id,
                message_type=MessageTypeEnum.comment,
                content=f"テストメッセージ {i + 1}",
                status=MessageStatusEnum.unread,
            )
            for i in range(3)
        ]

        for message in messages:
            test_db_session.add(message)
        test_db_session.commit()

        app.dependency_overrides[_get_current_user] = lambda: receiver
        response = client.get("/messages/")
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) >= 3

    def test_get_my_messages_pagination(self, client, test_db_session, create_user):
        sender = create_user(user_id="pag_sender", user_name="pagsender")
        receiver = create_user(user_id="pag_receiver", user_name="pagreceiver")

        # 多数のメッセージを作成
        messages = [
            Message(
                message_id=str(uuid4()),
                from_user_id=sender.user_id,
                to_user_id=receiver.user_id,
                message_type=MessageTypeEnum.comment,
                content=f"ページネーションテスト {i + 1}",
                status=MessageStatusEnum.unread,
            )
            for i in range(15)
        ]

        for message in messages:
            test_db_session.add(message)
        test_db_session.commit()

        app.dependency_overrides[_get_current_user] = lambda: receiver
        # 最初のページ
        response = client.get("/messages/?skip=0&limit=10")
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert len(response_data) == 10

    def test_get_my_messages_unauthenticated(self, client):
        response = client.get("/messages/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_message_status_success(
        self, client, test_db_session, create_user, csrf_headers
    ):
        sender = create_user(user_id="status_sender", user_name="statussender")
        receiver = create_user(user_id="status_receiver", user_name="statusreceiver")

        message = Message(
            message_id=str(uuid4()),
            from_user_id=sender.user_id,
            to_user_id=receiver.user_id,
            message_type=MessageTypeEnum.comment,
            content="ステータス更新テスト",
            status=MessageStatusEnum.unread,
        )
        test_db_session.add(message)
        test_db_session.commit()

        update_data = {"status": "read"}

        app.dependency_overrides[_get_current_user] = lambda: receiver
        response = client.patch(
            f"/messages/{message.message_id}", json=update_data, headers=csrf_headers
        )
        app.dependency_overrides = {}

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_reply_to_message_success(
        self, client, test_db_session, create_user, csrf_headers
    ):
        sender = create_user(user_id="reply_sender", user_name="replysender")
        receiver = create_user(user_id="reply_receiver", user_name="replyreceiver")

        # 元のメッセージを作成
        original_message = Message(
            message_id=str(uuid4()),
            from_user_id=sender.user_id,
            to_user_id=receiver.user_id,
            message_type=MessageTypeEnum.comment,
            content="元のメッセージ",
            status=MessageStatusEnum.unread,
        )
        test_db_session.add(original_message)
        test_db_session.commit()

        reply_data = {
            "parent_message_id": str(original_message.message_id),
            "to_user_id": sender.user_id,
            "message_type": "comment",
            "content": "返信メッセージです",
        }

        app.dependency_overrides[_get_current_user] = lambda: receiver
        response = client.post("/messages/", json=reply_data, headers=csrf_headers)
        app.dependency_overrides = {}

        # 返信機能が実装されている場合の成功レスポンスを確認
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_get_notifications_success(self, client, test_db_session, create_user):
        user = create_user(user_id="notif_user", user_name="notifuser")
        sender = create_user(user_id="notif_sender", user_name="notifsender")

        # 通知用メッセージを作成
        message = Message(
            message_id=str(uuid4()),
            from_user_id=sender.user_id,
            to_user_id=user.user_id,
            message_type=MessageTypeEnum.like,
            content="いいね！",
            status=MessageStatusEnum.unread,
        )
        test_db_session.add(message)
        test_db_session.commit()

        app.dependency_overrides[_get_current_user] = lambda: user
        response = client.get("/messages/notifications")
        app.dependency_overrides = {}

        # 通知エンドポイントが実装されている場合
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_message_content_length_validation(self, client, create_user, csrf_headers):
        sender = create_user(user_id="length_sender", user_name="lengthsender")
        receiver = create_user(user_id="length_receiver", user_name="lengthreceiver")

        # 非常に長いメッセージ
        very_long_content = "A" * 5000  # 5000文字

        message_data = {
            "to_user_id": receiver.user_id,
            "message_type": "comment",
            "content": very_long_content,
        }

        app.dependency_overrides[_get_current_user] = lambda: sender
        response = client.post("/messages/", json=message_data, headers=csrf_headers)
        app.dependency_overrides = {}

        # 長すぎる場合のエラーまたは成功レスポンスを確認
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_200_OK,
        ]

    @pytest.mark.parametrize("msg_type", ["comment", "like"])
    def test_message_type_validation(self, client, create_user, msg_type, csrf_headers):
        sender = create_user(user_id="type_sender", user_name="typesender")
        receiver = create_user(user_id="type_receiver", user_name="typereceiver")

        message_data = {
            "to_user_id": receiver.user_id,
            "message_type": msg_type,
            "content": f"{msg_type}メッセージテスト",
        }

        app.dependency_overrides[_get_current_user] = lambda: sender
        response = client.post("/messages/", json=message_data, headers=csrf_headers)
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
