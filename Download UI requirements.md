# UI/UX Redesign Requirements

## AI Resume Analyzer

## 1. Purpose

This document defines the new UI/UX requirements for the AI Resume Analyzer application. The redesigned application must provide a professional public home page, clear login and registration flows, customizable light and dark themes, CV/resume import and storage, an authenticated dashboard, and an AI-powered standalone CV analysis experience.

The interface must never intentionally display a blank screen. Every route and operation must provide visible content, a loading state, an empty state, or a clear error message.

---

## 2. Primary User Flow

The expected user journey is:

```text
Open application
→ View public home page without logging in
→ Select Log In or Register
→ Complete login or registration
→ Redirect to the authenticated dashboard
→ Import and save a CV/resume
→ Select a saved CV/resume
→ Run standalone AI analysis
→ View and save the analysis result
```

---

## 3. General Design Requirements

The new interface must be:

- Professional and appropriate for CV, career, and recruitment use cases.
- Modern, clean, and easy to understand.
- Responsive on desktop, tablet, and mobile devices.
- Consistent in colors, typography, spacing, icons, and component behavior.
- Accessible through keyboard navigation and readable color contrast.
- Clear about loading, success, empty, and error states.
- Designed so that a backend or API error does not cause the entire interface to become blank.

---

## 4. Theme Requirements

### 4.1 Supported Themes

The application must support:

- Light theme.
- Dark theme.
- System theme preference.
- Manual theme selection.

The selected preference should be saved locally and restored the next time the user opens the application.

### 4.2 Visual Direction

Suggested visual style:

- Neutral backgrounds with blue, indigo, teal, or emerald accents.
- Rounded cards with subtle borders and restrained shadows.
- Clear modern sans-serif typography.
- Green for successful or strong results.
- Amber for warnings and improvement opportunities.
- Red for errors and critical issues.
- Consistent icons for home, resume, upload, analysis, history, account, and theme controls.

Color must not be the only way to communicate meaning. Scores and statuses must include text labels and numeric values.

---

## 5. Public Home Page

### 5.1 Public Access

When an unauthenticated visitor opens the application root URL, the public home page must be displayed immediately.

Suggested route:

```text
/
```

The basic public home page must render even if the backend is temporarily unavailable.

### 5.2 Public Header

The public header must include:

- Product logo or application name.
- Home link.
- Features link, where applicable.
- Theme selector.
- `Log In` button.
- `Register` or `Get Started` button.

### 5.3 Hero Section

The hero section should include:

- A clear product title.
- A short description of the product.
- A primary registration action.
- A secondary login action.
- A professional visual related to CV review, AI analysis, or career development.

Suggested content:

```text
Build a Stronger CV with AI

Import your CV, receive an independent AI evaluation, and discover practical ways to improve your professional profile.
```

Suggested buttons:

```text
Get Started
Log In
```

### 5.4 Feature Overview

The public home page should introduce the main capabilities:

- Import and save CV/resume documents.
- Review extracted candidate and resume information.
- Run standalone AI CV analysis.
- View overall and category scores.
- Identify strengths and weaknesses.
- Receive suggestions and practical career advice.
- Review saved analysis results after authentication.

### 5.5 Public Home Page Behavior

- Selecting `Log In` must navigate to `/login`.
- Selecting `Register` or `Get Started` must navigate to `/register`.
- If an unauthenticated visitor opens a protected route, redirect the visitor to `/login`.
- If an authenticated user opens `/`, the application may redirect to `/dashboard` or display a `Go to Dashboard` action.
- The selected behavior must remain consistent throughout the application.

---

## 6. Login Page

Suggested route:

```text
/login
```

### 6.1 Required Fields and Actions

The login page must include:

- Email address or username.
- Password.
- Show or hide password control.
- Remember-me option, where supported.
- `Log In` button.
- Link to the registration page.
- Link back to the public home page.

### 6.2 Form Behavior

The page must:

- Validate required fields.
- Validate email format when email is used.
- Disable repeated submission while the request is processing.
- Display a visible loading indicator.
- Display safe authentication and network error messages.
- Keep the page visible when the backend is unavailable.

Suggested invalid-credentials message:

> Unable to sign in with the provided credentials. Please check your information and try again.

