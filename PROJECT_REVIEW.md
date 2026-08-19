# AI Resume Analyzer - Project Review

## Project Structure Overview

```
Ai_Resume_Analyzer/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── analysis.py
│   │   │   ├── certification.py
│   │   │   ├── education.py
│   │   │   ├── job_description.py
│   │   │   ├── job_seeker.py
│   │   │   ├── project.py
│   │   │   ├── resume.py
│   │   │   ├── resume_history.py
│   │   │   ├── resume_skill.py
│   │   │   ├── skill.py
│   │   │   ├── user.py
│   │   │   ├── work_experience.py
│   │   │   └── __init__.py
│   │   ├── auth/
│   │   │   ├── dependencies.py
│   │   │   ├── jwt.py
│   │   │   ├── password.py
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── resume.py
│   │   │   ├── job_description.py
│   │   │   ├── dashboard.py
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── auth_schema.py
│   │   │   ├── extraction_schema.py
│   │   │   ├── job_description_schema.py
│   │   │   ├── resume_schema.py
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── analysis_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── export_service.py
│   │   │   ├── job_description_service.py
│   │   │   ├── llm_analyzer.py
│   │   │   ├── parser_service.py
│   │   │   ├── resume_persistence_service.py
│   │   │   ├── resume_validation_service.py
│   │   │   └── __init__.py
│   │   ├── rag/
│   │   │   ├── vector_store.py
│   │   │   ├── knowledge/
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── .venv/
│   ├── requirements.txt
│   ├── .env
│   └── test_extract.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── analysis/
│   │   │   ├── common/
│   │   │   ├── cv/
│   │   │   ├── forms/
│   │   │   ├── jd/
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Header.css
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Sidebar.css
│   │   │   └── ui/
│   │   │       ├── Alert.jsx / Alert.css
│   │   │       ├── Badge.jsx / Badge.css
│   │   │       ├── Button.jsx / Button.css
│   │   │       ├── Card.jsx / Card.css
│   │   │       ├── EmptyState.jsx / EmptyState.css
│   │   │       ├── Input.jsx / Input.css
│   │   │       ├── LoadingSpinner.jsx / LoadingSpinner.css
│   │   │       ├── Modal.jsx / Modal.css
│   │   │       ├── Pagination.jsx / Pagination.css
│   │   │       ├── ProgressBar.jsx / ProgressBar.css
│   │   │       ├── ScoreCard.jsx / ScoreCard.css
│   │   │       ├── Select.jsx / Select.css
│   │   │       ├── SkillsRadar.jsx / SkillsRadar.css
│   │   │       ├── SuggestionList.jsx / SuggestionList.css
│   │   │       ├── Tabs.jsx / Tabs.css
│   │   │       ├── Tooltip.jsx / Tooltip.css
│   │   │       └── index.js
│   │   │   ├── FileUpload.jsx
│   │   │   └── Navbar.jsx
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx
│   │   ├── hooks/
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   │   ├── AuthPage.css
│   │   │   │   ├── LoginPage.jsx
│   │   │   │   └── RegisterPage.jsx
│   │   │   ├── AnalyzePage.jsx / AnalyzePage.css
│   │   │   ├── AnalyzeResultPage.jsx
│   │   │   ├── ComparePage.jsx / ComparePage.css
│   │   │   ├── CompareResultPage.jsx
│   │   │   ├── DashboardPage.jsx / DashboardPage.css
│   │   │   ├── HomePage.jsx
│   │   │   ├── JobDescriptionDetailPage.jsx
│   │   │   ├── JobDescriptionFormPage.jsx
│   │   │   ├── JobDescriptionsPage.jsx
│   │   │   ├── ResumeDetailPage.jsx
│   │   │   ├── ResumeImportPage.jsx
│   │   │   ├── ResumeListPage.jsx
│   │   │   ├── AnalysisHistoryPage.jsx
│   │   │   ├── ResultPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── theme/
│   │   │   ├── ThemeProvider.jsx
│   │   │   └── tokens.js
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── node_modules/
│   ├── public/
│   ├── dist/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── index.html
│   ├── .gitignore
│   ├── .oxlintrc.json
│   └── README.md
├── data/
│   ├── db.sql
│   └── sample_cvs/
├── test/
├── .venv/
├── .git/
├── PROJECT_REVIEW.md
├── NEW_UI_DESIGN_REQUIREMENTS.md
├── REVIEW_SYSTEM.md
├── test_pg.py
└── test_main.http
```
## Architecture Overview

