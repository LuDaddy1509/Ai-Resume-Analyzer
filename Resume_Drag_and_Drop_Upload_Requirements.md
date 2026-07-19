# Resume Drag-and-Drop Upload – Functional and UI Specification

> This document defines the functional, user interface, validation, privacy, and acceptance requirements for uploading a resume through a drag-and-drop area or a file picker. The feature is designed for the **AI Resume Analyzer & Job Matcher** application.

---

## 1. Purpose

The Resume Upload feature allows users to submit a resume for parsing and analysis. The upload experience must be simple, accessible, secure, and transparent about file validation and data retention.

The feature must support:

- Dragging and dropping a resume file into an upload area
- Selecting a resume file through the operating system file picker
- Displaying the selected file name and size
- Validating the file type and ensuring that the uploaded file is a supported resume document
- Enforcing a maximum file-size limit
- Displaying clear error messages when a file cannot be read or processed
- Avoiding long-term file storage unless the user explicitly provides consent

---

## 2. Supported File Types

The initial version must support the following resume formats:

- PDF: `.pdf`
- Microsoft Word: `.docx`
- Plain text: `.txt`

Legacy Word `.doc` files are not included in the initial scope unless a compatible parser is added later.

### MIME types

The frontend and backend should validate both the extension and detected MIME type.

```text
application/pdf
application/vnd.openxmlformats-officedocument.wordprocessingml.document
text/plain
```

The system must not rely only on the file extension because a malicious or invalid file may be renamed to use a supported extension.

---

## 3. Maximum File Size

### Default limit

The recommended maximum file size is:

```text
10 MB per file
```

The limit must be configurable through application settings rather than hard-coded in multiple components.

### Configuration example

```text
MAX_RESUME_FILE_SIZE_MB=10
```

### File-size behavior

- Files within the limit may proceed to upload and parsing.
- Files larger than the configured limit must be rejected before parsing.
- The UI must display the maximum allowed size before the user selects a file.

---

## 4. Upload Component UI

## 4.1 Default state

The upload component must contain:

- A clearly visible drag-and-drop area
- An upload or document icon
- Primary guidance text
- A file selection button
- Supported format information
- Maximum file-size information
- A short privacy notice

### Suggested UI copy

```text
Upload your resume

Drag and drop your PDF, DOCX, or TXT file here
or
[Choose File]

Maximum file size: 10 MB
Your file will not be stored permanently without your consent.
```

## 4.2 Wireframe

```text
┌──────────────────────────────────────────────────────┐
│                                                      │
│                  [Document Upload Icon]              │
│                                                      │
│                  Upload your resume                  │
│                                                      │
│       Drag and drop a PDF, DOCX, or TXT file here    │
│                         or                           │
│                    [ Choose File ]                   │
│                                                      │
│                  Maximum size: 10 MB                 │
│                                                      │
│  Your file will not be stored permanently without   │
│                    your consent.                     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 5. Drag-and-Drop Behavior

## 5.1 Drag enter

When a user drags a file over the upload area:

- Highlight the drop zone
- Change the border color or background shade
- Display a message such as `Drop your resume here`
- Preserve sufficient color contrast

## 5.2 Drag leave

When the dragged file leaves the upload area:

- Restore the default appearance
- Remove the temporary drop instruction

## 5.3 Drop

When the user drops a file:

1. Read the first dropped file.
2. Reject multiple files if the feature supports one resume at a time.
3. Validate the file size.
4. Validate the extension and MIME type.
5. Perform a basic file signature or content check when supported.
6. Display the selected file information.
7. Start upload automatically or wait for explicit confirmation, depending on the selected interaction model.

### Multiple-file behavior

For the MVP, only one resume may be selected at a time.

If multiple files are dropped, display:

```text
Please upload one resume at a time.
```

---

## 6. File Picker Behavior

When the user selects `Choose File`:

- Open the native file picker
- Filter visible files to PDF, DOCX, and TXT where the platform supports filtering
- Allow the user to cancel without showing an error
- Run the same validation logic used by drag-and-drop after selection

The drag-and-drop flow and file-picker flow must produce the same result and validation messages.

---

## 7. Selected File Display

After a valid file is selected, display:

- File name
- Human-readable file size
- File type
- Validation status
- Remove or replace action
- Upload or analyze action, if upload does not begin automatically

### Example

```text
Selected resume
────────────────────────────────────────
File: Nguyen_Van_A_Resume.pdf
Type: PDF
Size: 1.84 MB
Status: Ready to upload

