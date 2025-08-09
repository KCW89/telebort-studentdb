#!/usr/bin/env python3
"""
Push 10-Parameter Model to Google Sheets
Using MCP Zapier integration
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class GoogleSheetsUploader:
    """Upload core parameters to Google Sheets"""
    
    def __init__(self):
        self.spreadsheet_id = None
        self.dashboard_data = []
    
    def prepare_upload_data(self, core_df):
        """Prepare data for Google Sheets upload"""
        
        # Calculate dashboard metrics
        self.dashboard_data = [
            ['Metric', 'Value', 'Percentage', 'Status', 'Last Updated'],
            ['Total Sessions', len(core_df), '100%', '📊', datetime.now().strftime('%Y-%m-%d %H:%M')],
            ['Unique Students', core_df['student_id'].nunique(), '', '👥', ''],
            ['Unique Teachers', core_df['session_teacher'].nunique(), '', '👩‍🏫', ''],
            ['High Confidence', (core_df['data_confidence'] >= 0.8).sum(), 
             f"{(core_df['data_confidence'] >= 0.8).sum()/len(core_df)*100:.1f}%", 
             '⭐' if (core_df['data_confidence'] >= 0.8).sum()/len(core_df) > 0.6 else '⚠️', ''],
            ['Attended Sessions', (core_df['attendance_status'] == 'Attended').sum(),
             f"{(core_df['attendance_status'] == 'Attended').sum()/len(core_df)*100:.1f}%", '✅', ''],
            ['Lessons Completed', (core_df['progress_status'] == 'Completed').sum(),
             f"{(core_df['progress_status'] == 'Completed').sum()/len(core_df)*100:.1f}%", '🎓', ''],
            ['At Risk Students', self.count_at_risk(core_df), '', '⚠️', ''],
            ['Data Quality Score', round(core_df['data_confidence'].mean(), 3), 
             f"{core_df['data_confidence'].mean()*100:.1f}%", 
             '✅' if core_df['data_confidence'].mean() > 0.7 else '⚠️', '']
        ]
        
        # Prepare main data for upload (limit columns for Google Sheets)
        upload_df = core_df[['student_id', 'session_date', 'program_code', 
                            'lesson_topic', 'progress_status', 'attendance_status',
                            'session_teacher', 'data_confidence']].copy()
        
        # Format data confidence as percentage
        upload_df['data_confidence'] = upload_df['data_confidence'].apply(lambda x: f"{x*100:.0f}%")
        
        # Add quality indicator
        upload_df['quality'] = core_df['data_confidence'].apply(self.get_quality_indicator)
        
        return upload_df
    
    def count_at_risk(self, df):
        """Count at-risk students"""
        at_risk = 0
        for student_id in df['student_id'].unique():
            student_data = df[df['student_id'] == student_id]
            
            # Check for consecutive absences
            absences = 0
            for status in student_data.sort_values('session_date')['attendance_status']:
                if status == 'Absent':
                    absences += 1
                    if absences >= 3:
                        at_risk += 1
                        break
                else:
                    absences = 0
        
        return at_risk
    
    def get_quality_indicator(self, confidence):
        """Get quality indicator emoji"""
        if confidence >= 0.8:
            return '⭐'
        elif confidence >= 0.5:
            return '🔶'
        else:
            return '⚠️'
    
    def generate_mcp_instructions(self, upload_df):
        """Generate MCP instructions for upload"""
        
        instructions = f"""
# MCP Upload Instructions for 10-Parameter Model

## Step 1: Create Spreadsheet
Use: mcp__zapier__google_sheets_create_spreadsheet
Title: Telebort_Core_Params_{datetime.now().strftime('%Y%m%d')}
Headers: student_id,session_date,program_code,lesson_topic,progress_status,attendance_status,session_teacher,data_confidence,quality

## Step 2: Add Main Data (in batches of 100)
Total rows to upload: {len(upload_df)}

## Step 3: Create Dashboard Sheet
Use: mcp__zapier__google_sheets_create_worksheet
Title: Dashboard
Headers: Metric,Value,Percentage,Status,Last_Updated

## Step 4: Add Dashboard Metrics
{len(self.dashboard_data)} rows of metrics

## Step 5: Create At-Risk Students Sheet
Identify and list students with:
- 3+ consecutive absences
- Multiple incomplete lessons
- Low data confidence

## Step 6: Share Spreadsheet
Use: mcp__zapier__google_drive_add_file_sharing_preference
Permission: anyone_with_link_can_view
"""
        
        return instructions
    
    def save_for_upload(self, upload_df):
        """Save data for manual upload if needed"""
        
        # Save main data
        upload_file = f"data/core_params/for_sheets_upload_{datetime.now().strftime('%Y%m%d')}.csv"
        upload_df.to_csv(upload_file, index=False)
        
        # Save dashboard data
        dashboard_file = f"data/core_params/dashboard_data_{datetime.now().strftime('%Y%m%d')}.csv"
        pd.DataFrame(self.dashboard_data[1:], columns=self.dashboard_data[0]).to_csv(dashboard_file, index=False)
        
        print(f"📁 Data saved for upload:")
        print(f"  Main data: {upload_file}")
        print(f"  Dashboard: {dashboard_file}")
        
        return upload_file, dashboard_file

if __name__ == "__main__":
    # Load core parameters
    core_df = pd.read_csv("data/core_params/telebort_core_params_20250809.csv")
    
    # Create uploader
    uploader = GoogleSheetsUploader()
    
    # Prepare data
    upload_df = uploader.prepare_upload_data(core_df)
    
    # Generate instructions
    instructions = uploader.generate_mcp_instructions(upload_df)
    
    # Save for upload
    main_file, dashboard_file = uploader.save_for_upload(upload_df)
    
    # Save instructions
    with open("data/core_params/mcp_upload_instructions.md", 'w') as f:
        f.write(instructions)
    
    print("\n✅ Data prepared for Google Sheets upload!")
    print(f"📊 {len(upload_df)} rows ready")
    print(f"📋 Instructions saved to: data/core_params/mcp_upload_instructions.md")