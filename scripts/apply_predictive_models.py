#!/usr/bin/env python3
"""
Apply predictive models to solve remaining gaps using discovered patterns
"""

import csv
import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
import re

class PredictiveModelApplicator:
    """Apply predictive models to enhance coverage beyond 55.8%"""
    
    def __init__(self):
        self.data = []
        self.master_index = {}
        self.cohort_patterns = {}
        self.predictions = []
        
    def load_data(self):
        """Load the maximum coverage data"""
        print("📁 Loading data...")
        
        # Load maximum coverage file
        with open('data/vertical_csv/telebort_maximum_coverage_20250807_000045.csv', 'r') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
        
        # Load master index
        with open('data/vertical_csv/course-master-index.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                course = row['Course_Code']
                if course not in self.master_index:
                    self.master_index[course] = []
                self.master_index[course].append(row)
        
        print(f"  Loaded {len(self.data)} sessions")
        return self.data
    
    def identify_gaps(self):
        """Identify sessions that still need prediction"""
        gaps = []
        
        for row in self.data:
            # Check if session has no lesson topic
            has_topic = (row.get('Lesson_Topic_Standard') and 
                        row['Lesson_Topic_Standard'] not in ['', '-', '_'])
            
            if not has_topic:
                # Check if it's a legitimate gap
                attendance = row.get('Attendance_Normalized', row.get('Attendance', ''))
                
                # Only consider attended sessions for prediction
                if attendance == 'Attended':
                    gaps.append(row)
        
        print(f"\n🔍 Found {len(gaps)} attended sessions without lesson topics")
        return gaps
    
    def build_cohort_model(self):
        """Build cohort-based prediction model"""
        print("\n👥 Building Cohort Model...")
        
        # Group sessions by program-date
        program_date_groups = defaultdict(list)
        
        for row in self.data:
            key = f"{row['Program']}_{row['Session_Date']}"
            program_date_groups[key].append(row)
        
        # Find patterns
        for key, sessions in program_date_groups.items():
            if len(sessions) > 1:
                # Find sessions with topics
                with_topics = [s for s in sessions 
                              if s.get('Lesson_Topic_Standard') and 
                              s['Lesson_Topic_Standard'] not in ['', '-', '_']]
                
                if with_topics:
                    # Store most common topic
                    topic_counts = Counter(s['Lesson_Topic_Standard'] for s in with_topics)
                    most_common = topic_counts.most_common(1)[0]
                    
                    self.cohort_patterns[key] = {
                        'topic': most_common[0],
                        'confidence': len(with_topics) / len(sessions),
                        'count': most_common[1]
                    }
        
        print(f"  Built {len(self.cohort_patterns)} cohort patterns")
        return self.cohort_patterns
    
    def apply_cohort_prediction(self, session):
        """Apply cohort-based prediction to a session"""
        key = f"{session['Program']}_{session['Session_Date']}"
        
        if key in self.cohort_patterns:
            pattern = self.cohort_patterns[key]
            if pattern['confidence'] > 0.5:
                return {
                    'topic': pattern['topic'],
                    'method': 'cohort_prediction',
                    'confidence': pattern['confidence']
                }
        
        return None
    
    def apply_session_mapping(self, session):
        """Apply direct session number to lesson mapping"""
        if not session.get('Session_Number'):
            return None
        
        try:
            session_num = int(session['Session_Number'])
        except:
            return None
        
        # Map program to course
        program = session.get('Program', '')
        course_map = {
            'E (W-3)': 'Web-3',
            'G (AI-2)': 'AI-2',
            'F (AI-1)': 'AI-1',
            'AI-3': 'AI-2',
            'AI-2': 'AI-2',
            'BBP': 'BBP',
            'BBW': 'BBW',
            'D (W-2)': 'Web-2',
            'C (W-1)': 'Web-1',
            'H (BBD)': 'BBD',
            'A (FD-1)': 'Foundation 1',
            'B (FD-2)': 'Foundation 2'
        }
        
        course = course_map.get(program)
        if not course or course not in self.master_index:
            return None
        
        # Find lessons in course
        lessons = [item for item in self.master_index[course] 
                  if item['Content_Type'] == 'Lesson']
        
        # Direct mapping: session number to lesson number
        if 0 < session_num <= len(lessons):
            lesson = lessons[session_num - 1]
            return {
                'topic': lesson['Title'],
                'lesson_id': lesson['Content_ID'],
                'method': 'session_mapping',
                'confidence': 0.8
            }
        
        return None
    
    def apply_cross_student_pattern(self, session):
        """Use patterns from other students in same program"""
        program = session.get('Program', '')
        session_num = session.get('Session_Number', '')
        
        if not session_num:
            return None
        
        # Find other students with same program and session number
        similar_sessions = []
        for row in self.data:
            if (row['Program'] == program and 
                row['Session_Number'] == session_num and
                row.get('Lesson_Topic_Standard') and
                row['Lesson_Topic_Standard'] not in ['', '-', '_']):
                similar_sessions.append(row)
        
        if similar_sessions:
            # Get most common topic
            topics = Counter(s['Lesson_Topic_Standard'] for s in similar_sessions)
            most_common = topics.most_common(1)[0]
            
            return {
                'topic': most_common[0],
                'method': 'cross_student',
                'confidence': min(0.7, most_common[1] / len(similar_sessions))
            }
        
        return None
    
    def apply_temporal_interpolation(self, session):
        """Interpolate based on sessions before and after"""
        student_id = session['Student_ID']
        session_date = session['Session_Date']
        
        # Get student's other sessions
        student_sessions = [s for s in self.data if s['Student_ID'] == student_id]
        student_sessions.sort(key=lambda x: x['Session_Date'])
        
        # Find sessions before and after
        before = None
        after = None
        
        for s in student_sessions:
            if s['Session_Date'] < session_date:
                if (s.get('Lesson_Topic_Standard') and 
                    s['Lesson_Topic_Standard'] not in ['', '-', '_']):
                    before = s
            elif s['Session_Date'] > session_date:
                if (s.get('Lesson_Topic_Standard') and 
                    s['Lesson_Topic_Standard'] not in ['', '-', '_']):
                    after = s
                    break
        
        # If we have both before and after, interpolate
        if before and after:
            # Check if lessons are sequential
            before_num = self.extract_lesson_number(before.get('Lesson_ID', ''))
            after_num = self.extract_lesson_number(after.get('Lesson_ID', ''))
            
            if before_num and after_num and after_num == before_num + 2:
                # This session is likely the lesson in between
                program = session.get('Program', '')
                course_map = {
                    'E (W-3)': 'Web-3',
                    'G (AI-2)': 'AI-2',
                    'F (AI-1)': 'AI-1',
                    'AI-3': 'AI-2',
                    'BBP': 'BBP'
                }
                
                course = course_map.get(program)
                if course and course in self.master_index:
                    lessons = [item for item in self.master_index[course] 
                              if item['Content_Type'] == 'Lesson']
                    
                    middle_num = before_num + 1
                    if 0 < middle_num <= len(lessons):
                        lesson = lessons[middle_num - 1]
                        return {
                            'topic': lesson['Title'],
                            'lesson_id': lesson['Content_ID'],
                            'method': 'temporal_interpolation',
                            'confidence': 0.6
                        }
        
        return None
    
    def extract_lesson_number(self, lesson_id):
        """Extract lesson number from various formats"""
        if not lesson_id:
            return None
        
        patterns = [
            r'L(\d+)',
            r'Lesson[_\s]?(\d+)',
            r'S\d+[_\s]?L(\d+)',
            r'^(\d+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(lesson_id), re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def apply_all_models(self, gaps):
        """Apply all predictive models to gaps"""
        print("\n🚀 Applying Predictive Models...")
        
        predictions = []
        method_counts = Counter()
        
        for i, session in enumerate(gaps):
            # Try each method in order of confidence
            prediction = None
            
            # 1. Try cohort prediction (highest confidence)
            prediction = self.apply_cohort_prediction(session)
            
            # 2. Try session mapping
            if not prediction:
                prediction = self.apply_session_mapping(session)
            
            # 3. Try cross-student pattern
            if not prediction:
                prediction = self.apply_cross_student_pattern(session)
            
            # 4. Try temporal interpolation
            if not prediction:
                prediction = self.apply_temporal_interpolation(session)
            
            if prediction:
                predictions.append({
                    'session': session,
                    'prediction': prediction
                })
                method_counts[prediction['method']] += 1
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(gaps)} gaps...")
        
        print(f"\n✅ Made {len(predictions)} predictions out of {len(gaps)} gaps")
        print(f"   Success rate: {len(predictions)/len(gaps)*100:.1f}%")
        
        print("\n📊 Prediction Methods Used:")
        for method, count in method_counts.most_common():
            print(f"  {method}: {count} predictions")
        
        return predictions
    
    def save_enhanced_data(self, predictions):
        """Save the enhanced data with predictions"""
        print("\n💾 Saving Enhanced Data...")
        
        # Create a copy of data
        enhanced_data = []
        prediction_map = {}
        
        # Build prediction map for quick lookup
        for pred in predictions:
            session = pred['session']
            key = f"{session['Student_ID']}_{session['Session_Date']}"
            prediction_map[key] = pred['prediction']
        
        # Apply predictions to data
        enhanced_count = 0
        for row in self.data:
            enhanced_row = row.copy()
            
            # Check if we have a prediction for this session
            key = f"{row['Student_ID']}_{row['Session_Date']}"
            if key in prediction_map:
                pred = prediction_map[key]
                enhanced_row['Lesson_Topic_Standard'] = pred['topic']
                enhanced_row['Inference_Method'] = pred['method']
                enhanced_row['Inference_Confidence'] = str(pred['confidence'])
                enhanced_row['Inference_Status'] = 'Predictive_Model'
                
                if 'lesson_id' in pred:
                    enhanced_row['Lesson_ID'] = pred['lesson_id']
                
                enhanced_count += 1
            
            enhanced_data.append(enhanced_row)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/vertical_csv/telebort_predictive_enhanced_{timestamp}.csv"
        
        # Get columns from first row and add new fields
        if enhanced_data:
            columns = list(enhanced_data[0].keys())
            
            # Add new fields if not present
            new_fields = ['Inference_Method', 'Inference_Confidence', 'Inference_Status', 'Lesson_ID']
            for field in new_fields:
                if field not in columns:
                    columns.append(field)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(enhanced_data)
        
        print(f"  Saved to {output_file}")
        print(f"  Enhanced {enhanced_count} sessions with predictions")
        
        return output_file, enhanced_count
    
    def calculate_final_coverage(self):
        """Calculate the final coverage after predictions"""
        print("\n📊 Final Coverage Analysis")
        print("=" * 70)
        
        # Count sessions with topics
        total = len(self.data)
        has_topic = sum(1 for row in self.data 
                       if row.get('Lesson_Topic_Standard') and 
                       row['Lesson_Topic_Standard'] not in ['', '-', '_'])
        
        print(f"Total sessions: {total}")
        print(f"Sessions with topics: {has_topic}")
        print(f"Final coverage: {has_topic/total*100:.1f}%")
        
        # Breakdown by status
        status_counts = Counter(row.get('Inference_Status', 'Original') for row in self.data)
        
        print("\n📈 Coverage Breakdown:")
        for status, count in status_counts.most_common():
            print(f"  {status}: {count} ({count/total*100:.1f}%)")
    
    def run(self):
        """Run the complete predictive modeling process"""
        print("🚀 APPLYING PREDICTIVE MODELS TO MAXIMIZE COVERAGE")
        print("=" * 70)
        
        # Load data
        self.load_data()
        
        # Identify gaps
        gaps = self.identify_gaps()
        
        if not gaps:
            print("No gaps found to predict!")
            return
        
        # Build models
        self.build_cohort_model()
        
        # Apply predictions
        predictions = self.apply_all_models(gaps)
        
        # Save enhanced data
        output_file, enhanced_count = self.save_enhanced_data(predictions)
        
        # Calculate final coverage
        self.calculate_final_coverage()
        
        # Generate summary
        print("\n" + "=" * 70)
        print("✨ PREDICTIVE MODELING COMPLETE")
        print("=" * 70)
        print(f"📁 Output: {output_file}")
        print(f"🎯 New predictions: {len(predictions)}")
        print(f"📈 Coverage improvement: +{len(predictions)/len(self.data)*100:.1f}%")
        
        # Save summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_sessions': len(self.data),
            'gaps_found': len(gaps),
            'predictions_made': len(predictions),
            'success_rate': len(predictions)/len(gaps)*100 if gaps else 0,
            'coverage_gain': len(predictions)/len(self.data)*100,
            'output_file': output_file
        }
        
        with open('data/vertical_csv/predictive_model_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        return predictions

if __name__ == "__main__":
    applicator = PredictiveModelApplicator()
    applicator.run()