#!/usr/bin/env python3
"""
fetch_complete_data.py - Fetch COMPLETE student data including all historical sessions

This script fetches all 338 columns (A-LZ) from Google Sheets to ensure we capture
the complete learning history for each student, not just recent sessions.
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

# MCP function imports (will be simulated if not available)
try:
    from mcp_google_sheets import get_spreadsheet_rows
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP not available, will use cached data if available")

def fetch_complete_student_data(start_row: int = 5, end_row: int = 112) -> List[Dict]:
    """
    Fetch complete student data from Google Sheets including ALL columns (A-LZ)
    
    This ensures we get all historical sessions (up to 66 sessions per student)
    """
    all_students = []
    
    # Google Sheets details
    SPREADSHEET_ID = "1zbw7hLSa-5k83T0d6KrD-eiZv5nM855oYHV_B-tslbU"
    WORKSHEET_ID = "891163674"
    
    # Process in batches to avoid timeout
    batch_size = 20
    
    for batch_start in range(start_row, end_row + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, end_row)
        
        logger.info(f"Fetching rows {batch_start} to {batch_end}...")
        
        if MCP_AVAILABLE:
            # Use actual MCP to fetch data
            try:
                result = get_spreadsheet_rows(
                    spreadsheet=SPREADSHEET_ID,
                    worksheet=WORKSHEET_ID,
                    first_row=batch_start,
                    row_count=batch_end - batch_start + 1,
                    range="A:LZ"  # FULL range to column LZ (338 columns)
                )
                
                if result and 'rows' in result:
                    for row in result['rows']:
                        student = parse_complete_row(row)
                        if student:
                            all_students.append(student)
                            
            except Exception as e:
                logger.error(f"Error fetching batch {batch_start}-{batch_end}: {e}")
        else:
            # For testing, create sample complete data
            logger.info("Using sample data for testing...")
            # Would normally load from complete cache file
            pass
    
    logger.info(f"Fetched {len(all_students)} students with complete data")
    return all_students

def parse_complete_row(row: List) -> Dict:
    """
    Parse a complete row with all 338 columns
    
    Structure:
    - Columns A-H (0-7): Student info
    - Columns I-M (8-12): Session 1 (5 columns)
    - Columns N-R (13-17): Session 2 (5 columns)
    - ... continues for up to 66 sessions
    - Up to column LZ (338)
    """
    
    if not row or len(row) < 8:
        return None
    
    # Skip if no student ID
    if not row[2] or row[2] == '-':
        return None
    
    student = {
        'name': row[0] if row[0] else '',
        'status': row[1] if row[1] else '',
        'student_id': row[2],
        'program': row[3] if row[3] else '',
        'day': row[4] if row[4] else '',
        'start_time': row[5] if row[5] else '',
        'end_time': row[6] if row[6] else '',
        'teacher': row[7] if row[7] else '',
        'schedule': f"{row[4]} {row[5]}-{row[6]}" if row[4] and row[5] and row[6] else '-',
        'sessions': []
    }
    
    # Parse ALL sessions (every 5 columns from column 8 onwards)
    # Maximum possible sessions = (338 - 8) / 5 = 66 sessions
    session_count = 0
    
    for i in range(8, len(row), 5):
        # Check if we have a complete session (5 columns)
        if i + 4 >= len(row):
            break
            
        date = row[i] if i < len(row) else ''
        session_num = row[i+1] if i+1 < len(row) else ''
        lesson = row[i+2] if i+2 < len(row) else ''
        attendance = row[i+3] if i+3 < len(row) else ''
        progress = row[i+4] if i+4 < len(row) else ''
        
        # Only add sessions with valid dates
        if date and date != '-':
            student['sessions'].append({
                'date': date,
                'session': session_num,
                'lesson': lesson,
                'attendance': attendance,
                'progress': progress
            })
            session_count += 1
    
    logger.debug(f"Student {student['student_id']} has {session_count} sessions")
    
    return student

def save_complete_data(students: List[Dict], filename: str = "complete_student_data.json"):
    """Save complete student data to JSON file"""
    
    filepath = os.path.join(os.path.dirname(__file__), '..', filename)
    
    with open(filepath, 'w') as f:
        json.dump({
            'fetched_at': datetime.now().isoformat(),
            'total_students': len(students),
            'column_range': 'A:LZ (338 columns)',
            'max_sessions_per_student': 66,
            'students': students
        }, f, indent=2)
    
    logger.info(f"Saved complete data for {len(students)} students to {filename}")
    
    # Also save session statistics
    stats = calculate_session_stats(students)
    logger.info(f"Session statistics:")
    logger.info(f"  • Average sessions per student: {stats['avg_sessions']:.1f}")
    logger.info(f"  • Maximum sessions: {stats['max_sessions']}")
    logger.info(f"  • Minimum sessions: {stats['min_sessions']}")
    logger.info(f"  • Students with 20+ sessions: {stats['students_with_20_plus']}")

def calculate_session_stats(students: List[Dict]) -> Dict:
    """Calculate statistics about session counts"""
    
    session_counts = [len(s['sessions']) for s in students]
    
    return {
        'avg_sessions': sum(session_counts) / len(session_counts) if session_counts else 0,
        'max_sessions': max(session_counts) if session_counts else 0,
        'min_sessions': min(session_counts) if session_counts else 0,
        'students_with_20_plus': sum(1 for c in session_counts if c >= 20),
        'total_sessions': sum(session_counts)
    }

def process_with_complete_data(students: List[Dict]):
    """Process students with complete data and generate reports"""
    
    logger.info("Processing with enhanced data cleaning...")
    
    # Initialize processors
    enhanced_processor = EnhancedDataProcessor()
    data_processor = DataProcessor()
    report_generator = ReportGenerator()
    
    # Apply enhanced cleaning
    enhanced_students, quality_metrics = enhanced_processor.process_student_data(students)
    
    logger.info(f"Data quality improvements:")
    logger.info(f"  • Teacher names fixed: {quality_metrics['teacher_name_fixes']}")
    logger.info(f"  • Progress standardized: {quality_metrics['progress_standardizations']}")
    logger.info(f"  • URLs extracted: {quality_metrics['url_extractions']}")
    
    # Generate reports
    logger.info("Generating reports with complete history...")
    
    success_count = 0
    error_count = 0
    
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
            
            # Add all sessions
            for session in enhanced_student.get('sessions', []):
                processor_data['sessions'].append({
                    'date': session['date'],
                    'session': session['session'],
                    'lesson': session.get('lesson_title', session.get('lesson_raw', '')),
                    'attendance': session['attendance'],
                    'progress': session['progress']
                })
            
            # Process and generate report
            processed_data = data_processor.process_student(processor_data)
            report_path = report_generator.generate_report(processed_data)
            
            success_count += 1
            
            # Show progress
            if success_count % 10 == 0:
                logger.info(f"  Generated {success_count} reports...")
                
        except Exception as e:
            error_count += 1
            logger.error(f"Error processing {enhanced_student['student_id']}: {e}")
    
    logger.info(f"\nComplete! Generated {success_count} reports with full history")
    logger.info(f"Errors: {error_count}")

def main():
    """Main execution"""
    
    print("=" * 70)
    print("FETCHING COMPLETE STUDENT DATA (ALL 338 COLUMNS)")
    print("=" * 70)
    
    # Check if we have cached complete data
    cache_file = os.path.join(os.path.dirname(__file__), '..', 'complete_student_data.json')
    
    if os.path.exists(cache_file):
        logger.info("Found cached complete data, loading...")
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        students = cache_data.get('students', [])
        logger.info(f"Loaded {len(students)} students from cache")
        
        # Check if cache is recent (within 1 day)
        cache_time = datetime.fromisoformat(cache_data['fetched_at'])
        age_hours = (datetime.now() - cache_time).total_seconds() / 3600
        
        if age_hours > 24:
            logger.info(f"Cache is {age_hours:.1f} hours old, consider refreshing")
    else:
        # Fetch fresh data
        logger.info("Fetching fresh data from Google Sheets...")
        students = fetch_complete_student_data()
        
        if students:
            # Save to cache
            save_complete_data(students)
        else:
            logger.error("Failed to fetch student data")
            return
    
    # Process and generate reports
    if students:
        process_with_complete_data(students)
        
        # Show example of complete data
        print("\n" + "=" * 70)
        print("EXAMPLE: s10788 Complete History")
        print("=" * 70)
        
        for student in students:
            if student['student_id'] == 's10788':
                print(f"Student: {student['name']} ({student['student_id']})")
                print(f"Program: {student['program']}")
                print(f"Total sessions: {len(student['sessions'])}")
                
                if student['sessions']:
                    # Show first and last sessions
                    first = student['sessions'][0]
                    last = student['sessions'][-1]
                    
                    print(f"\nFirst session: {first['date']} - {first['lesson'][:50]}...")
                    print(f"Last session: {last['date']} - {last['lesson'][:50]}...")
                    
                    # Show session timeline
                    print(f"\nSession timeline:")
                    for i, session in enumerate(student['sessions'][:10]):
                        print(f"  {session['date']} | Session {session['session']} | {session['attendance']}")
                    
                    if len(student['sessions']) > 10:
                        print(f"  ... and {len(student['sessions']) - 10} more sessions")
                
                break
    
    print("\n✅ Complete data processing finished!")


if __name__ == "__main__":
    main()