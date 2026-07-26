from pydantic import BaseModel
from typing import List, Optional

class Experience(BaseModel):
    company: str
    position: str
    dates: str
    bullets: List[str] = []

class ResumeAnalysis(BaseModel):
    match_score: int
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    suggestions: List[str] = []
    ats_score: Optional[int] = None
    strengths: Optional[List[str]] = None

class Resume(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    skills: List[str] = []
    experiences: List[Experience] = []
    analysis: Optional[ResumeAnalysis] = None

class ResumeResponse(BaseModel):
    """Wrapper response that includes validation information"""
    success: bool
    is_resume: bool
    resume_confidence: float
    message: str
    data: Optional[Resume] = None
    history_id: Optional[int] = None

class ValidationErrorResponse(BaseModel):
    """Response for validation failures"""
    success: bool
    is_resume: bool
    error_code: str
    message: str
