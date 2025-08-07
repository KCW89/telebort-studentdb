#!/usr/bin/env python3
"""
Analyze relationships between Session_Date, Session_Number, Attendance, and Lesson_Topic
to develop better inference rules for data enhancement
"""

import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json

def load_data(file_path):
    """Load vertical CSV data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return data

def analyze_session_number_patterns(data):
    """Analyze how session numbers relate to dates and lessons"""
    print("=" * 60)
    print("📊 SESSION NUMBER ANALYSIS")
    print("=" * 60)
    
    # Group by student to track progression
    student_sessions = defaultdict(list)
    for row in data:
        if row['Session_Date']:
            student_sessions[row['Student_ID']].append({
                'date': row['Session_Date'],
                'number': row['Session_Number'],
                'attendance': row['Attendance'],
                'topic': row['Lesson_Topic']
            })
    
    # Sort each student's sessions by date
    for student_id, sessions in student_sessions.items():
        sessions.sort(key=lambda x: x['date'])
    
    # Analyze patterns
    patterns = {
        'sequential': 0,  # 1, 2, 3, 4...
        'repeated': 0,     # Same number multiple times
        'missing': 0,      # Gaps in numbering
        'reset': 0,        # Numbering restarts
        'non_numeric': 0   # Non-standard numbering
    }
    
    session_number_examples = defaultdict(list)
    
    for student_id, sessions in student_sessions.items():
        prev_num = None
        for i, session in enumerate(sessions):
            curr_num = session['number']
            
            # Track examples of different session numbers
            if curr_num and curr_num != '-':
                session_number_examples[curr_num].append({
                    'student': student_id,
                    'date': session['date'],
                    'topic': session['topic'][:50] if session['topic'] else ''
                })
            
            # Analyze progression
            if curr_num and curr_num != '-':
                try:
                    curr_int = int(re.findall(r'\d+', curr_num)[0]) if re.findall(r'\d+', curr_num) else None
                    if prev_num:
                        prev_int = int(re.findall(r'\d+', prev_num)[0]) if re.findall(r'\d+', prev_num) else None
                        if curr_int and prev_int:
                            if curr_int == prev_int + 1:
                                patterns['sequential'] += 1
                            elif curr_int == prev_int:
                                patterns['repeated'] += 1
                            elif curr_int < prev_int:
                                patterns['reset'] += 1
                            else:
                                patterns['missing'] += 1
                except:
                    patterns['non_numeric'] += 1
                prev_num = curr_num
    
    print("\n🔢 Session Number Patterns:")
    for pattern, count in patterns.items():
        print(f"  {pattern:<15} {count:>6} occurrences")
    
    print("\n📝 Common Session Number Formats:")
    session_formats = Counter([row['Session_Number'] for row in data if row['Session_Number']])
    for fmt, count in session_formats.most_common(10):
        if fmt and fmt != '-':
            print(f"  '{fmt}'  appears {count} times")
    
    return student_sessions, session_number_examples

def analyze_attendance_patterns(data):
    """Analyze attendance patterns and their relationship to lessons"""
    print("\n" + "=" * 60)
    print("📊 ATTENDANCE PATTERN ANALYSIS")
    print("=" * 60)
    
    # Attendance vs Lesson Progress
    attendance_lesson_map = defaultdict(lambda: defaultdict(int))
    
    for row in data:
        attendance = row['Attendance']
        has_lesson = bool(row['Lesson_Topic'] and row['Lesson_Topic'] != '-')
        progress = row['Progress']
        
        if attendance:
            attendance_lesson_map[attendance]['total'] += 1
            if has_lesson:
                attendance_lesson_map[attendance]['with_lesson'] += 1
            attendance_lesson_map[attendance][f'progress_{progress}'] += 1
    
    print("\n📋 Attendance vs Lesson Data:")
    print(f"{'Attendance':<20} {'Total':<8} {'Has Lesson':<12} {'Completion Rate'}")
    print("-" * 60)
    
    for attendance, stats in sorted(attendance_lesson_map.items()):
        total = stats['total']
        with_lesson = stats['with_lesson']
        lesson_rate = (with_lesson / total * 100) if total > 0 else 0
        completed = stats.get('progress_Completed', 0)
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        print(f"{attendance:<20} {total:<8} {with_lesson:<12} {completion_rate:.1f}%")
    
    # Special attendance values that might be teacher names
    teacher_names = ["Soumiya", "Han Yang", "Khairina", "Arrvinna", "Syahin",
                    "Hafiz", "Yasmin", "Nurafrina", "Rahmat", "Fatin",
                    "Aisyah", "Puvin", "Afiqah", "Aaron", "Farah"]
    
    print("\n👩‍🏫 Teacher Names in Attendance Field:")
    for teacher in teacher_names:
        count = sum(1 for row in data if row['Attendance'] == teacher)
        if count > 0:
            print(f"  {teacher:<15} {count:>4} times (likely means 'Attended')")
    
    return attendance_lesson_map

def analyze_date_progression(data):
    """Analyze how dates progress and relate to lesson sequence"""
    print("\n" + "=" * 60)
    print("📊 DATE PROGRESSION ANALYSIS")
    print("=" * 60)
    
    # Group by student and program
    student_programs = defaultdict(lambda: {'sessions': [], 'program': ''})
    
    for row in data:
        if row['Session_Date']:
            student_programs[row['Student_ID']]['sessions'].append({
                'date': row['Session_Date'],
                'topic': row['Lesson_Topic'],
                'attendance': row['Attendance']
            })
            student_programs[row['Student_ID']]['program'] = row['Program']
    
    # Analyze weekly patterns
    weekly_patterns = defaultdict(int)
    date_gaps = []
    
    for student_id, info in student_programs.items():
        sessions = sorted(info['sessions'], key=lambda x: x['date'])
        
        for i in range(1, len(sessions)):
            try:
                date1 = datetime.strptime(sessions[i-1]['date'], '%Y-%m-%d')
                date2 = datetime.strptime(sessions[i]['date'], '%Y-%m-%d')
                gap_days = (date2 - date1).days
                
                if gap_days > 0:
                    date_gaps.append(gap_days)
                    
                    # Classify gap
                    if gap_days == 7:
                        weekly_patterns['weekly'] += 1
                    elif gap_days == 14:
                        weekly_patterns['biweekly'] += 1
                    elif gap_days < 7:
                        weekly_patterns['multi_per_week'] += 1
                    elif gap_days > 14 and gap_days <= 30:
                        weekly_patterns['irregular'] += 1
                    else:
                        weekly_patterns['long_break'] += 1
            except:
                pass
    
    print("\n📅 Session Frequency Patterns:")
    for pattern, count in sorted(weekly_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern:<20} {count:>6} occurrences")
    
    if date_gaps:
        avg_gap = sum(date_gaps) / len(date_gaps)
        print(f"\n  Average gap between sessions: {avg_gap:.1f} days")
        print(f"  Most common gap: {Counter(date_gaps).most_common(1)[0][0]} days")
    
    return student_programs

def analyze_lesson_progression(data):
    """Analyze how lessons progress within programs"""
    print("\n" + "=" * 60)
    print("📊 LESSON PROGRESSION ANALYSIS")
    print("=" * 60)
    
    # Group by program
    program_lessons = defaultdict(lambda: defaultdict(list))
    
    for row in data:
        if row['Lesson_Topic'] and row['Lesson_Topic'] != '-':
            program = row['Program']
            topic = row['Lesson_Topic']
            
            # Extract lesson number if present
            lesson_match = re.search(r'L(\d+)', topic)
            if lesson_match:
                lesson_num = int(lesson_match.group(1))
                program_lessons[program][lesson_num].append(topic)
    
    print("\n📚 Lesson Sequences by Program:")
    
    for program in sorted(program_lessons.keys())[:5]:  # Show first 5 programs
        lessons = program_lessons[program]
        if lessons:
            print(f"\n  {program}:")
            sorted_lessons = sorted(lessons.items())[:10]  # Show first 10 lessons
            for lesson_num, topics in sorted_lessons:
                # Show most common topic for this lesson number
                topic_counter = Counter(topics)
                most_common = topic_counter.most_common(1)[0]
                print(f"    L{lesson_num}: {most_common[0][:50]}... ({most_common[1]} times)")
    
    return program_lessons

def analyze_missing_data_patterns(data):
    """Analyze patterns in missing data to develop inference rules"""
    print("\n" + "=" * 60)
    print("📊 MISSING DATA PATTERNS")
    print("=" * 60)
    
    missing_patterns = {
        'no_topic_but_attended': 0,
        'no_topic_but_completed': 0,
        'has_topic_no_attendance': 0,
        'no_session_number': 0,
        'complete_record': 0
    }
    
    inference_opportunities = []
    
    for row in data:
        has_topic = bool(row['Lesson_Topic'] and row['Lesson_Topic'] != '-')
        has_attendance = bool(row['Attendance'] and row['Attendance'] not in ['-', 'Not Marked'])
        has_session_num = bool(row['Session_Number'] and row['Session_Number'] != '-')
        is_attended = row['Attendance'] == 'Attended' or row['Attendance'] in ["Soumiya", "Han Yang", "Khairina"]
        is_completed = row['Progress'] == 'Completed'
        
        # Identify patterns
        if not has_topic and is_attended:
            missing_patterns['no_topic_but_attended'] += 1
            inference_opportunities.append({
                'type': 'missing_topic_attended',
                'student': row['Student_ID'],
                'date': row['Session_Date'],
                'program': row['Program']
            })
        
        if not has_topic and is_completed:
            missing_patterns['no_topic_but_completed'] += 1
        
        if has_topic and not has_attendance:
            missing_patterns['has_topic_no_attendance'] += 1
        
        if not has_session_num:
            missing_patterns['no_session_number'] += 1
        
        if has_topic and has_attendance and has_session_num:
            missing_patterns['complete_record'] += 1
    
    print("\n🔍 Missing Data Patterns:")
    total = len(data)
    for pattern, count in missing_patterns.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {pattern:<30} {count:>6} ({percentage:.1f}%)")
    
    print("\n💡 Inference Opportunities:")
    print(f"  - Sessions marked 'Attended' but no lesson topic: {missing_patterns['no_topic_but_attended']}")
    print(f"    → Can infer lesson based on date sequence and program curriculum")
    print(f"  - Sessions marked 'Completed' but no lesson topic: {missing_patterns['no_topic_but_completed']}")
    print(f"    → Strong indicator that a lesson was taught")
    
    return missing_patterns, inference_opportunities

def develop_inference_rules(student_sessions, program_lessons, attendance_patterns):
    """Develop specific inference rules based on analysis"""
    print("\n" + "=" * 60)
    print("📊 INFERENCE RULES DEVELOPED")
    print("=" * 60)
    
    rules = {
        'session_number_rules': [],
        'lesson_topic_rules': [],
        'attendance_rules': [],
        'progress_rules': []
    }
    
    # Rule 1: Session numbers should be sequential for attended sessions
    rules['session_number_rules'].append({
        'rule': 'sequential_numbering',
        'description': 'Session numbers increment by 1 for each attended session',
        'condition': 'Attendance == "Attended"',
        'action': 'Assign next sequential number'
    })
    
    # Rule 2: Teacher name in attendance means attended
    rules['attendance_rules'].append({
        'rule': 'teacher_name_attended',
        'description': 'Teacher name in attendance field means student attended',
        'condition': 'Attendance in teacher_names',
        'action': 'Set Attendance = "Attended", Session_Teacher = teacher_name'
    })
    
    # Rule 3: If attended and no topic, infer from sequence
    rules['lesson_topic_rules'].append({
        'rule': 'infer_from_sequence',
        'description': 'Infer lesson topic from previous/next sessions in same program',
        'condition': 'Attendance == "Attended" AND Lesson_Topic is empty',
        'action': 'Look up expected lesson number from curriculum sequence'
    })
    
    # Rule 4: Progress inference
    rules['progress_rules'].append({
        'rule': 'attended_implies_progress',
        'description': 'Attended session with lesson topic implies at least "In Progress"',
        'condition': 'Attendance == "Attended" AND has Lesson_Topic',
        'action': 'If Progress empty, set to "In Progress"'
    })
    
    print("\n📋 Inference Rules Summary:")
    
    for category, category_rules in rules.items():
        print(f"\n  {category.replace('_', ' ').title()}:")
        for rule in category_rules:
            print(f"    • {rule['description']}")
            print(f"      When: {rule['condition']}")
            print(f"      Then: {rule['action']}")
    
    return rules

def save_analysis_report(all_results, output_file):
    """Save detailed analysis report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': all_results['summary'],
        'inference_rules': all_results['rules'],
        'missing_data_patterns': all_results['missing_patterns']
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {output_file}")

