#!/usr/bin/env python3
"""
run_complete_enhancement.py - Complete enhanced processing with proper data structure adaptation

This script bridges the enhanced processor output to the report generator format.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_data_processor import EnhancedDataProcessor
from process_data import DataProcessor
from generate_reports import ReportGenerator

def adapt_enhanced_to_report_format(enhanced_data: Dict) -> Dict:
    """
    Adapt enhanced processor output to report generator format
    
    Converts from enhanced format to the expected report format with:
    - current_status
    - learning_journey
    - attendance_summary
    - metadata
    """
    
    # Use the standard DataProcessor to format the data properly
    processor = DataProcessor()
    
    # Convert enhanced data back to raw format for processing
    raw_data = {
        'student_id': enhanced_data['student_id'],
        'name': enhanced_data['name'],
        'program': enhanced_data['program'],
        'schedule': enhanced_data['schedule'],
        'teacher': enhanced_data['teacher'],
        'sessions': []
    }
    
    # Convert enhanced sessions to raw format
    for session in enhanced_data.get('sessions', []):
        raw_data['sessions'].append({
            'date': session['date'],
            'session': session['session'],
            'lesson': session.get('lesson_title', ''),
            'attendance': session['attendance'],
            'progress': session['progress']
        })
    
    # Process through standard processor to get proper format
    return processor.process_student(raw_data)

def main():
    """Main execution function"""
    
    print("=" * 60)
    print("COMPLETE ENHANCED DATA PROCESSING")
    print("=" * 60)
    
    # Initialize components
    enhanced_processor = EnhancedDataProcessor()
    report_generator = ReportGenerator()
    
    # Load cached data files
    all_students = []
    data_files = ['sheets_data.json', 'sheets_data_batch2.json', 'sheets_data_batch3.json']
    
    for filename in data_files:
        filepath = os.path.join(os.path.dirname(__file__), '..', filename)
        if os.path.exists(filepath):
            print(f"\nLoading {filename}...")
            with open(filepath, 'r') as f:
                file_data = json.load(f)
                
            # Parse the cached data
            if 'results' in file_data and file_data['results']:
                raw_rows = file_data['results'][0].get('raw_rows', '[]')
                if isinstance(raw_rows, str):
                    rows = json.loads(raw_rows)
                else:
                    rows = raw_rows
                
                # Process each row (skip headers)
                for row_data in rows[3:]:
                    if not row_data or not row_data[1]:  # No student ID
                        continue
                    
                    student = {
                        'student_id': row_data[1] if row_data[1] else '',
                        'name': row_data[0] if row_data[0] else '',
                        'program': row_data[2] if row_data[2] else '',
                        'schedule': f"{row_data[3]} {row_data[4]}-{row_data[5]}" if row_data[3] and row_data[4] and row_data[5] else '-',
                        'teacher': row_data[6] if row_data[6] else '',
                        'sessions': []
                    }
                    
                    # Parse sessions (every 5 columns starting from column 7)
                    for i in range(7, len(row_data), 5):
                        if i + 4 < len(row_data):
                            date = row_data[i] if i < len(row_data) else ''
                            session = row_data[i+1] if i+1 < len(row_data) else ''
                            lesson = row_data[i+2] if i+2 < len(row_data) else ''
                            attendance = row_data[i+3] if i+3 < len(row_data) else ''
                            progress = row_data[i+4] if i+4 < len(row_data) else ''
                            
                            if date and date != '-':
                                student['sessions'].append({
                                    'date': date,
                                    'session': session,
                                    'lesson': lesson,
                                    'attendance': attendance,
                                    'progress': progress
                                })
                    
                    if student['student_id']:
                        all_students.append(student)
    
    print(f"\nLoaded {len(all_students)} students from cached data")
    
    # Apply enhanced cleaning
    print("\nApplying enhanced data cleaning...")
    enhanced_students, quality_metrics = enhanced_processor.process_student_data(all_students)
    
    print("\nData Quality Improvements:")
    print(f"  • Teacher name fixes: {quality_metrics['teacher_name_fixes']}")
    print(f"  • Progress standardizations: {quality_metrics['progress_standardizations']}")
    print(f"  • URL extractions: {quality_metrics['url_extractions']}")
    print(f"  • Missing data handled: {quality_metrics['missing_data_handled']}")
    print(f"  • Invalid sessions fixed: {quality_metrics['invalid_sessions_fixed']}")
    print(f"  • Total improvements: {sum(quality_metrics.values())}")
    
    # Convert and generate reports
    print("\nGenerating reports with cleaned data...")
    
    stats = {
        'generated': 0,
        'updated': 0,
        'errors': 0,
        'error_details': []
    }
    
    for enhanced_student in enhanced_students:
        try:
            # Adapt to report format
            report_data = adapt_enhanced_to_report_format(enhanced_student)
            
            # Generate report
            report_path = report_generator.generate_report(report_data)
            
            if os.path.exists(report_path):
                stats['updated'] += 1
            else:
                stats['generated'] += 1
                
        except Exception as e:
            stats['errors'] += 1
            error_msg = f"Student {enhanced_student['student_id']}: {str(e)}"
            stats['error_details'].append(error_msg)
            print(f"  ❌ Error: {error_msg}")
    
    # Show summary
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    
    print(f"\nFinal Results:")
    print(f"  • Students processed: {len(enhanced_students)}")
    print(f"  • Data quality fixes: {sum(quality_metrics.values())}")
    print(f"  • Reports generated/updated: {stats['generated'] + stats['updated']}")
    print(f"  • Errors: {stats['errors']}")
    
    if stats['error_details']:
        print(f"\nError Details:")
        for error in stats['error_details'][:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    print(f"\n✅ Successfully processed {len(enhanced_students)} students with {sum(quality_metrics.values())} data quality improvements!")
    
    # Show sample report
    sample_report = "reports/s10769.md"
    if os.path.exists(sample_report):
        print(f"\nSample cleaned report: {sample_report}")
        with open(sample_report, 'r') as f:
            lines = f.readlines()[:25]
            print("".join(lines))


if __name__ == "__main__":
    main()