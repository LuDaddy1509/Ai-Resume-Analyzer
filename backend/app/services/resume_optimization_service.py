"""
Resume Optimization Engine Service

Rewrites resume sections for ATS optimization and human appeal:
- Professional summary tailored to JD
- Bullet points converted to STAR format with metrics
- Skills section optimized for keyword density
- Version comparison and ATS score prediction
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Optional, Any
import json
import re
from datetime import datetime

from app.models.resume_optimization import ResumeOptimization, OptimizationStatus
from app.models.resumes import Resume
from app.models.analyses import Analysis
from app.models.job_description import JobDescription
from app.models.work_experiences import WorkExperience
from app.models.education import Education
from app.models.projects import Project
from app.models.certifications import Certification
from app.models.skills import Skill
from app.models.resume_skills import ResumeSkill
from app.services.llm_analyzer import LLMAnalyzer
from app.services.parser_service import KNOWN_SKILLS, _extract_skills
from app.rag.vector_store import ResumeRAG


class ResumeOptimizationService:
    def __init__(self):
        self.llm_analyzer = LLMAnalyzer()
        self.rag = ResumeRAG()

    def _load_resume_data(self, resume: Resume, db: Session) -> Dict:
        """Load all resume data into a structured dict"""
        # Get experiences
        experiences = []
        for exp in resume.work_experiences:
            experiences.append({
                "company": exp.company,
                "position": exp.position,
                "location": exp.location,
                "start_date": exp.start_date.isoformat() if exp.start_date else None,
                "end_date": exp.end_date.isoformat() if exp.end_date else None,
                "is_current": exp.is_current == "true",
                "description": exp.description,
                "achievements": exp.achievements
            })

        # Get education
        education = []
        for edu in resume.educations:
            education.append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "start_date": edu.start_date.isoformat() if edu.start_date else None,
                "end_date": edu.end_date.isoformat() if edu.end_date else None,
                "grade": edu.grade,
                "activities": edu.activities,
                "description": edu.description
            })

        # Get projects
        projects = []
        for proj in resume.projects:
            projects.append({
                "name": proj.name,
                "description": proj.description,
                "technologies": proj.technologies,
                "start_date": proj.start_date.isoformat() if proj.start_date else None,
                "end_date": proj.end_date.isoformat() if proj.end_date else None,
                "project_url": proj.project_url,
                "github_url": proj.github_url
            })

        # Get certifications
        certifications = []
        for cert in resume.certifications:
            certifications.append({
                "name": cert.name,
                "issuer": cert.issuer,
                "issue_date": cert.issue_date.isoformat() if cert.issue_date else None,
                "expiry_date": cert.expiry_date.isoformat() if cert.expiry_date else None,
                "credential_id": cert.credential_id,
                "credential_url": cert.credential_url
            })

        # Get skills
        skills = []
        for rs in resume.resume_skills:
            if rs.skill:
                skills.append({
                    "name": rs.skill.name,
                    "category": rs.skill.category,
                    "proficiency_level": rs.proficiency_level,
                    "years_of_experience": rs.years_of_experience
                })

        return {
            "full_name": resume.parsed_text[:100] if resume.parsed_text else "",  # placeholder
            "email": "",
            "phone": "",
            "skills": [s["name"] for s in skills],
            "experiences": experiences,
            "education": education,
            "projects": projects,
            "certifications": certifications,
            "skills_detailed": skills
        }

    def _calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density in text"""
        if not text:
            return {}

        text_lower = text.lower()
        total_words = len(text_lower.split())
        density = {}

        for keyword in keywords:
            count = len(re.findall(rf"\b{re.escape(keyword.lower())}\b", text_lower))
            density[keyword] = (count / total_words * 100) if total_words > 0 else 0

        return density

    def _extract_jd_keywords(self, jd: JobDescription) -> List[str]:
        """Extract keywords from job description"""
        if jd.extracted_keywords:
            try:
                return json.loads(jd.extracted_keywords)
            except:
                pass

        # Fallback: extract from raw text
        return _extract_skills(jd.raw_text)

    async def optimize_resume(
        self,
        resume_id: int,
        analysis_id: Optional[int],
        job_description_id: Optional[int],
        db: Session
    ) -> ResumeOptimization:
        """
        Main entry point: Optimize a resume for ATS and human appeal.
        """
        # Get resume
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("Resume not found")

        # Get analysis if provided
        analysis = None
        if analysis_id:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

        # Get JD if provided
        jd = None
        jd_keywords = []
        if job_description_id:
            jd = db.query(JobDescription).filter(JobDescription.id == job_description_id).first()
            if jd:
                jd_keywords = self._extract_jd_keywords(jd)

        # Load resume data
        resume_data = self._load_resume_data(resume, db)

        # Create optimization record
        optimization = ResumeOptimization(
            resume_id=resume_id,
            analysis_id=analysis_id,
            job_description_id=job_description_id,
            status=OptimizationStatus.IN_PROGRESS,
            original_summary="",  # Will be filled from parsed text
            original_skills=resume_data["skills"],
            original_experiences=resume_data["experiences"],
            original_projects=resume_data["projects"],
            original_education=resume_data["education"]
        )
        db.add(optimization)
        db.commit()
        db.refresh(optimization)

        try:
            # Calculate original ATS score
            original_text = resume.parsed_text or ""
            optimization.original_ats_score = self._calculate_ats_score(original_text, jd_keywords)

            # Calculate original match score if JD provided
            if jd_keywords and analysis:
                optimization.original_match_score = analysis.match_score

            # Perform optimization
            optimized_data = await self._optimize_sections(
                resume_data=resume_data,
                jd=jd,
                jd_keywords=jd_keywords,
                analysis=analysis
            )

            # Save optimized content
            optimization.optimized_summary = optimized_data["summary"]
            optimization.optimized_skills = optimized_data["skills"]
            optimization.optimized_experiences = optimized_data["experiences"]
            optimization.optimized_projects = optimized_data["projects"]
            optimization.optimized_education = optimized_data["education"]

            # Calculate optimized ATS score
            optimized_text = self._build_full_text(optimized_data)
            optimization.optimized_ats_score = self._calculate_ats_score(optimized_text, jd_keywords)

            # Calculate improvements
            if optimization.original_ats_score and optimization.optimized_ats_score:
                optimization.ats_improvement = optimization.optimized_ats_score - optimization.original_ats_score

            if optimization.original_match_score and jd_keywords:
                # Estimate match improvement based on keyword coverage
                original_density = self._calculate_keyword_density(original_text, jd_keywords)
                optimized_density = self._calculate_keyword_density(optimized_text, jd_keywords)
                optimization.keyword_density_before = original_density
                optimization.keyword_density_after = optimized_density

                # Estimate match score improvement
                matched_before = sum(1 for k, v in original_density.items() if v > 0)
                matched_after = sum(1 for k, v in optimized_density.items() if v > 0)
                if len(jd_keywords) > 0:
                    optimization.optimized_match_score = min(
                        (matched_after / len(jd_keywords)) * 100, 100
                    )
                    optimization.match_improvement = optimization.optimized_match_score - (optimization.original_match_score or 0)

            # Record optimization notes
            optimization.optimization_notes = optimized_data.get("notes", [])

            optimization.status = OptimizationStatus.COMPLETED
            optimization.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(optimization)

            return optimization

        except Exception as e:
            optimization.status = OptimizationStatus.FAILED
            optimization.optimization_notes = [f"Error: {str(e)}"]
            db.commit()
            raise

    async def _optimize_sections(
        self,
        resume_data: Dict,
        jd: Optional[JobDescription],
        jd_keywords: List[str],
        analysis: Optional[Analysis]
    ) -> Dict:
        """Optimize all resume sections using LLM + RAG"""

        # Build context for LLM
        jd_text = jd.raw_text if jd else ""
        resume_text = self._build_full_text(resume_data)

        # Use RAG to get best practices
        query = f"Resume optimization ATS best practices for {jd.title if jd else 'tech role'}"
        docs = self.rag.retrieve(query, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Generate optimized content using LLM
        if self.llm_analyzer.llm:
            optimized = await self._llm_optimize(
                resume_data=resume_data,
                jd_text=jd_text,
                jd_keywords=jd_keywords,
                context=context,
                analysis=analysis
            )
        else:
            optimized = self._rule_based_optimize(resume_data, jd_keywords, analysis)

        return optimized

    async def _llm_optimize(
        self,
        resume_data: Dict,
        jd_text: str,
        jd_keywords: List[str],
        context: str,
        analysis: Optional[Analysis]
    ) -> Dict:
        """Use LLM to optimize resume sections"""

        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import PydanticOutputParser
        from pydantic import BaseModel, Field
        from typing import List, Optional

        class OptimizedResume(BaseModel):
            summary: str = Field(..., description="Optimized professional summary (3-4 lines)")
            skills: List[str] = Field(..., description="Optimized skills list prioritized for JD")
            experiences: List[Dict] = Field(..., description="Optimized experiences with STAR bullets")
            projects: List[Dict] = Field(..., description="Optimized projects")
            education: List[Dict] = Field(..., description="Optimized education")
            notes: List[str] = Field(default=[], description="List of changes made")

        parser = PydanticOutputParser(pydantic_object=OptimizedResume)

        prompt = PromptTemplate(
            template="""Bạn là **Senior Technical Recruiter & ATS Optimization Expert** với 15+ năm kinh nghiệm.

**Kiến thức tham khảo (ATS Best Practices):**
{context}

**CV gốc của ứng viên:**
{resume_text}

**Job Description (nếu có):**
{jd_text}

**Từ khóa quan trọng từ JD:**
{jd_keywords}

**Phân tích hiện tại (nếu có):**
{analysis_info}

**Nhiệm vụ:** Tối ưu hóa từng section của CV để:
1. **ATS-friendly**: Từ khóa chính xác từ JD, density phù hợp, format chuẩn
2. **Human appeal**: STAR method, định lượng kết quả, động từ mạnh
3. **Tailored**: Tùy chỉnh cho JD cụ thể (nếu có)

**Yêu cầu chi tiết:**

1. **Professional Summary (3-4 dòng):**
   - Bao gồm: Role hiện tại, năm kinh nghiệm, 3-4 core skills từ JD, value proposition
   - Không dùng cliché ("hardworking", "team player")

2. **Skills (ưu tiên theo JD):**
   - Nhóm: Languages, Frameworks, Databases, Cloud/DevOps, Tools
   - Ưu tiên skills có trong JD lên đầu
   - Thêm synonyms (React + React.js, AWS + Amazon Web Services)

3. **Experience (STAR method cho bullets):**
   - Mỗi bullet: Action verb + Context + Metric/Result
   - Định lượng: % improvement, $ saved, time reduced, scale handled
   - Tự nhiên nhúng từ khóa JD vào bullets

4. **Projects (2-3 projects nổi bật):**
   - Name, 1-sentence description, tech stack, impact/result, link

5. **Education (concise):**
   - Degree, major, institution, honors (nếu có), relevant coursework (cho junior)

**Output:** JSON hợp lệ theo schema. Chỉ trả về JSON.

{format_instructions}""",
            input_variables=["context", "resume_text", "jd_text", "jd_keywords", "analysis_info"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        chain = prompt | self.llm_analyzer.llm | parser

        analysis_info = ""
        if analysis:
            analysis_info = f"""
Match Score: {analysis.match_score}%
Matched Skills: {analysis.skills_match}
Missing Skills: {analysis.missing_skills}
Strengths: {analysis.strengths}
Weaknesses: {analysis.weaknesses}
"""

        try:
            result = await chain.ainvoke({
                "context": context,
                "resume_text": resume_text[:15000],
                "jd_text": jd_text[:5000] if jd_text else "Không có JD",
                "jd_keywords": ", ".join(jd_keywords) if jd_keywords else "Không có",
                "analysis_info": analysis_info
            })
            return result.model_dump()
        except Exception as e:
            print(f"LLM Optimization Error: {e}")
            return self._rule_based_optimize(resume_data, jd_keywords, analysis)

    def _rule_based_optimize(
        self,
        resume_data: Dict,
        jd_keywords: List[str],
        analysis: Optional[Analysis]
    ) -> Dict:
        """Fallback rule-based optimization"""
        notes = []

        # Optimize summary
        summary = self._generate_summary(resume_data, jd_keywords)
        notes.append("Generated professional summary tailored to JD keywords")

        # Optimize skills - prioritize JD keywords
        current_skills = set(s.lower() for s in resume_data.get("skills", []))
        jd_skills_lower = set(k.lower() for k in jd_keywords)

        # Add missing JD skills as "learning" or prioritize existing
        optimized_skills = list(resume_data.get("skills", []))
        for kw in jd_keywords:
            if kw.lower() not in current_skills:
                optimized_skills.insert(0, f"{kw} (learning)")
                notes.append(f"Added missing JD keyword: {kw}")

        # Reorder: JD skills first, then others
        jd_skills = [s for s in optimized_skills if s.lower() in jd_skills_lower]
        other_skills = [s for s in optimized_skills if s.lower() not in jd_skills_lower]
        optimized_skills = jd_skills + other_skills
        notes.append("Reordered skills to prioritize JD keywords")

        # Optimize experiences - enhance bullets with STAR
        optimized_experiences = []
        for exp in resume_data.get("experiences", []):
            enhanced = exp.copy()
            bullets = exp.get("achievements") or exp.get("bullets") or []

            if bullets:
                enhanced_bullets = []
                for bullet in bullets:
                    enhanced_bullet = self._enhance_bullet(bullet, jd_keywords)
                    enhanced_bullets.append(enhanced_bullet)
                enhanced["bullets"] = enhanced_bullets
                enhanced["achievements"] = enhanced_bullets
                notes.append(f"Enhanced bullets for {exp.get('position')} at {exp.get('company')} with STAR format")
            optimized_experiences.append(enhanced)

        # Optimize projects
        optimized_projects = []
        for proj in resume_data.get("projects", []):
            enhanced = proj.copy()
            if proj.get("description"):
                enhanced["description"] = self._enhance_project_description(proj["description"], jd_keywords)
            optimized_projects.append(enhanced)

        # Education - minimal changes
        optimized_education = resume_data.get("education", [])

        return {
            "summary": summary,
            "skills": optimized_skills,
            "experiences": optimized_experiences,
            "projects": optimized_projects,
            "education": optimized_education,
            "notes": notes
        }

    def _generate_summary(self, resume_data: Dict, jd_keywords: List[str]) -> str:
        """Generate a professional summary"""
        experiences = resume_data.get("experiences", [])
        skills = resume_data.get("skills", [])

        # Get current/last role
        current_role = ""
        years_exp = 0
        if experiences:
            last_exp = experiences[0]
            current_role = last_exp.get("position", "")
            # Estimate years from dates
            try:
                if last_exp.get("start_date"):
                    from datetime import datetime
                    start = datetime.fromisoformat(last_exp["start_date"].replace("Z", "+00:00"))
                    years_exp = (datetime.now() - start).days // 365
            except:
                pass

        # Top JD skills present in resume
        matching_skills = [s for s in skills if s.lower() in [k.lower() for k in jd_keywords]][:4]

        parts = []
        if current_role:
            parts.append(f"{current_role} với {years_exp}+ năm kinh nghiệm" if years_exp else current_role)
        if matching_skills:
            parts.append(f"Chuyên về {', '.join(matching_skills)}")
        if skills:
            other_skills = [s for s in skills if s not in matching_skills][:3]
            if other_skills:
                parts.append(f"Thành thạo: {', '.join(other_skills)}")

        return ". ".join(parts) + "." if parts else "IT Professional seeking new opportunities."

    def _enhance_bullet(self, bullet: str, jd_keywords: List[str]) -> str:
        """Enhance a bullet point with STAR format"""
        # Already good if it has metrics
        if re.search(r"\d+%|\d+x|\$\d+|\d+\s*(users|requests|transactions|GB|TB)", bullet, re.IGNORECASE):
            return bullet

        # Try to add JD keywords naturally
        enhanced = bullet
        for kw in jd_keywords[:3]:  # Add up to 3 keywords
            if kw.lower() not in bullet.lower():
                # Simple insertion - in reality would be more sophisticated
                enhanced = f"{bullet} (using {kw})"
                break

        return enhanced

    def _enhance_project_description(self, description: str, jd_keywords: List[str]) -> str:
        """Enhance project description"""
        # Add tech stack if missing
        tech_in_desc = [kw for kw in jd_keywords if kw.lower() in description.lower()]
        if len(tech_in_desc) < 2 and jd_keywords:
            description += f" | Tech: {', '.join(jd_keywords[:5])}"
        return description

    def _build_full_text(self, resume_data: Dict) -> str:
        """Build full text representation of resume for scoring"""
        parts = []

        if resume_data.get("summary"):
            parts.append(resume_data["summary"])

        if resume_data.get("skills"):
            parts.append("Skills: " + ", ".join(resume_data["skills"]))

        for exp in resume_data.get("experiences", []):
            parts.append(f"{exp.get('position', '')} at {exp.get('company', '')}")
            if exp.get("bullets"):
                parts.extend(exp["bullets"])
            if exp.get("achievements"):
                parts.extend(exp["achievements"])
            if exp.get("description"):
                parts.append(exp["description"])

        for proj in resume_data.get("projects", []):
            parts.append(f"Project: {proj.get('name', '')}")
            if proj.get("description"):
                parts.append(proj["description"])
            if proj.get("technologies"):
                parts.append(proj["technologies"])

        return "\n".join(parts)

    def _calculate_ats_score(self, text: str, jd_keywords: List[str]) -> float:
        """
        Calculate ATS compatibility score (0-100).
        Based on: keyword presence, formatting, structure, contact info.
        """
        if not text:
            return 0.0

        score = 0.0
        text_lower = text.lower()

        # 1. Keyword coverage (40 points)
        if jd_keywords:
            matched = sum(1 for kw in jd_keywords if kw.lower() in text_lower)
            score += (matched / len(jd_keywords)) * 40
        else:
            score += 20  # Base if no JD

        # 2. Contact info (10 points)
        if re.search(r"[\w\.\-+]+@[\w\.\-]+\.\w{2,}", text):
            score += 5
        if re.search(r"(?:\+84|84|0)\d{9,10}", text):
            score += 5

        # 3. Structure (20 points)
        sections = ["experience", "education", "skills", "project", "certification"]
        found_sections = sum(1 for s in sections if re.search(s, text_lower))
        score += (found_sections / len(sections)) * 20

        # 4. Quantifiable achievements (15 points)
        metrics = len(re.findall(r"\d+%|\d+x|\$\d+|\d+\s*(users|requests|transactions|GB|TB|ms|sec)", text_lower))
        score += min(metrics * 3, 15)

        # 5. Action verbs (10 points)
        action_verbs = ["developed", "built", "designed", "implemented", "led", "managed", "optimized",
                       "created", "architected", "delivered", "improved", "reduced", "increased",
                       "automated", "deployed", "configured", "maintained", "resolved"]
        verb_count = sum(1 for v in action_verbs if v in text_lower)
        score += min(verb_count * 1, 10)

        # 6. Formatting penalties (deductions)
        if "table" in text_lower:
            score -= 5
        if "column" in text_lower:
            score -= 3

        return max(0, min(100, score))

    def get_optimization(self, optimization_id: int, db: Session) -> Optional[ResumeOptimization]:
        """Get optimization by ID"""
        return db.query(ResumeOptimization).filter(ResumeOptimization.id == optimization_id).first()

    def get_resume_optimizations(self, resume_id: int, db: Session) -> List[ResumeOptimization]:
        """Get all optimizations for a resume"""
        return db.query(ResumeOptimization).filter(
            ResumeOptimization.resume_id == resume_id
        ).order_by(ResumeOptimization.created_at.desc()).all()

    def compare_versions(self, optimization: ResumeOptimization) -> Dict:
        """Generate side-by-side comparison of original vs optimized"""
        return {
            "summary": {
                "original": optimization.original_summary,
                "optimized": optimization.optimized_summary
            },
            "skills": {
                "original": optimization.original_skills,
                "optimized": optimization.optimized_skills
            },
            "experiences": {
                "original": optimization.original_experiences,
                "optimized": optimization.optimized_experiences
            },
            "projects": {
                "original": optimization.original_projects,
                "optimized": optimization.optimized_projects
            },
            "education": {
                "original": optimization.original_education,
                "optimized": optimization.optimized_education
            },
            "scores": {
                "original_ats": optimization.original_ats_score,
                "optimized_ats": optimization.optimized_ats_score,
                "ats_improvement": optimization.ats_improvement,
                "original_match": optimization.original_match_score,
                "optimized_match": optimization.optimized_match_score,
                "match_improvement": optimization.match_improvement
            },
            "keyword_density": {
                "before": optimization.keyword_density_before,
                "after": optimization.keyword_density_after
            },
            "notes": optimization.optimization_notes
        }