#!/usr/bin/env python3
"""
Enhanced data enrichment using master index AND inference rules
Fills missing lesson topics using sequential patterns and attendance data
"""

import csv
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

def load_master_index(file_path):
    """Load course master index into memory"""
    master_index = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            course_code = row['Course_Code']
            if course_code not in master_index:
                master_index[course_code] = []
            master_index[course_code].append(row)
    
    # Sort lessons by ID for each course
    for course_code in master_index:
        master_index[course_code].sort(key=lambda x: (x['Content_Type'], int(x['Content_ID']) if x['Content_ID'].isdigit() else 999))
    
    return master_index

def load_vertical_data(file_path):
    """Load and sort vertical CSV data by student and date"""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # Sort by student ID and date for sequential processing
    data.sort(key=lambda x: (x['Student_ID'], x['Session_Date']))
    
    return data

def map_program_to_course(program):
    """Enhanced program to course mapping"""
    mappings = {
        # AI Programs
        'G (AI-2)': 'AI-2',
        'F (AI-1)': 'AI-1',
        'AI-2': 'AI-2',
        'AI-1': 'AI-1',
        'AI-3': 'AI-2',  # AI-3 uses AI-2 curriculum
        
        # Web Development
        'D (W-2)': 'Web-2',
        'C (W-1)': 'Web-1',
        'E (W-3)': 'Web-3',
        
        # Block-Based Programming
        'BBP': 'BBP',
        'BBW': 'BBW',
        
        # Foundation/Design
        'A (FD-1)': 'Foundation 1',
        'B (FD-2)': 'Foundation 2',
        'H (BBD)': 'BBD',
        
        # Junior Coding
        'JC': 'JC'
    }
    
    return mappings.get(program, None)

def normalize_attendance(attendance):
    """Normalize attendance values including teacher names"""
    if not attendance:
        return 'Not Marked', None
    
    attendance = attendance.strip()
    
    # Teacher names that indicate attendance
    teacher_names = ["Soumiya", "Han Yang", "Khairina", "Arrvinna", "Syahin",
                    "Hafiz", "Yasmin", "Nurafrina", "Rahmat", "Fatin",
                    "Aisyah", "Puvin", "Afiqah", "Aaron", "Farah",
                    "Amirul", "Anisha", "Fatiha", "Choy Yein", "Hong Yi",
                    "Mardhiah", "Theyvii", "Yong Sheng"]
    
    # Check if attendance is a teacher name
    for teacher in teacher_names:
        if teacher.lower() in attendance.lower():
            return 'Attended', teacher
    
    # Standard attendance values
    att_lower = attendance.lower()
    if 'attended' in att_lower:
        return 'Attended', None
    elif 'absent' in att_lower:
        return 'Absent', None
    elif 'no class' in att_lower:
        return 'No Class', None
    elif 'holiday' in att_lower:
        return 'Public Holiday', None
    elif 'break' in att_lower:
        return 'In Break', None
    elif 'off' in att_lower:
        return 'Off', None
    
    return attendance, None

def infer_lesson_from_sequence(student_id, session_date, student_sessions, course_lessons):
    """Infer lesson based on sequential patterns"""
    if not course_lessons:
        return None
    
    # Get student's session history
    sessions = student_sessions.get(student_id, [])
    if not sessions:
        return None
    
    # Find current session index
    current_idx = None
    for i, sess in enumerate(sessions):
        if sess['date'] == session_date:
            current_idx = i
            break
    
    if current_idx is None:
        return None
    
    # Count attended sessions before this one
    attended_count = 0
    for i in range(current_idx):
        sess = sessions[i]
        if sess['attendance_norm'] == 'Attended':
            attended_count += 1
    
    # This would be the next lesson number (1-indexed)
    expected_lesson_num = attended_count + 1
    
    # Find matching lesson in course
    for lesson in course_lessons:
        if lesson['Content_Type'] == 'Lesson' and lesson['Content_ID'] == str(expected_lesson_num):
            return lesson
    
    # Try to find by sequence even if numbers don't match
    lesson_type_lessons = [l for l in course_lessons if l['Content_Type'] == 'Lesson']
    if 0 <= attended_count < len(lesson_type_lessons):
        return lesson_type_lessons[attended_count]
    
    return None

