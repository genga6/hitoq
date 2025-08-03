import uuid

from sqlalchemy.orm import Session, joinedload

from src.db.tables import Answer, ProfileItem, User
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
