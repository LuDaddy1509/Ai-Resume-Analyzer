from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.resume_history import ResumeHistory
from datetime import datetime
from typing import Optional, List, Dict
import json
from collections import Counter


# Skill normalization mapping
SKILL_NORMALIZATION = {
    'JS': 'JavaScript',
    'JAVASCRIPT': 'JavaScript',
    'REACT.JS': 'React',
    'REACTJS': 'React',
    'VUE.JS': 'Vue',
    'VUEJS': 'Vue',
    'NODE.JS': 'Node.js',
    'NODEJS': 'Node.js',
    'POSTGRES': 'PostgreSQL',
    'POSTGRESQL': 'PostgreSQL',
}


class DashboardService:
    @staticmethod
    def normalize_skill(skill: str) -> str:
        """Normalize skill name to standard form."""
        skill_upper = skill.upper()
        return SKILL_NORMALIZATION.get(skill_upper, skill)

    @staticmethod
    def get_summary(db: Session, date_from: Optional[datetime] = None,
                   date_to: Optional[datetime] = None) -> Dict:
        """Get dashboard summary statistics."""
        query = db.query(ResumeHistory)

        if date_from:
            query = query.filter(ResumeHistory.created_at >= date_from)
        if date_to:
            query = query.filter(ResumeHistory.created_at <= date_to)

        total_resumes = query.count()

        # Calculate average scores
        avg_match_score = db.query(func.avg(ResumeHistory.match_score)).filter(
            ResumeHistory.match_score.isnot(None)
        )
        if date_from:
            avg_match_score = avg_match_score.filter(ResumeHistory.created_at >= date_from)
        if date_to:
            avg_match_score = avg_match_score.filter(ResumeHistory.created_at <= date_to)

        avg_match_score = avg_match_score.scalar() or 0

        return {
            'total_resumes': total_resumes,
            'avg_match_score': round(avg_match_score, 1)
        }

    @staticmethod
    def get_score_distribution(db: Session, score_type: str = 'match',
                              date_from: Optional[datetime] = None,
                              date_to: Optional[datetime] = None) -> Dict:
        """Get score distribution in buckets."""
        query = db.query(ResumeHistory)

        if date_from:
            query = query.filter(ResumeHistory.created_at >= date_from)
        if date_to:
            query = query.filter(ResumeHistory.created_at <= date_to)

        # Use match_score (only score we have currently)
        score_field = ResumeHistory.match_score

        # Define buckets
        bucket_case = case(
            (score_field <= 20, '0-20'),
            (score_field <= 40, '21-40'),
            (score_field <= 60, '41-60'),
            (score_field <= 80, '61-80'),
            else_='81-100'
        )

        results = db.query(
            bucket_case.label('bucket'),
            func.count().label('count')
        ).filter(
            score_field.isnot(None)
        )

        if date_from:
            results = results.filter(ResumeHistory.created_at >= date_from)
        if date_to:
            results = results.filter(ResumeHistory.created_at <= date_to)

        results = results.group_by('bucket').all()

        # Calculate total for percentages
        total = sum(r.count for r in results)

        # Format response
        buckets = []
        bucket_order = ['0-20', '21-40', '41-60', '61-80', '81-100']
        result_dict = {r.bucket: r.count for r in results}

        for bucket_label in bucket_order:
            count = result_dict.get(bucket_label, 0)
            percentage = round((count / total * 100), 1) if total > 0 else 0
            buckets.append({
                'label': bucket_label,
                'count': count,
                'percentage': percentage
            })

        return {
            'score_type': score_type,
            'buckets': buckets
        }

    @staticmethod
    def get_top_skills(db: Session, limit: int = 10,
                      date_from: Optional[datetime] = None,
                      date_to: Optional[datetime] = None) -> List[Dict]:
        """Get top N skills across all resumes."""
        query = db.query(ResumeHistory)

        if date_from:
            query = query.filter(ResumeHistory.created_at >= date_from)
        if date_to:
            query = query.filter(ResumeHistory.created_at <= date_to)

        resumes = query.all()

        # Count skills across all resumes
        skill_counts = Counter()
        total_resumes = len(resumes)

        for resume in resumes:
            if resume.skills:
                try:
                    skills = json.loads(resume.skills)
                    # Normalize and deduplicate skills per resume
                    normalized_skills = set()
                    for skill in skills:
                        normalized = DashboardService.normalize_skill(skill)
                        normalized_skills.add(normalized)

                    # Count each normalized skill once per resume
                    for skill in normalized_skills:
                        skill_counts[skill] += 1
                except:
                    pass

        # Get top N skills
        top_skills = skill_counts.most_common(limit)

        # Format response
        return [
            {
                'skill': skill,
                'resume_count': count,
                'percentage': round((count / total_resumes * 100), 1) if total_resumes > 0 else 0
            }
            for skill, count in top_skills
        ]
