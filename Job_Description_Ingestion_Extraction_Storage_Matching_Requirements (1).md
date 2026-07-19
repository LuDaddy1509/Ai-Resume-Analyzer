# Job Description Ingestion, Requirement Extraction, Storage, and Resume Matching Specification

> This document defines the functional, UI, data, API, validation, privacy, and acceptance requirements for importing Job Descriptions from images and documents, extracting recruitment requirements, storing structured JD data, and comparing saved Job Descriptions with resumes in the **AI Resume Analyzer & Job Matcher** application.

---

## 1. Purpose

The Job Description module allows users to import a Job Description from an image, DOCX document, or PDF file. The system extracts readable text, identifies the most relevant recruitment requirements, converts the extracted information into structured data, and stores the Job Description for later reuse.

A stored Job Description can then be selected and compared with an uploaded resume. The system produces a structured matching result containing scores, matched requirements, missing requirements, skill gaps, and improvement suggestions.

---

## 2. Business Goals

- Reduce manual Job Description data entry.
- Support job postings received as screenshots, images, PDF files, or Word documents.
- Convert unstructured recruitment content into reusable structured records.
- Allow users to build and manage a personal Job Description library.
- Compare the same JD against multiple resumes.
- Preserve the JD used for each analysis so historical results remain reproducible.
- Generate transparent matching results without inventing candidate experience or qualifications.

---

## 3. Scope

## 3.1 Included in the initial scope

- Upload JD files in image, PDF, and DOCX formats.
- Paste JD text manually as an alternative input method.
- Extract text from supported documents.
- Apply OCR to image-based files and scanned PDFs.
- Detect and extract recruitment requirements.
- Let users review and edit extracted information.
- Store the original text and structured JD data.
- Search, filter, edit, archive, duplicate, and reuse saved JDs.
- Compare a selected resume with a saved JD.
- Generate explainable matching results.

## 3.2 Supported input formats

### Images

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`, if supported by the selected OCR pipeline

### Documents

- `.pdf`
- `.docx`

### Optional text input

- Pasted plain text
- `.txt`

## 3.3 Outside the initial scope

- Importing a JD directly from arbitrary recruitment websites.
- Browser extensions for capturing job postings.
- Automatic application submission.
- Ranking candidates for employers.
- Making definitive hiring or rejection decisions.
- Guaranteeing interview or employment outcomes.

---

# 4. User Roles

## 4.1 Job Seeker

A Job Seeker can:

- Upload or paste a Job Description.
- Review and correct extracted data.
- Save the JD.
- Select a saved JD for resume matching.
- View matching scores and recommendations.

## 4.2 Anonymous User

An anonymous user may import and analyze a JD in a temporary session. Permanent storage requires account authentication and explicit consent.

## 4.3 Administrator

An administrator may:

- Monitor import success and failure statistics.
- Review parser and OCR error rates without exposing unnecessary personal data.
- Manage extraction dictionaries and skill aliases.
- View aggregated usage metrics.

---

# 5. Main User Flow

```text
Open Job Description page
        ↓
Choose input method
        ↓
Upload image / PDF / DOCX or paste text
        ↓
Validate file type and size
        ↓
Extract text using document parser or OCR
        ↓
Detect recruitment requirements
        ↓
Display editable extraction preview
        ↓
User reviews and confirms data
        ↓
Save JD to the system
        ↓
Select an existing resume
        ↓
Run Resume–JD matching
        ↓
Display scores, matched requirements, gaps, and suggestions
```

---

# 6. Job Description Import UI

## 6.1 Input options

The interface must provide two tabs or segmented controls:

1. `Upload File`
2. `Paste Text`

## 6.2 Upload area

The upload interface must include:

- Drag-and-drop area
- `Choose File` button
- Supported format label
- Maximum file-size label
- Privacy notice

### Suggested copy

```text
Import a Job Description

Drag and drop a JPG, PNG, PDF, or DOCX file here
or
[Choose File]

