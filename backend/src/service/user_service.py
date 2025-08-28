import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from src.db.tables import Answer, AnswerLike, Message, MessageLike, ProfileItem, User
from src.schema.user import UserCreate
from src.service.qna_service import initialize_default_questions
from src.service.yaml_loader import load_default_labels


def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_with_profile_items(db: Session, user_id: str) -> User | None:
    return (
        db.query(User)
        .options(joinedload(User.profile_items))
        .filter(User.user_id == user_id)
        .first()
    )


def get_user_with_qna_items(db: Session, user_id: str) -> User | None:
    return (
        db.query(User)
        .options(joinedload(User.answers).joinedload(Answer.question))
        .filter(User.user_id == user_id)
        .first()
    )


def get_user_by_username(db: Session, user_name: str) -> User | None:
    return db.query(User).filter(User.user_name == user_name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def search_users_by_display_name(
    db: Session, display_name: str, limit: int = 10
) -> list[User]:
    return (
        db.query(User)
        .filter(User.display_name.ilike(f"%{display_name}%"))
        .limit(limit)
        .all()
    )


def create_default_profile_items(db: Session, user_id: str) -> None:
    default_labels = load_default_labels()

    for i, label in enumerate(default_labels, 1):
        profile_item = ProfileItem(
            profile_item_id=uuid.uuid4(),
            user_id=user_id,
            label=label,
            value="",
            display_order=i,
        )
        db.add(profile_item)

    db.commit()


def delete_user(db: Session, user_id: str) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    # Delete all likes on messages sent by this user
    user_messages = db.query(Message).filter(Message.from_user_id == user_id).all()
    message_ids = [msg.message_id for msg in user_messages]
    if message_ids:
        db.query(MessageLike).filter(MessageLike.message_id.in_(message_ids)).delete(
            synchronize_session=False
        )

    # Delete all likes on answers by this user
    user_answers = db.query(Answer).filter(Answer.user_id == user_id).all()
    answer_ids = [ans.answer_id for ans in user_answers]
    if answer_ids:
        db.query(AnswerLike).filter(AnswerLike.answer_id.in_(answer_ids)).delete(
            synchronize_session=False
        )

    # Delete all likes made by this user
    db.query(MessageLike).filter(MessageLike.user_id == user_id).delete(
        synchronize_session=False
    )
    db.query(AnswerLike).filter(AnswerLike.user_id == user_id).delete(
        synchronize_session=False
    )

    # Now delete the user (cascade will handle messages, answers, etc.)
    db.delete(db_user)
    db.commit()
    return True


def upsert_user(db: Session, user_in: UserCreate) -> User:
    # Initialize default questions if they don't exist
    initialize_default_questions(db)

    db_user = get_user_by_username(db, user_in.user_name)
    is_new_user = db_user is None

    if db_user:
        update_data = user_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_user, key, value)
    else:
        db_user = User(**user_in.model_dump())

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if is_new_user:
        create_default_profile_items(db, db_user.user_id)

    return db_user


def update_last_login(db: Session, user_id: str) -> None:
    db_user = get_user(db, user_id)
    if db_user:
        db_user.last_login_at = datetime.now(timezone.utc)
        db.commit()


def _get_activity_based_users(
    db: Session, base_query, seven_days_ago: datetime, three_days_ago: datetime
):
    # 新規登録・最近ログインしたユーザー
    activity_query = base_query.filter(
        or_(
            User.created_at >= seven_days_ago,
            User.last_login_at >= three_days_ago,
        )
    ).distinct()

    # 最近Q&A回答またはメッセージ送信をしたユーザー
    recent_activity_query = (
        base_query.join(Answer, User.user_id == Answer.user_id, isouter=True)
        .join(Message, User.user_id == Message.from_user_id, isouter=True)
        .filter(
            or_(
                Answer.created_at >= three_days_ago,
                Message.created_at >= three_days_ago,
            )
        )
        .distinct()
    )

    return activity_query.union(recent_activity_query)


def _get_random_users_excluding(
    db: Session, base_query, exclude_ids: list[str], limit: int
) -> list[User]:
    random_query = base_query.order_by(func.random())
    if exclude_ids:
        random_query = random_query.filter(~User.user_id.in_(exclude_ids))
    return random_query.limit(limit).all()


def discover_users(
    db: Session,
    discovery_type: Literal["activity", "random", "recommend"] = "recommend",
    limit: int = 10,
    offset: int = 0,
    current_user_id: str | None = None,
) -> list[User]:
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    three_days_ago = now - timedelta(days=3)

    base_query = db.query(User)
    if current_user_id:
        base_query = base_query.filter(User.user_id != current_user_id)

    if discovery_type == "activity":
        final_query = _get_activity_based_users(
            db, base_query, seven_days_ago, three_days_ago
        )
        return final_query.offset(offset).limit(limit).all()

    elif discovery_type == "random":
        final_query = base_query.order_by(func.random())
        return final_query.offset(offset).limit(limit).all()

    else:  # recommend　# TODO: Currently, it is a simple mix, but we may implement an AI recommendation function in the future.
        activity_limit = limit // 2
        random_limit = limit - activity_limit

        activity_query = _get_activity_based_users(
            db, base_query, seven_days_ago, three_days_ago
        )
        activity_users = activity_query.limit(activity_limit).all()

        exclude_ids = [user.user_id for user in activity_users]
        if current_user_id:
            exclude_ids.append(current_user_id)

        random_users = _get_random_users_excluding(
            db, base_query, exclude_ids, random_limit
        )

        return activity_users + random_users
