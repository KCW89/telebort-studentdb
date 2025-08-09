#!/usr/bin/env python3
"""
Core Parameter Consolidation Script
Transforms 24 parameters to 10 essential parameters
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import re

class CoreParameterConsolidator:
    """Consolidate 24 params to 10 core params"""
    
    def __init__(self):
        self.stats = {
            'total_records': 0,
            'consolidated': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0
        }
    
    def consolidate_parameters(self, df):
        """Transform 24 params to 10 core params"""
        
        core_df = pd.DataFrame()
        
        # WHO (Identity) - 3 params
        core_df['student_id'] = df['Student_ID']
        core_df['primary_teacher'] = df['Primary_Teacher']
        core_df['session_teacher'] = df['Session_Teacher'].fillna(df['Primary_Teacher'])
        
        # WHAT (Content) - 2 params
        core_df['lesson_topic'] = self.consolidate_lesson_topic(df)
        core_df['progress_status'] = self.consolidate_progress(df)
        
        # WHEN (Temporal) - 2 params
        core_df['session_date'] = pd.to_datetime(df['Session_Date'])
        core_df['session_sequence'] = self.calculate_sequence(df)
        
        # WHERE (Program) - 1 param
        core_df['program_code'] = self.standardize_program(df)
        
        # HOW (Engagement) - 2 params
        core_df['attendance_status'] = df['Attendance_Normalized']
        core_df['data_confidence'] = self.calculate_confidence(df)
        
        # Update stats
        self.stats['total_records'] = len(core_df)
        self.stats['consolidated'] = len(core_df)
        self.stats['high_confidence'] = (core_df['data_confidence'] >= 0.8).sum()
        self.stats['medium_confidence'] = ((core_df['data_confidence'] >= 0.5) & (core_df['data_confidence'] < 0.8)).sum()
        self.stats['low_confidence'] = (core_df['data_confidence'] < 0.5).sum()
        
        return core_df
    
    def consolidate_lesson_topic(self, df):
        """Choose best available lesson topic"""
        topics = []
        
        for idx, row in df.iterrows():
            # Priority: Standard > Original > Constructed
            if pd.notna(row.get('Lesson_Topic_Standard')) and str(row['Lesson_Topic_Standard']).strip():
                topic = str(row['Lesson_Topic_Standard'])
            elif pd.notna(row.get('Lesson_Topic_Original')) and str(row['Lesson_Topic_Original']).strip():
                topic = str(row['Lesson_Topic_Original'])
            elif pd.notna(row.get('Lesson_Type')) and pd.notna(row.get('Lesson_ID')):
                topic = f"{row['Lesson_Type']} {row['Lesson_ID']}"
            else:
                topic = None
            
            topics.append(topic)
        
        return pd.Series(topics)
    
    def consolidate_progress(self, df):
        """Standardize progress status"""
        progress_map = {
            'Completed': 'Completed',
            'In Progress': 'InProgress', 
            'Not Started': 'NotStarted',
            'Graduated': 'Completed',
            'In Break': 'NotStarted',
            'Off': 'NotStarted'
        }
        
        progress = []
        for idx, row in df.iterrows():
            # Priority: Inferred > Original
            status = row.get('Progress_Inferred', row.get('Progress', 'Unknown'))
            
            # Standardize
            if pd.isna(status) or str(status).strip() in ['', '-', '_']:
                # Infer from attendance
                if row.get('Attendance_Normalized') == 'Attended':
                    status = 'InProgress'
                else:
                    status = 'NotStarted'
            else:
                status = progress_map.get(str(status), 'Unknown')
            
            progress.append(status)
        
        return pd.Series(progress)
    
    def calculate_sequence(self, df):
        """Calculate session sequence number"""
        sequences = []
        
        for idx, row in df.iterrows():
            # Try to extract from Session_Number
            session_num = row.get('Session_Number', '')
            
            if pd.notna(session_num):
                # Extract number from strings like 'S1', '1', 'Session 1'
                match = re.search(r'\d+', str(session_num))
                if match:
                    sequences.append(int(match.group()))
                else:
                    sequences.append(0)
            else:
                # Calculate from date order (would need groupby student)
                sequences.append(0)
        
        return pd.Series(sequences)
    
    def standardize_program(self, df):
        """Standardize program codes"""
        program_map = {
            'G (AI-2)': 'AI-2',
            'F (AI-1)': 'AI-1',
            'E (W-3)': 'W-3',
            'D (W-2)': 'W-2',
            'C (W-1)': 'W-1',
            'H (BBD)': 'BBD',
            'A (FD-1)': 'FD-1',
            'B (FD-2)': 'FD-2',
            'BBP': 'BBP',
            'BBW': 'BBW',
            'JC': 'JC',
            'AI-1': 'AI-1',
            'AI-2': 'AI-2',
            'AI-3': 'AI-2'  # Map AI-3 to AI-2
        }
        
        programs = []
        for idx, row in df.iterrows():
            prog = row.get('Program', row.get('Course_Code', ''))
            
            # Direct mapping
            if prog in program_map:
                programs.append(program_map[prog])
            else:
                # Try to extract code from string
                for key, value in program_map.items():
                    if key in str(prog):
                        programs.append(value)
                        break
                else:
                    programs.append(str(prog))
        
        return pd.Series(programs)
    
    def calculate_confidence(self, df):
        """Calculate data confidence score (0.0-1.0)"""
        confidences = []
        
        for idx, row in df.iterrows():
            score = 0.0
            weights = {
                'has_topic': 0.3,
                'has_progress': 0.2,
                'ml_confidence': 0.2,
                'validation': 0.15,
                'attendance': 0.15
            }
            
            # Has lesson topic
            if pd.notna(row.get('Lesson_Topic_Standard')) and str(row['Lesson_Topic_Standard']).strip():
                score += weights['has_topic']
            elif pd.notna(row.get('Lesson_Topic_Original')) and str(row['Lesson_Topic_Original']).strip():
                score += weights['has_topic'] * 0.7
            
            # Has progress
            if pd.notna(row.get('Progress_Inferred')) and str(row['Progress_Inferred']) != 'Unknown':
                score += weights['has_progress']
            elif pd.notna(row.get('Progress')) and str(row['Progress']) != 'Unknown':
                score += weights['has_progress'] * 0.7
            
            # ML confidence
            if pd.notna(row.get('Inference_Confidence')):
                try:
                    ml_conf = float(row['Inference_Confidence'])
                    score += ml_conf * weights['ml_confidence']
                except:
                    pass
            
            # Validation status
            if row.get('Inference_Status') == 'Corrected':
                score += weights['validation']
            elif row.get('Inference_Method') == 'direct_match':
                score += weights['validation'] * 0.9
            
            # Attendance consistency
            if row.get('Attendance_Normalized') in ['Attended', 'Absent', 'No Class']:
                score += weights['attendance']
            
            confidences.append(round(min(score, 1.0), 3))
        
        return pd.Series(confidences)
    
    def generate_summary(self):
        """Generate consolidation summary"""
        summary = f"""
