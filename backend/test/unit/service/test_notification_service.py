import pytest

from src.db.tables import MessageTypeEnum, NotificationLevelEnum
from src.schema.message import MessageCreate
from src.service import message_service, notification_service


@pytest.mark.unit
class TestNotificationService:
    @pytest.mark.parametrize(
        "notification_level,message_type,expected",
        [
            (NotificationLevelEnum.none, MessageTypeEnum.comment, False),
            (NotificationLevelEnum.important, MessageTypeEnum.comment, True),
            (NotificationLevelEnum.important, MessageTypeEnum.like, False),
            (NotificationLevelEnum.all, MessageTypeEnum.like, True),
        ],
    )
    def test_should_notify_user(self, notification_level, message_type, expected):
        result = notification_service.should_notify_user(
            notification_level, message_type
        )
        assert result is expected

    def test_get_notifications_for_user(self, test_db_session, create_user):
        create_user(user_id="recipient", notification_level=NotificationLevelEnum.all)
        create_user(user_id="sender")

        message_data = MessageCreate(
            to_user_id="recipient",
            message_type=MessageTypeEnum.comment,
            content="Notification message",
        )
        message_service.create_message(test_db_session, message_data, "sender")

        result = notification_service.get_notifications_for_user(
            test_db_session, "recipient"
        )

        assert len(result) == 1
        assert result[0].content == "Notification message"

    def test_mark_all_notifications_as_read(self, test_db_session, create_user):
        create_user(user_id="recipient", notification_level=NotificationLevelEnum.all)
        create_user(user_id="sender")

        # Create multiple unread messages
        for i in range(3):
            message_data = MessageCreate(
                to_user_id="recipient",
                message_type=MessageTypeEnum.comment,
                content=f"Message {i}",
            )
            message_service.create_message(test_db_session, message_data, "sender")

        # Mark all as read
        updated_count = notification_service.mark_all_notifications_as_read(
            test_db_session, "recipient"
        )

        assert updated_count == 3
