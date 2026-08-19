from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.resume_schema import Resume, ResumeAnalysis, ResumeResponse, ValidationErrorResponse
from app.services.parser_service import parse_resume_file, analyze_resume_against_job, _extract_text
from app.services.resume_validation_service import ResumeValidator
from app.services.export_service import ExportService
from app.database import get_db
from app.models.resume_history import ResumeHistory
from app.models.resumes import Resume, ResumeStatus
from app.models.analyses import Analysis
from app.models.job_description import JobDescription
from app.models.skills import Skill
from app.models.resume_skills import ResumeSkill
from app.models.work_experiences import WorkExperience
from datetime import datetime
import json
import os
import re

router = APIRouter(prefix='/api', tags=['resume'])
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg']

# Initialize validator
validator = ResumeValidator()


def _parse_date_range(dates_str: str):
    """Parse a date string like '01/2020 - 06/2022' or '2018-2020' into start/end datetimes."""
    if not dates_str:
        return None, None
    matches = re.findall(r"(\d{1,2})[\/\-\.](\d{4})", dates_str)
    start = None
    end = None
    if len(matches) >= 1:
        try:
            start = datetime(int(matches[0][1]), int(matches[0][0]), 1)
        except ValueError:
            start = None
    if len(matches) >= 2:
        try:
            end = datetime(int(matches[1][1]), int(matches[1][0]), 1)
        except ValueError:
            end = None
    if not start:
        m = re.search(r"(\d{4})", dates_str or "")
        if m:
            try:
                start = datetime(int(m.group(1)), 1, 1)
            except ValueError:
                start = None
    return start, end


def _persist_resume_analysis(db: Session, resume_data, analysis, filename: str, job_description: Optional[str]):
    """Create Resume + Analysis + JD + Skills records so optimization & skill-gaps work."""
    # 1. Resume record
    resume = Resume(
        user_id=None,
        file_name=filename,
        file_path=filename,
        file_size=0,
        mime_type="application/octet-stream",
        parsed_text=f"Resume of {resume_data.full_name or 'Unknown'}",
        status=ResumeStatus.COMPLETED,
    )
    db.add(resume)
    db.flush()

    # 2. Job description record (if text provided)
    jd = None
    if job_description and job_description.strip():
        from app.services.parser_service import _extract_skills
        jd = JobDescription(
            title=(job_description.strip().splitlines()[0][:200] or "Job Description"),
            raw_text=job_description,
            extracted_keywords=json.dumps(_extract_skills(job_description), ensure_ascii=False),
            status="active",
        )
        db.add(jd)
        db.flush()

    # 3. Analysis record
    analysis_record = Analysis(
        resume_id=resume.id,
        job_description_id=jd.id if jd else None,
        match_score=analysis.match_score,
        skills_match=analysis.matched_skills or [],
        missing_skills=analysis.missing_skills or [],
        recommendations="\n".join(analysis.suggestions or []),
        strengths=None,
        weaknesses=None,
    )
    db.add(analysis_record)
    db.flush()

    # 4. Skills catalog + resume_skills links
    for skill_name in resume_data.skills:
        skill = db.query(Skill).filter(Skill.name == skill_name).first()
        if not skill:
            skill = Skill(name=skill_name)
            db.add(skill)
            db.flush()
        rs = ResumeSkill(resume_id=resume.id, skill_id=skill.id)
        db.add(rs)

    # 5. Work experiences from parsed data
    for exp in resume_data.experiences:
        start, end = _parse_date_range(exp.dates)
        is_current = "false"
        if exp.dates and re.search(r"nay|present|now|hi[eệ]n\s*t[aạ]i", exp.dates, re.IGNORECASE):
            is_current = "true"
        if end is None and re.search(r"\d{4}\s*-\s*(\d{4})", exp.dates or ""):
            is_current = "false"
        we = WorkExperience(
            resume_id=resume.id,
            company=exp.company or "Unknown",
            position=exp.position or "Unknown",
            start_date=start,
            end_date=end,
            is_current=is_current,
            description="\n".join(exp.bullets or []),
            achievements=json.dumps(exp.bullets or [], ensure_ascii=False),
        )
        db.add(we)

    db.commit()
    return resume.id, analysis_record.id, jd.id if jd else None


