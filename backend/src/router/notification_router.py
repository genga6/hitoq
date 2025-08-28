from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.tables import User
from src.router.auth import _get_current_user
from src.schema.message import NotificationRead
from src.service import notification_service

notification_router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@notification_router.get("", response_model=list[NotificationRead])
def get_notifications(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(50, ge=1, le=100, description="Limit"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    notifications = notification_service.get_notifications_for_user(
        db, current_user.user_id, skip, limit
    )
    return notifications


@notification_router.patch("/mark-all-read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    updated_count = notification_service.mark_all_notifications_as_read(
        db, current_user.user_id
    )
    return {"updated_count": updated_count}
