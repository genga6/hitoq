from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.answer import AnswerCreate, AnswerRead
from src.schema.question import QuestionRead
from src.service import qna_service

qna_router = APIRouter(
    prefix="/users/{user_id}",
    tags=["Q&A"],
)

questions_router = APIRouter(
    prefix="/users",
    tags=["Questions"],
)


@qna_router.post("/questions/{question_id}/answers", response_model=AnswerRead)
def create_new_answer(
    user_id: str,
    question_id: int,
    answer_in: AnswerCreate,
    db: Session = Depends(get_db),
):
    return qna_service.create_answer(
        db=db, user_id=user_id, question_id=question_id, answer_in=answer_in
    )


@questions_router.get("/questions", response_model=list[QuestionRead])
def read_all_questions(db: Session = Depends(get_db)):
    return qna_service.get_all_questions(db=db)
