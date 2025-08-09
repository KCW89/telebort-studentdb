#!/usr/bin/env python3
"""
Derived Metrics Calculator
Calculate all metrics from 10 core parameters
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

class DerivedMetricsCalculator:
    """Calculate all analytics from core parameters"""
    
    def __init__(self, core_df):
        self.df = core_df
        self.metrics = {}
    
    def calculate_all_metrics(self):
        """Calculate all derived metrics"""
        
        self.metrics = {
            'student_metrics': self.calculate_student_metrics(),
            'teacher_metrics': self.calculate_teacher_metrics(),
            'program_metrics': self.calculate_program_metrics(),
            'risk_flags': self.identify_at_risk_students(),
            'quality_metrics': self.calculate_quality_metrics(),
            'temporal_metrics': self.calculate_temporal_metrics()
        }
        
        return self.metrics
    
    def calculate_student_metrics(self):
        """Per-student metrics"""
        student_metrics = {}
        
        for student_id in self.df['student_id'].unique():
            student_data = self.df[self.df['student_id'] == student_id]
            
            # Attendance rate
            attended = (student_data['attendance_status'] == 'Attended').sum()
            absent = (student_data['attendance_status'] == 'Absent').sum()
            total_classes = attended + absent
            attendance_rate = attended / total_classes if total_classes > 0 else 0
            
            # Completion rate
            completed = (student_data['progress_status'] == 'Completed').sum()
            total_sessions = len(student_data[student_data['attendance_status'] == 'Attended'])
            completion_rate = completed / total_sessions if total_sessions > 0 else 0
            
            # Learning velocity (sessions per completion)
            avg_sessions_to_complete = total_sessions / completed if completed > 0 else 0
            
            # Data quality
            avg_confidence = student_data['data_confidence'].mean()
            
            # Consecutive absences
            absences = student_data.sort_values('session_date')['attendance_status'] == 'Absent'
            max_consecutive_absences = self.max_consecutive(absences)
            
            student_metrics[student_id] = {
                'attendance_rate': round(attendance_rate, 3),
                'completion_rate': round(completion_rate, 3),
                'avg_sessions_to_complete': round(avg_sessions_to_complete, 1),
                'avg_data_confidence': round(avg_confidence, 3),
                'max_consecutive_absences': max_consecutive_absences,
                'total_sessions': len(student_data),
                'sessions_attended': attended,
                'lessons_completed': completed
            }
        
        return student_metrics
    
    def calculate_teacher_metrics(self):
        """Teacher effectiveness metrics"""
        teacher_metrics = {}
        
        for teacher in self.df['session_teacher'].unique():
            if pd.isna(teacher):
                continue
            
            teacher_data = self.df[self.df['session_teacher'] == teacher]
            
            # Students taught
            unique_students = teacher_data['student_id'].nunique()
            
            # Completion rate
            completed = (teacher_data['progress_status'] == 'Completed').sum()
            total = len(teacher_data[teacher_data['attendance_status'] == 'Attended'])
            completion_rate = completed / total if total > 0 else 0
            
            # Average progress per session
            progress_score = teacher_data['progress_status'].map({
                'Completed': 1.0,
                'InProgress': 0.5,
                'NotStarted': 0.0,
                'Unknown': 0.0
            }).mean()
            
            # Data quality when teaching
            avg_confidence = teacher_data['data_confidence'].mean()
            
            teacher_metrics[teacher] = {
                'students_taught': unique_students,
                'total_sessions': len(teacher_data),
                'completion_rate': round(completion_rate, 3),
                'progress_score': round(progress_score, 3),
                'avg_data_confidence': round(avg_confidence, 3),
                'sessions_completed': completed
            }
        
        return teacher_metrics
    
    def calculate_program_metrics(self):
        """Program-level metrics"""
        program_metrics = {}
        
        for program in self.df['program_code'].unique():
            if pd.isna(program):
                continue
            
            program_data = self.df[self.df['program_code'] == program]
            
            # Student count
            unique_students = program_data['student_id'].nunique()
            
            # Attendance
            attended = (program_data['attendance_status'] == 'Attended').sum()
            total_possible = attended + (program_data['attendance_status'] == 'Absent').sum()
            attendance_rate = attended / total_possible if total_possible > 0 else 0
            
            # Progress
            completed = (program_data['progress_status'] == 'Completed').sum()
            in_progress = (program_data['progress_status'] == 'InProgress').sum()
            
            # Difficulty (avg sessions to complete)
            student_sessions = program_data.groupby('student_id').size()
            avg_sessions = student_sessions.mean()
            
            program_metrics[program] = {
                'total_students': unique_students,
                'total_sessions': len(program_data),
                'attendance_rate': round(attendance_rate, 3),
                'lessons_completed': completed,
                'lessons_in_progress': in_progress,
                'avg_sessions_per_student': round(avg_sessions, 1),
                'completion_percentage': round(completed / len(program_data) * 100, 1) if len(program_data) > 0 else 0
            }
        
        return program_metrics
    
    def identify_at_risk_students(self):
        """Identify students at risk"""
        at_risk = []
        
        for student_id in self.df['student_id'].unique():
            student_data = self.df[self.df['student_id'] == student_id].sort_values('session_date')
            
            # Risk factors
            risk_score = 0
            reasons = []
            
            # Check consecutive absences
            absences = student_data['attendance_status'] == 'Absent'
            consecutive_absences = self.max_consecutive(absences)
            if consecutive_absences >= 3:
                risk_score += 3
                reasons.append(f"{consecutive_absences} consecutive absences")
            
            # Check incomplete lessons
            incomplete = (student_data['progress_status'] == 'InProgress').sum()
            if incomplete >= 3:
                risk_score += 2
                reasons.append(f"{incomplete} incomplete lessons")
            
            # Check recent attendance (last 5 sessions)
            recent = student_data.tail(5)
            recent_absences = (recent['attendance_status'] == 'Absent').sum()
            if recent_absences >= 3:
                risk_score += 2
                reasons.append(f"{recent_absences}/5 recent absences")
            
            # Low data confidence
            avg_confidence = student_data['data_confidence'].mean()
            if avg_confidence < 0.5:
                risk_score += 1
                reasons.append(f"Low data quality ({avg_confidence:.2f})")
            
            if risk_score >= 3:
                at_risk.append({
                    'student_id': student_id,
                    'risk_score': risk_score,
                    'risk_level': 'HIGH' if risk_score >= 5 else 'MEDIUM',
                    'reasons': reasons,
                    'last_attendance': student_data['session_date'].max()
                })
        
        return sorted(at_risk, key=lambda x: x['risk_score'], reverse=True)
    
    def calculate_quality_metrics(self):
        """Overall data quality metrics"""
        quality = {
            'total_records': len(self.df),
            'high_confidence': (self.df['data_confidence'] >= 0.8).sum(),
            'medium_confidence': ((self.df['data_confidence'] >= 0.5) & (self.df['data_confidence'] < 0.8)).sum(),
            'low_confidence': (self.df['data_confidence'] < 0.5).sum(),
            'avg_confidence': self.df['data_confidence'].mean(),
            'lessons_with_topics': self.df['lesson_topic'].notna().sum(),
            'topic_coverage': self.df['lesson_topic'].notna().sum() / len(self.df) * 100,
            'complete_records': ((self.df['lesson_topic'].notna()) & 
                               (self.df['progress_status'] != 'Unknown') &
                               (self.df['data_confidence'] >= 0.5)).sum()
        }
        
        quality['quality_score'] = (
            quality['high_confidence'] * 1.0 +
            quality['medium_confidence'] * 0.65 +
            quality['low_confidence'] * 0.3
        ) / quality['total_records']
        
        return quality
    
    def calculate_temporal_metrics(self):
        """Time-based trends"""
        # Convert dates
        self.df['session_date'] = pd.to_datetime(self.df['session_date'])
        
        # Weekly attendance
        weekly_attendance = self.df.groupby([
            pd.Grouper(key='session_date', freq='W'),
            'attendance_status'
        ]).size().unstack(fill_value=0)
        
        # Monthly progress
        monthly_progress = self.df.groupby([
            pd.Grouper(key='session_date', freq='M'),
            'progress_status'
        ]).size().unstack(fill_value=0)
        
        # Trend analysis
        recent_30_days = self.df[self.df['session_date'] >= (datetime.now() - timedelta(days=30))]
        previous_30_days = self.df[
            (self.df['session_date'] >= (datetime.now() - timedelta(days=60))) &
            (self.df['session_date'] < (datetime.now() - timedelta(days=30)))
        ]
        
        trends = {
            'attendance_trend': 'improving' if len(recent_30_days) > len(previous_30_days) else 'declining',
            'recent_attendance_rate': (recent_30_days['attendance_status'] == 'Attended').mean() if len(recent_30_days) > 0 else 0,
            'active_students_30d': recent_30_days['student_id'].nunique() if len(recent_30_days) > 0 else 0,
            'sessions_last_7d': len(self.df[self.df['session_date'] >= (datetime.now() - timedelta(days=7))]),
            'weekly_avg': len(self.df) / ((self.df['session_date'].max() - self.df['session_date'].min()).days / 7) if len(self.df) > 0 else 0
        }
        
        return trends
    
    def max_consecutive(self, series):
        """Calculate maximum consecutive True values"""
        max_count = 0
        current_count = 0
        
        for val in series:
            if val:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count
    
    def generate_report(self):
        """Generate comprehensive metrics report"""
        report = f"""
