# Codebase and Database Refactoring Requirements

## 1. Purpose

Refactor the AI Resume Analyzer codebase so that its backend models, parsing services, analysis workflow, API endpoints, and persistence layer follow the approved ERD and the PostgreSQL schema defined in `db.sql`.

The refactored system must:

- Read and validate uploaded CV/resume documents.
- Extract structured candidate and resume information from valid CV/resume documents.
- Store candidate, resume, skill, education, work experience, project, and certification data in PostgreSQL.
- Read and store Job Description (JD) data.
- Analyze a resume independently or compare it with a selected Job Description.
- Store the generated analysis result in the database.
- Allow fields to remain `NULL` or collections to remain empty when the source document does not provide the corresponding information.

---

## 2. Database Source of Truth

The supplied PostgreSQL schema is the source of truth for persistence. The codebase must provide ORM models, schemas, repositories, services, and API contracts corresponding to these tables:

- `users`
- `job_seekers`
- `education`
- `resumes`
- `certifications`
- `projects`
- `work_experiences`
- `skills`
- `resume_skills`
- `job_descriptions`
- `analyses`

The existing primary keys, foreign keys, unique constraints, and deletion behaviors must be preserved unless a separate migration explicitly changes them.

### Key Relationships

- One user can upload zero or more resumes.
- Each stored resume must belong to one user.
- One job seeker can be represented by one or more resumes.
- Each stored resume must refer to one job seeker.
- One job seeker can have zero or more education records.
- One resume can contain zero or more certifications.
- One resume can contain zero or more projects.
- One resume can contain zero or more work experience records.
- Resumes and skills have a many-to-many relationship through `resume_skills`.
- One resume can have zero or more analysis records.
- One Job Description can be referenced by zero or more analysis records.
- An analysis may have no Job Description when standalone CV analysis is performed.

---

## 3. Codebase Refactoring Scope

### 3.1 Persistence Layer

Create or update the ORM models so that all columns and relationships match `db.sql`.

The implementation must include:

- UUID primary keys.
- Database-generated UUID defaults where supported.
- Nullable columns consistent with the database schema.
- Composite primary key support for `resume_skills`.
- Unique constraints for user email and skill name.
- Foreign-key relationships and appropriate cascade behavior.
- Database transactions for multi-table persistence.
- PostgreSQL-compatible configuration and connection management.

Recommended backend organization:

```text
backend/app/
├── models/
│   ├── user.py
│   ├── job_seeker.py
│   ├── education.py
│   ├── resume.py
│   ├── certification.py
│   ├── project.py
│   ├── work_experience.py
│   ├── skill.py
│   ├── resume_skill.py
│   ├── job_description.py
│   └── analysis.py
├── schemas/
├── repositories/
├── services/
├── routers/
└── database.py
```

The exact folder names may follow the current architecture, but responsibilities must remain separated.

### 3.2 Schema and API Layer

Create request and response schemas for:

- Resume upload and parsing.
- Job seeker data.
- Education history.
- Work experience.
- Skills and resume-skill metadata.
- Projects and certifications.
- Job Description creation and update.
- Resume analysis requests.
- Stored analysis results.

Response schemas must not expose password hashes, internal file paths, stack traces, or provider secrets.

---

## 4. CV/Resume Ingestion Requirements

### FR-CV-01: Accept Supported Documents

The resume ingestion feature must accept the supported document types configured by the project, including PDF and DOCX. Basic validation must check the extension, MIME type, configured maximum size, readability, and password protection status.

### FR-CV-02: Verify That the Document Is a CV/Resume

Before persistent resume data is created, the processing service must determine whether the uploaded document appears to be a CV/resume.

If the document is not a CV/resume:

- Stop processing.
- Return a clear validation error.
- Do not create `job_seekers`, `resumes`, child resume records, or `analyses` rows.
- Do not permanently store the source file.
- Delete temporary files and extracted temporary content.

Recommended response message:

> This document does not appear to be a CV or resume. Please upload a valid CV in PDF or DOCX format.

The CV classification result is processing-only information and does not need its own database table.

### FR-CV-03: Extract Structured Resume Data

