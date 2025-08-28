import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


# https://docs.sqlalchemy.org/en/20/orm/quickstart.html
class Base(DeclarativeBase):
    pass


class NotificationLevelEnum(enum.Enum):
    none = "none"
    important = "important"
    all = "all"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(300), nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    visits_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notification_level: Mapped[NotificationLevelEnum] = mapped_column(
        default=NotificationLevelEnum.all, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
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
    blocks_made: Mapped[list["UserBlock"]] = relationship(
        "UserBlock",
        foreign_keys="[UserBlock.blocker_user_id]",
        back_populates="blocker_user",
        cascade="all, delete-orphan",
    )
    blocks_received: Mapped[list["UserBlock"]] = relationship(
        "UserBlock",
        foreign_keys="[UserBlock.blocked_user_id]",
        back_populates="blocked_user",
        cascade="all, delete-orphan",
    )
    reports_made: Mapped[list["UserReport"]] = relationship(
        "UserReport",
        foreign_keys="[UserReport.reporter_user_id]",
        back_populates="reporter_user",
        cascade="all, delete-orphan",
    )
    reports_received: Mapped[list["UserReport"]] = relationship(
        "UserReport",
        foreign_keys="[UserReport.reported_user_id]",
        back_populates="reported_user",
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
    comment = "comment"
    like = "like"


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


class ReportTypeEnum(enum.Enum):
    spam = "spam"
    harassment = "harassment"
    inappropriate_content = "inappropriate_content"
    other = "other"


class ReportStatusEnum(enum.Enum):
    pending = "pending"
    reviewing = "reviewing"
    resolved = "resolved"
    dismissed = "dismissed"


class UserBlock(Base):
    __tablename__ = "user_blocks"

    block_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    blocker_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    blocked_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    blocker_user: Mapped["User"] = relationship(
        "User", foreign_keys=[blocker_user_id], back_populates="blocks_made"
    )
    blocked_user: Mapped["User"] = relationship(
        "User", foreign_keys=[blocked_user_id], back_populates="blocks_received"
    )


class UserReport(Base):
    __tablename__ = "user_reports"

    report_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    reporter_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    reported_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    report_type: Mapped[ReportTypeEnum]
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[ReportStatusEnum] = mapped_column(default=ReportStatusEnum.pending)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    reporter_user: Mapped["User"] = relationship(
        "User", foreign_keys=[reporter_user_id], back_populates="reports_made"
    )
    reported_user: Mapped["User"] = relationship(
        "User", foreign_keys=[reported_user_id], back_populates="reports_received"
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
    parent_message_id: Mapped[str | None] = mapped_column(
        ForeignKey("messages.message_id"), nullable=True
    )
    status: Mapped[MessageStatusEnum] = mapped_column(default=MessageStatusEnum.unread)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # 動的に設定される属性（DBには保存されない）
    reply_count: int = 0
    thread_depth: int = 0
    thread_parent_id: str | None = None

    from_user: Mapped["User"] = relationship(
        "User", foreign_keys=[from_user_id], back_populates="messages_sent"
    )
    to_user: Mapped["User"] = relationship(
        "User", foreign_keys=[to_user_id], back_populates="messages_received"
    )
    reference_answer: Mapped["Answer"] = relationship(
        "Answer", foreign_keys=[reference_answer_id]
    )
    parent_message: Mapped["Message"] = relationship(
        "Message", foreign_keys=[parent_message_id], remote_side=[message_id]
    )
    replies: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys=[parent_message_id],
        cascade="all, delete-orphan",
        overlaps="parent_message",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reply_count = 0
        self.thread_depth = 0
        self.thread_parent_id = None


class MessageLike(Base):
    __tablename__ = "message_likes"

    like_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.message_id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    message: Mapped["Message"] = relationship("Message", foreign_keys=[message_id])
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="uq_message_user_like"),
        {"comment": "メッセージのいいね機能"},
    )


class AnswerLike(Base):
    __tablename__ = "answer_likes"

    like_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.answer_id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    answer: Mapped["Answer"] = relationship("Answer", foreign_keys=[answer_id])
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("answer_id", "user_id", name="uq_answer_user_like"),
        {"comment": "QA回答のいいね機能"},
    )
