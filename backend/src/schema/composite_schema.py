from datetime import datetime

from src.schema.answer import AnswerBase
from src.schema.bucket_list_item import BucketListItemBase
from src.schema.profile_item import ProfileItemBase
from src.schema.question import QuestionRead
from src.schema.user import UserRead


class ProfileItemReadForUser(ProfileItemBase):
    id: int


class BucketListItemReadForUser(BucketListItemBase):
    id: int
    created_at: datetime


class AnswerReadForUser(AnswerBase):
    id: int
    created_at: datetime
    question: QuestionRead


class UserReadWithDetails(UserRead):
    profile_items: list[ProfileItemReadForUser] = []
    bucket_list_items: list[BucketListItemReadForUser] = []
    answers: list[AnswerReadForUser] = []
