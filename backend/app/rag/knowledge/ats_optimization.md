---
category: ats_optimization
tags: [ats, applicant_tracking_system, parsing, keywords, formatting]
source: ats_vendor_docs
priority: high
---

# ATS (Applicant Tracking System) Optimization Guide

## Cách ATS Parse CV
1. **Text Extraction**: OCR cho PDF scan, text layer cho PDF digital, XML cho DOCX
2. **Section Detection**: Header detection (Experience, Education, Skills, etc.)
3. **Entity Extraction**: Dates, Companies, Titles, Skills, Degrees, Certifications
4. **Keyword Matching**: So khớp với JD requirements
5. **Scoring**: Rank ứng viên dựa trên match score

## Top ATS Vendors & Parsing Behavior
| ATS | Parsing Engine | Strengths | Weaknesses |
|-----|---------------|-----------|------------|
| **Greenhouse** | Sovren/Textkernel | Good structure detection | Struggles with multi-column |
| **Lever** | Sovren | Clean parsing | Tables sometimes broken |
| **Workday** | Built-in | Enterprise features | Strict formatting requirements |
| **iCIMS** | Textkernel | High volume | Complex layouts fail |
| **BambooHR** | Built-in | SMB friendly | Limited customization |
| **Ashby** | Modern | Good UX | Newer, less tested |

## Formatting Rules - MUST FOLLOW

### ✅ DO
- Single column layout
- Standard section headers: "Experience", "Education", "Skills", "Projects", "Certifications"
- Bullet points (•, -, *) for achievements
- Dates in consistent format: "Jan 2022 - Present" or "01/2022 - Present"
- Plain text skills list (comma or line separated)
- Standard fonts: Arial, Calibri, Helvetica, Roboto, Inter
- Font size 10-12pt for body, 14-16pt for headers
- Save as PDF (text-based) or DOCX

### ❌ DON'T
- **Tables** - ATS reads row by row,破坏结构
- **Text boxes / Frames** - Often ignored completely
- **Headers/Footers** - Contact info in header may be missed
- **Multi-column layouts** - Parsing order becomes random
- **Graphics/Icons/Charts** - Not parsed, waste space
- **Special characters** as bullets (►, ◆, ★) - use standard bullets
- **Columns for skills** - Put in single list
- **Password-protected PDF** - Auto-reject
- **Image-based PDF** - Requires OCR, error-prone

## Keyword Strategy
1. **Exact Match Priority**: JD yêu cầu "React" → CV phải có "React" (không phải "React.js" hay "ReactJS")
2. **Frequency Matters**: Skill xuất hiện 2-3 lần (Skills section + Experience bullets) score cao hơn
3. **Context Awareness**: "5 years React experience" > "React" alone
4. **Synonyms**: Include both acronym and full form: "CI/CD", "Continuous Integration/Continuous Deployment"
5. **Hard vs Soft Skills**: ATS weights hard skills 3-5x higher than soft skills

## Section-Specific Optimization

### Skills Section
```
Technical Skills
• Languages: Python, Go, TypeScript, Java, SQL
• Frameworks: React, Next.js, FastAPI, Gin, gRPC
• Databases: PostgreSQL, Redis, MongoDB, ClickHouse
• Cloud/DevOps: AWS (ECS, Lambda, RDS), Terraform, Kubernetes, GitHub Actions
• Tools: Git, Docker, Linux, VS Code, Datadog, Prometheus
```

### Experience Section - Keyword Density
Mỗi bullet nên chứa 1-2 hard skills từ JD:
- "Built **REST APIs** using **FastAPI** and **PostgreSQL**, deployed on **AWS ECS** with **Terraform**"
- "Implemented **CI/CD pipelines** with **GitHub Actions**, reduced deployment time from 45min to 8min"

## Testing Your CV
1. **Free ATS Scanners**: Jobscan, Resume Worded, Enhancv (limited free)
2. **Manual Test**: Convert PDF → Text (pdftotext), check if content readable in order
3. **Keyword Check**: Ctrl+F search cho từng skill trong JD
4. **Section Check**: Verify all standard sections detected
