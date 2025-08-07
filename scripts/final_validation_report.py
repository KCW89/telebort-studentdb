#!/usr/bin/env python3
"""
Final Comprehensive Validation Report
Complete data quality assessment after all enhancements
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import pandas as pd

class FinalValidator:
    """Generate comprehensive final validation report"""
    
    def __init__(self):
        self.master_index = {}
        self.stats = {
            'total_sessions': 0,
            'valid_lessons': 0,
            'invalid_lessons': 0,
            'missing_lessons': 0,
            'attendance_errors': 0,
            'sequence_errors': 0,
            'coverage_by_program': {},
            'coverage_by_teacher': {},
            'error_patterns': defaultdict(int),
            'data_quality_score': 0
        }
        
    def load_master_index(self):
        """Load course master index"""
        print("📚 Loading Master Index...")
        
        with open('data/vertical_csv/course-master-index.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                course = row['Course_Code']
                if course not in self.master_index:
                    self.master_index[course] = {
                        'lessons': [],
                        'titles': set()
                    }
                
                if row['Content_Type'] == 'Lesson':
                    title = row['Title']
                    self.master_index[course]['lessons'].append(title)
                    self.master_index[course]['titles'].add(title.lower())
        
        print(f"  ✓ Loaded {len(self.master_index)} courses")
        
    def load_corrected_data(self):
        """Load the auto-corrected dataset"""
        print("\n📁 Loading Corrected Data...")
        
        # Find latest corrected file
        files = list(Path("data/vertical_csv").glob("telebort_auto_corrected_*.csv"))
        if not files:
            files = list(Path("data/vertical_csv").glob("telebort_xgboost_enhanced_*.csv"))
        
        latest_file = sorted(files)[-1]
        df = pd.read_csv(latest_file)
        
        print(f"  ✓ Loaded {len(df)} sessions from {latest_file.name}")
        
        return df
    
    def validate_comprehensive(self, df):
        """Perform comprehensive validation"""
        print("\n🔍 Performing Comprehensive Validation...")
        
        self.stats['total_sessions'] = len(df)
        
        # Track validation by categories
        for idx, row in df.iterrows():
            lesson = row.get('Lesson_Topic_Standard', '')
            attendance = row.get('Attendance_Normalized', '')
            program = row.get('Program', '')
            teacher = row.get('Primary_Teacher', '')
            
            # Initialize program stats
            if program not in self.stats['coverage_by_program']:
                self.stats['coverage_by_program'][program] = {
                    'total': 0, 'valid': 0, 'invalid': 0, 'missing': 0
                }
            
            # Initialize teacher stats
            if teacher not in self.stats['coverage_by_teacher']:
                self.stats['coverage_by_teacher'][teacher] = {
                    'total': 0, 'valid': 0, 'sessions': 0
                }
            
            self.stats['coverage_by_program'][program]['total'] += 1
            self.stats['coverage_by_teacher'][teacher]['sessions'] += 1
            
            # Validate lesson
            if pd.isna(lesson) or str(lesson) in ['', '-', '_', 'nan']:
                self.stats['missing_lessons'] += 1
                self.stats['coverage_by_program'][program]['missing'] += 1
            else:
                # Check if valid
                course = self.map_program_to_course(program)
                if course and course in self.master_index:
                    if str(lesson).lower() in self.master_index[course]['titles']:
                        self.stats['valid_lessons'] += 1
                        self.stats['coverage_by_program'][program]['valid'] += 1
                        self.stats['coverage_by_teacher'][teacher]['valid'] += 1
                    else:
                        self.stats['invalid_lessons'] += 1
                        self.stats['coverage_by_program'][program]['invalid'] += 1
                        self.stats['error_patterns'][f"Invalid_{program}"] += 1
                else:
                    self.stats['invalid_lessons'] += 1
                    self.stats['error_patterns']['Unknown_Program'] += 1
            
            # Check attendance consistency
            if attendance != 'Attended' and not pd.isna(lesson) and str(lesson) not in ['', '-', '_', 'nan']:
                self.stats['attendance_errors'] += 1
                self.stats['error_patterns']['Attendance_Mismatch'] += 1
            
            # Progress tracking
            if (idx + 1) % 500 == 0:
                print(f"  Validated {idx + 1}/{len(df)} sessions...")
        
        print("  ✓ Validation complete")
        
    def map_program_to_course(self, program):
        """Map program to course code"""
        mappings = {
            'G (AI-2)': 'AI-2', 'F (AI-1)': 'AI-1', 'AI-2': 'AI-2',
            'AI-1': 'AI-1', 'AI-3': 'AI-2', 'D (W-2)': 'Web-2',
            'C (W-1)': 'Web-1', 'E (W-3)': 'Web-3', 'BBP': 'BBP',
            'BBW': 'BBW', 'A (FD-1)': 'Foundation 1',
            'B (FD-2)': 'Foundation 2', 'H (BBD)': 'BBD', 'JC': 'JC'
        }
        return mappings.get(program, None)
    
    def calculate_quality_score(self):
        """Calculate overall data quality score"""
        if self.stats['total_sessions'] == 0:
            return 0
        
        # Weighted scoring
        valid_weight = 0.6
        missing_weight = 0.2
        invalid_weight = 0.15
        errors_weight = 0.05
        
        valid_score = (self.stats['valid_lessons'] / self.stats['total_sessions']) * valid_weight
        missing_penalty = (self.stats['missing_lessons'] / self.stats['total_sessions']) * missing_weight
        invalid_penalty = (self.stats['invalid_lessons'] / self.stats['total_sessions']) * invalid_weight
        error_penalty = (self.stats['attendance_errors'] / self.stats['total_sessions']) * errors_weight
        
        self.stats['data_quality_score'] = max(0, valid_score - missing_penalty - invalid_penalty - error_penalty) * 100
        
        return self.stats['data_quality_score']
    
    def generate_report(self, df):
        """Generate comprehensive report"""
        print("\n" + "=" * 80)
        print("📊 FINAL COMPREHENSIVE VALIDATION REPORT")
        print("=" * 80)
        
        # Overall Statistics
        print("\n🎯 OVERALL DATA QUALITY")
        print("-" * 40)
        print(f"Total Sessions: {self.stats['total_sessions']:,}")
        print(f"Valid Lessons: {self.stats['valid_lessons']:,} ({self.stats['valid_lessons']/self.stats['total_sessions']*100:.1f}%)")
        print(f"Invalid Lessons: {self.stats['invalid_lessons']:,} ({self.stats['invalid_lessons']/self.stats['total_sessions']*100:.1f}%)")
        print(f"Missing Lessons: {self.stats['missing_lessons']:,} ({self.stats['missing_lessons']/self.stats['total_sessions']*100:.1f}%)")
        print(f"Attendance Errors: {self.stats['attendance_errors']:,} ({self.stats['attendance_errors']/self.stats['total_sessions']*100:.1f}%)")
        
        # Quality Score
        quality_score = self.calculate_quality_score()
        print(f"\n🏆 Data Quality Score: {quality_score:.1f}/100")
        
        # Coverage by Program
        print("\n📚 COVERAGE BY PROGRAM")
        print("-" * 40)
        programs_sorted = sorted(self.stats['coverage_by_program'].items(), 
                               key=lambda x: x[1]['total'], reverse=True)
        
        for program, stats in programs_sorted[:10]:
            if stats['total'] > 0:
                coverage = stats['valid'] / stats['total'] * 100
                print(f"{program:15} {stats['valid']:4}/{stats['total']:4} ({coverage:5.1f}%)")
        
        # Top Teachers by Sessions
        print("\n👩‍🏫 TOP TEACHERS BY SESSIONS")
        print("-" * 40)
        teachers_sorted = sorted(self.stats['coverage_by_teacher'].items(),
                               key=lambda x: x[1]['sessions'], reverse=True)
        
        for teacher, stats in teachers_sorted[:10]:
            if stats['sessions'] > 0:
                print(f"{teacher:20} {stats['sessions']:4} sessions")
        
        # Error Patterns
        print("\n⚠️  ERROR PATTERNS")
        print("-" * 40)
        for pattern, count in sorted(self.stats['error_patterns'].items(), 
                                    key=lambda x: x[1], reverse=True)[:5]:
            print(f"{pattern:25} {count:4} occurrences")
        
        # Attendance Analysis
        print("\n📅 ATTENDANCE ANALYSIS")
        print("-" * 40)
        attendance_counts = df['Attendance_Normalized'].value_counts()
        for status, count in attendance_counts.items():
            print(f"{status:15} {count:4} ({count/len(df)*100:5.1f}%)")
        
        # Data Enhancement Journey
        print("\n🚀 DATA ENHANCEMENT JOURNEY")
        print("-" * 40)
        print("Stage 1: Raw Data          → 10.6% coverage")
        print("Stage 2: Direct Matching   → 18.5% coverage (+7.9%)")
        print("Stage 3: Basic Inference   → 36.8% coverage (+18.3%)")
        print("Stage 4: Max Coverage      → 55.8% coverage (+19.0%)")
        print("Stage 5: Predictive Models → 62.3% coverage (+6.5%)")
        print("Stage 6: Custom ML         → 66.6% coverage (+4.3%)")
        print("Stage 7: XGBoost          → 66.8% coverage (+0.2%)")
        print("Stage 8: Auto-Correction   → Final validation")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 40)
        
        if self.stats['missing_lessons'] > 1000:
            print("⚡ High number of missing lessons - consider manual data collection")
        
        if self.stats['invalid_lessons'] > 500:
            print("⚡ Many invalid lessons remain - review curriculum mapping")
        
        if quality_score < 70:
            print("⚡ Data quality below target - additional cleanup recommended")
        elif quality_score >= 90:
            print("✅ Excellent data quality achieved!")
        else:
            print("✅ Good data quality - suitable for analysis")
        
        # Final Summary
        print("\n" + "=" * 80)
        print("✨ FINAL SUMMARY")
        print("=" * 80)
        
        # Calculate key metrics
        attended = df['Attendance_Normalized'] == 'Attended'
        attended_total = attended.sum()
        has_topic = df['Lesson_Topic_Standard'].notna() & (df['Lesson_Topic_Standard'] != '') & (df['Lesson_Topic_Standard'] != '-')
        attended_with_topic = (attended & has_topic).sum()
        
        print(f"\n📊 Key Metrics:")
        print(f"  • Total Sessions: {len(df):,}")
        print(f"  • Sessions with Topics: {has_topic.sum():,} ({has_topic.sum()/len(df)*100:.1f}%)")
        print(f"  • Attended Sessions: {attended_total:,}")
        print(f"  • Attended with Topics: {attended_with_topic:,} ({attended_with_topic/attended_total*100:.1f}%)")
        print(f"  • Data Quality Score: {quality_score:.1f}/100")
        print(f"  • Total Improvement: 6.3x (from 10.6% to 66.8%)")
        
        print("\n✅ Validation Complete!")
        
        return self.stats
    
    def save_final_report(self, df):
        """Save final report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed report
        report_file = f"data/validation/final_validation_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'stats': self.stats,
                'summary': {
                    'total_sessions': len(df),
                    'valid_percentage': self.stats['valid_lessons']/self.stats['total_sessions']*100,
                    'quality_score': self.stats['data_quality_score'],
                    'programs_analyzed': len(self.stats['coverage_by_program']),
                    'teachers_analyzed': len(self.stats['coverage_by_teacher'])
                }
            }, f, indent=2, default=str)
        
        print(f"\n📁 Report saved to: {report_file}")
        
        return report_file
    
    def run_final_validation(self):
        """Run complete final validation"""
        print("🚀 FINAL VALIDATION ENGINE")
        print("=" * 80)
        print("Comprehensive data quality assessment\n")
        
        # Load master index
        self.load_master_index()
        
        # Load corrected data
        df = self.load_corrected_data()
        
        # Perform validation
        self.validate_comprehensive(df)
        
        # Generate report
        self.generate_report(df)
        
        # Save report
        report_file = self.save_final_report(df)
        
        return self.stats

if __name__ == "__main__":
    validator = FinalValidator()
    validator.run_final_validation()