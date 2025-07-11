from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schema.user import UserRead
from src.service import user_service

router = APIRouter(
    tags=["Utilities"],
)


@router.get("/resolve-users-id", response_model=list[UserRead])
def resolve_user_by_username(
    user_name: str = Query(..., min_length=1), db: Session = Depends(get_db)
):
    return user_service.get_user_by_username(db, user_name=user_name)
