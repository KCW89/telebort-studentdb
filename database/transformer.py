#!/usr/bin/env python3
"""
Data transformer for converting horizontal batch data to vertical database structure
"""

import json
import hashlib
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import (
    SessionLocal, 
    Student, Teacher, Program, Session, Attendance, Progress,
    StudentStatus, AttendanceStatus, ProgressStatus
)
from database.parse_horizontal import parse_batch1_format

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HorizontalToVerticalTransformer:
    """Transform horizontal batch data to vertical database structure"""
    
    def __init__(self, db_session=None):
        """Initialize transformer with database session"""
        self.db = db_session or SessionLocal()
        self.teacher_cache = {}  # Cache teacher lookups
        self.stats = {
            'students_created': 0,
            'students_updated': 0,
            'sessions_created': 0,
            'attendance_created': 0,
            'progress_created': 0,
            'errors': []
        }
    
    def transform_batch(self, batch_file_path: str) -> Dict:
        """Transform a single batch file"""
        logger.info(f"Transforming batch file: {batch_file_path}")
        
        # Parse using the horizontal parser
        students_data = parse_batch1_format(batch_file_path)
        
        # Transform each student
        for student_data in students_data:
            try:
                self.transform_student(student_data)
            except Exception as e:
                logger.error(f"Error transforming student {student_data.get('student_id', 'unknown')}: {e}")
                self.stats['errors'].append({
                    'student_id': student_data.get('student_id', 'unknown'),
                    'error': str(e)
                })
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"Batch transformation complete. Stats: {self.stats}")
        return self.stats
    
    def transform_student(self, student_data: Dict) -> Student:
        """Transform a single student's data to vertical structure"""
        student_id = student_data.get('student_id', '')
        
        if not student_id:
            raise ValueError("Student ID is required")
        
        logger.debug(f"Transforming student: {student_id}")
        
        # Check if student exists
        student = self.db.query(Student).filter_by(student_id=student_id).first()
        
        if student:
            # Update existing student
            self._update_student(student, student_data)
            self.stats['students_updated'] += 1
        else:
            # Create new student
            student = self._create_student(student_data)
            self.stats['students_created'] += 1
        
        # Transform sessions
        sessions = student_data.get('sessions', [])
        for session_data in sessions:
            self._transform_session(student, session_data)
        
        return student
    
    def _create_student(self, student_data: Dict) -> Student:
        """Create a new student record"""
        student = Student(
            student_id=student_data.get('student_id'),
            name=student_data.get('name', ''),
            status=self._parse_student_status(student_data.get('status', '')),
            program_id=student_data.get('program', ''),
            primary_teacher=student_data.get('teacher', ''),
            data_hash=self._calculate_hash(student_data)
        )
        
        self.db.add(student)
        self.db.flush()  # Get ID without committing
        
        return student
    
    def _update_student(self, student: Student, student_data: Dict):
        """Update existing student record"""
        student.name = student_data.get('name', student.name)
        student.status = self._parse_student_status(student_data.get('status', ''))
        student.program_id = student_data.get('program', student.program_id)
        student.primary_teacher = student_data.get('teacher', student.primary_teacher)
        student.data_hash = self._calculate_hash(student_data)
        student.updated_at = datetime.utcnow()
    
    def _transform_session(self, student: Student, session_data: Dict):
        """Transform a single session to vertical structure"""
        # Parse session date
        session_date = self._parse_date(session_data.get('date', ''))
        if not session_date:
            return  # Skip sessions without valid dates
        
        # Check if session exists
        existing_session = self.db.query(Session).filter_by(
            student_id=student.student_id,
            session_date=session_date
        ).first()
        
        if existing_session:
            # Update existing session
            self._update_session(existing_session, session_data)
        else:
            # Create new session
            session = self._create_session(student, session_data, session_date)
            self.stats['sessions_created'] += 1
            
            # Create attendance record
            self._create_attendance(session, session_data)
            self.stats['attendance_created'] += 1
            
            # Create progress record
            self._create_progress(session, session_data)
            self.stats['progress_created'] += 1
    
    def _create_session(self, student: Student, session_data: Dict, session_date: date) -> Session:
        """Create a new session record"""
        # Get or create teacher
        teacher_name = session_data.get('teacher', '')
        teacher = self._get_or_create_teacher(teacher_name) if teacher_name else None
        
        session = Session(
            student_id=student.student_id,
            teacher_id=teacher.teacher_id if teacher else None,
            session_date=session_date,
            session_number=self._parse_int(session_data.get('session', '')),
            lesson_title=session_data.get('lesson', ''),
            lesson_url=session_data.get('submission_link', ''),
            session_hash=self._calculate_hash(session_data)
        )
        
        self.db.add(session)
        self.db.flush()
        
        return session
    
    def _update_session(self, session: Session, session_data: Dict):
        """Update existing session record"""
        # Get or create teacher
        teacher_name = session_data.get('teacher', '')
        if teacher_name:
            teacher = self._get_or_create_teacher(teacher_name)
            session.teacher_id = teacher.teacher_id if teacher else None
        
        session.session_number = self._parse_int(session_data.get('session', ''))
        session.lesson_title = session_data.get('lesson', '')
        session.lesson_url = session_data.get('submission_link', '')
        session.session_hash = self._calculate_hash(session_data)
        session.updated_at = datetime.utcnow()
    
    def _create_attendance(self, session: Session, session_data: Dict):
        """Create attendance record for session"""
        attendance = Attendance(
            session_id=session.session_id,
            status=self._parse_attendance_status(session_data.get('attendance', '')),
            marked_by=session.teacher_id
        )
        
        self.db.add(attendance)
    
    def _create_progress(self, session: Session, session_data: Dict):
        """Create progress record for session"""
        progress = Progress(
            session_id=session.session_id,
            status=self._parse_progress_status(session_data.get('progress', '')),
            stars_rating=self._parse_stars(session_data.get('progress', '')),
            submission_link=session_data.get('submission_link', ''),
            exit_ticket_score=self._parse_float(session_data.get('exit_ticket', ''))
        )
        
        self.db.add(progress)
    
    def _get_or_create_teacher(self, teacher_name: str) -> Optional[Teacher]:
        """Get existing teacher or create new one"""
        if not teacher_name:
            return None
        
        # Check cache
        if teacher_name in self.teacher_cache:
            return self.teacher_cache[teacher_name]
        
        # Query database
        teacher = self.db.query(Teacher).filter_by(name=teacher_name).first()
        
        if not teacher:
            # Create new teacher
            teacher = Teacher(name=teacher_name, active=True)
            self.db.add(teacher)
            self.db.flush()
        
        # Cache for future use
        self.teacher_cache[teacher_name] = teacher
        
        return teacher
    
    def _parse_batch_data(self, batch_data: any) -> List[Dict]:
        """Parse different batch data formats"""
        students = []
        
        # Handle list format (batches 3, 4)
        if isinstance(batch_data, list):
            for item in batch_data:
                students.append({
                    'student_id': item.get('student_id', ''),
                    'name': item.get('name', ''),
                    'program': item.get('program', ''),
                    'teacher': item.get('teacher', ''),
                    'status': item.get('status', ''),
                    'sessions': item.get('sessions', [])
                })
        
        # Handle dictionary with results->rows format
        elif isinstance(batch_data, dict):
            if 'results' in batch_data:
                results = batch_data['results']
                
                # If results is a list, use it directly
                if isinstance(results, list):
                    rows = results
                # If results is a dict, get rows or raw_rows
                else:
                    rows = results.get('rows', results.get('raw_rows', []))
                
                for row in rows:
                    students.append({
                        'student_id': row.get('student_id', ''),
                        'name': row.get('name', ''),
                        'program': row.get('program', ''),
                        'teacher': row.get('teacher', ''),
                        'status': row.get('status', ''),
                        'sessions': row.get('sessions', [])
                    })
            elif 'raw_data' in batch_data:
                # Handle raw_data format
                for item in batch_data.get('raw_data', []):
                    students.append({
                        'student_id': item.get('student_id', ''),
                        'name': item.get('name', ''),
                        'program': item.get('program', ''),
                        'teacher': item.get('teacher', ''),
                        'status': item.get('status', ''),
                        'sessions': item.get('sessions', [])
                    })
        
        return students
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        
        # Try different date formats
        formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _parse_student_status(self, status_str: str) -> StudentStatus:
        """Parse student status string to enum"""
        status_map = {
            'active': StudentStatus.ACTIVE,
            'graduated': StudentStatus.GRADUATED,
            'inactive': StudentStatus.INACTIVE,
            'withdrawn': StudentStatus.WITHDRAWN,
            'not enrolled yet': StudentStatus.NOT_ENROLLED
        }
        
        status_lower = status_str.lower().strip()
        return status_map.get(status_lower, StudentStatus.ACTIVE)
    
    def _parse_attendance_status(self, attendance_str: str) -> AttendanceStatus:
        """Parse attendance status string to enum"""
        status_map = {
            'attended': AttendanceStatus.ATTENDED,
            'absent': AttendanceStatus.ABSENT,
            'no class': AttendanceStatus.NO_CLASS,
            'public holiday': AttendanceStatus.PUBLIC_HOLIDAY,
            'not marked': AttendanceStatus.NOT_MARKED,
            'in break': AttendanceStatus.IN_BREAK,
            'teacher parent day': AttendanceStatus.TEACHER_PARENT_DAY,
            'hari raya holiday': AttendanceStatus.HARI_RAYA_HOLIDAY
        }
        
        attendance_lower = attendance_str.lower().strip()
        
        # Check if it's a teacher name (common data issue)
        teacher_names = ['soumiya', 'han yang', 'khairina', 'arrvinna', 'syahin', 
                        'hafiz', 'yasmin', 'nurafrina', 'rahmat', 'fatin', 
                        'aisyah', 'puvin', 'afiqah', 'aaron', 'farah']
        
        if attendance_lower in teacher_names:
            return AttendanceStatus.ATTENDED  # Assume attended if teacher name present
        
        return status_map.get(attendance_lower, AttendanceStatus.NOT_MARKED)
    
    def _parse_progress_status(self, progress_str: str) -> ProgressStatus:
        """Parse progress status string to enum"""
        status_map = {
            'completed': ProgressStatus.COMPLETED,
            'in progress': ProgressStatus.IN_PROGRESS,
            'not started': ProgressStatus.NOT_STARTED,
            'graduated': ProgressStatus.GRADUATED
        }
        
        progress_lower = progress_str.lower().strip()
        
        # Check for stars rating in progress string
        if '★' in progress_str or '☆' in progress_str:
            stars = progress_str.count('★')
            if stars >= 4:
                return ProgressStatus.COMPLETED
            elif stars >= 2:
                return ProgressStatus.IN_PROGRESS
            else:
                return ProgressStatus.NOT_STARTED
        
        return status_map.get(progress_lower, ProgressStatus.NOT_STARTED)
    
    def _parse_stars(self, progress_str: str) -> Optional[int]:
        """Parse stars rating from progress string"""
        if '★' in progress_str:
            return progress_str.count('★')
        return None
    
    def _parse_int(self, value: any) -> Optional[int]:
        """Safely parse integer value"""
        if isinstance(value, int):
            return value
        
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None
        
        return None
    
    def _parse_float(self, value: any) -> Optional[float]:
        """Safely parse float value"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            try:
                # Remove percentage sign if present
                value = value.replace('%', '')
                return float(value)
            except ValueError:
                return None
        
        return None
    
    def _calculate_hash(self, data: Dict) -> str:
        """Calculate SHA-256 hash for data"""
        # Create a consistent string representation
        hash_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(hash_str.encode()).hexdigest()
    
    def close(self):
        """Close database session"""
        self.db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Transform horizontal batch data to vertical database")
    parser.add_argument('batch_file', help='Path to batch JSON file')
    parser.add_argument('--commit', action='store_true', help='Commit changes to database')
    
    args = parser.parse_args()
    
    transformer = HorizontalToVerticalTransformer()
    
    try:
        stats = transformer.transform_batch(args.batch_file)
        
        print(f"""
Transformation Complete:
- Students Created: {stats['students_created']}
- Students Updated: {stats['students_updated']}
- Sessions Created: {stats['sessions_created']}
- Attendance Records: {stats['attendance_created']}
- Progress Records: {stats['progress_created']}
- Errors: {len(stats['errors'])}
        """)
        
        if stats['errors']:
            print("\nErrors encountered:")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error['student_id']}: {error['error']}")
        
        if args.commit:
            transformer.db.commit()
            print("\nChanges committed to database")
        else:
            print("\nChanges NOT committed (use --commit flag to save)")
        
    finally:
        transformer.close()