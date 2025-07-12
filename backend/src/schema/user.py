from datetime import datetime

from src.schema.common import OrmBaseModel


class UserBase(OrmBaseModel):
    user_name: str
    bio: str | None = None
    icon_url: str | None = None


class UserCreate(UserBase):
    id: str


class UserUpdate(OrmBaseModel):
    user_name: str | None = None
    bio: str | None = None
    icon_url: str | None = None


class UserRead(UserBase):
    id: str
    created_at: datetime
