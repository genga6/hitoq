from datetime import datetime

from src.schema.common import OrmBaseModel


class QuestionBase(OrmBaseModel):
    category_id: str
    text: str
    display_order: int


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(OrmBaseModel):
    category_id: str | None = None
    text: str | None = None
    display_order: int | None = None


class QuestionRead(QuestionBase):
    question_id: int
    created_at: datetime
