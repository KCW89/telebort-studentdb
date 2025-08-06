#!/usr/bin/env python3
"""
process_batches_10_12.py - Process batches 10-12 complete data and generate enhanced student reports

This script:
1. Loads batch10_complete.json, batch11_complete.json, batch12_complete.json
2. Uses enhanced_data_processor.py for data cleaning
3. Processes all 18 students (6 per batch)
4. Handles 338 columns (metadata 0-6, sessions from 7+ in 5-column pattern)
5. Generates enhanced student reports in scripts/reports/
6. Returns comprehensive summary with data quality metrics
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add the parent directory to the path so we can import enhanced_data_processor
script_dir = Path(__file__).parent
sys.path.append(str(script_dir.parent))

from scripts.enhanced_data_processor import EnhancedDataProcessor

class BatchProcessor10_12:
    """Process batches 10-12 with enhanced data processing"""
    
    def __init__(self):
        self.processor = EnhancedDataProcessor()
        self.base_path = Path(__file__).parent.parent
        self.reports_dir = self.base_path / "scripts" / "reports"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(exist_ok=True)
        
        # Summary data
        self.summary = {
            'total_students': 0,
            'batches_processed': [],
            'sessions_per_student': {},
            'teacher_distribution': {},
            'program_distribution': {},
            'data_quality_metrics': {},
            'reports_generated': [],
            'processing_errors': []
        }
    
    def process_all_batches(self) -> Dict[str, Any]:
        """Process all three batches and generate reports"""
        
        print("=== Processing Batches 10-12 Complete Data ===\n")
        
        # Load and process each batch
        batch_files = [
            ('batch10_complete.json', 10),
            ('batch11_complete.json', 11), 
            ('batch12_complete.json', 12)
        ]
        
        all_students = []
        
        for filename, batch_num in batch_files:
            print(f"Processing {filename}...")
            
            try:
                batch_data = self._load_batch_file(filename)
                students = self._convert_batch_to_student_format(batch_data, batch_num)
                all_students.extend(students)
                
                self.summary['batches_processed'].append({
                    'batch_number': batch_num,
                    'file': filename,
                    'students_count': len(students),
                    'status': 'success'
                })
                
                print(f"  ✓ Loaded {len(students)} students from batch {batch_num}")
                
            except Exception as e:
                error_msg = f"Error processing {filename}: {str(e)}"
                print(f"  ✗ {error_msg}")
                self.summary['processing_errors'].append(error_msg)
        
        # Process with enhanced data processor
        print(f"\nProcessing {len(all_students)} students with enhanced data cleaning...")
        processed_students, quality_metrics = self.processor.process_student_data(all_students)
        
        self.summary['total_students'] = len(processed_students)
        self.summary['data_quality_metrics'] = quality_metrics
        
        # Generate reports for each student
        print(f"\nGenerating reports for {len(processed_students)} students...")
        for student in processed_students:
            try:
                self._generate_student_report(student)
                self.summary['reports_generated'].append(student['student_id'])
                
                # Update statistics
                student_id = student['student_id']
                sessions_count = len(student['sessions'])
                self.summary['sessions_per_student'][student_id] = sessions_count
                
                # Teacher distribution
                teacher = student['teacher']
                self.summary['teacher_distribution'][teacher] = self.summary['teacher_distribution'].get(teacher, 0) + 1
                
                # Program distribution
                program = student['program']
                self.summary['program_distribution'][program] = self.summary['program_distribution'].get(program, 0) + 1
                
            except Exception as e:
                error_msg = f"Error generating report for {student.get('student_id', 'unknown')}: {str(e)}"
                print(f"  ✗ {error_msg}")
                self.summary['processing_errors'].append(error_msg)
        
        print(f"\n✓ Successfully generated {len(self.summary['reports_generated'])} reports")
        
        return self.summary
    
    def _load_batch_file(self, filename: str) -> Dict:
        """Load a batch JSON file"""
        filepath = self.base_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Batch file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _convert_batch_to_student_format(self, batch_data: Dict, batch_num: int) -> List[Dict]:
        """Convert batch JSON format to student format expected by enhanced processor"""
        
        students = []
        raw_data = batch_data.get('raw_data', [])
        student_metadata = batch_data.get('students', [])
        
        for i, student_row in enumerate(raw_data):
            try:
                # Get student metadata
                if i < len(student_metadata):
                    student_info = student_metadata[i]
                    student_id = student_info['id']
                    name = student_info['name']
                    program = student_info['program']
                    teacher = student_info['teacher']
                else:
                    # Fallback to extracting from raw data
                    student_id = student_row[1] if len(student_row) > 1 else f"s{batch_num}_{i:03d}"
                    name = student_row[0] if len(student_row) > 0 else "Unknown"
                    program = student_row[2] if len(student_row) > 2 else "Unknown"
                    teacher = student_row[6] if len(student_row) > 6 else "Unknown"
                
                # Build schedule from metadata columns
                schedule = "Unknown"
                if len(student_row) >= 7:
                    day = student_row[3] if len(student_row) > 3 else ""
                    start_time = student_row[4] if len(student_row) > 4 else ""
                    end_time = student_row[5] if len(student_row) > 5 else ""
                    if day and start_time and end_time:
                        schedule = f"{day} {start_time}-{end_time}"
                
                # Parse sessions from columns 7+ (5-column pattern)
                sessions = self._parse_sessions_from_row(student_row[7:])
                
                student_data = {
                    'student_id': student_id,
                    'name': name,
                    'program': program,
                    'schedule': schedule,
                    'teacher': teacher,
                    'sessions': sessions
                }
                
                students.append(student_data)
                
            except Exception as e:
                print(f"    Warning: Error processing student row {i}: {e}")
                continue
        
        return students
    
    def _parse_sessions_from_row(self, session_data: List) -> List[Dict]:
        """Parse sessions from row data (5-column pattern: date, session, lesson, attendance, progress)"""
        
        sessions = []
        
        # Process in groups of 5 columns
        for i in range(0, len(session_data), 5):
            if i + 4 >= len(session_data):
                break
            
            date = session_data[i] if i < len(session_data) else ""
            session_num = session_data[i + 1] if i + 1 < len(session_data) else ""
            lesson = session_data[i + 2] if i + 2 < len(session_data) else ""
            attendance = session_data[i + 3] if i + 3 < len(session_data) else ""
            progress = session_data[i + 4] if i + 4 < len(session_data) else ""
            
            # Skip empty sessions
            if not date or date == '-' or date == '':
                continue
            
            session = {
                'date': str(date).strip(),
                'session': str(session_num).strip() if session_num else "",
                'lesson': str(lesson).strip() if lesson else "",
                'attendance': str(attendance).strip() if attendance else "",
                'progress': str(progress).strip() if progress else ""
            }
            
            sessions.append(session)
        
        return sessions
    
    def _generate_student_report(self, student_data: Dict):
        """Generate enhanced markdown report for a student"""
        
        student_id = student_data['student_id']
        report_path = self.reports_dir / f"{student_id}.md"
        
        # Calculate statistics
        sessions = student_data.get('sessions', [])
        attendance_stats = student_data.get('attendance_stats', {})
        
        # Get date range
        valid_sessions = [s for s in sessions if s['date'] and s['date'] != '-']
        if valid_sessions:
            dates = [self._parse_date(s['date']) for s in valid_sessions]
            dates = [d for d in dates if d != datetime.min]
            if dates:
                start_date = min(dates).strftime('%d/%m/%Y')
                end_date = max(dates).strftime('%d/%m/%Y')
                date_range = f"{start_date} - {end_date}"
            else:
                date_range = "No valid dates"
        else:
            date_range = "No sessions"
        
        # Calculate progress distribution
        progress_counts = {}
        for session in sessions:
            progress = session.get('progress', 'Not Started')
            progress_counts[progress] = progress_counts.get(progress, 0) + 1
        
        # Generate report content
        content = f"""# Enhanced Student Report - {student_data.get('name', 'Unknown')}