For a valid CV/resume, the document reader and extraction model must produce a normalized object that may include:

- Candidate name, email, phone number, major, and image reference.
- Education entries.
- Resume interests, description or summary, activities, honors, and awards.
- Work experience entries.
- Skills, categories, proficiency levels, and extraction confidence scores.
- Projects.
- Certifications.
- Original filename, file type, storage path, extracted text, and upload timestamp.

### FR-CV-04: Persist Resume Data

After successful validation and extraction, save the data in one database transaction using this sequence:

1. Identify the authenticated `users` record.
2. Create or resolve the corresponding `job_seekers` record.
3. Insert the `resumes` record with `userid` and `jsid`.
4. Insert available `education` records for the job seeker.
5. Insert available `work_experiences` records for the resume.
6. Insert available `projects` records for the resume.
7. Insert available `certifications` records for the resume.
8. Normalize and upsert `skills` by unique `skill_name`.
9. Insert the related `resume_skills` rows.
10. Commit only after all required persistence steps succeed.

If a required insert fails, roll back the complete transaction to avoid partial resume data.

### FR-CV-05: Job Seeker Resolution

The user of the application and the person described in the CV are different concepts:

- `users` represents the account operating the application.
- `job_seekers` represents the candidate described by the CV.

The service should avoid accidentally combining different candidates. If candidate identity cannot be resolved safely, create a new job seeker record rather than merging records based only on a non-unique name.

---

## 5. Missing Source Data Rules

The extraction model must never invent values that are not supported by the source CV, resume, or JD.

When the source document does not contain a value:

- Store `NULL` for nullable scalar database columns.
- Store an empty string only when an existing API contract explicitly requires a string and changing it is outside the refactoring scope.
- Store an empty list in the extraction result for missing collections.
- Do not insert child rows for missing education, experience, project, certification, or skill collections.
- Do not use placeholder values such as `Unknown`, `N/A`, `None`, or fake dates unless a separate business rule explicitly requires them.
- Preserve zero only when zero is a genuine calculated value, not when a score is unavailable.

Examples:

```json
{
  "name": "Candidate Name",
  "email": null,
  "phone": null,
  "major": null,
  "education": [],
  "work_experiences": [],
  "projects": [],
  "certifications": [],
  "skills": []
}
```

The extraction result should distinguish between:

- Missing information: `null` or an empty collection.
- Successfully calculated zero: `0` or `0.00`.
- Processing failure: an explicit error state.

### Required-Column Conflict

Some database columns are currently `NOT NULL`, including `job_seekers.name`, `projects.project_name`, `certifications.certification_name`, and `work_experiences.company`.

The service must not insert incomplete child records that lack their required identifying value. For the candidate name, the implementation must either:

1. Require a reliably extracted candidate name before persistence, or
2. Introduce an approved database migration that makes the column nullable.

The system must not silently insert fabricated content merely to satisfy a database constraint.

---

## 6. Job Description Requirements

### FR-JD-01: Read JD Input

The system must support Job Description content supplied through the existing input methods, such as pasted text, form data, or an uploaded supported document.

The JD reader must normalize the source into fields corresponding to `job_descriptions`:

- `title`
- `company_name`
- `location`
- `emp_type`
- `experience_level`
- `description`
- `source_url`
- `requirement`
- `priority`

### FR-JD-02: Store JD Data

The normalized Job Description must be inserted into `job_descriptions`.

If a field is not present in the source JD, store `NULL` where the column is nullable. The default database value may be used for `priority` when no value is supplied.

### FR-JD-03: Update and Retrieve JD Data

The existing JD management functionality must allow the application to:

- Create a JD.
- Retrieve one or more JDs.
- Update a JD.
- Delete a JD according to authorization rules.
- Select a stored JD for resume matching.

---

## 7. Document Reading and Analysis Model

### FR-AI-01: Document Reader

Implement a document reader capable of extracting text and structural content from supported sources.

Recommended processing sequence:

```text
Receive source document
        |
        v
Validate format, size, and readability
        |
        v
Extract text and document structure
        |
        v
Classify uploaded resume input as CV or non-CV
        |
        v
Normalize content for the extraction model
```

