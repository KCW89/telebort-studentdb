#!/usr/bin/env python3
"""
Enhance vertical CSV data using course master index
Fills missing lesson topics and standardizes existing ones
"""

import csv
import re
from datetime import datetime
from pathlib import Path
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
    
    print(f"📚 Loaded master index with {len(master_index)} courses")
    for code, lessons in master_index.items():
        print(f"  - {code}: {len(lessons)} items")
    
    return master_index

def load_vertical_data(file_path):
    """Load vertical CSV data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    print(f"\n📁 Loaded {len(data)} session records")
    return data

def map_program_to_course(program):
    """Map program codes to course codes"""
    # Mapping based on program patterns
    mappings = {
        # AI Programs
        'G (AI-2)': 'AI-2',
        'F (AI-1)': 'AI-1',
        'AI-2': 'AI-2',
        'AI-1': 'AI-1',
        'AI-3': 'AI-2',  # Assuming AI-3 follows AI-2 curriculum
        
        # Web Development
        'D (W-2)': 'W-2',
        'C (W-1)': 'W-1',
        'E (W-3)': 'W-3',
        
        # Block-Based Programming
        'BBP': 'BBP',
        'BBW': 'BBW',
        
        # Foundation/Design
        'A (FD-1)': 'FD-1',
        'B (FD-2)': 'FD-2',
        'H (BBD)': 'BBD',
        
        # Junior Coding
        'JC': 'JC'
    }
    
    return mappings.get(program, None)

def extract_lesson_info(text):
    """Extract lesson number and type from text"""
    if not text or text == '-':
        return None, None, None
    
    # Clean text
    text = text.strip()
    
    # Pattern matching for lesson numbers
    patterns = [
        (r'L(\d+)\s*[:]\s*(.*)', 'Lesson'),
        (r'Lesson\s*(\d+)\s*[:]\s*(.*)', 'Lesson'),
        (r'concept\s*(\d+)\s*(.*)', 'Lesson'),
        (r'Project\s*(\d+)\s*[:]\s*(.*)', 'Project'),
        (r'P(\d+)\s*[:]\s*(.*)', 'Project'),
        (r'Quiz\s*(\d+)', 'Quiz'),
        (r'Exercise\s*(\d+)\s*[:]\s*(.*)', 'Activity'),
        (r'Activity\s*(\d+)\s*[:]\s*(.*)', 'Activity')
    ]
    
    for pattern, content_type in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            lesson_num = match.group(1)
            rest = match.group(2) if len(match.groups()) > 1 else ""
            return lesson_num, content_type, rest
    
    # Check for quiz without number
    if 'quiz' in text.lower():
        # Try to extract quiz number
        match = re.search(r'quiz\s*[-]?\s*(\d+)', text, re.IGNORECASE)
        if match:
            return match.group(1), 'Quiz', ''
        return None, 'Quiz', text
    
    # Check for project without clear number
    if 'project' in text.lower():
        return None, 'Project', text
    
    # Check for final project
    if 'final' in text.lower() and 'project' in text.lower():
        return '5', 'Project', text  # Final projects are usually Project 5
    
    return None, None, text

def find_best_match(lesson_num, content_type, additional_text, course_lessons):
    """Find best matching lesson from master index"""
    if not course_lessons:
        return None
    
    best_match = None
    best_score = 0
    
    # First try exact ID match
    if lesson_num:
        for lesson in course_lessons:
            if (lesson['Content_ID'] == lesson_num and 
                lesson['Content_Type'] == content_type):
                return lesson
    
    # If we have additional text, try fuzzy matching
    if additional_text:
        additional_lower = additional_text.lower()
        for lesson in course_lessons:
            title_lower = lesson['Title'].lower()
            
            # Check for key terms match
            key_terms_score = 0
            key_terms = re.findall(r'\b\w+\b', additional_lower)
            for term in key_terms:
                if term in title_lower:
                    key_terms_score += 1
            
            # Calculate similarity score
            similarity = SequenceMatcher(None, additional_lower, title_lower).ratio()
            total_score = (key_terms_score * 0.5) + (similarity * 0.5)
            
            if total_score > best_score:
                best_score = total_score
                best_match = lesson
    
    # Return best match if score is reasonable
    if best_score > 0.3:
        return best_match
    
    # Fallback: return lesson by number only
    if lesson_num:
        for lesson in course_lessons:
            if lesson['Content_ID'] == lesson_num:
                return lesson
    
    return None

def enhance_session_data(session, master_index):
    """Enhance a single session with master index data"""
    enhanced = session.copy()
    
    # Get course code from program
    program = session.get('Program', '')
    course_code = map_program_to_course(program)
    
    if not course_code or course_code not in master_index:
        # Can't enhance without course mapping
        return enhanced
    
    course_lessons = master_index[course_code]
    
    # Get current lesson topic
    current_topic = session.get('Lesson_Topic', '')
    
    # Try to extract lesson info
    lesson_num, content_type, additional = extract_lesson_info(current_topic)
    
    # Find best match in master index
    matched_lesson = find_best_match(lesson_num, content_type, additional, course_lessons)
    
    if matched_lesson:
        # Update with standardized data
        enhanced['Course_Code'] = course_code
        enhanced['Lesson_ID'] = matched_lesson['Content_ID']
        enhanced['Lesson_Type'] = matched_lesson['Content_Type']
        enhanced['Lesson_Topic_Standard'] = matched_lesson['Title']
        enhanced['Lesson_Topic_Original'] = current_topic
        enhanced['Duration_Min'] = matched_lesson['Duration_Min']
        
        # Add links if available
        if matched_lesson.get('Exit_Ticket_Link'):
            enhanced['Exit_Ticket_Link'] = matched_lesson['Exit_Ticket_Link']
        if matched_lesson.get('Quiz_Link'):
            enhanced['Quiz_Link'] = matched_lesson['Quiz_Link']
        if matched_lesson.get('Submission_Link'):
            enhanced['Submission_Link'] = matched_lesson['Submission_Link']
        
        enhanced['Data_Quality'] = 'Enhanced'
    else:
        # Couldn't match, keep original
        enhanced['Course_Code'] = course_code
        enhanced['Lesson_ID'] = lesson_num or ''
        enhanced['Lesson_Type'] = content_type or ''
        enhanced['Lesson_Topic_Standard'] = current_topic
        enhanced['Lesson_Topic_Original'] = current_topic
        enhanced['Data_Quality'] = 'Original'
    
    return enhanced

def process_all_data(vertical_data, master_index):
    """Process all session data with enhancements"""
    enhanced_data = []
    
    stats = {
        'total': len(vertical_data),
        'enhanced': 0,
        'original': 0,
        'by_program': {}
    }
    
    print("\n🔄 Processing sessions...")
    
    for i, session in enumerate(vertical_data):
        enhanced = enhance_session_data(session, master_index)
        enhanced_data.append(enhanced)
        
        # Update stats
        if enhanced.get('Data_Quality') == 'Enhanced':
            stats['enhanced'] += 1
        else:
            stats['original'] += 1
        
        # Track by program
        program = session.get('Program', 'Unknown')
        if program not in stats['by_program']:
            stats['by_program'][program] = {'total': 0, 'enhanced': 0}
        stats['by_program'][program]['total'] += 1
        if enhanced.get('Data_Quality') == 'Enhanced':
            stats['by_program'][program]['enhanced'] += 1
        
        # Progress indicator
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(vertical_data)} sessions...")
    
    return enhanced_data, stats

def save_enhanced_csv(enhanced_data, output_file):
    """Save enhanced data to CSV"""
    if not enhanced_data:
        print("No data to save")
        return
    
    # Define column order (original + new fields)
    columns = [
        'Student_ID',
        'Student_Name',
        'Program',
        'Course_Code',  # New
        'Session_Date',
        'Session_Number',
        'Lesson_ID',  # New
        'Lesson_Type',  # New
        'Lesson_Topic_Standard',  # New - standardized from master index
        'Lesson_Topic_Original',  # Original topic
        'Attendance',
        'Progress',
        'Session_Teacher',
        'Duration_Min',  # New
        'Schedule_Day',
        'Schedule_Time',
        'Primary_Teacher',
        'Lesson_Links',
        'Exit_Ticket_Link',  # New
        'Quiz_Link',  # New
        'Submission_Link',  # New
        'Data_Quality'  # New - Enhanced or Original
    ]
    
    # Filter to only include columns that exist
    available_columns = []
    for col in columns:
        if col in enhanced_data[0]:
            available_columns.append(col)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=available_columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(enhanced_data)
    
    print(f"\n✅ Saved enhanced data to {output_file}")

def main():
    """Main processing function"""
    print("🚀 ENHANCING SESSION DATA WITH MASTER INDEX")
    print("=" * 60)
    
    # File paths
    master_index_file = Path("data/vertical_csv/course-master-index.csv")
    vertical_csv_file = Path("data/vertical_csv/telebort_all_sessions_vertical_20250806_232159.csv")
    
    # Check files exist
    if not master_index_file.exists():
        print(f"❌ Master index not found: {master_index_file}")
        return
    
    if not vertical_csv_file.exists():
        print(f"❌ Vertical CSV not found: {vertical_csv_file}")
        return
    
    # Load data
    master_index = load_master_index(master_index_file)
    vertical_data = load_vertical_data(vertical_csv_file)
    
    # Process and enhance
    enhanced_data, stats = process_all_data(vertical_data, master_index)
    
    # Save enhanced data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("data/vertical_csv") / f"telebort_sessions_enhanced_{timestamp}.csv"
    save_enhanced_csv(enhanced_data, output_file)
    
    # Print statistics
    print("\n" + "=" * 60)
    print("📊 ENHANCEMENT STATISTICS")
    print("=" * 60)
    print(f"Total sessions: {stats['total']}")
    print(f"Enhanced: {stats['enhanced']} ({stats['enhanced']/stats['total']*100:.1f}%)")
    print(f"Original: {stats['original']} ({stats['original']/stats['total']*100:.1f}%)")
    
    print(f"\n📈 Enhancement by Program:")
    for program, program_stats in sorted(stats['by_program'].items()):
        enhanced_pct = (program_stats['enhanced']/program_stats['total']*100) if program_stats['total'] > 0 else 0
        print(f"  {program:<15} {program_stats['enhanced']:>4}/{program_stats['total']:<4} ({enhanced_pct:.1f}%)")
    
    print("\n" + "=" * 60)
    print("✨ Enhancement complete!")
    print(f"📁 Output file: {output_file}")
    print("\n📌 The enhanced CSV includes:")
    print("  - Standardized lesson topics from master index")
    print("  - Course codes mapped from programs")
    print("  - Lesson IDs and types")
    print("  - Exit ticket, quiz, and submission links")
    print("  - Data quality indicators")

if __name__ == "__main__":
    main()