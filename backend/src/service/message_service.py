import uuid

from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from src.db.tables import (
    Message,
    MessageLike,
    MessageStatusEnum,
    MessageTypeEnum,
    UserBlock,
)
from src.schema.message import MessageCreate, MessageUpdate
from src.schema.user import UserRead


def create_message(db: Session, message: MessageCreate, from_user_id: str) -> Message:
    is_blocked = (
        db.query(UserBlock)
        .filter(
            UserBlock.blocker_user_id == message.to_user_id,
            UserBlock.blocked_user_id == from_user_id,
        )
        .first()
        is not None
    )

    if is_blocked:
        raise ValueError("Cannot send message to user who has blocked you")

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
    blocked_user_ids_subquery = db.query(UserBlock.blocked_user_id).filter(
        UserBlock.blocker_user_id == user_id
    )

    return (
        db.query(Message)
        .options(joinedload(Message.from_user))
        .filter(
            Message.to_user_id == user_id,
            ~Message.from_user_id.in_(blocked_user_ids_subquery),
        )
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_message(db: Session, message_id: str) -> Message | None:
    return (
        db.query(Message)
        .options(joinedload(Message.from_user), joinedload(Message.to_user))
        .filter(Message.message_id == message_id)
        .first()
    )


def update_message_status(
    db: Session, message_id: str, status_update: MessageUpdate
) -> Message | None:
    db_message = db.query(Message).filter(Message.message_id == message_id).first()
    if db_message:
        db_message.status = status_update.status
        db.commit()
        db.refresh(db_message)
    return db_message


def get_unread_count(db: Session, user_id: str) -> int:
    return (
        db.query(Message)
        .filter(
            Message.to_user_id == user_id, Message.status == MessageStatusEnum.unread
        )
        .count()
    )


def get_message_thread(db: Session, message_id: str, user_id: str) -> list[Message]:
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

    thread_data = db.execute(
        text("""
            WITH RECURSIVE thread_tree AS (
                -- Base case: direct replies to root message (depth 1), excluding heart reactions
                SELECT m.*, 1 as depth, m.parent_message_id as thread_parent
                FROM messages m 
                WHERE m.parent_message_id = :root_id
                AND NOT (m.message_type = 'like' AND m.content = '❤️')
                
                UNION ALL
                
                -- Recursive case: replies to replies (increasing depth), excluding heart reactions
                SELECT m.*, tt.depth + 1 as depth, m.parent_message_id as thread_parent
                FROM messages m
                INNER JOIN thread_tree tt ON m.parent_message_id = tt.message_id
                WHERE NOT (m.message_type = 'like' AND m.content = '❤️')
            )
            SELECT *, thread_parent FROM thread_tree ORDER BY thread_parent, created_at ASC
            """),
        {"root_id": root_message.message_id},
    ).fetchall()

    if not thread_data:
        return []

    message_ids = [row[0] for row in thread_data]
    depth_map = {row[0]: row[-2] for row in thread_data}
    parent_map = {row[0]: row[-1] for row in thread_data}

    thread_messages = (
        db.query(Message)
        .options(joinedload(Message.from_user), joinedload(Message.to_user))
        .filter(Message.message_id.in_(message_ids))
        .all()
    )

    for message in thread_messages:
        message.thread_depth = depth_map.get(message.message_id, 0)
        message.thread_parent_id = parent_map.get(message.message_id)

    def sort_messages_hierarchically(messages: list[Message]) -> list[Message]:
        children_map: dict[str, list[Message]] = {}
        root_messages: list[Message] = []

        for msg in messages:
            parent_id: str | None = getattr(msg, "thread_parent_id", None)

            if parent_id == root_message.message_id:
                root_messages.append(msg)
            elif parent_id is not None:
                if parent_id not in children_map:
                    children_map[parent_id] = []
                children_map[parent_id].append(msg)

        result: list[Message] = []

        def add_message_and_children(msg: Message) -> None:
            result.append(msg)

            children = children_map.get(msg.message_id, [])
            children.sort(key=lambda x: x.created_at)
            for child in children:
                add_message_and_children(child)

        root_messages.sort(key=lambda x: x.created_at)
        for root_msg in root_messages:
            add_message_and_children(root_msg)

        return result

    return sort_messages_hierarchically(thread_messages)


def _get_full_thread_count(db: Session, root_message_id: str) -> int:
    thread_count_data = db.execute(
        text("""
            WITH RECURSIVE thread_tree AS (
                SELECT m.message_id
                FROM messages m 
                WHERE m.parent_message_id = :root_id
                AND NOT (m.message_type = 'like' AND m.content = '❤️')
                
                UNION ALL
                
                SELECT m.message_id
                FROM messages m
                INNER JOIN thread_tree tt ON m.parent_message_id = tt.message_id
                WHERE NOT (m.message_type = 'like' AND m.content = '❤️')
            )
            SELECT count(*) FROM thread_tree
            """),
        {"root_id": root_message_id},
    ).scalar_one_or_none()

    return thread_count_data if thread_count_data is not None else 0


def get_messages_with_replies(
    db: Session, user_id: str, skip: int = 0, limit: int = 50
) -> list[Message]:
    messages = (
        db.query(Message)
        .options(joinedload(Message.from_user))
        .filter(
            Message.to_user_id == user_id,
            Message.parent_message_id.is_(None),
        )
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    for message in messages:
        message.reply_count = _get_full_thread_count(db, message.message_id)

    return messages


def get_conversation_messages_for_user(
    db: Session, user_id: str, skip: int = 0, limit: int = 50
) -> list[Message]:
    messages = (
        db.query(Message)
        .options(joinedload(Message.from_user), joinedload(Message.to_user))
        .filter(
            ((Message.to_user_id == user_id) | (Message.from_user_id == user_id)),
            Message.parent_message_id.is_(None),
        )
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    for message in messages:
        message.reply_count = _get_full_thread_count(db, message.message_id)

    return messages


def update_message_content(
    db: Session, message_id: str, new_content: str
) -> Message | None:
    db_message = db.query(Message).filter(Message.message_id == message_id).first()
    if db_message:
        db_message.content = new_content
        db.commit()
        db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: str) -> bool:
    try:
        replies = (
            db.query(Message).filter(Message.parent_message_id == message_id).all()
        )
        for reply in replies:
            delete_message(db, reply.message_id)

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
) -> Message | None:
    return (
        db.query(Message)
        .filter(
            Message.from_user_id == user_id,
            Message.parent_message_id == target_message_id,
            Message.message_type == MessageTypeEnum.like,
            Message.content == "❤️",
        )
        .first()
    )


def toggle_heart_reaction(db: Session, user_id: str, target_message_id: str) -> dict:
    existing_like = (
        db.query(MessageLike)
        .filter(
            MessageLike.user_id == user_id,
            MessageLike.message_id == target_message_id,
        )
        .first()
    )

    if existing_like:
        db.delete(existing_like)
        user_liked = False
    else:
        new_like = MessageLike(
            message_id=target_message_id,
            user_id=user_id,
        )
        db.add(new_like)
        user_liked = True

    db.commit()

    like_count = (
        db.query(MessageLike)
        .filter(MessageLike.message_id == target_message_id)
        .count()
    )

    return {"user_liked": user_liked, "like_count": like_count}


def get_message_likes(db: Session, message_id: str) -> list[dict]:
    likes = (
        db.query(MessageLike)
        .options(joinedload(MessageLike.user))
        .filter(MessageLike.message_id == message_id)
        .order_by(MessageLike.created_at.desc())
        .all()
    )

    return [
        UserRead.model_validate(like.user).model_dump(by_alias=True)
        for like in likes
        if like.user
    ]


def get_heart_states_for_messages(
    db: Session, user_id: str, message_ids: list[str]
) -> dict:
    if not message_ids:
        return {}

    user_likes = (
        db.query(MessageLike.message_id)
        .filter(
            MessageLike.user_id == user_id,
            MessageLike.message_id.in_(message_ids),
        )
        .all()
    )
    user_liked_messages = {like[0] for like in user_likes}

    like_counts = (
        db.query(MessageLike.message_id, func.count(MessageLike.like_id).label("count"))
        .filter(MessageLike.message_id.in_(message_ids))
        .group_by(MessageLike.message_id)
        .all()
    )

    result = {}
    for message_id in message_ids:
        count = next(
            (item.count for item in like_counts if item.message_id == message_id),
            0,
        )
        result[message_id] = {
            "user_liked": message_id in user_liked_messages,
            "like_count": count,
        }

    return result
