"""
Teacher model for vertical database
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Teacher(Base):
    __tablename__ = 'teachers'
    
    # Primary key
    teacher_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Teacher information
    name = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    
    # Teaching details
    subjects = Column(JSON)  # List of subjects they teach
    specializations = Column(JSON)  # Areas of expertise
    
    # Status
    active = Column(Boolean, default=True)
    hire_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="teacher")
    attendance_records = relationship("Attendance", back_populates="marked_by_teacher")
    
    def __repr__(self):
        return f"<Teacher(name='{self.name}', active={self.active})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'teacher_id': self.teacher_id,
            'name': self.name,
            'email': self.email,
            'subjects': self.subjects,
            'specializations': self.specializations,
            'active': self.active,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None
        }
    
    @classmethod
    def get_or_create(cls, session, name):
        """Get existing teacher or create new one"""
        teacher = session.query(cls).filter_by(name=name).first()
        if not teacher:
            teacher = cls(name=name)
            session.add(teacher)
            session.flush()
        return teacher