from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

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
                temperature=0.3,
                api_key=api_key
            )
        
        self.parser = PydanticOutputParser(pydantic_object=AnalysisResult)
        
        self.prompt = PromptTemplate(
            template="""Bạn là chuyên gia tuyển dụng cao cấp. Phân tích CV sau một cách chi tiết và khách quan.

CV Information:
{resume_text}

{job_description_section}

{format_instructions}

Trả về kết quả theo đúng JSON format.""",
            input_variables=["resume_text", "job_description_section"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    async def analyze(self, resume_text: str, job_description: str = None):
        """Phân tích CV bằng Gemini"""
        if not self.llm:
            return self._fallback_analyze(resume_text, job_description)
            
        jd_section = f"Job Description:\n{job_description}\n" if job_description else ""
        
        chain = self.prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({
                "resume_text": resume_text,
                "job_description_section": jd_section
            })
            return result
        except Exception as e:
            print("LLM Error:", e)
            return self._fallback_analyze(resume_text, job_description)

    def _fallback_analyze(self, resume_text: str, job_description: str):
        # Fallback sang local parsing & analysis
        # pyrefly: ignore [missing-import]
        from app.services.parser_service import parse_resume_file, analyze_resume_against_job
        # Giả lập file bytes từ resume_text
        resume_data = parse_resume_file(resume_text.encode("utf-8", errors="ignore"), "resume.txt")
        rule_analysis = analyze_resume_against_job(resume_data, job_description)
        return AnalysisResult(
            overall_score=rule_analysis.match_score,
            ats_score=rule_analysis.match_score,
            strengths=["Hồ sơ có các kỹ năng kỹ thuật cần thiết"],
            weaknesses=["Chưa nhận diện thêm điểm yếu từ AI"],
            skill_gaps=rule_analysis.missing_skills,
            suggestions=rule_analysis.suggestions,
            match_score=rule_analysis.match_score
        )