from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.model.tables import Answer, Question, Template, User
from src.db.session import get_db

router = APIRouter()


@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/templates")
def list_templates(db: Session = Depends(get_db)):
    return db.query(Template).all()


@router.get("/questions")
def list_questions(template_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Question)
        .filter(Question.template_id == template_id)
        .order_by(Question.order)
        .all()
    )


@router.post("/answers")
def submit_answer(answer: Answer, db: Session = Depends(get_db)):
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer
