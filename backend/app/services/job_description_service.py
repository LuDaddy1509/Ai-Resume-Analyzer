from sqlalchemy.orm import Session
from app.models.job_description import JobDescription
from app.schemas.job_description_schema import JobDescriptionCreate, JobDescriptionUpdate
from typing import List, Optional
import json
import re
from datetime import datetime


# Reuse KNOWN_SKILLS from parser_service
from app.services.parser_service import KNOWN_SKILLS


def extract_keywords_from_text(text: str) -> List[str]:
    """Extract technical keywords from job description text."""
    found = set()
    text_upper = text.upper()

    for skill in KNOWN_SKILLS:
        pattern = r"(?<![A-Z0-9])" + re.escape(skill.upper()) + r"(?![A-Z0-9])"
        if re.search(pattern, text_upper):
            found.add(skill)

    return sorted(found)


class JobDescriptionService:
    @staticmethod
    def create_jd(db: Session, jd_data: JobDescriptionCreate) -> JobDescription:
        """Create a new job description."""
        extracted_keywords = extract_keywords_from_text(jd_data.raw_text)

        jd = JobDescription(
            title=jd_data.title,
            company=jd_data.company,
            job_level=jd_data.job_level,
            location=jd_data.location,
            work_type=jd_data.work_type,
            source_url=jd_data.source_url,
            raw_text=jd_data.raw_text,
            extracted_keywords=json.dumps(extracted_keywords),
            tags=json.dumps(jd_data.tags or []),
            status="active"
        )
        db.add(jd)
        db.commit()
        db.refresh(jd)
        return jd

    @staticmethod
    def get_all_jds(db: Session, status: Optional[str] = None,
                    search: Optional[str] = None,
                    skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get all job descriptions with optional filters."""
        query = db.query(JobDescription)

        if status:
            query = query.filter(JobDescription.status == status)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (JobDescription.title.ilike(search_term)) |
                (JobDescription.company.ilike(search_term)) |
                (JobDescription.raw_text.ilike(search_term))
            )

        return query.order_by(JobDescription.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_jd_by_id(db: Session, jd_id: int) -> Optional[JobDescription]:
        """Get a single job description by ID."""
        return db.query(JobDescription).filter(JobDescription.id == jd_id).first()

    @staticmethod
    def update_jd(db: Session, jd_id: int, jd_data: JobDescriptionUpdate) -> Optional[JobDescription]:
        """Update an existing job description."""
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not jd:
            return None

        update_dict = jd_data.dict(exclude_unset=True)

        # Re-extract keywords if raw_text is updated
        if 'raw_text' in update_dict:
            extracted_keywords = extract_keywords_from_text(update_dict['raw_text'])
            update_dict['extracted_keywords'] = json.dumps(extracted_keywords)

        # Handle tags serialization
        if 'tags' in update_dict and update_dict['tags'] is not None:
            update_dict['tags'] = json.dumps(update_dict['tags'])

        for key, value in update_dict.items():
            setattr(jd, key, value)

        db.commit()
        db.refresh(jd)
        return jd

    @staticmethod
    def increment_usage(db: Session, jd_id: int):
        """Increment usage count and update last used timestamp."""
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if jd:
            jd.usage_count += 1
            jd.last_used_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def archive_jd(db: Session, jd_id: int) -> Optional[JobDescription]:
        """Archive a job description (soft delete)."""
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if jd:
            jd.status = "archived"
            db.commit()
            db.refresh(jd)
        return jd

    @staticmethod
    def duplicate_jd(db: Session, jd_id: int) -> Optional[JobDescription]:
        """Create a copy of an existing job description."""
        original = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not original:
            return None

        new_jd = JobDescription(
            title=f"{original.title} (Copy)",
            company=original.company,
            job_level=original.job_level,
            location=original.location,
            work_type=original.work_type,
            source_url=original.source_url,
            raw_text=original.raw_text,
            extracted_keywords=original.extracted_keywords,
            tags=original.tags,
            status="active"
        )
        db.add(new_jd)
        db.commit()
        db.refresh(new_jd)
        return new_jd
