# AI Resume Analyzer - Project Review

## Project Structure Overview

```
Ai_Resume_Analyzer/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── resume_history.py
│   │   │   └── job_description.py
│   │   ├── schemas/
│   │   │   ├── resume_schema.py
│   │   │   └── job_description_schema.py
│   │   ├── routers/
│   │   │   ├── resume.py
│   │   │   ├── job_description.py
│   │   │   └── dashboard.py
│   │   ├── services/
│   │   │   ├── parser_service.py
│   │   │   ├── llm_analyzer.py
│   │   │   ├── resume_validation_service.py
│   │   │   ├── export_service.py
│   │   │   ├── job_description_service.py
│   │   │   └── dashboard_service.py
│   │   └── rag/
│   │       ├── vector_store.py
│   │       └── knowledge/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── AnalyzePage.jsx
│   │   │   ├── ResultPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── JobDescriptionsPage.jsx
│   │   │   └── JobDescriptionFormPage.jsx
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── ScoreCard.jsx
│   │   │   ├── SkillsRadar.jsx
│   │   │   ├── SuggestionList.jsx
│   │   │   └── Navbar.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── test/
├── data/
└── REVIEW_SYSTEM.md
```
## Architecture Overview

### Backend (FastAPI)
- **Framework**: FastAPI 0.104+ with Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **API Structure**: RESTful with 3 routers
  - /api - Resume parsing & analysis
  - /api/job-descriptions - JD management
  - /api/dashboard - Analytics & statistics
- **LLM**: Google Gemini 1.5 Flash via LangChain
- **RAG**: ChromaDB + Google Embeddings + BM25 Hybrid Search + Token Budget Management
- **Vector Store**: Semantic search + Keyword (BM25) hybrid retrieval
- **Context Window Management**: Token-aware context building for LLM
- **Validation**: Lenient mode (never rejects) with quality scoring metadata

### Core Features

#### 1. Resume Parsing (parser_service.py)
- **Supported formats**: PDF, DOCX, TXT
- **OCR Support**: Tesseract for scanned PDFs (Vietnamese + English)
- **Extracted info**: Name, Email, Phone, Skills, Experience, Education
- **Enhancements**:
  - **Name extraction**: Lenient - handles Title Case, UPPERCASE, lowercase, compound names, labeled fields
  - **Phone normalization**: E.164 format (+84xxxxxxxxx) with VN/US/intl support
  - **Email OCR handling**: Recovers @ from at and . from dot artifacts
  - **Password-protected PDF detection**: Graceful error with specific error code
  - **Section-aware extraction**: Skills/Experience sections detected via headers

#### 2. Resume Validation (resume_validation_service.py) - Lenient Mode
- **Philosophy**: Never rejects documents - accepts ALL for parsing
- **Returns**: Quality metadata for logging/debugging (not blocking)
- **ValidationResult Structure**:
  is_resume: bool = True (ALWAYS True)
  confidence: float = 1.0 (Quality score 0-1)
  reason: str = Document accepted
  error_code: str = None (Only for info, e.g., SHORT_DOCUMENT)
  details: Dict = None (Rich metadata)
- **Quality Scores** (in metadata):
  - contact_info (0-1): Email, phone, LinkedIn, address detection
  - cv_sections (0-1): Standard CV sections found
  - experience_education (0-1): Dates, universities, job titles, companies
  - structure (0-1): Bullet points, paragraphs, headers
  - detected_sections: List of found section names
  - has_contact: Boolean
- **API Response includes** validation metadata with confidence and details

#### 3. LLM Analysis (llm_analyzer.py) - Enhanced with RAG & Context Management
- **Provider**: Google Gemini 1.5 Flash (temperature=0.2)
- **Structured Output**: Pydantic AnalysisResult with fields:
  - overall_score (0-100), ats_score (0-100)
  - strengths (4-6), weaknesses (3-5)
  - skill_gaps, suggestions (actionable)
  - match_score (vs JD)
