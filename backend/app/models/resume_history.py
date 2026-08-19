from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import json

class ResumeHistory(Base):
    __tablename__ = "resume_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String(255), index=True)
    full_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20), nullable=True)
    skills = Column(Text)           # Lưu dạng JSON string
    experiences = Column(Text)      # Lưu dạng JSON string
    match_score = Column(Integer, default=0)
    job_description_id = Column(Integer, nullable=True, index=True)
    job_description_snapshot = Column(Text, nullable=True)  # JSON snapshot
    resume_id = Column(Integer, nullable=True)
    analysis_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    user = relationship("User", back_populates="resume_history")