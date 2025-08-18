from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.router.auth import get_current_user
from src.schema.visit import VisitorInfo, VisitRead, VisitsVisibilityUpdate
from src.service import visit_service

visit_router = APIRouter(
    prefix="/users/{user_id}",
    tags=["Visits"],
)


@visit_router.post("/visit", status_code=201)
def record_visit_endpoint(
    user_id: str, request: Request, db: Session = Depends(get_db)
):
    visitor_user_id = None
    try:
        current_user = get_current_user(request, db)
        visitor_user_id = current_user.user_id
    except HTTPException:
        pass

    visit = visit_service.record_visit(
        db=db, visited_user_id=user_id, visitor_user_id=visitor_user_id
    )

    if not visit:
        raise HTTPException(status_code=400, detail="Visit not recorded")

    return {"message": "Visit recorded successfully"}


@visit_router.get("/visits", response_model=list[VisitRead])
def get_user_visits_endpoint(
    user_id: str, limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)
):
    visits = visit_service.get_user_visits(db=db, user_id=user_id, limit=limit)

    visit_reads = []
    for visit in visits:
        visitor_info = None
        if visit.visitor_user and not visit.is_anonymous:
            visitor_info = VisitorInfo(
                user_id=visit.visitor_user.user_id,
                user_name=visit.visitor_user.user_name,
                display_name=visit.visitor_user.display_name,
                icon_url=visit.visitor_user.icon_url,
                is_anonymous=False,
            )
        elif visit.is_anonymous:
            visitor_info = VisitorInfo(is_anonymous=True)

        visit_reads.append(
            VisitRead(
                visit_id=visit.visit_id,
                visitor_user_id=visit.visitor_user_id,
                visited_user_id=visit.visited_user_id,
                is_anonymous=visit.is_anonymous,
                visited_at=visit.visited_at,
                visitor_info=visitor_info,
            )
        )

    return visit_reads


@visit_router.put("/visits-visibility", status_code=204)
def update_visits_visibility_endpoint(
    user_id: str,
    visibility_update: VisitsVisibilityUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request, db)

    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = visit_service.update_visits_visibility(
        db=db, user_id=user_id, visible=visibility_update.visible
    )

    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return None


@visit_router.get("/visits-visibility")
def get_visits_visibility_endpoint(
    user_id: str, request: Request, db: Session = Depends(get_db)
):
    current_user = get_current_user(request, db)

    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    visible = visit_service.get_visits_visibility(db=db, user_id=user_id)

    return {"visible": visible}
