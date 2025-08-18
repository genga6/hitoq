from datetime import datetime

from pydantic import Field

from src.db.tables import NotificationLevelEnum
from src.schema.common import OrmBaseModel


class UserBase(OrmBaseModel):
    user_name: str = Field(..., min_length=1, description="Username cannot be empty")
    display_name: str = Field(
        ..., min_length=1, description="Display name cannot be empty"
    )
    bio: str | None = None
    self_introduction: str | None = None
    icon_url: str | None = None


class UserCreate(UserBase):
    user_id: str = Field(..., min_length=1, description="User ID cannot be empty")


class UserUpdate(OrmBaseModel):
    user_name: str | None = None
    display_name: str | None = None
    bio: str | None = None
    self_introduction: str | None = None
    icon_url: str | None = None
    notification_level: NotificationLevelEnum | None = None


class UserRead(UserBase):
    user_id: str
    notification_level: NotificationLevelEnum
    created_at: datetime
    last_login_at: datetime | None = None