### Backend (FastAPI)
- **Framework**: FastAPI 0.104+ with Uvicorn
- **Database**: PostgreSQL with SQLAlchemy ORM (11 tables, full FK constraints)
- **API Structure**: RESTful with 4 routers
  - `/api/auth` - Authentication (register, login, JWT)
  - `/api` - Resume parsing & analysis
  - `/api/job-descriptions` - JD management
  - `/api/dashboard` - Analytics & statistics
- **LLM**: Google Gemini 1.5 Flash via LangChain (temperature=0.2)
- **RAG**: ChromaDB + Google Embeddings (embedding-001) + BM25 Hybrid Search + Token Budget Management
- **Vector Store**: Semantic search + Keyword (BM25) hybrid retrieval via EnsembleRetriever (50/50 weights)
- **Context Window Management**: Token-aware context building for LLM (tiktoken cl100k_base)
- **Validation**: Lenient mode (never rejects) with quality scoring metadata
- **Authentication**: JWT tokens with refresh support, bcrypt password hashing

### Frontend (React 19 + Vite + Modern Architecture)
Modern React application with:
- React 19 + Vite 5
- React Router v7 for routing
- Context-based state management (Theme, Auth)
- CSS Custom Properties for theming (design tokens system)
- Bootstrap 5 (utility) + Custom design system
- Recharts 3 for data visualization
- Axios with interceptors for API
- React Hot Toast for notifications
- clsx for conditional classNames

### Database (PostgreSQL)
PostgreSQL database with 11 tables:
| Table | Description |
|-------|-------------|
| users | User accounts with roles |
| job_seekers | Candidate profiles |
| resumes | Resume documents & metadata |
| education | Education history |
| work_experiences | Work experience entries |
| projects | Project portfolio |
| certifications | Certifications |
| skills | Skills catalog |
| resume_skills | Resume-Skill many-to-many |
| job_descriptions | Job postings |
| analyses | Analysis results (standalone + comparison) |

Full foreign key constraints with CASCADE/SET NULL behaviors.

---

## Core Features

### 1. Resume Parsing (parser_service.py)
- **Supported formats**: PDF, DOCX, TXT
- **OCR Support**: Tesseract for scanned PDFs (Vietnamese + English)
- **Extracted info**: Name, Email, Phone, Skills, Experience, Education
- **Enhancements**:
  - **Name extraction**: Lenient - handles Title Case, UPPERCASE, lowercase, compound names, labeled fields
  - **Phone normalization**: E.164 format (+84xxxxxxxxx) with VN/US/intl support
  - **Email OCR handling**: Recovers @ from "at" and . from "dot" artifacts
  - **Password-protected PDF detection**: Graceful error with specific error code
  - **Section-aware extraction**: Skills/Experience sections detected via headers

### 2. Resume Validation (resume_validation_service.py) - Lenient Mode
- **Philosophy**: Never rejects documents - accepts ALL for parsing
- **Returns**: Quality metadata for logging/debugging (not blocking)
- **ValidationResult Structure**:
  - is_resume: bool = True (ALWAYS True)
  - confidence: float = 1.0 (Quality score 0-1)
  - reason: str = Document accepted
  - error_code: str = None (Only for info, e.g., SHORT_DOCUMENT)
  - details: Dict = None (Rich metadata)
- **Quality Scores** (in metadata):
  - contact_info (0-1): Email, phone, LinkedIn, address detection
  - cv_sections (0-1): Standard CV sections found
  - experience_education (0-1): Dates, universities, job titles, companies
  - structure (0-1): Bullet points, paragraphs, headers
  - detected_sections: List of found section names
  - has_contact: Boolean
- **API Response includes** validation metadata with confidence and details

### 3. LLM Analysis (llm_analyzer.py) - Enhanced with RAG & Context Management
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

### 4. RAG System (rag/vector_store.py) - Enhanced Hybrid Search + Knowledge Base
- **Vector DB**: ChromaDB with Google Generative AI Embeddings (embedding-001)
- **Hybrid Retrieval**: 50% Semantic (Chroma) + 50% Keyword (BM25) via EnsembleRetriever
- **Knowledge Base**: 7 Markdown files in `backend/app/rag/knowledge/`:
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

