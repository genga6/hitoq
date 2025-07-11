import uuid
from datetime import datetime

from src.schema.common import OrmBaseModel


class AnswerBase(OrmBaseModel):
    answer_text: str


class AnswerCreate(AnswerBase):
    pass


class AnswerUpdate(OrmBaseModel):
    answer_text: str | None = None


class AnswerRead(AnswerBase):
    id: int
    user_id: uuid.UUID
    question_id: int
    created_at: datetime
