#!/usr/bin/env python3
"""
XGBoost and Advanced Scikit-learn Models for Maximum Coverage
Using state-of-the-art ML to solve the remaining gaps
"""

import csv
import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Import ML libraries
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb

class XGBoostEnhancer:
    """Advanced ML models using XGBoost and scikit-learn"""
    
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.scaler = StandardScaler()
        self.feature_importance = {}
        
    def load_and_prepare_data(self):
        """Load and prepare data for ML training"""
        print("📁 Loading data for advanced ML...")
        
        # Find latest enhanced file
        files = list(Path("data/vertical_csv").glob("telebort_ml_enhanced_*.csv"))
        if not files:
            files = list(Path("data/vertical_csv").glob("telebort_predictive_enhanced_*.csv"))
        
        latest_file = sorted(files)[-1]
        
        # Load data
        df = pd.read_csv(latest_file)
        print(f"  Loaded {len(df)} sessions from {latest_file.name}")
        
        # Filter to attended sessions only
        df_attended = df[df['Attendance_Normalized'] == 'Attended'].copy()
        
        # Separate training and test data
        train_df = df_attended[df_attended['Lesson_Topic_Standard'].notna() & 
                               (df_attended['Lesson_Topic_Standard'] != '') &
                               (df_attended['Lesson_Topic_Standard'] != '-')].copy()
        
        test_df = df_attended[df_attended['Lesson_Topic_Standard'].isna() | 
                             (df_attended['Lesson_Topic_Standard'] == '') |
                             (df_attended['Lesson_Topic_Standard'] == '-')].copy()
        
        print(f"  Training set: {len(train_df)} sessions")
        print(f"  Test set (gaps): {len(test_df)} sessions")
        
        return df, train_df, test_df
    
    def engineer_features(self, df):
        """Engineer advanced features for ML models"""
        print("\n🔧 Engineering Advanced Features...")
        
        features = pd.DataFrame()
        
        # Program encoding
        le_program = LabelEncoder()
        df['Program_Encoded'] = le_program.fit_transform(df['Program'].fillna('Unknown'))
        features['program_encoded'] = df['Program_Encoded']
        self.encoders['program'] = le_program
        
        # Teacher encoding
        le_teacher = LabelEncoder()
        df['Teacher_Encoded'] = le_teacher.fit_transform(
            df['Session_Teacher'].fillna(df['Primary_Teacher'].fillna('Unknown'))
        )
        features['teacher_encoded'] = df['Teacher_Encoded']
        self.encoders['teacher'] = le_teacher
        
        # Session number features
        def extract_session_num(s):
            if pd.isna(s):
                return -1
            s = str(s)
            # Extract numbers from various formats
            import re
            nums = re.findall(r'\d+', s)
            return int(nums[-1]) if nums else -1
        
        df['Session_Num_Int'] = df['Session_Number'].apply(extract_session_num)
        features['session_num'] = df['Session_Num_Int']
        features['session_num_mod5'] = df['Session_Num_Int'] % 5
        features['session_num_mod10'] = df['Session_Num_Int'] % 10
        features['has_session_num'] = (df['Session_Num_Int'] >= 0).astype(int)
        
        # Temporal features
        df['Session_Date'] = pd.to_datetime(df['Session_Date'])
        features['day_of_week'] = df['Session_Date'].dt.dayofweek
        features['month'] = df['Session_Date'].dt.month
        features['day_of_month'] = df['Session_Date'].dt.day
        features['week_of_year'] = df['Session_Date'].dt.isocalendar().week
        features['quarter'] = df['Session_Date'].dt.quarter
        
        # Calculate days since course start
        course_start = pd.to_datetime('2024-09-01')
        features['days_since_start'] = (df['Session_Date'] - course_start).dt.days
        
        # Student features
        student_stats = df.groupby('Student_ID').agg({
            'Attendance_Normalized': lambda x: (x == 'Attended').sum(),
            'Session_Date': 'count'
        }).rename(columns={'Attendance_Normalized': 'attended_count', 'Session_Date': 'total_count'})
        
        student_stats['attendance_rate'] = student_stats['attended_count'] / student_stats['total_count']
        
        df = df.merge(student_stats[['attendance_rate']], left_on='Student_ID', right_index=True, how='left')
        features['student_attendance_rate'] = df['attendance_rate']
        
        # Program type indicators
        features['is_ai_program'] = df['Program'].str.contains('AI', na=False).astype(int)
        features['is_web_program'] = df['Program'].str.contains('W-|Web', na=False).astype(int)
        features['is_foundation'] = df['Program'].str.contains('FD|Foundation', na=False).astype(int)
        features['is_bb_program'] = df['Program'].str.contains('BB', na=False).astype(int)
        features['is_jc_program'] = (df['Program'] == 'JC').astype(int)
        
        # Session patterns - look at previous and next sessions
        df_sorted = df.sort_values(['Student_ID', 'Session_Date'])
        
        # Days since last session for each student
        df_sorted['prev_date'] = df_sorted.groupby('Student_ID')['Session_Date'].shift(1)
        df_sorted['days_since_last'] = (df_sorted['Session_Date'] - df_sorted['prev_date']).dt.days
        features['days_since_last'] = df_sorted['days_since_last'].fillna(7)
        
        # Cumulative attended sessions per student
        df_sorted['cumulative_attended'] = df_sorted.groupby('Student_ID').cumcount()
        features['cumulative_attended'] = df_sorted['cumulative_attended']
        
        # Cohort features - how many students have same session on same date
        cohort_size = df.groupby(['Session_Date', 'Program']).size().reset_index(name='cohort_size')
        df = df.merge(cohort_size, on=['Session_Date', 'Program'], how='left')
        features['cohort_size'] = df['cohort_size'].fillna(1)
        
        # Session density - sessions in surrounding week
        window_sessions = []
        for idx, row in df.iterrows():
            date = row['Session_Date']
            program = row['Program']
            
            # Count sessions within ±3 days
            nearby = df[(df['Program'] == program) & 
                       (abs((df['Session_Date'] - date).dt.days) <= 3)]
            window_sessions.append(len(nearby))
        
        features['window_density'] = window_sessions
        
        # Fill NaN values with appropriate defaults
        for col in features.columns:
            if features[col].dtype in ['uint32', 'uint16', 'uint8']:
                features[col] = features[col].fillna(0)
            elif features[col].dtype in ['int64', 'int32', 'float64', 'float32']:
                features[col] = features[col].fillna(-1)
            else:
                # Convert to float first to handle fillna
                features[col] = features[col].astype('float64').fillna(-1)
        
        print(f"  Created {features.shape[1]} features for {features.shape[0]} samples")
        
        # Store feature names
        self.feature_names = features.columns.tolist()
        
        return features, df
    
    def train_xgboost_model(self, X_train, y_train, X_val, y_val):
        """Train XGBoost model with optimized parameters"""
        print("\n🚀 Training XGBoost Model...")
        
        # Encode labels
        le_target = LabelEncoder()
        y_train_encoded = le_target.fit_transform(y_train)
        y_val_encoded = le_target.transform(y_val)
        self.encoders['target'] = le_target
        
        # XGBoost parameters optimized for this task
        params = {
            'objective': 'multi:softprob',
            'num_class': len(le_target.classes_),
            'max_depth': 8,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.05,
            'reg_lambda': 1,
            'random_state': 42,
            'n_jobs': -1,
            'early_stopping_rounds': 20,  # Move early_stopping_rounds to params
            'eval_metric': 'mlogloss'
        }
        
        # Train model
        xgb_model = xgb.XGBClassifier(**params)
        xgb_model.fit(
            X_train, y_train_encoded,
            eval_set=[(X_val, y_val_encoded)],
            verbose=False
        )
        
        # Evaluate
        y_pred = xgb_model.predict(X_val)
        accuracy = accuracy_score(y_val_encoded, y_pred)
        print(f"  XGBoost Validation Accuracy: {accuracy:.3f}")
        
        # Feature importance
        importance = xgb_model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importance))
        sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        print("\n  Top 10 Important Features:")
        for feat, imp in sorted_importance[:10]:
            print(f"    {feat:<25} {imp:.4f}")
        
        self.models['xgboost'] = xgb_model
        self.feature_importance['xgboost'] = feature_importance
        
        return xgb_model
    
    def train_random_forest(self, X_train, y_train, X_val, y_val):
        """Train Random Forest with optimized parameters"""
        print("\n🌲 Training Random Forest Model...")
        
        y_train_encoded = self.encoders['target'].transform(y_train)
        y_val_encoded = self.encoders['target'].transform(y_val)
        
        rf_model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        
        rf_model.fit(X_train, y_train_encoded)
        
        # Evaluate
        y_pred = rf_model.predict(X_val)
        accuracy = accuracy_score(y_val_encoded, y_pred)
        print(f"  Random Forest Validation Accuracy: {accuracy:.3f}")
        
        self.models['random_forest'] = rf_model
        
        return rf_model
    
    def train_neural_network(self, X_train, y_train, X_val, y_val):
        """Train Neural Network model"""
        print("\n🧠 Training Neural Network Model...")
        
        # Scale features for NN
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        y_train_encoded = self.encoders['target'].transform(y_train)
        y_val_encoded = self.encoders['target'].transform(y_val)
        
        nn_model = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            max_iter=500,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        
        nn_model.fit(X_train_scaled, y_train_encoded)
        
        # Evaluate
        y_pred = nn_model.predict(X_val_scaled)
        accuracy = accuracy_score(y_val_encoded, y_pred)
        print(f"  Neural Network Validation Accuracy: {accuracy:.3f}")
        
        self.models['neural_network'] = nn_model
        
        return nn_model
    
    def ensemble_predict(self, X_test, confidence_threshold=0.5):
        """Ensemble prediction from all models"""
        print("\n🎯 Making Ensemble Predictions...")
        
        predictions = []
        confidences = []
        
        # Get predictions from each model
        all_probs = []
        
        # XGBoost predictions
        if 'xgboost' in self.models:
            xgb_probs = self.models['xgboost'].predict_proba(X_test)
            all_probs.append(xgb_probs * 1.2)  # Weight XGBoost higher
        
        # Random Forest predictions
        if 'random_forest' in self.models:
            rf_probs = self.models['random_forest'].predict_proba(X_test)
            all_probs.append(rf_probs)
        
        # Neural Network predictions
        if 'neural_network' in self.models:
            X_test_scaled = self.scaler.transform(X_test)
            nn_probs = self.models['neural_network'].predict_proba(X_test_scaled)
            all_probs.append(nn_probs * 0.9)  # Weight NN slightly lower
        
        # Average probabilities
        if all_probs:
            avg_probs = np.mean(all_probs, axis=0)
            
            # Get predictions and confidence
            for probs in avg_probs:
                best_class = np.argmax(probs)
                confidence = probs[best_class]
                
                if confidence >= confidence_threshold:
                    prediction = self.encoders['target'].inverse_transform([best_class])[0]
                    predictions.append(prediction)
                    confidences.append(confidence)
                else:
                    predictions.append(None)
                    confidences.append(confidence)
        
        return predictions, confidences
    
    def apply_to_gaps(self, test_df, features_test):
        """Apply models to remaining gaps"""
        print("\n📊 Applying to Remaining Gaps...")
        
        # Make predictions
        predictions, confidences = self.ensemble_predict(features_test, confidence_threshold=0.45)
        
        # Count successful predictions
        successful = sum(1 for p in predictions if p is not None)
        
        print(f"  Made {successful} predictions out of {len(test_df)} gaps")
        print(f"  Success rate: {successful/len(test_df)*100:.1f}%")
        
        # Analyze confidence distribution
        conf_array = np.array([c for c in confidences if c is not None])
        if len(conf_array) > 0:
            print(f"\n  Confidence Statistics:")
            print(f"    Mean: {conf_array.mean():.3f}")
            print(f"    Median: {np.median(conf_array):.3f}")
            print(f"    Min: {conf_array.min():.3f}")
            print(f"    Max: {conf_array.max():.3f}")
        
        return predictions, confidences
    
    def save_enhanced_data(self, df, test_df, predictions, confidences):
        """Save the XGBoost-enhanced data"""
        print("\n💾 Saving XGBoost-Enhanced Data...")
        
        # Create prediction mapping
        test_df = test_df.copy()
        test_df['XGB_Prediction'] = predictions
        test_df['XGB_Confidence'] = confidences
        
        # Merge back to main dataframe
        for idx, row in test_df.iterrows():
            if row['XGB_Prediction'] is not None:
                df.loc[idx, 'Lesson_Topic_Standard'] = row['XGB_Prediction']
                df.loc[idx, 'Inference_Method'] = 'xgboost_ensemble'
                df.loc[idx, 'Inference_Confidence'] = str(row['XGB_Confidence'])
                df.loc[idx, 'Inference_Status'] = 'XGBoost_ML'
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/vertical_csv/telebort_xgboost_enhanced_{timestamp}.csv"
        
        df.to_csv(output_file, index=False)
        print(f"  Saved to {output_file}")
        
        # Calculate final metrics
        total = len(df)
        has_topic = df['Lesson_Topic_Standard'].notna() & (df['Lesson_Topic_Standard'] != '') & (df['Lesson_Topic_Standard'] != '-')
        topic_count = has_topic.sum()
        
        attended = df['Attendance_Normalized'] == 'Attended'
        attended_total = attended.sum()
        attended_with_topic = (attended & has_topic).sum()
        
        print(f"\n📊 Final Coverage with XGBoost:")
        print(f"  Total: {topic_count}/{total} ({topic_count/total*100:.1f}%)")
        print(f"  Attended: {attended_with_topic}/{attended_total} ({attended_with_topic/attended_total*100:.1f}%)")
        
        return output_file
    
    def run_complete_pipeline(self):
        """Run the complete XGBoost enhancement pipeline"""
        print("🚀 XGBOOST ADVANCED ML ENHANCEMENT")
        print("=" * 70)
        
        # Load data
        df, train_df, test_df = self.load_and_prepare_data()
        
        # Engineer features
        features_train, train_df = self.engineer_features(train_df)
        features_test, test_df = self.engineer_features(test_df)
        
        # Prepare training data
        X = features_train.reset_index(drop=True)
        y = train_df['Lesson_Topic_Standard'].reset_index(drop=True)
        
        # Remove any remaining NaN targets
        valid_mask = y.notna()
        X = X[valid_mask]
        y = y[valid_mask]
        
        # Remove classes with only 1 sample
        value_counts = y.value_counts()
        valid_classes = value_counts[value_counts >= 2].index
        mask = y.isin(valid_classes)
        X = X[mask]
        y = y[mask]
        
        # Split for validation (stratify only if we have enough samples)
        if len(y.unique()) > 10:
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
        
        print(f"\n📚 Training Data:")
        print(f"  Training set: {len(X_train)} samples")
        print(f"  Validation set: {len(X_val)} samples")
        print(f"  Unique lessons: {y.nunique()}")
        
        # Train models
        self.train_xgboost_model(X_train, y_train, X_val, y_val)
        self.train_random_forest(X_train, y_train, X_val, y_val)
        self.train_neural_network(X_train, y_train, X_val, y_val)
        
        # Apply to gaps
        predictions, confidences = self.apply_to_gaps(test_df, features_test)
        
        # Save enhanced data
        output_file = self.save_enhanced_data(df, test_df, predictions, confidences)
        
        print("\n" + "=" * 70)
        print("✨ XGBoost Enhancement Complete!")
        print(f"📁 Output: {output_file}")
        
        # Save model artifacts
        import joblib
        
        model_dir = Path("models")
        model_dir.mkdir(exist_ok=True)
        
        # Save models
        joblib.dump(self.models, model_dir / "xgboost_models.pkl")
        joblib.dump(self.encoders, model_dir / "encoders.pkl")
        joblib.dump(self.scaler, model_dir / "scaler.pkl")
        joblib.dump(self.feature_importance, model_dir / "feature_importance.pkl")
        
        print(f"📦 Models saved to {model_dir}/")
        
        return predictions, confidences

if __name__ == "__main__":
    enhancer = XGBoostEnhancer()
    enhancer.run_complete_pipeline()