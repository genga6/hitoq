import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.db.tables import ProfileItem
from src.schema.profile_item import ProfileItemCreate, ProfileItemUpdate


def _get_profile_item(
    db: Session, user_id: str, item_id: str | uuid.UUID
) -> ProfileItem:
    if isinstance(item_id, str):
        try:
            item_id = uuid.UUID(item_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail="Profile item not found") from e

    item = (
        db.query(ProfileItem)
        .filter(ProfileItem.profile_item_id == item_id, ProfileItem.user_id == user_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Profile item not found")
    return item


def create_profile_item(
    db: Session, user_id: str, item_in: ProfileItemCreate
) -> ProfileItem:
    db_item = ProfileItem(
        profile_item_id=uuid.uuid4(), user_id=user_id, **item_in.model_dump()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_profile_item(
    db: Session, user_id: str, item_id: str, item_in: ProfileItemUpdate
) -> ProfileItem:
    db_item = _get_profile_item(db, user_id, item_id)
    update_data = item_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_profile_item(db: Session, user_id: str, item_id: str):
    db_item = _get_profile_item(db, user_id, item_id)
    db.delete(db_item)
    db.commit()
    return {"ok": True}
