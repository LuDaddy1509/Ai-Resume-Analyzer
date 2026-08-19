from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class OptimizationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResumeOptimization(Base):
    __tablename__ = "resume_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    status = Column(SQLEnum(OptimizationStatus), default=OptimizationStatus.PENDING, nullable=False)

    # Original content
    original_summary = Column(Text, nullable=True)
    original_skills = Column(JSON, nullable=True)
    original_experiences = Column(JSON, nullable=True)
    original_projects = Column(JSON, nullable=True)
    original_education = Column(JSON, nullable=True)

    # Optimized content
    optimized_summary = Column(Text, nullable=True)
    optimized_skills = Column(JSON, nullable=True)
    optimized_experiences = Column(JSON, nullable=True)
    optimized_projects = Column(JSON, nullable=True)
    optimized_education = Column(JSON, nullable=True)

    # ATS scores
    original_ats_score = Column(Float, nullable=True)
    optimized_ats_score = Column(Float, nullable=True)
    ats_improvement = Column(Float, nullable=True)

    # Match scores (if JD provided)
    original_match_score = Column(Float, nullable=True)
    optimized_match_score = Column(Float, nullable=True)
    match_improvement = Column(Float, nullable=True)

    # Metadata
    optimization_notes = Column(JSON, nullable=True)  # List of changes made
    keyword_density_before = Column(JSON, nullable=True)
    keyword_density_after = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    resume = relationship("Resume", back_populates="optimizations")
    analysis = relationship("Analysis")
    job_description = relationship("JobDescription")


class OptimizationTemplate(Base):
    __tablename__ = "optimization_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    target_role = Column(String(100), nullable=True)
    target_level = Column(String(50), nullable=True)  # junior, mid, senior, staff
    template_data = Column(JSON, nullable=False)  # Structure templates for each section
    is_active = Column(String(10), default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())