from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.profile_item import (
    ProfileItemRead,
    ProfileItemUpdate,
)
from src.service import profile_service

profile_router = APIRouter(
    prefix="/users/{user_id}",
    tags=["Profile Items"],
)


@profile_router.put("/profile-items/{item_id}", response_model=ProfileItemRead)
def update_profile_item_endpoint(
    user_id: str,
    item_id: str,
    item_in: ProfileItemUpdate,
    db: Session = Depends(get_db),
):
    return profile_service.update_profile_item(
        db=db, user_id=user_id, item_id=item_id, item_in=item_in
    )
