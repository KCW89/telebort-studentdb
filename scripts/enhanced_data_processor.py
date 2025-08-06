#!/usr/bin/env python3
"""
enhanced_data_processor.py - Enhanced data processor with data quality fixes

This version includes all the data cleaning logic identified in the data quality analysis:
1. Fixes teacher names in attendance fields
2. Standardizes progress values
3. Extracts URLs from lesson fields
4. Handles missing data appropriately
5. Provides data quality metrics
"""

import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import logging

class EnhancedDataProcessor:
    """Enhanced processor with comprehensive data cleaning"""
    
    # Known teacher names that appear in attendance field
    TEACHER_NAMES = [
        'Soumiya', 'Han Yang', 'Khairina', 'Arrvinna', 
        'Syahin', 'Hafiz', 'Yasmin', 'Nurafrina',
        'Rahmat', 'Fatin', 'Aisyah', 'Puvin'
    ]
    
    # Progress value standardization
    PROGRESS_MAP = {
        'COMPLETED': 'Completed',
        'completed': 'Completed', 
        'Complete': 'Completed',
        'IN PROGRESS': 'In Progress',
        'in progress': 'In Progress',
        'In progress': 'In Progress',
        'GRADUATED': 'Graduated',
        'graduated': 'Graduated',
        'NOT STARTED': 'Not Started',
        'not started': 'Not Started',
        '-': 'Not Started',
        '': 'Not Started',
        None: 'Not Started'
    }
    
    # Valid attendance values
    VALID_ATTENDANCE = {
        'Attended', 'Absent', 'No Class', 'Public Holiday',
        'In Break', 'Teacher Parent Day', 'Hari Raya Holiday',
        'Not Marked'
    }
    
    def __init__(self):
        """Initialize the enhanced processor"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data_quality_metrics = {
            'teacher_name_fixes': 0,
            'progress_standardizations': 0,
            'url_extractions': 0,
            'missing_data_handled': 0,
            'invalid_sessions_fixed': 0
        }
    
    def process_student_data(self, raw_data: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Process raw student data with enhanced cleaning
        
        Returns:
            Tuple of (processed_data, quality_metrics)
        """
        processed = []
        
        for student_raw in raw_data:
            try:
                student_data = self._process_single_student(student_raw)
                if student_data:
                    processed.append(student_data)
            except Exception as e:
                self.logger.error(f"Error processing student {student_raw.get('student_id', 'unknown')}: {e}")
        
        self.logger.info(f"Data quality metrics: {self.data_quality_metrics}")
        return processed, self.data_quality_metrics
    
    def _process_single_student(self, raw: Dict) -> Optional[Dict]:
        """Process a single student's data with all cleaning logic"""
        
        # Extract basic info
        student_id = raw.get('student_id', '').strip()
        if not student_id:
            return None
            
        student_data = {
            'student_id': student_id,
            'name': raw.get('name', '').strip(),
            'program': self._clean_program(raw.get('program', '')),
            'schedule': self._clean_schedule(raw.get('schedule', '')),
            'teacher': self._extract_primary_teacher(raw),
            'sessions': []
        }
        
        # Process each session
        sessions_data = raw.get('sessions', [])
        for session_raw in sessions_data:
            session = self._process_session(session_raw, student_data['teacher'])
            if session:
                student_data['sessions'].append(session)
        
        # Sort sessions by date
        student_data['sessions'].sort(key=lambda x: self._parse_date(x['date']), reverse=True)
        
        # Calculate attendance stats
        student_data['attendance_stats'] = self._calculate_attendance_stats(student_data['sessions'])
        
        return student_data
    
    def _process_session(self, session_raw: Dict, default_teacher: str) -> Optional[Dict]:
        """Process a single session with comprehensive cleaning"""
        
        date = session_raw.get('date', '').strip()
        if not date or date == '-':
            self.data_quality_metrics['missing_data_handled'] += 1
            return None
        
        # Clean attendance field
        attendance_raw = session_raw.get('attendance', '').strip()
        attendance, actual_teacher = self._clean_attendance(attendance_raw)
        
        # Clean progress field  
        progress_raw = session_raw.get('progress', '')
        progress = self._standardize_progress(progress_raw)
        
        # Clean lesson field
        lesson_raw = session_raw.get('lesson', '').strip()
        lesson_data = self._parse_lesson(lesson_raw)
        
        # Clean session number
        session_num = self._clean_session_number(session_raw.get('session', ''))
        
        return {
            'date': date,
            'session': session_num,
            'attendance': attendance,
            'teacher_present': actual_teacher or default_teacher,
            'progress': progress,
            'lesson_title': lesson_data['title'],
            'lesson_url': lesson_data['url'],
            'activity_url': lesson_data['activity_url'],
            'exit_ticket': lesson_data['exit_ticket'],
            'lesson_raw': lesson_raw  # Preserve original for reference
        }
    
    def _clean_attendance(self, attendance: str) -> Tuple[str, Optional[str]]:
        """
        Clean attendance field and extract teacher if present
        
        Returns:
            Tuple of (cleaned_attendance, teacher_name)
        """
        attendance = attendance.strip()
        
        # Check if it's a teacher name
        if attendance in self.TEACHER_NAMES:
            self.data_quality_metrics['teacher_name_fixes'] += 1
            return ('Attended', attendance)
        
        # Check if it's a valid attendance value
        if attendance in self.VALID_ATTENDANCE:
            return (attendance, None)
        
        # Handle edge cases
        if attendance == '':
            return ('Not Marked', None)
        if attendance == '-':
            return ('Not Marked', None)
            
        # Unknown value - log it
        self.logger.warning(f"Unknown attendance value: {attendance}")
        return (attendance, None)
    
    def _standardize_progress(self, progress: str) -> str:
        """Standardize progress values to consistent format"""
        
        if not isinstance(progress, str):
            progress = str(progress) if progress else ''
        
        progress = progress.strip()
        
        # Direct mapping
        if progress in self.PROGRESS_MAP:
            standardized = self.PROGRESS_MAP[progress]
            if standardized != progress:
                self.data_quality_metrics['progress_standardizations'] += 1
            return standardized
        
        # Check for partial matches
        progress_lower = progress.lower()
        if 'complet' in progress_lower:
            self.data_quality_metrics['progress_standardizations'] += 1
            return 'Completed'
        elif 'progress' in progress_lower:
            self.data_quality_metrics['progress_standardizations'] += 1
            return 'In Progress'
        elif 'graduat' in progress_lower:
            self.data_quality_metrics['progress_standardizations'] += 1
            return 'Graduated'
        elif 'start' in progress_lower:
            return 'Not Started'
        
        # Default for unknown
        return 'Not Started' if not progress else progress
    
    def _parse_lesson(self, lesson: str) -> Dict[str, str]:
        """
        Parse lesson field to extract components
        
        Returns dict with:
            - title: Main lesson title
            - url: Primary lesson URL
            - activity_url: Activity/form URL
            - exit_ticket: Exit ticket score if present
        """
        result = {
            'title': '',
            'url': '',
            'activity_url': '',
            'exit_ticket': ''
        }
        
        if not lesson or lesson == '-':
            return result
        
        # Extract URLs
        urls = re.findall(r'https?://[^\s]+', lesson)
        if urls:
            self.data_quality_metrics['url_extractions'] += 1
            result['url'] = urls[0] if urls else ''
            result['activity_url'] = urls[1] if len(urls) > 1 else ''
            
            # Remove URLs from lesson text
            lesson_text = lesson
            for url in urls:
                lesson_text = lesson_text.replace(url, '')
        else:
            lesson_text = lesson
        
        # Extract exit ticket score
        et_match = re.search(r'ET:\s*(\d+/\d+)', lesson_text)
        if et_match:
            result['exit_ticket'] = et_match.group(1)
            lesson_text = lesson_text.replace(et_match.group(0), '')
        
        # Clean up the title
        lesson_text = re.sub(r'\s+', ' ', lesson_text)  # Normalize whitespace
        lesson_text = lesson_text.replace('\\n', ' ')  # Remove newlines
        lesson_text = lesson_text.strip()
        
        # Handle multiple lessons separated by newlines
        if '\\n' in lesson or '\n' in lesson:
            # Take the first lesson as primary
            parts = re.split(r'\\n|\n', lesson)
            lesson_text = parts[0] if parts else lesson_text
        
        result['title'] = lesson_text
        return result
    
    def _clean_session_number(self, session: Any) -> str:
        """Clean and validate session number"""
        
        if not session:
            return '0'
        
        session_str = str(session).strip()
        
        # Remove any non-numeric characters
        session_clean = re.sub(r'[^\d]', '', session_str)
        
        if not session_clean:
            self.data_quality_metrics['invalid_sessions_fixed'] += 1
            return '0'
        
        # Validate reasonable range (0-100)
        try:
            session_num = int(session_clean)
            if session_num < 0 or session_num > 100:
                self.data_quality_metrics['invalid_sessions_fixed'] += 1
                return '0'
            return str(session_num)
        except ValueError:
            self.data_quality_metrics['invalid_sessions_fixed'] += 1
            return '0'
    
    def _clean_program(self, program: str) -> str:
        """Clean program name"""
        if not program or program == '-':
            return 'Unknown'
        
        # Remove extra spaces and normalize
        program = re.sub(r'\s+', ' ', program.strip())
        
        # Standardize known programs
        program_map = {
            'G (AI-2)': 'AI-2',
            'F (AI-1)': 'AI-1', 
            'AI-3': 'AI-3',
            'H (BBD)': 'BBD',
            'BBP': 'BBP',
            'C (W-1)': 'Web-1',
            'D (W-2)': 'Web-2',
            'E (W-3)': 'Web-3'
        }
        
        return program_map.get(program, program)
    
    def _clean_schedule(self, schedule: str) -> str:
        """Clean schedule information"""
        if not schedule or schedule == '-' or schedule == ' -':
            self.data_quality_metrics['missing_data_handled'] += 1
            return 'Schedule TBD'
        
        return schedule.strip()
    
    def _extract_primary_teacher(self, raw: Dict) -> str:
        """Extract the primary teacher from the data"""
        
        # Try the teacher field first
        teacher = raw.get('teacher', '').strip()
        if teacher and teacher != '-':
            return teacher
        
        # Look through sessions for teacher names
        sessions = raw.get('sessions', [])
        teacher_counts = {}
        
        for session in sessions:
            attendance = session.get('attendance', '')
            if attendance in self.TEACHER_NAMES:
                teacher_counts[attendance] = teacher_counts.get(attendance, 0) + 1
        
        # Return most frequent teacher
        if teacher_counts:
            return max(teacher_counts, key=teacher_counts.get)
        
        return 'Unknown'
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str or date_str == '-':
            return datetime.min
        
        try:
            # Try DD/MM/YYYY format
            return datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            try:
                # Try other formats
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                self.logger.warning(f"Could not parse date: {date_str}")
                return datetime.min
    
    def _calculate_attendance_stats(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Calculate attendance statistics"""
        
        total = len(sessions)
        attended = sum(1 for s in sessions if s['attendance'] == 'Attended')
        absent = sum(1 for s in sessions if s['attendance'] == 'Absent')
        no_class = sum(1 for s in sessions if s['attendance'] in ['No Class', 'Public Holiday', 'In Break'])
        
        # Calculate rate only for actual classes
        actual_classes = attended + absent
        attendance_rate = (attended / actual_classes * 100) if actual_classes > 0 else 0
        
        return {
            'total_sessions': total,
            'attended': attended,
            'absent': absent, 
            'no_class': no_class,
            'attendance_rate': round(attendance_rate, 1)
        }
    
    def generate_quality_report(self) -> str:
        """Generate a report on data quality improvements made"""
        
        report = []
        report.append("=== Data Quality Report ===")
        report.append(f"Teacher name fixes: {self.data_quality_metrics['teacher_name_fixes']}")
        report.append(f"Progress standardizations: {self.data_quality_metrics['progress_standardizations']}")
        report.append(f"URL extractions: {self.data_quality_metrics['url_extractions']}")
        report.append(f"Missing data handled: {self.data_quality_metrics['missing_data_handled']}")
        report.append(f"Invalid sessions fixed: {self.data_quality_metrics['invalid_sessions_fixed']}")
        
        total_fixes = sum(self.data_quality_metrics.values())
        report.append(f"\nTotal data quality improvements: {total_fixes}")
        
        return '\n'.join(report)


# Example usage
if __name__ == "__main__":
    import json
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize processor
    processor = EnhancedDataProcessor()
    
    # Load sample data (you would load from sheets_data.json)
    sample_data = [
        {
            'student_id': 's10769',
            'name': 'Nathakit Shotiwoth',
            'program': 'G (AI-2)',
            'schedule': 'Saturday 10:00-11:00',
            'teacher': 'Soumiya',
            'sessions': [
                {
                    'date': '19/07/2025',
                    'session': '1',
                    'lesson': 'L1 Introduction to AI https://www.telebort.com/demo/ai1/lesson/1 ET: 5/5',
                    'attendance': 'Soumiya',  # Teacher name instead of "Attended"
                    'progress': 'COMPLETED'  # Needs standardization
                },
                {
                    'date': '26/07/2025', 
                    'session': '1',
                    'lesson': '-',
                    'attendance': 'Absent',
                    'progress': '-'
                }
            ]
        }
    ]
    
    # Process the data
    processed_data, quality_metrics = processor.process_student_data(sample_data)
    
    # Print results
    print("\n=== Processed Data ===")
    print(json.dumps(processed_data, indent=2))
    
    print("\n" + processor.generate_quality_report())