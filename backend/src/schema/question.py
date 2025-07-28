from datetime import datetime

from src.db.tables import QuestionCategoryEnum
from src.schema.common import OrmBaseModel


class QuestionBase(OrmBaseModel):
    category: QuestionCategoryEnum
    text: str
    display_order: int
    template_id: str


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(OrmBaseModel):
    category: QuestionCategoryEnum | None = None
    text: str | None = None
    display_order: int | None = None


class QuestionRead(QuestionBase):
    question_id: int
    created_at: datetime
