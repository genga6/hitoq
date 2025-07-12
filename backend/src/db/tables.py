import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


# https://docs.sqlalchemy.org/en/20/orm/quickstart.html
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        primary_key=True
    )  # TODO: XのユーザーIDに置き換わる
    user_name: Mapped[str]  # Xのユーザー名
    bio: Mapped[str | None]
    icon_url: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    answers: Mapped[list["Answer"]] = relationship(back_populates="user")
    profile_items: Mapped[list["ProfileItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    bucket_list_items: Mapped[list["BucketListItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class ProfileItem(Base):
    __tablename__ = "profile_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    label: Mapped[str]
    value: Mapped[str]
    display_order: Mapped[int]


class BucketListItem(Base):
    __tablename__ = "bucket_list_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    content: Mapped[str]
    is_completed: Mapped[bool] = mapped_column(default=False)
    display_order: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="bucket_list_items")


class QuestionCategoryEnum(enum.Enum):
    self_introduction = "self-introduction"
    values = "values"
    otaku = "otaku"
    misc = "misc"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[QuestionCategoryEnum]
    text: Mapped[str]
    display_order: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    answers: Mapped[list["Answer"]] = relationship(back_populates="question")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer_text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship(back_populates="answers")
