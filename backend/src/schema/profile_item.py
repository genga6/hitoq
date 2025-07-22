import uuid

from src.schema.common import OrmBaseModel


class ProfileItemBase(OrmBaseModel):
    label: str
    value: str
    display_order: int


class ProfileItemCreate(ProfileItemBase):
    pass


class ProfileItemUpdate(OrmBaseModel):
    label: str | None = None
    value: str | None = None
    display_order: int | None = None


class ProfileItemRead(ProfileItemBase):
    profile_item_id: uuid.UUID
    user_id: str
