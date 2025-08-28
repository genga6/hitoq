import uuid

from pydantic import Field

from src.schema.common import OrmBaseModel


class ProfileItemBase(OrmBaseModel):
    label: str = Field(..., min_length=1, description="Label cannot be empty")
    value: str
    display_order: int


class ProfileItemCreate(ProfileItemBase):
    pass


class ProfileItemUpdate(OrmBaseModel):
    value: str | None = Field(None, max_length=500)


class ProfileItemRead(ProfileItemBase):
    profile_item_id: uuid.UUID
    user_id: str
