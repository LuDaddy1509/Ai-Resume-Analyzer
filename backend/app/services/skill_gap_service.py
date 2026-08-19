"""
Skill Gap Analysis & Learning Path Generation Service

Analyzes missing skills from resume vs JD, prioritizes them by market demand,
learnability, and impact, then generates personalized learning paths with resources.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Optional, Any
import json
import re
from datetime import datetime

from app.models.skill_gaps import SkillGap, SkillGapPriority, LearningPath, UserSkillProgress
from app.models.analyses import Analysis
from app.models.job_description import JobDescription
from app.models.skills import Skill
from app.services.parser_service import KNOWN_SKILLS
from app.rag.vector_store import ResumeRAG


# Skill categorization for learnability estimation
SKILL_CATEGORIES = {
    # Programming languages - moderate to high learnability
    "programming": {
        "skills": ["Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Dart", "Lua"],
        "learnability": 0.7,
        "avg_weeks": 8
    },
    # Frontend frameworks - moderate learnability
    "frontend": {
        "skills": ["React", "Vue", "Angular", "Next.js", "Nuxt.js", "HTML", "CSS", "Sass", "Tailwind", "Bootstrap", "jQuery", "Redux", "Webpack", "Vite"],
        "learnability": 0.6,
        "avg_weeks": 6
    },
    # Backend frameworks - moderate learnability
    "backend": {
        "skills": ["FastAPI", "Django", "Flask", "Express", "NestJS", "Spring", "Laravel", "Rails", "ASP.NET", "Node.js", "GraphQL", "REST", "gRPC"],
        "learnability": 0.6,
        "avg_weeks": 6
    },
    # Databases - moderate learnability
    "database": {
        "skills": ["SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "DynamoDB", "Firebase", "Oracle", "MSSQL"],
        "learnability": 0.7,
        "avg_weeks": 4
    },
    # DevOps/Cloud - lower learnability (more complex)
    "devops": {
        "skills": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Jenkins", "GitHub Actions", "Terraform", "Ansible", "Nginx", "Linux", "Bash"],
        "learnability": 0.4,
        "avg_weeks": 10
    },
    # Data/AI/ML - lower learnability
    "data_ai": {
        "skills": ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Spark", "Hadoop", "Tableau", "Power BI", "Data Analysis", "NLP", "Computer Vision"],
        "learnability": 0.3,
        "avg_weeks": 12
    },
    # Tools - high learnability
    "tools": {
        "skills": ["Git", "GitHub", "GitLab", "Jira", "Confluence", "Figma", "Postman", "VS Code", "IntelliJ", "PyCharm", "Excel", "Agile", "Scrum"],
        "learnability": 0.9,
        "avg_weeks": 2
    },
}


class SkillGapService:
    def __init__(self):
        self.rag = ResumeRAG()
        self._skill_category_map = self._build_category_map()

    def _build_category_map(self) -> Dict[str, str]:
        """Map each known skill to its category"""
        mapping = {}
        for category, info in SKILL_CATEGORIES.items():
            for skill in info["skills"]:
                mapping[skill.lower()] = category
        return mapping

    def _get_skill_category(self, skill: str) -> str:
        """Get category for a skill, default to 'tools'"""
        return self._skill_category_map.get(skill.lower(), "tools")

    def _estimate_learnability(self, skill: str) -> float:
        """Estimate learnability score (0-1) for a skill"""
        category = self._get_skill_category(skill)
        return SKILL_CATEGORIES.get(category, {}).get("learnability", 0.5)

    def _estimate_weeks(self, skill: str) -> int:
        """Estimate weeks to learn a skill"""
        category = self._get_skill_category(skill)
        return SKILL_CATEGORIES.get(category, {}).get("avg_weeks", 6)

    def _calculate_market_demand(self, skill: str, db: Session, target_role: str = None) -> float:
        """
        Calculate market demand score (0-1) based on frequency in job descriptions.
        Higher = more in-demand in the job market.
        """
        # Count how many active JDs mention this skill
        jds = db.query(JobDescription).filter(JobDescription.status == "active").all()

        if not jds:
            return 0.5  # Default if no data

        count = 0
        skill_upper = skill.upper()
        for jd in jds:
            try:
                keywords = json.loads(jd.extracted_keywords) if jd.extracted_keywords else []
                if any(k.upper() == skill_upper for k in keywords):
                    count += 1
            except:
                # Fallback to raw text search
                if re.search(rf"(?<![A-Z0-9]){re.escape(skill_upper)}(?![A-Z0-9])", jd.raw_text.upper()):
                    count += 1

        # Normalize: max 50 JDs mentioning a skill = 1.0 demand
        return min(count / 50.0, 1.0)

    def _calculate_impact_on_match(self, skill: str, required_skills: set, current_match: float) -> float:
        """
        Estimate how much match score would improve if this skill was added.
        Based on weight of skill in required skills.
        """
        if not required_skills:
            return 0.0

        # Each missing skill contributes equally to the gap
        total_required = len(required_skills)
        if total_required == 0:
            return 0.0

        # Base impact: 100% / total_required skills
        base_impact = 100.0 / total_required

        # Adjust for match score - if already high, marginal gains are smaller
        if current_match > 80:
            base_impact *= 0.5
        elif current_match > 60:
            base_impact *= 0.75

        return min(base_impact, 30.0)  # Cap at 30 points per skill

    def _determine_priority(self, market_demand: float, learnability: float, impact: float) -> SkillGapPriority:
        """Determine priority based on demand, learnability, and impact"""
        # High priority: high demand + high learnability + high impact
        # Low priority: low demand + low learnability + low impact
        score = (market_demand * 0.4) + (learnability * 0.3) + (min(impact / 30.0, 1.0) * 0.3)

        if score >= 0.7:
            return SkillGapPriority.HIGH
        elif score >= 0.4:
            return SkillGapPriority.MEDIUM
        else:
            return SkillGapPriority.LOW

    def analyze_skill_gaps(
        self,
        analysis: Analysis,
        resume_skills: List[str],
        db: Session
    ) -> List[SkillGap]:
        """
        Main entry point: Analyze skill gaps from an Analysis and create SkillGap records.
        """
        if not analysis.job_description_id or not analysis.missing_skills:
            return []

        # Get JD to understand target role
        jd = db.query(JobDescription).filter(JobDescription.id == analysis.job_description_id).first()
        target_role = jd.title if jd else None

        # Get required skills from JD
        required_skills = set()
        if jd and jd.extracted_keywords:
            try:
                required_skills = set(json.loads(jd.extracted_keywords))
            except:
                pass

        # Get current match score
        current_match = analysis.match_score or 0

        skill_gaps = []

        for skill_name in analysis.missing_skills:
            # Calculate metrics
            market_demand = self._calculate_market_demand(skill_name, db, target_role)
            learnability = self._estimate_learnability(skill_name)
            impact = self._calculate_impact_on_match(skill_name, required_skills, current_match)
            priority = self._determine_priority(market_demand, learnability, impact)

            # Estimate current proficiency (could be enhanced with resume analysis)
            current_proficiency = "none"
            # Check if skill appears in resume but wasn't detected as "matched"
            for rs in resume_skills:
                if rs.lower() == skill_name.lower():
                    current_proficiency = "basic"
                    break

            skill_gap = SkillGap(
                analysis_id=analysis.id,
                skill_name=skill_name,
                priority=priority,
                market_demand_score=market_demand,
                learnability_score=learnability,
                impact_on_match_score=impact,
                current_proficiency=current_proficiency,
                target_proficiency="proficient"
            )
            skill_gaps.append(skill_gap)

        # Sort by priority (high first), then by impact
        priority_order = {"high": 0, "medium": 1, "low": 2}
        skill_gaps.sort(key=lambda sg: (priority_order.get(sg.priority.value, 3), -sg.impact_on_match_score or 0))

        return skill_gaps

    def generate_learning_path(self, skill_gap: SkillGap, db: Session) -> LearningPath:
        """
        Generate a personalized learning path for a skill gap.
        Uses RAG to retrieve relevant learning resources.
        """
        skill_name = skill_gap.skill_name

        # Retrieve learning resources from RAG
        query = f"Learning resources tutorials courses for {skill_name} skill development"
        docs = self.rag.retrieve(query, k=5)

        # Build resources list
        resources = self._build_resources_list(skill_name, docs)

        # Generate project ideas based on skill category
        project_ideas = self._generate_project_ideas(skill_name)

        # Create milestones
        estimated_weeks = self._estimate_weeks(skill_name)
        milestones = self._create_milestones(skill_name, estimated_weeks)

        learning_path = LearningPath(
            skill_gap_id=skill_gap.id,
            resources=resources,
            estimated_weeks=estimated_weeks,
            project_ideas=project_ideas,
            milestones=milestones
        )

        return learning_path

    def _build_resources_list(self, skill_name: str, docs: List) -> List[Dict]:
        """Build structured resources list from RAG docs + known resources"""
        resources = []

        # Add known free resources based on skill
        free_resources = self._get_known_free_resources(skill_name)
        for r in free_resources:
            resources.append({
                "type": "free",
                "title": r["title"],
                "url": r["url"],
                "cost": "free",
                "duration_weeks": r.get("duration_weeks", 4),
                "rating": r.get("rating", 4.5),
                "description": r.get("description", "")
            })

        # Add known paid resources
        paid_resources = self._get_known_paid_resources(skill_name)
        for r in paid_resources:
            resources.append({
                "type": "paid",
                "title": r["title"],
                "url": r["url"],
                "cost": r.get("cost", "$10-50"),
                "duration_weeks": r.get("duration_weeks", 6),
                "rating": r.get("rating", 4.7),
                "description": r.get("description", "")
            })

        # Add RAG-retrieved resources
        for doc in docs[:3]:
            resources.append({
                "type": "reference",
                "title": doc.metadata.get("source", "Reference").split("/")[-1].replace(".md", ""),
                "url": "",
                "cost": "free",
                "duration_weeks": 1,
                "rating": 4.0,
                "description": doc.page_content[:200] + "..."
            })

        return resources

    def _get_known_free_resources(self, skill_name: str) -> List[Dict]:
        """Get known free resources for common skills"""
        resource_map = {
            "Python": [
                {"title": "Python.org Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "duration_weeks": 4, "rating": 4.8, "description": "Official comprehensive tutorial"},
                {"title": "Automate the Boring Stuff with Python", "url": "https://automatetheboringstuff.com/", "duration_weeks": 6, "rating": 4.9, "description": "Practical Python for beginners"},
                {"title": "Real Python", "url": "https://realpython.com/", "duration_weeks": 8, "rating": 4.8, "description": "In-depth articles and tutorials"},
            ],
            "React": [
                {"title": "React Official Tutorial", "url": "https://react.dev/learn", "duration_weeks": 4, "rating": 4.9, "description": "Official hands-on tutorial"},
                {"title": "Scrimba React Course", "url": "https://scrimba.com/learn/learnreact", "duration_weeks": 3, "rating": 4.8, "description": "Interactive coding screencasts"},
                {"title": "React Beta Docs", "url": "https://beta.reactjs.org/", "duration_weeks": 4, "rating": 4.7, "description": "Modern React with hooks"},
            ],
            "Kubernetes": [
                {"title": "Kubernetes the Hard Way", "url": "https://github.com/kelseyhightower/kubernetes-the-hard-way", "duration_weeks": 6, "rating": 4.7, "description": "Kelsey Hightower's hands-on guide"},
                {"title": "CNCF Free Training", "url": "https://training.cncf.io/", "duration_weeks": 8, "rating": 4.5, "description": "Official CNCF courses"},
                {"title": "Play with Kubernetes", "url": "https://labs.play-with-k8s.com/", "duration_weeks": 2, "rating": 4.6, "description": "Free browser-based K8s playground"},
            ],
            "AWS": [
                {"title": "AWS Skill Builder Free Tier", "url": "https://skillbuilder.aws/", "duration_weeks": 8, "rating": 4.6, "description": "Official AWS free training"},
                {"title": "AWS Well-Architected Framework", "url": "https://aws.amazon.com/architecture/well-architected/", "duration_weeks": 2, "rating": 4.8, "description": "Best practices for cloud architecture"},
            ],
            "Docker": [
                {"title": "Docker Official Getting Started", "url": "https://docs.docker.com/get-started/", "duration_weeks": 2, "rating": 4.8, "description": "Official hands-on guide"},
                {"title": "Docker Curriculum", "url": "https://docker-curriculum.com/", "duration_weeks": 3, "rating": 4.7, "description": "Comprehensive free tutorial"},
            ],
            "SQL": [
                {"title": "SQLBolt Interactive Tutorial", "url": "https://sqlbolt.com/", "duration_weeks": 3, "rating": 4.9, "description": "Interactive SQL lessons"},
                {"title": "Mode Analytics SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "duration_weeks": 4, "rating": 4.8, "description": "Business-focused SQL"},
            ],
            "Git": [
                {"title": "Git Official Documentation", "url": "https://git-scm.com/doc", "duration_weeks": 2, "rating": 4.7, "description": "Complete reference"},
                {"title": "Oh Shit, Git!?", "url": "https://ohshitgit.com/", "duration_weeks": 1, "rating": 4.9, "description": "Fixing common Git mistakes"},
            ],
        }

        return resource_map.get(skill_name, [
            {"title": f"{skill_name} Official Documentation", "url": f"https://{skill_name.lower()}.org", "duration_weeks": 4, "rating": 4.5, "description": "Official documentation and guides"},
            {"title": f"Free {skill_name} Tutorial - YouTube", "url": f"https://youtube.com/results?search_query={skill_name}+tutorial", "duration_weeks": 3, "rating": 4.3, "description": "Video tutorials"},
        ])

    def _get_known_paid_resources(self, skill_name: str) -> List[Dict]:
        """Get known paid resources for common skills"""
        paid_map = {
            "Python": [
                {"title": "Complete Python Bootcamp (Udemy)", "url": "https://udemy.com/course/complete-python-bootcamp/", "cost": "$15-20", "duration_weeks": 6, "rating": 4.7, "description": "Jose Portilla's comprehensive course"},
                {"title": "Python for Everybody (Coursera)", "url": "https://coursera.org/specializations/python", "cost": "$49/mo", "duration_weeks": 8, "rating": 4.8, "description": "University of Michigan specialization"},
            ],
            "React": [
                {"title": "Epic React (Kent C. Dodds)", "url": "https://epicreact.dev/", "cost": "$200-600", "duration_weeks": 8, "rating": 4.9, "description": "Advanced React patterns and hooks"},
                {"title": "React - The Complete Guide (Udemy)", "url": "https://udemy.com/course/react-the-complete-guide-incl-redux/", "cost": "$15-20", "duration_weeks": 10, "rating": 4.7, "description": "Maximilian Schwarzmüller's course"},
            ],
            "Kubernetes": [
                {"title": "Certified Kubernetes Administrator (CKA) Prep", "url": "https://kubernetes.io/training/", "cost": "$300-600", "duration_weeks": 6, "rating": 4.6, "description": "Official CKA certification prep"},
                {"title": "Kubernetes for Developers (CKAD)", "url": "https://training.linuxfoundation.org/training/kubernetes-for-developers-lfd259/", "cost": "$300", "duration_weeks": 8, "rating": 4.5, "description": "CKAD certification course"},
            ],
            "AWS": [
                {"title": "AWS Certified Solutions Architect Associate", "url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/", "cost": "$150", "duration_weeks": 8, "rating": 4.7, "description": "Industry-standard cloud certification"},
            ],
        }

        return paid_map.get(skill_name, [
            {"title": f"Advanced {skill_name} Course (Udemy/Coursera)", "url": f"https://udemy.com/course/{skill_name.lower()}", "cost": "$15-50", "duration_weeks": 6, "rating": 4.5, "description": "Comprehensive paid course"},
        ])

    def _generate_project_ideas(self, skill_name: str) -> List[str]:
        """Generate portfolio project ideas for a skill"""
        project_map = {
            "Python": [
                "Build a CLI tool for automating a repetitive task",
                "Create a REST API with FastAPI + PostgreSQL",
                "Develop a web scraper with async/await",
                "Build a data pipeline with Pandas + SQLAlchemy",
            ],
            "React": [
                "Build a dashboard with charts (Recharts) and state management",
                "Create a component library with Storybook",
                "Develop a real-time chat app with WebSockets",
                "Build an e-commerce frontend with cart + checkout",
            ],
            "Kubernetes": [
                "Deploy a microservices app on local K8s (Kind/k3d)",
                "Set up Helm charts for a 3-tier application",
                "Implement GitOps with ArgoCD",
                "Configure monitoring with Prometheus + Grafana",
            ],
            "AWS": [
                "Deploy a serverless API with Lambda + API Gateway + DynamoDB",
                "Set up CI/CD pipeline with CodePipeline + CodeBuild",
                "Build a static site hosting with S3 + CloudFront",
                "Implement infrastructure as code with Terraform",
            ],
            "Docker": [
                "Dockerize a multi-service application",
                "Create optimized multi-stage Dockerfiles",
                "Set up Docker Compose for local development",
                "Build and push images to GitHub Container Registry",
            ],
            "SQL": [
                "Design a normalized database schema for an app",
                "Write complex queries with CTEs, window functions",
                "Build a reporting dashboard with SQL views",
                "Implement database migration scripts",
            ],
            "Git": [
                "Set up a monorepo with proper branching strategy",
                "Configure Git hooks for code quality",
                "Resolve complex merge conflicts",
                "Set up signed commits and verification",
            ],
        }

        return project_map.get(skill_name, [
            f"Build a portfolio project demonstrating {skill_name} proficiency",
            f"Contribute to an open-source project using {skill_name}",
            f"Create a tutorial or blog post about {skill_name}",
        ])

    def _create_milestones(self, skill_name: str, estimated_weeks: int) -> List[Dict]:
        """Create weekly milestones for learning path"""
        milestones = []
        weeks_per_phase = max(1, estimated_weeks // 4)

        phases = [
            ("Foundation", f"Complete introductory tutorials and understand core concepts of {skill_name}"),
            ("Practice", f"Build small exercises and complete guided projects in {skill_name}"),
            ("Project", f"Build a portfolio project showcasing {skill_name} skills"),
            ("Mastery", f"Refine project, add tests/documentation, prepare for interviews"),
        ]

        current_week = 0
        for phase_name, goal in phases:
            phase_weeks = weeks_per_phase
            current_week += phase_weeks
            milestones.append({
                "week": current_week,
                "phase": phase_name,
                "goal": goal,
                "deliverable": self._get_deliverable_for_phase(skill_name, phase_name)
            })

        return milestones

    def _get_deliverable_for_phase(self, skill_name: str, phase: str) -> str:
        deliverables = {
            "Foundation": f"Notes/summary of {skill_name} core concepts",
            "Practice": f"Completed exercises and mini-projects in {skill_name}",
            "Project": f"GitHub repository with {skill_name} portfolio project",
            "Mastery": f"Polished project with README, tests, and demo",
        }
        return deliverables.get(phase, f"Completed {phase} phase for {skill_name}")

    def get_user_skill_progress(self, user_id: int, db: Session) -> List[UserSkillProgress]:
        """Get all skill progress for a user"""
        return db.query(UserSkillProgress).filter(UserSkillProgress.user_id == user_id).all()

    def update_skill_progress(
        self,
        user_id: int,
        skill_name: str,
        status: str = None,
        proficiency_level: str = None,
        evidence_url: str = None,
        notes: str = None,
        db: Session = None
    ) -> UserSkillProgress:
        """Create or update user's skill progress"""
        progress = db.query(UserSkillProgress).filter(
            UserSkillProgress.user_id == user_id,
            UserSkillProgress.skill_name == skill_name
        ).first()

        if not progress:
            progress = UserSkillProgress(
                user_id=user_id,
                skill_name=skill_name,
                status="learning"
            )
            db.add(progress)

        if status:
            progress.status = status
        if proficiency_level:
            progress.proficiency_level = proficiency_level
        if evidence_url:
            progress.evidence_url = evidence_url
        if notes:
            progress.notes = notes

        if status in ["proficient", "showcased"] and not progress.completed_at:
            progress.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(progress)
        return progress