"""
SyncRun model for tracking synchronization operations
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from datetime import datetime
import enum
import uuid

from .base import Base


class SyncStatus(enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    PARTIAL = "partial"


class SyncRun(Base):
    __tablename__ = 'sync_runs'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Unique run identifier
    run_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(Enum(SyncStatus), default=SyncStatus.RUNNING, nullable=False)
    
    # Statistics
    students_fetched = Column(Integer, default=0)
    students_processed = Column(Integer, default=0)
    students_updated = Column(Integer, default=0)
    students_created = Column(Integer, default=0)
    
    sessions_added = Column(Integer, default=0)
    sessions_updated = Column(Integer, default=0)
    
    reports_generated = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    
    # Version control
    git_commit_hash = Column(String(40))  # Git commit hash after sync
    git_branch = Column(String(100))  # Branch name
    
    # Rollback data
    rollback_data = Column(Text)  # JSON blob containing rollback information
    
    # Error information
    error_message = Column(Text)
    error_details = Column(Text)  # JSON blob with detailed error information
    
    # Sync metadata
    sync_type = Column(String(50))  # 'weekly', 'manual', 'force_full'
    triggered_by = Column(String(100))  # 'github_action', 'manual', 'api'
    
    def __repr__(self):
        return f"<SyncRun(run_id='{self.run_id}', status='{self.status}', started_at='{self.started_at}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'run_id': self.run_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status.value if self.status else None,
            'students_fetched': self.students_fetched,
            'students_processed': self.students_processed,
            'students_updated': self.students_updated,
            'students_created': self.students_created,
            'sessions_added': self.sessions_added,
            'sessions_updated': self.sessions_updated,
            'reports_generated': self.reports_generated,
            'errors_count': self.errors_count,
            'git_commit_hash': self.git_commit_hash,
            'git_branch': self.git_branch,
            'sync_type': self.sync_type,
            'triggered_by': self.triggered_by,
            'duration_seconds': self.duration_seconds
        }
    
    @property
    def duration_seconds(self):
        """Calculate sync duration in seconds"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_successful(self):
        """Check if sync was successful"""
        return self.status == SyncStatus.COMPLETED
    
    @property
    def has_errors(self):
        """Check if sync had errors"""
        return self.errors_count > 0 or self.status == SyncStatus.FAILED
    
    def mark_completed(self, status=SyncStatus.COMPLETED):
        """Mark sync run as completed"""
        self.status = status
        self.completed_at = datetime.utcnow()
    
    def add_error(self, error_message, error_details=None):
        """Add error information to sync run"""
        self.errors_count += 1
        self.error_message = error_message
        if error_details:
            self.error_details = error_details