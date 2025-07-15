from sqlalchemy.orm import Session, joinedload

from src.db.tables import Answer, User
from src.schema.user import UserCreate


def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_with_profile_items(db: Session, user_id: str) -> User | None:
    return (
        db.query(User)
        .options(joinedload(User.profile_items))
        .filter(User.user_id == user_id)
        .first()
    )


def get_user_with_bucket_list_items(db: Session, user_id: str) -> User | None:
    return (
        db.query(User)
        .options(joinedload(User.bucket_list_items))
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


def upsert_user(db: Session, user_in: UserCreate) -> User:
    db_user = get_user_by_username(db, user_in.user_name)
    if db_user:
        print(f"Updating existing user: {user_in.user_name}")
        update_data = user_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_user, key, value)
    else:
        print(f"Creating new user: {user_in.user_name}")
        db_user = User(**user_in.model_dump())

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