### 5. Export Service (export_service.py)
- **PDF Export** (ReportLab): Professional report with header, CV info, JD info, scores, skills, matched/missing keywords, suggestions
- **Excel Export** (openpyxl): Multi-sheet: Overview, Skills, Matched Keywords, Missing Keywords, Suggestions
- **API Endpoints**:
  - GET `/api/analyses/{id}/export/pdf`
  - GET `/api/analyses/{id}/export/excel`

### 6. Dashboard & Analytics (dashboard_service.py)
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
  - GET `/api/dashboard/summary`
  - GET `/api/dashboard/score-distribution`
  - GET `/api/dashboard/top-skills`

### 7. Job Description Management (job_description.py router)
- **CRUD**: Create, List, Get, Update, Delete
- **Fields**: title, company, description, requirements, location, job_level, employment_type, salary_range
- **Archive/Restore**: Soft delete via is_archived flag
- **Duplicate**: Clone existing JD for similar roles
- **Mark Used**: Track JD usage for analytics

### 8. Authentication System (auth/)
- **Register**: Email, username, phone, password (with strength validation), terms agreement
- **Login**: Email/password, remember me option
- **JWT**: Access tokens with refresh token support
- **Password**: bcrypt hashing, strength requirements (8+ chars, upper, lower, digit)
- **Protected Routes**: Frontend ProtectedRoute component with auth context

### 9. Analysis History
- **Storage**: All analyses saved to PostgreSQL (analysis_id, resume_id, jdid, scores, strengths, weaknesses, keywords, suggestions)
- **Filtering**: By type (standalone vs comparison), date range, score range
- **Re-run**: Re-execute analysis with same parameters
- **Export**: PDF/Excel export per analysis

---

## Frontend Pages & Components

### Pages
| Path | Component | Description |
|------|-----------|-------------|
| /login | LoginPage | Email/password login, remember me, forgot password |
| /register | RegisterPage | Username, email, phone, password, confirm, terms |
| /dashboard | DashboardPage | KPIs, charts, recent CVs/JDs/analyses, quick actions |
| /resumes | ResumeListPage | Search, filter, sort, table view, actions |
| /resumes/import | ResumeImportPage | Drag-drop upload, JD optional, validation preview, review extracted data |
| /resumes/:id | ResumeDetailPage | Full resume view with all sections |
| /job-descriptions | JobDescriptionsPage | Grid/list, search, filter, archive/duplicate |
| /job-descriptions/new | JobDescriptionFormPage | Create/edit JD with all fields |
| /job-descriptions/:id | JobDescriptionDetailPage | JD view with comparisons |
| /analyze | AnalyzePage | Select saved CV, standalone AI analysis |
| /compare | ComparePage | Select CV + JD, AI comparison |
| /analyze-result/:id | AnalyzeResultPage | Detailed standalone analysis result |
| /compare-result/:id | CompareResultPage | Detailed comparison result |
| /analysis-history | AnalysisHistoryPage | Search, filter, sort, re-run, export |
| /settings | SettingsPage | Theme, account, notifications |

### Layout Components
- **Header**: Logo, desktop nav, mobile hamburger, theme toggle, user menu (settings, logout)
- **Sidebar**: Collapsible navigation, brand, nav links with active state, theme toggle, user avatar, logout
- **Responsive**: Mobile drawer overlay, desktop persistent sidebar

### UI Components (Design System)
- **Button**: Variants (primary, secondary, outline, ghost, danger), sizes, loading state, fullWidth
- **Card**: Header, Body, Footer, hoverable, bordered
- **Input**: Label, error/success states, icons, password toggle
- **Select**: Searchable, multi-select, grouped options
- **Badge**: Variants (default, primary, success, warning, error, info), sizes, dot indicator
- **Modal**: Portal, overlay, focus trap, ESC to close, sizes
- **ProgressBar**: Variants, sizes, striped, animated, label
- **LoadingSpinner**: Sizes, inline/overlay
- **Alert**: Variants, dismissible, actions
- **Pagination**: Page numbers, prev/next, page size selector
- **ScoreCard**: Score with color coding (excellent/good/moderate/weak), label
- **SkillsRadar**: Recharts radar chart for skill visualization
- **SuggestionList**: Priority-grouped actionable suggestions
- **Tabs**: Keyboard accessible, animated indicator
- **Tooltip**: Positions, hover/focus trigger
- **EmptyState**: Icon, title, description, action button
- **Tooltip**: Positions, hover/focus trigger
- **ProtectedRoute**: Auth guard with redirect

