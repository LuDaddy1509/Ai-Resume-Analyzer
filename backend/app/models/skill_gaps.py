from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class SkillGapPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    skill_name = Column(String(100), nullable=False, index=True)
    priority = Column(SQLEnum(SkillGapPriority), default=SkillGapPriority.MEDIUM, nullable=False)
    market_demand_score = Column(Float, nullable=True)  # 0-1 scale
    learnability_score = Column(Float, nullable=True)   # 0-1 scale (higher = easier to learn)
    impact_on_match_score = Column(Float, nullable=True)  # estimated points gained
    current_proficiency = Column(String(50), nullable=True)  # none, basic, intermediate, advanced
    target_proficiency = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    analysis = relationship("Analysis", back_populates="skill_gaps")
    learning_paths = relationship("LearningPath", back_populates="skill_gap", cascade="all, delete-orphan")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    skill_gap_id = Column(Integer, ForeignKey("skill_gaps.id"), nullable=False)
    resources = Column(JSON, nullable=True)  # List of {type, title, url, cost, duration_weeks, rating}
    estimated_weeks = Column(Integer, nullable=True)
    project_ideas = Column(JSON, nullable=True)  # List of project descriptions
    milestones = Column(JSON, nullable=True)  # List of {week, goal, deliverable}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    skill_gap = relationship("SkillGap", back_populates="learning_paths")


class UserSkillProgress(Base):
    __tablename__ = "user_skill_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    skill_name = Column(String(100), nullable=False, index=True)  # Denormalized for skills not in catalog
    status = Column(String(50), default="learning", nullable=False)  # learning, proficient, showcased
    proficiency_level = Column(String(50), nullable=True)  # basic, intermediate, advanced, expert
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    evidence_url = Column(String(500), nullable=True)  # GitHub, portfolio, certificate link
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="skill_progress")
    skill = relationship("Skill", back_populates="user_progress")