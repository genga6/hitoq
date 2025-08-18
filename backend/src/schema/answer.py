from datetime import datetime

from src.schema.common import OrmBaseModel


class AnswerBase(OrmBaseModel):
    answer_text: str


class AnswerCreate(AnswerBase):
    pass


class AnswerUpdate(OrmBaseModel):
    answer_text: str | None = None


class AnswerRead(AnswerBase):
    answer_id: int
    user_id: str
    question_id: int
    created_at: datetime
