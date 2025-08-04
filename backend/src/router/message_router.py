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


@message_router.get("/notifications", response_model=list[MessageRead])
def get_notifications(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Get notification messages based on user's notification level."""
    notifications = message_service.get_notifications_for_user(
        db, current_user.user_id, skip, limit
    )
    return notifications


@message_router.get("/notification-count")
def get_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Get count of unread notifications based on user's notification level."""
    count = message_service.get_notification_count(db, current_user.user_id)
    return {"notification_count": count}


@message_router.get("/{message_id}/thread", response_model=list[MessageRead])
def get_message_thread(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Get a message thread (original message + all replies)."""
    thread = message_service.get_message_thread(db, message_id, current_user.user_id)
    if not thread:
        raise HTTPException(
            status_code=404, detail="Message thread not found or no access"
        )
    return thread


@message_router.put("/{message_id}/content", response_model=MessageRead)
def update_message_content(
    message_id: str,
    content_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Update message content (only for the sender)."""
    message = message_service.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only the sender can edit the message
    if message.from_user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to edit this message"
        )

    updated_message = message_service.update_message_content(
        db, message_id, content_update.get("content", "")
    )
    return updated_message


@message_router.delete("/{message_id}")
def delete_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Delete a message (only for the sender)."""
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


@message_router.post("/{message_id}/heart")
def toggle_heart_reaction(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Toggle heart reaction for a message."""
    # Verify target message exists
    target_message = message_service.get_message(db, message_id)
    if not target_message:
        raise HTTPException(status_code=404, detail="Message not found")

    result = message_service.toggle_heart_reaction(
        db, current_user.user_id, message_id, target_message.from_user_id
    )

    return {
        "action": result["action"],
        "like_count": result["like_count"],
        "user_liked": result["action"] == "added",
    }


@message_router.get("/{message_id}/likes")
def get_message_likes(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Get list of users who liked a message."""
    # Verify target message exists
    target_message = message_service.get_message(db, message_id)
    if not target_message:
        raise HTTPException(status_code=404, detail="Message not found")

    likes = message_service.get_message_likes(db, message_id)
    return {"likes": likes}


@message_router.post("/heart-states")
def get_heart_states(
    message_ids: list[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """Get heart states for multiple messages."""
    heart_states = message_service.get_heart_states_for_messages(
        db, current_user.user_id, message_ids
    )
    return {"heart_states": heart_states}
