from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.tables import User
from src.router.auth import _get_current_user
from src.schema.message import (
    HeartReactionResponse,
    HeartStatesResponse,
    MessageCreate,
    MessageRead,
    MessageUpdate,
)
from src.service import message_service, user_service

message_router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


@message_router.post("", response_model=MessageRead)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    target_user = user_service.get_user(db, message.to_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    db_message = message_service.create_message(db, message, current_user.user_id)
    return db_message


@message_router.get("", response_model=list[MessageRead])
def get_my_messages(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(50, ge=1, le=100, description="Limit"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    messages = message_service.get_messages_with_replies(
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
    message = message_service.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.to_user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this message"
        )

    updated_message = message_service.update_message_status(
        db, message_id, message_update
    )
    return updated_message


@message_router.get("/{message_id}/thread", response_model=list[MessageRead])
def get_message_thread(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    thread = message_service.get_message_thread(db, message_id, current_user.user_id)
    if not thread:
        raise HTTPException(
            status_code=404, detail="Message thread not found or no access"
        )
    return thread


@message_router.delete("/{message_id}")
def delete_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    message = message_service.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only the sender can delete the message
    if message.from_user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this message"
        )

    success = message_service.delete_message(db, message_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete message")

    return {"message": "Message deleted successfully"}


@message_router.post("/{message_id}/heart", response_model=HeartReactionResponse)
def toggle_heart_reaction(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    target_message = message_service.get_message(db, message_id)
    if not target_message:
        raise HTTPException(status_code=404, detail="Message not found")

    result = message_service.toggle_heart_reaction(db, current_user.user_id, message_id)

    return result


@message_router.post("/heart-states", response_model=HeartStatesResponse)
def get_heart_states(
    message_ids: list[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    heart_states = message_service.get_heart_states_for_messages(
        db, current_user.user_id, message_ids
    )
    return {"heart_states": heart_states}