Suggested connection-error message:

> The application cannot connect to the server right now. Please try again shortly.

### 6.3 Successful Login

After a successful login:

1. Create or restore the authenticated session.
2. Load the required user information.
3. Redirect to the authenticated dashboard.

Suggested route:

```text
/dashboard
```

---

## 7. Registration Page

Suggested route:

```text
/register
```

### 7.1 Required Fields

The registration page should include:

- Username or full name.
- Email address.
- Phone number, where required or optional.
- Password.
- Password confirmation.
- Terms and privacy agreement, where required.

### 7.2 Validation

The page must validate:

- Required fields.
- Email format.
- Password requirements.
- Password confirmation.
- Terms acceptance, where required.

The password field must include a show or hide control. Backend validation errors must be shown as understandable field-level or form-level messages.

### 7.3 Successful Registration

After successful registration, use one consistent flow:

```text
Successful registration
→ Display a success message
→ Redirect to /login
```

Alternatively, when the backend supports automatic authentication:

```text
Successful registration
→ Create authenticated session
→ Redirect to /dashboard
```

Redirecting to `/login` is recommended unless the registration endpoint already returns a valid authenticated session.

---

## 8. Authenticated Dashboard / Main Home Page

The authenticated dashboard is the main page displayed after login.

Suggested route:

```text
/dashboard
```

### 8.1 Main Navigation

The authenticated navigation must include:

- Dashboard.
- CVs/Resumes.
- Import CV/Resume.
- Analyze CV.
- Analysis History.
- Account or Settings.
- Logout.

It should also include a theme selector and a visible active-page state.

### 8.2 Dashboard Overview

The dashboard must provide an overview of the application's functions and the user's stored data.

Suggested summary cards:

- Total saved CVs/resumes.
- Total completed analyses.
- Average overall CV score.
- Average ATS score.
- Most recently analyzed CV.

### 8.3 Saved CV/Resume Section

Display recently saved CVs/resumes with:

- Candidate name.
- Original filename.
- File type.
- Upload date.
- Extracted skills preview.
- Latest analysis score, when available.
- Processing or analysis status.

Suggested actions:

- View details.
- Analyze CV.
- Download the original file, where permitted.
- Delete with confirmation.

### 8.4 Recent Analysis Results

Display recent analysis results with:

- Candidate name.
- CV/resume filename.
- Overall score.
- ATS score.
- Analysis date.
- Status.
- `View Result` action.

### 8.5 Dashboard Quick Actions

The dashboard must provide visible actions for:

- Import CV/Resume.
- Analyze a saved CV.
- View all saved CVs.
- View analysis history.

### 8.6 Empty Dashboard

A new user with no stored data must see a helpful empty state instead of an empty screen.

Suggested message:

> No CVs have been saved yet. Import your first CV to begin AI analysis.

Suggested action:

```text
Import CV/Resume
```

### 8.7 Dashboard API Failure

If dashboard data cannot be loaded:

- Keep the application shell and navigation visible.
- Display an error inside the affected content area.
- Provide a retry button.
- Do not redirect the user to a blank page.

Suggested message:

> The dashboard is available, but saved data could not be loaded. Check the server connection and try again.

---

## 9. CV/Resume Storage and Import Page

## 9.1 CV/Resume List Page

Suggested route:

```text
/resumes
```

The page must display all CV/resume records saved by the authenticated user.

Required features:

- Search by candidate name or filename.
- Sort by upload date, candidate name, or latest score.
- Filter by file type or analysis status.
- Card or table view.
- Pagination or incremental loading when needed.
- Helpful empty state.

Each record should include:

- Candidate name.
- Filename.
- File type.
- Upload date.
- Skills preview.
- Latest overall score, when available.
- Latest ATS score, when available.
- Analysis status.

Record actions:

- View CV details.
- Analyze CV.
- Download, where supported.
- Delete with confirmation.

## 9.2 Import CV/Resume Page

Suggested route:

```text
/resumes/import
```

### Upload Area

The import page must:

- Support drag-and-drop.
- Support file selection.
- Display accepted formats, including PDF and DOCX.
- Display the configured maximum file size.
- Show the selected filename and file size.
- Allow the selected file to be replaced.
- Show upload and processing progress.

