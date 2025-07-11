import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.tables import Answer, Question
from src.schema.answer import AnswerCreate, AnswerRead
from src.schema.question import QuestionRead

router = APIRouter(tags=["Q&A"])


@router.get("/questions", response_model=list[QuestionRead])
def read_all_questions(db: Session = Depends(get_db)):
    return db.query(Question).order_by(Question.display_order).all()


@router.post(
    "/users/{user_id}/questions/{question_id}/answers", response_model=AnswerRead
)
def create_new_answer(
    user_id: uuid.UUID,
    question_id: int,
    answer_in: AnswerCreate,
    db: Session = Depends(get_db),
):
    db_answer = Answer(
        user_id=user_id, question_id=question_id, **answer_in.model_dump()
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer
