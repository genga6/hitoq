from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.models.answer import AnswerCreate, AnswerRead
from src.db.models.question import QuestionRead
from src.db.models.template import TemplateRead
from src.db.models.user import UserRead
from src.db.session import get_db
from src.db.tables import Answer, Question, Template, User

router = APIRouter()


@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/templates", response_model=list[TemplateRead])
def list_templates(db: Session = Depends(get_db)):
    return db.query(Template).all()


@router.get("/questions", response_model=list[QuestionRead])
def list_questions(template_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Question)
        .filter(Question.template_id == template_id)
        .order_by(Question.order)
        .all()
    )


@router.post("/answers", response_model=AnswerRead)
def submit_answer(answer_in: AnswerCreate, db: Session = Depends(get_db)):
    answer = Answer(**answer_in.model_dump())
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer
