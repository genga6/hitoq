from datetime import datetime

from src.db.tables import MessageStatusEnum, MessageTypeEnum
from src.schema.common import OrmBaseModel
from src.schema.user import UserRead


class MessageBase(OrmBaseModel):
    message_type: MessageTypeEnum
    content: str
    reference_answer_id: int | None = None


class MessageCreate(MessageBase):
    to_user_id: str


class MessageUpdate(OrmBaseModel):
    status: MessageStatusEnum


class MessageRead(MessageBase):
    message_id: str
    from_user_id: str
    to_user_id: str
    status: MessageStatusEnum
    created_at: datetime
    from_user: UserRead | None = None
    to_user: UserRead | None = None
