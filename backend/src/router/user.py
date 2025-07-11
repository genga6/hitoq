import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.bucket_list_item import (
    BucketListItemCreate,
    BucketListItemRead,
    BucketListItemUpdate,
)
from src.schema.composite_schema import UserReadWithDetails
from src.schema.profile_item import (
    ProfileItemCreate,
    ProfileItemRead,
    ProfileItemUpdate,
)
from src.schema.user import UserCreate, UserRead
from src.service import bucket_list_item_service, profile_service, user_service

router = APIRouter(
    prefix="/users",
    tags=["Users & Profile"],
)


@router.post("/", response_model=UserRead, status_code=201)
def create_new_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db=db, user_in=user_in)


@router.get("/", response_model=list[UserRead])
def read_all_user(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_service.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def read_user_by_id(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id=user_id)


@router.get("/{user_id}/details", response_model=UserReadWithDetails)
def read_user_with_all_details(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id=user_id)


@router.post(
    "/{user_id}/profile-items",
    response_model=ProfileItemRead,
    status_code=201,
    tags=["Profile Items"],
)
def create_user_profile_item(
    user_id: uuid.UUID, item_in: ProfileItemCreate, db: Session = Depends(get_db)
):
    # TODO: 認証チェック - ログインユーザーがuser_idと一致するか
    return profile_service.create_profile_item(db=db, user_id=user_id, item_in=item_in)


@router.put(
    "/profile-items/{item_id}", response_model=ProfileItemRead, tags=["Profile Items"]
)
def update_user_profile_item(
    item_id: int, item_in: ProfileItemUpdate, db: Session = Depends(get_db)
):
    # TODO: 認証チェック - ログインユーザーがこのアイテムの所有者か
    return profile_service.update_profile_item(db=db, item_id=item_id, item_in=item_in)


@router.delete("/profile-items/{item_id}", status_code=204, tags=["Profile Items"])
def delete_user_profile_item(item_id: int, db: Session = Depends(get_db)):
    # TODO: 認証チェック - ログインユーザーがこのアイテムの所有者か
    profile_service.delete_profile_item(db=db, item_id=item_id)
    return None


@router.post(
    "/{user_id}/bucket-list-items",
    response_model=BucketListItemRead,
    status_code=201,
    tags=["Bucket List Items"],
)
def create_user_bucket_list_item(
    user_id: uuid.UUID, item_in: BucketListItemCreate, db: Session = Depends(get_db)
):
    # TODO: 認証チェック
    return bucket_list_item_service.create_bucket_list_item(
        db=db, user_id=user_id, item_in=item_in
    )


@router.put(
    "/bucket-list-items/{item_id}",
    response_model=BucketListItemRead,
    tags=["Bucket List Items"],
)
def update_user_bucket_list_item(
    item_id: int, item_in: BucketListItemUpdate, db: Session = Depends(get_db)
):
    # TODO: 認証チェック
    return bucket_list_item_service.update_bucket_list_item(
        db=db, item_id=item_id, item_in=item_in
    )


@router.delete(
    "/bucket-list-items/{item_id}",
    status_code=204,
    tags=["Bucket List Items"],
)
def delete_user_bucket_list_item(item_id: int, db: Session = Depends(get_db)):
    # TODO: 認証チェック
    bucket_list_item_service.delete_bucket_list_item(db=db, item_id=item_id)
    return None