Scanned documents and screenshots will be processed using OCR.
Maximum file size: 10 MB
```

## 6.3 Selected file display

After selection, display:

- Original file name
- File type
- Human-readable file size
- Extraction mode: Parser or OCR
- Validation status
- Replace and remove actions

## 6.4 Processing states

The UI must support:

```text
Idle
Validating
Uploading
Extracting text
Running OCR
Extracting requirements
Ready for review
Saved
Warning
Error
```

---

# 7. File Validation Requirements

Validation must occur on both the client and server.

## 7.1 Validation order

1. Confirm that a file was submitted.
2. Confirm that only one JD file was submitted.
3. Reject zero-byte files.
4. Enforce the configured maximum size.
5. Validate file extension.
6. Validate detected MIME type.
7. Verify document or image structure where possible.
8. Attempt text extraction.
9. Use OCR when direct text extraction returns insufficient readable text.

## 7.2 Default maximum file size

```text
10 MB per Job Description file
```

The limit must be configurable.

## 7.3 MIME types

```text
image/jpeg
image/png
image/webp
application/pdf
application/vnd.openxmlformats-officedocument.wordprocessingml.document
text/plain
```

## 7.4 Error messages

### Unsupported format

```text
Unsupported file format. Please upload a JPG, PNG, PDF, DOCX, or TXT file.
```

### File too large

```text
This file exceeds the 10 MB limit. Please upload a smaller file.
```

### Unreadable document

```text
We could not read this Job Description. The file may be corrupted, encrypted, or use an unsupported structure.
```

### OCR failure

```text
We could not recognize enough text from this image. Please upload a clearer image or paste the Job Description text manually.
```

### Insufficient JD content

```text
The extracted content does not appear to contain enough job information. Please review the text or upload another file.
```

---

# 8. Text Extraction Pipeline

## 8.1 PDF extraction

1. Attempt native text extraction.
2. Measure the amount and quality of extracted text.
3. If the PDF contains little or no readable text, treat it as a scanned PDF.
4. Convert relevant pages to images.
5. Run OCR.
6. Merge text in page order.

## 8.2 DOCX extraction

Extract:

- Paragraphs
- Headings
- Lists
- Table text
- Relevant hyperlinks, if required

The parser should preserve logical ordering where possible.

## 8.3 Image extraction

For JPG, PNG, or WEBP:

1. Validate image readability.
2. Correct orientation using metadata where possible.
3. Improve OCR input with safe preprocessing if needed.
4. Run OCR.
5. Return text with confidence information when available.

## 8.4 Pasted text

- Normalize whitespace.
- Preserve list structure where possible.
- Reject empty content.
- Warn when content is too short.

## 8.5 Extraction output

```json
{
  "rawText": "...",
  "extractionMethod": "native_pdf | docx | ocr | pasted_text",
  "pageCount": 2,
  "ocrConfidence": 0.91,
  "warnings": []
}
```

---

# 9. Recruitment Requirement Extraction

## 9.1 Purpose

The system must filter the Job Description content and identify requirements relevant to recruitment and resume matching.

## 9.2 Information to extract

### Job identity

- Job title
- Company name
- Department or team
- Job level
- Employment type
- Work arrangement: onsite, hybrid, or remote
- Location

### Required qualifications

- Required hard skills
- Required soft skills
- Required technologies and tools
- Minimum years of experience
- Required education
- Required certifications
- Language requirements

### Preferred qualifications

- Preferred hard skills
- Preferred technologies
- Preferred certifications
- Domain experience
- Additional language skills

### Responsibilities

- Main duties
- Expected deliverables
- Collaboration requirements
- Leadership or ownership expectations

### Compensation and conditions, when present

- Salary range
- Benefits
- Working hours
- Contract type

### Recruitment metadata

- Source URL
- Application deadline
- Contact information, if intentionally retained
- Original document name

## 9.3 Requirement attributes

Each extracted requirement should include:

```text
name
normalized_name
category
requirement_level
importance
source_text
evidence_start
evidence_end
confidence
```

### Requirement level

```text
required
preferred
optional
unknown
```

### Category

```text
hard_skill
soft_skill
tool
technology
experience
education
certification
language
responsibility
location
work_type
other
```

## 9.4 Requirement importance

Suggested levels:

```text
critical
high
medium
low
```

Importance may be determined by:

- Placement in a `Required Qualifications` section
- Words such as must, required, mandatory, minimum
- Repetition
- Position in the document
- Explicit preference language

## 9.5 Skill normalization

The system should map aliases to one canonical value.

```text
JS, Javascript, JavaScript → JavaScript
React.js, ReactJS, React → React
Postgres, PostgreSQL → PostgreSQL
Amazon Web Services, AWS → AWS
```

The original text must remain available as evidence.

## 9.6 Extraction safety rules

- Do not infer requirements that are not supported by the JD text.
- Distinguish required and preferred qualifications.
- Attach evidence text to extracted requirements.
- Show low-confidence results for review rather than silently treating them as facts.
- Do not transform benefits or company descriptions into candidate requirements.

---

# 10. Extraction Review UI

Before saving, the user must be able to review and edit the extracted information.

## 10.1 Page layout

### Left panel

- Original file preview or extracted raw text
- Highlighted evidence for the selected requirement

### Right panel

Editable structured information:

- Job title
- Company
- Job level
- Location
- Employment type
- Responsibilities
- Required skills
- Preferred skills
- Experience
- Education
- Certifications
- Languages

## 10.2 Requirement tags

Use visual statuses:

- Required: strong emphasis
- Preferred: secondary emphasis
- Low confidence: warning style
- User edited: edited indicator

## 10.3 Actions

- Add requirement
- Edit requirement
- Remove incorrect requirement
- Change category
- Change required/preferred status
- Restore extracted value
- Save Job Description
- Cancel import

---

# 11. Job Description Storage

## 11.1 Storage principles

Store both:

1. The source or normalized raw text
2. The structured extracted data

This allows the system to improve extraction later while preserving the original evidence.

## 11.2 Privacy and retention

- Temporary imports must not be stored permanently without user consent.
- Permanent JD storage requires an authenticated user or workspace owner.
- Temporary source files should be deleted after parsing according to a configured retention policy.
- Raw JD text may be retained when the user chooses to save the JD.
- Avoid logging full JD content in operational logs.

## 11.3 Job Description statuses

```text
draft
active
archived
deleted
```

## 11.4 Usage tracking

Store:

- Number of times the JD was used for matching
- Last used date
- Number of resumes analyzed against the JD

---

# 12. Database Design

## 12.1 `job_descriptions`

```text
id
user_id
title
company
department
job_level
employment_type
work_arrangement
location
salary_min
salary_max
salary_currency
source_url
source_file_name
source_file_type
raw_text
extraction_method
ocr_confidence
status
usage_count
last_used_at
created_at
updated_at
deleted_at
```

## 12.2 `job_requirements`

```text
id
job_description_id
name
normalized_name
category
requirement_level
importance
source_text
evidence_start
evidence_end
confidence
is_user_edited
created_at
updated_at
```

## 12.3 `job_responsibilities`

```text
id
job_description_id
description
importance
source_text
confidence
sort_order
created_at
updated_at
```

## 12.4 `job_description_files`

Use this table only when source-file metadata or temporary storage tracking is required.

```text
id
job_description_id
original_file_name
stored_file_key
file_type
mime_type
file_size_bytes
is_temporary
expires_at
created_at
deleted_at
```

## 12.5 `analysis_results`

The analysis record should reference the selected resume and JD.

```text
id
user_id
resume_id
job_description_id
resume_snapshot_json
job_description_snapshot_json
overall_score
ats_score
match_score
hard_skill_match_score
soft_skill_match_score
experience_match_score
education_match_score
keyword_coverage_score
matched_requirements_json
missing_requirements_json
partial_matches_json
skill_gaps_json
suggestions_json
created_at
```

## 12.6 Snapshot requirement

Every analysis must store a JD snapshot. If the saved JD is edited later, historical analysis results must remain unchanged.

---

# 13. Saved Job Description Management

## 13.1 JD library page

The page must support:

- Search by job title, company, or keyword
- Filter by status, job level, location, and creation date
- Sort by newest, recently used, or most used
- View details
- Edit
- Duplicate
- Archive
- Delete
- Use for matching

## 13.2 JD card content

- Job title
- Company
- Location
- Job level
- Required skills preview
- Created date
- Updated date
- Usage count
- Last used date
- Status

## 13.3 Reuse flow

From the resume matching page, users can choose:

```text
Enter a new Job Description
or
Select a saved Job Description
```

After selection:

- Display a JD preview.
- Allow the user to confirm the selection.
- Allow duplication before editing.
- Do not silently modify the original saved JD.

---

# 14. Resume and Saved JD Matching

## 14.1 Matching flow

```text
Select parsed resume
        ↓
