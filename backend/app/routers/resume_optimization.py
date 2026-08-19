from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.resume_optimization import ResumeOptimization, OptimizationStatus
from app.models.resumes import Resume
from app.models.analyses import Analysis
from app.models.job_description import JobDescription
from app.services.resume_optimization_service import ResumeOptimizationService

router = APIRouter(prefix="/api/resume-optimization", tags=["resume-optimization"])

optimization_service = ResumeOptimizationService()


# Pydantic Schemas
class ResumeOptimizationRequest(BaseModel):
    resume_id: int
    analysis_id: Optional[int] = None
    job_description_id: Optional[int] = None


class ResumeOptimizationResponse(BaseModel):
    id: int
    resume_id: int
    analysis_id: Optional[int]
    job_description_id: Optional[int]
    status: str
    original_summary: Optional[str]
    optimized_summary: Optional[str]
    original_skills: Optional[List[str]]
    optimized_skills: Optional[List[str]]
    original_experiences: Optional[List[dict]]
    optimized_experiences: Optional[List[dict]]
    original_projects: Optional[List[dict]]
    optimized_projects: Optional[List[dict]]
    original_education: Optional[List[dict]]
    optimized_education: Optional[List[dict]]
    original_ats_score: Optional[float]
    optimized_ats_score: Optional[float]
    ats_improvement: Optional[float]
    original_match_score: Optional[float]
    optimized_match_score: Optional[float]
    match_improvement: Optional[float]
    optimization_notes: Optional[List[str]]
    keyword_density_before: Optional[dict]
    keyword_density_after: Optional[dict]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class OptimizationComparisonResponse(BaseModel):
    summary: dict
    skills: dict
    experiences: dict
    projects: dict
    education: dict
    scores: dict
    keyword_density: dict
    notes: Optional[List[str]]


