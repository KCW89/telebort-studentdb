#!/usr/bin/env python3
"""
process_data.py - Transforms raw student data into report-ready format

This script processes raw data from Google Sheets and prepares it for
report generation. Following the "blood test model", it only extracts
observable facts without any interpretation.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


class DataProcessor:
    """Processes student data without inference or interpretation"""
    
    def __init__(self):
        """Initialize the data processor"""
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('DataProcessor')
        logger.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        
        return logger
    
    def process_student(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process one student's raw data into report format
        
        Args:
            raw_data: Dictionary with 'info' and 'sessions' keys
            
        Returns:
            Dictionary with processed data ready for report generation
        """
        student_id = raw_data['info'].get('student_id', 'Unknown')
        self.logger.debug(f"Processing student {student_id}")
        
        try:
            processed = {
                'student_id': student_id,
                'current_status': self.extract_current_status(raw_data),
                'learning_journey': self.build_learning_journey(raw_data['sessions']),
                'attendance_summary': self.calculate_attendance(raw_data['sessions']),
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'week_number': datetime.now().isocalendar()[1],
                    'year': datetime.now().year
                }
            }
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Error processing student {student_id}: {str(e)}")
            raise
    
    def extract_current_status(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract current status from the latest non-empty session
        
        Args:
            raw_data: Student's raw data
            
        Returns:
            Dictionary with current status information
        """
        info = raw_data['info']
        sessions = raw_data['sessions']
        
        # Basic information from fixed columns
        status = {
            'program': info.get('program', ''),
            'schedule': f"{info.get('day', '')} {info.get('start_time', '')}-{info.get('end_time', '')}",
            'teacher': info.get('teacher', ''),
            'latest_session': '',
            'latest_session_date': '',
            'latest_lesson': '',
            'latest_status': ''
        }
        
        # Find the latest session with data
        for session in sessions:
            if session.get('session') and session.get('date'):
                status['latest_session'] = session['session']
                status['latest_session_date'] = session['date']
                status['latest_lesson'] = session.get('lesson', '')
                status['latest_status'] = session.get('progress', '')
                break
        
        return status
    
    def build_learning_journey(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build chronological learning journey from sessions
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            List of processed sessions (newest first)
        """
        journey = []
        
        for session in sessions:
            # Only include sessions with at least date or session number
            if session.get('date') or session.get('session'):
                journey_entry = {
                    'date': session.get('date', ''),
                    'session': session.get('session', ''),
                    'lesson': session.get('lesson', ''),
                    'attendance': session.get('attendance', ''),
                    'progress': session.get('progress', '')
                }
                journey.append(journey_entry)
        
        # Journey is already in newest-first order from the sheet
        return journey
    
    def calculate_attendance(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate attendance statistics from session data
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dictionary with attendance counts and percentage
        """
        attended = 0
        absent = 0
        no_class = 0
        total_with_data = 0
        
        for session in sessions:
            attendance = session.get('attendance', '').strip()
            
            if attendance:
                total_with_data += 1
                
                # Count based on attendance value
                if attendance.lower() in ['absent', 'cuti']:
                    absent += 1
                elif attendance.lower() in ['no class', 'in break', 'public holiday', 'ph']:
                    no_class += 1
                elif attendance:  # Any other non-empty value (teacher name, "attended", etc.)
                    attended += 1
        
        # Calculate percentage
        # Only count attended vs (attended + absent), excluding no class days
        countable_sessions = attended + absent
        attendance_rate = 0.0
        if countable_sessions > 0:
            attendance_rate = round((attended / countable_sessions) * 100, 1)
        
        return {
            'total_sessions': total_with_data,
            'attended': attended,
            'absent': absent,
            'no_class': no_class,
            'attendance_rate': attendance_rate,
            'countable_sessions': countable_sessions
        }
    
    def process_batch(self, students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of students
        
        Args:
            students: List of raw student data
            
        Returns:
            List of processed student data
        """
        processed_students = []
        errors = []
        
        for i, student in enumerate(students):
            try:
                processed = self.process_student(student)
                processed_students.append(processed)
            except Exception as e:
                student_id = student.get('info', {}).get('student_id', f'index_{i}')
                errors.append(f"Student {student_id}: {str(e)}")
                self.logger.error(f"Failed to process student {student_id}: {str(e)}")
        
        self.logger.info(f"Processed {len(processed_students)}/{len(students)} students successfully")
        
        if errors:
            self.logger.warning(f"{len(errors)} students failed processing")
        
        return processed_students


def main():
    """Main function for testing"""
    processor = DataProcessor()
    
    # Test data
    test_student = {
        'info': {
            'student_name': 'Test Student',
            'student_id': 's12345',
            'program': 'G (AI-2)',
            'day': 'Saturday',
            'start_time': '10:00',
            'end_time': '11:00',
            'teacher': 'Soumiya'
        },
        'sessions': [
            {
                'date': '09/08/2025',
                'session': '2',
                'lesson': 'C2 Machine Learning',
                'attendance': 'Soumiya',
                'progress': 'In Progress'
            },
            {
                'date': '02/08/2025',
                'session': '1',
                'lesson': 'C1 Introduction to AI',
                'attendance': 'Soumiya',
                'progress': 'Completed'
            },
            {
                'date': '26/07/2025',
                'session': '0',
                'lesson': '',
                'attendance': 'No Class',
                'progress': ''
            }
        ]
    }
    
    # Process test student
    result = processor.process_student(test_student)
    
    # Print results
    import json
    print(json.dumps(result, indent=2))
    
    return 0


if __name__ == "__main__":
    exit(main())