### Processing Steps

The UI should display the current stage:

1. Uploading the document.
2. Validating file type and size.
3. Checking whether the document is a CV/resume.
4. Extracting text.
5. Extracting structured CV information.
6. Preparing extracted information for review.
7. Saving the CV/resume.

### Invalid CV/Resume

If the uploaded document is not recognized as a CV/resume, display:

> This document does not appear to be a CV or resume. Please upload a valid CV in PDF or DOCX format.

The user must remain on the import page and be able to select another file immediately. Invalid documents must not be presented as saved CVs.

### Extracted Data Review

Before saving, display available extracted information grouped into sections:

- Candidate information.
- Contact information.
- Professional summary.
- Education.
- Work experience.
- Skills.
- Projects.
- Certifications.
- Interests.
- Activities.
- Honors and awards.

If the source CV does not contain information for a supported field:

- Display an empty field or `Not provided`.
- Do not display fabricated information.
- Allow correction or manual entry where editing is supported.

### Save Actions

- Save CV/Resume.
- Save and Analyze.
- Cancel.

## 9.3 CV/Resume Detail Page

Suggested route:

```text
/resumes/:resumeId
```

The detail page must display:

- File metadata.
- Candidate profile.
- Extracted CV data grouped into sections.
- Skills with available proficiency or confidence information.
- Previous analysis results.
- Actions to analyze, edit permitted fields, download, or delete.

---

## 10. Standalone AI CV Analysis Page

Suggested route:

```text
/analyze
```

This page analyzes one saved CV/resume independently, without requiring a Job Description.

### 10.1 Select a Saved CV

The user must be able to:

- Search saved CVs/resumes.
- Select one CV/resume.
- Preview candidate name, filename, upload date, and extracted skills.
- Navigate to CV import when no saved CV exists.

### 10.2 Start Analysis

The page must explain that the AI model will independently evaluate the selected CV.

The primary action should be:

```text
Analyze CV
```

The button must be disabled while analysis is running to prevent duplicate requests.

### 10.3 Processing State

The UI should display progress through stages such as:

1. Loading the saved CV data.
2. Preparing extracted content.
3. Evaluating ATS compatibility.
4. Evaluating work experience.
5. Evaluating education.
6. Evaluating skills and content quality.
7. Generating strengths and weaknesses.
8. Generating suggestions and advice.
9. Saving the analysis result.

### 10.4 Analysis Result

The result page must display all available results returned by the AI model, including:

- Overall score.
- ATS score.
- Skill score.
- Work experience score.
- Education score.
- Strengths.
- Weaknesses.
- Suggestions.
- Practical advice.
- Recommended next steps.

### 10.5 Recommended Result Layout

The result page should include:

1. Header with candidate name, filename, analysis date, and status.
2. Main score cards.
3. Score visualization such as a radar chart or bar chart.
4. Strengths section.
5. Weaknesses section.
6. Suggestions grouped by priority.
7. Practical advice section.
8. Recommended next actions.

### 10.6 Score Presentation

Suggested score groups:

- `80–100`: Strong.
- `60–79`: Good, with recommended improvements.
- `40–59`: Moderate, with important gaps.
- `0–39`: Weak, requiring significant improvement.

Every score must include:

- Numeric value.
- Text label.
- Visual indicator.

### 10.7 Result Actions

The result must be saved automatically after successful analysis.

Available actions should include:

- View saved result.
- Reanalyze CV.
- Return to CV details.
- View analysis history.
- Export or download the report, where supported.
- Return to dashboard.

The interface must state that AI-generated evaluation is advisory and may require human review.

---

## 11. Analysis History Page

Suggested route:

```text
/analysis-history
```

The page must display stored analysis results.

Required features:

- Search by candidate name or filename.
- Filter by status, date, or score range.
- Sort by newest, oldest, overall score, or ATS score.
- Open analysis details.
- Reanalyze a CV.
- Delete a result when permitted.

Each history record should display:

- Candidate name.
- Filename.
- Overall score.
- ATS score.
- Analysis date.
- Analysis status.

---

## 12. Routing and Access Control

### Public Routes

```text
/
/login
/register
```

### Protected Routes