The reader should use deterministic parsing first. OCR may be used for scanned documents when supported.

### FR-AI-02: Structured Extraction Model

Use a parsing model, NLP pipeline, LLM, or hybrid approach to convert unstructured source text into structured data matching the database entities.

The model output must be validated against a strict schema before persistence. It must not be written directly to the database without type, length, range, and relationship validation.

The structured result should contain evidence or confidence metadata in memory when helpful, but only fields represented by the approved persistence model must be stored.

### FR-AI-03: Resume Analysis

The analysis service must support:

1. Standalone resume analysis without a JD.
2. Resume-to-JD matching when a JD is supplied.

The service may calculate:

- Overall score.
- ATS score.
- Match score.
- Experience score.
- Education score.
- Skill score.
- Strengths.
- Weaknesses.
- Matched keywords.
- Missing keywords.
- Suggestions.
- Analysis status.

The analysis model must use the parsed resume data, extracted source text, and the selected JD when available.

### FR-AI-04: Persist Analysis Results

After the analysis result passes schema validation, create a row in `analyses` containing:

- `resume_id`
- Optional `jdid`
- Available scores
- Strengths and weaknesses
- Matched and missing keywords
- Suggestions
- Status
- Analysis timestamp

When no JD is used:

- `jdid` must be `NULL`.
- JD-specific results such as `match_score`, `matched_keywords`, and `missing_keywords` may be `NULL` when they are not calculated.

If analysis fails:

- Do not store a successful status.
- Roll back an incomplete analysis insert, or store an explicit failure status only if failure-history persistence is intentionally supported.
- Return a safe error response without provider internals.

---

## 8. Transaction and Idempotency Requirements

- Resume persistence and all related child inserts must use a database transaction.
- Analysis persistence must not be committed before the analysis result is validated.
- Skill creation must respect the unique constraint on `skills.skill_name`.
- Skill names should be normalized consistently before lookup or insertion.
- Repeated API retries must not unintentionally create duplicate records.
- An idempotency key, file checksum, or request identifier should be considered for upload endpoints.
- Concurrent skill upserts must safely handle unique-constraint conflicts.

---

## 9. Validation Rules

### File Validation

- Accept only configured file types.
- Enforce the maximum file size.
- Reject unreadable, empty, corrupted, or password-protected files.
- Validate on the backend even when the frontend already validates.

### Data Validation

- Score values must be within the configured range, normally 0 to 100.
- Confidence scores must follow one documented scale, either 0 to 1 or 0 to 100.
- Email addresses and URLs should be validated when present.
- Text must be trimmed and normalized before persistence.
- Values longer than database column limits must be safely rejected or intentionally truncated according to a documented rule.
- UUID references must exist before related rows are inserted.

---

## 10. Privacy and Security Requirements

- Store only data required for the product functionality.
- Do not log full CV text, passwords, access tokens, API keys, or sensitive candidate details.
- Keep uploaded documents in controlled storage and persist only the intended path or object key.
- Sanitize filenames and never trust client-provided paths.
- Delete temporary source files after processing.
- Apply authorization so users can access only permitted resumes, candidates, JDs, and analyses.
- Continue storing only password hashes in `users.password_hash`.
- Use parameterized ORM queries and safe transaction handling.

---

## 11. API Behavior

### Successful Resume Processing

```json
{
  "success": true,
  "resume_id": "uuid",
  "job_seeker_id": "uuid",
  "message": "The CV was processed and saved successfully.",
  "data": {
    "job_seeker": {},
    "resume": {},
    "education": [],
    "work_experiences": [],
    "projects": [],
    "certifications": [],
    "skills": []
  }
}
```

### Successful Analysis

```json
{
  "success": true,
  "analysis_id": "uuid",
  "resume_id": "uuid",
  "job_description_id": "uuid-or-null",
  "status": "completed",
  "result": {
    "overall_score": 82.5,
    "ats_score": 79.0,
    "match_score": 75.0,
    "strengths": "...",
    "weaknesses": "...",
    "suggestions": "..."
  }
}
```

### Non-CV Document

Recommended HTTP status: `422 Unprocessable Entity`.

