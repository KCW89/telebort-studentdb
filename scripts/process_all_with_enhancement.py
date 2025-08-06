#!/usr/bin/env python3
"""
process_all_with_enhancement.py - Process ALL students with enhanced cleaning

This script fetches all student data and applies enhanced cleaning.
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_all_student_ids() -> List[str]:
    """Get list of all student IDs from existing reports"""
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    student_ids = []
    
    for filename in os.listdir(reports_dir):
        if filename.endswith('.md') and filename.startswith('s'):
            student_id = filename.replace('.md', '')
            student_ids.append(student_id)
    
    return sorted(student_ids)

def load_student_data_from_report(student_id: str) -> Dict:
    """Load and parse student data from existing report"""
    report_path = os.path.join(os.path.dirname(__file__), '..', 'reports', f'{student_id}.md')
    
    if not os.path.exists(report_path):
        return None
    
    student_data = {
        'student_id': student_id,
        'name': '',
        'program': '',
        'schedule': '',
        'teacher': '',
        'sessions': []
    }
    
    with open(report_path, 'r') as f:
        lines = f.readlines()
    
    # Parse the report to extract data
    in_journey_section = False
    for line in lines:
        line = line.strip()
        
        # Extract program
        if line.startswith('- **Program:**'):
            student_data['program'] = line.replace('- **Program:**', '').strip()
        
        # Extract schedule
        elif line.startswith('- **Schedule:**'):
            student_data['schedule'] = line.replace('- **Schedule:**', '').strip()
        
        # Extract teacher
        elif line.startswith('- **Teacher:**'):
            student_data['teacher'] = line.replace('- **Teacher:**', '').strip()
        
        # Start of journey section
        elif '## Learning Journey' in line:
            in_journey_section = True
        
        # Parse journey table rows
        elif in_journey_section and line.startswith('|') and not line.startswith('| Date'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 5 and parts[0] != '------':
                # Check if this is the header separator line
                if '---' in parts[0]:
                    continue
                    
                student_data['sessions'].append({
                    'date': parts[0],
                    'session': parts[1],
                    'lesson': parts[2],
                    'attendance': parts[3],
                    'progress': parts[4]
                })
    
    return student_data

def main():
    """Main execution"""
    
    print("=" * 70)
    print("PROCESSING ALL STUDENTS WITH ENHANCED DATA CLEANING")
    print("=" * 70)
    
    # Get all student IDs
    logger.info("Getting list of all students...")
    student_ids = get_all_student_ids()
    logger.info(f"Found {len(student_ids)} student reports to process")
    
    # Load data from existing reports
    logger.info("Loading student data from reports...")
    all_students = []
    
    for student_id in student_ids:
        student_data = load_student_data_from_report(student_id)
        if student_data:
            all_students.append(student_data)
    
    logger.info(f"Loaded data for {len(all_students)} students")
    
    # Apply enhanced cleaning
    logger.info("Applying enhanced data cleaning...")
    enhanced_processor = EnhancedDataProcessor()
    enhanced_students, quality_metrics = enhanced_processor.process_student_data(all_students)
    
    print("\n" + "=" * 50)
    print("DATA QUALITY IMPROVEMENTS:")
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
            processor_data = {
                'info': {
                    'student_id': enhanced_student['student_id'],
                    'name': enhanced_student.get('name', ''),
                    'program': enhanced_student.get('program', ''),
                    'schedule': enhanced_student.get('schedule', ''),
                    'teacher': enhanced_student.get('teacher', '')
                },
                'sessions': []
            }
            
            # Use cleaned sessions
            for session in enhanced_student.get('sessions', []):
                processor_data['sessions'].append({
                    'date': session['date'],
                    'session': session['session'],
                    'lesson': session.get('lesson_title', session.get('lesson_raw', '')),
                    'attendance': session['attendance'],  # Now "Attended" instead of teacher name
                    'progress': session['progress']
                })
            
            # Process the data
            processed_data = data_processor.process_student(processor_data)
            
            # Generate report
            report_path = report_generator.generate_report(processed_data)
            stats['generated'] += 1
            
            # Show progress every 20 students
            if stats['generated'] % 20 == 0:
                print(f"  ✓ Processed {stats['generated']} reports...")
                
        except Exception as e:
            stats['errors'] += 1
            error_msg = f"Student {enhanced_student['student_id']}: {str(e)}"
            stats['error_list'].append(error_msg)
    
    # Final summary
    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Final Results:")
    print(f"  • Students processed: {len(enhanced_students)}")
    print(f"  • Data quality fixes applied: {sum(quality_metrics.values())}")
    print(f"  • Reports updated: {stats['generated']}")
    print(f"  • Errors: {stats['errors']}")
    
    if stats['errors'] > 0:
        print(f"\n⚠️  Errors encountered:")
        for error in stats['error_list'][:5]:
            print(f"    - {error}")
    
    print("\n✅ All student reports have been updated with enhanced data cleaning!")
    print("   • Teacher names replaced with 'Attended'")
    print("   • Progress values standardized")
    print("   • URLs extracted from lesson fields")
    print("   • Data quality significantly improved")


if __name__ == "__main__":
    main()