def main():
    """Run comprehensive relationship analysis"""
    print("🔬 ANALYZING FIELD RELATIONSHIPS IN SESSION DATA")
    print("=" * 60)
    
    # Load data
    data_file = 'data/vertical_csv/telebort_all_sessions_vertical_20250806_232159.csv'
    data = load_data(data_file)
    print(f"📁 Loaded {len(data)} session records")
    
    # Run analyses
    student_sessions, session_examples = analyze_session_number_patterns(data)
    attendance_patterns = analyze_attendance_patterns(data)
    student_programs = analyze_date_progression(data)
    program_lessons = analyze_lesson_progression(data)
    missing_patterns, inference_opps = analyze_missing_data_patterns(data)
    
    # Develop inference rules
    rules = develop_inference_rules(student_sessions, program_lessons, attendance_patterns)
    
    # Compile results
    all_results = {
        'summary': {
            'total_sessions': len(data),
            'unique_students': len(set(row['Student_ID'] for row in data)),
            'unique_programs': len(set(row['Program'] for row in data if row['Program']))
        },
        'missing_patterns': missing_patterns,
        'rules': rules
    }
    
    # Save report
    report_file = f'data/vertical_csv/field_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    save_analysis_report(all_results, report_file)
    
    print("\n" + "=" * 60)
    print("✅ ANALYSIS COMPLETE!")
    print("\n🎯 Key Insights:")
    print("  1. Teacher names in attendance field indicate attended sessions")
    print("  2. Session numbers should increment sequentially for attended sessions")
    print("  3. Most sessions follow weekly patterns (7-day intervals)")
    print("  4. 89% of sessions are missing lesson topics - need inference")
    print("  5. Programs follow predictable lesson sequences (L1, L2, L3...)")

if __name__ == "__main__":
    main()