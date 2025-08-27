from uuid import uuid4

import pytest

from src.db.tables import MessageStatusEnum, MessageTypeEnum, NotificationLevelEnum
from src.schema.block import BlockCreate
from src.schema.message import MessageCreate, MessageUpdate
from src.service import block_service, message_service


@pytest.mark.unit
class TestMessageService:
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
        result = message_service.should_notify_user(notification_level, message_type)
        assert result is expected

    def test_create_message_success(self, test_db_session, create_user):
        create_user(user_id="from_user")
        create_user(user_id="to_user")

        message_data = MessageCreate(
            to_user_id="to_user",
            message_type=MessageTypeEnum.comment,
            content="Test message",
        )

        result = message_service.create_message(
            test_db_session, message_data, "from_user"
        )

        assert result.from_user_id == "from_user"
        assert result.to_user_id == "to_user"
        assert result.content == "Test message"
        assert result.status == MessageStatusEnum.unread

    def test_create_message_blocked_user(self, test_db_session, create_user):
        create_user(user_id="blocker")
        create_user(user_id="blocked")

        block_service.create_block(
            test_db_session, "blocker", BlockCreate(blocked_user_id="blocked")
        )

        message_data = MessageCreate(
            to_user_id="blocker",
            message_type=MessageTypeEnum.like,
            content="Should fail",
        )

        with pytest.raises(
            ValueError, match="Cannot send message to user who has blocked you"
        ):
            message_service.create_message(test_db_session, message_data, "blocked")

    def test_get_messages_for_user(self, test_db_session, create_user):
        create_user(user_id="recipient")
        create_user(user_id="sender")

        message_data = MessageCreate(
            to_user_id="recipient",
            message_type=MessageTypeEnum.comment,
            content="Test message",
        )
        message_service.create_message(test_db_session, message_data, "sender")

        result = message_service.get_messages_for_user(test_db_session, "recipient")

        assert len(result) == 1
        assert result[0].content == "Test message"
        assert result[0].from_user.user_id == "sender"

    def test_get_messages_excludes_blocked_users(self, test_db_session, create_user):
        create_user(user_id="recipient")
        create_user(user_id="sender")
        create_user(user_id="blocked_sender")

        message1 = MessageCreate(
            to_user_id="recipient",
            message_type=MessageTypeEnum.comment,
            content="Message 1",
        )
        message2 = MessageCreate(
            to_user_id="recipient",
            message_type=MessageTypeEnum.comment,
            content="Message 2",
        )

        message_service.create_message(test_db_session, message1, "sender")
        message_service.create_message(test_db_session, message2, "blocked_sender")

        block_service.create_block(
            test_db_session, "recipient", BlockCreate(blocked_user_id="blocked_sender")
        )

        result = message_service.get_messages_for_user(test_db_session, "recipient")

        assert len(result) == 1
        assert result[0].from_user.user_id == "sender"

    def test_get_message(self, test_db_session, create_user):
        create_user(user_id="from_user")
        create_user(user_id="to_user")

        message_data = MessageCreate(
            to_user_id="to_user",
            message_type=MessageTypeEnum.comment,
            content="Test message",
        )
        created_message = message_service.create_message(
            test_db_session, message_data, "from_user"
        )

        result = message_service.get_message(
            test_db_session, created_message.message_id
        )

        assert result is not None
        assert result.message_id == created_message.message_id
        assert result.from_user.user_id == "from_user"
        assert result.to_user.user_id == "to_user"

    def test_get_message_not_found(self, test_db_session):
        result = message_service.get_message(test_db_session, str(uuid4()))
        assert result is None

    def test_update_message_status(self, test_db_session, create_user):
        create_user(user_id="from_user")
        create_user(user_id="to_user")

        message_data = MessageCreate(
            to_user_id="to_user",
            message_type=MessageTypeEnum.comment,
            content="Test message",
        )
        created_message = message_service.create_message(
            test_db_session, message_data, "from_user"
        )

        update_data = MessageUpdate(status=MessageStatusEnum.read)
        result = message_service.update_message_status(
            test_db_session, created_message.message_id, update_data
        )

        assert result is not None
        assert result.status == MessageStatusEnum.read

    def test_update_message_status_not_found(self, test_db_session):
        update_data = MessageUpdate(status=MessageStatusEnum.read)
        result = message_service.update_message_status(
            test_db_session, str(uuid4()), update_data
        )
        assert result is None

    def test_get_unread_count(self, test_db_session, create_user):
        create_user(user_id="from_user")
        create_user(user_id="recipient")

        for i in range(3):
            message_data = MessageCreate(
                to_user_id="recipient",
                message_type=MessageTypeEnum.comment,
                content=f"Message {i}",
            )
            message_service.create_message(test_db_session, message_data, "from_user")

        result = message_service.get_unread_count(test_db_session, "recipient")
        assert result == 3

    @pytest.mark.parametrize(
        "notification_level,messages,expected_count",
        [
            (
                NotificationLevelEnum.none,
                [MessageTypeEnum.comment],
                0,
            ),
            (
                NotificationLevelEnum.important,
                [MessageTypeEnum.comment, MessageTypeEnum.like],
                1,
            ),
        ],
    )
    def test_get_notification_count(
        self, test_db_session, create_user, notification_level, messages, expected_count
    ):
        create_user(user_id="recipient", notification_level=notification_level)
        create_user(user_id="sender")

        for i, message_type in enumerate(messages):
            message_data = MessageCreate(
                to_user_id="recipient",
                message_type=message_type,
                content=f"Message {i}",
            )
            message_service.create_message(test_db_session, message_data, "sender")

        result = message_service.get_notification_count(test_db_session, "recipient")
        assert result == expected_count

    def test_get_notifications_for_user(self, test_db_session, create_user):
        create_user(user_id="recipient", notification_level=NotificationLevelEnum.all)
        create_user(user_id="sender")

        message_data = MessageCreate(
            to_user_id="recipient",
            message_type=MessageTypeEnum.comment,
            content="Notification message",
        )
        message_service.create_message(test_db_session, message_data, "sender")

        result = message_service.get_notifications_for_user(
            test_db_session, "recipient"
        )

        assert len(result) == 1
        assert result[0].content == "Notification message"

    def test_get_messages_with_replies(self, test_db_session, create_user):
        create_user(user_id="from_user")
        create_user(user_id="recipient")

        root_message_data = MessageCreate(
            to_user_id="recipient",
            message_type=MessageTypeEnum.comment,
            content="Root message",
        )
        root_message = message_service.create_message(
            test_db_session, root_message_data, "from_user"
        )

        reply_message_data = MessageCreate(
            to_user_id="from_user",
            message_type=MessageTypeEnum.comment,
            content="Reply message",
            parent_message_id=root_message.message_id,
        )
        message_service.create_message(test_db_session, reply_message_data, "recipient")

        result = message_service.get_messages_with_replies(test_db_session, "recipient")

        assert len(result) == 1
        assert result[0].content == "Root message"
        assert result[0].reply_count == 1

    def test_get_conversation_messages_for_user(self, test_db_session, create_user):
        create_user(user_id="user1")
        create_user(user_id="user2")

        message1 = MessageCreate(
            to_user_id="user2",
            message_type=MessageTypeEnum.comment,
            content="From user1",
        )
        message2 = MessageCreate(
            to_user_id="user1",
            message_type=MessageTypeEnum.comment,
            content="From user2",
        )

        message_service.create_message(test_db_session, message1, "user1")
        message_service.create_message(test_db_session, message2, "user2")

        result = message_service.get_conversation_messages_for_user(
            test_db_session, "user1"
        )

        assert len(result) == 2
        message_contents = [msg.content for msg in result]
        assert "From user1" in message_contents
        assert "From user2" in message_contents

    def test_update_message_content(self, test_db_session, create_user):
        create_user(user_id="from_user")
        create_user(user_id="to_user")

        message_data = MessageCreate(
            to_user_id="to_user",
            message_type=MessageTypeEnum.comment,
            content="Original content",
        )
        created_message = message_service.create_message(
            test_db_session, message_data, "from_user"
        )

        result = message_service.update_message_content(
            test_db_session, created_message.message_id, "Updated content"
        )

        assert result is not None
        assert result.content == "Updated content"

    def test_delete_message(self, test_db_session, create_user):
        create_user(user_id="from_user")
        create_user(user_id="to_user")

        message_data = MessageCreate(
            to_user_id="to_user",
            message_type=MessageTypeEnum.comment,
            content="To be deleted",
        )
        created_message = message_service.create_message(
            test_db_session, message_data, "from_user"
        )

        result = message_service.delete_message(
            test_db_session, created_message.message_id
        )

        assert result is True
        deleted_message = message_service.get_message(
            test_db_session, created_message.message_id
        )
        assert deleted_message is None

    def test_toggle_heart_reaction_add(self, test_db_session, create_user):
        create_user(user_id="liker")
        create_user(user_id="author")

        message_data = MessageCreate(
            to_user_id="author",
            message_type=MessageTypeEnum.comment,
            content="Original message",
        )
        original_message = message_service.create_message(
            test_db_session, message_data, "author"
        )

        result = message_service.toggle_heart_reaction(
            test_db_session, "liker", original_message.message_id
        )

        assert result["user_liked"] is True
        assert result["like_count"] == 1

    def test_toggle_heart_reaction_remove(self, test_db_session, create_user):
        create_user(user_id="liker")
        create_user(user_id="author")

        message_data = MessageCreate(
            to_user_id="author",
            message_type=MessageTypeEnum.comment,
            content="Original message",
        )
        original_message = message_service.create_message(
            test_db_session, message_data, "author"
        )

        message_service.toggle_heart_reaction(
            test_db_session, "liker", original_message.message_id
        )

        result = message_service.toggle_heart_reaction(
            test_db_session, "liker", original_message.message_id
        )

        assert result["user_liked"] is False
        assert result["like_count"] == 0

    def test_get_message_likes(self, test_db_session, create_user):
        create_user(user_id="author")
        create_user(user_id="liker1", display_name="Liker 1")
        create_user(user_id="liker2", display_name="Liker 2")

        message_data = MessageCreate(
            to_user_id="author",
            message_type=MessageTypeEnum.comment,
            content="Popular message",
        )
        original_message = message_service.create_message(
            test_db_session, message_data, "author"
        )

        message_service.toggle_heart_reaction(
            test_db_session, "liker1", original_message.message_id
        )
        message_service.toggle_heart_reaction(
            test_db_session, "liker2", original_message.message_id
        )

        result = message_service.get_message_likes(
            test_db_session, original_message.message_id
        )

        assert len(result) == 2
        user_ids = [like["userId"] for like in result]
        assert "liker1" in user_ids
        assert "liker2" in user_ids

    def test_get_heart_states_for_messages(self, test_db_session, create_user):
        create_user(user_id="user")
        create_user(user_id="author")

        message1_data = MessageCreate(
            to_user_id="author",
            message_type=MessageTypeEnum.comment,
            content="Message 1",
        )
        message2_data = MessageCreate(
            to_user_id="author",
            message_type=MessageTypeEnum.comment,
            content="Message 2",
        )

        message1 = message_service.create_message(
            test_db_session, message1_data, "author"
        )
        message2 = message_service.create_message(
            test_db_session, message2_data, "author"
        )

        message_service.toggle_heart_reaction(
            test_db_session, "user", message1.message_id
        )

        result = message_service.get_heart_states_for_messages(
            test_db_session, "user", [message1.message_id, message2.message_id]
        )

        assert result[message1.message_id]["user_liked"] is True
        assert result[message1.message_id]["like_count"] == 1
        assert result[message2.message_id]["user_liked"] is False
        assert result[message2.message_id]["like_count"] == 0
