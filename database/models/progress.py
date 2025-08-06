"""
Progress model for vertical database
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Text, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base


class ProgressStatus(enum.Enum):
    COMPLETED = "Completed"
    IN_PROGRESS = "In Progress"
    NOT_STARTED = "Not Started"
    GRADUATED = "Graduated"


class Progress(Base):
    __tablename__ = 'progress'
    
    # Primary key
    progress_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    session_id = Column(Integer, ForeignKey('sessions.session_id'), nullable=False, unique=True, index=True)
    
    # Progress information
    status = Column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED)
    
    # Rating (1-5 stars)
    stars_rating = Column(Integer, CheckConstraint('stars_rating >= 1 AND stars_rating <= 5'))
    
    # Submission details
    submission_link = Column(Text)  # URL to student's work
    submission_date = Column(DateTime)
    
    # Scores
    exit_ticket_score = Column(Float)  # Percentage or points
    assessment_score = Column(Float)
    
    # Feedback
    teacher_feedback = Column(Text)
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="progress")
    
    def __repr__(self):
        return f"<Progress(session_id={self.session_id}, status='{self.status}', stars={self.stars_rating})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'progress_id': self.progress_id,
            'session_id': self.session_id,
            'status': self.status.value if self.status else None,
            'stars_rating': self.stars_rating,
            'submission_link': self.submission_link,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'exit_ticket_score': self.exit_ticket_score,
            'assessment_score': self.assessment_score,
            'teacher_feedback': self.teacher_feedback,
            'notes': self.notes
        }
    
    @property
    def stars_display(self):
        """Get stars as display string"""
        if not self.stars_rating:
            return "☆☆☆☆☆"
        
        filled = "★" * self.stars_rating
        empty = "☆" * (5 - self.stars_rating)
        return filled + empty
    
    @property
    def is_completed(self):
        """Check if session is completed"""
        return self.status in [ProgressStatus.COMPLETED, ProgressStatus.GRADUATED]
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage based on status"""
        status_map = {
            ProgressStatus.NOT_STARTED: 0,
            ProgressStatus.IN_PROGRESS: 50,
            ProgressStatus.COMPLETED: 100,
            ProgressStatus.GRADUATED: 100
        }
        return status_map.get(self.status, 0)