def extract_lesson_info(text):
    """Extract lesson number and type from text"""
    if not text or text == '-' or text == '_':
        return None, None, None
    
    text = text.strip()
    
    # Pattern matching
    patterns = [
        (r'L(\d+)\s*[:]\s*(.*)', 'Lesson'),
        (r'S(\d+)\s+L(\d+)', 'Lesson'),  # S1 L1 format
        (r'Lesson\s*(\d+)', 'Lesson'),
        (r'concept\s*(\d+)', 'Lesson'),
        (r'Project\s*(\d+)', 'Project'),
        (r'P(\d+)', 'Project'),
        (r'Quiz\s*(\d+)', 'Quiz'),
        (r'Exercise\s*(\d+)', 'Activity')
    ]
    
    for pattern, content_type in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Handle S1 L1 format
            if 'S' in pattern and len(match.groups()) > 1:
                lesson_num = match.group(2)
            else:
                lesson_num = match.group(1)
            rest = match.groups()[-1] if len(match.groups()) > 1 else ""
            return lesson_num, content_type, rest
    
    # Check for keywords
    text_lower = text.lower()
    if 'quiz' in text_lower:
        match = re.search(r'(\d+)', text)
        num = match.group(1) if match else None
        return num, 'Quiz', text
    elif 'project' in text_lower:
        match = re.search(r'(\d+)', text)
        num = match.group(1) if match else None
        return num, 'Project', text
    elif 'final' in text_lower:
        return '5', 'Project', text
    
    return None, None, text

def find_best_match(lesson_num, content_type, additional_text, course_lessons, strict=False):
    """Find best matching lesson from master index"""
    if not course_lessons:
        return None
    
    # Try exact match first
    if lesson_num and content_type:
        for lesson in course_lessons:
            if (lesson['Content_ID'] == lesson_num and 
                lesson['Content_Type'] == content_type):
                return lesson
    
    # If not strict, try fuzzy matching
    if not strict and additional_text:
        best_match = None
        best_score = 0
        
        additional_lower = additional_text.lower()
        for lesson in course_lessons:
            title_lower = lesson['Title'].lower()
            
            # Calculate similarity
            key_terms = re.findall(r'\b\w+\b', additional_lower)
            matches = sum(1 for term in key_terms if term in title_lower)
            
            if matches > best_score:
                best_score = matches
                best_match = lesson
        
        if best_score > 0:
            return best_match
    
    # Fallback to lesson number only
    if lesson_num:
        for lesson in course_lessons:
            if lesson['Content_ID'] == lesson_num:
                return lesson
    
    return None

def process_student_sessions(data, master_index):
    """Process all sessions with intelligent enhancement"""
    
    # First pass: Group sessions by student
    student_sessions = defaultdict(list)
    for row in data:
        att_norm, teacher = normalize_attendance(row['Attendance'])
        student_sessions[row['Student_ID']].append({
            'date': row['Session_Date'],
            'attendance': row['Attendance'],
            'attendance_norm': att_norm,
            'teacher': teacher,
            'topic': row['Lesson_Topic'],
            'progress': row['Progress'],
            'row_index': data.index(row)
        })
    
    # Sort each student's sessions by date
    for student_id in student_sessions:
        student_sessions[student_id].sort(key=lambda x: x['date'])
    
    # Second pass: Enhance each session
    enhanced_data = []
    stats = {
        'total': len(data),
        'enhanced_direct': 0,
        'enhanced_inferred': 0,
        'original': 0
    }
    
    for row_idx, row in enumerate(data):
        enhanced = row.copy()
        
        # Get course mapping
        program = row.get('Program', '')
        course_code = map_program_to_course(program)
        enhanced['Course_Code'] = course_code or ''
        
        # Normalize attendance
        att_norm, teacher = normalize_attendance(row['Attendance'])
        enhanced['Attendance_Normalized'] = att_norm
        if teacher:
            enhanced['Session_Teacher'] = teacher
        
        # Try to enhance with master index
        matched_lesson = None
        enhancement_type = 'Original'
        
        if course_code and course_code in master_index:
            course_lessons = master_index[course_code]
            
            # First try: Direct match from existing topic
            if row['Lesson_Topic'] and row['Lesson_Topic'] not in ['-', '_', '']:
                lesson_num, content_type, additional = extract_lesson_info(row['Lesson_Topic'])
                matched_lesson = find_best_match(lesson_num, content_type, additional, course_lessons)
                if matched_lesson:
                    enhancement_type = 'Enhanced_Direct'
                    stats['enhanced_direct'] += 1
            
            # Second try: Infer from sequence if attended
            if not matched_lesson and att_norm == 'Attended':
                matched_lesson = infer_lesson_from_sequence(
                    row['Student_ID'], 
                    row['Session_Date'],
                    student_sessions,
                    course_lessons
                )
                if matched_lesson:
                    enhancement_type = 'Enhanced_Inferred'
                    stats['enhanced_inferred'] += 1
        
        # Apply enhancement
        if matched_lesson:
            enhanced['Lesson_ID'] = matched_lesson['Content_ID']
            enhanced['Lesson_Type'] = matched_lesson['Content_Type']
            enhanced['Lesson_Topic_Standard'] = matched_lesson['Title']
            enhanced['Lesson_Topic_Original'] = row['Lesson_Topic']
            enhanced['Duration_Min'] = matched_lesson.get('Duration_Min', '')
            
            # Add links
            if matched_lesson.get('Exit_Ticket_Link'):
                enhanced['Exit_Ticket_Link'] = matched_lesson['Exit_Ticket_Link']
            if matched_lesson.get('Quiz_Link'):
                enhanced['Quiz_Link'] = matched_lesson['Quiz_Link']
            if matched_lesson.get('Submission_Link'):
                enhanced['Submission_Link'] = matched_lesson['Submission_Link']
        else:
            enhanced['Lesson_Topic_Standard'] = row['Lesson_Topic']
            enhanced['Lesson_Topic_Original'] = row['Lesson_Topic']
            stats['original'] += 1
        
        enhanced['Data_Enhancement'] = enhancement_type
        
        # Infer progress if missing
        if not enhanced.get('Progress') or enhanced['Progress'] == 'Not Started':
            if att_norm == 'Attended' and matched_lesson:
                enhanced['Progress_Inferred'] = 'In Progress'
            else:
                enhanced['Progress_Inferred'] = enhanced.get('Progress', 'Not Started')
        else:
            enhanced['Progress_Inferred'] = enhanced['Progress']
        
        enhanced_data.append(enhanced)
        
        # Progress indicator
        if (row_idx + 1) % 500 == 0:
            print(f"  Processed {row_idx + 1}/{len(data)} sessions...")
    
    return enhanced_data, stats