```text
/dashboard
/resumes
/resumes/import
/resumes/:resumeId
/analyze
/analyze/:analysisId
/analysis-history
/settings
```

### Route Rules

- Unauthenticated access to a protected route must redirect to `/login`.
- Successful login must redirect to `/dashboard`.
- Unknown routes must display a visible 404 page.
- Authentication restoration must display a loading state and must not render `null` indefinitely.

---

## 13. Loading, Empty, Success, and Error States

Every page must implement:

### Loading State

- Visible spinner, skeleton, or progress indicator.
- Clear processing text.
- Disabled duplicate actions.

### Empty State

- Clear explanation of missing data.
- Relevant next action.

### Success State

Use confirmation messages for:

- Registration completed.
- Login completed.
- CV/resume saved.
- Analysis completed and saved.
- Record deleted.

### Error State

Errors must:

- Use clear, user-friendly language.
- Explain the next action.
- Include retry where appropriate.
- Avoid exposing stack traces, internal API details, or model-provider secrets.

### Unexpected Frontend Error

An application-level error boundary must display a recovery page instead of a blank screen.

Suggested message:

> The application encountered an unexpected error. Reload the page or return to the home page.

---

## 14. Frontend and Backend Integration

The frontend must:

- Read the backend URL from environment configuration.
- Use a shared API client.
- Normalize authentication, validation, network, timeout, and server errors.
- Keep public static UI visible when the backend is unavailable.
- Display retry options for failed dashboard and analysis requests.

Example environment variable:

```text
VITE_API_BASE_URL=http://localhost:8000
```

The backend should provide a health endpoint:

```http
GET /health
```

Suggested response:

```json
{
  "status": "ok",
  "service": "ai-resume-analyzer-api"
}
```

The backend must configure CORS for approved frontend origins.

---

## 15. Responsive Design

### Desktop

- Use sidebar or full top navigation.
- Use multi-column dashboard layouts.
- Display data tables where appropriate.

### Tablet

- Reduce the number of columns.
- Collapse secondary controls.
- Preserve readable scores and charts.

### Mobile

- Use a single-column layout.
- Use a navigation drawer or compact mobile navigation.
- Convert wide tables into cards or scrollable containers.
- Keep upload controls and primary actions easy to use.
- Keep charts and analysis sections readable.

---

## 16. Accessibility

The UI must:

- Support keyboard navigation.
- Provide visible focus indicators.
- Use labels for form fields.
- Provide accessible names for icon-only buttons.
- Maintain sufficient contrast in light and dark modes.
- Avoid depending only on color for scores and statuses.
- Provide text descriptions for charts.
- Announce asynchronous success and error messages.
- Respect reduced-motion preferences where possible.

---

## 17. Suggested Reusable Components

- Public navigation bar.
- Authenticated application shell.
- Sidebar and mobile navigation.
- Theme switcher.
- Login form.
- Registration form.
- File drop zone.
- Processing stepper.
- CV/resume card.
- Candidate summary card.
- Score card.
- Score badge.
- Skills list.
- Chart wrapper.
- Strengths panel.
- Weaknesses panel.
- Suggestions panel.
- Advice panel.
- Search input.
- Filter controls.
- Empty-state component.
- Loading skeleton.
- Error alert.
- Toast notification.
- Confirmation dialog.
- Application error boundary.

---

## 18. Acceptance Criteria

### AC-01: Public Home Page

**Given** a visitor is not authenticated,  
**When** the application root URL is opened,  
**Then** the public home page is visible with `Log In` and `Register` actions.

### AC-02: Public Rendering Without Backend

**Given** the backend is temporarily unavailable,  
**When** a visitor opens the application,  
**Then** the public home page still renders and does not become blank.

### AC-03: Login Navigation

**Given** the visitor is on the public home page,  
**When** `Log In` is selected,  
**Then** the login page is displayed.

### AC-04: Registration Navigation

**Given** the visitor is on the public home page,  
**When** `Register` or `Get Started` is selected,  
**Then** the registration page is displayed.

### AC-05: Successful Login

**Given** valid credentials are submitted,  
**When** authentication succeeds,  
**Then** the user is redirected to the authenticated dashboard.

### AC-06: Dashboard Overview

