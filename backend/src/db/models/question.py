from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class QuestionBase(BaseModel):
    text: str
    order: int
    template_id: str | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionRead(QuestionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
