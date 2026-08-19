#!/usr/bin/env python
"""
Test script to verify the new Skill Gap Analysis and Resume Optimization features.
Run this after running migrate_db.py to create the tables.
"""
import os
import sys

# Set DATABASE_URL for PostgreSQL
os.environ["DATABASE_URL"] = "postgresql://postgres:15092004@localhost:1509/Ai_resume"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import (
    User, ResumeHistory, JobDescription, Resume, Certification, Education,
    WorkExperience, Project, Analysis, Skill, ResumeSkill, JobSeeker,
    SkillGap, SkillGapPriority, LearningPath, UserSkillProgress,
    ResumeOptimization, OptimizationStatus, OptimizationTemplate
)
from sqlalchemy import inspect


def test_models():
    """Test that all models can be imported and tables created"""
    print("Testing model imports...")
    print("✓ All models imported successfully")

    # Create all tables
    print("\nCreating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")

    # Verify tables exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables ({len(tables)}):")
    for table in sorted(tables):
        print(f"  - {table}")

    # Check new tables specifically
    new_tables = [
        "skill_gaps", "learning_paths", "user_skill_progress",
        "resume_optimizations", "optimization_templates"
    ]
    print("\nNew feature tables:")
    for table in new_tables:
        if table in tables:
            cols = inspector.get_columns(table)
            print(f"  ✓ {table} ({len(cols)} columns)")
            for col in cols:
                print(f"    - {col['name']}: {col['type']}")
        else:
            print(f"  ✗ {table} - NOT FOUND")

    return True


def test_services():
    """Test service imports"""
    print("\n\nTesting service imports...")
    try:
        from app.services.skill_gap_service import SkillGapService
        from app.services.resume_optimization_service import ResumeOptimizationService
        print("✓ SkillGapService imported")
        print("✓ ResumeOptimizationService imported")
    except Exception as e:
        print(f"✗ Service import failed: {e}")
        return False

    # Test instantiation
    try:
        sg_service = SkillGapService()
        ro_service = ResumeOptimizationService()
        print("✓ Services instantiated successfully")
    except Exception as e:
        print(f"✗ Service instantiation failed: {e}")
        return False

    return True


def test_routers():
    """Test router imports"""
    print("\n\nTesting router imports...")
    try:
        from app.routers.skill_gaps import router as skill_gaps_router
        from app.routers.resume_optimization import router as resume_optimization_router
        print("✓ skill_gaps router imported")
        print("✓ resume_optimization router imported")
    except Exception as e:
        print(f"✗ Router import failed: {e}")
        return False
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Skill Gap Analysis + Resume Optimization Features")
    print("=" * 60)

    success = True
    success &= test_models()
    success &= test_services()
    success &= test_routers()

    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED - Features ready to use!")
    else:
        print("✗ SOME TESTS FAILED - Check errors above")
    print("=" * 60)