### Theme System
- **Design Tokens** (`theme/tokens.js`): Colors (primary, secondary, semantic, score), spacing, typography, borderRadius, shadows, transitions, breakpoints, z-indices
- **Light/Dark/System Themes**: Complete token sets for each
- **CSS Variables Generator**: Auto-generates CSS custom properties
- **Persistence**: localStorage + system preference detection
- **Score Colors**: Excellent (80-100 green), Good (60-79 blue), Moderate (40-59 amber), Weak (0-39 red) - with text labels for accessibility

---

## API Endpoints Summary

### Auth (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /register | Register new user (returns JWT) |
| POST | /login | Login (returns JWT) |
| GET | /me | Get current user profile |
| POST | /refresh | Refresh access token |
| POST | /forgot-password | Request password reset |
| POST | /reset-password | Reset password with token |

### Resume (`/api`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /parse-resume | Upload & parse CV (returns validation + analysis) |
| GET | /history | List user resumes with analysis count |
| GET | /resumes/{id} | Get full resume with all sections |
| GET | /analyses/{id} | Get analysis result |

### Job Descriptions (`/api/job-descriptions`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | List JDs (search, pagination) |
| POST | / | Create JD |
| GET | /{id} | Get JD |
| PUT | /{id} | Update JD |
| DELETE | /{id} | Delete JD |
| POST | /{id}/archive | Archive JD |
| POST | /{id}/restore | Restore JD |
| POST | /{id}/duplicate | Duplicate JD |
| POST | /{id}/use | Track JD usage |

### Dashboard (`/api/dashboard`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /summary | Summary stats |
| GET | /score-distribution | Score buckets with counts |
| GET | /top-skills | Top skills with normalization |

### Analysis History
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/analysis-history | List with filters |
| GET | /api/analysis-history/{id} | Get analysis detail |
| POST | /api/analysis-history/{id}/rerun | Re-run analysis |
| DELETE | /api/analysis-history/{id} | Delete analysis |
| GET | /api/analysis-history/{id}/export/pdf | Export PDF |
| GET | /api/analysis-history/{id}/export/excel | Export Excel |

---

## Key Dependencies

### Backend
fastapi, uvicorn, sqlalchemy, pydantic, pymupdf, python-docx, pytesseract, pillow, langchain-google-genai, langchain-core, langchain-community, chromadb, langchain-text-splitters, reportlab, openpyxl, tiktoken, pyyaml, python-jose[cryptography], passlib[bcrypt], python-multipart, psycopg2-binary, python-dotenv, requests

### Frontend
react@19, react-dom@19, react-router-dom@7, axios, bootstrap@5, recharts@3, react-hot-toast, clsx, @vitejs/plugin-react

---

## Environment Variables (.env)

### Backend
```
DATABASE_URL=postgresql://postgres:1234@localhost:1509/Ai_resumec
GEMINI_API_KEY=your_gemini_api_key
CHROMA_DB_PATH=./chroma_db
```

### Frontend (`.env` in frontend/)
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## Running the Project

