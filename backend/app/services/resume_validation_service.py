"""
CV/Resume Validation Service (Lenient Mode)

This service analyzes documents but accepts ALL documents for parsing.
It provides validation metadata but never rejects - empty fields are allowed.
"""

import re
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of CV validation (lenient - always accepts)"""
    is_resume: bool = True
    confidence: float = 1.0
    reason: str = "Document accepted for parsing"
    error_code: str = None
    details: Dict = None


class ResumeValidator:
    """
    Lenient validator that accepts all documents for parsing.
    Provides quality signals but never blocks processing.
    """

    def __init__(self):
        """Initialize the validator"""
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for quality analysis"""
        self.cv_section_patterns = {}
        self.cv_sections = {
            "personal_summary": [r"professional\s+summary", r"career\s+objective", r"summary", r"profile", r"about\s+me"],
            "experience": [r"work\s+experience", r"professional\s+experience", r"experience", r"employment\s+history", r"kinh\s+nghi[eệ]m", r"qu[aá]\s+tr[iì]nh\s+l[aà]m\s+vi[eệ]c"],
            "education": [r"education", r"academic\s+background", r"qualifications", r"h[oọ]c\s+v[aấ]n", r"gi[aá]o\s+d[uụ]c"],
            "skills": [r"skills", r"technical\s+skills", r"core\s+competencies", r"k[yỹ]\s+n[aă]ng", r"n[aă]ng\s+l[uự]c"],
            "projects": [r"projects", r"key\s+projects", r"d[uự]\s+[aá]n", r"c[aá]c\s+d[uự]\s+[aá]n"],
            "certifications": [r"certifications?", r"certificates?", r"ch[uứ]ng\s+ch[ỉi]", r"ch[uứ]ng\s+nh[aậ]n"],
            "languages": [r"languages?", r"ngo[aạ]i\s+ng[uử]", r"ng[oô]n\s+ng[uử]"],
        }
        for category, patterns in self.cv_sections.items():
            self.cv_section_patterns[category] = [re.compile(p, re.IGNORECASE) for p in patterns]

    def validate(self, text: str) -> ValidationResult:
        """
        Lenient validation - ALWAYS accepts document for parsing.
        Returns quality metadata for logging/debugging.
        """
        if not text or len(text.strip()) < 10:
            return ValidationResult(
                is_resume=True,
                confidence=0.1,
                reason="Very short document, but will attempt parsing",
                error_code="SHORT_DOCUMENT",
                details={"text_length": len(text)}
            )

        scores = self._calculate_quality_scores(text)
        total_score = sum(scores.values()) / len(scores) if scores else 0.5

        return ValidationResult(
            is_resume=True,  # ALWAYS True - never reject
            confidence=max(total_score, 0.1),
            reason="Document accepted for parsing",
            error_code=None,
            details={
                "text_length": len(text),
                "quality_scores": scores,
                "detected_sections": self._get_detected_sections(text),
                "has_contact": self._has_contact_info(text)
            }
        )

    def _calculate_quality_scores(self, text: str) -> Dict[str, float]:
        """Calculate quality scores for metadata only (no threshold)"""
        return {
            "contact_info": self._score_contact_info(text),
            "cv_sections": self._score_cv_sections(text),
            "experience_education": self._score_experience_education(text),
            "structure": self._score_structure(text),
        }

    def _score_contact_info(self, text: str) -> float:
        score = 0.0
        if re.search(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", text): score += 0.4
        if re.search(r"(?:\+84|84|0)\s*[-.]?\s*\d{2,3}\s*[-.]?\s*\d{3}\s*[-.]?\s*\d{3,4}", text): score += 0.3
        if re.search(r"linkedin\.com|github\.com|portfolio", text, re.IGNORECASE): score += 0.2
        if re.search(r"\b(address|location|city|[dđ][iị]a\s+ch[ỉi])\b", text, re.IGNORECASE): score += 0.1
        return min(score, 1.0)

    def _score_cv_sections(self, text: str) -> float:
        found = sum(1 for cat, patterns in self.cv_section_patterns.items() if any(p.search(text) for p in patterns))
        return min(found / 4.0, 1.0)

    def _score_experience_education(self, text: str) -> float:
        score = 0.0
        if re.search(r"\d{4}\s*[-–—]\s*(\d{4}|present|current|nay)", text, re.IGNORECASE): score += 0.3
        if re.search(r"university|college|[dđ]ại\s+h[oọ]c|cao\s+[dđ][aẳ]ng", text, re.IGNORECASE): score += 0.3
        if re.search(r"engineer|developer|manager|analyst|k[yỹ]\s+s[uư]|gi[aá]m\s+[dđ][oố]c", text, re.IGNORECASE): score += 0.2
        if re.search(r"company|corporation|inc\.|ltd\.|công\s+ty", text, re.IGNORECASE): score += 0.2
        return min(score, 1.0)

    def _score_structure(self, text: str) -> float:
        score = 0.0
        bullets = len(re.findall(r"^\s*[\-\•\*\+✓✔►▸→]\s+", text, re.MULTILINE))
        if bullets >= 3: score += 0.5
        elif bullets >= 1: score += 0.2
        if len(re.findall(r"\n\s*\n", text)) >= 2: score += 0.3
        if len(re.findall(r"^\s*[A-ZÀ-Ỹ][A-ZÀ-Ỹ\s]{2,}", text, re.MULTILINE)) >= 2: score += 0.2
        return min(score, 1.0)

    def _get_detected_sections(self, text: str) -> List[str]:
        return [cat for cat, patterns in self.cv_section_patterns.items() if any(p.search(text) for p in patterns)]

    def _has_contact_info(self, text: str) -> bool:
        return bool(re.search(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", text)) or bool(re.search(r"(?:\+84|84|0)\d{9,10}", text))
