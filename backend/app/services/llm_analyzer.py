from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from app.rag.vector_store import ResumeRAG
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AnalysisResult(BaseModel):
    overall_score: int = Field(..., description="Điểm tổng thể 0-100")
    ats_score: int = Field(..., description="Điểm tương thích ATS")
    strengths: List[str] = Field(..., description="Điểm mạnh")
    weaknesses: List[str] = Field(..., description="Điểm yếu")
    skill_gaps: List[str] = Field(..., description="Kỹ năng thiếu")
    suggestions: List[str] = Field(..., description="Gợi ý cải thiện")
    match_score: Optional[int] = Field(None, description="Điểm khớp với JD")


class LLMAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.llm = None
        else:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.2,
                api_key=api_key
            )

        self.rag = ResumeRAG()
        self.parser = PydanticOutputParser(pydantic_object=AnalysisResult)

        self.prompt = PromptTemplate(
            template="""Bạn là **Senior Technical Recruiter** với 12+ năm kinh nghiệm tại Google, Meta và FPT Software.

**Kiến thức tham khảo từ RAG (Best Practices CV & Job Market):**
{context}

**CV của ứng viên:**
{resume_text}

{job_description_section}

**Yêu cầu phân tích chi tiết:**

1. **Overall Score** (0-100): Điểm tổng thể.
2. **ATS Score** (0-100): Tính tương thích ATS.
3. **Strengths**: 4-6 điểm mạnh nổi bật.
4. **Weaknesses**: 3-5 điểm yếu rõ ràng.
5. **Skill Gaps**: Kỹ năng còn thiếu so với JD.
6. **Suggestions**: Gợi ý **cụ thể, actionable**.

**Hướng dẫn output:**
- Trả về **JSON hợp lệ** theo đúng schema.
- Sử dụng tiếng Việt chuyên nghiệp.
- Suggestions phải thực tế, có thể áp dụng ngay.
- Dựa vào context RAG để đưa ra lời khuyên chính xác.

{format_instructions}

**Chỉ trả về JSON, không thêm bất kỳ ký tự hoặc giải thích nào.**""",
            input_variables=["context", "resume_text", "job_description_section"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    async def analyze(self, resume_text: str, job_description: str = None):
        if not self.llm:
            return self._fallback_analyze(resume_text, job_description)

        # Build retrieval query from resume + optional JD
        query = f"Phân tích CV với kỹ năng: {resume_text[:800]}"
        if job_description:
            query += f" và JD: {job_description[:500]}"

        # Use get_context() for hybrid retrieval + token budget management
        try:
            context = self.rag.get_context(
                query=query,
                resume_text=resume_text or "",
                job_description=job_description or "",
                max_context_tokens=3000,
                use_hybrid=True,
            )
        except Exception as e:
            logger.warning("RAG get_context failed, fallback to empty context: %s", e)
            context = ""

        jd_section = (
            f"**Job Description:**\n{job_description}\n"
            if job_description
            else "Không có Job Description."
        )

        chain = self.prompt | self.llm | self.parser

        try:
            result = await chain.ainvoke({
                "context": context,
                "resume_text": resume_text[:18000],
                "job_description_section": jd_section,
            })
            return result
        except Exception as e:
            logger.error("LLM Error: %s", e)
            return self._fallback_analyze(resume_text, job_description)

    def _fallback_analyze(self, resume_text: str, job_description: str):
        try:
            from app.services.resume_analyzer import ResumeAnalyzer
            analyzer = ResumeAnalyzer()
            resume_dict = {
                "skills": [],
                "experiences": [],
                "full_name": "",
                "email": "",
            }
            return analyzer.analyze(resume_dict, job_description)
        except Exception:
            return AnalysisResult(
                overall_score=65,
                ats_score=70,
                strengths=["Có một số kỹ năng cơ bản"],
                weaknesses=["Cần cải thiện cấu trúc CV"],
                skill_gaps=[],
                suggestions=[
                    "Thêm quantifiable achievements",
                    "Tối ưu từ khóa JD",
                ],
                match_score=60,
            )
