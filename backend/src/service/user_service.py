import uuid
from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from src.db.tables import Answer, Message, ProfileItem, User
from src.schema.user import UserCreate, UserUpdate
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


def update_user(db: Session, user_id: str, user_update: UserUpdate) -> User | None:
    """Update user information including notification settings."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False

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
    """Update user's last login timestamp."""
    db_user = get_user(db, user_id)
    if db_user:
        db_user.last_login_at = datetime.utcnow()
        db.commit()


def discover_users(
    db: Session,
    discovery_type: Literal["activity", "random", "mixed"] = "mixed",
    limit: int = 10,
    offset: int = 0,
    current_user_id: str | None = None,
) -> list[User]:
    """
    ユーザー発見機能

    Args:
        db: データベースセッション
        discovery_type: 発見タイプ ("activity", "random", "mixed")
        limit: 取得数上限
        offset: オフセット
        current_user_id: 現在のユーザーID（除外用）

    Returns:
        発見されたユーザーリスト
    """
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    three_days_ago = now - timedelta(days=3)

    base_query = db.query(User)

    # 自分自身を除外
    if current_user_id:
        base_query = base_query.filter(User.user_id != current_user_id)

    if discovery_type == "activity":
        # アクティビティベースのユーザー発見
        activity_query = base_query.filter(
            or_(
                # 新規登録ユーザー (7日以内)
                User.created_at >= seven_days_ago,
                # 最近ログインしたユーザー (3日以内)
                User.last_login_at >= three_days_ago,
            )
        ).distinct()

        # 最近Q&A回答またはメッセージ送信をしたユーザーを追加
        recent_activity_users = (
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

        # 両方のクエリを結合
        final_query = activity_query.union(recent_activity_users)

    elif discovery_type == "random":
        # 完全にランダム
        final_query = base_query.order_by(func.random())

    else:  # mixed
        # アクティビティユーザー + ランダムユーザーの混合
        activity_limit = limit // 2
        random_limit = limit - activity_limit

        # アクティビティユーザーを直接取得（再帰呼び出しを避ける）
        activity_query = base_query.filter(
            or_(
                # 新規登録ユーザー (7日以内)
                User.created_at >= seven_days_ago,
                # 最近ログインしたユーザー (3日以内)
                User.last_login_at >= three_days_ago,
            )
        ).distinct()

        # 最近Q&A回答またはメッセージ送信をしたユーザーを追加
        recent_activity_users = (
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

        # アクティビティユーザーを取得
        activity_users = (
            activity_query.union(recent_activity_users).limit(activity_limit).all()
        )

        # アクティビティユーザーのIDを取得
        activity_user_ids = [user.user_id for user in activity_users]
        exclude_ids = activity_user_ids[:]
        if current_user_id:
            exclude_ids.append(current_user_id)

        # ランダムユーザー（アクティビティユーザーを除外）
        random_query = base_query.order_by(func.random())
        if exclude_ids:
            random_query = random_query.filter(~User.user_id.in_(exclude_ids))

        random_users = random_query.limit(random_limit).all()

        return activity_users + random_users

    return final_query.offset(offset).limit(limit).all()
