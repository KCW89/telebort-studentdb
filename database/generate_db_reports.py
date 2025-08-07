#!/usr/bin/env python3
"""
Generate student reports from the vertical database
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import (
    SessionLocal,
    Student, Session, Attendance, Progress,
    AttendanceStatus, ProgressStatus
)


class DatabaseReportGenerator:
    """Generate reports from vertical database"""
    
    def __init__(self, db_session=None):
        """Initialize with database session"""
        self.db = db_session or SessionLocal()
    
    def generate_student_report(self, student_id: str) -> str:
        """Generate markdown report for a single student"""
        
        # Get student data
        student = self.db.query(Student).filter_by(student_id=student_id).first()
        
        if not student:
            return f"Student {student_id} not found"
        
        # Get all sessions for the student
        sessions = self.db.query(Session).filter_by(
            student_id=student_id
        ).order_by(Session.session_date.desc()).all()
        
        # Calculate statistics
        total_sessions = len(sessions)
        attended_sessions = 0
        
        for session in sessions:
            if session.attendance and session.attendance.status == AttendanceStatus.ATTENDED:
                attended_sessions += 1
        
        attendance_rate = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Get date range
        if sessions:
            earliest_date = sessions[-1].session_date
            latest_date = sessions[0].session_date
            date_range = f"{earliest_date.strftime('%d/%m/%Y')} to {latest_date.strftime('%d/%m/%Y')}"
        else:
            date_range = "No sessions"
        
        # Build report
        report = f"""# Student Attendance & Progress Report

**Student ID:** {student.student_id}
**Name:** {student.name}
**Program:** {student.program_id or 'N/A'}
**Primary Teacher:** {student.primary_teacher or 'N/A'}
**Status:** {student.status.value if student.status else 'Active'}

## Summary Statistics
- **Total Sessions:** {total_sessions}
- **Sessions Attended:** {attended_sessions}
- **Attendance Rate:** {attendance_rate:.1f}%
- **Date Range:** {date_range}

## Detailed Session Log

| Session | Date | Attendance | Lesson/Topic | Progress |
|---------|------|------------|--------------|----------|
"""
        
        # Add session details
        for session in sessions:
            attendance_status = session.attendance.status.value if session.attendance else "Not Marked"
            progress_status = session.progress.status.value if session.progress else "Not Started"
            
            # Format lesson title (truncate if too long)
            lesson = session.lesson_title or "-"
            if len(lesson) > 50:
                lesson = lesson[:47] + "..."
            
            report += f"| {session.session_number or '-'} | {session.session_date.strftime('%d/%m/%Y')} | {attendance_status} | {lesson} | {progress_status} |\n"
        
        report += f"""
---
*Report generated from database on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
        
        return report
    
    def generate_all_reports(self, output_dir: str = "reports_db"):
        """Generate reports for all students in database"""
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Get all students
        students = self.db.query(Student).all()
        
        print(f"Generating reports for {len(students)} students...")
        
        for student in students:
            # Generate report
            report = self.generate_student_report(student.student_id)
            
            # Save to file
            report_file = output_path / f"{student.student_id}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"  Generated: {report_file}")
        
        print(f"\nGenerated {len(students)} reports in {output_dir}/")
    
    def get_database_stats(self):
        """Get overall database statistics"""
        
        stats = {
            'total_students': self.db.query(Student).count(),
            'total_sessions': self.db.query(Session).count(),
            'total_attendance': self.db.query(Attendance).count(),
            'total_progress': self.db.query(Progress).count()
        }
        
        # Get attendance breakdown
        attended = self.db.query(Attendance).filter_by(status=AttendanceStatus.ATTENDED).count()
        absent = self.db.query(Attendance).filter_by(status=AttendanceStatus.ABSENT).count()
        no_class = self.db.query(Attendance).filter_by(status=AttendanceStatus.NO_CLASS).count()
        
        stats['attendance_breakdown'] = {
            'attended': attended,
            'absent': absent,
            'no_class': no_class
        }
        
        # Get progress breakdown
        completed = self.db.query(Progress).filter_by(status=ProgressStatus.COMPLETED).count()
        in_progress = self.db.query(Progress).filter_by(status=ProgressStatus.IN_PROGRESS).count()
        not_started = self.db.query(Progress).filter_by(status=ProgressStatus.NOT_STARTED).count()
        
        stats['progress_breakdown'] = {
            'completed': completed,
            'in_progress': in_progress,
            'not_started': not_started
        }
        
        return stats
    
    def close(self):
        """Close database session"""
        self.db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate reports from vertical database")
    parser.add_argument('--student', help='Generate report for specific student ID')
    parser.add_argument('--all', action='store_true', help='Generate reports for all students')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--output', default='reports_db', help='Output directory for reports')
    
    args = parser.parse_args()
    
    generator = DatabaseReportGenerator()
    
    try:
        if args.stats:
            stats = generator.get_database_stats()
            print("""
Database Statistics:
==================
Total Students: {total_students}
Total Sessions: {total_sessions}
Total Attendance Records: {total_attendance}
Total Progress Records: {total_progress}

Attendance Breakdown:
- Attended: {attended}
- Absent: {absent}
- No Class: {no_class}

Progress Breakdown:
- Completed: {completed}
- In Progress: {in_progress}
- Not Started: {not_started}
            """.format(
                **stats,
                **stats['attendance_breakdown'],
                **stats['progress_breakdown']
            ))
        
        elif args.student:
            report = generator.generate_student_report(args.student)
            print(report)
        
        elif args.all:
            generator.generate_all_reports(args.output)
        
        else:
            parser.print_help()
    
    finally:
        generator.close()