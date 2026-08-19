from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class InterviewSessionStatus(str, enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class QuestionType(str, enum.Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SITUATIONAL = "situational"
    CULTURE_FIT = "culture_fit"


class QuestionDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    target_role = Column(String(100), nullable=True)
    target_level = Column(String(50), nullable=True)  # junior, mid, senior, staff
    status = Column(SQLEnum(InterviewSessionStatus), default=InterviewSessionStatus.CREATED, nullable=False)
    total_score = Column(Float, nullable=True)
    behavioral_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    jd = relationship("JobDescription")
    resume = relationship("Resume")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan", order_by="InterviewQuestion.order")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    category = Column(String(100), nullable=True)  # leadership, conflict, system_design, coding, etc.
    question = Column(Text, nullable=False)
    expected_keywords = Column(JSON, nullable=True)  # List of keywords to listen for
    model_answer = Column(Text, nullable=True)  # Ideal answer outline
    difficulty = Column(SQLEnum(QuestionDifficulty), default=QuestionDifficulty.MEDIUM, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    time_limit_seconds = Column(Integer, default=180, nullable=True)  # 3 minutes default
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), unique=True, nullable=False)
    user_answer = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)  # If voice recording saved
    duration_seconds = Column(Integer, nullable=True)

    # AI Evaluation scores (0-25 each, total 100)
    star_structure_score = Column(Float, nullable=True)
    keyword_coverage_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)

    # AI Feedback
    ai_feedback = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)  # List of strengths
    improvements = Column(JSON, nullable=True)  # List of improvements
    suggested_answer = Column(Text, nullable=True)  # Better version

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    question = relationship("InterviewQuestion", back_populates="answer")


class QuestionTemplate(Base):
    __tablename__ = "question_templates"

    id = Column(Integer, primary_key=True, index=True)
    role_category = Column(String(100), nullable=False, index=True)  # frontend, backend, fullstack, devops, data, mobile, qa, management
    target_level = Column(String(50), nullable=False, index=True)  # junior, mid, senior, staff
    question_type = Column(SQLEnum(QuestionType), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # leadership, conflict, system_design, coding, debugging, etc.
    question_text = Column(Text, nullable=False)
    expected_keywords = Column(JSON, nullable=True)
    model_answer = Column(Text, nullable=True)
    difficulty = Column(SQLEnum(QuestionDifficulty), default=QuestionDifficulty.MEDIUM, nullable=False)
    tags = Column(JSON, nullable=True)  # Additional tags for filtering
    is_active = Column(String(10), default="true", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())