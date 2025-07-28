from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.router.auth import _get_current_user
from src.schema.answer import AnswerCreate, AnswerRead
from src.schema.bucket_list_item import (
    BucketListItemCreate,
    BucketListItemRead,
    BucketListItemUpdate,
)
from src.schema.composite_schema import (
    BucketListPageData,
    ProfilePageData,
    QnAPageData,
)
from src.schema.profile_item import (
    ProfileItemCreate,
    ProfileItemRead,
    ProfileItemUpdate,
)
from src.schema.question import QuestionRead
from src.schema.user import UserCreate, UserRead
from src.schema.visit import VisitorInfo, VisitRead, VisitsVisibilityUpdate
from src.service import (
    bucket_list_item_service,
    profile_service,
    qna_service,
    user_service,
    visit_service,
)
from src.service.question_templates import get_category_title

resource_router = APIRouter(
    prefix="/users/{user_id}",
    tags=["Resources (by UserID)"],
)

username_router = APIRouter(
    prefix="/users/by-username/{user_name}",
    tags=["Page Data (by UserName)"],
)

global_router = APIRouter(
    prefix="/users",
    tags=["Global User Resources"],
)


@username_router.get("/profile", response_model=ProfilePageData)
def read_profile_page_data(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_with_items = user_service.get_user_with_profile_items(db, user.user_id)
    if not user_with_items:
        raise HTTPException(status_code=404, detail="User not found")
    return {"profile": user_with_items, "profile_items": user_with_items.profile_items}


@username_router.get("/bucket-list", response_model=BucketListPageData)
def read_bucket_list_page_data(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_with_items = user_service.get_user_with_bucket_list_items(db, user.user_id)
    if not user_with_items:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "profile": user_with_items,
        "bucket_list_items": user_with_items.bucket_list_items,
    }


@username_router.get("/qna", response_model=QnAPageData)
def read_qna_page_data(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_with_items = user_service.get_user_with_qna_items(db, user.user_id)
    if not user_with_items:
        raise HTTPException(status_code=404, detail="User not found")
    user_answer_groups = qna_service.get_user_qna(db, user.user_id)
    all_questions_grouped = qna_service.get_all_questions_grouped(db)

    available_templates = []
    for category, questions in all_questions_grouped.items():
        if not any(group.template_id == category.name for group in user_answer_groups):
            available_templates.append(
                {
                    "id": category.name,
                    "title": get_category_title(category),
                    "questions": questions,
                }
            )

    return {
        "profile": user_with_items,
        "user_answer_groups": user_answer_groups,
        "available_templates": available_templates,
    }


@resource_router.post(
    "/profile-items",
    response_model=ProfileItemRead,
    status_code=201,
)
def create_profile_item_endpoint(
    user_id: str, item_in: ProfileItemCreate, db: Session = Depends(get_db)
):
    return profile_service.create_profile_item(db=db, user_id=user_id, item_in=item_in)


@resource_router.put("/profile-items/{item_id}", response_model=ProfileItemRead)
def update_profile_item_endpoint(
    user_id: str,
    item_id: str,
    item_in: ProfileItemUpdate,
    db: Session = Depends(get_db),
):
    return profile_service.update_profile_item(
        db=db, user_id=user_id, item_id=item_id, item_in=item_in
    )


@resource_router.delete("/profile-items/{item_id}", status_code=204)
def delete_profile_item_endpoint(
    user_id: str, item_id: str, db: Session = Depends(get_db)
):
    profile_service.delete_profile_item(db=db, user_id=user_id, item_id=item_id)
    return None


@resource_router.post(
    "/bucket-list-items",
    response_model=BucketListItemRead,
    status_code=201,
)
def create_bucket_list_item_endpoint(
    user_id: str, item_in: BucketListItemCreate, db: Session = Depends(get_db)
):
    return bucket_list_item_service.create_bucket_list_item(
        db=db, user_id=user_id, item_in=item_in
    )


@resource_router.put("/bucket-list-items/{item_id}", response_model=BucketListItemRead)
def update_bucket_list_item_endpoint(
    user_id: str,
    item_id: int,
    item_in: BucketListItemUpdate,
    db: Session = Depends(get_db),
):
    return bucket_list_item_service.update_bucket_list_item(
        db=db, user_id=user_id, item_id=item_id, item_in=item_in
    )


@resource_router.delete("/bucket-list-items/{item_id}", status_code=204)
def delete_bucket_list_item_endpoint(
    user_id: str, item_id: int, db: Session = Depends(get_db)
):
    bucket_list_item_service.delete_bucket_list_item(
        db=db, user_id=user_id, item_id=item_id
    )
    return None


@resource_router.post("/questions/{question_id}/answers", response_model=AnswerRead)
def create_new_answer(
    user_id: str,
    question_id: int,
    answer_in: AnswerCreate,
    db: Session = Depends(get_db),
):
    return qna_service.create_answer(
        db=db, user_id=user_id, question_id=question_id, answer_in=answer_in
    )


@global_router.post("", response_model=UserRead, status_code=201)
def upsert_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_service.upsert_user(db=db, user_in=user_in)


@global_router.get("", response_model=list[UserRead])
def read_all_users_endpoint(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return user_service.get_users(db, skip=skip, limit=limit)


@global_router.get("/{user_id}", response_model=UserRead)
def read_user_by_id_endpoint(user_id: str, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@global_router.get("/by-username/{user_name}", response_model=UserRead)
def read_user_by_username_endpoint(user_name: str, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@global_router.get("/resolve-users-id", response_model=UserRead)
def resolve_user_by_username(
    user_name: str = Query(..., min_length=1), db: Session = Depends(get_db)
):
    user = user_service.get_user_by_username(db, user_name=user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@global_router.get("/search/users", response_model=list[UserRead])
def search_users_by_display_name(
    q: str = Query(..., min_length=1, description="Search query for display name"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    """Search users by display name with partial matching."""
    users = user_service.search_users_by_display_name(db, display_name=q, limit=limit)
    return users


@global_router.delete("/{user_id}", status_code=204)
def delete_user_endpoint(user_id: str, db: Session = Depends(get_db)):
    success = user_service.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None


@global_router.get("/questions", response_model=list[QuestionRead])
def read_all_questions(db: Session = Depends(get_db)):
    return qna_service.get_all_questions(db=db)


# Visit related endpoints
@resource_router.post("/visit", status_code=201)
def record_visit_endpoint(
    user_id: str, request: Request, db: Session = Depends(get_db)
):
    """Record a visit to a user's page."""
    # Try to get current user (may be None for anonymous visitors)
    visitor_user_id = None
    try:
        current_user = _get_current_user(request, db)
        visitor_user_id = current_user.user_id
    except HTTPException:
        # Anonymous visitor
        pass

    visit = visit_service.record_visit(
        db=db, visited_user_id=user_id, visitor_user_id=visitor_user_id
    )

    if not visit:
        raise HTTPException(status_code=400, detail="Visit not recorded")

    return {"message": "Visit recorded successfully"}


@resource_router.get("/visits", response_model=list[VisitRead])
def get_user_visits_endpoint(
    user_id: str, limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)
):
    """Get visits to a user's page (only if visits are visible)."""
    visits = visit_service.get_user_visits(db=db, user_id=user_id, limit=limit)

    # Convert to response format
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


@resource_router.put("/visits-visibility", status_code=204)
def update_visits_visibility_endpoint(
    user_id: str,
    visibility_update: VisitsVisibilityUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Update visits visibility setting (requires authentication and ownership)."""
    current_user = _get_current_user(request, db)

    # Check if user is updating their own settings
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = visit_service.update_visits_visibility(
        db=db, user_id=user_id, visible=visibility_update.visible
    )

    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return None


@resource_router.get("/visits-visibility")
def get_visits_visibility_endpoint(
    user_id: str, request: Request, db: Session = Depends(get_db)
):
    """Get visits visibility setting (requires authentication and ownership)."""
    current_user = _get_current_user(request, db)

    # Check if user is accessing their own settings
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    visible = visit_service.get_visits_visibility(db=db, user_id=user_id)

    return {"visible": visible}
