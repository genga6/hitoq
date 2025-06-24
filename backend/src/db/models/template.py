from datetime import datetime

from pydantic import BaseModel


class TemplateBase(BaseModel):
    title: str
    description: str | None = None


class TemplateCreate(TemplateBase):
    id: str


class TemplateRead(TemplateBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