Select saved Job Description
        ↓
Load resume and JD snapshots
        ↓
Normalize skills and keywords
        ↓
Compare required and preferred requirements
        ↓
Calculate component scores
        ↓
Generate explanations and suggestions
        ↓
Save AnalysisResult
        ↓
Display result dashboard
```

## 14.2 Matching categories

The system should compare:

- Hard skills
- Soft skills
- Technologies and tools
- Experience duration and relevance
- Education
- Certifications
- Languages
- Responsibilities and project evidence
- Keyword coverage

## 14.3 Match statuses

Each JD requirement should receive one of the following statuses:

```text
matched
partially_matched
missing
not_enough_evidence
not_applicable
```

## 14.4 Scoring model

Initial heuristic:

```text
Match Score =
Hard Skill Match × 40%
+ Soft Skill Match × 15%
+ Experience Match × 20%
+ Education Match × 10%
+ Keyword Coverage × 15%
```

Required and preferred requirements should not contribute equally. Required requirements must carry greater weight.

## 14.5 Match evidence

Every matched or partially matched requirement should include evidence from the resume.

Example:

```json
{
  "requirement": "FastAPI",
  "status": "matched",
  "resumeEvidence": "Developed REST APIs using FastAPI and PostgreSQL",
  "resumeSection": "Projects",
  "confidence": 0.94
}
```

## 14.6 Missing requirement behavior

The system must not recommend adding a missing skill as if the user already has it.

Correct guidance:

```text
The JD requires Docker, but the resume does not currently provide evidence of Docker experience. Add it only if you have used it, and include the relevant project or work context.
```

---

# 15. Matching Result UI

## 15.1 Score cards

- Match Score
- Hard Skill Match
- Soft Skill Match
- Experience Match
- Education Match
- Keyword Coverage

## 15.2 Requirement summary

- Number of required requirements matched
- Number partially matched
- Number missing
- Number with insufficient evidence

## 15.3 Detailed sections

### Matched requirements

Display requirement, category, importance, and resume evidence.

### Missing requirements

Display requirement, importance, and safe recommendation.

### Partial matches

Display why the evidence is incomplete.

### Skill gaps

Rank by impact on the overall score.

### Improvement suggestions

Provide 3–5 prioritized actions.

## 15.4 User actions

- Export result to PDF
- Export result to Excel
- Compare another resume
- Reuse the same JD
- Edit or duplicate the JD
- Open the resume improvement workspace

---

# 16. API Specification

## 16.1 Import JD file

```text
POST /api/job-descriptions/import
Content-Type: multipart/form-data
```

Request fields:

```text
file
saveConsent
sessionId (optional)
```

## 16.2 Extract from pasted text

```text
POST /api/job-descriptions/extract
Content-Type: application/json
```

```json
{
  "rawText": "Full Job Description text..."
}
```

## 16.3 Save reviewed JD

```text
POST /api/job-descriptions
```

## 16.4 Update JD

```text
PUT /api/job-descriptions/{jobDescriptionId}
```

## 16.5 List saved JDs

```text
GET /api/job-descriptions
```

Suggested query parameters:

```text
search
status
jobLevel
location
sort
page
pageSize
```

## 16.6 Use or duplicate JD

```text
POST /api/job-descriptions/{id}/use
POST /api/job-descriptions/{id}/duplicate
PATCH /api/job-descriptions/{id}/archive
```

## 16.7 Compare resume with saved JD

```text
POST /api/matches
```

```json
{
  "resumeId": "res_123",
  "jobDescriptionId": "jd_456"
}
```

## 16.8 Retrieve result

```text
GET /api/analysis-results/{analysisId}
```

---

# 17. Suggested Service Architecture

```text
JobDescriptionImportService
├── FileValidationService
├── PdfTextExtractor
├── DocxTextExtractor
├── ImageOcrService
└── TextQualityEvaluator

