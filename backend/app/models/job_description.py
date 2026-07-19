from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from app.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    company = Column(String(200), nullable=True, index=True)
    job_level = Column(String(50), nullable=True)
    location = Column(String(200), nullable=True)
    work_type = Column(String(50), nullable=True)
    source_url = Column(String(500), nullable=True)
    raw_text = Column(Text, nullable=False)
    extracted_keywords = Column(Text, nullable=True)  # JSON
    tags = Column(Text, nullable=True)  # JSON
    status = Column(String(20), default="active")
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_jd_status_created', 'status', 'created_at'),
    )
