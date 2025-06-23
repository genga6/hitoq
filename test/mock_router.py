from fastapi import APIRouter

from src.db.model.schema import AnswerModel
from test.mock_data import ANSWERS, QUESTIONS, TEMPLATES

router = APIRouter()


@router.get("/templates")
def get_templates():
    return TEMPLATES


@router.get("/questions")
def get_questions(template_id: str):
    return sorted(
        [q for q in QUESTIONS if q["template_id"] == template_id],
        key=lambda q: q["order"],
    )


@router.post("/answers")
def post_answer(answer: AnswerModel):
    ANSWERS.append(answer.model_dump())
    return {"message": "回答OK", "answer": answer}
