from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AnswerBase(BaseModel):
    text: str
    user_id: UUID
    question_id: UUID


class AnswerCreate(AnswerBase):
    pass


class AnswerRead(AnswerBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
