from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.db.tables import User, Visit


def record_visit(
    db: Session, visited_user_id: str, visitor_user_id: Optional[str] = None
) -> Optional[Visit]:
    """
    Record a visit to a user's page.
    Returns None if the visit was not recorded (e.g., same user visiting their own page).
    """
    # Don't record visits to own page
    if visitor_user_id == visited_user_id:
        return None

    # Check if visited user exists
    visited_user = db.query(User).filter(User.user_id == visited_user_id).first()
    if not visited_user:
        return None

    # Check for recent visit (within last hour) to avoid spam
    recent_cutoff = datetime.utcnow() - timedelta(hours=1)
    existing_visit = (
        db.query(Visit)
        .filter(
            Visit.visited_user_id == visited_user_id,
            Visit.visitor_user_id == visitor_user_id,
            Visit.visited_at > recent_cutoff,
        )
        .first()
    )

    if existing_visit:
        # Update existing visit timestamp
        existing_visit.visited_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_visit)
        return existing_visit

    # Create new visit record
    visit = Visit(
        visitor_user_id=visitor_user_id,
        visited_user_id=visited_user_id,
        is_anonymous=(visitor_user_id is None),
    )

    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


def get_user_visits(db: Session, user_id: str, limit: int = 50) -> list[Visit]:
    """
    Get visits to a user's page, ordered by most recent.
    Only returns visits if the user has made their visits visible.
    Returns only the latest visit per visitor to avoid duplicates.
    """
    # Check if user exists and has visits visible
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.visits_visible:
        return []

    # Subquery to get the latest visit_id for each visitor
    latest_visits_subquery = (
        db.query(func.max(Visit.visit_id).label("max_visit_id"), Visit.visitor_user_id)
        .filter(Visit.visited_user_id == user_id)
        .group_by(Visit.visitor_user_id)
        .subquery()
    )

    # Main query to get the actual visit records
    visits = (
        db.query(Visit)
        .options(joinedload(Visit.visitor_user))
        .join(
            latest_visits_subquery,
            Visit.visit_id == latest_visits_subquery.c.max_visit_id,
        )
        .order_by(Visit.visited_at.desc())
        .limit(limit)
        .all()
    )

    return visits


def get_visit_count(db: Session, user_id: str) -> int:
    """Get the total number of visits to a user's page."""
    return db.query(Visit).filter(Visit.visited_user_id == user_id).count()


def update_visits_visibility(db: Session, user_id: str, visible: bool) -> bool:
    """Update a user's visits visibility setting."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return False

    user.visits_visible = visible
    db.commit()
    return True


def get_visits_visibility(db: Session, user_id: str) -> bool:
    """Get a user's visits visibility setting."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return False

    return user.visits_visible
