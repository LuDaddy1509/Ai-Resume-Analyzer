#!/usr/bin/env python
"""
Database migration script to recreate tables with the correct schema
for PostgreSQL backend.
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import User, ResumeHistory, JobDescription, Resume, Certification, Education, WorkExperience, Project, Analysis, Skill, ResumeSkill, JobSeeker, SkillGap, LearningPath, UserSkillProgress, ResumeOptimization, OptimizationTemplate

def main():
    print("Dropping all existing tables...")
    # Use CASCADE to drop tables with dependencies
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    print("Tables dropped successfully")

    print("Creating all tables with correct schema...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables: {tables}")

    # Verify users table structure
    if 'users' in tables:
        columns = inspector.get_columns('users')
        print(f"\nUsers table columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

if __name__ == "__main__":
    main()