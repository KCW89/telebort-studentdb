#!/usr/bin/env python3
"""
apply_enhanced_cleaning.py - Apply enhanced cleaning to all student reports

This script properly processes all 101 students with enhanced data cleaning.
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
from sync_sheets_mcp import SheetsSyncManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_all_student_data() -> List[Dict]:
    """Load all student data from Google Sheets cache files"""
    all_students = []
    
    # Load from all cache files
    cache_files = [
        'sheets_data.json',
        'sheets_data_batch2.json', 
        'sheets_data_batch3.json'
    ]
    
    for filename in cache_files:
        filepath = os.path.join(os.path.dirname(__file__), '..', filename)
        if os.path.exists(filepath):
            logger.info(f"Loading {filename}...")
            with open(filepath, 'r') as f:
                cache_data = json.load(f)
            
            # Extract rows from cache
            if 'results' in cache_data and cache_data['results']:
                raw_rows = cache_data['results'][0].get('raw_rows', '[]')
                if isinstance(raw_rows, str):
                    rows = json.loads(raw_rows)
                else:
                    rows = raw_rows
                
                # Parse each student row (skip headers)
                for row in rows[3:]:
                    if not row or not row[1]:  # No student ID
                        continue
                    
                    student = parse_student_row(row)
                    if student:
                        all_students.append(student)
    
    # If no cache files, fetch fresh data
    if not all_students:
        logger.info("No cached data found, fetching fresh data...")
        sync_manager = SheetsSyncManager()
        # Fetch all rows from 5 to 112
        for start_row in range(5, 113, 50):
            end_row = min(start_row + 49, 112)
            batch_data = sync_manager.fetch_batch(start_row, end_row)
            
            for student_data in batch_data:
                student = {
                    'student_id': student_data['student_id'],
                    'name': student_data.get('name', ''),
                    'program': student_data.get('program', ''),
                    'schedule': student_data.get('schedule', ''),
                    'teacher': student_data.get('teacher', ''),
                    'sessions': student_data.get('sessions', [])
                }
                all_students.append(student)
    
    return all_students

def parse_student_row(row: List) -> Dict:
    """Parse a single student row from Google Sheets"""
    student = {
        'student_id': row[1],
        'name': row[0] if row[0] else '',
        'program': row[2] if row[2] else '',
        'schedule': f"{row[3]} {row[4]}-{row[5]}" if row[3] and row[4] and row[5] else '-',
        'teacher': row[6] if row[6] else '',
        'sessions': []
    }
    
    # Parse sessions (every 5 columns starting from column 7)
    for i in range(7, len(row), 5):
        if i + 4 < len(row):
            date = row[i] if i < len(row) else ''
            session = row[i+1] if i+1 < len(row) else ''
            lesson = row[i+2] if i+2 < len(row) else ''
            attendance = row[i+3] if i+3 < len(row) else ''
            progress = row[i+4] if i+4 < len(row) else ''
            
            if date and date != '-':
                student['sessions'].append({
                    'date': date,
                    'session': session,
                    'lesson': lesson,
                    'attendance': attendance,
                    'progress': progress
                })
    
    return student

def convert_to_processor_format(enhanced_student: Dict) -> Dict:
    """Convert enhanced student data to processor format"""
    
    # Build info section
    info = {
        'student_id': enhanced_student['student_id'],
        'name': enhanced_student.get('name', ''),
        'program': enhanced_student.get('program', ''),
        'schedule': enhanced_student.get('schedule', ''),
        'teacher': enhanced_student.get('teacher', '')
    }
    
    # Convert sessions - use the cleaned attendance values
    sessions = []
    for session in enhanced_student.get('sessions', []):
        sessions.append({
            'date': session['date'],
            'session': session['session'],
            'lesson': session.get('lesson_title', session.get('lesson_raw', '')),
            'attendance': session['attendance'],  # This should now be "Attended" instead of teacher name
            'progress': session['progress']
        })
    
    return {
        'info': info,
        'sessions': sessions
    }

def main():
    """Main execution"""
    
    print("=" * 70)
    print("APPLYING ENHANCED DATA CLEANING TO ALL STUDENT REPORTS")
    print("=" * 70)
    
    # Load all student data
    logger.info("Loading student data...")
    all_students = load_all_student_data()
    logger.info(f"Loaded {len(all_students)} students")
    
    # Apply enhanced cleaning
    logger.info("Applying enhanced data cleaning...")
    enhanced_processor = EnhancedDataProcessor()
    enhanced_students, quality_metrics = enhanced_processor.process_student_data(all_students)
    
    print("\n" + "=" * 50)
    print("DATA QUALITY IMPROVEMENTS APPLIED:")
    print("=" * 50)
    print(f"  • Teacher names → 'Attended': {quality_metrics['teacher_name_fixes']}")
    print(f"  • Progress standardized: {quality_metrics['progress_standardizations']}")
    print(f"  • URLs extracted: {quality_metrics['url_extractions']}")
    print(f"  • Missing data handled: {quality_metrics['missing_data_handled']}")
    print(f"  • Invalid sessions fixed: {quality_metrics['invalid_sessions_fixed']}")
    print(f"  • TOTAL FIXES: {sum(quality_metrics.values())}")
    print("=" * 50)
    
    # Process and generate reports
    logger.info("Generating reports with cleaned data...")
    data_processor = DataProcessor()
    report_generator = ReportGenerator()
    
    stats = {'generated': 0, 'errors': 0, 'error_list': []}
    
    for enhanced_student in enhanced_students:
        try:
            # Convert to processor format
            processor_data = convert_to_processor_format(enhanced_student)
            
            # Process the data
            processed_data = data_processor.process_student(processor_data)
            
            # Generate report
            report_path = report_generator.generate_report(processed_data)
            stats['generated'] += 1
            
            # Show progress every 10 students
            if stats['generated'] % 10 == 0:
                print(f"  ✓ Generated {stats['generated']} reports...")
                
        except Exception as e:
            stats['errors'] += 1
            error_msg = f"Student {enhanced_student['student_id']}: {str(e)}"
            stats['error_list'].append(error_msg)
            logger.error(error_msg)
    
    # Final summary
    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Final Results:")
    print(f"  • Students processed: {len(enhanced_students)}")
    print(f"  • Data quality fixes applied: {sum(quality_metrics.values())}")
    print(f"  • Reports generated: {stats['generated']}")
    print(f"  • Errors: {stats['errors']}")
    
    if stats['errors'] > 0:
        print(f"\n⚠️  Errors encountered:")
        for error in stats['error_list'][:5]:
            print(f"    - {error}")
    
    # Show sample of improved report
    print("\n" + "=" * 50)
    print("SAMPLE OF CLEANED REPORT:")
    print("=" * 50)
    
    sample_report = "reports/s10769.md"
    if os.path.exists(sample_report):
        with open(sample_report, 'r') as f:
            lines = f.readlines()[:30]
            print("".join(lines))
    
    print("\n✅ Enhanced data cleaning has been successfully applied to all reports!")
    print("   Teacher names have been replaced with 'Attended'")
    print("   Progress values have been standardized")
    print("   URLs have been extracted from lesson fields")


if __name__ == "__main__":
    main()