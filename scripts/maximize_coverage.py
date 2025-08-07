#!/usr/bin/env python3
"""
Maximize lesson topic coverage using advanced inference techniques
Target: Reach 74.7% coverage (maximum achievable)
"""

import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional

class MaximizeCoverage:
    """Advanced inference engine to maximize lesson topic coverage"""
    
    def __init__(self):
        self.master_index = {}
        self.program_sequences = {}
        self.teacher_patterns = defaultdict(list)
        self.confidence_scores = {}
        self.audit_trail = []
        
    def load_data(self):
        """Load all necessary data files"""
        print("📁 Loading data files...")
        
        # Load master index
        with open('data/vertical_csv/course-master-index.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                course = row['Course_Code']
                if course not in self.master_index:
                    self.master_index[course] = []
                self.master_index[course].append(row)
        
        # Load current enhanced data
        with open('data/vertical_csv/telebort_sessions_final_20250806_233834.csv', 'r') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
        
        print(f"  ✓ Loaded {len(self.data)} sessions")
        print(f"  ✓ Loaded {len(self.master_index)} course curricula")
        
        return self.data
    
    def build_program_sequences(self):
        """Build detailed lesson sequences for each program"""
        print("\n🔧 Building program-specific sequences...")
        
        # Analyze existing filled sessions to learn patterns
        for row in self.data:
            if row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['-', '', '_']:
                program = row.get('Program', '')
                lesson_id = row.get('Lesson_ID', '')
                
                if program and lesson_id:
                    if program not in self.program_sequences:
                        self.program_sequences[program] = {}
                    
                    # Track which lesson IDs appear for each session number
                    session_num = row.get('Session_Number', '')
                    if session_num and session_num.isdigit():
                        session_int = int(session_num)
                        if session_int not in self.program_sequences[program]:
                            self.program_sequences[program][session_int] = Counter()
                        self.program_sequences[program][session_int][lesson_id] += 1
        
        # Print learned sequences
        for program in ['E (W-3)', 'AI-3', 'BBP', 'G (AI-2)', 'F (AI-1)']:
            if program in self.program_sequences:
                seq = self.program_sequences[program]
                sorted_sessions = sorted(seq.items())[:10]
                print(f"  {program}: Sessions {sorted_sessions[0][0]}-{sorted_sessions[-1][0] if sorted_sessions else 0}")
    
    def analyze_teacher_patterns(self):
        """Analyze teaching patterns by teacher"""
        print("\n👩‍🏫 Analyzing teacher patterns...")
        
        teacher_data = defaultdict(lambda: {'total': 0, 'with_topic': 0, 'lessons': []})
        
        for row in self.data:
            teacher = row.get('Session_Teacher', row.get('Primary_Teacher', ''))
            if teacher:
                teacher_data[teacher]['total'] += 1
                
                if row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['-', '', '_']:
                    teacher_data[teacher]['with_topic'] += 1
                    teacher_data[teacher]['lessons'].append({
                        'program': row.get('Program', ''),
                        'session_num': row.get('Session_Number', ''),
                        'lesson_id': row.get('Lesson_ID', ''),
                        'topic': row.get('Lesson_Topic_Standard', '')
                    })
        
        # Store patterns for high-volume teachers
        for teacher, data in teacher_data.items():
            if data['total'] > 50:  # Focus on teachers with many sessions
                coverage = (data['with_topic'] / data['total'] * 100) if data['total'] > 0 else 0
                print(f"  {teacher:<15} {data['total']:>4} sessions, {coverage:.1f}% coverage")
                self.teacher_patterns[teacher] = data['lessons']
    
    def enhanced_sequential_inference(self, session):
        """Enhanced inference using multiple signals"""
        student_id = session.get('Student_ID', '')
        program = session.get('Program', '')
        session_num = session.get('Session_Number', '')
        session_date = session.get('Session_Date', '')
        teacher = session.get('Session_Teacher', session.get('Primary_Teacher', ''))
        
        # Get student's history
        student_sessions = [s for s in self.data if s.get('Student_ID') == student_id]
        student_sessions.sort(key=lambda x: x.get('Session_Date', ''))
        
        inference_methods = []
        
        # Method 1: Direct session number mapping
        if session_num and session_num.isdigit() and program in self.program_sequences:
            session_int = int(session_num)
            if session_int in self.program_sequences[program]:
                most_common = self.program_sequences[program][session_int].most_common(1)
                if most_common:
                    lesson_id = most_common[0][0]
                    confidence = most_common[0][1] / sum(self.program_sequences[program][session_int].values())
                    inference_methods.append(('session_number_mapping', lesson_id, confidence))
        
        # Method 2: Sequential progression
        attended_before = sum(1 for s in student_sessions 
                            if s.get('Session_Date', '') < session_date 
                            and s.get('Attendance_Normalized') == 'Attended')
        
        expected_lesson = attended_before + 1
        course_code = self.map_program_to_course(program)
        
        if course_code and course_code in self.master_index:
            lessons = [l for l in self.master_index[course_code] if l['Content_Type'] == 'Lesson']
            if 0 <= attended_before < len(lessons):
                lesson = lessons[attended_before]
                inference_methods.append(('sequential_progression', lesson['Content_ID'], 0.7))
        
        # Method 3: Teacher pattern matching
        if teacher in self.teacher_patterns:
            teacher_lessons = self.teacher_patterns[teacher]
            # Find similar sessions from this teacher
            similar = [l for l in teacher_lessons 
                      if l['program'] == program and l['session_num'] == session_num]
            if similar:
                most_common_lesson = Counter([s['lesson_id'] for s in similar]).most_common(1)
                if most_common_lesson:
                    inference_methods.append(('teacher_pattern', most_common_lesson[0][0], 0.6))
        
        # Method 4: Temporal proximity
        # Look at sessions within 2 weeks
        try:
            current_date = datetime.strptime(session_date, '%Y-%m-%d')
            nearby_sessions = []
            for s in student_sessions:
                if s.get('Session_Date') and s.get('Lesson_ID'):
                    s_date = datetime.strptime(s['Session_Date'], '%Y-%m-%d')
                    if abs((s_date - current_date).days) <= 14:
                        nearby_sessions.append(s)
            
            if nearby_sessions:
                # Use the closest session's pattern
                closest = min(nearby_sessions, 
                            key=lambda x: abs((datetime.strptime(x['Session_Date'], '%Y-%m-%d') - current_date).days))
                if closest.get('Lesson_ID'):
                    # Adjust lesson number based on time difference
                    inference_methods.append(('temporal_proximity', closest['Lesson_ID'], 0.5))
        except:
            pass
        
        # Choose best inference
        if inference_methods:
            # Sort by confidence
            inference_methods.sort(key=lambda x: x[2], reverse=True)
            method, lesson_id, confidence = inference_methods[0]
            
            # Get lesson details from master index
            if course_code and course_code in self.master_index:
                for lesson in self.master_index[course_code]:
                    if lesson['Content_ID'] == lesson_id:
                        return lesson, method, confidence
        
        return None, None, 0
    
    def map_program_to_course(self, program):
        """Map program to course code"""
        mappings = {
            'G (AI-2)': 'AI-2',
            'F (AI-1)': 'AI-1',
            'AI-2': 'AI-2',
            'AI-1': 'AI-1',
            'AI-3': 'AI-2',
            'D (W-2)': 'Web-2',
            'C (W-1)': 'Web-1',
            'E (W-3)': 'Web-3',
            'BBP': 'BBP',
            'BBW': 'BBW',
            'A (FD-1)': 'Foundation 1',
            'B (FD-2)': 'Foundation 2',
            'H (BBD)': 'BBD',
            'JC': 'JC'
        }
        return mappings.get(program, None)
    
    def process_all_sessions(self):
        """Process all sessions with enhanced inference"""
        print("\n🚀 Processing sessions with enhanced inference...")
        
        enhanced_count = 0
        already_filled = 0
        legitimate_empty = 0
        could_not_infer = 0
        
        enhanced_data = []
        
        for i, row in enumerate(self.data):
            enhanced_row = row.copy()
            
            # Check if already has topic
            if row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['-', '', '_']:
                already_filled += 1
                enhanced_data.append(enhanced_row)
                continue
            
            # Check if legitimate empty (absent, no class, etc.)
            attendance = row.get('Attendance_Normalized', row.get('Attendance', ''))
            if attendance in ['Absent', 'No Class', 'Public Holiday', 'Teacher Parent Day', 'In Break', 'Off']:
                legitimate_empty += 1
                enhanced_row['Inference_Status'] = 'Legitimate_Empty'
                enhanced_data.append(enhanced_row)
                continue
            
            # Try enhanced inference for attended sessions
            if attendance == 'Attended':
                lesson, method, confidence = self.enhanced_sequential_inference(row)
                
                if lesson and confidence > 0.4:  # Confidence threshold
                    enhanced_row['Lesson_ID'] = lesson['Content_ID']
                    enhanced_row['Lesson_Type'] = lesson['Content_Type']
                    enhanced_row['Lesson_Topic_Standard'] = lesson['Title']
                    enhanced_row['Duration_Min'] = lesson.get('Duration_Min', '')
                    enhanced_row['Inference_Method'] = method
                    enhanced_row['Inference_Confidence'] = str(confidence)
                    enhanced_row['Inference_Status'] = 'Enhanced_MaxCoverage'
                    
                    # Add links if available
                    if lesson.get('Exit_Ticket_Link'):
                        enhanced_row['Exit_Ticket_Link'] = lesson['Exit_Ticket_Link']
                    if lesson.get('Quiz_Link'):
                        enhanced_row['Quiz_Link'] = lesson['Quiz_Link']
                    if lesson.get('Submission_Link'):
                        enhanced_row['Submission_Link'] = lesson['Submission_Link']
                    
                    enhanced_count += 1
                    
                    # Log audit trail
                    self.audit_trail.append({
                        'student': row['Student_ID'],
                        'date': row['Session_Date'],
                        'method': method,
                        'confidence': confidence,
                        'lesson': lesson['Title']
                    })
                else:
                    could_not_infer += 1
                    enhanced_row['Inference_Status'] = 'Could_Not_Infer'
            else:
                # Unmarked attendance
                enhanced_row['Inference_Status'] = 'Attendance_Unclear'
                could_not_infer += 1
            
            enhanced_data.append(enhanced_row)
            
            # Progress indicator
            if (i + 1) % 500 == 0:
                print(f"  Processed {i + 1}/{len(self.data)} sessions...")
        
        return enhanced_data, {
            'already_filled': already_filled,
            'enhanced': enhanced_count,
            'legitimate_empty': legitimate_empty,
            'could_not_infer': could_not_infer
        }
    
    def save_results(self, enhanced_data, stats):
        """Save enhanced data and reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save enhanced CSV
        output_file = Path("data/vertical_csv") / f"telebort_maximum_coverage_{timestamp}.csv"
        
        # Define columns
        columns = [
            'Student_ID', 'Student_Name', 'Program', 'Course_Code',
            'Session_Date', 'Session_Number',
            'Lesson_ID', 'Lesson_Type', 'Lesson_Topic_Standard', 'Lesson_Topic_Original',
            'Attendance', 'Attendance_Normalized', 'Progress', 'Progress_Inferred',
            'Session_Teacher', 'Primary_Teacher',
            'Duration_Min', 'Schedule_Day', 'Schedule_Time',
            'Lesson_Links', 'Exit_Ticket_Link', 'Quiz_Link', 'Submission_Link',
            'Inference_Status', 'Inference_Method', 'Inference_Confidence',
            'Data_Enhancement'
        ]
        
        available_columns = [col for col in columns if col in enhanced_data[0]]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=available_columns, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(enhanced_data)
        
        print(f"\n✅ Saved enhanced data to {output_file}")
        
        # Save audit trail
        audit_file = Path("data/vertical_csv") / f"coverage_audit_{timestamp}.json"
        with open(audit_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'statistics': stats,
                'audit_trail': self.audit_trail[:100]  # Save first 100 for review
            }, f, indent=2, default=str)
        
        print(f"📋 Saved audit trail to {audit_file}")
        
        return output_file
    
    def generate_teacher_reports(self, enhanced_data):
        """Generate reports for teachers showing their missing sessions"""
        print("\n📝 Generating teacher feedback forms...")
        
        teacher_missing = defaultdict(list)
        
        for row in enhanced_data:
            if row.get('Inference_Status') == 'Could_Not_Infer':
                teacher = row.get('Session_Teacher', row.get('Primary_Teacher', 'Unknown'))
                teacher_missing[teacher].append({
                    'student': row['Student_Name'],
                    'student_id': row['Student_ID'],
                    'date': row['Session_Date'],
                    'session': row.get('Session_Number', ''),
                    'program': row['Program']
                })
        
        # Save teacher reports
        report_dir = Path("data/teacher_feedback")
        report_dir.mkdir(exist_ok=True)
        
        for teacher, sessions in teacher_missing.items():
            if len(sessions) > 10:  # Only for teachers with significant gaps
                report_file = report_dir / f"missing_topics_{teacher.replace(' ', '_')}.csv"
                
                with open(report_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['date', 'student', 'student_id', 'program', 'session', 'lesson_topic'])
                    writer.writeheader()
                    
                    for session in sorted(sessions, key=lambda x: x['date']):
                        writer.writerow({
                            'date': session['date'],
                            'student': session['student'],
                            'student_id': session['student_id'],
                            'program': session['program'],
                            'session': session['session'],
                            'lesson_topic': ''  # To be filled by teacher
                        })
                
                print(f"  Created feedback form for {teacher}: {len(sessions)} sessions")
    
    def run(self):
        """Run the complete maximization process"""
        print("=" * 70)
        print("🚀 MAXIMIZING LESSON TOPIC COVERAGE")
        print("=" * 70)
        
        # Load data
        self.load_data()
        
        # Build intelligence
        self.build_program_sequences()
        self.analyze_teacher_patterns()
        
        # Process sessions
        enhanced_data, stats = self.process_all_sessions()
        
        # Calculate final coverage
        total = len(enhanced_data)
        has_topic = sum(1 for row in enhanced_data 
                       if row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['-', '', '_'])
        
        coverage = (has_topic / total * 100) if total > 0 else 0
        
        # Print results
        print("\n" + "=" * 70)
        print("📊 FINAL RESULTS")
        print("=" * 70)
        print(f"Total sessions:        {total}")
        print(f"Already filled:        {stats['already_filled']} ({stats['already_filled']/total*100:.1f}%)")
        print(f"Newly enhanced:        {stats['enhanced']} ({stats['enhanced']/total*100:.1f}%)")
        print(f"Legitimate empty:      {stats['legitimate_empty']} ({stats['legitimate_empty']/total*100:.1f}%)")
        print(f"Could not infer:       {stats['could_not_infer']} ({stats['could_not_infer']/total*100:.1f}%)")
        print(f"\n🎯 FINAL COVERAGE:     {has_topic}/{total} ({coverage:.1f}%)")
        
        # Save results
        output_file = self.save_results(enhanced_data, stats)
        
        # Generate teacher reports
        self.generate_teacher_reports(enhanced_data)
        
        print("\n" + "=" * 70)
        print("✨ Maximum coverage process complete!")
        print(f"📁 Main output: {output_file}")
        print("📋 Teacher feedback forms: data/teacher_feedback/")
        
        return enhanced_data, stats

if __name__ == "__main__":
    maximizer = MaximizeCoverage()
    maximizer.run()