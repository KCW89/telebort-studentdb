#!/usr/bin/env python3
"""
Transform existing batch JSON files to vertical CSV format for Google Sheets import
Uses the 18 batch files already processed from the horizontal format
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import re

def load_batch_data(batch_file):
    """Load and parse batch JSON file"""
    with open(batch_file, 'r') as f:
        data = json.load(f)
    
    students = []
    
    # Handle different batch formats
    if isinstance(data, dict):
        # Format 1: raw_data array (batch2, 5-18)
        if 'raw_data' in data and isinstance(data['raw_data'], list):
            for row in data['raw_data']:
                student = parse_horizontal_row(row)
                if student:
                    students.append(student)
        
        # Format 2: results->rows or results->raw_rows (batch1, 6, 7)
        elif 'results' in data and isinstance(data['results'], list):
            for result in data['results']:
                rows_data = result.get('rows') or result.get('raw_rows', [])
                if isinstance(rows_data, list):
                    for row in rows_data:
                        student = parse_horizontal_row(row)
                        if student:
                            students.append(student)
    
    # Format 3: Direct list (batch3, 4 - already processed format)
    elif isinstance(data, list):
        for item in data:
            if 'sessions' in item and 'student_id' in item:
                students.append(item)
    
    return students

def parse_horizontal_row(row):
    """Parse a single horizontal row into structured format"""
    if not row or len(row) < 6:
        return None
    
    # Detect format based on student ID location
    if len(row) > 1 and isinstance(row[1], str) and row[1].startswith('s') and len(row[1]) > 1 and row[1][1:].isdigit():
        # Format 2: StudentID in column 1
        student_data = {
            'name': row[0] if len(row) > 0 else '',
            'student_id': row[1] if len(row) > 1 else '',
            'program': row[2] if len(row) > 2 else '',
            'schedule_day': row[3] if len(row) > 3 else '',
            'start_time': row[4] if len(row) > 4 else '',
            'end_time': row[5] if len(row) > 5 else '',
            'teacher': row[6] if len(row) > 6 else '',
            'sessions': []
        }
        session_start = 7
    else:
        # Format 1: StudentID in column 2
        student_data = {
            'name': row[0] if len(row) > 0 else '',
            'student_id': row[2] if len(row) > 2 else '',
            'program': row[3] if len(row) > 3 else '',
            'schedule_day': row[4] if len(row) > 4 else '',
            'start_time': row[5] if len(row) > 5 else '',
            'end_time': row[6] if len(row) > 6 else '',
            'teacher': row[7] if len(row) > 7 else '',
            'sessions': []
        }
        session_start = 8
    
    # Skip if no valid student ID
    if not student_data['student_id'] or not student_data['student_id'].startswith('s'):
        return None
    
    # Parse sessions (5-column pattern)
    for i in range(session_start, len(row), 5):
        if i + 4 >= len(row):
            break
        
        date = row[i] if i < len(row) else ''
        session_num = row[i + 1] if i + 1 < len(row) else ''
        submission = row[i + 2] if i + 2 < len(row) else ''
        attendance = row[i + 3] if i + 3 < len(row) else ''
        lesson = row[i + 4] if i + 4 < len(row) else ''
        
        # Skip empty sessions
        if not date or date == '-':
            continue
        
        session = {
            'date': date,
            'session': session_num,
            'submission_link': submission,
            'attendance': attendance,
            'lesson': lesson
        }
        
        student_data['sessions'].append(session)
    
    return student_data

def transform_to_vertical(students_data):
    """Transform student data to vertical CSV format"""
    vertical_rows = []
    
    for student in students_data:
        student_id = student.get('student_id', '')
        student_name = student.get('name', '')
        program = student.get('program', '')
        schedule_day = student.get('schedule_day', '') or student.get('day', '')
        start_time = student.get('start_time', '')
        end_time = student.get('end_time', '')
        primary_teacher = student.get('teacher', '') or student.get('primary_teacher', '')
        
        # Process each session
        for session in student.get('sessions', []):
            # Parse date
            date_str = session.get('date', '')
            date_parsed = parse_date(date_str)
            
            # Parse attendance
            attendance = parse_attendance(session.get('attendance', ''))
            
            # Extract teacher from attendance if it's a name
            session_teacher = ''
            teacher_names = ["Soumiya", "Han Yang", "Khairina", "Arrvinna", "Syahin",
                           "Hafiz", "Yasmin", "Nurafrina", "Rahmat", "Fatin",
                           "Aisyah", "Puvin", "Afiqah", "Aaron", "Farah"]
            
            att_value = session.get('attendance', '')
            if att_value in teacher_names:
                session_teacher = att_value
                attendance = "Attended"
            else:
                session_teacher = session.get('teacher', '') or primary_teacher
            
            # Parse lesson
            lesson_text = session.get('lesson', '')
            lesson_title = parse_lesson(lesson_text)
            
            # Parse progress
            progress = parse_progress(session.get('progress', ''))
            
            # Extract links
            links = extract_links(lesson_text)
            if session.get('submission_link'):
                sub_links = extract_links(session.get('submission_link', ''))
                if sub_links:
                    links = f"{links} | {sub_links}" if links else sub_links
            
            vertical_row = {
                'Student_ID': student_id,
                'Student_Name': student_name,
                'Program': program,
                'Session_Date': date_parsed,
                'Session_Number': session.get('session', ''),
                'Attendance': attendance,
                'Session_Teacher': session_teacher,
                'Lesson_Topic': lesson_title,
                'Progress': progress,
                'Schedule_Day': schedule_day,
                'Schedule_Time': f"{start_time}-{end_time}" if start_time and end_time else "",
                'Primary_Teacher': primary_teacher,
                'Lesson_Links': links,
                'Raw_Data': lesson_text
            }
            
            vertical_rows.append(vertical_row)
    
    return vertical_rows

def parse_date(date_str):
    """Parse date string to ISO format"""
    if not date_str or date_str == '-':
        return ''
    
    # Skip non-date values
    if any(x in date_str.lower() for x in ['teacher', 'parent', 'holiday', 'no class']):
        return ''
    
    # Try different formats
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%y']
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except:
            continue
    
    return ''

def parse_attendance(att_str):
    """Normalize attendance status"""
    if not att_str:
        return 'Not Marked'
    
    att_lower = att_str.lower().strip()
    
    if 'attended' in att_lower:
        return 'Attended'
    elif 'absent' in att_lower:
        return 'Absent'
    elif 'no class' in att_lower:
        return 'No Class'
    elif 'holiday' in att_lower:
        return 'Public Holiday'
    elif 'break' in att_lower:
        return 'In Break'
    elif 'teacher parent' in att_lower:
        return 'Teacher Parent Day'
    elif att_str == '-':
        return 'Not Marked'
    
    # Check if it's a teacher name
    teacher_names = ["soumiya", "han yang", "khairina", "arrvinna", "syahin",
                    "hafiz", "yasmin", "nurafrina", "rahmat", "fatin",
                    "aisyah", "puvin", "afiqah", "aaron", "farah"]
    if att_lower in teacher_names:
        return 'Attended'
    
    return att_str

def parse_lesson(lesson_str):
    """Extract clean lesson title"""
    if not lesson_str or lesson_str == '-':
        return ''
    
    # Remove URLs
    lesson_clean = re.sub(r'https?://\S+', '', lesson_str)
    
    # Remove status markers
    lesson_clean = re.sub(r'\b(COMPLETED|IN PROGRESS|NOT STARTED|DOING)\b', '', lesson_clean, flags=re.IGNORECASE)
    
    # Clean whitespace
    lesson_clean = re.sub(r'\s+', ' ', lesson_clean)
    lesson_clean = lesson_clean.strip()
    
    return lesson_clean

def parse_progress(progress_str):
    """Parse progress status"""
    if not progress_str or progress_str == '-':
        return 'Not Started'
    
    prog_lower = progress_str.lower()
    
    if 'completed' in prog_lower:
        return 'Completed'
    elif 'in progress' in prog_lower or 'in_progress' in prog_lower:
        return 'In Progress'
    elif 'graduated' in prog_lower:
        return 'Graduated'
    elif 'not started' in prog_lower:
        return 'Not Started'
    
    return progress_str

def extract_links(text):
    """Extract URLs from text"""
    if not text:
        return ''
    
    urls = re.findall(r'https?://\S+', text)
    return ' | '.join(urls) if urls else ''

def save_to_csv(vertical_data, output_file):
    """Save vertical data to CSV"""
    if not vertical_data:
        print("No data to save")
        return
    
    # Sort by student ID and date
    vertical_data.sort(key=lambda x: (x['Student_ID'], x['Session_Date']))
    
    # Define columns
    columns = [
        'Student_ID',
        'Student_Name',
        'Program',
        'Session_Date',
        'Session_Number',
        'Attendance',
        'Session_Teacher',
        'Lesson_Topic',
        'Progress',
        'Schedule_Day',
        'Schedule_Time',
        'Primary_Teacher',
        'Lesson_Links'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(vertical_data)
    
    print(f"✅ Saved {len(vertical_data)} session records to {output_file}")

def main():
    """Process all batch files to vertical CSV"""
    
    print("🔄 Converting batch files to vertical CSV format...")
    print("=" * 60)
    
    # Get all batch files
    batch_dir = Path("data/raw/batches")
    batch_files = sorted(batch_dir.glob("batch*_complete.json"))
    
    if not batch_files:
        print("❌ No batch files found in data/raw/batches/")
        return
    
    print(f"📁 Found {len(batch_files)} batch files")
    
    # Process all batches
    all_vertical_data = []
    student_count = 0
    
    for batch_file in batch_files:
        print(f"\n  Processing {batch_file.name}...", end=" ")
        students = load_batch_data(batch_file)
        
        if students:
            student_count += len(students)
            vertical_data = transform_to_vertical(students)
            all_vertical_data.extend(vertical_data)
            print(f"✓ {len(students)} students, {len(vertical_data)} sessions")
        else:
            print("✗ No data")
    
    # Create output directory
    output_dir = Path("data/vertical_csv")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"telebort_all_sessions_vertical_{timestamp}.csv"
    save_to_csv(all_vertical_data, output_file)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"  Total students processed: {student_count}")
    print(f"  Total session records: {len(all_vertical_data)}")
    
    # Count unique students
    unique_students = set(row['Student_ID'] for row in all_vertical_data if row['Student_ID'])
    print(f"  Unique student IDs: {len(unique_students)}")
    
    # Attendance breakdown
    attendance_counts = {}
    for row in all_vertical_data:
        status = row['Attendance']
        attendance_counts[status] = attendance_counts.get(status, 0) + 1
    
    print(f"\n  Attendance breakdown:")
    for status, count in sorted(attendance_counts.items()):
        percentage = (count / len(all_vertical_data) * 100) if all_vertical_data else 0
        print(f"    {status:<20} {count:>5} ({percentage:.1f}%)")
    
    # Progress breakdown
    progress_counts = {}
    for row in all_vertical_data:
        status = row['Progress']
        progress_counts[status] = progress_counts.get(status, 0) + 1
    
    print(f"\n  Progress breakdown:")
    for status, count in sorted(progress_counts.items()):
        percentage = (count / len(all_vertical_data) * 100) if all_vertical_data else 0
        print(f"    {status:<20} {count:>5} ({percentage:.1f}%)")
    
    print("\n" + "=" * 60)
    print(f"✨ Output file: {output_file}")
    print("\n📌 This CSV is ready to import into Google Sheets!")
    print("   1. Open Google Sheets")
    print("   2. File > Import > Upload")
    print("   3. Select this CSV file")
    print("   4. Choose 'Replace spreadsheet' or 'Insert new sheet'")

if __name__ == "__main__":
    main()