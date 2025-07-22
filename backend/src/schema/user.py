from datetime import datetime

from src.schema.common import OrmBaseModel


class UserBase(OrmBaseModel):
    user_name: str
    display_name: str
    bio: str | None = None
    icon_url: str | None = None


class UserCreate(UserBase):
    user_id: str


class UserUpdate(OrmBaseModel):
    user_name: str | None = None
    display_name: str | None = None
    bio: str | None = None
    icon_url: str | None = None


class UserRead(UserBase):
    user_id: str
    created_at: datetime
