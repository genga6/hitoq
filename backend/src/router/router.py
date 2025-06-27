from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.models.answer import AnswerCreate, AnswerRead
from src.db.models.question import QuestionRead
from src.db.models.template import TemplateRead
from src.db.models.user import UserCreate, UserRead
from src.db.session import get_db
from src.db.tables import Answer, Question, Template, User

router = APIRouter()


@router.get("/users", response_model=list[UserRead])
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("/users", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = User(**user_in.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/templates", response_model=list[TemplateRead])
def read_templates(db: Session = Depends(get_db)):
    return db.query(Template).all()


@router.get("/questions", response_model=list[QuestionRead])
def read_questions(template_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Question)
        .filter(Question.template_id == template_id)
        .order_by(Question.order)
        .all()
    )


@router.get("/answers", response_model=list[AnswerRead])
def read_answers(user_id: UUID | None = None, db: Session = Depends(get_db)):
    query = db.query(Answer)
    if user_id:
        query = query.filter(Answer.user_id == user_id)
    return query.all()


@router.post("/answers", response_model=AnswerRead)
def create_answer(answer_in: AnswerCreate, db: Session = Depends(get_db)):
    answer = Answer(**answer_in.model_dump())
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


@router.get("/api/resolve-users-id")
def resolve_users_id(user_name: str = Query(...), db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .filter(User.username == user_name)
        .order_by(User.created_at.desc())
        .all()
    )
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return [
        {
            "user_id": u.id,
            "username": u.username,
            "created_at": u.created_at.isoformat(),
            "icon_url": u.icon_url,
        }
        for u in users
    ]