# Derived Metrics Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📊 Overall Statistics
- Total Records: {len(self.df):,}
- Unique Students: {self.df['student_id'].nunique()}
- Unique Teachers: {self.df['session_teacher'].nunique()}
- Programs: {', '.join(self.df['program_code'].unique()[:10])}

## 🎓 Student Performance
Top Performers (by completion rate):
"""
        
        # Add top students
        student_metrics = self.metrics.get('student_metrics', {})
        top_students = sorted(student_metrics.items(), 
                            key=lambda x: x[1]['completion_rate'], 
                            reverse=True)[:5]
        
        for student_id, metrics in top_students:
            report += f"- {student_id}: {metrics['completion_rate']:.1%} completion, {metrics['attendance_rate']:.1%} attendance\n"
        
        report += "\n## ⚠️ At-Risk Students\n"
        for student in self.metrics.get('risk_flags', [])[:5]:
            report += f"- {student['student_id']} ({student['risk_level']}): {', '.join(student['reasons'])}\n"
        
        report += "\n## 👩‍🏫 Teacher Effectiveness\n"
        teacher_metrics = self.metrics.get('teacher_metrics', {})
        for teacher, metrics in sorted(teacher_metrics.items(), 
                                      key=lambda x: x[1]['completion_rate'], 
                                      reverse=True)[:5]:
            report += f"- {teacher}: {metrics['completion_rate']:.1%} completion rate, {metrics['students_taught']} students\n"
        
        report += "\n## 📈 Data Quality\n"
        quality = self.metrics.get('quality_metrics', {})
        report += f"- Overall Quality Score: {quality.get('quality_score', 0):.3f}\n"
        report += f"- High Confidence Records: {quality.get('high_confidence', 0):,} ({quality.get('high_confidence', 0)/quality.get('total_records', 1)*100:.1f}%)\n"
        report += f"- Topic Coverage: {quality.get('topic_coverage', 0):.1f}%\n"
        
        return report

if __name__ == "__main__":
    # Load core parameters
    core_df = pd.read_csv("data/core_params/telebort_core_params_20250809.csv")
    
    # Calculate metrics
    calculator = DerivedMetricsCalculator(core_df)
    metrics = calculator.calculate_all_metrics()
    
    # Generate report
    report = calculator.generate_report()
    
    # Save metrics
    import json
    with open("data/core_params/derived_metrics.json", 'w') as f:
        # Convert non-serializable objects
        serializable_metrics = json.loads(json.dumps(metrics, default=str))
        json.dump(serializable_metrics, f, indent=2)
    
    # Save report
    with open("data/core_params/metrics_report.md", 'w') as f:
        f.write(report)
    
    print("✅ Metrics calculated and saved!")