# Core Parameter Consolidation Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Processing Statistics
- Total Records: {self.stats['total_records']:,}
- Successfully Consolidated: {self.stats['consolidated']:,}
- High Confidence (≥0.8): {self.stats['high_confidence']:,} ({self.stats['high_confidence']/self.stats['total_records']*100:.1f}%)
- Medium Confidence (0.5-0.8): {self.stats['medium_confidence']:,} ({self.stats['medium_confidence']/self.stats['total_records']*100:.1f}%)
- Low Confidence (<0.5): {self.stats['low_confidence']:,} ({self.stats['low_confidence']/self.stats['total_records']*100:.1f}%)

## Parameter Reduction
- Original Parameters: 24
- Core Parameters: 10
- Reduction: 58.3%

## Data Quality
- Overall Confidence: {(self.stats['high_confidence'] + self.stats['medium_confidence']*0.65 + self.stats['low_confidence']*0.3) / self.stats['total_records']:.3f}
"""
        return summary
    
    def process_file(self, input_file, output_file=None):
        """Process a CSV file and consolidate parameters"""
        print(f"📊 Processing: {input_file}")
        
        # Load data
        df = pd.read_csv(input_file)
        print(f"  Loaded {len(df)} records")
        
        # Consolidate
        core_df = self.consolidate_parameters(df)
        print(f"  Consolidated to 10 core parameters")
        
        # Save output
        if output_file is None:
            output_file = f"data/core_params/consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Ensure directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        core_df.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file}")
        
        # Generate summary
        summary = self.generate_summary()
        summary_file = output_file.replace('.csv', '_summary.md')
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"  Summary saved to: {summary_file}")
        
        return core_df, self.stats

if __name__ == "__main__":
    consolidator = CoreParameterConsolidator()
    
    # Process the latest enhanced file
    input_file = "data/vertical_csv/telebort_auto_corrected_20250807_100650.csv"
    output_file = "data/core_params/telebort_core_params_20250809.csv"
    
    core_df, stats = consolidator.process_file(input_file, output_file)
    
    print("\n✅ Consolidation Complete!")
    print(f"📊 Data Quality: {stats['high_confidence']}/{stats['total_records']} high confidence records")