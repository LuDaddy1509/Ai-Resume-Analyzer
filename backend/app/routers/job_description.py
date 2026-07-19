from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db
from app.services.job_description_service import JobDescriptionService
from app.schemas.job_description_schema import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobDescriptionUpdate
)

router = APIRouter(prefix="/api/job-descriptions", tags=["job-descriptions"])


@router.post("/", response_model=JobDescriptionResponse, status_code=201)
async def create_job_description(jd: JobDescriptionCreate, db: Session = Depends(get_db)):
    """Create a new job description."""
    created_jd = JobDescriptionService.create_jd(db, jd)

    # Deserialize JSON fields for response
    response = JobDescriptionResponse(
        id=created_jd.id,
        title=created_jd.title,
        company=created_jd.company,
        job_level=created_jd.job_level,
        location=created_jd.location,
        work_type=created_jd.work_type,
        source_url=created_jd.source_url,
        raw_text=created_jd.raw_text,
        tags=json.loads(created_jd.tags) if created_jd.tags else [],
        extracted_keywords=json.loads(created_jd.extracted_keywords) if created_jd.extracted_keywords else [],
        status=created_jd.status,
        usage_count=created_jd.usage_count,
        last_used_at=created_jd.last_used_at,
        created_at=created_jd.created_at,
        updated_at=created_jd.updated_at
    )
    return response


@router.get("/", response_model=List[JobDescriptionResponse])
async def get_job_descriptions(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db: Session = Depends(get_db)
):
    """Get all job descriptions with optional filters."""
    jds = JobDescriptionService.get_all_jds(db, status, search, skip, limit)

    # Deserialize JSON fields for response
    return [
        JobDescriptionResponse(
            id=jd.id,
            title=jd.title,
            company=jd.company,
            job_level=jd.job_level,
            location=jd.location,
            work_type=jd.work_type,
            source_url=jd.source_url,
            raw_text=jd.raw_text,
            tags=json.loads(jd.tags) if jd.tags else [],
            extracted_keywords=json.loads(jd.extracted_keywords) if jd.extracted_keywords else [],
            status=jd.status,
            usage_count=jd.usage_count,
            last_used_at=jd.last_used_at,
            created_at=jd.created_at,
            updated_at=jd.updated_at
        )
        for jd in jds
    ]


@router.get("/{jd_id}", response_model=JobDescriptionResponse)
async def get_job_description(jd_id: int, db: Session = Depends(get_db)):
    """Get a single job description by ID."""
    jd = JobDescriptionService.get_jd_by_id(db, jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job Description not found")

    return JobDescriptionResponse(
        id=jd.id,
        title=jd.title,
        company=jd.company,
        job_level=jd.job_level,
        location=jd.location,
        work_type=jd.work_type,
        source_url=jd.source_url,
        raw_text=jd.raw_text,
        tags=json.loads(jd.tags) if jd.tags else [],
        extracted_keywords=json.loads(jd.extracted_keywords) if jd.extracted_keywords else [],
        status=jd.status,
        usage_count=jd.usage_count,
        last_used_at=jd.last_used_at,
        created_at=jd.created_at,
        updated_at=jd.updated_at
    )


@router.put("/{jd_id}", response_model=JobDescriptionResponse)
async def update_job_description(jd_id: int, jd_data: JobDescriptionUpdate, db: Session = Depends(get_db)):
    """Update an existing job description."""
    jd = JobDescriptionService.update_jd(db, jd_id, jd_data)
    if not jd:
        raise HTTPException(status_code=404, detail="Job Description not found")

    return JobDescriptionResponse(
        id=jd.id,
        title=jd.title,
        company=jd.company,
        job_level=jd.job_level,
        location=jd.location,
        work_type=jd.work_type,
        source_url=jd.source_url,
        raw_text=jd.raw_text,
        tags=json.loads(jd.tags) if jd.tags else [],
        extracted_keywords=json.loads(jd.extracted_keywords) if jd.extracted_keywords else [],
        status=jd.status,
        usage_count=jd.usage_count,
        last_used_at=jd.last_used_at,
        created_at=jd.created_at,
        updated_at=jd.updated_at
    )


@router.post("/{jd_id}/duplicate", response_model=JobDescriptionResponse)
async def duplicate_job_description(jd_id: int, db: Session = Depends(get_db)):
    """Create a copy of an existing job description."""
    jd = JobDescriptionService.duplicate_jd(db, jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job Description not found")

    return JobDescriptionResponse(
        id=jd.id,
        title=jd.title,
        company=jd.company,
        job_level=jd.job_level,
        location=jd.location,
        work_type=jd.work_type,
        source_url=jd.source_url,
        raw_text=jd.raw_text,
        tags=json.loads(jd.tags) if jd.tags else [],
        extracted_keywords=json.loads(jd.extracted_keywords) if jd.extracted_keywords else [],
        status=jd.status,
        usage_count=jd.usage_count,
        last_used_at=jd.last_used_at,
        created_at=jd.created_at,
        updated_at=jd.updated_at
    )


@router.patch("/{jd_id}/archive", response_model=JobDescriptionResponse)
async def archive_job_description(jd_id: int, db: Session = Depends(get_db)):
    """Archive a job description (soft delete)."""
    jd = JobDescriptionService.archive_jd(db, jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job Description not found")

    return JobDescriptionResponse(
        id=jd.id,
        title=jd.title,
        company=jd.company,
        job_level=jd.job_level,
        location=jd.location,
        work_type=jd.work_type,
        source_url=jd.source_url,
        raw_text=jd.raw_text,
        tags=json.loads(jd.tags) if jd.tags else [],
        extracted_keywords=json.loads(jd.extracted_keywords) if jd.extracted_keywords else [],
        status=jd.status,
        usage_count=jd.usage_count,
        last_used_at=jd.last_used_at,
        created_at=jd.created_at,
        updated_at=jd.updated_at
    )


@router.post("/{jd_id}/use")
async def mark_jd_used(jd_id: int, db: Session = Depends(get_db)):
    """Record that a job description was used."""
    JobDescriptionService.increment_usage(db, jd_id)
    return {"message": "Usage recorded"}


@router.delete("/{jd_id}")
async def delete_job_description(jd_id: int, db: Session = Depends(get_db)):
    """Delete (archive) a job description."""
    jd = JobDescriptionService.archive_jd(db, jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return {"message": "Job Description archived"}
