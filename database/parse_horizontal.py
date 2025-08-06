#!/usr/bin/env python3
"""
Parse horizontal batch data from 338 columns to structured format
This handles the raw Google Sheets export format
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


def parse_horizontal_row(row: List) -> Dict:
    """
    Parse a single horizontal row (338 columns) into structured format
    
    Row structure:
    0-6: Student metadata (Name, Status, ID, Program, Day, Start, End, Teacher)
    7+: Sessions in 5-column pattern (Date, Session#, Submission, Attendance, Lesson, Teacher, Progress)
    """
    
    if not row or len(row) < 7:
        return None
    
    # Extract student info from first 7 columns
    student_info = {
        'name': row[0] if len(row) > 0 else '',
        'status': row[1] if len(row) > 1 else '',
        'student_id': row[2] if len(row) > 2 else '',
        'program': row[3] if len(row) > 3 else '',
        'schedule_day': row[4] if len(row) > 4 else '',
        'start_time': row[5] if len(row) > 5 else '',
        'end_time': row[6] if len(row) > 6 else '',
        'teacher': row[7] if len(row) > 7 else ''
    }
    
    # Parse sessions from remaining columns (5-column pattern)
    sessions = []
    
    # Start from column 8, process in chunks of 5
    for i in range(8, len(row), 5):
        if i + 4 >= len(row):
            break  # Not enough columns for a complete session
        
        # Extract session data
        date_str = row[i] if row[i] else ''
        session_num = row[i + 1] if i + 1 < len(row) else ''
        submission = row[i + 2] if i + 2 < len(row) else ''
        attendance = row[i + 3] if i + 3 < len(row) else ''
        lesson = row[i + 4] if i + 4 < len(row) else ''
        
        # Skip empty sessions
        if not date_str or date_str == '-':
            continue
        
        # Determine teacher and progress from the pattern
        teacher_name = ''
        progress = 'Not Started'
        
        # Sometimes teacher and progress are in the submission/lesson fields
        if i + 5 < len(row) and row[i + 5]:
            # Could be teacher name
            potential_teacher = row[i + 5]
            teacher_names = ['Soumiya', 'Han Yang', 'Khairina', 'Arrvinna', 'Syahin', 
                           'Hafiz', 'Yasmin', 'Nurafrina', 'Rahmat', 'Fatin', 
                           'Aisyah', 'Puvin', 'Afiqah', 'Aaron', 'Farah']
            if potential_teacher in teacher_names:
                teacher_name = potential_teacher
        
        if i + 6 < len(row) and row[i + 6]:
            # Progress status
            progress = row[i + 6]
        
        # Create session object
        session = {
            'date': date_str,
            'session': session_num,
            'submission_link': submission if submission and submission != '-' else '',
            'attendance': attendance if attendance else 'Not Marked',
            'lesson': lesson if lesson else '',
            'teacher': teacher_name,
            'progress': progress
        }
        
        sessions.append(session)
    
    return {
        'student_id': student_info['student_id'],
        'name': student_info['name'],
        'status': student_info['status'],
        'program': student_info['program'],
        'schedule_day': student_info['schedule_day'],
        'start_time': student_info['start_time'],
        'end_time': student_info['end_time'],
        'teacher': student_info['teacher'],
        'sessions': sessions
    }


def parse_batch1_format(batch_file: str) -> List[Dict]:
    """Parse batch1 specific format"""
    
    with open(batch_file, 'r') as f:
        data = json.load(f)
    
    students = []
    
    # Navigate the nested structure
    if 'results' in data and isinstance(data['results'], list):
        for result in data['results']:
            if 'rows' in result and isinstance(result['rows'], list):
                for row in result['rows']:
                    student_data = parse_horizontal_row(row)
                    if student_data and student_data['student_id']:
                        students.append(student_data)
    
    return students


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parse_horizontal.py <batch_file.json>")
        sys.exit(1)
    
    batch_file = sys.argv[1]
    students = parse_batch1_format(batch_file)
    
    print(f"Parsed {len(students)} students from {batch_file}")
    
    for student in students:
        print(f"\nStudent: {student['name']} ({student['student_id']})")
        print(f"  Program: {student['program']}")
        print(f"  Sessions: {len(student['sessions'])}")
        
        if student['sessions']:
            print(f"  First session: {student['sessions'][0]['date']}")
            print(f"  Last session: {student['sessions'][-1]['date']}")