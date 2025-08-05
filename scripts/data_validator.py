#!/usr/bin/env python3
"""
data_validator.py - Data validation and quality checks for student records

This module provides comprehensive validation for:
- Student information completeness
- Session data integrity
- Date format consistency
- Progress tracking accuracy
- Attendance validation
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class DataValidator:
    """Validate student data quality and integrity"""
    
    # Valid values for various fields
    VALID_ATTENDANCE = {'Attended', 'Absent', 'No Class', 'Public Holiday'}
    VALID_PROGRESS = {'Completed', 'In Progress', 'Not Started', 'Graduated', '-', ''}
    
    # Date format pattern
    DATE_PATTERN = re.compile(r'^\d{2}/\d{2}/\d{4}$')
    
    # Student ID pattern
    STUDENT_ID_PATTERN = re.compile(r'^s\d{5}$')
    
    def __init__(self):
        """Initialize the validator"""
        self.logger = self._setup_logger()
        self.validation_results = []
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('DataValidator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        
        return logger
    
    def validate_student(self, student_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate a single student record
        
        Args:
            student_data: Student data dictionary
            
        Returns:
            List of validation issues found
        """
        issues = []
        student_info = student_data.get('info', {})
        student_id = student_info.get('student_id', 'Unknown')
        
        # Validate student info
        info_issues = self._validate_student_info(student_info)
        issues.extend(info_issues)
        
        # Validate sessions
        sessions = student_data.get('sessions', [])
        if not sessions:
            issues.append({
                'student_id': student_id,
                'type': 'no_sessions',
                'severity': 'warning',
                'message': 'No session data found'
            })
        else:
            session_issues = self._validate_sessions(sessions, student_id)
            issues.extend(session_issues)
        
        # Cross-validation checks
        cross_issues = self._cross_validate(student_data)
        issues.extend(cross_issues)
        
        return issues
    
    def _validate_student_info(self, info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate student information fields"""
        issues = []
        student_id = info.get('student_id', 'Unknown')
        
        # Required fields
        required_fields = {
            'student_id': 'Student ID',
            'student_name': 'Student Name',
            'program': 'Program'
        }
        
        for field, display_name in required_fields.items():
            if not info.get(field):
                issues.append({
                    'student_id': student_id,
                    'type': 'missing_required_field',
                    'field': field,
                    'severity': 'error',
                    'message': f'{display_name} is missing'
                })
        
        # Validate student ID format
        if info.get('student_id'):
            if not self.STUDENT_ID_PATTERN.match(info['student_id']):
                issues.append({
                    'student_id': student_id,
                    'type': 'invalid_student_id_format',
                    'value': info['student_id'],
                    'severity': 'error',
                    'message': f'Invalid student ID format: {info["student_id"]}'
                })
        
        # Validate time fields
        if info.get('start_time') and info.get('end_time'):
            start_time = info['start_time']
            end_time = info['end_time']
            
            # Check time format
            time_pattern = re.compile(r'^\d{1,2}:\d{2}$')
            if not time_pattern.match(start_time) or not time_pattern.match(end_time):
                issues.append({
                    'student_id': student_id,
                    'type': 'invalid_time_format',
                    'severity': 'warning',
                    'message': 'Invalid time format for start/end time'
                })
        
        return issues
    
    def _validate_sessions(self, sessions: List[Dict[str, Any]], student_id: str) -> List[Dict[str, Any]]:
        """Validate session data"""
        issues = []
        
        # Track session numbers for sequence validation
        session_numbers = []
        dates = []
        
        for i, session in enumerate(sessions):
            # Validate date format
            if session.get('date'):
                if not self.DATE_PATTERN.match(session['date']):
                    issues.append({
                        'student_id': student_id,
                        'type': 'invalid_date_format',
                        'session_index': i,
                        'value': session['date'],
                        'severity': 'error',
                        'message': f'Invalid date format in session {i+1}: {session["date"]}'
                    })
                else:
                    # Try to parse date
                    try:
                        date_obj = datetime.strptime(session['date'], '%d/%m/%Y')
                        dates.append(date_obj)
                    except ValueError:
                        issues.append({
                            'student_id': student_id,
                            'type': 'unparseable_date',
                            'session_index': i,
                            'value': session['date'],
                            'severity': 'error',
                            'message': f'Cannot parse date in session {i+1}: {session["date"]}'
                        })
            
            # Validate session number
            if session.get('session'):
                try:
                    session_num = int(session['session'])
                    session_numbers.append(session_num)
                except ValueError:
                    if session['session'] not in ['-', '']:
                        issues.append({
                            'student_id': student_id,
                            'type': 'invalid_session_number',
                            'session_index': i,
                            'value': session['session'],
                            'severity': 'warning',
                            'message': f'Non-numeric session number: {session["session"]}'
                        })
            
            # Validate attendance
            if session.get('attendance'):
                if session['attendance'] not in self.VALID_ATTENDANCE and session['attendance'] not in ['-', '']:
                    issues.append({
                        'student_id': student_id,
                        'type': 'invalid_attendance_value',
                        'session_index': i,
                        'value': session['attendance'],
                        'severity': 'warning',
                        'message': f'Invalid attendance value: {session["attendance"]}'
                    })
            
            # Validate progress
            if session.get('progress'):
                if session['progress'] not in self.VALID_PROGRESS:
                    issues.append({
                        'student_id': student_id,
                        'type': 'invalid_progress_value',
                        'session_index': i,
                        'value': session['progress'],
                        'severity': 'warning',
                        'message': f'Invalid progress value: {session["progress"]}'
                    })
        
        # Check date sequence (should be descending - most recent first)
        if len(dates) > 1:
            for i in range(1, len(dates)):
                if dates[i] > dates[i-1]:
                    issues.append({
                        'student_id': student_id,
                        'type': 'date_sequence_error',
                        'severity': 'warning',
                        'message': 'Dates are not in descending order'
                    })
                    break
        
        # Check session number sequence
        if len(session_numbers) > 1:
            # Remove duplicates while preserving order
            unique_sessions = []
            seen = set()
            for num in session_numbers:
                if num not in seen:
                    seen.add(num)
                    unique_sessions.append(num)
            
            # Check if generally descending
            descending_count = sum(1 for i in range(1, len(unique_sessions)) 
                                 if unique_sessions[i] < unique_sessions[i-1])
            if descending_count < len(unique_sessions) - 1:
                issues.append({
                    'student_id': student_id,
                    'type': 'session_sequence_warning',
                    'severity': 'info',
                    'message': 'Session numbers may not be in expected sequence'
                })
        
        return issues
    
    def _cross_validate(self, student_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform cross-validation checks"""
        issues = []
        student_info = student_data.get('info', {})
        student_id = student_info.get('student_id', 'Unknown')
        sessions = student_data.get('sessions', [])
        
        # Check: If student is marked as graduated, should have graduation session
        if student_info.get('status') == 'Graduated':
            has_graduation = any(
                'graduation' in session.get('lesson', '').lower() or
                session.get('progress') == 'Graduated'
                for session in sessions
            )
            if not has_graduation:
                issues.append({
                    'student_id': student_id,
                    'type': 'missing_graduation_record',
                    'severity': 'warning',
                    'message': 'Student marked as graduated but no graduation session found'
                })
        
        # Check: Attendance consistency
        attendance_sessions = [s for s in sessions if s.get('attendance') == 'Attended']
        progress_sessions = [s for s in sessions if s.get('progress') in ['Completed', 'In Progress']]
        
        if len(progress_sessions) > len(attendance_sessions) * 1.5:
            issues.append({
                'student_id': student_id,
                'type': 'attendance_progress_mismatch',
                'severity': 'info',
                'message': 'More progress records than attendance records'
            })
        
        return issues
    
    def validate_batch(self, students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of students
        
        Args:
            students: List of student records
            
        Returns:
            Validation summary
        """
        self.logger.info(f"Validating {len(students)} students...")
        
        all_issues = []
        issue_counts = defaultdict(int)
        students_with_issues = set()
        
        for student in students:
            issues = self.validate_student(student)
            if issues:
                student_id = student.get('info', {}).get('student_id', 'Unknown')
                students_with_issues.add(student_id)
                all_issues.extend(issues)
                
                for issue in issues:
                    issue_counts[issue['type']] += 1
        
        # Generate summary
        summary = {
            'total_students': len(students),
            'students_with_issues': len(students_with_issues),
            'total_issues': len(all_issues),
            'issue_counts': dict(issue_counts),
            'issues_by_severity': {
                'error': sum(1 for i in all_issues if i['severity'] == 'error'),
                'warning': sum(1 for i in all_issues if i['severity'] == 'warning'),
                'info': sum(1 for i in all_issues if i['severity'] == 'info')
            },
            'validation_rate': (len(students) - len(students_with_issues)) / len(students) if students else 0
        }
        
        self.logger.info(f"Validation complete: {summary['total_issues']} issues found")
        
        return summary, all_issues
    
    def generate_validation_report(self, summary: Dict[str, Any], issues: List[Dict[str, Any]]) -> str:
        """Generate a human-readable validation report"""
        report_lines = [
            "=" * 60,
            "DATA VALIDATION REPORT",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"Total students validated: {summary['total_students']}",
            f"Students with issues: {summary['students_with_issues']}",
            f"Total issues found: {summary['total_issues']}",
            f"Validation rate: {summary['validation_rate']:.1%}",
            "",
            "## Issues by Severity",
            f"Errors: {summary['issues_by_severity']['error']}",
            f"Warnings: {summary['issues_by_severity']['warning']}",
            f"Info: {summary['issues_by_severity']['info']}",
            "",
            "## Issues by Type"
        ]
        
        # Sort issue types by count
        sorted_types = sorted(summary['issue_counts'].items(), key=lambda x: x[1], reverse=True)
        for issue_type, count in sorted_types:
            report_lines.append(f"  {issue_type}: {count}")
        
        # Add sample issues
        if issues:
            report_lines.extend([
                "",
                "## Sample Issues (first 10)",
                "-" * 40
            ])
            
            for issue in issues[:10]:
                report_lines.append(
                    f"[{issue['severity'].upper()}] Student {issue['student_id']}: "
                    f"{issue['message']}"
                )
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)


def main():
    """Example usage"""
    validator = DataValidator()
    
    # Example student data
    test_student = {
        'info': {
            'student_id': 's10123',
            'student_name': 'Test Student',
            'program': 'AI-2',
            'start_time': '10:00',
            'end_time': '12:00'
        },
        'sessions': [
            {
                'date': '05/08/2025',
                'session': '10',
                'lesson': 'L10: Machine Learning',
                'attendance': 'Attended',
                'progress': 'Completed'
            },
            {
                'date': '29/07/2025',
                'session': '9',
                'lesson': 'L9: Data Science',
                'attendance': 'Attended',
                'progress': 'Completed'
            },
            {
                'date': 'invalid-date',
                'session': 'abc',
                'lesson': 'L8: Python',
                'attendance': 'Present',  # Invalid value
                'progress': 'Done'  # Invalid value
            }
        ]
    }
    
    # Validate single student
    print("Validating single student...")
    issues = validator.validate_student(test_student)
    for issue in issues:
        print(f"  [{issue['severity']}] {issue['message']}")
    
    # Validate batch
    print("\nValidating batch...")
    summary, all_issues = validator.validate_batch([test_student])
    
    # Generate report
    print("\n" + validator.generate_validation_report(summary, all_issues))


if __name__ == "__main__":
    main()