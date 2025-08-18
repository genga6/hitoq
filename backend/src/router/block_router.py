from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.config.limiter import limiter
from src.db.session import get_db
from src.router.auth import get_current_user
from src.schema.block import (
    BlockCreate,
    BlockRead,
    ReportCreate,
    ReportRead,
    ReportUpdate,
)
from src.service import block_service

block_router = APIRouter()


@block_router.post("/block", response_model=BlockRead)
@limiter.limit("10/minute")
async def create_block(
    request: Request,
    block_in: BlockCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        block = block_service.create_block(db, current_user.user_id, block_in)
        return block
    except ValueError as e:
        if "User not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e)) from e
        raise HTTPException(status_code=400, detail=str(e)) from e


@block_router.delete("/block/{blocked_user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def remove_block(
    request: Request,
    blocked_user_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = block_service.remove_block(db, current_user.user_id, blocked_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Block not found")


@block_router.get("/blocks", response_model=list[BlockRead])
async def get_blocked_users(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    blocks = block_service.get_blocked_users(db, current_user.user_id)
    return blocks


@block_router.post("/report", response_model=ReportRead)
@limiter.limit("5/minute")
async def create_report(
    request: Request,
    report_in: ReportCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        report = block_service.create_report(db, current_user.user_id, report_in)
        return report
    except ValueError as e:
        if "User not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e)) from e
        raise HTTPException(status_code=400, detail=str(e)) from e


@block_router.get("/reports", response_model=list[ReportRead])
async def get_reports(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reports = block_service.get_reports(db, skip, limit)
    return reports


@block_router.get("/reports/{report_id}", response_model=ReportRead)
async def get_report(
    report_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = block_service.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@block_router.put("/reports/{report_id}", response_model=ReportRead)
@limiter.limit("20/minute")
async def update_report(
    request: Request,
    report_id: UUID,
    report_update: ReportUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = block_service.update_report(db, report_id, report_update)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@block_router.get("/is-blocked/{user_id}")
async def check_is_blocked(
    user_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    is_blocked = block_service.is_blocked(db, current_user.user_id, user_id)
    return {"is_blocked": is_blocked}
