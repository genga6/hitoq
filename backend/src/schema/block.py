from datetime import datetime
from uuid import UUID

from src.db.tables import ReportStatusEnum, ReportTypeEnum
from src.schema.common import OrmBaseModel


class BlockCreate(OrmBaseModel):
    blocked_user_id: str


class BlockRead(OrmBaseModel):
    block_id: UUID
    blocker_user_id: str
    blocked_user_id: str
    created_at: datetime


class ReportCreate(OrmBaseModel):
    reported_user_id: str
    report_type: ReportTypeEnum
    description: str | None = None


class ReportRead(OrmBaseModel):
    report_id: UUID
    reporter_user_id: str
    reported_user_id: str
    report_type: ReportTypeEnum
    description: str | None = None
    status: ReportStatusEnum
    created_at: datetime
    reviewed_at: datetime | None = None
