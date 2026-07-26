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
from datetime import datetime
import json
import os

router = APIRouter(prefix='/api', tags=['resume'])
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']

# Initialize validator
validator = ResumeValidator()


@router.post('/parse-resume')
async def parse_resume(
        file: UploadFile = File(...),
        job_description: Optional[str] = Form(None),
        db: Session = Depends(get_db)
):
    # 1. Kiểm tra định dạng file
    filename_lower = file.filename.lower()
    if not any(filename_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail='Chỉ hỗ trợ file PDF, DOCX và TXT')

    # 2. Đọc nội dung và kiểm tra dung lượng
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail='Kích thước file vượt quá giới hạn 5MB')

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

        # Lưu vào SQLite
        history = ResumeHistory(
            filename=file.filename,
            full_name=resume_data.full_name,
            email=resume_data.email,
            phone=resume_data.phone,
            skills=json.dumps(resume_data.skills),
            experiences=json.dumps([exp.model_dump() for exp in resume_data.experiences]),
            match_score=analysis.match_score
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
                'history_id': history.id
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