def save_enhanced_csv(enhanced_data, output_file):
    """Save enhanced data to CSV"""
    if not enhanced_data:
        return
    
    # Define column order
    columns = [
        'Student_ID',
        'Student_Name',
        'Program',
        'Course_Code',
        'Session_Date',
        'Session_Number',
        'Lesson_ID',
        'Lesson_Type',
        'Lesson_Topic_Standard',
        'Lesson_Topic_Original',
        'Attendance',
        'Attendance_Normalized',
        'Progress',
        'Progress_Inferred',
        'Session_Teacher',
        'Duration_Min',
        'Schedule_Day',
        'Schedule_Time',
        'Primary_Teacher',
        'Lesson_Links',
        'Exit_Ticket_Link',
        'Quiz_Link',
        'Submission_Link',
        'Data_Enhancement'
    ]
    
    # Only include columns that exist
    available_columns = [col for col in columns if col in enhanced_data[0]]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=available_columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(enhanced_data)

def main():
    """Main processing function"""
    print("🚀 ENHANCED DATA ENRICHMENT WITH INFERENCE")
    print("=" * 60)
    
    # File paths
    master_index_file = Path("data/vertical_csv/course-master-index.csv")
    vertical_csv_file = Path("data/vertical_csv/telebort_all_sessions_vertical_20250806_232159.csv")
    
    # Load data
    print("📚 Loading master index...")
    master_index = load_master_index(master_index_file)
    print(f"  Loaded {len(master_index)} courses")
    
    print("\n📁 Loading session data...")
    data = load_vertical_data(vertical_csv_file)
    print(f"  Loaded {len(data)} sessions")
    
    # Process with enhancements
    print("\n🔄 Processing sessions with inference...")
    enhanced_data, stats = process_student_sessions(data, master_index)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("data/vertical_csv") / f"telebort_sessions_final_{timestamp}.csv"
    save_enhanced_csv(enhanced_data, output_file)
    
    # Print statistics
    print("\n" + "=" * 60)
    print("📊 ENHANCEMENT STATISTICS")
    print("=" * 60)
    print(f"Total sessions:      {stats['total']}")
    print(f"Enhanced (direct):   {stats['enhanced_direct']} ({stats['enhanced_direct']/stats['total']*100:.1f}%)")
    print(f"Enhanced (inferred): {stats['enhanced_inferred']} ({stats['enhanced_inferred']/stats['total']*100:.1f}%)")
    print(f"Original:            {stats['original']} ({stats['original']/stats['total']*100:.1f}%)")
    print(f"TOTAL ENHANCED:      {stats['enhanced_direct'] + stats['enhanced_inferred']} ({(stats['enhanced_direct'] + stats['enhanced_inferred'])/stats['total']*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print("✨ Enhancement complete!")
    print(f"📁 Output file: {output_file}")
    print("\n🎯 Improvements made:")
    print("  ✓ Normalized attendance (teacher names → 'Attended')")
    print("  ✓ Inferred lessons for attended sessions")
    print("  ✓ Standardized lesson topics from master index")
    print("  ✓ Added course codes and lesson IDs")
    print("  ✓ Included assessment links")
    print("  ✓ Inferred progress for attended sessions")

if __name__ == "__main__":
    main()