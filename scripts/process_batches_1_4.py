#!/usr/bin/env python3
"""
process_batches_1_4.py - Process batch1_complete.json and batch4_complete.json

This script processes both batch files containing complete student data and generates
enhanced student reports using the enhanced data processor for data quality improvements.

Batch 1: Contains 6 students with 338-column raw data structure
Batch 4: Contains 6 students with pre-structured JSON format
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

class BatchesProcessor:
    """Process batch1 and batch4 complete data and generate student reports"""
    
    def __init__(self, base_dir: str):
        """Initialize processor with base directory"""
        self.base_dir = base_dir
        self.scripts_dir = os.path.join(base_dir, "scripts")
        self.batch1_file = os.path.join(base_dir, "batch1_complete.json")
        self.batch4_file = os.path.join(base_dir, "batch4_complete.json")
        self.enhanced_processor = EnhancedDataProcessor()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_batch1_data(self) -> Dict[str, Any]:
        """Load the batch1_complete.json data (338-column format)"""
        try:
            with open(self.batch1_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Batch 1 has a different structure with 'results' containing rows
            if 'results' in data and len(data['results']) > 0:
                rows = data['results'][0].get('rows', [])
                self.logger.info(f"Loaded batch 1 with {len(rows)} students from 338-column format")
                return {'format': '338-column', 'rows': rows, 'batch': 1}
            else:
                self.logger.error("Batch 1 data does not contain expected 'results' structure")
                raise ValueError("Invalid batch 1 data structure")
            
        except FileNotFoundError:
            self.logger.error(f"Batch 1 file not found: {self.batch1_file}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in batch 1 file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading batch 1 data: {e}")
            raise
    
    def load_batch4_data(self) -> Dict[str, Any]:
        """Load the batch4_complete.json data (structured format)"""
        try:
            with open(self.batch4_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Batch 4 appears to be a list of structured student objects
            if isinstance(data, list):
                self.logger.info(f"Loaded batch 4 with {len(data)} students from structured format")
                return {'format': 'structured', 'students': data, 'batch': 4}
            else:
                self.logger.error("Batch 4 data is not in expected list format")
                raise ValueError("Invalid batch 4 data structure")
            
        except FileNotFoundError:
            self.logger.error(f"Batch 4 file not found: {self.batch4_file}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in batch 4 file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading batch 4 data: {e}")
            raise
    
    def convert_338_column_to_structured(self, rows: List[List]) -> List[Dict[str, Any]]:
        """Convert 338-column raw data to structured student data"""
        structured_students = []
        
        for row_data in rows:
            if not row_data or len(row_data) < 8:
                self.logger.warning(f"Skipping row with insufficient data: {len(row_data) if row_data else 0} columns")
                continue
            
            # Extract basic student info from first columns
            name = row_data[0] if len(row_data) > 0 else ''
            # Second column appears to be empty in batch1
            student_id = row_data[2] if len(row_data) > 2 else ''
            program = row_data[3] if len(row_data) > 3 else ''
            day = row_data[4] if len(row_data) > 4 else ''
            start_time = row_data[5] if len(row_data) > 5 else ''
            end_time = row_data[6] if len(row_data) > 6 else ''
            teacher = row_data[7] if len(row_data) > 7 else ''
            
            # Create schedule string
            schedule = f"{day} {start_time}-{end_time}" if day and start_time and end_time else ''
            
            student_data = {
                'student_id': student_id,
                'name': name,
                'program': program,
                'schedule': schedule,
                'teacher': teacher,
                'sessions': []
            }
            
            # Parse sessions from remaining columns (starting from index 8)
            sessions = self._parse_338_sessions(row_data[8:])
            student_data['sessions'] = sessions
            
            structured_students.append(student_data)
            self.logger.info(f"Converted 338-column student {student_id} ({name}) with {len(sessions)} sessions")
        
        return structured_students
    
    def _parse_338_sessions(self, session_data: List[str]) -> List[Dict[str, Any]]:
        """Parse sessions from 338-column format (remaining columns after basic info)"""
        sessions = []
        
        # The format appears to be: date, session, lesson, teacher, progress, repeated
        # But the exact pattern may vary, so we'll look for dates as anchors
        
        i = 0
        while i < len(session_data) - 4:  # Need at least 5 columns for a complete session
            current_item = session_data[i].strip() if session_data[i] else ''
            
            # Check if this looks like a date (DD/MM/YYYY)
            if self._is_valid_date(current_item):
                date = current_item
                
                # Extract the next fields (session, lesson, teacher, progress)
                session_num = session_data[i + 1].strip() if i + 1 < len(session_data) else ''
                lesson = session_data[i + 2].strip() if i + 2 < len(session_data) else ''
                teacher_or_attendance = session_data[i + 3].strip() if i + 3 < len(session_data) else ''
                progress = session_data[i + 4].strip() if i + 4 < len(session_data) else ''
                
                session = {
                    'date': date,
                    'session': session_num,
                    'lesson': lesson,
                    'attendance': teacher_or_attendance,
                    'progress': progress
                }
                
                sessions.append(session)
                i += 5  # Move to next potential session
            else:
                i += 1  # Move to next item
        
        return sessions
    
    def convert_structured_to_standard(self, students: List[Dict]) -> List[Dict[str, Any]]:
        """Convert batch4 structured format to standard format"""
        structured_students = []
        
        for student_data in students:
            # Batch4 data is already well-structured
            student = {
                'student_id': student_data.get('student_id', ''),
                'name': student_data.get('name', ''),
                'program': student_data.get('program', ''),
                'schedule': student_data.get('schedule', ''),
                'teacher': student_data.get('teacher', ''),
                'sessions': []
            }
            
            # Extract sessions
            sessions_data = student_data.get('sessions', [])
            for session_raw in sessions_data:
                session = {
                    'date': session_raw.get('date', ''),
                    'session': session_raw.get('session', ''),
                    'lesson': session_raw.get('lesson', ''),
                    'attendance': session_raw.get('attendance', ''),
                    'progress': session_raw.get('progress', '')
                }
                student['sessions'].append(session)
            
            structured_students.append(student)
            self.logger.info(f"Converted structured student {student['student_id']} ({student['name']}) with {len(student['sessions'])} sessions")
        
        return structured_students
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if a string looks like a valid date"""
        if not date_str or date_str == '-':
            return False
        
        # Check for DD/MM/YYYY pattern
        import re
        date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
        return bool(re.match(date_pattern, date_str))
    
    def process_students(self, structured_data: List[Dict[str, Any]], batch_num: int) -> List[Dict[str, Any]]:
        """Process students using enhanced data processor"""
        
        self.logger.info(f"Processing {len(structured_data)} students from batch {batch_num} with enhanced data processor")
        
        # Process with enhanced cleaning
        processed_data, quality_metrics = self.enhanced_processor.process_student_data(structured_data)
        
        self.logger.info(f"Enhanced processing complete for batch {batch_num}. Quality metrics: {quality_metrics}")
        
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
        report_lines.append("*Processed from batch 1 & 4 complete data*")
        report_lines.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return '\n'.join(report_lines)
    
    def save_reports(self, processed_students: List[Dict[str, Any]], batch_num: int) -> Dict[str, str]:
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
                self.logger.info(f"Saved report for {student_id} (batch {batch_num}): {report_file}")
                
            except Exception as e:
                self.logger.error(f"Error saving report for {student_id}: {e}")
                results[student_id] = f"Error: {e}"
        
        return results
    
    def process_all_batches(self) -> Dict[str, Any]:
        """Main processing method for both batches"""
        
        self.logger.info("Starting batch 1 & 4 processing")
        
        all_processed_students = []
        all_report_files = {}
        batch_summaries = {}
        
        # Process Batch 1
        try:
            self.logger.info("Processing Batch 1...")
            batch1_data = self.load_batch1_data()
            
            if batch1_data['format'] == '338-column':
                structured_data = self.convert_338_column_to_structured(batch1_data['rows'])
            else:
                raise ValueError("Unexpected batch1 format")
            
            processed_students = self.process_students(structured_data, 1)
            all_processed_students.extend(processed_students)
            
            batch1_reports = self.save_reports(processed_students, 1)
            all_report_files.update(batch1_reports)
            
            batch_summaries['batch1'] = {
                'students_processed': len(processed_students),
                'student_ids': [s['student_id'] for s in processed_students],
                'student_names': [f"{s['student_id']}: {s['name']}" for s in processed_students]
            }
            
        except Exception as e:
            self.logger.error(f"Error processing batch 1: {e}")
            batch_summaries['batch1'] = {'error': str(e), 'students_processed': 0}
        
        # Process Batch 4
        try:
            self.logger.info("Processing Batch 4...")
            batch4_data = self.load_batch4_data()
            
            if batch4_data['format'] == 'structured':
                structured_data = self.convert_structured_to_standard(batch4_data['students'])
            else:
                raise ValueError("Unexpected batch4 format")
            
            processed_students = self.process_students(structured_data, 4)
            all_processed_students.extend(processed_students)
            
            batch4_reports = self.save_reports(processed_students, 4)
            all_report_files.update(batch4_reports)
            
            batch_summaries['batch4'] = {
                'students_processed': len(processed_students),
                'student_ids': [s['student_id'] for s in processed_students],
                'student_names': [f"{s['student_id']}: {s['name']}" for s in processed_students]
            }
            
        except Exception as e:
            self.logger.error(f"Error processing batch 4: {e}")
            batch_summaries['batch4'] = {'error': str(e), 'students_processed': 0}
        
        # Generate overall summary
        total_students = len(all_processed_students)
        
        # Generate session count summary
        session_counts = {}
        for student in all_processed_students:
            student_id = student['student_id']
            session_count = len(student['sessions'])
            session_counts[student_id] = session_count
        
        summary = {
            'batches_processed': [1, 4],
            'total_students_processed': total_students,
            'batch_summaries': batch_summaries,
            'report_files': all_report_files,
            'session_counts': session_counts,
            'data_quality_metrics': self.enhanced_processor.data_quality_metrics,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"All batches processing complete: {total_students} total students processed")
        
        return summary


def main():
    """Main execution function"""
    
    # Determine base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize and run processor
    processor = BatchesProcessor(base_dir)
    
    try:
        results = processor.process_all_batches()
        
        print("\n=== Batches 1 & 4 Processing Results ===")
        print(f"Total students processed: {results['total_students_processed']}")
        print(f"Data quality improvements: {sum(results['data_quality_metrics'].values())}")
        
        # Print batch-by-batch summary
        for batch_name, batch_info in results['batch_summaries'].items():
            print(f"\n{batch_name.upper()} Summary:")
            if 'error' in batch_info:
                print(f"  ERROR: {batch_info['error']}")
            else:
                print(f"  Students processed: {batch_info['students_processed']}")
                print("  Student names:")
                for name_info in batch_info['student_names']:
                    print(f"    - {name_info}")
        
        print(f"\nSession counts per student:")
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
        logging.error(f"Batches processing failed: {e}")
        raise


if __name__ == "__main__":
    main()