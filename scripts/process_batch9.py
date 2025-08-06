#!/usr/bin/env python3
"""
process_batch9.py - Process batch 9 complete data and generate student reports

This script:
1. Loads the batch9_complete.json data
2. Uses enhanced_data_processor.py to clean the data
3. Processes each student's complete historical data (all 338 columns)
4. Generates markdown reports for each student
5. Handles teacher name fixes, progress standardization, and URL extraction
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

# Add the scripts directory to Python path
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from enhanced_data_processor import EnhancedDataProcessor

class Batch9Processor:
    """Process batch 9 complete data and generate reports"""
    
    def __init__(self):
        self.processor = EnhancedDataProcessor()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.results_summary = {
            'students_processed': 0,
            'total_sessions': 0,
            'reports_generated': 0,
            'data_quality_improvements': 0
        }
    
    def load_batch9_data(self, json_file: Path) -> Dict:
        """Load batch 9 complete data from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Loaded batch 9 data: {data['student_count']} students")
            return data
        except Exception as e:
            self.logger.error(f"Error loading batch 9 data: {e}")
            raise
    
    def convert_raw_data_to_structured(self, batch_data: Dict) -> List[Dict]:
        """Convert raw batch data to structured format for processing"""
        structured_data = []
        
        for i, student_info in enumerate(batch_data['students']):
            student_id = student_info['id']
            student_name = student_info['name']
            raw_row = batch_data['raw_data'][i]
            
            # Parse the 338-column structure (every 8 columns is one session)
            student_record = {
                'student_id': student_id,
                'name': student_name,
                'program': raw_row[2] if len(raw_row) > 2 else '',
                'schedule': self._build_schedule(raw_row),
                'teacher': raw_row[6] if len(raw_row) > 6 else '',
                'sessions': []
            }
            
            # Process every 5 columns as one session starting from column 7
            session_count = 0
            for col_start in range(7, len(raw_row), 5):  # Start from column 7 (first date), step by 5
                if col_start + 4 < len(raw_row):
                    session = self._parse_session_from_columns(raw_row, col_start)
                    if session:
                        session_count += 1
                        student_record['sessions'].append(session)
            
            self.logger.info(f"Processed {student_id} ({student_name}): {session_count} sessions")
            structured_data.append(student_record)
        
        return structured_data
    
    def _build_schedule(self, raw_row: List) -> str:
        """Build schedule string from raw data"""
        try:
            day = raw_row[3] if len(raw_row) > 3 else ''
            start_time = raw_row[4] if len(raw_row) > 4 else ''
            end_time = raw_row[5] if len(raw_row) > 5 else ''
            
            if day and start_time and end_time:
                return f"{day} {start_time}-{end_time}"
            return "Schedule TBD"
        except:
            return "Schedule TBD"
    
    def _parse_session_from_columns(self, raw_row: List, col_start: int) -> Dict:
        """Parse session data from 5-column group"""
        try:
            # Column structure: Date, Session, Lesson, Attendance, Progress  
            date = raw_row[col_start] if col_start < len(raw_row) else ''
            session = raw_row[col_start + 1] if col_start + 1 < len(raw_row) else ''
            lesson = raw_row[col_start + 2] if col_start + 2 < len(raw_row) else ''
            attendance = raw_row[col_start + 3] if col_start + 3 < len(raw_row) else ''
            progress = raw_row[col_start + 4] if col_start + 4 < len(raw_row) else ''
            
            # Skip empty or invalid sessions
            if not date or date == '-' or not date.strip():
                return None
            
            return {
                'date': date.strip(),
                'session': session,
                'lesson': lesson,
                'attendance': attendance,
                'progress': progress
            }
        except Exception as e:
            self.logger.warning(f"Error parsing session at column {col_start}: {e}")
            return None
    
    def process_students(self, structured_data: List[Dict]) -> List[Dict]:
        """Process students using enhanced data processor"""
        processed_students, quality_metrics = self.processor.process_student_data(structured_data)
        
        self.results_summary['students_processed'] = len(processed_students)
        self.results_summary['data_quality_improvements'] = sum(quality_metrics.values())
        
        # Count total sessions
        total_sessions = sum(len(student['sessions']) for student in processed_students)
        self.results_summary['total_sessions'] = total_sessions
        
        return processed_students
    
    def generate_student_report(self, student: Dict, output_dir: Path) -> bool:
        """Generate markdown report for a single student"""
        try:
            report_path = output_dir / f"{student['student_id']}.md"
            
            # Build the markdown report
            report_lines = []
            
            # Header
            report_lines.append(f"# Student Progress Report - {student['name']}")
            report_lines.append(f"**Student ID:** {student['student_id']}")
            report_lines.append(f"**Program:** {student['program']}")
            report_lines.append(f"**Schedule:** {student['schedule']}")
            report_lines.append(f"**Primary Teacher:** {student['teacher']}")
            report_lines.append(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            # Summary Statistics
            stats = student['attendance_stats']
            report_lines.append("## Summary Statistics")
            report_lines.append(f"- Total Sessions: {stats['total_sessions']}")
            report_lines.append(f"- Classes Attended: {stats['attended']}")
            report_lines.append(f"- Classes Absent: {stats['absent']}")
            report_lines.append(f"- No Class Days: {stats['no_class']}")
            report_lines.append(f"- Attendance Rate: {stats['attendance_rate']}%")
            report_lines.append("")
            
            # Detailed Session History
            report_lines.append("## Detailed Session History")
            report_lines.append("| Date | Session | Attendance | Teacher | Progress | Lesson |")
            report_lines.append("|------|---------|------------|---------|----------|--------|")
            
            for session in student['sessions']:
                date = session['date']
                session_num = session['session']
                attendance = session['attendance']
                teacher = session['teacher_present']
                progress = session['progress']
                lesson = session['lesson_title'][:50] + "..." if len(session['lesson_title']) > 50 else session['lesson_title']
                
                report_lines.append(f"| {date} | {session_num} | {attendance} | {teacher} | {progress} | {lesson} |")
            
            report_lines.append("")
            
            # URL Links (if any)
            urls = []
            for session in student['sessions']:
                if session['lesson_url']:
                    urls.append(f"- [{session['lesson_title']}]({session['lesson_url']})")
                if session['activity_url']:
                    urls.append(f"  - Activity: {session['activity_url']}")
            
            if urls:
                report_lines.append("## Resource Links")
                report_lines.extend(urls[:20])  # Limit to first 20 URLs
                if len(urls) > 20:
                    report_lines.append("... (additional links available)")
                report_lines.append("")
            
            # Data Quality Notes
            report_lines.append("## Notes")
            report_lines.append("- This report was generated using enhanced data processing")
            report_lines.append("- Teacher names have been normalized from attendance fields")
            report_lines.append("- Progress values have been standardized")
            report_lines.append("- URLs have been extracted from lesson descriptions")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("*Report generated by Telebort Student Data Management System*")
            
            # Write the report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            self.logger.info(f"Generated report for {student['student_id']} at {report_path}")
            self.results_summary['reports_generated'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating report for {student['student_id']}: {e}")
            return False
    
    def generate_processing_summary(self) -> str:
        """Generate summary of processing results"""
        summary_lines = []
        summary_lines.append("=== Batch 9 Processing Summary ===")
        summary_lines.append(f"Students Processed: {self.results_summary['students_processed']}")
        summary_lines.append(f"Total Sessions Parsed: {self.results_summary['total_sessions']}")
        summary_lines.append(f"Reports Generated: {self.results_summary['reports_generated']}")
        summary_lines.append(f"Data Quality Improvements: {self.results_summary['data_quality_improvements']}")
        summary_lines.append("")
        summary_lines.append("Student Details:")
        
        return '\n'.join(summary_lines)

def main():
    """Main processing function"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Define paths
    project_root = Path(__file__).parent.parent
    batch9_file = project_root / "batch9_complete.json"
    output_dir = project_root / "Teacher Yasmin"  # Use existing teacher folder
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize processor
        processor = Batch9Processor()
        
        # Load batch 9 data
        logger.info("Loading batch 9 data...")
        batch_data = processor.load_batch9_data(batch9_file)
        
        # Convert to structured format
        logger.info("Converting raw data to structured format...")
        structured_data = processor.convert_raw_data_to_structured(batch_data)
        
        # Process students with enhanced cleaning
        logger.info("Processing students with enhanced data cleaning...")
        processed_students = processor.process_students(structured_data)
        
        # Generate reports for each student
        logger.info("Generating student reports...")
        for student in processed_students:
            processor.generate_student_report(student, output_dir)
        
        # Generate and display summary
        summary = processor.generate_processing_summary()
        print("\n" + summary)
        
        # Print data quality report
        print("\n" + processor.processor.generate_quality_report())
        
        # Print individual student stats
        print("\nIndividual Student Statistics:")
        for student in processed_students:
            stats = student['attendance_stats']
            print(f"- {student['student_id']} ({student['name']}): {stats['total_sessions']} sessions, {stats['attendance_rate']}% attendance")
        
        logger.info("Batch 9 processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in batch 9 processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()