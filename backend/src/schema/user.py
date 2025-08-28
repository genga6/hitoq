from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from src.db.tables import NotificationLevelEnum
from src.schema.common import OrmBaseModel

# ユーザー名バリデーション型
Username = Annotated[
    str,
    StringConstraints(pattern=r"^[a-zA-Z0-9_-]{3,30}$"),
    Field(
        description="Username (3-30 characters, alphanumeric, underscore, hyphen only)"
    ),
]


class UserBase(OrmBaseModel):
    user_name: str = Field(
        ..., min_length=1, max_length=50, description="Username cannot be empty"
    )
    display_name: str = Field(
        ..., min_length=1, max_length=50, description="Display name cannot be empty"
    )
    bio: str | None = Field(None, max_length=200, description="Bio")
    icon_url: str | None = Field(None, max_length=500, description="Icon URL")


class UserCreate(UserBase):
    user_id: str = Field(..., min_length=1, description="User ID cannot be empty")


class UserUpdate(OrmBaseModel):
    user_name: str | None = None
    display_name: str | None = None
    bio: str | None = None
    icon_url: str | None = None
    notification_level: NotificationLevelEnum | None = None


class UserRead(UserBase):
    user_id: str
    notification_level: NotificationLevelEnum
    created_at: datetime
    last_login_at: datetime | None = None