- **RAG Integration**: Retrieves relevant knowledge from ChromaDB + BM25
- **Context Window Management**:
  - Token budget: 3000 default, 500 reserved
  - Auto-calculates available tokens after resume + JD
  - Truncates RAG context using tiktoken (cl100k_base)
  - Logs token budget for debugging

#### 4. RAG System (rag/vector_store.py) - Enhanced Hybrid Search + Knowledge Base
- **Vector DB**: ChromaDB with Google Generative AI Embeddings (embedding-001)
- **Hybrid Retrieval**: 50% Semantic (Chroma) + 50% Keyword (BM25) via EnsembleRetriever
- **Knowledge Base**: 6 Markdown files in backend/app/rag/knowledge/:
  | File | Category | Priority | Key Topics |
  |------|----------|----------|------------|
  | cv_best_practices.md | cv_best_practices | high | Structure, STAR method, IT skills 2024-25 |
  | ats_optimization.md | ats_optimization | high | ATS parsing, formatting rules, keyword strategy |
  | job_market_trends.md | job_market_trends | high | AI/ML, Cloud, Data, Security trends 2024-25 |
  | interview_preparation.md | interview_preparation | medium | STAR method, behavioral, system design, red flags |
  | skill_gap_analysis.md | skill_gap_analysis | high | Competency matrix, gap analysis, 70-20-10 learning |
  | salary_negotiation.md | salary_negotiation | medium | Total comp, equity, negotiation framework, VN context |
  | vietnam_job_market.md | vietnam_job_market | high | VN salaries, companies, skills, tax, hiring channels |
- **Document Processing**:
  - YAML frontmatter support (category, tags, priority, source)
  - RecursiveCharacterTextSplitter (chunk_size=500, overlap=100)
  - Metadata preserved for filtering/stats
- **Token Budget Management** (get_context()):
  available_tokens = max_context_tokens - resume_tokens - jd_tokens - RESERVED_TOKENS
- **Stats API**: get_stats() returns document count, categories, embeddings model

#### 5. Export Service (export_service.py)
- **PDF Export** (ReportLab): Professional report with header, CV info, JD info, scores, skills, matched/missing keywords, suggestions
- **Excel Export** (openpyxl): Multi-sheet: Overview, Skills, Matched Keywords, Missing Keywords, Suggestions
- **API Endpoints**:
  - GET /api/history/{id}/export/pdf
  - GET /api/history/{id}/export/excel

#### 6. Dashboard & Analytics (dashboard_service.py)
- **Summary Stats**: Total resumes, average match score
- **Score Distribution**: 5 buckets (0-20, 21-40, 41-60, 61-80, 81-100) with counts & percentages
- **Top Skills**: Normalized skill counting across resumes
  - **Skill Normalization Map**:
    JS, JAVASCRIPT -> JavaScript
    REACT.JS, REACTJS -> React
    VUE.JS, VUEJS -> Vue
    NODE.JS, NODEJS -> Node.js
    POSTGRES, POSTGRESQL -> PostgreSQL
  - Deduplicates per resume, shows percentage of resumes with skill
- **Date Filtering**: Optional date_from / date_to query params
- **API Endpoints**:
  - GET /api/dashboard/stats
  - GET /api/dashboard/skills-trend
  - GET /api/dashboard/score-distribution

#### 7. Job Description Management (job_description.py)
- **CRUD**: Create, List, Update, Delete, Archive, Duplicate
- **Fields**: title, company, description, requirements, location, job_level, employment_type, salary_range
- **Archive/Restore**: Soft delete via is_archived flag
- **Duplicate**: Clone existing JD for similar roles
### Frontend (React 19 + Vite)
- **Routing**: React Router v7
- **Styling**: Bootstrap 5 + Custom CSS
- **Charts**: Recharts (Radar, Bar charts)
- **State**: React hooks (useState, useContext)
- **API**: Axios with interceptors

