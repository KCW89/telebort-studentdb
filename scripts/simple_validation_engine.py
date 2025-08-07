#!/usr/bin/env python3
"""
Simple Validation Engine
Direct validation against course master index - no ML, no predictions
"""

import csv
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re

class SimpleValidator:
    """Simple validation against course master index"""
    
    def __init__(self):
        self.master_index = {}
        self.validation_results = {
            'valid': [],
            'invalid': [],
            'missing': [],
            'sequence_errors': [],
            'attendance_errors': []
        }
        
    def load_master_index(self):
        """Load course master index as source of truth"""
        print("📚 Loading Course Master Index...")
        
        with open('data/vertical_csv/course-master-index.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                course = row['Course_Code']
                if course not in self.master_index:
                    self.master_index[course] = {
                        'lessons': [],
                        'titles': [],
                        'title_to_id': {},
                        'id_to_title': {}
                    }
                
                if row['Content_Type'] == 'Lesson':
                    lesson_id = row['Content_ID']
                    title = row['Title']
                    
                    self.master_index[course]['lessons'].append(lesson_id)
                    self.master_index[course]['titles'].append(title)
                    self.master_index[course]['title_to_id'][title.lower()] = lesson_id
                    self.master_index[course]['id_to_title'][lesson_id] = title
        
        print(f"  ✓ Loaded {len(self.master_index)} courses")
        for course in list(self.master_index.keys())[:5]:
            print(f"    {course}: {len(self.master_index[course]['lessons'])} lessons")
        
        return self.master_index
    
    def load_current_data(self):
        """Load current enhanced data"""
        print("\n📁 Loading Current Data...")
        
        # Find latest enhanced file
        files = list(Path("data/vertical_csv").glob("telebort_xgboost_enhanced_*.csv"))
        if not files:
            files = list(Path("data/vertical_csv").glob("telebort_ml_enhanced_*.csv"))
        if not files:
            files = list(Path("data/vertical_csv").glob("telebort_maximum_coverage_*.csv"))
        
        latest_file = sorted(files)[-1]
        
        with open(latest_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        print(f"  ✓ Loaded {len(data)} sessions from {latest_file.name}")
        return data
    
    def map_program_to_course(self, program):
        """Map program to course code"""
        mappings = {
            'G (AI-2)': 'AI-2',
            'F (AI-1)': 'AI-1',
            'AI-2': 'AI-2',
            'AI-1': 'AI-1',
            'AI-3': 'AI-2',  # AI-3 uses AI-2 curriculum
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
    
    def validate_lesson(self, session):
        """Validate a single lesson against master index"""
        lesson_topic = session.get('Lesson_Topic_Standard', '')
        program = session.get('Program', '')
        attendance = session.get('Attendance_Normalized', session.get('Attendance', ''))
        
        # Get course code
        course = self.map_program_to_course(program)
        
        # Validation result
        result = {
            'student': session.get('Student_Name', ''),
            'student_id': session.get('Student_ID', ''),
            'date': session.get('Session_Date', ''),
            'program': program,
            'course': course,
            'lesson_original': session.get('Lesson_Topic_Original', ''),
            'lesson_standard': lesson_topic,
            'attendance': attendance,
            'status': 'UNKNOWN',
            'reason': '',
            'suggested_correction': ''
        }
        
        # Rule 1: Missing lesson
        if not lesson_topic or lesson_topic in ['', '-', '_']:
            result['status'] = 'MISSING'
            result['reason'] = 'No lesson topic recorded'
            return result
        
        # Rule 2: No course mapping
        if not course or course not in self.master_index:
            result['status'] = 'INVALID'
            result['reason'] = f'Unknown program/course: {program}'
            return result
        
        # Rule 3: Attendance validation
        if attendance != 'Attended' and lesson_topic:
            result['status'] = 'ATTENDANCE_ERROR'
            result['reason'] = f'Has lesson but attendance is: {attendance}'
            return result
        
        # Rule 4: Exact match validation
        course_data = self.master_index[course]
        lesson_lower = lesson_topic.lower()
        
        # Check exact match
        if lesson_lower in course_data['title_to_id']:
            result['status'] = 'VALID'
            result['reason'] = 'Exact match with master index'
            return result
        
        # Check if it's a valid lesson title (even with minor differences)
        for title in course_data['titles']:
            if self.fuzzy_match(lesson_topic, title):
                result['status'] = 'VALID_WITH_TYPO'
                result['reason'] = f'Close match to: {title}'
                result['suggested_correction'] = title
                return result
        
        # Not found in master index
        result['status'] = 'INVALID'
        result['reason'] = 'Lesson not found in course curriculum'
        
        # Try to suggest correction
        suggestion = self.find_closest_match(lesson_topic, course_data['titles'])
        if suggestion:
            result['suggested_correction'] = suggestion
        
        return result
    
    def fuzzy_match(self, text1, text2, threshold=0.85):
        """Simple fuzzy matching"""
        # Normalize texts
        t1 = re.sub(r'[^\w\s]', '', text1.lower())
        t2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        # Check if most words match
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0
        return similarity >= threshold
    
    def find_closest_match(self, text, options):
        """Find closest matching option"""
        text_lower = text.lower()
        
        # Look for lesson number patterns
        lesson_num = None
        patterns = [
            r'lesson\s*(\d+)',
            r'l(\d+)',
            r'concept\s*(\d+)',
            r'^(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                lesson_num = int(match.group(1))
                break
        
        if lesson_num and lesson_num <= len(options):
            return options[lesson_num - 1]
        
        # Find best text match
        best_match = None
        best_score = 0
        
        for option in options:
            if self.fuzzy_match(text, option, 0.6):
                score = len(set(text.lower().split()).intersection(set(option.lower().split())))
                if score > best_score:
                    best_score = score
                    best_match = option
        
        return best_match
    
    def validate_sequence(self, student_sessions):
        """Validate lesson sequence for a student"""
        sequences = []
        
        # Sort by date
        sessions = sorted(student_sessions, key=lambda x: x.get('Session_Date', ''))
        
        # Track lesson numbers
        prev_lesson_num = 0
        
        for session in sessions:
            if session.get('Attendance_Normalized') != 'Attended':
                continue
            
            lesson = session.get('Lesson_Topic_Standard', '')
            if not lesson:
                continue
            
            # Extract lesson number
            lesson_num = None
            patterns = [r'lesson\s*(\d+)', r'l(\d+)', r'concept\s*(\d+)']
            for pattern in patterns:
                match = re.search(pattern, lesson.lower())
                if match:
                    lesson_num = int(match.group(1))
                    break
            
            if lesson_num:
                if lesson_num < prev_lesson_num:
                    sequences.append({
                        'student': session.get('Student_Name'),
                        'date': session.get('Session_Date'),
                        'issue': f'Lesson {lesson_num} after Lesson {prev_lesson_num}',
                        'lesson': lesson
                    })
                prev_lesson_num = max(prev_lesson_num, lesson_num)
        
        return sequences
    
    def validate_all(self, data):
        """Validate all sessions"""
        print("\n🔍 Validating All Sessions...")
        
        # Validate each session
        for i, session in enumerate(data):
            result = self.validate_lesson(session)
            
            # Categorize results
            if result['status'] == 'VALID':
                self.validation_results['valid'].append(result)
            elif result['status'] == 'VALID_WITH_TYPO':
                self.validation_results['invalid'].append(result)
            elif result['status'] == 'MISSING':
                self.validation_results['missing'].append(result)
            elif result['status'] == 'ATTENDANCE_ERROR':
                self.validation_results['attendance_errors'].append(result)
            else:
                self.validation_results['invalid'].append(result)
            
            # Progress indicator
            if (i + 1) % 500 == 0:
                print(f"  Validated {i + 1}/{len(data)} sessions...")
        
        # Validate sequences by student
        print("\n🔄 Validating Sequences...")
        students = defaultdict(list)
        for session in data:
            students[session.get('Student_ID')].append(session)
        
        for student_id, sessions in students.items():
            seq_errors = self.validate_sequence(sessions)
            self.validation_results['sequence_errors'].extend(seq_errors)
        
        print(f"  ✓ Validation complete")
        
        return self.validation_results
    
    def generate_report(self):
        """Generate validation report"""
        print("\n📊 VALIDATION REPORT")
        print("=" * 70)
        
        total = sum(len(v) for v in self.validation_results.values())
        
        print(f"Total sessions validated: {total}")
        print(f"\n✅ Valid: {len(self.validation_results['valid'])} ({len(self.validation_results['valid'])/total*100:.1f}%)")
        print(f"❌ Invalid: {len(self.validation_results['invalid'])} ({len(self.validation_results['invalid'])/total*100:.1f}%)")
        print(f"❓ Missing: {len(self.validation_results['missing'])} ({len(self.validation_results['missing'])/total*100:.1f}%)")
        print(f"⚠️  Attendance Errors: {len(self.validation_results['attendance_errors'])} ({len(self.validation_results['attendance_errors'])/total*100:.1f}%)")
        print(f"🔄 Sequence Errors: {len(self.validation_results['sequence_errors'])}")
        
        # Sample invalid entries
        print("\n📝 Sample Invalid Entries (need correction):")
        print("-" * 70)
        for result in self.validation_results['invalid'][:5]:
            print(f"\nStudent: {result['student']} ({result['student_id']})")
            print(f"  Date: {result['date']}")
            print(f"  Program: {result['program']}")
            print(f"  Lesson: {result['lesson_standard']}")
            print(f"  Reason: {result['reason']}")
            if result['suggested_correction']:
                print(f"  ✨ Suggestion: {result['suggested_correction']}")
        
        # Sample sequence errors
        if self.validation_results['sequence_errors']:
            print("\n🔄 Sample Sequence Errors:")
            print("-" * 70)
            for error in self.validation_results['sequence_errors'][:5]:
                print(f"{error['student']} - {error['date']}: {error['issue']}")
        
        # Actionable insights
        print("\n💡 ACTIONABLE INSIGHTS")
        print("=" * 70)
        
        # Count by reason
        reasons = defaultdict(int)
        for result in self.validation_results['invalid']:
            reasons[result['reason']] += 1
        
        print("\nInvalid Reasons Breakdown:")
        for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
            print(f"  {reason}: {count}")
        
        # Count suggestions
        has_suggestion = sum(1 for r in self.validation_results['invalid'] if r['suggested_correction'])
        print(f"\n✨ Auto-correctable: {has_suggestion} ({has_suggestion/len(self.validation_results['invalid'])*100:.1f}% of invalid)")
        
        return self.validation_results
    
    def save_validation_report(self):
        """Save validation results to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save invalid entries for correction
        invalid_file = f"data/validation/invalid_lessons_{timestamp}.csv"
        Path("data/validation").mkdir(exist_ok=True)
        
        with open(invalid_file, 'w', newline='', encoding='utf-8') as f:
            if self.validation_results['invalid']:
                fieldnames = self.validation_results['invalid'][0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.validation_results['invalid'])
        
        print(f"\n📁 Saved invalid entries to: {invalid_file}")
        
        # Save all results as JSON
        json_file = f"data/validation/validation_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'summary': {
                    'valid': len(self.validation_results['valid']),
                    'invalid': len(self.validation_results['invalid']),
                    'missing': len(self.validation_results['missing']),
                    'attendance_errors': len(self.validation_results['attendance_errors']),
                    'sequence_errors': len(self.validation_results['sequence_errors'])
                },
                'sample_results': {
                    'valid': self.validation_results['valid'][:10],
                    'invalid': self.validation_results['invalid'][:10],
                    'missing': self.validation_results['missing'][:10]
                }
            }, f, indent=2, default=str)
        
        print(f"📁 Saved full report to: {json_file}")
        
        return invalid_file, json_file
    
    def run_validation(self):
        """Run complete validation process"""
        print("🚀 SIMPLE VALIDATION ENGINE")
        print("=" * 70)
        print("No ML, No Predictions - Just Facts\n")
        
        # Load master index
        self.load_master_index()
        
        # Load current data
        data = self.load_current_data()
        
        # Validate all
        self.validate_all(data)
        
        # Generate report
        self.generate_report()
        
        # Save results
        invalid_file, json_file = self.save_validation_report()
        
        print("\n" + "=" * 70)
        print("✅ Validation Complete!")
        print(f"📋 Review invalid entries in: {invalid_file}")
        print(f"📊 Full report in: {json_file}")
        
        return self.validation_results

if __name__ == "__main__":
    validator = SimpleValidator()
    validator.run_validation()