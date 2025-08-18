from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .common import OrmBaseModel


class VisitBase(BaseModel):
    visitor_user_id: Optional[str] = None
    visited_user_id: str
    is_anonymous: bool = False


class VisitCreate(VisitBase):
    pass


class VisitorInfo(OrmBaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    display_name: Optional[str] = None
    icon_url: Optional[str] = None
    is_anonymous: bool = False


class VisitRead(OrmBaseModel):
    visit_id: int
    visitor_user_id: Optional[str] = None
    visited_user_id: str
    is_anonymous: bool
    visited_at: datetime
    visitor_info: Optional[VisitorInfo] = None


class VisitsVisibilityUpdate(BaseModel):
    visible: bool
