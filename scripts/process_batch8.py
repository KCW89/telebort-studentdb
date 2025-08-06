#!/usr/bin/env python3
"""
process_batch8.py - Process batch8_complete.json and generate student reports

This script processes the batch8_complete.json data containing 6 students and generates
markdown reports using the enhanced data processor for data quality improvements.
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Add the scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_data_processor import EnhancedDataProcessor

class Batch8Processor:
    """Process batch8 complete data and generate student reports"""
    
    def __init__(self, base_dir: str):
        """Initialize processor with base directory"""
        self.base_dir = base_dir
        self.scripts_dir = os.path.join(base_dir, "scripts")
        self.batch_file = os.path.join(base_dir, "batch8_complete.json")
        self.enhanced_processor = EnhancedDataProcessor()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_batch_data(self) -> Dict[str, Any]:
        """Load the batch8_complete.json data"""
        try:
            with open(self.batch_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded batch {data['batch']} with {data['student_count']} students")
            return data
        
        except FileNotFoundError:
            self.logger.error(f"Batch file not found: {self.batch_file}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in batch file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading batch data: {e}")
            raise
    
    def convert_raw_data_to_structured(self, batch_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert raw data array to structured student data"""
        students = batch_data.get('students', [])
        raw_data = batch_data.get('raw_data', [])
        
        structured_students = []
        
        for i, student_info in enumerate(students):
            if i >= len(raw_data):
                self.logger.warning(f"No raw data for student {student_info['id']}")
                continue
            
            raw_row = raw_data[i]
            
            # Parse student basic info (first 6 columns)
            student_data = {
                'student_id': student_info['id'],
                'name': student_info['name'],
                'program': raw_row[2] if len(raw_row) > 2 else '',  # Column 2: Program
                'schedule': f"{raw_row[3]} {raw_row[4]}-{raw_row[5]}" if len(raw_row) > 5 else '',  # Columns 3-5: Schedule
                'teacher': raw_row[6] if len(raw_row) > 6 else '',  # Column 6: Teacher
                'sessions': []
            }
            
            # Parse sessions (starting from column 7, every 8 columns)
            sessions = self._parse_sessions_from_raw(raw_row[7:])  # Skip first 7 columns
            student_data['sessions'] = sessions
            
            structured_students.append(student_data)
            self.logger.info(f"Converted student {student_data['student_id']} with {len(sessions)} sessions")
        
        return structured_students
    
    def _parse_sessions_from_raw(self, session_data: List[str]) -> List[Dict[str, Any]]:
        """Parse sessions from raw data (variable pattern)"""
        sessions = []
        
        # The data structure varies, but typically follows patterns like:
        # date, session, lesson, teacher/attendance, progress, [additional fields]
        # We need to identify sessions by looking for valid dates
        
        i = 0
        while i < len(session_data):
            # Look for a date pattern (DD/MM/YYYY)
            current_item = session_data[i].strip() if session_data[i] else ''
            
            # Check if this looks like a date
            if self._is_valid_date(current_item):
                # Found a potential session start
                date = current_item
                session_num = ''
                lesson = ''
                attendance = ''
                progress = ''
                
                # Try to extract the next few fields
                if i + 1 < len(session_data):
                    next_field = session_data[i + 1].strip() if session_data[i + 1] else ''
                    # This could be session number or lesson
                    if next_field.isdigit() or next_field.startswith('S') or next_field.startswith('L'):
                        session_num = next_field
                        
                        # Look for lesson in next field
                        if i + 2 < len(session_data):
                            lesson = session_data[i + 2].strip() if session_data[i + 2] else ''
                            
                            # Look for attendance/teacher
                            if i + 3 < len(session_data):
                                attendance = session_data[i + 3].strip() if session_data[i + 3] else ''
                                
                                # Look for progress
                                if i + 4 < len(session_data):
                                    progress = session_data[i + 4].strip() if session_data[i + 4] else ''
                    else:
                        # Next field might be lesson directly
                        lesson = next_field
                        if i + 2 < len(session_data):
                            attendance = session_data[i + 2].strip() if session_data[i + 2] else ''
                            if i + 3 < len(session_data):
                                progress = session_data[i + 3].strip() if session_data[i + 3] else ''
                
                session = {
                    'date': date,
                    'session': session_num,
                    'lesson': lesson,
                    'attendance': attendance,
                    'progress': progress
                }
                
                sessions.append(session)
                i += 5  # Move forward by a reasonable step
            else:
                i += 1  # Move to next item
        
        return sessions
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if a string looks like a valid date"""
        if not date_str or date_str == '-':
            return False
        
        # Check for DD/MM/YYYY pattern
        import re
        date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
        return bool(re.match(date_pattern, date_str))
    
    def process_students(self, structured_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process students using enhanced data processor"""
        
        self.logger.info(f"Processing {len(structured_data)} students with enhanced data processor")
        
        # Process with enhanced cleaning
        processed_data, quality_metrics = self.enhanced_processor.process_student_data(structured_data)
        
        self.logger.info(f"Enhanced processing complete. Quality metrics: {quality_metrics}")
        
        return processed_data
    
    def generate_student_report(self, student_data: Dict[str, Any]) -> str:
        """Generate markdown report for a student"""
        
        student_id = student_data['student_id']
        name = student_data['name']
        program = student_data['program']
        schedule = student_data['schedule']
        teacher = student_data['teacher']
        sessions = student_data['sessions']
        attendance_stats = student_data.get('attendance_stats', {})
        
        # Generate report content
        report_lines = []
        report_lines.append(f"# Student Attendance & Progress Report - {name}")
        report_lines.append(f"**Student:** {name}")
        report_lines.append(f"**Student ID:** {student_id}")
        report_lines.append(f"**Program:** {program}")
        report_lines.append(f"**Schedule:** {schedule}")
        report_lines.append(f"**Primary Teacher:** {teacher}")
        report_lines.append(f"**Total Sessions:** {len(sessions)}")
        report_lines.append("")
        
        # Add attendance statistics
        if attendance_stats:
            report_lines.append("## Summary Statistics")
            report_lines.append(f"- Classes Attended: {attendance_stats.get('attended', 0)}")
            report_lines.append(f"- Classes Absent: {attendance_stats.get('absent', 0)}")
            report_lines.append(f"- No Class/Holiday: {attendance_stats.get('no_class', 0)}")
            report_lines.append(f"- Attendance Rate: {attendance_stats.get('attendance_rate', 0):.1f}%")
            report_lines.append("")
        
        # Add detailed session log
        report_lines.append("## Detailed Session Log")
        report_lines.append("| Date | Session | Attendance | Teacher | Progress | Lesson/Topic |")
        report_lines.append("|------|---------|------------|---------|----------|--------------|")
        
        for session in sessions:
            date = session['date']
            session_num = session['session']
            attendance = session['attendance']
            teacher_present = session.get('teacher_present', teacher)
            progress = session['progress']
            lesson_title = session.get('lesson_title', session.get('lesson', ''))
            
            # Clean lesson title for table display
            lesson_display = lesson_title.replace('|', '\\|').replace('\n', ' ')[:100]
            if len(lesson_title) > 100:
                lesson_display += "..."
            
            report_lines.append(f"| {date} | {session_num} | {attendance} | {teacher_present} | {progress} | {lesson_display} |")
        
        # Add URLs section if any sessions have URLs
        url_sessions = [s for s in sessions if s.get('lesson_url') or s.get('activity_url')]
        if url_sessions:
            report_lines.append("")
            report_lines.append("## Lesson Resources")
            for session in url_sessions:
                if session.get('lesson_url'):
                    report_lines.append(f"- **{session['date']}**: {session.get('lesson_title', 'Lesson')}")
                    report_lines.append(f"  - Lesson: {session['lesson_url']}")
                    if session.get('activity_url'):
                        report_lines.append(f"  - Activity: {session['activity_url']}")
        
        # Add data quality note
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*Report generated with enhanced data processing and quality improvements*")
        report_lines.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return '\n'.join(report_lines)
    
    def save_reports(self, processed_students: List[Dict[str, Any]]) -> Dict[str, str]:
        """Save individual student reports and return summary"""
        
        results = {}
        reports_dir = os.path.join(self.scripts_dir, "reports")
        
        # Ensure reports directory exists
        os.makedirs(reports_dir, exist_ok=True)
        
        for student_data in processed_students:
            student_id = student_data['student_id']
            
            # Generate report
            report_content = self.generate_student_report(student_data)
            
            # Save to file
            report_file = os.path.join(reports_dir, f"{student_id}.md")
            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                results[student_id] = report_file
                self.logger.info(f"Saved report for {student_id}: {report_file}")
                
            except Exception as e:
                self.logger.error(f"Error saving report for {student_id}: {e}")
                results[student_id] = f"Error: {e}"
        
        return results
    
    def process_batch8(self) -> Dict[str, Any]:
        """Main processing method"""
        
        self.logger.info("Starting batch8 processing")
        
        # Load batch data
        batch_data = self.load_batch_data()
        
        # Convert to structured format
        structured_data = self.convert_raw_data_to_structured(batch_data)
        
        # Process with enhanced cleaning
        processed_students = self.process_students(structured_data)
        
        # Save reports
        report_files = self.save_reports(processed_students)
        
        # Generate summary
        summary = {
            'batch_number': batch_data['batch'],
            'students_processed': len(processed_students),
            'report_files': report_files,
            'data_quality_metrics': self.enhanced_processor.data_quality_metrics,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # Generate session count summary
        session_counts = {}
        for student in processed_students:
            student_id = student['student_id']
            session_count = len(student['sessions'])
            session_counts[student_id] = session_count
        
        summary['session_counts'] = session_counts
        
        self.logger.info(f"Batch8 processing complete: {len(processed_students)} students processed")
        
        return summary


def main():
    """Main execution function"""
    
    # Determine base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize and run processor
    processor = Batch8Processor(base_dir)
    
    try:
        results = processor.process_batch8()
        
        print("\n=== Batch8 Processing Results ===")
        print(f"Students processed: {results['students_processed']}")
        print(f"Data quality improvements: {sum(results['data_quality_metrics'].values())}")
        print("\nSession counts per student:")
        for student_id, count in results['session_counts'].items():
            print(f"  {student_id}: {count} sessions")
        
        print(f"\nData quality metrics:")
        for metric, count in results['data_quality_metrics'].items():
            print(f"  {metric}: {count}")
        
        print("\nReport files generated:")
        for student_id, file_path in results['report_files'].items():
            print(f"  {student_id}: {file_path}")
        
        # Also generate quality report
        quality_report = processor.enhanced_processor.generate_quality_report()
        print(f"\n{quality_report}")
        
        return results
        
    except Exception as e:
        logging.error(f"Batch8 processing failed: {e}")
        raise


if __name__ == "__main__":
    main()