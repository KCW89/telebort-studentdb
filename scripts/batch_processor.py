#\!/usr/bin/env python3
"""
Batch processor for complete student data
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enhanced_data_processor import EnhancedDataProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_batch_data(batch_data) -> List[Dict]:
    """Parse student data from batch JSON"""
    students = []
    
    # Handle list format (batches 3, 4)
    if isinstance(batch_data, list):
        for student_data in batch_data:
            student = {
                'name': student_data.get('name', ''),
                'student_id': student_data.get('student_id', ''),
                'program': student_data.get('program', ''),
                'teacher': student_data.get('teacher', ''),
                'sessions': student_data.get('sessions', [])
            }
            
            if student['student_id']:
                students.append(student)
        return students
    
    # Handle raw_data format
    if 'raw_data' in batch_data:
        for row in batch_data['raw_data']:
            if not row or len(row) < 7:
                continue
                
            student = {
                'name': row[0],
                'student_id': row[1],
                'program': row[2] if len(row) > 2 else '',
                'teacher': row[6] if len(row) > 6 else '',
                'sessions': []
            }
            
            # Parse sessions (every 5 columns starting from index 7)
            for i in range(7, len(row), 5):
                if i + 4 >= len(row):
                    break
                    
                date = row[i]
                session = row[i+1] if i+1 < len(row) else ''
                lesson = row[i+2] if i+2 < len(row) else ''
                attendance = row[i+3] if i+3 < len(row) else ''
                progress = row[i+4] if i+4 < len(row) else ''
                
                if date and date != '-':
                    student['sessions'].append({
                        'date': date,
                        'session': session,
                        'lesson': lesson,
                        'attendance': attendance,
                        'progress': progress
                    })
            
            if student['student_id'] and student['student_id'] != '-':
                students.append(student)
    
    # Handle results format (batches 1, 8-18)
    elif 'results' in batch_data:
        results = batch_data['results']
        if results and len(results) > 0:
            # Try raw_rows first, then rows
            rows = results[0].get('raw_rows', results[0].get('rows', []))
            
            for row in rows:
                if not row or len(row) < 7:
                    continue
                    
                # Check if student_id is at index 1 or 2
                student_id = row[1] if row[1] and row[1] != '' else row[2] if len(row) > 2 else ''
                
                student = {
                    'name': row[0],
                    'student_id': student_id,
                    'program': row[3] if len(row) > 3 else row[2] if len(row) > 2 else '',
                    'teacher': row[7] if len(row) > 7 else row[6] if len(row) > 6 else '',
                    'sessions': []
                }
                
                for i in range(7, len(row), 5):
                    if i + 4 >= len(row):
                        break
                        
                    date = row[i]
                    session = row[i+1] if i+1 < len(row) else ''
                    lesson = row[i+2] if i+2 < len(row) else ''
                    attendance = row[i+3] if i+3 < len(row) else ''
                    progress = row[i+4] if i+4 < len(row) else ''
                    
                    if date and date != '-':
                        student['sessions'].append({
                            'date': date,
                            'session': session,
                            'lesson': lesson,
                            'attendance': attendance,
                            'progress': progress
                        })
                
                if student['student_id'] and student['student_id'] != '-':
                    students.append(student)
    
    return students

def generate_report(student: Dict) -> str:
    """Generate markdown report for a student"""
    report = []
    
    report.append(f"# Student Attendance & Progress Report")
    report.append(f"\n**Student ID:** {student['student_id']}")
    report.append(f"**Name:** {student['name']}")
    report.append(f"**Program:** {student.get('program', 'N/A')}")
    report.append(f"**Primary Teacher:** {student.get('teacher', 'Various')}")
    
    sessions = student.get('sessions', [])
    total_sessions = len(sessions)
    attended = sum(1 for s in sessions if s.get('attendance') in ['Attended', 'Completed', 'In Progress'])
    
    report.append(f"\n## Summary Statistics")
    report.append(f"- **Total Sessions:** {total_sessions}")
    report.append(f"- **Sessions Attended:** {attended}")
    
    if total_sessions > 0:
        attendance_rate = (attended / total_sessions) * 100
        report.append(f"- **Attendance Rate:** {attendance_rate:.1f}%")
    
    if sessions:
        dates = [s['date'] for s in sessions if s.get('date') and s['date'] != '-']
        if dates:
            report.append(f"- **Date Range:** {dates[-1]} to {dates[0]}")
    
    report.append(f"\n## Detailed Session Log")
    report.append(f"\n| Session | Date | Attendance | Lesson/Topic | Progress |")
    report.append(f"|---------|------|------------|--------------|----------|")
    
    for session in sessions:
        session_num = session.get('session', '-')
        date = session.get('date', '-')
        attendance = session.get('attendance', '-')
        lesson = session.get('lesson', '-')[:50]
        progress = session.get('progress', '-')
        
        if lesson and lesson != '-':
            lesson = lesson.replace('\n', ' ').replace('\r', ' ')
            if len(lesson) > 50:
                lesson = lesson[:47] + "..."
        
        report.append(f"| {session_num} | {date} | {attendance} | {lesson} | {progress} |")
    
    report.append(f"\n---")
    report.append(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    return '\n'.join(report)

def process_batch_file(batch_file: str) -> Optional[Dict]:
    """Process a single batch file"""
    try:
        batch_path = Path(batch_file)
        
        if not batch_path.exists():
            batch_path = Path("/Users/chongwei/Telebort Engineering/telebort-studentdb") / batch_file
        
        if not batch_path.exists():
            logging.error(f"Batch file not found: {batch_file}")
            return None
        
        logging.info(f"Processing {batch_file}...")
        
        with open(batch_path, 'r') as f:
            batch_data = json.load(f)
        
        students = parse_batch_data(batch_data)
        
        if not students:
            logging.warning(f"No students found in {batch_file}")
            return None
        
        logging.info(f"Parsed {len(students)} students from {batch_file}")
        
        processor = EnhancedDataProcessor()
        cleaned_students, metrics = processor.process_student_data(students)
        
        # Use cleaned students for reports
        students = cleaned_students
        total_sessions = sum(len(s['sessions']) for s in students)
        
        reports_dir = Path("/Users/chongwei/Telebort Engineering/telebort-studentdb/reports")
        reports_dir.mkdir(exist_ok=True)
        
        reports_generated = 0
        for student in students:
            try:
                report_content = generate_report(student)
                report_path = reports_dir / f"{student['student_id']}.md"
                
                with open(report_path, 'w') as f:
                    f.write(report_content)
                
                reports_generated += 1
                
            except Exception as e:
                logging.error(f"Error generating report for {student['student_id']}: {e}")
        
        return {
            'students_processed': len(students),
            'total_sessions': total_sessions,
            'reports_generated': reports_generated,
            'data_quality_improvements': sum(metrics.values())
        }
        
    except Exception as e:
        logging.error(f"Error processing {batch_file}: {e}")
        return None

def main():
    """Process all batch files"""
    batch_files = [
        "batch1_complete.json", "batch2_complete.json", "batch3_complete.json",
        "batch4_complete.json", "batch5_complete.json", "batch6_complete.json",
        "batch7_complete.json", "batch8_complete.json", "batch9_complete.json",
        "batch10_complete.json", "batch11_complete.json", "batch12_complete.json",
        "batch13_complete.json", "batch14_complete.json", "batch15_complete.json",
        "batch16_complete.json", "batch17_complete.json", "batch18_complete.json"
    ]
    
    print("=" * 70)
    print("BATCH PROCESSING - COMPLETE STUDENT DATA")
    print("=" * 70)
    
    total_students = 0
    total_sessions = 0
    total_reports = 0
    processed_batches = []
    failed_batches = []
    
    for batch_file in batch_files:
        result = process_batch_file(batch_file)
        
        if result:
            total_students += result['students_processed']
            total_sessions += result['total_sessions']
            total_reports += result['reports_generated']
            processed_batches.append(batch_file)
            
            print(f"✅ {batch_file}: {result['students_processed']} students, {result['reports_generated']} reports")
        else:
            failed_batches.append(batch_file)
            print(f"❌ {batch_file}: Failed to process")
    
    print("\n" + "=" * 70)
    print("PROCESSING SUMMARY")
    print("=" * 70)
    print(f"\n📊 Results:")
    print(f"   • Batches processed: {len(processed_batches)}/{len(batch_files)}")
    print(f"   • Students processed: {total_students}")
    print(f"   • Total sessions: {total_sessions}")
    print(f"   • Reports generated: {total_reports}")
    
    if total_students > 0:
        print(f"   • Average sessions/student: {total_sessions/total_students:.1f}")
    
    if failed_batches:
        print(f"\n⚠️  Failed batches:")
        for batch in failed_batches:
            print(f"   • {batch}")
    else:
        print(f"\n✅ All batches processed successfully!")
    
    return 0 if not failed_batches else 1

if __name__ == "__main__":
    exit(main())