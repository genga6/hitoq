from uuid import uuid4

import pytest
from fastapi import status

from src.db.tables import (
    Message,
    MessageStatusEnum,
    MessageTypeEnum,
    NotificationLevelEnum,
)
from src.main import app
from src.router.auth import _get_current_user


@pytest.mark.integration
class TestNotificationRouter:
    def test_get_notifications_success(self, client, test_db_session, create_user):
        user = create_user(
            user_id="notif_user",
            user_name="notifuser",
            notification_level=NotificationLevelEnum.all,
        )
        sender = create_user(user_id="notif_sender", user_name="notifsender")

        # 通知用メッセージを作成
        message = Message(
            message_id=str(uuid4()),
            from_user_id=sender.user_id,
            to_user_id=user.user_id,
            message_type=MessageTypeEnum.comment,
            content="通知テストメッセージ",
            status=MessageStatusEnum.unread,
        )
        test_db_session.add(message)
        test_db_session.commit()

        app.dependency_overrides[_get_current_user] = lambda: user
        response = client.get("/notifications/")
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) >= 1
        assert response_data[0]["content"] == "通知テストメッセージ"

    def test_get_notifications_pagination(self, client, test_db_session, create_user):
        user = create_user(
            user_id="pag_user",
            user_name="paguser",
            notification_level=NotificationLevelEnum.all,
        )
        sender = create_user(user_id="pag_sender", user_name="pagsender")

        # 多数の通知メッセージを作成
        messages = [
            Message(
                message_id=str(uuid4()),
                from_user_id=sender.user_id,
                to_user_id=user.user_id,
                message_type=MessageTypeEnum.comment,
                content=f"通知メッセージ {i + 1}",
                status=MessageStatusEnum.unread,
            )
            for i in range(15)
        ]

        for message in messages:
            test_db_session.add(message)
        test_db_session.commit()

        app.dependency_overrides[_get_current_user] = lambda: user
        response = client.get("/notifications/?skip=0&limit=10")
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert len(response_data) == 10

    def test_get_notification_count_success(self, client, test_db_session, create_user):
        user = create_user(
            user_id="count_user",
            user_name="countuser",
            notification_level=NotificationLevelEnum.all,
        )
        sender = create_user(user_id="count_sender", user_name="countsender")

        # 通知メッセージを作成
        for i in range(3):
            message = Message(
                message_id=str(uuid4()),
                from_user_id=sender.user_id,
                to_user_id=user.user_id,
                message_type=MessageTypeEnum.comment,
                content=f"通知カウントテスト {i + 1}",
                status=MessageStatusEnum.unread,
            )
            test_db_session.add(message)
        test_db_session.commit()

        app.dependency_overrides[_get_current_user] = lambda: user
        response = client.get("/notifications/count")
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["notification_count"] == 3

    def test_mark_all_notifications_as_read_success(
        self, client, test_db_session, create_user, csrf_headers
    ):
        user = create_user(
            user_id="read_user",
            user_name="readuser",
            notification_level=NotificationLevelEnum.all,
        )
        sender = create_user(user_id="read_sender", user_name="readsender")

        # 未読の通知メッセージを作成
        for i in range(5):
            message = Message(
                message_id=str(uuid4()),
                from_user_id=sender.user_id,
                to_user_id=user.user_id,
                message_type=MessageTypeEnum.comment,
                content=f"既読テスト {i + 1}",
                status=MessageStatusEnum.unread,
            )
            test_db_session.add(message)
        test_db_session.commit()

        app.dependency_overrides[_get_current_user] = lambda: user
        response = client.patch("/notifications/mark-all-read", headers=csrf_headers)
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["updated_count"] == 5

        # 通知カウントが0になることを確認
        app.dependency_overrides[_get_current_user] = lambda: user
        count_response = client.get("/notifications/count")
        app.dependency_overrides = {}
        assert count_response.json()["notification_count"] == 0

    def test_get_notifications_with_notification_level_none(
        self, client, test_db_session, create_user
    ):
        user = create_user(
            user_id="none_user",
            user_name="noneuser",
            notification_level=NotificationLevelEnum.none,
        )
        sender = create_user(user_id="none_sender", user_name="nonesender")

        # メッセージを作成
        message = Message(
            message_id=str(uuid4()),
            from_user_id=sender.user_id,
            to_user_id=user.user_id,
            message_type=MessageTypeEnum.comment,
            content="通知無効テスト",
            status=MessageStatusEnum.unread,
        )
        test_db_session.add(message)
        test_db_session.commit()

        app.dependency_overrides[_get_current_user] = lambda: user
        response = client.get("/notifications/")
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # notification_level が none の場合、通知は返されない
        assert len(response_data) == 0

    def test_get_notifications_with_notification_level_important(
        self, client, test_db_session, create_user
    ):
        user = create_user(
            user_id="imp_user",
            user_name="impuser",
            notification_level=NotificationLevelEnum.important,
        )
        sender = create_user(user_id="imp_sender", user_name="impsender")

        # comment と like メッセージを作成
        comment_message = Message(
            message_id=str(uuid4()),
            from_user_id=sender.user_id,
            to_user_id=user.user_id,
            message_type=MessageTypeEnum.comment,
            content="重要な通知（コメント）",
            status=MessageStatusEnum.unread,
        )
        like_message = Message(
            message_id=str(uuid4()),
            from_user_id=sender.user_id,
            to_user_id=user.user_id,
            message_type=MessageTypeEnum.like,
            content="いいね",
            status=MessageStatusEnum.unread,
        )

        test_db_session.add(comment_message)
        test_db_session.add(like_message)
        test_db_session.commit()

        app.dependency_overrides[_get_current_user] = lambda: user
        response = client.get("/notifications/")
        app.dependency_overrides = {}

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # important レベルではコメントのみが通知される
        assert len(response_data) == 1
        assert response_data[0]["messageType"] == "comment"

    def test_get_notifications_unauthenticated(self, client):
        response = client.get("/notifications/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_notification_count_unauthenticated(self, client):
        response = client.get("/notifications/count")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_mark_all_notifications_as_read_unauthenticated(self, client, csrf_headers):
        response = client.patch("/notifications/mark-all-read", headers=csrf_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
