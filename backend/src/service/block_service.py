from uuid import UUID

from sqlalchemy.orm import Session

from src.db.tables import UserBlock, UserReport
from src.schema.block import BlockCreate, ReportCreate, ReportUpdate
from src.service import user_service


def create_block(db: Session, blocker_user_id: str, block_in: BlockCreate) -> UserBlock:
    # Check if blocked user exists
    blocked_user = user_service.get_user(db, block_in.blocked_user_id)
    if not blocked_user:
        raise ValueError("User not found")

    existing_block = (
        db.query(UserBlock)
        .filter(
            UserBlock.blocker_user_id == blocker_user_id,
            UserBlock.blocked_user_id == block_in.blocked_user_id,
        )
        .first()
    )

    if existing_block:
        return existing_block

    if blocker_user_id == block_in.blocked_user_id:
        raise ValueError("Cannot block yourself")

    db_block = UserBlock(
        blocker_user_id=blocker_user_id,
        blocked_user_id=block_in.blocked_user_id,
    )
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block


def remove_block(db: Session, blocker_user_id: str, blocked_user_id: str) -> bool:
    block = (
        db.query(UserBlock)
        .filter(
            UserBlock.blocker_user_id == blocker_user_id,
            UserBlock.blocked_user_id == blocked_user_id,
        )
        .first()
    )

    if not block:
        return False

    db.delete(block)
    db.commit()
    return True


def get_blocked_users(db: Session, user_id: str) -> list[UserBlock]:
    return db.query(UserBlock).filter(UserBlock.blocker_user_id == user_id).all()


def is_blocked(db: Session, blocker_user_id: str, blocked_user_id: str) -> bool:
    return (
        db.query(UserBlock)
        .filter(
            UserBlock.blocker_user_id == blocker_user_id,
            UserBlock.blocked_user_id == blocked_user_id,
        )
        .first()
        is not None
    )


def create_report(
    db: Session, reporter_user_id: str, report_in: ReportCreate
) -> UserReport:
    # Check if reported user exists
    reported_user = user_service.get_user(db, report_in.reported_user_id)
    if not reported_user:
        raise ValueError("User not found")

    if reporter_user_id == report_in.reported_user_id:
        raise ValueError("Cannot report yourself")

    db_report = UserReport(
        reporter_user_id=reporter_user_id,
        reported_user_id=report_in.reported_user_id,
        report_type=report_in.report_type,
        description=report_in.description,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_reports(db: Session, skip: int = 0, limit: int = 100) -> list[UserReport]:
    return db.query(UserReport).offset(skip).limit(limit).all()


def get_report_by_id(db: Session, report_id: UUID) -> UserReport | None:
    return db.query(UserReport).filter(UserReport.report_id == report_id).first()


def update_report(
    db: Session, report_id: UUID, report_update: ReportUpdate
) -> UserReport | None:
    report = get_report_by_id(db, report_id)
    if not report:
        return None

    for field, value in report_update.model_dump(exclude_unset=True).items():
        setattr(report, field, value)

    db.commit()
    db.refresh(report)
    return report
