from src.schema.common import OrmBaseModel
from src.schema.message import MessageRead
from src.schema.profile_item import ProfileItemRead
from src.schema.question import QuestionRead
from src.schema.user import UserRead


class ProfilePageData(OrmBaseModel):
    profile: UserRead
    profile_items: list[ProfileItemRead] = []


class AnsweredQARead(OrmBaseModel):
    answer_id: int
    answer_text: str
    question: QuestionRead


class UserAnswerGroupRead(OrmBaseModel):
    template_id: str
    template_title: str
    answers: list[AnsweredQARead]


class CategoryInfoRead(OrmBaseModel):
    id: str
    label: str
    description: str


class AvailableQATemplateRead(OrmBaseModel):
    id: str
    title: str
    questions: list[QuestionRead]
    category: str


class QnAPageData(OrmBaseModel):
    profile: UserRead
    user_answer_groups: list[UserAnswerGroupRead]
    available_templates: list[AvailableQATemplateRead]
    categories: dict[str, CategoryInfoRead]


class MessagesPageData(OrmBaseModel):
    profile: UserRead
    messages: list[MessageRead]