**Student ID:** {student_id}
**Program:** {student_data.get('program', 'Unknown')}
**Schedule:** {student_data.get('schedule', 'Unknown')}
**Primary Teacher:** {student_data.get('teacher', 'Unknown')}
**Total Sessions:** {len(sessions)}
**Date Range:** {date_range}

## Attendance Summary

- **Total Sessions:** {attendance_stats.get('total_sessions', 0)}
- **Classes Attended:** {attendance_stats.get('attended', 0)}
- **Classes Absent:** {attendance_stats.get('absent', 0)}
- **No Class/Holiday:** {attendance_stats.get('no_class', 0)}
- **Attendance Rate:** {attendance_stats.get('attendance_rate', 0):.1f}%

## Progress Distribution

"""
        
        for progress, count in progress_counts.items():
            content += f"- **{progress}:** {count} sessions\n"
        
        content += "\n## Session Details\n\n"
        content += "| Date | Session | Attendance | Teacher | Progress | Lesson/Topic |\n"
        content += "|------|---------|------------|---------|----------|---------------|\n"
        
        for session in sessions:
            date = session.get('date', '-')
            session_num = session.get('session', '-')
            attendance = session.get('attendance', '-')
            teacher = session.get('teacher_present', student_data.get('teacher', '-'))
            progress = session.get('progress', '-')
            lesson_title = session.get('lesson_title', session.get('lesson', '-'))
            
            # Truncate long lesson titles
            if len(lesson_title) > 50:
                lesson_title = lesson_title[:47] + "..."
            
            content += f"| {date} | {session_num} | {attendance} | {teacher} | {progress} | {lesson_title} |\n"
        
        # Add data quality information
        content += f"\n## Data Quality Information\n\n"
        content += f"- **Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"- **Data Source:** Batch processing from complete data JSON files\n"
        content += f"- **Enhanced Processing:** Applied data cleaning and standardization\n"
        
        if sessions:
            urls_found = sum(1 for s in sessions if s.get('lesson_url') or s.get('activity_url'))
            content += f"- **URLs Extracted:** {urls_found} sessions contain lesson/activity URLs\n"
        
        # Write the report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Generated report: {report_path.name}")
    
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
                return datetime.min
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print comprehensive processing summary"""
        
        print("\n" + "="*60)
        print("BATCH 10-12 PROCESSING SUMMARY")
        print("="*60)
        
        # Basic statistics
        print(f"\nSTUDENT PROCESSING:")
        print(f"  Total Students Processed: {summary['total_students']}")
        print(f"  Reports Generated: {len(summary['reports_generated'])}")
        print(f"  Processing Errors: {len(summary['processing_errors'])}")
        
        # Batch details
        print(f"\nBATCH DETAILS:")
        for batch in summary['batches_processed']:
            status_icon = "✓" if batch['status'] == 'success' else "✗"
            print(f"  {status_icon} Batch {batch['batch_number']}: {batch['students_count']} students ({batch['file']})")
        
        # Sessions per student
        print(f"\nSESSIONS PER STUDENT:")
        for student_id, session_count in summary['sessions_per_student'].items():
            print(f"  {student_id}: {session_count} sessions")
        
        # Teacher distribution
        print(f"\nTEACHER DISTRIBUTION:")
        for teacher, count in sorted(summary['teacher_distribution'].items()):
            print(f"  {teacher}: {count} students")
        
        # Program distribution  
        print(f"\nPROGRAM DISTRIBUTION:")
        for program, count in sorted(summary['program_distribution'].items()):
            print(f"  {program}: {count} students")
        
        # Data quality metrics
        print(f"\nDATA QUALITY IMPROVEMENTS:")
        metrics = summary['data_quality_metrics']
        print(f"  Teacher name fixes: {metrics.get('teacher_name_fixes', 0)}")
        print(f"  Progress standardizations: {metrics.get('progress_standardizations', 0)}")
        print(f"  URL extractions: {metrics.get('url_extractions', 0)}")
        print(f"  Missing data handled: {metrics.get('missing_data_handled', 0)}")
        print(f"  Invalid sessions fixed: {metrics.get('invalid_sessions_fixed', 0)}")
        total_fixes = sum(metrics.values())
        print(f"  TOTAL IMPROVEMENTS: {total_fixes}")
        
        # Errors (if any)
        if summary['processing_errors']:
            print(f"\nPROCESSING ERRORS:")
            for error in summary['processing_errors']:
                print(f"  ✗ {error}")
        
        print(f"\nREPORTS LOCATION: {self.reports_dir}")
        print("="*60)

def main():
    """Main execution function"""
    
    processor = BatchProcessor10_12()
    
    try:
        # Process all batches
        summary = processor.process_all_batches()
        
        # Print comprehensive summary
        processor.print_summary(summary)
        
        # Save summary to file
        summary_path = processor.base_path / "scripts" / "batch_10_12_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            # Convert datetime objects to strings for JSON serialization
            json_summary = json.loads(json.dumps(summary, default=str))
            json.dump(json_summary, f, indent=2)
        
        print(f"\nSummary saved to: {summary_path}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Fatal error during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)