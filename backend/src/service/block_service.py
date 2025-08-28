from sqlalchemy.orm import Session

from src.db.tables import UserBlock, UserReport
from src.schema.block import BlockCreate, ReportCreate
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
