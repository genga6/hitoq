import uuid
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.db.tables import (
    Message,
    MessageStatusEnum,
    MessageTypeEnum,
    NotificationLevelEnum,
    User,
)
from src.schema.message import MessageCreate, MessageUpdate


def should_notify_user(
    notification_level: NotificationLevelEnum, message_type: MessageTypeEnum
) -> bool:
    """Determine if user should be notified based on their notification level and message type."""
    if notification_level == NotificationLevelEnum.none:
        return False
    elif notification_level == NotificationLevelEnum.important:
        return message_type in [MessageTypeEnum.question, MessageTypeEnum.request]
    else:
        return True


def create_message(db: Session, message: MessageCreate, from_user_id: str) -> Message:
    db_message = Message(
        message_id=str(uuid.uuid4()),
        from_user_id=from_user_id,
        to_user_id=message.to_user_id,
        message_type=message.message_type,
        content=message.content,
        reference_answer_id=message.reference_answer_id,
        parent_message_id=message.parent_message_id,
        status=MessageStatusEnum.unread,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_messages_for_user(
    db: Session, user_id: str, skip: int = 0, limit: int = 50
) -> list[Message]:
    """Get messages received by a user."""
    return (
        db.query(Message)
        .options(joinedload(Message.from_user))
        .filter(Message.to_user_id == user_id)
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_message(db: Session, message_id: str) -> Optional[Message]:
    """Get a message by ID."""
    return (
        db.query(Message)
        .options(joinedload(Message.from_user), joinedload(Message.to_user))
        .filter(Message.message_id == message_id)
        .first()
    )


def update_message_status(
    db: Session, message_id: str, status_update: MessageUpdate
) -> Optional[Message]:
    """Update message status."""
    db_message = db.query(Message).filter(Message.message_id == message_id).first()
    if db_message:
        db_message.status = status_update.status
        db.commit()
        db.refresh(db_message)
    return db_message


def get_unread_count(db: Session, user_id: str) -> int:
    """Get count of unread messages for a user."""
    return (
        db.query(Message)
        .filter(
            Message.to_user_id == user_id, Message.status == MessageStatusEnum.unread
        )
        .count()
    )


def get_notification_count(db: Session, user_id: str) -> int:
    """Get count of unread messages that should notify the user based on their notification level."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return 0

    if user.notification_level == NotificationLevelEnum.none:
        return 0

    query = db.query(Message).filter(
        Message.to_user_id == user_id, Message.status == MessageStatusEnum.unread
    )

    if user.notification_level == NotificationLevelEnum.important:
        query = query.filter(
            Message.message_type.in_(
                [MessageTypeEnum.question, MessageTypeEnum.request]
            )
        )

    return query.count()


def get_notifications_for_user(
    db: Session, user_id: str, skip: int = 0, limit: int = 10
) -> list[Message]:
    """Get notification messages for a user based on their notification level."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return []

    if user.notification_level == NotificationLevelEnum.none:
        return []

    query = (
        db.query(Message)
        .options(joinedload(Message.from_user))
        .filter(Message.to_user_id == user_id)
    )

    if user.notification_level == NotificationLevelEnum.important:
        query = query.filter(
            Message.message_type.in_(
                [MessageTypeEnum.question, MessageTypeEnum.request]
            )
        )

    return query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()


def get_message_thread(db: Session, message_id: str, user_id: str) -> list[Message]:
    """Get a message thread with hierarchical structure like Twitter."""
    root_message = db.query(Message).filter(Message.message_id == message_id).first()
    if not root_message:
        return []

    while root_message.parent_message_id:
        root_message = (
            db.query(Message)
            .filter(Message.message_id == root_message.parent_message_id)
            .first()
        )
        if not root_message:
            return []

    if root_message.from_user_id != user_id and root_message.to_user_id != user_id:
        return []

    # Get all messages in the thread tree with depth level (excluding heart reactions)
    from sqlalchemy import text

    thread_data = db.execute(
        text("""
            WITH RECURSIVE thread_tree AS (
                -- Base case: direct replies to root message (depth 1), excluding heart reactions
                SELECT m.*, 1 as depth, m.parent_message_id as thread_parent
                FROM messages m 
                WHERE m.parent_message_id = :root_id
                AND NOT (m.message_type = 'reaction' AND m.content = '❤️')
                
                UNION ALL
                
                -- Recursive case: replies to replies (increasing depth), excluding heart reactions
                SELECT m.*, tt.depth + 1 as depth, m.parent_message_id as thread_parent
                FROM messages m
                INNER JOIN thread_tree tt ON m.parent_message_id = tt.message_id
                WHERE NOT (m.message_type = 'reaction' AND m.content = '❤️')
            )
            SELECT *, thread_parent FROM thread_tree ORDER BY thread_parent, created_at ASC
            """),
        {"root_id": root_message.message_id},
    ).fetchall()

    if not thread_data:
        return []

    # Get Message objects and add depth information
    message_ids = [row[0] for row in thread_data]  # message_id is first column
    depth_map = {row[0]: row[-2] for row in thread_data}  # message_id -> depth
    parent_map = {row[0]: row[-1] for row in thread_data}  # message_id -> parent_id

    thread_messages = (
        db.query(Message)
        .options(joinedload(Message.from_user), joinedload(Message.to_user))
        .filter(Message.message_id.in_(message_ids))
        .all()
    )

    for message in thread_messages:
        message.thread_depth = depth_map.get(message.message_id, 0)
        message.thread_parent_id = parent_map.get(message.message_id)

    def sort_messages_hierarchically(messages):
        children_map: dict = {}
        root_messages: list = []

        for msg in messages:
            parent_id = getattr(msg, "thread_parent_id", None)
            if parent_id == root_message.message_id:
                # Direct reply to root
                root_messages.append(msg)
            else:
                # Reply to another reply
                if parent_id not in children_map:
                    children_map[parent_id] = []
                children_map[parent_id].append(msg)

        # Build hierarchical list
        result = []

        def add_message_and_children(msg):
            result.append(msg)
            # Add children in chronological order
            children = children_map.get(msg.message_id, [])
            children.sort(key=lambda x: x.created_at)
            for child in children:
                add_message_and_children(child)

        # Add root messages and their descendants
        root_messages.sort(key=lambda x: x.created_at)
        for root_msg in root_messages:
            add_message_and_children(root_msg)

        return result

    return sort_messages_hierarchically(thread_messages)


def get_messages_with_replies(
    db: Session, user_id: str, skip: int = 0, limit: int = 50
) -> list[Message]:
    """Get messages for a user with reply counts (excluding replies themselves)."""
    # Get only root messages (messages without parent_message_id)
    messages = (
        db.query(Message)
        .options(joinedload(Message.from_user))
        .filter(
            Message.to_user_id == user_id,
            Message.parent_message_id.is_(None),  # Only root messages
        )
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Add reply count to each message
    for message in messages:
        reply_count = (
            db.query(Message)
            .filter(Message.parent_message_id == message.message_id)
            .count()
        )
        # Add reply_count as an attribute (will be handled in schema)
        message.reply_count = reply_count

    return messages


def get_conversation_messages_for_user(
    db: Session, user_id: str, skip: int = 0, limit: int = 50
) -> list[Message]:
    """Get all conversation messages for a user (both sent and received, root messages only)."""
    # Get root messages where user is either sender or receiver
    messages = (
        db.query(Message)
        .options(joinedload(Message.from_user), joinedload(Message.to_user))
        .filter(
            ((Message.to_user_id == user_id) | (Message.from_user_id == user_id)),
            Message.parent_message_id.is_(None),  # Only root messages
        )
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Add reply count to each message
    for message in messages:
        reply_count = (
            db.query(Message)
            .filter(Message.parent_message_id == message.message_id)
            .count()
        )
        # Add reply_count as an attribute (will be handled in schema)
        message.reply_count = reply_count

    return messages


def update_message_content(
    db: Session, message_id: str, new_content: str
) -> Optional[Message]:
    """Update message content."""
    db_message = db.query(Message).filter(Message.message_id == message_id).first()
    if db_message:
        db_message.content = new_content
        db.commit()
        db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: str) -> bool:
    """Delete a message and all its replies."""
    try:
        # First delete all replies recursively
        replies = (
            db.query(Message).filter(Message.parent_message_id == message_id).all()
        )
        for reply in replies:
            delete_message(db, reply.message_id)

        # Then delete the message itself
        db_message = db.query(Message).filter(Message.message_id == message_id).first()
        if db_message:
            db.delete(db_message)
            db.commit()
            return True
    except Exception:
        db.rollback()
        return False
    return False


def get_user_heart_reaction(
    db: Session, user_id: str, target_message_id: str
) -> Optional[Message]:
    """Get user's existing heart reaction to a specific message."""
    return (
        db.query(Message)
        .filter(
            Message.from_user_id == user_id,
            Message.parent_message_id == target_message_id,
            Message.message_type == MessageTypeEnum.reaction,
            Message.content == "❤️",
        )
        .first()
    )


def toggle_heart_reaction(
    db: Session, user_id: str, target_message_id: str, to_user_id: str
) -> dict:
    """Toggle heart reaction for a message. Returns action taken and like count."""
    import uuid

    existing_reaction = get_user_heart_reaction(db, user_id, target_message_id)

    if existing_reaction:
        # Remove existing reaction
        db.delete(existing_reaction)
        db.commit()
        action = "removed"
    else:
        # Add new reaction
        new_reaction = Message(
            message_id=str(uuid.uuid4()),
            from_user_id=user_id,
            to_user_id=to_user_id,
            message_type=MessageTypeEnum.reaction,
            content="❤️",
            parent_message_id=target_message_id,
            status=MessageStatusEnum.unread,
        )
        db.add(new_reaction)
        db.commit()
        action = "added"

    # Count total heart reactions for this message
    like_count = (
        db.query(Message)
        .filter(
            Message.parent_message_id == target_message_id,
            Message.message_type == MessageTypeEnum.reaction,
            Message.content == "❤️",
        )
        .count()
    )

    return {"action": action, "like_count": like_count}


def get_message_likes(db: Session, message_id: str) -> list[dict]:
    """Get list of users who liked a specific message."""
    likes = (
        db.query(Message)
        .options(joinedload(Message.from_user))
        .filter(
            Message.parent_message_id == message_id,
            Message.message_type == MessageTypeEnum.reaction,
            Message.content == "❤️",
        )
        .order_by(Message.created_at.desc())
        .all()
    )

    return [
        {
            "user_id": like.from_user.user_id,
            "user_name": like.from_user.user_name,
            "display_name": like.from_user.display_name,
            "icon_url": like.from_user.icon_url,
            "created_at": like.created_at.isoformat(),
        }
        for like in likes
        if like.from_user
    ]


def get_heart_states_for_messages(
    db: Session, user_id: str, message_ids: list[str]
) -> dict:
    """Get heart states (liked status and count) for multiple messages."""
    if not message_ids:
        return {}

    # Get user's likes for these messages
    user_likes = (
        db.query(Message.parent_message_id)
        .filter(
            Message.from_user_id == user_id,
            Message.parent_message_id.in_(message_ids),
            Message.message_type == MessageTypeEnum.reaction,
            Message.content == "❤️",
        )
        .all()
    )
    user_liked_messages = {like[0] for like in user_likes}

    # Get total like counts for these messages
    like_counts = (
        db.query(
            Message.parent_message_id, func.count(Message.message_id).label("count")
        )
        .filter(
            Message.parent_message_id.in_(message_ids),
            Message.message_type == MessageTypeEnum.reaction,
            Message.content == "❤️",
        )
        .group_by(Message.parent_message_id)
        .all()
    )

    # Build result dictionary
    result = {}
    for message_id in message_ids:
        count = next(
            (
                item.count
                for item in like_counts
                if item.parent_message_id == message_id
            ),
            0,
        )
        result[message_id] = {
            "liked": message_id in user_liked_messages,
            "count": count,
        }

    return result