@router.post("/optimize", response_model=ResumeOptimizationResponse)
async def optimize_resume(
    request: ResumeOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize a resume for ATS and human appeal.
    Optionally provide analysis_id and job_description_id for targeted optimization.
    """
    # Verify resume exists
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Verify analysis if provided
    if request.analysis_id:
        analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        if analysis.resume_id != request.resume_id:
            raise HTTPException(status_code=400, detail="Analysis does not belong to this resume")

    # Verify JD if provided
    if request.job_description_id:
        jd = db.query(JobDescription).filter(JobDescription.id == request.job_description_id).first()
        if not jd:
            raise HTTPException(status_code=404, detail="Job Description not found")

    # Run optimization
    try:
        optimization = await optimization_service.optimize_resume(
            resume_id=request.resume_id,
            analysis_id=request.analysis_id,
            job_description_id=request.job_description_id,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

    return ResumeOptimizationResponse(
        id=optimization.id,
        resume_id=optimization.resume_id,
        analysis_id=optimization.analysis_id,
        job_description_id=optimization.job_description_id,
        status=optimization.status.value,
        original_summary=optimization.original_summary,
        optimized_summary=optimization.optimized_summary,
        original_skills=optimization.original_skills,
        optimized_skills=optimization.optimized_skills,
        original_experiences=optimization.original_experiences,
        optimized_experiences=optimization.optimized_experiences,
        original_projects=optimization.original_projects,
        optimized_projects=optimization.optimized_projects,
        original_education=optimization.original_education,
        optimized_education=optimization.optimized_education,
        original_ats_score=optimization.original_ats_score,
        optimized_ats_score=optimization.optimized_ats_score,
        ats_improvement=optimization.ats_improvement,
        original_match_score=optimization.original_match_score,
        optimized_match_score=optimization.optimized_match_score,
        match_improvement=optimization.match_improvement,
        optimization_notes=optimization.optimization_notes,
        keyword_density_before=optimization.keyword_density_before,
        keyword_density_after=optimization.keyword_density_after,
        created_at=optimization.created_at,
        completed_at=optimization.completed_at
    )


@router.get("/resume/{resume_id}", response_model=List[ResumeOptimizationResponse])
async def get_resume_optimizations(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Get all optimizations for a resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    optimizations = optimization_service.get_resume_optimizations(resume_id, db)

    return [
        ResumeOptimizationResponse(
            id=opt.id,
            resume_id=opt.resume_id,
            analysis_id=opt.analysis_id,
            job_description_id=opt.job_description_id,
            status=opt.status.value,
            original_summary=opt.original_summary,
            optimized_summary=opt.optimized_summary,
            original_skills=opt.original_skills,
            optimized_skills=opt.optimized_skills,
            original_experiences=opt.original_experiences,
            optimized_experiences=opt.optimized_experiences,
            original_projects=opt.original_projects,
            optimized_projects=opt.optimized_projects,
            original_education=opt.original_education,
            optimized_education=opt.optimized_education,
            original_ats_score=opt.original_ats_score,
            optimized_ats_score=opt.optimized_ats_score,
            ats_improvement=opt.ats_improvement,
            original_match_score=opt.original_match_score,
            optimized_match_score=opt.optimized_match_score,
            match_improvement=opt.match_improvement,
            optimization_notes=opt.optimization_notes,
            keyword_density_before=opt.keyword_density_before,
            keyword_density_after=opt.keyword_density_after,
            created_at=opt.created_at,
            completed_at=opt.completed_at
        )
        for opt in optimizations
    ]


@router.get("/{optimization_id}", response_model=ResumeOptimizationResponse)
async def get_optimization(
    optimization_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific optimization by ID"""
    optimization = optimization_service.get_optimization(optimization_id, db)
    if not optimization:
        raise HTTPException(status_code=404, detail="Optimization not found")

    return ResumeOptimizationResponse(
        id=optimization.id,
        resume_id=optimization.resume_id,
        analysis_id=optimization.analysis_id,
        job_description_id=optimization.job_description_id,
        status=optimization.status.value,
        original_summary=optimization.original_summary,
        optimized_summary=optimization.optimized_summary,
        original_skills=optimization.original_skills,
        optimized_skills=optimization.optimized_skills,
        original_experiences=optimization.original_experiences,
        optimized_experiences=optimization.optimized_experiences,
        original_projects=optimization.original_projects,
        optimized_projects=optimization.optimized_projects,
        original_education=optimization.original_education,
        optimized_education=optimization.optimized_education,
        original_ats_score=optimization.original_ats_score,
        optimized_ats_score=optimization.optimized_ats_score,
        ats_improvement=optimization.ats_improvement,
        original_match_score=optimization.original_match_score,
        optimized_match_score=optimization.optimized_match_score,
        match_improvement=optimization.match_improvement,
        optimization_notes=optimization.optimization_notes,
        keyword_density_before=optimization.keyword_density_before,
        keyword_density_after=optimization.keyword_density_after,
        created_at=optimization.created_at,
        completed_at=optimization.completed_at
    )


@router.get("/{optimization_id}/compare", response_model=OptimizationComparisonResponse)
async def compare_optimization_versions(
    optimization_id: int,
    db: Session = Depends(get_db)
):
    """Get side-by-side comparison of original vs optimized resume"""
    optimization = optimization_service.get_optimization(optimization_id, db)
    if not optimization:
        raise HTTPException(status_code=404, detail="Optimization not found")

    comparison = optimization_service.compare_versions(optimization)
    return OptimizationComparisonResponse(**comparison)


@router.post("/{optimization_id}/export-pdf")
async def export_optimized_resume_pdf(
    optimization_id: int,
    db: Session = Depends(get_db)
):
    """Export optimized resume as PDF"""
    from app.services.export_service import ExportService
    from fastapi.responses import StreamingResponse

    optimization = optimization_service.get_optimization(optimization_id, db)
    if not optimization:
        raise HTTPException(status_code=404, detail="Optimization not found")

    if optimization.status != OptimizationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Optimization not completed")

    # Build resume data for export
    resume_data = {
        "full_name": "Optimized Resume",
        "email": "",
        "phone": "",
        "skills": optimization.optimized_skills or [],
        "experiences": optimization.optimized_experiences or [],
        "projects": optimization.optimized_projects or [],
        "education": optimization.optimized_education or [],
        "summary": optimization.optimized_summary,
        "match_score": optimization.optimized_match_score or 0,
        "analysis": {
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": optimization.optimization_notes or []
        }
    }

    pdf_buffer = ExportService.generate_pdf(resume_data)

    return StreamingResponse(
        pdf_buffer,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=optimized-resume-{optimization_id}.pdf'}
    )