### Pages
| Path | Component | Description |
|------|-----------|-------------|
| / | HomePage | Landing page |
| /analyze | AnalyzePage | Upload CV + JD, run analysis |
| /result/:id | ResultPage | Detailed analysis results |
| /dashboard | DashboardPage | Statistics & charts |
| /job-descriptions | JobDescriptionsPage | JD management |
| /job-descriptions/new | JobDescriptionFormPage | Create/edit JD |
## Key Dependencies

### Backend
fastapi, uvicorn, sqlalchemy, pydantic, pymupdf, python-docx, pytesseract, pillow, langchain-google-genai, chromadb, langchain-community, reportlab, openpyxl, tiktoken, pyyaml

### Frontend
react@19, react-dom@19, react-router-dom@7, axios, bootstrap@5, recharts@3

## Environment Variables (.env)
DATABASE_URL=sqlite:///./resume_history.db
GEMINI_API_KEY=your_gemini_api_key
CHROMA_DB_PATH=./chroma_db

## Running the Project

### Backend
cd backend
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend
cd frontend
npm install
npm run dev
## API Endpoints Summary

### Resume API (/api)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /parse-resume | Upload & analyze CV (returns validation metadata + analysis) |
| GET | /history | List analysis history |
| GET | /history/{id}/export/pdf | Export PDF report |
| GET | /history/{id}/export/excel | Export Excel report |

### Job Description API (/api/job-descriptions)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | List all JDs (supports ?include_archived=true) |
| POST | / | Create new JD |
| PUT | /{id} | Update JD |
| DELETE | /{id} | Delete JD |
| POST | /{id}/archive | Archive JD (soft delete) |
| POST | /{id}/restore | Restore archived JD |
| POST | /{id}/duplicate | Duplicate JD |

### Dashboard API (/api/dashboard)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /stats | Overall statistics (total, avg score) |
| GET | /skills-trend | Top skills with normalization & percentages |
| GET | /score-distribution | Score distribution in 5 buckets (counts + %) |
## Service Deep Dives

### Resume Validation Service (Lenient Mode)
Never rejects - always returns is_resume=True with confidence and details:
confidence: 0.85, details: { text_length: 2500, quality_scores: {...}, detected_sections: [...], has_contact: true }

### Parser Service - Key Improvements
- Phone: E.164 normalization (+84xxxxxxxxx, +1xxxxxxxxxx)
- Email: OCR artifact recovery (@ from at, . from dot)
- Name: Multi-format (Title Case, UPPER, lower, labeled, compound)
- Skills: Section-aware + full-text fallback
- Experience: STAR bullet parsing, date range extraction

### LLM Analyzer with RAG & Context Management
1. Build query from resume + JD
2. Hybrid retrieve (semantic + BM25) from ChromaDB
3. Build context with token budget (3000 default - resume - JD - 500 reserved)
4. Inject into prompt as Senior Technical Recruiter context
5. Structured JSON output via Pydantic parser

### RAG Vector Store - Hybrid Search & Token Budget
Hybrid retrieval (50/50 semantic + keyword): docs = rag.retrieve(query, k=5, use_hybrid=True)
Context building with token budget: context = rag.get_context(query=..., resume_text=..., job_description=..., max_context_tokens=3000, use_hybrid=True)
Logs: Token budget: 1200 for RAG context (resume: 800, JD: 500)

### Export Service
PDF: pdf_buffer = ExportService.generate_pdf(analysis_data)
Excel: excel_buffer = ExportService.generate_excel_single(analysis_data)

### Dashboard Service - Skill Normalization
Normalizes variants: normalize_skill(REACT.JS) -> React, normalize_skill(JS) -> JavaScript
Top skills example: skill=Python, resume_count=45, percentage=78.5
## Knowledge Base Files (RAG)
Located in backend/app/rag/knowledge/ (6 files, ~27KB total):
1. cv_best_practices.md - IT CV structure, STAR method, 2024-25 skill highlights
2. ats_optimization.md - ATS parsing behavior by vendor, formatting rules, keyword strategy
3. job_market_trends.md - AI/ML, Cloud, Data, Security trends; hiring patterns; salary signals
4. interview_preparation.md - STAR behavioral, system design, technical categories, red flags
5. skill_gap_analysis.md - Competency matrix by level, 70-20-10 learning, priority matrix
6. salary_negotiation.md - Total comp components, negotiation framework, VN market context
7. vietnam_job_market.md - VN company tiers, salary bands, skills demand, hiring channels, tax/legal

