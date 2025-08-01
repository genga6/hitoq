import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


# https://docs.sqlalchemy.org/en/20/orm/quickstart.html
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(300), nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    visits_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    answers: Mapped[list["Answer"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    profile_items: Mapped[list["ProfileItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    visits_received: Mapped[list["Visit"]] = relationship(
        "Visit",
        foreign_keys="[Visit.visited_user_id]",
        back_populates="visited_user",
        cascade="all, delete-orphan",
    )
    visits_made: Mapped[list["Visit"]] = relationship(
        "Visit",
        foreign_keys="[Visit.visitor_user_id]",
        back_populates="visitor_user",
        cascade="all, delete-orphan",
    )
    messages_sent: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="[Message.from_user_id]",
        back_populates="from_user",
        cascade="all, delete-orphan",
    )
    messages_received: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="[Message.to_user_id]",
        back_populates="to_user",
        cascade="all, delete-orphan",
    )


class ProfileItem(Base):
    __tablename__ = "profile_items"

    profile_item_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    label: Mapped[str]
    value: Mapped[str]
    display_order: Mapped[int]

    user: Mapped["User"] = relationship(back_populates="profile_items")


class MessageTypeEnum(enum.Enum):
    question = "question"
    comment = "comment"
    request = "request"
    reaction = "reaction"


class MessageStatusEnum(enum.Enum):
    unread = "unread"
    read = "read"
    replied = "replied"


class Question(Base):
    __tablename__ = "questions"

    question_id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[str] = mapped_column(
        String, nullable=False
    )  # categories.pyのCategoryInfo.id
    text: Mapped[str]
    display_order: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    answers: Mapped[list["Answer"]] = relationship(back_populates="question")


class Answer(Base):
    __tablename__ = "answers"

    answer_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.question_id"))
    answer_text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship(back_populates="answers")


class Visit(Base):
    __tablename__ = "visits"

    visit_id: Mapped[int] = mapped_column(primary_key=True)
    visitor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id"), nullable=True
    )
    visited_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"), nullable=False
    )
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    visited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    visitor_user: Mapped["User"] = relationship(
        "User", foreign_keys=[visitor_user_id], back_populates="visits_made"
    )
    visited_user: Mapped["User"] = relationship(
        "User", foreign_keys=[visited_user_id], back_populates="visits_received"
    )


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    from_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    to_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    message_type: Mapped[MessageTypeEnum]
    content: Mapped[str] = mapped_column(String(500))
    reference_answer_id: Mapped[int | None] = mapped_column(
        ForeignKey("answers.answer_id"), nullable=True
    )
    status: Mapped[MessageStatusEnum] = mapped_column(default=MessageStatusEnum.unread)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    from_user: Mapped["User"] = relationship(
        "User", foreign_keys=[from_user_id], back_populates="messages_sent"
    )
    to_user: Mapped["User"] = relationship(
        "User", foreign_keys=[to_user_id], back_populates="messages_received"
    )
    reference_answer: Mapped["Answer"] = relationship(
        "Answer", foreign_keys=[reference_answer_id]
    )