[Remove]                         [Continue]
```

### File size formatting

Use readable units:

- Bytes for very small files
- KB for files below 1 MB
- MB for larger files

Do not display long raw byte values as the primary size label.

---

## 8. Validation Requirements

Validation must be performed on both the frontend and backend. Frontend validation improves user experience, while backend validation remains the authoritative security control.

## 8.1 Required validation order

1. Confirm that a file exists.
2. Confirm that only one file was submitted.
3. Confirm that the size is greater than zero.
4. Confirm that the size does not exceed the configured limit.
5. Confirm that the extension is supported.
6. Confirm that the detected MIME type is supported.
7. Check the file signature or document structure when possible.
8. Attempt text extraction.
9. Reject encrypted, corrupted, empty, or unreadable documents when processing is impossible.

## 8.2 Resume document validation

The system should determine whether the document is reasonably usable as a resume by checking whether extracted content contains meaningful text.

Possible indicators include:

- Contact or personal information section
- Education section
- Experience or project section
- Skills section
- A minimum amount of readable text

This check must not reject unconventional resumes solely because a specific heading is missing. The system should return a warning rather than a hard error when the file is readable but the resume structure is unclear.

## 8.3 Validation result categories

### Valid

The file is supported, readable, and ready for parsing.

### Valid with warnings

The file can be parsed, but potential issues exist, such as:

- Very little text
- No recognizable resume sections
- Complex formatting
- Possible scanned/image-only PDF

### Invalid

The file cannot proceed because it is unsupported, too large, empty, corrupted, encrypted, or unreadable.

---

## 9. Error Messages

Error messages must be specific, actionable, and displayed near the upload component.

## 9.1 Unsupported format

```text
Unsupported file format. Please upload a PDF, DOCX, or TXT resume.
```

## 9.2 File too large

```text
This file exceeds the 10 MB limit. Please upload a smaller file.
```

## 9.3 Empty file

```text
The selected file is empty. Please choose a valid resume file.
```

## 9.4 Corrupted or unreadable file

```text
We could not read this file. It may be corrupted or use an unsupported document structure. Please try another file.
```

## 9.5 Password-protected or encrypted file

```text
This document is password-protected. Please remove the password and upload it again.
```

## 9.6 Image-only or scanned PDF

For an MVP without OCR:

```text
This PDF appears to contain scanned images without readable text. Please upload a text-based PDF, DOCX, or TXT file.
```

If OCR is available:

```text
This PDF appears to be scanned. Text recognition may take longer and may require your review.
```

## 9.7 Network or server error

```text
The upload could not be completed. Check your connection and try again.
```

## 9.8 Parser timeout

```text
The resume took too long to process. Please try again or upload a simpler version of the document.
```

---

## 10. Upload and Processing States

The component must visibly represent each state.

## 10.1 Idle

No file has been selected.

## 10.2 Drag active

A file is currently over the drop zone.

## 10.3 Validating

The application is checking type, size, and readability.

```text
Validating your resume...
```

## 10.4 Uploading

The file is being transmitted.

```text
Uploading... 65%
```

## 10.5 Parsing

The server is extracting and classifying resume content.

```text
Reading and organizing your resume...
```

## 10.6 Success

The file has been parsed successfully.

```text
Resume uploaded successfully.
```

## 10.7 Warning

The file can proceed, but the user should review extraction results.

## 10.8 Error

The file cannot proceed. Display a retry or replace action.

---

## 11. Privacy and File Retention

## 11.1 Default behavior

The uploaded resume must be treated as temporary unless the user explicitly agrees to save it.

Without consent:

- Store the file only for the duration required to upload and parse it
- Delete the original file after parsing or after a short configurable retention period
- Avoid writing resume contents to application logs
- Avoid including personal data in error monitoring events
- Retain only the minimum temporary data needed to complete the current session

## 11.2 Consent option

Provide an explicit checkbox or toggle:

```text
[ ] Save this resume to my account for future analyses.
```

The checkbox must not be pre-selected.

## 11.3 Anonymous users

For anonymous sessions:

- Use a temporary session identifier
- Apply a short expiration time
- Delete temporary files automatically
- Do not create permanent resume records unless the user signs in and consents

## 11.4 Deletion behavior

If the user removes the file before analysis:

- Remove it from the current UI state
- Cancel in-progress upload when possible
- Delete any temporary server copy associated with the session

---

## 12. Accessibility Requirements

- The drop zone must be keyboard accessible.
- The `Choose File` action must be reachable using Tab.
- Pressing Enter or Space on the drop zone should open the file picker.
- Error messages must be announced to screen readers.
- Upload progress must expose an accessible status.
- Color must not be the only method used to communicate success or failure.
- The component must show a visible focus indicator.
- All icons must have accessible labels or be marked decorative.

---

## 13. Responsive Design

## Desktop

- Use a large centered drop zone.
- Support drag-and-drop interactions.
- Display file metadata and actions on one row when space allows.

## Mobile

- Retain the drop zone instruction, but prioritize the `Choose File` button.
- Stack file metadata and actions vertically.
- Use touch targets of sufficient size.
- Avoid requiring drag-and-drop because mobile platforms may not support it consistently.

---

## 14. Frontend Component Structure

Suggested components:

```text
ResumeUploadPage
├── ResumeDropzone
├── FilePickerButton
├── SelectedFileCard
├── UploadProgress
├── ValidationMessage
├── PrivacyConsent
└── UploadActions
```

Suggested client state:

```text
idle
validating
ready
uploading
parsing
success
warning
error
```

---

## 15. API Requirements

## 15.1 Upload endpoint

```text
POST /api/resumes/upload
Content-Type: multipart/form-data
```

### Request fields

```text
file: binary resume file
saveConsent: boolean
sessionId: optional string
```

### Successful response

```json
{
  "resumeId": "res_123",
  "fileName": "Nguyen_Van_A_Resume.pdf",
  "fileType": "pdf",
  "fileSizeBytes": 1929374,
  "status": "parsed",
  "warnings": [],
  "temporary": true,
  "expiresAt": "2026-07-16T10:30:00Z"
}
```

### Validation error response

```json
{
  "code": "UNSUPPORTED_FILE_TYPE",
  "message": "Unsupported file format. Please upload a PDF, DOCX, or TXT resume.",
  "details": {
    "allowedExtensions": ["pdf", "docx", "txt"]
  }
}
```

## 15.2 Temporary file deletion endpoint

```text
DELETE /api/resumes/{resumeId}/temporary-file
```

This endpoint may be called when the user removes a file or abandons the upload flow.

---

## 16. Security Requirements

- Generate server-side file names; never trust the original file name as a storage path.
- Sanitize the original file name before display or persistence.
- Store temporary files outside publicly executable directories.
- Do not execute macros or embedded document content.
- Do not accept arbitrary content based solely on extension.
- Apply request-size limits at both the reverse proxy and application layers.
- Scan uploaded content if malware scanning is available.
- Prevent path traversal.
- Rate-limit upload attempts.
- Return generic internal errors without exposing server paths or stack traces.

---

## 17. Analytics Events

The frontend may emit non-sensitive events:

```text
resume_upload_started
resume_upload_validation_failed
resume_upload_completed
resume_parse_started
resume_parse_completed
resume_parse_failed
resume_file_removed
resume_save_consent_enabled
```

Event properties may include:

- File type
- File-size bucket
- Error code
- Processing duration

Do not include:

- Resume raw text
- Candidate name
- Email address
- Phone number
- Original file contents

---

## 18. Acceptance Criteria

### RU-01 — Drag and drop

Given the upload page is open, when the user drops one supported resume file into the drop zone, the system validates and displays the selected file.

### RU-02 — File picker

When the user selects `Choose File`, the native file picker opens and permits the user to select a supported document.

### RU-03 — File metadata

After valid selection, the UI displays the file name, readable size, type, and status.

### RU-04 — Format validation

The application accepts valid PDF, DOCX, and TXT files and rejects unsupported formats with a clear message.

### RU-05 — Resume readability

The backend attempts to extract text and returns either a successful result, a warning, or a clear unreadable-file error.

### RU-06 — Size validation

Files above the configured maximum size are rejected before parsing.

### RU-07 — Empty or corrupt files

Empty, corrupt, encrypted, or unreadable files produce specific error messages and a replace-file action.

### RU-08 — Privacy default

The file is temporary by default and is not permanently saved unless the user explicitly provides consent.

### RU-09 — Remove and replace

The user can remove the selected file and choose another resume without refreshing the page.

### RU-10 — Accessibility

The complete upload flow can be operated using a keyboard and provides screen-reader status updates.

### RU-11 — Consistent validation

Drag-and-drop and file-picker uploads use the same validation rules and error messages.

### RU-12 — Sensitive-data protection

The system does not send raw resume content to analytics or expose internal storage paths in error messages.

---

## 19. Definition of Done

The Resume Drag-and-Drop Upload feature is complete when:

- The drop zone and file-picker button work on supported browsers.
- PDF, DOCX, and TXT files are supported.
- File name, type, and readable size are displayed.
- Frontend and backend validation are implemented.
- Files exceeding the size limit are rejected.
- Empty, corrupt, encrypted, unsupported, and unreadable files return clear errors.
- Temporary files are automatically deleted according to the retention policy.
- Permanent saving requires explicit user consent.
- Users can remove and replace a selected file.
- Upload and parsing states are visible.
- The component meets the specified keyboard and screen-reader requirements.
- Automated tests cover valid files, invalid types, size limits, corrupt files, and consent behavior.