### Backend
```bash
cd backend
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or recreate venv:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### PostgreSQL (if not running)
PostgreSQL 18.x on port 1509, database `Ai_resumec`, user `postgres`, password `1234`

---

## Service Deep Dives

### Resume Validation Service (Lenient Mode)
Never rejects - always returns is_resume=True with confidence and details:
```
confidence: 0.85, details: { text_length: 2500, quality_scores: {...}, detected_sections: [...], has_contact: true }
```

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
Hybrid retrieval: docs = rag.retrieve(query, k=5, use_hybrid=True)
Context building with token budget: context = rag.get_context(query=..., resume_text=..., job_description=..., max_context_tokens=3000, use_hybrid=True)
Logs: Token budget: 1200 for RAG context (resume: 800, JD: 500)

### Export Service
PDF: pdf_buffer = ExportService.generate_pdf(analysis_data)
Excel: excel_buffer = ExportService.generate_excel_single(analysis_data)

### Dashboard Service - Skill Normalization
Normalizes variants: normalize_skill(REACT.JS) -> React, normalize_skill(JS) -> JavaScript
Top skills example: skill=Python, resume_count=45, percentage=78.5

---

## Knowledge Base Files (RAG)
Located in `backend/app/rag/knowledge/` (7 files, ~31KB total):
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

---

## Code Quality Observations

### Strengths
1. **Modular Architecture**: Clear separation (models, schemas, routers, services, rag, auth)
2. **Lenient Validation**: Never blocks users, provides rich quality metadata
3. **Multi-format Support**: PDF, DOCX, TXT with OCR fallback
4. **Advanced RAG**: Hybrid search (semantic + BM25) + token budget management
5. **Knowledge Base**: 7 curated markdown files with frontmatter metadata
6. **Context Window Management**: Tiktoken-aware truncation for LLM efficiency
7. **Export Features**: Professional PDF & Excel reports
8. **Dashboard Analytics**: Skill normalization, score distributions, date filtering
9. **Phone/Email Normalization**: E.164 phones, OCR-resistant email parsing
10. **JD Management**: Full CRUD + archive/duplicate
11. **Authentication**: JWT with refresh, bcrypt, protected routes
12. **Modern Frontend**: Design tokens, theming, responsive layout, component library
13. **PostgreSQL Schema**: 11 tables with proper FKs, indexes, constraints
14. **Frontend-Backend Separation**: Independent deployable services

### Areas for Improvement
1. **Error Handling**: Some try-catch blocks too broad (catch Exception)
2. **Type Hints**: Inconsistent annotations across services
3. **Testing**: Limited coverage (only test_validation.py exists)
4. **Rate Limiting**: No API rate limiting implemented
5. **Async/Await**: Some services not fully async (parser, export)
6. **Logging**: Uses print() instead of structured logging (structlog/loguru)
7. **Database Migrations**: No Alembic setup
8. **PDF Generation**: Minor bug - jd_table variable typo
9. **Knowledge Base**: No hot-reload on file changes (requires restart/rebuild_index)
10. **API Documentation**: OpenAPI could use more examples

---

## Recommended Next Steps

### High Priority
- Add API rate limiting (slowapi)
- Implement structured logging (structlog/loguru)
- Set up Alembic for DB migrations
- Write unit/integration tests (target >80% coverage)
- Fix PDF export variable name bug (jd_table vs jd_data)
- Add input sanitization/validation middleware

### Medium Priority
- Improve async support in parser_service & export_service
- Implement Redis caching for frequent queries (dashboard, RAG)
- Enhance OpenAPI documentation with examples
- Add knowledge base hot-reload / file watcher
- Implement password reset flow (email integration)

### Low Priority
- Frontend TypeScript migration
- CI/CD pipeline (GitHub Actions)
- Docker compose for full stack
- Skill taxonomy versioning in RAG knowledge base
- Unit test coverage >80%

---

## Related Files
- NEW_UI_DESIGN_REQUIREMENTS.md - Complete UI/UX specification for redesign
- REVIEW_SYSTEM.md - System architecture review
- test_validation.py - Validation service tests
- backend/.env.example - Environment template
- backend/app/rag/vector_store.py - RAG with hybrid search & token budget
- backend/app/services/llm_analyzer.py - LLM with context management
- backend/app/services/parser_service.py - Enhanced extraction (phone E.164, email OCR, name)
- backend/app/services/resume_validation_service.py - Lenient validator
- backend/app/services/export_service.py - PDF/Excel generation
- backend/app/services/dashboard_service.py - Analytics with skill normalization
- backend/app/routers/resume.py - Main API with validation metadata
- backend/app/routers/auth.py - JWT authentication
- backend/app/rag/knowledge/*.md (7 files) - Knowledge base
- data/db.sql - PostgreSQL schema (11 tables, FKs, constraints)
- frontend/src/theme/tokens.js - Design tokens
- frontend/src/theme/ThemeProvider.jsx - Theme context
- frontend/src/contexts/AuthContext.jsx - Auth state management

---
Updated: 2026-07-30
Project: AI Resume Analyzer