@router.post('/parse-resume')
async def parse_resume(
        file: UploadFile = File(...),
        job_description: Optional[str] = Form(None),
        db: Session = Depends(get_db)
):
    # 1. Kiểm tra định dạng file
    filename_lower = file.filename.lower()
    if not any(filename_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail='Chỉ hỗ trợ file PDF, DOCX, TXT, PNG, JPG, JPEG')

    # 2. Đọc nội dung file
    content = await file.read()

    try:
        # 3. Extract text for validation metadata
        text = _extract_text(content, file.filename)

        # 4. Validate for metadata (lenient - never rejects)
        validation_result = validator.validate(text)

        # 5. Phân tích CV - always parse regardless of validation
        resume_data = parse_resume_file(content, file.filename)

        # Tính toán match score động (sử dụng AI nếu cấu hình API Key)
        if os.getenv('GEMINI_API_KEY') and job_description:
            try:
                from app.services.llm_analyzer import LLMAnalyzer
                llm_analyzer = LLMAnalyzer()
                llm_result = await llm_analyzer.analyze(text, job_description)
                analysis = ResumeAnalysis(
                    match_score=llm_result.match_score if llm_result.match_score is not None else llm_result.overall_score,
                    matched_skills=resume_data.skills,
                    missing_skills=llm_result.skill_gaps,
                    suggestions=llm_result.suggestions,
                    ats_score=llm_result.ats_score,
                    strengths=llm_result.strengths
                )
            except Exception as e:
                print(f'LLM Analyzer Error, falling back to local: {e}')
                analysis = analyze_resume_against_job(resume_data, job_description)
        else:
            analysis = analyze_resume_against_job(resume_data, job_description)

        resume_data.analysis = analysis

        # Lưu vào database (history + resume + analysis + skills...)
        resume_id, analysis_id, jd_id = _persist_resume_analysis(
            db, resume_data, analysis, file.filename, job_description
        )
        history = ResumeHistory(
            filename=file.filename,
            full_name=resume_data.full_name,
            email=resume_data.email,
            phone=resume_data.phone,
            skills=json.dumps(resume_data.skills),
            experiences=json.dumps([exp.model_dump() for exp in resume_data.experiences]),
            match_score=analysis.match_score,
            job_description_id=jd_id,
            job_description_snapshot=json.dumps({"raw_text": job_description}) if job_description else None,
            resume_id=resume_id,
            analysis_id=analysis_id
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        # Return wrapped response with validation metadata
        return JSONResponse(
            status_code=200,
            content={
                'success': True,
                'validation': {
                    'is_resume': validation_result.is_resume,
                    'confidence': round(validation_result.confidence, 2),
                    'details': validation_result.details
                },
                'data': resume_data.model_dump(),
                'history_id': history.id,
                'resume_id': resume_id,
                'analysis_id': analysis_id
            }
        )

    except ValueError as ve:
        # Bắt các lỗi ném ra từ parser_service (VD: sai pass, hỏng file)
        error_message = str(ve)

        # Map specific errors to appropriate error codes
        if 'mật khẩu' in error_message.lower() or 'password' in error_message.lower():
            error_code = 'PASSWORD_PROTECTED_FILE'
        elif 'hỏng' in error_message.lower() or 'corrupted' in error_message.lower():
            error_code = 'CORRUPTED_FILE'
        elif 'không thể đọc' in error_message.lower() or 'unreadable' in error_message.lower():
            error_code = 'UNREADABLE_DOCUMENT'
        else:
            error_code = 'INVALID_FILE'

        return JSONResponse(
            status_code=422,
            content={
                'success': False,
                'error_code': error_code,
                'message': error_message
            }
        )
    except Exception as e:
        print(f'Lỗi Server: {e}')
        return JSONResponse(
            status_code=500,
            content={
                'success': False,
                'message': 'Đã xảy ra lỗi trong quá trình xử lý file.'
            }
        )

# lịch sữ lưu database
@router.get('/history')
async def get_history(db: Session = Depends(get_db)):
    '''API xem lịch sử phân tích'''
    histories = db.query(ResumeHistory).order_by(ResumeHistory.created_at.desc()).all()
    return [
        {
            'id': h.id,
            'filename': h.filename,
            'full_name': h.full_name,
            'email': h.email,
            'skills': json.loads(h.skills) if h.skills else [],
            'match_score': h.match_score,
            'resume_id': h.resume_id,
            'analysis_id': h.analysis_id,
            'created_at': h.created_at
        }
        for h in histories
    ]


@router.get('/history/{id}/export/pdf')
async def export_pdf(id: int, db: Session = Depends(get_db)):
    '''Export analysis result as PDF'''
    history = db.query(ResumeHistory).filter(ResumeHistory.id == id).first()
    if not history:
        raise HTTPException(status_code=404, detail='Resume analysis not found')

    # Prepare analysis data
    analysis_data = {
        'filename': history.filename,
        'full_name': history.full_name,
        'email': history.email,
        'phone': history.phone,
        'skills': json.loads(history.skills) if history.skills else [],
        'experiences': json.loads(history.experiences) if history.experiences else [],
        'match_score': history.match_score,
        'created_at': history.created_at.strftime('%Y-%m-%d %H:%M') if history.created_at else 'N/A',
        'job_description_snapshot': json.loads(history.job_description_snapshot) if history.job_description_snapshot else None,
        'analysis': {
            'matched_skills': [],
            'missing_skills': [],
            'suggestions': []
        }
    }

    # Generate PDF
    pdf_buffer = ExportService.generate_pdf(analysis_data)

    # Create filename
    safe_name = history.full_name.replace(' ', '-').replace('/', '-')
    filename = f'resume-analysis-{safe_name}-{datetime.now().strftime("%Y%m%d-%H%M")}.pdf'

    return StreamingResponse(
        pdf_buffer,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@router.get('/history/{id}/export/excel')
async def export_excel(id: int, db: Session = Depends(get_db)):
    '''Export analysis result as Excel'''
    history = db.query(ResumeHistory).filter(ResumeHistory.id == id).first()
    if not history:
        raise HTTPException(status_code=404, detail='Resume analysis not found')

    # Prepare analysis data
    analysis_data = {
        'filename': history.filename,
        'full_name': history.full_name,
        'email': history.email,
        'phone': history.phone,
        'skills': json.loads(history.skills) if history.skills else [],
        'experiences': json.loads(history.experiences) if history.experiences else [],
        'match_score': history.match_score,
        'created_at': history.created_at.strftime('%Y-%m-%d %H:%M') if history.created_at else 'N/A',
        'job_description_snapshot': json.loads(history.job_description_snapshot) if history.job_description_snapshot else None,
        'analysis': {
            'matched_skills': [],
            'missing_skills': [],
            'suggestions': []
        }
    }

    # Generate Excel
    excel_buffer = ExportService.generate_excel_single(analysis_data)

    # Create filename
    safe_name = history.full_name.replace(' ', '-').replace('/', '-')
    filename = f'resume-analysis-{safe_name}-{datetime.now().strftime("%Y%m%d-%H%M")}.xlsx'

    return StreamingResponse(
        excel_buffer,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
