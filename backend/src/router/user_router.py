from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.tables import User
from src.router.auth import get_current_user, get_current_user_optional
from src.schema.user import UserCreate, UserRead, UserUpdate
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
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return user_service.get_users(db, skip=skip, limit=limit)


# 特定のパスを先に配置（動的パスより前）
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
    新しいユーザーを発見する

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


@user_router.get("/me", response_model=UserRead)
def read_current_user_endpoint(current_user: User = Depends(get_current_user)):
    return current_user


@user_router.patch("/me", response_model=UserRead)
def update_current_user_endpoint(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user information including notification settings."""
    updated_user = user_service.update_user(db, current_user.user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@user_router.delete("/me", status_code=204)
def delete_current_user_endpoint(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    success = user_service.delete_user(db=db, user_id=current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None


@user_router.get("/{user_id}", response_model=UserRead)
def read_user_by_id_endpoint(user_id: str, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.get("/by-username/{user_name}", response_model=UserRead)
def read_user_by_username_endpoint(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.get("/resolve-users-id", response_model=UserRead)
def resolve_user_by_username(
    user_name: str = Query(..., min_length=1), db: Session = Depends(get_db)
):
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
    """Search users by display name with partial matching."""
    users = user_service.search_users_by_display_name(db, display_name=q, limit=limit)
    return users