JobDescriptionExtractionService
├── SectionDetector
├── RequirementExtractor
├── ResponsibilityExtractor
├── SkillNormalizationService
└── ExtractionConfidenceService

JobDescriptionService
├── Create
├── Update
├── Search
├── Duplicate
├── Archive
└── TrackUsage

ResumeJobMatchingService
├── ResumeEvidenceIndexer
├── RequirementMatcher
├── ScoreCalculator
├── GapAnalyzer
└── SuggestionGenerator
```

---

# 18. Error Handling

## Import errors

- Unsupported file type
- File too large
- Corrupted file
- Password-protected PDF
- OCR failure
- No meaningful text found

## Extraction warnings

- Job title not detected
- Required and preferred requirements could not be separated
- Low OCR confidence
- Very short JD
- Unrecognized section structure

## Matching errors

- Resume has not been parsed
- JD has not been confirmed
- JD contains no usable requirements
- AI provider timeout
- Matching service temporarily unavailable

All errors must include:

- Stable error code
- Human-readable message
- Suggested user action
- Retry eligibility

---

# 19. Privacy and Security Requirements

- Do not store source JD files permanently without consent.
- Do not expose private storage paths.
- Do not execute macros or embedded content from uploaded files.
- Validate MIME type and document structure server-side.
- Sanitize file names.
- Rate-limit import and OCR requests.
- Avoid logging complete JD or resume text.
- Encrypt stored data where required.
- Allow users to archive or delete saved JDs.
- Maintain tenant or user ownership checks for all JD and analysis endpoints.

---

# 20. Analytics Events

Allowed events:

```text
jd_import_started
jd_import_completed
jd_import_failed
jd_ocr_started
jd_ocr_completed
jd_extraction_completed
jd_saved
jd_updated
jd_duplicated
jd_reused
resume_jd_match_started
resume_jd_match_completed
resume_jd_match_failed
```

Safe event properties:

- File type
- File-size bucket
- Extraction method
- OCR confidence bucket
- Number of requirements
- Processing duration
- Error code

Do not include full JD or resume content in analytics.

---

# 21. Acceptance Criteria

## JD-01 — Image import

The user can upload a supported image and the system uses OCR to extract readable JD text.

## JD-02 — PDF import

The user can upload a text-based or scanned PDF. The system uses native parsing first and OCR when required.

## JD-03 — DOCX import

The user can upload DOCX and the system extracts paragraphs, lists, headings, and table text in a usable order.

## JD-04 — Requirement extraction

The system identifies required skills, preferred skills, experience, education, certifications, languages, and responsibilities when supported by the source text.

## JD-05 — Evidence and confidence

Every automatically extracted requirement includes source evidence and a confidence value or confidence state.

## JD-06 — Review before save

Users can review, add, edit, reclassify, and remove extracted requirements before saving.

## JD-07 — Save and reuse

An authenticated user can save the reviewed JD and select it later for another resume analysis.

## JD-08 — Historical consistency

An analysis stores a JD snapshot, and editing the original JD does not modify historical results.

## JD-09 — Resume comparison

The system compares a parsed resume with a selected saved JD and returns component scores and requirement statuses.

## JD-10 — Explainable result

Matched and partial requirements include resume evidence; missing requirements include safe, non-fabricated guidance.

## JD-11 — Privacy

Temporary files are deleted according to policy, and permanent storage requires consent.

## JD-12 — Error clarity

Unreadable files, OCR failures, incomplete JD content, and matching failures show clear and actionable messages.

---

# 22. Definition of Done

The feature is complete when:

- Users can import a JD from JPG, PNG, PDF, DOCX, or pasted text.
- Text-based documents are parsed successfully.
- Image and scanned files use OCR.
- The system extracts structured recruitment requirements.
- Users can review and correct extracted data.
- Confirmed JDs can be saved and managed.
- Saved JDs can be selected for future analyses.
- A parsed resume can be compared with a saved JD.
- Match scores and component scores are calculated.
- Matched, partial, missing, and insufficient-evidence requirements are displayed.
- Historical analysis records retain a JD snapshot.
- Upload, OCR, parsing, extraction, storage, and matching errors are handled.
- Privacy, ownership, and temporary-retention rules are enforced.
- Automated tests cover file formats, OCR fallback, extraction review, save/reuse, and resume–JD matching.

---

# 23. Recommended Implementation Order

```text
1. JD upload and pasted-text UI
2. File validation
3. PDF and DOCX text extraction
4. Image and scanned-PDF OCR
5. Requirement extraction
6. Extraction review and editing UI
7. JD database persistence
8. JD library and reuse flow
9. Resume–JD matching service
10. Matching result dashboard
11. Export and analytics integration
```
