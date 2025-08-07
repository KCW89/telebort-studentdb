#!/usr/bin/env python3
"""
Initialize the vertical database schema
Creates all tables and adds default data
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import (
    Base, engine, SessionLocal,
    Student, Teacher, Program, Session, Attendance, Progress, SyncRun
)
from database.models.program import ProgramType, DifficultyLevel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with schema and default data"""
    logger.info("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Initialize default teachers
        default_teachers = [
            'Soumiya', 'Han Yang', 'Khairina', 'Arrvinna', 
            'Syahin', 'Hafiz', 'Yasmin', 'Nurafrina',
            'Rahmat', 'Fatin', 'Aisyah', 'Puvin', 'Afiqah',
            'Aaron', 'Farah'  # Additional teachers found in data
        ]
        
        for teacher_name in default_teachers:
            existing = db.query(Teacher).filter_by(name=teacher_name).first()
            if not existing:
                teacher = Teacher(name=teacher_name, active=True)
                db.add(teacher)
                logger.info(f"Added teacher: {teacher_name}")
        
        db.commit()
        logger.info(f"Initialized {len(default_teachers)} teachers")
        
        # Initialize default programs
        Program.initialize_default_programs(db)
        logger.info("Initialized default programs")
        
        # Get database statistics
        student_count = db.query(Student).count()
        teacher_count = db.query(Teacher).count()
        program_count = db.query(Program).count()
        
        logger.info(f"""
Database initialized successfully!
Statistics:
- Students: {student_count}
- Teachers: {teacher_count}
- Programs: {program_count}
- Database URL: {engine.url}
        """)
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()


def reset_database():
    """Drop all tables and recreate (WARNING: Destroys all data)"""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")
    
    # Recreate
    return init_database()


def check_database():
    """Check database connection and schema"""
    try:
        db = SessionLocal()
        
        # Test queries
        student_count = db.query(Student).count()
        teacher_count = db.query(Teacher).count()
        program_count = db.query(Program).count()
        session_count = db.query(Session).count()
        
        logger.info(f"""
Database Status: ✅ Connected
Current Data:
- Students: {student_count}
- Teachers: {teacher_count}
- Programs: {program_count}
- Sessions: {session_count}
        """)
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Telebort StudentDB database")
    parser.add_argument('--reset', action='store_true', help='Reset database (WARNING: Destroys all data)')
    parser.add_argument('--check', action='store_true', help='Check database status')
    
    args = parser.parse_args()
    
    if args.reset:
        response = input("⚠️  This will DELETE ALL DATA. Are you sure? (yes/no): ")
        if response.lower() == 'yes':
            reset_database()
        else:
            print("Reset cancelled")
    elif args.check:
        check_database()
    else:
        init_database()