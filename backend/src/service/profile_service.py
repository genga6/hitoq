from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.db.tables import ProfileItem
from src.schema.profile_item import ProfileItemCreate, ProfileItemUpdate


def _get_profile_item(db: Session, user_id: str, item_id: int) -> ProfileItem:
    item = (
        db.query(ProfileItem)
        .filter(ProfileItem.id == item_id, ProfileItem.user_id == user_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Profile item not found")
    return item


def create_profile_item(
    db: Session, user_id: str, item_in: ProfileItemCreate
) -> ProfileItem:
    db_item = ProfileItem(user_id=user_id, **item_in.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_profile_item(
    db: Session, user_id: str, item_id: int, item_in: ProfileItemUpdate
) -> ProfileItem:
    db_item = _get_profile_item(db, user_id, item_id)
    update_data = item_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_profile_item(db: Session, user_id: str, item_id: int):
    db_item = _get_profile_item(db, user_id, item_id)
    db.delete(db_item)
    db.commit()
    return {"ok": True}
