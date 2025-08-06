#!/usr/bin/env python3
"""
process_batches_16_18.py - Process final batches 16-18 complete data

This script processes all students from batches 16, 17, and 18 using the enhanced
data processor and generates comprehensive reports.

Total students: 17 (6 from batch 16, 6 from batch 17, 5 from batch 18)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import logging

# Add the scripts directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_data_processor import EnhancedDataProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_batch_data(batch_file: str) -> Dict:
    """Load batch data from JSON file"""
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Batch file not found: {batch_file}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {batch_file}: {e}")
        return {}

def convert_raw_to_sessions(raw_data: List) -> List[Dict]:
    """
    Convert raw Google Sheets data to session format expected by processor
    
    Raw data format: each row is a list with repeating 8-column pattern:
    [0] Date, [1] Attendance, [2] Teacher, [3] Session, [4] Submission, [5] Lesson, [6] Exit, [7] Progress
    """
    sessions = []
    
    if not raw_data:
        return sessions
    
    # Process each 8-column group
    for i in range(7, len(raw_data), 8):  # Start from index 7 (first date), step by 8
        if i >= len(raw_data):
            break
            
        date = raw_data[i] if i < len(raw_data) else ''
        attendance = raw_data[i + 1] if i + 1 < len(raw_data) else ''
        teacher = raw_data[i + 2] if i + 2 < len(raw_data) else ''
        session = raw_data[i + 3] if i + 3 < len(raw_data) else ''
        submission = raw_data[i + 4] if i + 4 < len(raw_data) else ''
        lesson = raw_data[i + 5] if i + 5 < len(raw_data) else ''
        exit_ticket = raw_data[i + 6] if i + 6 < len(raw_data) else ''
        progress = raw_data[i + 7] if i + 7 < len(raw_data) else ''
        
        # Skip empty entries
        if not date or date == '-' or date.strip() == '':
            continue
            
        # Create session object
        session_data = {
            'date': date.strip() if isinstance(date, str) else str(date),
            'session': session.strip() if isinstance(session, str) else str(session),
            'attendance': attendance.strip() if isinstance(attendance, str) else str(attendance),
            'teacher': teacher.strip() if isinstance(teacher, str) else str(teacher),
            'lesson': lesson.strip() if isinstance(lesson, str) else str(lesson),
            'progress': progress.strip() if isinstance(progress, str) else str(progress),
            'submission': submission.strip() if isinstance(submission, str) else str(submission),
            'exit_ticket': exit_ticket.strip() if isinstance(exit_ticket, str) else str(exit_ticket)
        }
        
        sessions.append(session_data)
    
    return sessions

def process_batch_students(batch_data: Dict) -> List[Dict]:
    """Convert batch data to format expected by enhanced processor"""
    
    students_data = []
    
    if 'students' not in batch_data or 'raw_data' not in batch_data:
        logger.error("Invalid batch data format")
        return students_data
    
    students_info = batch_data['students']
    raw_rows = batch_data['raw_data']
    
    # Process each student
    for i, student_info in enumerate(students_info):
        if i >= len(raw_rows):
            logger.warning(f"Missing raw data for student {student_info['student_id']}")
            continue
            
        raw_row = raw_rows[i]
        sessions = convert_raw_to_sessions(raw_row)
        
        student_data = {
            'student_id': student_info['student_id'],
            'name': student_info['name'],
            'program': student_info['program'],
            'schedule': student_info['schedule'],
            'teacher': student_info['teacher'],
            'sessions': sessions
        }
        
        students_data.append(student_data)
        logger.info(f"Processed student {student_info['student_id']} with {len(sessions)} sessions")
    
    return students_data

def generate_markdown_report(student_data: Dict, output_dir: str) -> str:
    """Generate markdown report for a student"""
    
    student_id = student_data['student_id']
    name = student_data['name']
    program = student_data['program']
    schedule = student_data['schedule']
    teacher = student_data['teacher']
    sessions = student_data['sessions']
    stats = student_data.get('attendance_stats', {})
    
    # Calculate date range
    valid_dates = [s['date'] for s in sessions if s['date'] and s['date'] != '-']
    if valid_dates:
        # Sort dates chronologically
        try:
            sorted_dates = sorted(valid_dates, key=lambda x: datetime.strptime(x, '%d/%m/%Y'))
            date_range = f"{sorted_dates[0]} - {sorted_dates[-1]}"
        except:
            date_range = f"{valid_dates[0]} - {valid_dates[-1]}"
    else:
        date_range = "No valid dates"
    
    # Start building the report
    report = []
    report.append(f"# Student Progress Report - {student_id}")
    report.append(f"**Student:** {name}")
    report.append(f"**Program:** {program}")
    report.append(f"**Schedule:** {schedule}")
    report.append(f"**Primary Teacher:** {teacher}")
    report.append(f"**Total Sessions:** {stats.get('total_sessions', len(sessions))}")
    report.append(f"**Date Range:** {date_range}")
    report.append("")
    
    # Summary statistics
    report.append("## Summary Statistics")
    report.append(f"- Classes Attended: {stats.get('attended', 0)}")
    report.append(f"- Classes Absent: {stats.get('absent', 0)}")
    report.append(f"- No Class/Holidays: {stats.get('no_class', 0)}")
    report.append(f"- Attendance Rate: {stats.get('attendance_rate', 0):.1f}%")
    report.append("")
    
    # Progress summary
    if sessions:
        completed = sum(1 for s in sessions if s.get('progress') == 'Completed')
        in_progress = sum(1 for s in sessions if s.get('progress') == 'In Progress')
        graduated = sum(1 for s in sessions if s.get('progress') == 'Graduated')
        
        report.append("## Progress Summary")
        report.append(f"- Completed: {completed}")
        report.append(f"- In Progress: {in_progress}")
        report.append(f"- Graduated: {graduated}")
        report.append("")
    
    # Detailed session log
    report.append("## Detailed Session Log")
    report.append("| Date | Session | Attendance | Teacher | Progress | Lesson |")
    report.append("|------|---------|------------|---------|----------|--------|")
    
    for session in sessions:
        date = session.get('date', '-')
        session_num = session.get('session', '-')
        attendance = session.get('attendance', '-')
        teacher_present = session.get('teacher_present', session.get('teacher', '-'))
        progress = session.get('progress', '-')
        lesson = session.get('lesson_title', session.get('lesson', '-'))
        
        # Truncate long lesson titles
        if len(lesson) > 50:
            lesson = lesson[:47] + "..."
        
        # Escape markdown characters
        lesson = lesson.replace('|', '\\|')
        
        report.append(f"| {date} | {session_num} | {attendance} | {teacher_present} | {progress} | {lesson} |")
    
    report.append("")
    report.append("---")
    report.append(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Write to file
    report_filename = f"{student_id}.md"
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    return report_path

def main():
    """Main processing function"""
    
    # Define paths
    base_dir = "/Users/chongwei/Telebort Engineering/telebort-studentdb"
    batch_files = [
        os.path.join(base_dir, "batch16_complete.json"),
        os.path.join(base_dir, "batch17_complete.json"),  
        os.path.join(base_dir, "batch18_complete.json")
    ]
    
    output_dir = os.path.join(base_dir, "scripts", "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("Starting processing of batches 16-18")
    
    # Initialize the enhanced processor
    processor = EnhancedDataProcessor()
    
    # Collect all students from all batches
    all_students = []
    batch_summaries = []
    
    for i, batch_file in enumerate(batch_files, 16):
        logger.info(f"Processing batch {i}...")
        
        batch_data = load_batch_data(batch_file)
        if not batch_data:
            logger.error(f"Failed to load batch {i}")
            continue
        
        # Convert to processor format
        students_data = process_batch_students(batch_data)
        
        batch_summary = {
            'batch_number': i,
            'student_count': len(students_data),
            'students': [s['student_id'] for s in students_data]
        }
        batch_summaries.append(batch_summary)
        
        # Add to all students
        all_students.extend(students_data)
        
        logger.info(f"Batch {i}: {len(students_data)} students processed")
    
    logger.info(f"Total students collected: {len(all_students)}")
    
    # Process all students with enhanced processor
    logger.info("Applying enhanced data processing...")
    processed_students, quality_metrics = processor.process_student_data(all_students)
    
    logger.info(f"Enhanced processing completed. {len(processed_students)} students processed.")
    
    # Generate reports for each student
    logger.info("Generating individual student reports...")
    
    report_paths = []
    for student in processed_students:
        try:
            report_path = generate_markdown_report(student, output_dir)
            report_paths.append(report_path)
            logger.info(f"Generated report: {os.path.basename(report_path)}")
        except Exception as e:
            logger.error(f"Error generating report for {student['student_id']}: {e}")
    
    # Generate summary report
    summary_data = generate_summary_report(processed_students, batch_summaries, quality_metrics, output_dir)
    
    logger.info("Processing completed successfully!")
    logger.info(f"Generated {len(report_paths)} individual reports")
    logger.info(f"Output directory: {output_dir}")
    
    return summary_data

def generate_summary_report(students: List[Dict], batch_summaries: List[Dict], 
                          quality_metrics: Dict, output_dir: str) -> Dict:
    """Generate comprehensive summary report"""
    
    # Calculate overall statistics
    total_students = len(students)
    
    # Program breakdown
    programs = {}
    teachers = {}
    total_sessions = 0
    total_attended = 0
    total_absent = 0
    
    for student in students:
        program = student.get('program', 'Unknown')
        programs[program] = programs.get(program, 0) + 1
        
        teacher = student.get('teacher', 'Unknown')
        teachers[teacher] = teachers.get(teacher, 0) + 1
        
        stats = student.get('attendance_stats', {})
        total_sessions += stats.get('total_sessions', 0)
        total_attended += stats.get('attended', 0) 
        total_absent += stats.get('absent', 0)
    
    # Calculate overall attendance rate
    actual_classes = total_attended + total_absent
    overall_attendance_rate = (total_attended / actual_classes * 100) if actual_classes > 0 else 0
    
    summary_data = {
        'processing_date': datetime.now().isoformat(),
        'total_students': total_students,
        'batches_processed': [16, 17, 18],
        'batch_breakdown': batch_summaries,
        'programs': programs,
        'teachers': teachers,
        'session_stats': {
            'total_sessions': total_sessions,
            'total_attended': total_attended,
            'total_absent': total_absent,
            'overall_attendance_rate': round(overall_attendance_rate, 1)
        },
        'data_quality_metrics': quality_metrics,
        'students': []
    }
    
    # Add student summaries
    for student in students:
        student_summary = {
            'student_id': student['student_id'],
            'name': student['name'],
            'program': student['program'],
            'teacher': student['teacher'],
            'sessions': len(student.get('sessions', [])),
            'attendance_rate': student.get('attendance_stats', {}).get('attendance_rate', 0)
        }
        summary_data['students'].append(student_summary)
    
    # Sort students by ID
    summary_data['students'].sort(key=lambda x: x['student_id'])
    
    # Write summary to JSON
    summary_path = os.path.join(output_dir, 'batches_16_18_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    # Generate markdown summary
    generate_markdown_summary(summary_data, output_dir)
    
    logger.info(f"Summary report written to {summary_path}")
    
    return summary_data

def generate_markdown_summary(summary_data: Dict, output_dir: str):
    """Generate markdown summary report"""
    
    report = []
    report.append("# Batches 16-18 Processing Summary")
    report.append(f"**Processing Date:** {datetime.fromisoformat(summary_data['processing_date']).strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Total Students:** {summary_data['total_students']}")
    report.append("")
    
    # Batch breakdown
    report.append("## Batch Breakdown")
    for batch in summary_data['batch_breakdown']:
        report.append(f"- **Batch {batch['batch_number']}:** {batch['student_count']} students")
        student_list = ", ".join(batch['students'])
        report.append(f"  - Students: {student_list}")
    report.append("")
    
    # Program distribution
    report.append("## Program Distribution")
    for program, count in sorted(summary_data['programs'].items()):
        report.append(f"- **{program}:** {count} students")
    report.append("")
    
    # Teacher distribution
    report.append("## Teacher Distribution") 
    for teacher, count in sorted(summary_data['teachers'].items()):
        report.append(f"- **{teacher}:** {count} students")
    report.append("")
    
    # Session statistics
    stats = summary_data['session_stats']
    report.append("## Session Statistics")
    report.append(f"- **Total Sessions:** {stats['total_sessions']}")
    report.append(f"- **Total Attended:** {stats['total_attended']}")
    report.append(f"- **Total Absent:** {stats['total_absent']}")
    report.append(f"- **Overall Attendance Rate:** {stats['overall_attendance_rate']}%")
    report.append("")
    
    # Data quality metrics
    metrics = summary_data['data_quality_metrics']
    report.append("## Data Quality Improvements")
    report.append(f"- **Teacher name fixes:** {metrics.get('teacher_name_fixes', 0)}")
    report.append(f"- **Progress standardizations:** {metrics.get('progress_standardizations', 0)}")
    report.append(f"- **URL extractions:** {metrics.get('url_extractions', 0)}")
    report.append(f"- **Missing data handled:** {metrics.get('missing_data_handled', 0)}")
    report.append(f"- **Invalid sessions fixed:** {metrics.get('invalid_sessions_fixed', 0)}")
    report.append("")
    
    # Student list
    report.append("## All Students")
    report.append("| Student ID | Name | Program | Teacher | Sessions | Attendance Rate |")
    report.append("|------------|------|---------|---------|----------|-----------------|")
    
    for student in summary_data['students']:
        report.append(f"| {student['student_id']} | {student['name']} | {student['program']} | {student['teacher']} | {student['sessions']} | {student['attendance_rate']}% |")
    
    report.append("")
    report.append("---")
    report.append(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Write markdown summary
    summary_md_path = os.path.join(output_dir, 'batches_16_18_summary.md')
    with open(summary_md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    logger.info(f"Markdown summary written to {summary_md_path}")

if __name__ == "__main__":
    summary = main()
    
    # Print final summary to console
    print("\n" + "="*60)
    print("BATCHES 16-18 PROCESSING COMPLETED")
    print("="*60)
    print(f"Total Students Processed: {summary['total_students']}")
    print(f"Overall Attendance Rate: {summary['session_stats']['overall_attendance_rate']}%")
    print(f"Data Quality Fixes Applied: {sum(summary['data_quality_metrics'].values())}")
    print("\nProgram Distribution:")
    for program, count in sorted(summary['programs'].items()):
        print(f"  {program}: {count} students")
    print("\nTeacher Distribution:")
    for teacher, count in sorted(summary['teachers'].items()):
        print(f"  {teacher}: {count} students")
    print("="*60)