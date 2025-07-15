from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.answer import AnswerCreate, AnswerRead
from src.schema.bucket_list_item import (
    BucketListItemCreate,
    BucketListItemRead,
    BucketListItemUpdate,
)
from src.schema.composite_schema import (
    BucketListPageData,
    ProfilePageData,
    QnAPageData,
)
from src.schema.profile_item import (
    ProfileItemCreate,
    ProfileItemRead,
    ProfileItemUpdate,
)
from src.schema.question import QuestionRead
from src.schema.user import UserCreate, UserRead
from src.service import (
    bucket_list_item_service,
    profile_service,
    qna_service,
    user_service,
)

resource_router = APIRouter(
    prefix="/users/{user_id}",
    tags=["Resources (by UserID)"],
)

username_router = APIRouter(
    prefix="/users/by-username/{user_name}",
    tags=["Page Data (by UserName)"],
)

global_router = APIRouter(
    prefix="/users",
    tags=["Global User Resources"],
)


@username_router.get("/profile", response_model=ProfilePageData)
def read_profile_page_data(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"profile_items": user.profile_items}


@username_router.get("/bucket-list", response_model=BucketListPageData)
def read_bucket_list_page_data(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"bucket_list_items": user.bucket_list_items}


@username_router.get("/qna", response_model=QnAPageData)
def read_qna_page_data(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_answer_groups = qna_service.get_user_qna(db, user.user_id)
    all_questions_grouped = qna_service.get_all_questions_grouped(db)
    available_templates = []
    for category, questions in all_questions_grouped.items():
        if not any(group.template_id == category.name for group in user_answer_groups):
            available_templates.append(
                {
                    "id": category.name,
                    "title": qna_service.get_category_title(category),
                    "questions": questions,
                }
            )
    return {
        "user_answer_groups": user_answer_groups,
        "available_templates": available_templates,
    }


@resource_router.post(
    "/profile-items",
    response_model=ProfileItemRead,
    status_code=201,
)
def create_profile_item_endpoint(
    user_id: str, item_in: ProfileItemCreate, db: Session = Depends(get_db)
):
    return profile_service.create_profile_item(db=db, user_id=user_id, item_in=item_in)


@resource_router.put("profile-items/{item_id}", response_model=ProfileItemRead)
def update_profile_item_endpoint(
    user_id: str,
    item_id: int,
    item_in: ProfileItemUpdate,
    db: Session = Depends(get_db),
):
    return profile_service.update_profile_item(
        db=db, user_id=user_id, item_id=item_id, item_in=item_in
    )


@resource_router.delete("/profile-items/{item_id}", status_code=204)
def delete_profile_item_endpoint(
    user_id: str, item_id: int, db: Session = Depends(get_db)
):
    profile_service.delete_profile_item(db=db, user_id=user_id, item_id=item_id)
    return None


@resource_router.post(
    "/bucket-list-items",
    response_model=BucketListItemRead,
    status_code=201,
)
def create_bucket_list_item_endpoint(
    user_id: str, item_in: BucketListItemCreate, db: Session = Depends(get_db)
):
    return bucket_list_item_service.create_bucket_list_item(
        db=db, user_id=user_id, item_in=item_in
    )


@resource_router.put("/bucket-list-items/{item_id}", response_model=BucketListItemRead)
def update_bucket_list_item_endpoint(
    user_id: str,
    item_id: int,
    item_in: BucketListItemUpdate,
    db: Session = Depends(get_db),
):
    return bucket_list_item_service.update_bucket_list_item(
        db=db, user_id=user_id, item_id=item_id, item_in=item_in
    )


@resource_router.delete("/bucket-list-items/{item_id}", status_code=204)
def delete_bucket_list_item_endpoint(
    user_id: str, item_id: int, db: Session = Depends(get_db)
):
    bucket_list_item_service.delete_bucket_list_item(
        db=db, user_id=user_id, item_id=item_id
    )
    return None


@resource_router.post("/questions/{question_id}/answers", response_model=AnswerRead)
def create_new_answer(
    user_id: str,
    question_id: int,
    answer_in: AnswerCreate,
    db: Session = Depends(get_db),
):
    return qna_service.create_answer(
        db=db, user_id=user_id, question_id=question_id, answer_in=answer_in
    )


@global_router.post("", response_model=UserRead, status_code=201)
def upsert_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_service.upsert_user(db=db, user_in=user_in)


@global_router.get("", response_model=list[UserRead])
def read_all_users_endpoint(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return user_service.get_users(db, skip=skip, limit=limit)


@global_router.get("/{user_id}", response_model=UserRead)
def read_user_by_id_endpoint(user_id: str, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@global_router.get("/by-username/{user_name}", response_model=UserRead)
def read_user_by_username_endpoint(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@global_router.get("/resolve-users-id", response_model=list[UserRead])
def resolve_user_by_username(
    user_name: str = Query(..., min_length=1), db: Session = Depends(get_db)
):
    print(f"Received user_name: {user_name}")
    return user_service.get_user_by_username(db, user_name=user_name)


@global_router.get("/questions", response_model=list[QuestionRead])
def read_all_questions(db: Session = Depends(get_db)):
    return qna_service.get_all_questions(db=db)
