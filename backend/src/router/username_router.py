from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.composite_schema import (
    ProfilePageData,
    QnAPageData,
)
from src.service import qna_service, user_service
from src.service.question_templates import (
    get_all_category_info,
    get_default_templates,
)

username_router = APIRouter(
    prefix="/users/by-username/{user_name}",
    tags=["Page Data (by UserName)"],
)


@username_router.get("/profile", response_model=ProfilePageData)
def read_profile_page_data(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_with_items = user_service.get_user_with_profile_items(db, user.user_id)
    if not user_with_items:
        raise HTTPException(status_code=404, detail="User not found")
    return {"profile": user_with_items, "profile_items": user_with_items.profile_items}


@username_router.get("/qna", response_model=QnAPageData)
def read_qna_page_data(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_with_items = user_service.get_user_with_qna_items(db, user.user_id)
    if not user_with_items:
        raise HTTPException(status_code=404, detail="User not found")
    user_answer_groups = qna_service.get_user_qna(db, user.user_id)

    all_questions = qna_service.get_all_questions(db)
    questions_by_template = defaultdict(list)
    for question in all_questions:
        questions_by_template[question.template_id].append(question)

    available_templates = []
    for template in get_default_templates():
        template_id = (
            template.title.replace(" ", "-")
            .replace("の", "")
            .replace("質問", "")
            .lower()
        )
        template_questions = questions_by_template.get(template_id, [])

        available_templates.append(
            {
                "id": template_id,
                "title": template.title,
                "questions": template_questions,
                "category": template.category.value,
            }
        )

    categories_raw = get_all_category_info()
    categories_info = {
        key: {"id": info.id, "label": info.label, "description": info.description}
        for key, info in categories_raw.items()
    }

    return {
        "profile": user_with_items,
        "user_answer_groups": user_answer_groups,
        "available_templates": available_templates,
        "categories": categories_info,
    }
