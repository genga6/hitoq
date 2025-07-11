import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.db.tables import User
from src.schema.user import UserCreate


def get_user(db: Session, user_id: uuid.UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_username(db: Session, user_name: str) -> list[User]:
    return db.query(User).filter(User.user_name == user_name).all()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    existing_user = db.query(User).filter(User.user_name == user_in.user_name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = User(**user_in.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
