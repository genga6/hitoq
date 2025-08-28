from sqlalchemy.orm import Session, joinedload

from src.db.tables import (
    Message,
    MessageStatusEnum,
    MessageTypeEnum,
    NotificationLevelEnum,
    User,
)


def should_notify_user(
    notification_level: NotificationLevelEnum, message_type: MessageTypeEnum
) -> bool:
    if notification_level == NotificationLevelEnum.none:
        return False
    elif notification_level == NotificationLevelEnum.important:
        return message_type == MessageTypeEnum.comment
    else:
        return True


def get_notifications_for_user(
    db: Session, user_id: str, skip: int = 0, limit: int = 50
) -> list[Message]:
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
        query = query.filter(Message.message_type == MessageTypeEnum.comment)

    notifications = (
        query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    )

    return notifications


def mark_all_notifications_as_read(db: Session, user_id: str) -> int:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return 0

    if user.notification_level == NotificationLevelEnum.none:
        return 0

    query = db.query(Message).filter(
        Message.to_user_id == user_id, Message.status == MessageStatusEnum.unread
    )

    if user.notification_level == NotificationLevelEnum.important:
        query = query.filter(Message.message_type == MessageTypeEnum.comment)

    # Update all matching messages to read status
    updated_count = query.update(
        {Message.status: MessageStatusEnum.read}, synchronize_session="fetch"
    )

    db.commit()
    return updated_count
