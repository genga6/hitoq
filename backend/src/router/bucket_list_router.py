from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.bucket_list_item import (
    BucketListItemCreate,
    BucketListItemRead,
    BucketListItemUpdate,
)
from src.service import bucket_list_item_service

bucket_list_router = APIRouter(
    prefix="/users/{user_id}",
    tags=["Bucket List Items"],
)


@bucket_list_router.post(
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


@bucket_list_router.put(
    "/bucket-list-items/{item_id}", response_model=BucketListItemRead
)
def update_bucket_list_item_endpoint(
    user_id: str,
    item_id: int,
    item_in: BucketListItemUpdate,
    db: Session = Depends(get_db),
):
    return bucket_list_item_service.update_bucket_list_item(
        db=db, user_id=user_id, item_id=item_id, item_in=item_in
    )


@bucket_list_router.delete("/bucket-list-items/{item_id}", status_code=204)
def delete_bucket_list_item_endpoint(
    user_id: str, item_id: int, db: Session = Depends(get_db)
):
    bucket_list_item_service.delete_bucket_list_item(
        db=db, user_id=user_id, item_id=item_id
    )
    return None
