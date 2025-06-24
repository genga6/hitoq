from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter

from src.db.models.answer import AnswerCreate, AnswerRead
from src.db.models.question import QuestionRead
from src.db.models.template import TemplateRead
from test.mock_data import ANSWERS, QUESTIONS, TEMPLATES

router = APIRouter()


@router.get("/templates", response_model=list[TemplateRead])
def get_templates():
    return TEMPLATES


@router.get("/questions", response_model=list[QuestionRead])
def get_questions(template_id: str):
    return sorted(
        [QuestionRead(**q) for q in QUESTIONS if q["template_id"] == template_id],
        key=lambda q: q.order,
    )


@router.post("/answers", response_model=AnswerRead)
def post_answer(answer: AnswerCreate):
    answer_data = answer.model_dump()
    answer_data["id"] = uuid4()
    answer_data["created_at"] = datetime.utcnow()

    ANSWERS.append(answer_data)
    return AnswerRead(**answer_data)
