from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.composite_schema import CategoryInfoRead
from src.schema.message import MessageRead
from src.schema.profile_item import ProfileItemRead
from src.schema.user import Username, UserRead
from src.service import message_service, qna_service, user_service
from src.service.categories import get_all_categories

by_username_router = APIRouter(
    prefix="/by-username",
    tags=["By Username User Resources"],
)


@by_username_router.get("/{user_name}", response_model=UserRead)
def read_user_by_username(user_name: Username, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@by_username_router.get("/{user_name}/messages", response_model=list[MessageRead])
def read_messages_by_username(
    user_name: Username,
    db: Session = Depends(get_db),
):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    messages = message_service.get_messages_for_user(db, user.user_id)
    return messages


@by_username_router.get("/{user_name}/qna")
def read_qna_by_username(
    user_name: Username,
    db: Session = Depends(get_db),
):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_answer_groups = qna_service.get_user_qna(db, user.user_id)

    # CategoryInfoをCategoryInfoReadスキーマに変換
    category_list = get_all_categories()
    categories = {}
    for cat in category_list:
        categories[cat.id] = CategoryInfoRead(
            id=cat.id, label=cat.name, description=cat.description
        )

    return {
        "userAnswerGroups": user_answer_groups,
        "categories": categories,
    }


@by_username_router.get(
    "/{user_name}/profile-items", response_model=list[ProfileItemRead]
)
def read_profile_items_by_username(
    user_name: Username,
    db: Session = Depends(get_db),
):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_with_items = user_service.get_user_with_profile_items(db, user.user_id)
    if not user_with_items:
        raise HTTPException(status_code=404, detail="User not found")

    return user_with_items.profile_items