```json
{
  "success": false,
  "error_code": "NOT_A_RESUME",
  "message": "This document does not appear to be a CV or resume. Please upload a valid CV in PDF or DOCX format."
}
```

---

## 12. Acceptance Criteria

### AC-01: Valid CV Persistence

**Given** an authenticated user uploads a valid CV,  
**When** reading, validation, extraction, and schema validation succeed,  
**Then** the system stores the job seeker, resume, and all available related records in one transaction.

### AC-02: Missing Resume Information

**Given** a valid CV does not contain a phone number, projects, or certifications,  
**When** the CV is processed,  
**Then** nullable scalar values are stored as `NULL`, empty collections create no child records, and no information is fabricated.

### AC-03: Invalid Non-CV Document

**Given** the upload is not a CV/resume,  
**When** classification is completed,  
**Then** the system returns `NOT_A_RESUME` and creates no persistent resume-related data.

### AC-04: Work Experience Persistence

**Given** a CV contains multiple work experience entries,  
**When** extraction succeeds,  
**Then** each valid entry is stored in `work_experiences` and linked to the saved resume.

### AC-05: Skill Persistence

**Given** a CV contains skills,  
**When** the skills are normalized,  
**Then** existing skills are reused, new skills are inserted only once, and `resume_skills` stores the corresponding associations and optional metadata.

### AC-06: JD Persistence

**Given** the user submits a Job Description,  
**When** JD parsing succeeds,  
**Then** available JD fields are stored in `job_descriptions` and absent nullable fields remain `NULL`.

### AC-07: Standalone Analysis

**Given** a valid stored resume and no JD,  
**When** standalone analysis completes,  
**Then** an `analyses` row is stored with `resume_id`, `jdid = NULL`, available standalone scores, findings, suggestions, and a completed status.

### AC-08: Resume-to-JD Analysis

**Given** a valid stored resume and a selected stored JD,  
**When** matching completes,  
**Then** the resulting `analyses` row references both records and stores the available match scores, matched keywords, missing keywords, and suggestions.

### AC-09: Transaction Rollback

**Given** one required persistence operation fails during multi-table resume storage,  
**When** the transaction is rolled back,  
**Then** no partial job seeker, resume, or child data remains from that request.

### AC-10: Model Output Validation

**Given** the extraction or analysis model returns malformed or out-of-range data,  
**When** schema validation is applied,  
**Then** the invalid result is rejected and is not written to the database.

---

## 13. Testing Requirements

Implement automated tests for:

- PDF and DOCX text extraction.
- CV versus non-CV classification.
- Extraction with complete and incomplete source documents.
- Missing scalar and collection handling.
- ORM relationships and foreign-key integrity.
- Resume transaction success and rollback.
- Skill normalization and concurrent upsert behavior.
- JD parsing, creation, update, retrieval, and deletion.
- Standalone analysis.
- Resume-to-JD matching.
- Analysis result persistence.
- Authorization and cross-user access restrictions.
- Temporary file cleanup.

Tests must use controlled fixtures and must not rely on fabricated production data.

---

## 14. Migration and Delivery Requirements

- Compare current ORM models with `db.sql` before implementation.
- Introduce versioned database migrations for every schema change.
- Do not rely on automatic table creation as a substitute for migrations in deployed environments.
- Preserve existing valid data during migration.
- Update environment examples for PostgreSQL configuration.
- Update API documentation and project README.
- Document how to run migrations, tests, backend services, and the frontend.

---

## 15. Definition of Done

The refactoring is complete when:

- The codebase follows the approved ERD and PostgreSQL schema.
- All required ORM models and relationships are implemented.
- Valid CVs are parsed into structured data and persisted correctly.
- Non-CV files are rejected before persistent records are created.
- Missing source information is stored as `NULL` or represented by an empty collection without fabricated values.
- JD content can be read, normalized, stored, retrieved, updated, and selected for analysis.
- Standalone and JD-based analysis results are generated and persisted in `analyses`.
- Multi-table writes are transactional.
- Automated tests cover the critical workflows and acceptance criteria.
- Database migrations, configuration, API documentation, and setup instructions are updated.
