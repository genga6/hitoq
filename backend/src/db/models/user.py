from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class UserBase(BaseModel):
    username: str
    icon_url: HttpUrl | None = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
