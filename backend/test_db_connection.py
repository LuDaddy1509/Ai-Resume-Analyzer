#!/usr/bin/env python
"""
Test script to verify PostgreSQL database connection and table creation.
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import User, ResumeHistory, JobDescription, Resume, Certification, Education, WorkExperience, Project, Analysis, Skill, ResumeSkill, JobSeeker

from sqlalchemy import text

def test_connection():
    print("Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"Connected to PostgreSQL: {version[0]}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def create_tables():
    print("Creating all tables with correct schema...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        return True
    except Exception as e:
        print(f"Table creation failed: {e}")
        return False

def verify_tables():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables: {tables}")

    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n{table} table columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

if __name__ == "__main__":
    if test_connection():
        if create_tables():
            verify_tables()