from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class JobDescriptionBase(BaseModel):
    title: str = Field(..., max_length=200)
    company: Optional[str] = None
    job_level: Optional[str] = None
    location: Optional[str] = None
    work_type: Optional[str] = None
    source_url: Optional[str] = None
    raw_text: str
    tags: Optional[List[str]] = None


class JobDescriptionCreate(JobDescriptionBase):
    pass


class JobDescriptionUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    job_level: Optional[str] = None
    location: Optional[str] = None
    work_type: Optional[str] = None
    source_url: Optional[str] = None
    raw_text: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class JobDescriptionResponse(JobDescriptionBase):
    id: int
    extracted_keywords: List[str] = []
    status: str
    usage_count: int
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
