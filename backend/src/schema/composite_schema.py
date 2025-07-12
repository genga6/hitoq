from src.schema.answer import AnswerBase
from src.schema.bucket_list_item import BucketListItemRead
from src.schema.common import OrmBaseModel
from src.schema.profile_item import ProfileItemRead
from src.schema.question import QuestionRead
from src.schema.user import UserRead


class ProfilePageData(UserRead):
    profile_items: list[ProfileItemRead] = []


class BucketListPageData(UserRead):
    bucket_list_items: list[BucketListItemRead] = []


class AnsweredQARead(AnswerBase):
    question: QuestionRead


class UserAnswerGroupRead(OrmBaseModel):
    template_id: str
    template_title: str
    answers: list[AnsweredQARead]


class AvailableQATemplateRead(OrmBaseModel):
    id: str
    title: str
    questions: list[QuestionRead]


class QnAPageData(UserRead):
    user_answer_groups: list[UserAnswerGroupRead]
    available_templates: list[AvailableQATemplateRead]
