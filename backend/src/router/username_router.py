from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.composite_schema import (
    MessagesPageData,
    ProfilePageData,
    QnAPageData,
)
from src.schema.user import Username
from src.service import message_service, qna_service, user_service
from src.service.categories import get_all_categories

username_router = APIRouter(
    prefix="/users/by-username/{user_name}",
    tags=["Page Data (by UserName)"],
)


@username_router.get("/profile", response_model=ProfilePageData)
def read_profile_page_data(user_name: Username, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_with_items = user_service.get_user_with_profile_items(db, user.user_id)
    if not user_with_items:
        raise HTTPException(status_code=404, detail="User not found")
    return {"profile": user_with_items, "profile_items": user_with_items.profile_items}


@username_router.get("/qna", response_model=QnAPageData)
def read_qna_page_data(user_name: Username, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_with_items = user_service.get_user_with_qna_items(db, user.user_id)
    if not user_with_items:
        raise HTTPException(status_code=404, detail="User not found")
    user_answer_groups = qna_service.get_user_qna(db, user.user_id)

    all_questions = qna_service.get_all_questions(db)
    questions_by_category = defaultdict(list)
    for question in all_questions:
        questions_by_category[question.category_id].append(question)

    # 新しいフラットカテゴリ構造でテンプレート情報を作成
    available_templates = []
    categories = get_all_categories()
    for category in categories:
        category_questions = questions_by_category.get(category.id, [])

        available_templates.append(
            {
                "id": category.id,
                "title": category.name,
                "questions": category_questions,
                "category": category.id,
            }
        )

    # カテゴリ情報を新しい構造で作成
    categories_info = {
        category.id: {
            "id": category.id,
            "label": category.name,
            "description": category.description,
        }
        for category in categories
    }

    return {
        "profile": user_with_items,
        "user_answer_groups": user_answer_groups,
        "available_templates": available_templates,
        "categories": categories_info,
    }


@username_router.get("/messages", response_model=MessagesPageData)
def read_messages_page_data(user_name: Username, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    messages = message_service.get_conversation_messages_for_user(db, user.user_id)

    return {
        "profile": user,
        "messages": messages,
    }
