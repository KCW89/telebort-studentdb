"""
Attendance model for vertical database
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base


class AttendanceStatus(enum.Enum):
    ATTENDED = "Attended"
    ABSENT = "Absent"
    NO_CLASS = "No Class"
    PUBLIC_HOLIDAY = "Public Holiday"
    NOT_MARKED = "Not Marked"
    IN_BREAK = "In Break"
    TEACHER_PARENT_DAY = "Teacher Parent Day"
    HARI_RAYA_HOLIDAY = "Hari Raya Holiday"


class Attendance(Base):
    __tablename__ = 'attendance'
    
    # Primary key
    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    session_id = Column(Integer, ForeignKey('sessions.session_id'), nullable=False, unique=True, index=True)
    marked_by = Column(Integer, ForeignKey('teachers.teacher_id'), nullable=True)
    
    # Attendance information
    status = Column(Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.NOT_MARKED)
    
    # Additional information
    notes = Column(String(500))  # Any additional notes about attendance
    
    # Metadata
    marked_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="attendance")
    marked_by_teacher = relationship("Teacher", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<Attendance(session_id={self.session_id}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'attendance_id': self.attendance_id,
            'session_id': self.session_id,
            'status': self.status.value if self.status else None,
            'marked_by': self.marked_by,
            'notes': self.notes,
            'marked_at': self.marked_at.isoformat() if self.marked_at else None
        }
    
    @property
    def is_present(self):
        """Check if student was present"""
        return self.status == AttendanceStatus.ATTENDED
    
    @property
    def is_absent(self):
        """Check if student was absent"""
        return self.status == AttendanceStatus.ABSENT
    
    @property
    def is_class_cancelled(self):
        """Check if class was cancelled"""
        return self.status in [
            AttendanceStatus.NO_CLASS,
            AttendanceStatus.PUBLIC_HOLIDAY,
            AttendanceStatus.HARI_RAYA_HOLIDAY,
            AttendanceStatus.TEACHER_PARENT_DAY
        ]