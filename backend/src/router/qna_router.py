from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.answer import AnswerCreate, AnswerRead
from src.schema.composite_schema import QAWithDetails
from src.schema.question import QuestionRead
from src.service import qna_service

qna_router = APIRouter(
    prefix="/users/{user_id}",
    tags=["Q&A"],
)

questions_router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
)

answers_router = APIRouter(
    prefix="/answers",
    tags=["Answers"],
)


@qna_router.post("/questions/{question_id}/answers", response_model=AnswerRead)
def create_new_answer(
    user_id: str,
    question_id: int,
    answer_in: AnswerCreate,
    db: Session = Depends(get_db),
):
    try:
        return qna_service.create_answer(
            db=db, user_id=user_id, question_id=question_id, answer_in=answer_in
        )
    except ValueError as e:
        if "User not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e)) from e
        if "Question not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e)) from e
        raise HTTPException(status_code=400, detail=str(e)) from e


@questions_router.get("/", response_model=list[QuestionRead])
def read_all_questions(db: Session = Depends(get_db)):
    return qna_service.get_all_questions(db=db)


@questions_router.get("/by-category/{category_id}", response_model=list[QuestionRead])
def read_questions_by_category(category_id: str, db: Session = Depends(get_db)):
    """指定されたカテゴリの質問を取得（ガチャ機能用）"""
    return qna_service.get_questions_by_category(db=db, category_id=category_id)


@questions_router.get("/categories", response_model=list[dict])
def read_categories():
    """利用可能なカテゴリ一覧を取得（ガチャ機能用）"""
    from src.service.categories import get_all_categories

    categories = get_all_categories()
    return [
        {
            "id": category.id,
            "name": category.name,
            "description": category.description,
        }
        for category in categories
    ]


@answers_router.get("/{answer_id}/with-question", response_model=QAWithDetails)
def read_answer_with_question(answer_id: int, db: Session = Depends(get_db)):
    """指定されたanswer_idの回答とその質問を取得（トークのリファレンス表示用）"""
    return qna_service.get_answer_with_question(db=db, answer_id=answer_id)
