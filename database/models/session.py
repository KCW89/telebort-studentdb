"""
Session model for vertical database (class sessions, not database sessions)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Session(Base):
    __tablename__ = 'sessions'
    
    # Primary key
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    student_id = Column(String(10), ForeignKey('students.student_id'), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'), nullable=True)
    
    # Session information
    session_date = Column(Date, nullable=False, index=True)
    session_number = Column(Integer)  # Sequential session number for the student
    
    # Lesson details
    lesson_title = Column(Text)
    lesson_code = Column(String(20))  # L1, L2, etc.
    lesson_url = Column(Text)  # Resource URLs
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Data integrity
    session_hash = Column(String(64))  # SHA-256 hash for change detection
    
    # Relationships
    student = relationship("Student", back_populates="sessions")
    teacher = relationship("Teacher", back_populates="sessions")
    attendance = relationship("Attendance", back_populates="session", uselist=False, cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="session", uselist=False, cascade="all, delete-orphan")
    
    # Unique constraint to prevent duplicate sessions
    __table_args__ = (
        UniqueConstraint('student_id', 'session_date', name='_student_date_uc'),
    )
    
    def __repr__(self):
        return f"<Session(student_id='{self.student_id}', date='{self.session_date}', number={self.session_number})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'session_id': self.session_id,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'session_number': self.session_number,
            'lesson_title': self.lesson_title,
            'lesson_code': self.lesson_code,
            'lesson_url': self.lesson_url,
            'attendance': self.attendance.to_dict() if self.attendance else None,
            'progress': self.progress.to_dict() if self.progress else None
        }