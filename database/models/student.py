"""
Student model for vertical database
"""

from sqlalchemy import Column, String, DateTime, Enum, Time
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base


class StudentStatus(enum.Enum):
    ACTIVE = "Active"
    GRADUATED = "Graduated"
    INACTIVE = "Inactive"
    WITHDRAWN = "Withdrawn"
    NOT_ENROLLED = "Not Enrolled Yet"


class Student(Base):
    __tablename__ = 'students'
    
    # Primary key
    student_id = Column(String(10), primary_key=True, index=True)  # s10XXX format
    
    # Student information
    name = Column(String(255), nullable=False)
    status = Column(Enum(StudentStatus), default=StudentStatus.ACTIVE)
    
    # Program and schedule
    program_id = Column(String(20))  # AI-2, W-1, BBP, etc.
    schedule_day = Column(String(20))  # Monday, Tuesday, etc.
    start_time = Column(Time)
    end_time = Column(Time)
    
    # Teacher assignment
    primary_teacher = Column(String(100))
    
    # Metadata
    enrollment_date = Column(DateTime)
    graduation_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Data integrity
    data_hash = Column(String(64))  # SHA-256 hash for change detection
    
    # Relationships
    sessions = relationship("Session", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student(student_id='{self.student_id}', name='{self.name}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'student_id': self.student_id,
            'name': self.name,
            'status': self.status.value if self.status else None,
            'program_id': self.program_id,
            'schedule_day': self.schedule_day,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'primary_teacher': self.primary_teacher,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'graduation_date': self.graduation_date.isoformat() if self.graduation_date else None
        }