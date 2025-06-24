from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter

from src.db.models.answer import AnswerCreate, AnswerRead
from src.db.models.question import QuestionRead
from src.db.models.template import TemplateRead
from src.db.models.user import UserCreate, UserRead
from test.mock_data import ANSWERS, QUESTIONS, TEMPLATES, USERS

router = APIRouter()


@router.get("/users", response_model=list[UserRead])
def read_users():
    return [UserRead(**u) for u in USERS]


@router.post("/users", response_model=UserRead)
def create_user(user_in: UserCreate):
    user_data = user_in.model_dump()
    user_data["id"] = uuid4()
    user_data["created_at"] = datetime.now(timezone.utc)

    USERS.append(user_data)
    return UserRead(**user_data)


@router.get("/templates", response_model=list[TemplateRead])
def read_templates():
    return TEMPLATES


@router.get("/questions", response_model=list[QuestionRead])
def read_questions(template_id: str):
    return sorted(
        [QuestionRead(**q) for q in QUESTIONS if q["template_id"] == template_id],
        key=lambda q: q.order,
    )


@router.get("/answers", response_model=list[AnswerRead])
def read_answers(user_id: UUID | None = None):
    results = ANSWERS
    if user_id:
        results = [a for a in ANSWERS if a["user_id"] == user_id]
    return [AnswerRead(**a) for a in results]


@router.post("/answers", response_model=AnswerRead)
def create_answer(answer: AnswerCreate):
    answer_data = answer.model_dump()
    answer_data["id"] = uuid4()
    answer_data["created_at"] = datetime.now(timezone.utc)

    ANSWERS.append(answer_data)
    return AnswerRead(**answer_data)
