#!/usr/bin/env python3
"""
Advanced Machine Learning Models to solve remaining 359 gaps
Uses custom implementations optimized for lesson prediction
"""

import csv
import json
import math
import random
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
import re
import statistics

class AdvancedMLPredictor:
    """Advanced ML models for predicting remaining lesson topics"""
    
    def __init__(self):
        self.training_data = []
        self.test_data = []
        self.feature_vectors = []
        self.models = {}
        self.feature_importance = {}
        
    def load_data(self):
        """Load the latest predictive enhanced data"""
        print("📁 Loading data for ML training...")
        
        # Find latest file
        files = list(Path("data/vertical_csv").glob("telebort_predictive_enhanced_*.csv"))
        if not files:
            files = list(Path("data/vertical_csv").glob("telebort_maximum_coverage_*.csv"))
        
        latest_file = sorted(files)[-1]
        
        with open(latest_file, 'r') as f:
            reader = csv.DictReader(f)
            all_data = list(reader)
        
        # Separate training (has topics) and test (gaps) data
        for row in all_data:
            if row.get('Attendance_Normalized') == 'Attended':
                if row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['', '-', '_']:
                    self.training_data.append(row)
                else:
                    self.test_data.append(row)
        
        print(f"  Training set: {len(self.training_data)} attended sessions with topics")
        print(f"  Test set: {len(self.test_data)} attended sessions without topics")
        
        return self.training_data, self.test_data
    
    def analyze_remaining_gaps(self):
        """Deep analysis of why these 359 sessions are difficult"""
        print("\n🔍 Analyzing Remaining Gaps Characteristics")
        print("=" * 70)
        
        if not self.test_data:
            print("No gaps to analyze")
            return
        
        # Analyze patterns
        patterns = {
            'programs': Counter(),
            'teachers': Counter(),
            'session_numbers': Counter(),
            'months': Counter(),
            'day_of_week': Counter(),
            'students': Counter()
        }
        
        missing_session_nums = 0
        irregular_patterns = []
        
        for session in self.test_data:
            # Program distribution
            patterns['programs'][session.get('Program', 'Unknown')] += 1
            
            # Teacher distribution
            patterns['teachers'][session.get('Session_Teacher', 'Unknown')] += 1
            
            # Session numbers
            session_num = session.get('Session_Number', '')
            if session_num:
                patterns['session_numbers'][session_num] += 1
            else:
                missing_session_nums += 1
            
            # Temporal patterns
            try:
                date = datetime.strptime(session['Session_Date'], '%Y-%m-%d')
                patterns['months'][date.month] += 1
                patterns['day_of_week'][date.weekday()] += 1
            except:
                pass
            
            # Student frequency
            patterns['students'][session['Student_ID']] += 1
            
            # Check for irregular patterns
            if session_num and not session_num.isdigit():
                irregular_patterns.append(session_num)
        
        # Print analysis
        print("\n📊 Gap Characteristics:")
        print("-" * 50)
        
        print("\nTop Programs with Gaps:")
        for prog, count in patterns['programs'].most_common(5):
            print(f"  {prog:<20} {count:>4} gaps")
        
        print("\nTop Teachers with Gaps:")
        for teacher, count in patterns['teachers'].most_common(5):
            print(f"  {teacher:<20} {count:>4} gaps")
        
        print("\nSession Number Distribution:")
        print(f"  Missing session numbers: {missing_session_nums}")
        print(f"  Irregular formats: {len(irregular_patterns)}")
        if irregular_patterns:
            print(f"  Examples: {irregular_patterns[:5]}")
        
        print("\nTemporal Patterns:")
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for day, count in sorted(patterns['day_of_week'].items()):
            print(f"  {day_names[day]}: {count} gaps")
        
        print("\nStudent Distribution:")
        students_with_many_gaps = [s for s, c in patterns['students'].items() if c > 5]
        print(f"  Students with >5 gaps: {len(students_with_many_gaps)}")
        
        # Identify why these are difficult
        print("\n⚠️ Why These Gaps Are Challenging:")
        print("-" * 50)
        
        challenges = []
        
        if missing_session_nums > 50:
            challenges.append(f"1. {missing_session_nums} sessions lack session numbers (key feature)")
        
        if len(irregular_patterns) > 20:
            challenges.append(f"2. {len(irregular_patterns)} sessions have irregular numbering (S22, etc.)")
        
        sparse_programs = [p for p, c in patterns['programs'].items() if c < 10]
        if sparse_programs:
            challenges.append(f"3. {len(sparse_programs)} programs have sparse data (<10 examples)")
        
        new_teachers = [t for t in patterns['teachers'].keys() if t not in ['Yasmin', 'Rahmat', 'Khairina']]
        if new_teachers:
            challenges.append(f"4. Includes {len(new_teachers)} teachers with limited training data")
        
        for challenge in challenges:
            print(f"  {challenge}")
        
        return patterns
    
    def engineer_advanced_features(self, session, all_data=None):
        """Engineer sophisticated features for ML models"""
        features = {}
        
        # 1. Basic features
        features['program_encoded'] = hash(session.get('Program', '')) % 100
        features['has_session_num'] = 1 if session.get('Session_Number') else 0
        
        # 2. Session number features
        session_num = session.get('Session_Number', '')
        if session_num:
            # Handle various formats
            if session_num.isdigit():
                features['session_num_int'] = int(session_num)
                features['session_num_mod5'] = int(session_num) % 5
                features['session_num_mod10'] = int(session_num) % 10
            else:
                # Extract number from formats like "S22"
                nums = re.findall(r'\d+', session_num)
                if nums:
                    features['session_num_int'] = int(nums[-1])
                else:
                    features['session_num_int'] = 0
        else:
            features['session_num_int'] = -1
        
        # 3. Temporal features
        try:
            date = datetime.strptime(session['Session_Date'], '%Y-%m-%d')
            features['day_of_week'] = date.weekday()
            features['month'] = date.month
            features['day_of_month'] = date.day
            features['week_of_year'] = date.isocalendar()[1]
            
            # Days since course start (estimate)
            course_start = datetime(2024, 9, 1)
            features['days_since_start'] = (date - course_start).days
        except:
            features['day_of_week'] = -1
            features['month'] = -1
            features['day_of_month'] = -1
            features['week_of_year'] = -1
            features['days_since_start'] = -1
        
        # 4. Student progress features
        if all_data:
            student_id = session['Student_ID']
            student_sessions = [s for s in all_data if s['Student_ID'] == student_id]
            
            # Count previous attended sessions
            prev_attended = sum(1 for s in student_sessions 
                              if s['Session_Date'] < session['Session_Date'] 
                              and s.get('Attendance_Normalized') == 'Attended')
            features['prev_attended_count'] = prev_attended
            
            # Student's completion rate
            total_sessions = len(student_sessions)
            attended = sum(1 for s in student_sessions if s.get('Attendance_Normalized') == 'Attended')
            features['student_attendance_rate'] = attended / total_sessions if total_sessions > 0 else 0
            
            # Gap since last session
            student_sessions.sort(key=lambda x: x['Session_Date'])
            for i, s in enumerate(student_sessions):
                if s['Session_Date'] == session['Session_Date'] and i > 0:
                    try:
                        prev_date = datetime.strptime(student_sessions[i-1]['Session_Date'], '%Y-%m-%d')
                        curr_date = datetime.strptime(session['Session_Date'], '%Y-%m-%d')
                        features['days_since_last'] = (curr_date - prev_date).days
                    except:
                        features['days_since_last'] = 7
                    break
            else:
                features['days_since_last'] = 7
        
        # 5. Teacher features
        teacher = session.get('Session_Teacher', session.get('Primary_Teacher', ''))
        features['teacher_encoded'] = hash(teacher) % 50
        
        # 6. Program-specific features
        program = session.get('Program', '')
        features['is_ai_program'] = 1 if 'AI' in program else 0
        features['is_web_program'] = 1 if 'W-' in program or 'Web' in program else 0
        features['is_foundation'] = 1 if 'FD' in program or 'Foundation' in program else 0
        features['is_bb_program'] = 1 if 'BB' in program else 0
        
        # 7. Context window features (look at nearby sessions)
        if all_data:
            # Count how many students have same session on same date
            same_date_sessions = [s for s in all_data 
                                 if s['Session_Date'] == session['Session_Date']
                                 and s['Program'] == session['Program']]
            features['cohort_size'] = len(same_date_sessions)
            
            # Check if most have topics
            with_topics = sum(1 for s in same_date_sessions 
                            if s.get('Lesson_Topic_Standard') and 
                            s['Lesson_Topic_Standard'] not in ['', '-', '_'])
            features['cohort_coverage'] = with_topics / len(same_date_sessions) if same_date_sessions else 0
        
        return features
    
    def build_feature_matrix(self):
        """Build feature matrix for all training and test data"""
        print("\n🔧 Engineering Features...")
        
        all_data = self.training_data + self.test_data
        
        # Build features for training data
        X_train = []
        y_train = []
        
        for session in self.training_data[:2000]:  # Limit for performance
            features = self.engineer_advanced_features(session, all_data)
            X_train.append(features)
            
            # Encode target (lesson ID)
            lesson_id = session.get('Lesson_ID', session.get('Lesson_Topic_Standard', ''))
            y_train.append(lesson_id)
        
        # Build features for test data
        X_test = []
        for session in self.test_data:
            features = self.engineer_advanced_features(session, all_data)
            X_test.append(features)
        
        print(f"  Built {len(X_train)} training samples with {len(X_train[0])} features")
        print(f"  Built {len(X_test)} test samples")
        
        return X_train, y_train, X_test
    
    def build_decision_tree(self, X_train, y_train, max_depth=5):
        """Custom decision tree implementation"""
        print("\n🌳 Building Decision Tree Model...")
        
        class Node:
            def __init__(self, prediction=None):
                self.prediction = prediction
                self.feature = None
                self.threshold = None
                self.left = None
                self.right = None
        
        def entropy(labels):
            """Calculate entropy of labels"""
            if not labels:
                return 0
            counts = Counter(labels)
            total = len(labels)
            ent = 0
            for count in counts.values():
                if count > 0:
                    p = count / total
                    ent -= p * math.log2(p)
            return ent
        
        def best_split(X, y, features_to_try=10):
            """Find best feature and threshold to split on"""
            best_gain = 0
            best_feature = None
            best_threshold = None
            
            parent_entropy = entropy(y)
            
            # Try random subset of features
            all_features = list(X[0].keys())
            features = random.sample(all_features, min(features_to_try, len(all_features)))
            
            for feature in features:
                values = [x.get(feature, 0) for x in X]
                unique_values = sorted(set(values))
                
                if len(unique_values) < 2:
                    continue
                
                # Try different thresholds
                for i in range(min(5, len(unique_values) - 1)):
                    threshold = unique_values[i]
                    
                    # Split data
                    left_idx = [j for j, x in enumerate(X) if x.get(feature, 0) <= threshold]
                    right_idx = [j for j, x in enumerate(X) if x.get(feature, 0) > threshold]
                    
                    if not left_idx or not right_idx:
                        continue
                    
                    # Calculate information gain
                    left_labels = [y[j] for j in left_idx]
                    right_labels = [y[j] for j in right_idx]
                    
                    left_entropy = entropy(left_labels)
                    right_entropy = entropy(right_labels)
                    
                    weighted_entropy = (len(left_idx) * left_entropy + 
                                      len(right_idx) * right_entropy) / len(y)
                    
                    gain = parent_entropy - weighted_entropy
                    
                    if gain > best_gain:
                        best_gain = gain
                        best_feature = feature
                        best_threshold = threshold
            
            return best_feature, best_threshold, best_gain
        
        def build_tree(X, y, depth=0):
            """Recursively build decision tree"""
            # Base cases
            if not y:
                return Node(prediction='Unknown')
            
            if depth >= max_depth or len(set(y)) == 1:
                # Return most common label
                most_common = Counter(y).most_common(1)[0][0]
                return Node(prediction=most_common)
            
            # Find best split
            feature, threshold, gain = best_split(X, y)
            
            if feature is None or gain < 0.01:
                # No good split found
                most_common = Counter(y).most_common(1)[0][0]
                return Node(prediction=most_common)
            
            # Create node
            node = Node()
            node.feature = feature
            node.threshold = threshold
            
            # Split data and build subtrees
            left_idx = [i for i, x in enumerate(X) if x.get(feature, 0) <= threshold]
            right_idx = [i for i, x in enumerate(X) if x.get(feature, 0) > threshold]
            
            left_X = [X[i] for i in left_idx]
            left_y = [y[i] for i in left_idx]
            right_X = [X[i] for i in right_idx]
            right_y = [y[i] for i in right_idx]
            
            node.left = build_tree(left_X, left_y, depth + 1)
            node.right = build_tree(right_X, right_y, depth + 1)
            
            return node
        
        # Build the tree
        tree = build_tree(X_train, y_train)
        
        # Calculate feature importance
        feature_counts = Counter()
        
        def count_features(node):
            if node.feature:
                feature_counts[node.feature] += 1
                if node.left:
                    count_features(node.left)
                if node.right:
                    count_features(node.right)
        
        count_features(tree)
        
        print(f"  Tree built with {sum(feature_counts.values())} decision nodes")
        print(f"  Top features: {dict(feature_counts.most_common(5))}")
        
        return tree, feature_counts
    
    def build_knn_model(self, X_train, y_train, k=5):
        """K-Nearest Neighbors implementation"""
        print("\n🎯 Building KNN Model...")
        
        def euclidean_distance(x1, x2):
            """Calculate distance between two feature vectors"""
            distance = 0
            all_features = set(x1.keys()) | set(x2.keys())
            for feature in all_features:
                v1 = x1.get(feature, 0)
                v2 = x2.get(feature, 0)
                distance += (v1 - v2) ** 2
            return math.sqrt(distance)
        
        def predict_knn(x_test):
            """Predict using KNN"""
            # Calculate distances to all training points
            distances = []
            for i, x_train in enumerate(X_train):
                dist = euclidean_distance(x_test, x_train)
                distances.append((dist, y_train[i]))
            
            # Sort by distance and get k nearest
            distances.sort(key=lambda x: x[0])
            k_nearest = distances[:k]
            
            # Vote for prediction
            votes = Counter(label for _, label in k_nearest)
            prediction = votes.most_common(1)[0][0] if votes else 'Unknown'
            
            # Calculate confidence based on vote proportion
            confidence = votes[prediction] / k if prediction in votes else 0
            
            return prediction, confidence
        
        print(f"  KNN model ready with k={k}")
        
        return predict_knn
    
    def build_pattern_matching_model(self):
        """Advanced pattern matching using discovered relationships"""
        print("\n🔍 Building Pattern Matching Model...")
        
        # Build pattern database from training data
        patterns = {
            'program_session': defaultdict(Counter),
            'program_sequence': defaultdict(list),
            'teacher_patterns': defaultdict(Counter),
            'temporal_patterns': defaultdict(Counter)
        }
        
        for session in self.training_data:
            program = session.get('Program', '')
            session_num = session.get('Session_Number', '')
            teacher = session.get('Session_Teacher', '')
            lesson = session.get('Lesson_ID', session.get('Lesson_Topic_Standard', ''))
            
            # Program-session patterns
            if program and session_num:
                key = f"{program}_{session_num}"
                patterns['program_session'][key][lesson] += 1
            
            # Teacher patterns
            if teacher:
                patterns['teacher_patterns'][teacher][lesson] += 1
            
            # Temporal patterns (day of week + program)
            try:
                date = datetime.strptime(session['Session_Date'], '%Y-%m-%d')
                dow = date.weekday()
                temporal_key = f"{program}_{dow}"
                patterns['temporal_patterns'][temporal_key][lesson] += 1
            except:
                pass
        
        def predict_pattern(session):
            """Predict using pattern matching"""
            predictions = []
            
            # Check program-session pattern
            program = session.get('Program', '')
            session_num = session.get('Session_Number', '')
            if program and session_num:
                key = f"{program}_{session_num}"
                if key in patterns['program_session']:
                    most_common = patterns['program_session'][key].most_common(1)
                    if most_common:
                        predictions.append((most_common[0][0], 0.8))
            
            # Check teacher pattern
            teacher = session.get('Session_Teacher', '')
            if teacher in patterns['teacher_patterns']:
                most_common = patterns['teacher_patterns'][teacher].most_common(1)
                if most_common:
                    predictions.append((most_common[0][0], 0.6))
            
            # Check temporal pattern
            try:
                date = datetime.strptime(session['Session_Date'], '%Y-%m-%d')
                dow = date.weekday()
                temporal_key = f"{program}_{dow}"
                if temporal_key in patterns['temporal_patterns']:
                    most_common = patterns['temporal_patterns'][temporal_key].most_common(1)
                    if most_common:
                        predictions.append((most_common[0][0], 0.5))
            except:
                pass
            
            # Return highest confidence prediction
            if predictions:
                predictions.sort(key=lambda x: x[1], reverse=True)
                return predictions[0]
            
            return None, 0
        
        print(f"  Pattern database built with {len(patterns['program_session'])} program-session patterns")
        
        return predict_pattern
    
    def ensemble_predict(self, session, models):
        """Ensemble voting from multiple models"""
        predictions = []
        
        # Get predictions from each model
        for model_name, model_func in models.items():
            if model_name == 'decision_tree':
                # Tree prediction
                tree = model_func
                node = tree
                features = self.engineer_advanced_features(session, self.training_data + self.test_data)
                
                while node.left and node.right:
                    if features.get(node.feature, 0) <= node.threshold:
                        node = node.left
                    else:
                        node = node.right
                
                if node.prediction:
                    predictions.append((node.prediction, 0.7))
            
            elif callable(model_func):
                # KNN or pattern matching
                if model_name == 'knn':
                    features = self.engineer_advanced_features(session, self.training_data + self.test_data)
                    pred, conf = model_func(features)
                else:
                    pred, conf = model_func(session)
                
                if pred and pred != 'Unknown':
                    predictions.append((pred, conf))
        
        if not predictions:
            return None, 0
        
        # Weighted voting
        vote_scores = defaultdict(float)
        for pred, conf in predictions:
            vote_scores[pred] += conf
        
        # Get best prediction
        best_pred = max(vote_scores.items(), key=lambda x: x[1])
        
        # Calculate ensemble confidence
        total_weight = sum(vote_scores.values())
        ensemble_confidence = best_pred[1] / total_weight if total_weight > 0 else 0
        
        return best_pred[0], ensemble_confidence
    
    def apply_ml_predictions(self):
        """Apply ML models to remaining gaps"""
        print("\n🚀 Applying Advanced ML Models...")
        
        # Build feature matrices
        X_train, y_train, X_test = self.build_feature_matrix()
        
        # Build models
        models = {}
        
        # 1. Decision Tree
        tree, feature_importance = self.build_decision_tree(X_train, y_train)
        models['decision_tree'] = tree
        self.feature_importance = feature_importance
        
        # 2. KNN Model
        knn_predictor = self.build_knn_model(X_train, y_train, k=7)
        models['knn'] = knn_predictor
        
        # 3. Pattern Matching
        pattern_predictor = self.build_pattern_matching_model()
        models['pattern'] = pattern_predictor
        
        # Apply ensemble predictions
        ml_predictions = []
        confidence_levels = {'high': 0, 'medium': 0, 'low': 0}
        
        print("\n📊 Making Predictions...")
        for i, session in enumerate(self.test_data):
            prediction, confidence = self.ensemble_predict(session, models)
            
            if prediction and confidence > 0.45:  # Lower threshold for ML
                ml_predictions.append({
                    'session': session,
                    'prediction': prediction,
                    'confidence': confidence,
                    'method': 'ml_ensemble'
                })
                
                # Track confidence levels
                if confidence >= 0.7:
                    confidence_levels['high'] += 1
                elif confidence >= 0.55:
                    confidence_levels['medium'] += 1
                else:
                    confidence_levels['low'] += 1
            
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(self.test_data)} gaps...")
        
        print(f"\n✅ ML Predictions Made: {len(ml_predictions)} out of {len(self.test_data)}")
        print(f"   Success rate: {len(ml_predictions)/len(self.test_data)*100:.1f}%")
        print(f"   High confidence: {confidence_levels['high']}")
        print(f"   Medium confidence: {confidence_levels['medium']}")
        print(f"   Low confidence: {confidence_levels['low']}")
        
        return ml_predictions
    
    def save_ml_enhanced_data(self, ml_predictions):
        """Save data enhanced with ML predictions"""
        print("\n💾 Saving ML-Enhanced Data...")
        
        # Load latest data
        files = list(Path("data/vertical_csv").glob("telebort_predictive_enhanced_*.csv"))
        if not files:
            files = list(Path("data/vertical_csv").glob("telebort_maximum_coverage_*.csv"))
        
        latest_file = sorted(files)[-1]
        
        with open(latest_file, 'r') as f:
            reader = csv.DictReader(f)
            all_data = list(reader)
        
        # Create prediction map
        prediction_map = {}
        for pred in ml_predictions:
            session = pred['session']
            key = f"{session['Student_ID']}_{session['Session_Date']}"
            prediction_map[key] = pred
        
        # Apply predictions
        enhanced_data = []
        ml_enhanced_count = 0
        
        for row in all_data:
            enhanced_row = row.copy()
            
            key = f"{row['Student_ID']}_{row['Session_Date']}"
            if key in prediction_map:
                pred = prediction_map[key]
                
                # Map prediction to lesson topic
                lesson_topic = pred['prediction']
                
                # Try to get full lesson details from master index
                enhanced_row['Lesson_Topic_Standard'] = lesson_topic
                enhanced_row['Lesson_ID'] = lesson_topic
                enhanced_row['Inference_Method'] = 'ml_ensemble'
                enhanced_row['Inference_Confidence'] = str(pred['confidence'])
                enhanced_row['Inference_Status'] = 'ML_Advanced'
                
                ml_enhanced_count += 1
            
            enhanced_data.append(enhanced_row)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/vertical_csv/telebort_ml_enhanced_{timestamp}.csv"
        
        # Get columns
        if enhanced_data:
            columns = list(enhanced_data[0].keys())
            
            # Ensure ML fields are included
            ml_fields = ['Inference_Method', 'Inference_Confidence', 'Inference_Status']
            for field in ml_fields:
                if field not in columns:
                    columns.append(field)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(enhanced_data)
        
        print(f"  Saved to {output_file}")
        print(f"  Enhanced {ml_enhanced_count} sessions with ML predictions")
        
        return output_file, ml_enhanced_count
    
    def calculate_final_metrics(self, output_file):
        """Calculate final coverage metrics after ML enhancement"""
        print("\n📊 Final Coverage with ML Enhancement")
        print("=" * 70)
        
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        total = len(data)
        has_topic = sum(1 for row in data 
                       if row.get('Lesson_Topic_Standard') and 
                       row['Lesson_Topic_Standard'] not in ['', '-', '_'])
        
        attended = sum(1 for row in data if row.get('Attendance_Normalized') == 'Attended')
        attended_with_topic = sum(1 for row in data 
                                 if row.get('Attendance_Normalized') == 'Attended' and
                                 row.get('Lesson_Topic_Standard') and 
                                 row['Lesson_Topic_Standard'] not in ['', '-', '_'])
        
        print(f"Total sessions: {total}")
        print(f"Sessions with topics: {has_topic} ({has_topic/total*100:.1f}%)")
        print(f"Attended sessions with topics: {attended_with_topic}/{attended} ({attended_with_topic/attended*100:.1f}%)")
        
        # Count by inference type
        inference_counts = Counter(row.get('Inference_Status', 'Original') for row in data)
        
        print("\n📈 Coverage by Method:")
        for status, count in inference_counts.most_common():
            print(f"  {status:<25} {count:>5} ({count/total*100:.1f}%)")
        
        return has_topic, total, attended_with_topic, attended
    
    def run_complete_ml_pipeline(self):
        """Run the complete ML enhancement pipeline"""
        print("🚀 ADVANCED MACHINE LEARNING PIPELINE")
        print("=" * 70)
        
        # Load data
        self.load_data()
        
        # Analyze gaps
        patterns = self.analyze_remaining_gaps()
        
        # Apply ML models
        ml_predictions = self.apply_ml_predictions()
        
        # Save enhanced data
        output_file, enhanced_count = self.save_ml_enhanced_data(ml_predictions)
        
        # Calculate final metrics
        has_topic, total, attended_with_topic, attended = self.calculate_final_metrics(output_file)
        
        # Print summary
        print("\n" + "=" * 70)
        print("✨ ML ENHANCEMENT COMPLETE")
        print("=" * 70)
        print(f"📁 Output: {output_file}")
        print(f"🎯 ML predictions: {len(ml_predictions)}")
        print(f"📈 Final coverage: {has_topic}/{total} ({has_topic/total*100:.1f}%)")
        print(f"📊 Attended coverage: {attended_with_topic}/{attended} ({attended_with_topic/attended*100:.1f}%)")
        
        # Save summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'ml_predictions': len(ml_predictions),
            'total_coverage': has_topic/total*100,
            'attended_coverage': attended_with_topic/attended*100,
            'feature_importance': dict(self.feature_importance.most_common(10)),
            'output_file': output_file
        }
        
        with open('data/vertical_csv/ml_enhancement_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print("\n📋 Summary saved to ml_enhancement_summary.json")
        
        return ml_predictions

if __name__ == "__main__":
    predictor = AdvancedMLPredictor()
    predictor.run_complete_ml_pipeline()