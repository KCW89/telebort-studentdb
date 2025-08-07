#!/usr/bin/env python3
"""
Auto-Correction Engine
Apply suggested corrections from validation report to fix lesson topics
"""

import csv
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

class AutoCorrector:
    """Apply auto-corrections to invalid lessons"""
    
    def __init__(self):
        self.corrections_applied = 0
        self.corrections_log = []
        
    def load_validation_report(self):
        """Load the latest validation report"""
        print("📋 Loading Validation Report...")
        
        # Find latest validation report
        validation_dir = Path("data/validation")
        invalid_files = list(validation_dir.glob("invalid_lessons_*.csv"))
        
        if not invalid_files:
            print("❌ No validation reports found!")
            return None
            
        latest_invalid = sorted(invalid_files)[-1]
        print(f"  Using: {latest_invalid.name}")
        
        # Load invalid entries
        invalid_entries = []
        with open(latest_invalid, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            invalid_entries = list(reader)
        
        print(f"  Loaded {len(invalid_entries)} invalid entries")
        
        # Filter for auto-correctable entries
        correctable = [e for e in invalid_entries if e.get('suggested_correction')]
        print(f"  Auto-correctable: {len(correctable)} entries")
        
        return correctable
    
    def load_current_data(self):
        """Load the current enhanced dataset"""
        print("\n📁 Loading Current Dataset...")
        
        # Find latest enhanced file
        files = list(Path("data/vertical_csv").glob("telebort_xgboost_enhanced_*.csv"))
        if not files:
            files = list(Path("data/vertical_csv").glob("telebort_ml_enhanced_*.csv"))
        
        latest_file = sorted(files)[-1]
        print(f"  Using: {latest_file.name}")
        
        df = pd.read_csv(latest_file)
        print(f"  Loaded {len(df)} sessions")
        
        return df, latest_file
    
    def apply_corrections(self, df, corrections):
        """Apply corrections to the dataframe"""
        print("\n🔧 Applying Auto-Corrections...")
        
        for correction in corrections:
            # Find matching row
            mask = (
                (df['Student_ID'] == correction['student_id']) &
                (df['Session_Date'] == correction['date']) &
                (df['Lesson_Topic_Standard'] == correction['lesson_standard'])
            )
            
            matching_rows = df[mask]
            
            if len(matching_rows) > 0:
                # Apply correction
                df.loc[mask, 'Lesson_Topic_Standard'] = correction['suggested_correction']
                df.loc[mask, 'Inference_Method'] = 'auto_corrected'
                df.loc[mask, 'Inference_Status'] = 'Corrected'
                df.loc[mask, 'Inference_Confidence'] = '1.0'
                
                self.corrections_applied += len(matching_rows)
                
                # Log correction
                self.corrections_log.append({
                    'student': correction['student'],
                    'student_id': correction['student_id'],
                    'date': correction['date'],
                    'old_value': correction['lesson_standard'],
                    'new_value': correction['suggested_correction'],
                    'reason': correction['reason']
                })
                
                # Progress indicator
                if self.corrections_applied % 50 == 0:
                    print(f"  Applied {self.corrections_applied} corrections...")
        
        print(f"\n✅ Total corrections applied: {self.corrections_applied}")
        
        return df
    
    def save_corrected_data(self, df):
        """Save the corrected dataset"""
        print("\n💾 Saving Corrected Data...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/vertical_csv/telebort_auto_corrected_{timestamp}.csv"
        
        df.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file}")
        
        # Save correction log
        log_file = f"data/validation/corrections_log_{timestamp}.json"
        with open(log_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'corrections_applied': self.corrections_applied,
                'corrections': self.corrections_log[:20]  # Sample of corrections
            }, f, indent=2)
        
        print(f"  Log saved to: {log_file}")
        
        return output_file
    
    def calculate_new_coverage(self, df):
        """Calculate coverage after corrections"""
        print("\n📊 New Coverage Statistics:")
        
        total = len(df)
        has_topic = df['Lesson_Topic_Standard'].notna() & (df['Lesson_Topic_Standard'] != '') & (df['Lesson_Topic_Standard'] != '-')
        topic_count = has_topic.sum()
        
        attended = df['Attendance_Normalized'] == 'Attended'
        attended_total = attended.sum()
        attended_with_topic = (attended & has_topic).sum()
        
        print(f"  Total Coverage: {topic_count}/{total} ({topic_count/total*100:.1f}%)")
        print(f"  Attended Coverage: {attended_with_topic}/{attended_total} ({attended_with_topic/attended_total*100:.1f}%)")
        
        # Calculate improvement
        print("\n📈 Improvement from Auto-Correction:")
        print(f"  Sessions corrected: {self.corrections_applied}")
        print(f"  Coverage gain: +{self.corrections_applied/total*100:.2f}%")
        
        return {
            'total_coverage': topic_count/total*100,
            'attended_coverage': attended_with_topic/attended_total*100,
            'corrections_applied': self.corrections_applied
        }
    
    def run_auto_correction(self):
        """Run the complete auto-correction process"""
        print("🚀 AUTO-CORRECTION ENGINE")
        print("=" * 70)
        print("Applying validated corrections to improve data quality\n")
        
        # Load validation report
        corrections = self.load_validation_report()
        if not corrections:
            return
        
        # Load current data
        df, source_file = self.load_current_data()
        
        # Apply corrections
        df = self.apply_corrections(df, corrections)
        
        # Save corrected data
        output_file = self.save_corrected_data(df)
        
        # Calculate new coverage
        stats = self.calculate_new_coverage(df)
        
        print("\n" + "=" * 70)
        print("✨ Auto-Correction Complete!")
        print(f"📁 Corrected data: {output_file}")
        print(f"📊 Final Coverage: {stats['total_coverage']:.1f}%")
        print(f"✅ Corrections Applied: {stats['corrections_applied']}")
        
        return output_file, stats

if __name__ == "__main__":
    corrector = AutoCorrector()
    corrector.run_auto_correction()