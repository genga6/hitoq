from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.tables import User
from src.router.auth import _get_current_user, get_current_user_optional
from src.schema.user import UserCreate, Username, UserRead, UserUpdate
from src.service import user_service

user_router = APIRouter(
    prefix="/users",
    tags=["Global User Resources"],
)


@user_router.post("", response_model=UserRead, status_code=201)
def upsert_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_service.upsert_user(db=db, user_in=user_in)


@user_router.get("", response_model=list[UserRead])
def read_all_users_endpoint(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(100, ge=1, le=100, description="Limit"),
    db: Session = Depends(get_db),
):
    return user_service.get_users(db, skip=skip, limit=limit)


@user_router.get("/discover", response_model=list[UserRead])
def discover_users_endpoint(
    type: Literal["activity", "random", "recommend"] = Query(
        "recommend", description="Discovery type"
    ),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    - activity: アクティブなユーザー（新規登録、最近の回答・メッセージ・ログイン）
    - random: ランダムなユーザー
    - recommend: アクティブ + ランダムの混合（デフォルト）
    """
    current_user_id = current_user.user_id if current_user else None
    users = user_service.discover_users(
        db=db,
        discovery_type=type,
        limit=limit,
        offset=offset,
        current_user_id=current_user_id,
    )
    return users


@user_router.get("/{user_id}", response_model=UserRead)
def read_user_by_id_endpoint(user_id: str, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.get("/by-username/{user_name}", response_model=UserRead)
def read_user_by_username_endpoint(user_name: Username, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.get("/resolve-users-id", response_model=UserRead)
def resolve_user_by_username(user_name: Username, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.get("/search/users", response_model=list[UserRead])
def search_users_by_display_name(
    q: str = Query(..., min_length=1, description="Search query for display name"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    users = user_service.search_users_by_display_name(db, display_name=q, limit=limit)
    return users


@user_router.patch("/me", response_model=UserRead)
def update_current_user_endpoint(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    updated_user = user_service.update_user(db, current_user.user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@user_router.delete("/{user_id}", status_code=204)
def delete_user_endpoint(user_id: str, db: Session = Depends(get_db)):
    success = user_service.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
