from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.skill_gaps import SkillGap, SkillGapPriority, LearningPath, UserSkillProgress
from app.models.analyses import Analysis
from app.models.resumes import Resume
from app.services.skill_gap_service import SkillGapService

router = APIRouter(prefix="/api/skill-gaps", tags=["skill-gaps"])

skill_gap_service = SkillGapService()


# Pydantic Schemas
class SkillGapResponse(BaseModel):
    id: int
    analysis_id: int
    skill_name: str
    priority: str
    market_demand_score: Optional[float]
    learnability_score: Optional[float]
    impact_on_match_score: Optional[float]
    current_proficiency: Optional[str]
    target_proficiency: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LearningPathResponse(BaseModel):
    id: int
    skill_gap_id: int
    resources: Optional[List[dict]]
    estimated_weeks: Optional[int]
    project_ideas: Optional[List[str]]
    milestones: Optional[List[dict]]

    class Config:
        from_attributes = True


class SkillGapWithPathResponse(SkillGapResponse):
    learning_path: Optional[LearningPathResponse] = None


class UserSkillProgressCreate(BaseModel):
    skill_name: str
    status: str = "learning"
    proficiency_level: Optional[str] = None
    evidence_url: Optional[str] = None
    notes: Optional[str] = None


class UserSkillProgressResponse(BaseModel):
    id: int
    user_id: int
    skill_id: Optional[int]
    skill_name: str
    status: str
    proficiency_level: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    evidence_url: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class SkillGapAnalysisRequest(BaseModel):
    analysis_id: int
    resume_id: int


@router.post("/analyze", response_model=List[SkillGapWithPathResponse])
async def analyze_skill_gaps(
    request: SkillGapAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze skill gaps for a given analysis and resume.
    Creates SkillGap records and generates LearningPaths.
    """
    # Verify analysis exists
    analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Verify resume exists and get skills
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Get resume skills from resume_skills relationship
    resume_skills = []
    if resume.resume_skills:
        for rs in resume.resume_skills:
            if rs.skill:
                resume_skills.append(rs.skill.name)

    # Also get skills from parsed text (fallback)
    if not resume_skills and analysis.skills_match:
        try:
            resume_skills = json.loads(analysis.skills_match) if isinstance(analysis.skills_match, str) else analysis.skills_match
        except:
            pass

    # Analyze skill gaps
    skill_gaps = skill_gap_service.analyze_skill_gaps(analysis, resume_skills, db)

    # Save to database
    for sg in skill_gaps:
        db.add(sg)
    db.commit()

    # Generate learning paths for each skill gap
    result = []
    for sg in skill_gaps:
        db.refresh(sg)
        learning_path = skill_gap_service.generate_learning_path(sg, db)
        db.add(learning_path)
        db.commit()
        db.refresh(learning_path)

        result.append(SkillGapWithPathResponse(
            id=sg.id,
            analysis_id=sg.analysis_id,
            skill_name=sg.skill_name,
            priority=sg.priority.value,
            market_demand_score=sg.market_demand_score,
            learnability_score=sg.learnability_score,
            impact_on_match_score=sg.impact_on_match_score,
            current_proficiency=sg.current_proficiency,
            target_proficiency=sg.target_proficiency,
            created_at=sg.created_at,
            learning_path=LearningPathResponse(
                id=learning_path.id,
                skill_gap_id=learning_path.skill_gap_id,
                resources=learning_path.resources,
                estimated_weeks=learning_path.estimated_weeks,
                project_ideas=learning_path.project_ideas,
                milestones=learning_path.milestones
            )
        ))

    return result


@router.get("/analysis/{analysis_id}", response_model=List[SkillGapWithPathResponse])
async def get_skill_gaps_for_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get all skill gaps for an analysis with their learning paths"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    skill_gaps = db.query(SkillGap).filter(SkillGap.analysis_id == analysis_id).all()

    result = []
    for sg in skill_gaps:
        learning_path = db.query(LearningPath).filter(LearningPath.skill_gap_id == sg.id).first()

        result.append(SkillGapWithPathResponse(
            id=sg.id,
            analysis_id=sg.analysis_id,
            skill_name=sg.skill_name,
            priority=sg.priority.value,
            market_demand_score=sg.market_demand_score,
            learnability_score=sg.learnability_score,
            impact_on_match_score=sg.impact_on_match_score,
            current_proficiency=sg.current_proficiency,
            target_proficiency=sg.target_proficiency,
            created_at=sg.created_at,
            learning_path=LearningPathResponse(
                id=learning_path.id,
                skill_gap_id=learning_path.skill_gap_id,
                resources=learning_path.resources,
                estimated_weeks=learning_path.estimated_weeks,
                project_ideas=learning_path.project_ideas,
                milestones=learning_path.milestones
            ) if learning_path else None
        ))

    return result


@router.get("/{skill_gap_id}/learning-path", response_model=LearningPathResponse)
async def get_learning_path(
    skill_gap_id: int,
    db: Session = Depends(get_db)
):
    """Get learning path for a specific skill gap"""
    skill_gap = db.query(SkillGap).filter(SkillGap.id == skill_gap_id).first()
    if not skill_gap:
        raise HTTPException(status_code=404, detail="Skill gap not found")

    learning_path = db.query(LearningPath).filter(LearningPath.skill_gap_id == skill_gap_id).first()
    if not learning_path:
        # Generate on-demand
        learning_path = skill_gap_service.generate_learning_path(skill_gap, db)
        db.add(learning_path)
        db.commit()
        db.refresh(learning_path)

    return LearningPathResponse(
        id=learning_path.id,
        skill_gap_id=learning_path.skill_gap_id,
        resources=learning_path.resources,
        estimated_weeks=learning_path.estimated_weeks,
        project_ideas=learning_path.project_ideas,
        milestones=learning_path.milestones
    )


# User Skill Progress Endpoints
@router.post("/progress", response_model=UserSkillProgressResponse)
async def create_skill_progress(
    progress: UserSkillProgressCreate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Create or update user's skill progress"""
    updated = skill_gap_service.update_skill_progress(
        user_id=user_id,
        skill_name=progress.skill_name,
        status=progress.status,
        proficiency_level=progress.proficiency_level,
        evidence_url=progress.evidence_url,
        notes=progress.notes,
        db=db
    )
    return UserSkillProgressResponse.from_orm(updated)


@router.get("/progress/{user_id}", response_model=List[UserSkillProgressResponse])
async def get_user_skill_progress(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all skill progress for a user"""
    progress_list = skill_gap_service.get_user_skill_progress(user_id, db)
    return [UserSkillProgressResponse.from_orm(p) for p in progress_list]


@router.patch("/progress/{progress_id}", response_model=UserSkillProgressResponse)
async def update_skill_progress(
    progress_id: int,
    progress: UserSkillProgressCreate,
    db: Session = Depends(get_db)
):
    """Update a specific skill progress record"""
    existing = db.query(UserSkillProgress).filter(UserSkillProgress.id == progress_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Skill progress not found")

    updated = skill_gap_service.update_skill_progress(
        user_id=existing.user_id,
        skill_name=progress.skill_name,
        status=progress.status,
        proficiency_level=progress.proficiency_level,
        evidence_url=progress.evidence_url,
        notes=progress.notes,
        db=db
    )
    return UserSkillProgressResponse.from_orm(updated)


import json