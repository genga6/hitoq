import uuid
from datetime import datetime

from src.schema.common import OrmBaseModel


class BucketListItemBase(OrmBaseModel):
    content: str
    is_completed: bool = False
    display_order: int


class BucketListItemCreate(BucketListItemBase):
    pass


class BucketListItemUpdate(OrmBaseModel):
    content: str | None = None
    is_completed: bool | None = None
    display_order: int | None = None


class BucketListItemRead(BucketListItemBase):
    id: int
    user_id: uuid.UUID
    created_at: datetime