Each file has YAML frontmatter with category, tags, source, priority.
RAG uses category, priority, tags for potential filtering (currently all loaded).

### RAG Document Flow
1. Load: load_knowledge_base() reads all .md files recursively
2. Parse: YAML frontmatter extracted to metadata
3. Split: 500 char chunks with 100 overlap
4. Embed: Google embedding-001 -> ChromaDB
5. Index: BM25 built from same chunks
6. Retrieve: EnsembleRetriever (0.5/0.5 weights)
7. Context Budget: Token-aware truncation for LLM

## Code Quality Observations

### Strengths
1. Modular Architecture: Clear separation (models, schemas, routers, services, rag)
2. Lenient Validation: Never blocks users, provides rich quality metadata
3. Multi-format Support: PDF, DOCX, TXT with OCR fallback
4. Advanced RAG: Hybrid search (semantic + BM25) + token budget management
5. Knowledge Base: 6 curated markdown files with frontmatter metadata
6. Context Window Management: Tiktoken-aware truncation for LLM efficiency
7. Export Features: Professional PDF & Excel reports
8. Dashboard Analytics: Skill normalization, score distributions, date filtering
9. Phone/Email Normalization: E.164 phones, OCR-resistant email parsing
10. JD Management: Full CRUD + archive/duplicate
11. Frontend-Backend Separation: Independent deployable services

### Areas for Improvement
1. Error Handling: Some try-catch blocks too broad (catch Exception)
2. Type Hints: Inconsistent annotations across services
3. Testing: Limited coverage (only test_validation.py exists)
4. Authentication: No auth/authorization implemented
5. Rate Limiting: No API rate limiting
6. Async/Await: Some services not fully async (parser, export)
7. Logging: Uses print() instead of structured logging (structlog/loguru)
8. Database Migrations: No Alembic setup
9. PDF Generation: Minor bug - jd_table variable typo
10. Knowledge Base: No hot-reload on file changes (requires restart/rebuild_index)

## Recommended Next Steps

### High Priority
- Add authentication (JWT/OAuth)
- Implement API rate limiting
- Add structured logging (structlog/loguru)
- Set up Alembic for DB migrations
- Write unit/integration tests (target >80% coverage)
- Fix PDF export variable name bug (jd_table vs jd_table)

### Medium Priority
- Improve async support in parser_service & export_service
- Add input sanitization/validation middleware
- Implement Redis caching for frequent queries (dashboard, RAG)
- Enhance OpenAPI documentation with examples
- Add knowledge base hot-reload / file watcher

### Low Priority
- Frontend TypeScript migration
- CI/CD pipeline (GitHub Actions)
- Docker compose for full stack
- Unit test coverage >80%
- Skill taxonomy versioning in RAG knowledge base

## Related Files
- REVIEW_SYSTEM.md - System architecture review
- test_validation.py - Validation service tests
- backend/.env.example - Environment template
- backend/app/rag/vector_store.py - RAG implementation with hybrid search
- backend/app/services/llm_analyzer.py - LLM with context management
- backend/app/services/parser_service.py - Enhanced extraction (phone E.164, email OCR, name)
- backend/app/services/resume_validation_service.py - Lenient validator
- backend/app/services/export_service.py - PDF/Excel generation
- backend/app/services/dashboard_service.py - Analytics with skill normalization
- backend/app/routers/resume.py - Main API with validation metadata
- backend/app/rag/knowledge/*.md (6 files) - Knowledge base

---
Updated: 2026-07-26
Project: AI Resume Analyzer