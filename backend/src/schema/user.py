import uuid
from datetime import datetime

from src.schema.common import OrmBaseModel


class UserBase(OrmBaseModel):
    user_name: str
    bio: str | None = None
    icon_url: str | None = None


class UserCreate(UserBase):
    id: uuid.UUID


class UserUpdate(OrmBaseModel):
    user_name: str | None = None
    bio: str | None = None
    icon_url: str | None = None


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
