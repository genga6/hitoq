from datetime import datetime

from pydantic import Field

from src.db.tables import MessageStatusEnum, MessageTypeEnum
from src.schema.common import OrmBaseModel
from src.schema.user import UserRead


class MessageBase(OrmBaseModel):
    message_type: MessageTypeEnum
    content: str = Field(..., max_length=1000, description="Message content")
    reference_answer_id: int | None = None
    parent_message_id: str | None = None


class MessageCreate(MessageBase):
    to_user_id: str


class MessageUpdate(OrmBaseModel):
    status: MessageStatusEnum


class ParentMessageInfo(OrmBaseModel):
    """親メッセージの基本情報（循環参照を避けるため）"""

    message_id: str
    content: str
    from_user: UserRead | None = None
    created_at: datetime


class ReplyInfo(OrmBaseModel):
    """リプライの基本情報（循環参照を避けるため）"""

    message_id: str
    content: str
    from_user: UserRead | None = None
    created_at: datetime
    status: MessageStatusEnum
    reply_count: int = 0


class MessageRead(MessageBase):
    message_id: str
    from_user_id: str
    to_user_id: str
    status: MessageStatusEnum
    created_at: datetime
    from_user: UserRead | None = None
    to_user: UserRead | None = None
    replies: list[ReplyInfo] = []
    reply_count: int = 0
    parent_message: ParentMessageInfo | None = None  # 親メッセージの基本情報のみ


class NotificationRead(MessageBase):
    message_id: str
    from_user_id: str
    to_user_id: str
    status: MessageStatusEnum
    created_at: datetime
    from_user: UserRead | None = None
    to_user: UserRead | None = None
    parent_message: ParentMessageInfo | None = None  # 親メッセージの基本情報のみ


class HeartReactionResponse(OrmBaseModel):
    user_liked: bool
    like_count: int


class HeartStatesResponse(OrmBaseModel):
    heart_states: dict[str, HeartReactionResponse]
