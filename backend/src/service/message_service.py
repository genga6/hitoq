import uuid
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from src.db.tables import Message, MessageStatusEnum
from src.schema.message import MessageCreate, MessageUpdate


def create_message(db: Session, message: MessageCreate, from_user_id: str) -> Message:
    """Create a new message."""
    db_message = Message(
        message_id=str(uuid.uuid4()),
        from_user_id=from_user_id,
        to_user_id=message.to_user_id,
        message_type=message.message_type,
        content=message.content,
        reference_answer_id=message.reference_answer_id,
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
