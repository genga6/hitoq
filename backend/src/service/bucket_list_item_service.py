import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.db.tables import BucketListItem
from src.schema.bucket_list_item import BucketListItemCreate, BucketListItemUpdate


def create_bucket_list_item(
    db: Session, user_id: uuid.UUID, item_in: BucketListItemCreate
) -> BucketListItem:
    db_item = BucketListItem(user_id=user_id, **item_in.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_bucket_list_item(db: Session, item_id: int) -> BucketListItem:
    item = db.query(BucketListItem).filter(BucketListItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bucket list item not found")
    return item


def update_bucket_list_item(
    db: Session, item_id: int, item_in: BucketListItemUpdate
) -> BucketListItem:
    db_item = get_bucket_list_item(db, item_id)
    update_data = item_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_bucket_list_item(db: Session, item_id: int):
    db_item = get_bucket_list_item(db, item_id)
    db.delete(db_item)
    db.commit()
    return {"ok": True}