**Given** an authenticated user has saved CVs and analyses,  
**When** the dashboard is opened,  
**Then** saved CVs, recent analysis results, summary information, and quick actions are displayed.

### AC-07: Empty Dashboard

**Given** an authenticated user has no saved CVs or analyses,  
**When** the dashboard is opened,  
**Then** a useful empty state and CV import action are displayed.

### AC-08: CV Import

**Given** an authenticated user uploads a supported CV/resume,  
**When** validation and extraction succeed,  
**Then** the application displays extracted information for review and allows the CV to be saved.

### AC-09: Invalid CV Document

**Given** an uploaded document is not a CV/resume,  
**When** validation finishes,  
**Then** the page displays a clear error, does not save the document as a CV, and allows another file to be selected.

### AC-10: Missing CV Information

**Given** a valid CV lacks one or more supported fields,  
**When** extracted data is displayed,  
**Then** missing values are shown as empty or `Not provided`, without fabricated content.

### AC-11: Standalone CV Analysis

**Given** a saved CV is selected,  
**When** AI analysis succeeds,  
**Then** the page displays scores, strengths, weaknesses, suggestions, advice, and saves the result.

### AC-12: Analysis Failure

**Given** an AI or backend request fails,  
**When** the failure is received,  
**Then** the interface remains visible, preserves the selected CV, displays a safe error, and provides retry where appropriate.

### AC-13: Theme Selection

**Given** a visitor or authenticated user changes the theme,  
**When** light, dark, or system theme is selected,  
**Then** the complete interface updates and remembers the preference.

### AC-14: Protected Routes

**Given** a visitor is not authenticated,  
**When** a protected route is opened,  
**Then** the visitor is redirected to the login page rather than seeing protected content or a blank page.

### AC-15: Responsive Interface

**Given** the application is used on desktop, tablet, or mobile,  
**When** the viewport changes,  
**Then** public pages, authentication pages, dashboard, import forms, and analysis results remain readable and usable.

### AC-16: Unexpected Rendering Error

**Given** an unexpected frontend error occurs,  
**When** the error is caught,  
**Then** the application displays a recovery page instead of a blank screen.

---

## 19. Implementation Priorities

### Priority 1: Public Startup and Authentication

- Implement the public home page.
- Add login and registration navigation.
- Implement protected routes.
- Redirect successful login to the dashboard.
- Add startup loading and error states.
- Add an application-level error boundary.

### Priority 2: Authenticated Dashboard

- Implement the dashboard shell and navigation.
- Display saved CVs and recent analyses.
- Add summary cards and quick actions.
- Add empty and API-error states.

### Priority 3: CV/Resume Import and Storage UI

- Implement CV list, import, review, detail, and delete flows.
- Display validation and extraction progress.
- Handle non-CV documents.
- Display missing extracted information correctly.

### Priority 4: Standalone AI CV Analysis

- Implement saved-CV selection.
- Display AI processing stages.
- Display scores, strengths, weaknesses, suggestions, and advice.
- Persist and display analysis history.

### Priority 5: Theme, Responsiveness, and Accessibility

- Complete light, dark, and system themes.
- Test desktop, tablet, and mobile layouts.
- Review keyboard navigation, labels, focus states, and contrast.

---

## 20. Definition of Done

The UI redesign is complete when:

- Opening the application while logged out displays a public home page.
- Public login and registration buttons work correctly.
- Login and registration forms display validation, loading, success, and error states.
- Successful login redirects to the authenticated dashboard.
- Protected routes redirect unauthenticated visitors to login.
- The dashboard displays saved CVs, recent analysis results, summary information, and quick actions.
- New users receive useful empty states.
- Users can import, validate, review, and save CV/resume data.
- Non-CV files are rejected with a clear message.
- Users can select a saved CV and run standalone AI analysis.
- Analysis results include available scores, strengths, weaknesses, suggestions, and practical advice.
- Successful analysis results are saved and available in analysis history.
- Light, dark, and system themes work consistently.
- Backend errors do not cause blank pages.
- An application error boundary handles unexpected frontend failures.
- Desktop, tablet, and mobile layouts are tested.
- Accessibility requirements are reviewed.
- Critical user flows are covered by automated or documented UI tests.
