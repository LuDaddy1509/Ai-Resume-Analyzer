from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_summary(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get dashboard summary statistics."""
    # Parse dates if provided
    from_date = None
    to_date = None

    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            pass

    return DashboardService.get_summary(db, from_date, to_date)


@router.get("/score-distribution")
async def get_score_distribution(
    score_type: str = Query('match', description="Type of score: match, ats, overall"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get score distribution in buckets."""
    # Parse dates if provided
    from_date = None
    to_date = None

    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            pass

    return DashboardService.get_score_distribution(db, score_type, from_date, to_date)


@router.get("/top-skills")
async def get_top_skills(
    limit: int = Query(10, ge=1, le=50, description="Number of top skills to return"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get top N skills across all resumes."""
    # Parse dates if provided
    from_date = None
    to_date = None

    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            pass

    return DashboardService.get_top_skills(db, limit, from_date, to_date)
