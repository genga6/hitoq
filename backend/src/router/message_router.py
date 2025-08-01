from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.tables import User
from src.router.auth import _get_current_user
from src.schema.message import MessageCreate, MessageRead, MessageUpdate
from src.service import message_service, user_service

message_router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


@message_router.post("/", response_model=MessageRead)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Create a new message."""
    # Verify target user exists
    target_user = user_service.get_user(db, message.to_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    db_message = message_service.create_message(db, message, current_user.user_id)
    return db_message


@message_router.get("/", response_model=list[MessageRead])
def get_my_messages(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Get messages received by the current user."""
    messages = message_service.get_messages_for_user(
        db, current_user.user_id, skip, limit
    )
    return messages


@message_router.patch("/{message_id}", response_model=MessageRead)
def update_message(
    message_id: str,
    message_update: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Update message status (mark as read, etc.)."""
    message = message_service.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only the recipient can update the message status
    if message.to_user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this message"
        )

    updated_message = message_service.update_message_status(
        db, message_id, message_update
    )
    return updated_message


@message_router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Get count of unread messages."""
    count = message_service.get_unread_count(db, current_user.user_id)
    return {"unread_count": count}
