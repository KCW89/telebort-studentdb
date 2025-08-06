#!/usr/bin/env python3
"""
process_batches_13_15.py - Process batches 13-15 complete data with enhanced cleaning

This script processes batches 13, 14, and 15 complete data files and generates
enhanced student reports using the comprehensive data cleaning logic.

Features:
1. Loads all three batch JSON files (batch13, batch14, batch15)
2. Uses enhanced_data_processor.py for comprehensive data cleaning
3. Processes all students from the three batches
4. Handles 338-column structure properly
5. Generates high-quality student reports
6. Provides data quality improvements summary
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.enhanced_data_processor import EnhancedDataProcessor

class BatchProcessor_13_15:
    """Process batches 13-15 complete data"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        self.processor = EnhancedDataProcessor()
        
        # Ensure reports directory exists
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_batch_files(self) -> Dict[int, Dict]:
        """Load all three batch files"""
        batch_files = {
            13: 'batch13_complete.json',
            14: 'batch14_complete.json', 
            15: 'batch15_complete.json'
        }
        
        batches_data = {}
        
        for batch_num, filename in batch_files.items():
            filepath = os.path.join(self.base_dir, filename)
            
            if not os.path.exists(filepath):
                self.logger.error(f"Batch file not found: {filepath}")
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                    batches_data[batch_num] = batch_data
                    self.logger.info(f"Loaded batch {batch_num}: {batch_data['student_count']} students")
            except Exception as e:
                self.logger.error(f"Error loading {filename}: {e}")
        
        return batches_data
    
    def transform_raw_data(self, batch_data: Dict) -> List[Dict]:
        """Transform raw data from the 338-column format to structured format"""
        students = []
        
        raw_data = batch_data.get('raw_data', [])
        student_info = batch_data.get('students', [])
        
        if len(raw_data) != len(student_info):
            self.logger.warning(f"Mismatch: {len(raw_data)} raw data rows vs {len(student_info)} student info entries")
        
        for i, (raw_row, student_meta) in enumerate(zip(raw_data, student_info)):
            if not raw_row or len(raw_row) < 10:
                self.logger.warning(f"Skipping student {i}: insufficient data")
                continue
                
            try:
                student_data = self._parse_student_row(raw_row, student_meta)
                students.append(student_data)
            except Exception as e:
                self.logger.error(f"Error parsing student {student_meta.get('student_id', 'unknown')}: {e}")
        
        return students
    
    def _parse_student_row(self, raw_row: List, student_meta: Dict) -> Dict:
        """Parse a single student's raw data row"""
        
        # Extract basic info
        name = raw_row[0] if len(raw_row) > 0 else student_meta.get('name', '')
        student_id = raw_row[1] if len(raw_row) > 1 else student_meta.get('student_id', '')
        program = raw_row[2] if len(raw_row) > 2 else student_meta.get('program', '')
        
        # Extract schedule info (assuming columns 3-6 contain schedule data)
        schedule_parts = []
        if len(raw_row) > 3 and raw_row[3]:
            schedule_parts.append(raw_row[3])  # Day
        if len(raw_row) > 4 and raw_row[4]:
            schedule_parts.append(raw_row[4])  # Start time
        if len(raw_row) > 5 and raw_row[5]:
            schedule_parts.append(raw_row[5])  # End time
        
        schedule = ' '.join(filter(None, schedule_parts))
        
        # Extract primary teacher (column 6)
        primary_teacher = raw_row[6] if len(raw_row) > 6 else ''
        
        # Parse sessions (starting from column 7, in groups)
        sessions = []
        
        # The session data starts from column 7 and follows a pattern
        # We'll iterate through the remaining columns in groups
        session_start = 7
        
        while session_start < len(raw_row) - 4:  # Ensure we have at least 5 columns left
            try:
                session = self._parse_session_data(raw_row, session_start)
                if session and session.get('date') and session['date'] != '-':
                    sessions.append(session)
            except Exception as e:
                self.logger.debug(f"Error parsing session at index {session_start}: {e}")
            
            # Move to next session (typically 5-column groups: date, session, lesson, attendance, progress)
            session_start += 5
        
        return {
            'name': name.strip(),
            'student_id': student_id.strip(),
            'program': program.strip(),
            'schedule': schedule.strip(),
            'teacher': primary_teacher.strip(),
            'sessions': sessions
        }
    
    def _parse_session_data(self, raw_row: List, start_idx: int) -> Dict:
        """Parse session data from raw row starting at given index"""
        
        if start_idx + 4 >= len(raw_row):
            return {}
        
        # Extract session components (adjust indices based on actual data structure)
        date = raw_row[start_idx] if start_idx < len(raw_row) else ''
        session_num = raw_row[start_idx + 1] if start_idx + 1 < len(raw_row) else ''
        lesson = raw_row[start_idx + 2] if start_idx + 2 < len(raw_row) else ''
        attendance = raw_row[start_idx + 3] if start_idx + 3 < len(raw_row) else ''
        progress = raw_row[start_idx + 4] if start_idx + 4 < len(raw_row) else ''
        
        # Clean and validate data
        if not date or date.strip() in ['-', '']:
            return {}
        
        return {
            'date': str(date).strip(),
            'session': str(session_num).strip(),
            'lesson': str(lesson).strip(),
            'attendance': str(attendance).strip(),
            'progress': str(progress).strip()
        }
    
    def generate_student_report(self, student_data: Dict, quality_metrics: Dict) -> str:
        """Generate markdown report for a student"""
        
        name = student_data.get('name', 'Unknown')
        student_id = student_data.get('student_id', 'Unknown')
        program = student_data.get('program', 'Unknown')
        schedule = student_data.get('schedule', 'Not specified')
        teacher = student_data.get('teacher', 'Unknown')
        
        sessions = student_data.get('sessions', [])
        attendance_stats = student_data.get('attendance_stats', {})
        
        # Create report header
        report = []
        report.append(f"# Student Report - {name}")
        report.append(f"**Student ID:** {student_id}")
        report.append(f"**Program:** {program}")
        report.append(f"**Schedule:** {schedule}")
        report.append(f"**Primary Teacher:** {teacher}")
        report.append(f"**Report Generated:** {datetime.now().strftime('%d/%m/%Y at %H:%M')}")
        report.append("")
        
        # Attendance summary
        report.append("## Attendance Summary")
        if attendance_stats:
            report.append(f"- **Total Sessions:** {attendance_stats.get('total_sessions', 0)}")
            report.append(f"- **Classes Attended:** {attendance_stats.get('attended', 0)}")
            report.append(f"- **Classes Absent:** {attendance_stats.get('absent', 0)}")
            report.append(f"- **No Class/Holidays:** {attendance_stats.get('no_class', 0)}")
            report.append(f"- **Attendance Rate:** {attendance_stats.get('attendance_rate', 0):.1f}%")
        else:
            report.append("- No attendance data available")
        report.append("")
        
        # Session details
        report.append("## Session Details")
        if sessions:
            report.append("| Date | Session | Attendance | Teacher | Progress | Lesson |")
            report.append("|------|---------|------------|---------|----------|---------|")
            
            for session in sessions[:20]:  # Limit to first 20 sessions for readability
                date = session.get('date', '-')
                session_num = session.get('session', '-')
                attendance = session.get('attendance', '-')
                teacher_present = session.get('teacher_present', '-')
                progress = session.get('progress', '-')
                lesson_title = session.get('lesson_title', session.get('lesson_raw', ''))
                
                # Truncate long lesson titles
                if len(lesson_title) > 50:
                    lesson_title = lesson_title[:47] + "..."
                
                report.append(f"| {date} | {session_num} | {attendance} | {teacher_present} | {progress} | {lesson_title} |")
        else:
            report.append("No session data available.")
        
        report.append("")
        
        # Data quality improvements
        if quality_metrics and any(quality_metrics.values()):
            report.append("## Data Quality Improvements")
            if quality_metrics.get('teacher_name_fixes', 0) > 0:
                report.append(f"- Fixed {quality_metrics['teacher_name_fixes']} teacher name issues")
            if quality_metrics.get('progress_standardizations', 0) > 0:
                report.append(f"- Standardized {quality_metrics['progress_standardizations']} progress values")
            if quality_metrics.get('url_extractions', 0) > 0:
                report.append(f"- Extracted {quality_metrics['url_extractions']} URLs from lessons")
            if quality_metrics.get('missing_data_handled', 0) > 0:
                report.append(f"- Handled {quality_metrics['missing_data_handled']} missing data points")
            report.append("")
        
        report.append("---")
        report.append("*Report generated using enhanced data processing with comprehensive data cleaning*")
        
        return '\n'.join(report)
    
    def process_all_batches(self) -> Dict:
        """Process all batches and generate reports"""
        
        self.logger.info("Starting batch processing for batches 13-15")
        
        # Load batch files
        batches_data = self.load_batch_files()
        
        if not batches_data:
            self.logger.error("No batch files loaded")
            return {}
        
        results = {
            'processed_students': [],
            'total_students': 0,
            'total_sessions': 0,
            'program_distribution': {},
            'data_quality_summary': {},
            'batch_summary': {}
        }
        
        # Process each batch
        for batch_num, batch_data in batches_data.items():
            self.logger.info(f"Processing batch {batch_num}")
            
            # Transform raw data
            students_raw = self.transform_raw_data(batch_data)
            
            # Process with enhanced data processor
            processed_students, quality_metrics = self.processor.process_student_data(students_raw)
            
            # Generate reports
            reports_generated = 0
            for student in processed_students:
                student_id = student.get('student_id')
                if not student_id or student_id == 'Not Enrolled Yet':
                    continue
                
                try:
                    # Generate report
                    report_content = self.generate_student_report(student, quality_metrics)
                    
                    # Save report
                    report_filename = f"{student_id}.md"
                    report_path = os.path.join(self.reports_dir, report_filename)
                    
                    with open(report_path, 'w', encoding='utf-8') as f:
                        f.write(report_content)
                    
                    reports_generated += 1
                    
                    # Add to results
                    results['processed_students'].append({
                        'student_id': student_id,
                        'name': student.get('name', ''),
                        'program': student.get('program', ''),
                        'sessions': len(student.get('sessions', [])),
                        'attendance_rate': student.get('attendance_stats', {}).get('attendance_rate', 0)
                    })
                    
                    # Update program distribution
                    program = student.get('program', 'Unknown')
                    results['program_distribution'][program] = results['program_distribution'].get(program, 0) + 1
                    
                    # Count sessions
                    results['total_sessions'] += len(student.get('sessions', []))
                    
                except Exception as e:
                    self.logger.error(f"Error generating report for {student_id}: {e}")
            
            # Update batch summary
            results['batch_summary'][batch_num] = {
                'students_processed': reports_generated,
                'quality_fixes': sum(quality_metrics.values())
            }
            
            self.logger.info(f"Batch {batch_num}: {reports_generated} reports generated")
        
        # Update totals
        results['total_students'] = len(results['processed_students'])
        results['data_quality_summary'] = dict(self.processor.data_quality_metrics)
        
        # Save summary
        self._save_processing_summary(results)
        
        return results
    
    def _save_processing_summary(self, results: Dict):
        """Save processing summary to file"""
        summary_path = os.path.join(self.reports_dir, 'batches_13_15_summary.json')
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Processing summary saved to {summary_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving summary: {e}")
    
    def print_summary(self, results: Dict):
        """Print processing summary"""
        
        print("\n" + "="*60)
        print("BATCHES 13-15 PROCESSING SUMMARY")
        print("="*60)
        
        print(f"\nStudents Processed: {results['total_students']}")
        print(f"Total Sessions: {results['total_sessions']}")
        
        print(f"\nProgram Distribution:")
        for program, count in results['program_distribution'].items():
            print(f"  - {program}: {count} students")
        
        print(f"\nData Quality Improvements:")
        quality = results['data_quality_summary']
        for key, value in quality.items():
            if value > 0:
                print(f"  - {key.replace('_', ' ').title()}: {value}")
        
        print(f"\nBatch Summary:")
        for batch_num, summary in results['batch_summary'].items():
            print(f"  - Batch {batch_num}: {summary['students_processed']} students, {summary['quality_fixes']} quality fixes")
        
        print(f"\nStudent Details:")
        for student in results['processed_students'][:10]:  # Show first 10
            print(f"  - {student['student_id']} ({student['name']}): {student['program']}, {student['sessions']} sessions, {student['attendance_rate']:.1f}% attendance")
        
        if len(results['processed_students']) > 10:
            print(f"  ... and {len(results['processed_students']) - 10} more students")
        
        print(f"\nReports saved to: {self.reports_dir}")
        print("="*60)


def main():
    """Main processing function"""
    
    processor = BatchProcessor_13_15()
    
    try:
        results = processor.process_all_batches()
        processor.print_summary(results)
        
        print(f"\n✅ Successfully processed {results['total_students']} students from batches 13-15")
        print(f"📊 Generated enhanced reports with {sum(results['data_quality_summary'].values())} data quality improvements")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())