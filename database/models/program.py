"""
Program model for vertical database
"""

from sqlalchemy import Column, String, Integer, JSON, DateTime, Enum
from datetime import datetime
import enum

from .base import Base


class ProgramType(enum.Enum):
    AI_ML = "AI & Machine Learning"
    WEB_DEV = "Web Development"
    PYTHON = "Python Programming"
    BLOCK_BASED = "Block-Based Programming"
    JUNIOR_CODERS = "Junior Coders"
    FULL_STACK = "Full Stack Development"


class DifficultyLevel(enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class Program(Base):
    __tablename__ = 'programs'
    
    # Primary key
    program_id = Column(String(20), primary_key=True)  # AI-1, AI-2, W-1, BBP, etc.
    
    # Program information
    name = Column(String(255), nullable=False)
    program_type = Column(Enum(ProgramType))
    description = Column(String(1000))
    
    # Course structure
    total_lessons = Column(Integer, default=0)
    estimated_duration_weeks = Column(Integer)
    difficulty_level = Column(Enum(DifficultyLevel))
    
    # Detailed lesson structure (JSON)
    lesson_structure = Column(JSON)  # Contains lesson plans, objectives, etc.
    prerequisites = Column(JSON)  # List of prerequisite programs or skills
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Program(program_id='{self.program_id}', name='{self.name}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'program_id': self.program_id,
            'name': self.name,
            'program_type': self.program_type.value if self.program_type else None,
            'description': self.description,
            'total_lessons': self.total_lessons,
            'estimated_duration_weeks': self.estimated_duration_weeks,
            'difficulty_level': self.difficulty_level.value if self.difficulty_level else None,
            'lesson_structure': self.lesson_structure,
            'prerequisites': self.prerequisites
        }
    
    @classmethod
    def initialize_default_programs(cls, session):
        """Initialize default programs based on existing data"""
        default_programs = [
            {
                'program_id': 'AI-2',
                'name': 'AI & Machine Learning Level 2',
                'program_type': ProgramType.AI_ML,
                'description': 'Advanced AI and Machine Learning concepts',
                'total_lessons': 9,
                'difficulty_level': DifficultyLevel.INTERMEDIATE,
                'lesson_structure': {
                    'L1': 'Introduction to AI',
                    'L2': 'Supervised & Unsupervised Learning',
                    'L3': 'Data Preparation',
                    'L4': 'Regression',
                    'L5': 'Project 1 - Instagram Reach Analysis',
                    'L6': 'Classification',
                    'L7': 'Clustering',
                    'L8': 'Project 3 - Mall Customer Segmentation',
                    'L9': 'NLP Concepts'
                }
            },
            {
                'program_id': 'W-1',
                'name': 'Web Development Level 1',
                'program_type': ProgramType.WEB_DEV,
                'description': 'Introduction to web development with HTML, CSS, and JavaScript',
                'total_lessons': 12,
                'difficulty_level': DifficultyLevel.BEGINNER,
                'lesson_structure': {
                    'lessons': ['HTML Basics', 'CSS Fundamentals', 'JavaScript Introduction', 'Bootstrap Framework', 'React.js Basics']
                }
            },
            {
                'program_id': 'BBP',
                'name': 'Block-Based Programming',
                'program_type': ProgramType.BLOCK_BASED,
                'description': 'Visual programming for beginners',
                'total_lessons': 10,
                'difficulty_level': DifficultyLevel.BEGINNER
            },
            {
                'program_id': 'JC',
                'name': 'Junior Coders',
                'program_type': ProgramType.JUNIOR_CODERS,
                'description': 'Programming fundamentals for young learners',
                'total_lessons': 8,
                'difficulty_level': DifficultyLevel.BEGINNER
            }
        ]
        
        for program_data in default_programs:
            existing = session.query(cls).filter_by(program_id=program_data['program_id']).first()
            if not existing:
                program = cls(**program_data)
                session.add(program)
        
        session.commit()