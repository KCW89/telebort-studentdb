#!/usr/bin/env python3
"""
full_sync.py - Performs a full sync of all students from Google Sheets

This script fetches all student data in batches and generates reports.
Run this within Claude Code environment for MCP access.
"""

import os
import sys
import json
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_sheets_mcp import SheetsSyncManager, SPREADSHEET_ID, WORKSHEET_ID
from process_data import DataProcessor
from generate_reports import ReportGenerator


def fetch_students_batch(start_row, batch_size=20):
    """Fetch a batch of students from Google Sheets"""
    print(f"\nFetching rows {start_row} to {start_row + batch_size - 1}...")
    
    try:
        result = mcp__zapier__google_sheets_get_many_spreadsheet_rows_advanced(
            instructions=f"Get student data from row {start_row} to {start_row + batch_size - 1}",
            spreadsheet=SPREADSHEET_ID,
            worksheet=WORKSHEET_ID,
            first_row=str(start_row),
            row_count=str(batch_size),
            range="A:CZ",  # Limit columns to avoid token overflow
            output_format="line_items"
        )
        
        if result and 'results' in result and len(result['results']) > 0:
            rows = result['results'][0].get('rows', [])
            print(f"  Fetched {len(rows)} rows")
            return rows
        else:
            print("  No data received")
            return []
            
    except Exception as e:
        print(f"  Error fetching batch: {str(e)}")
        return []


def process_all_students():
    """Process all students from Google Sheets"""
    
    sync_manager = SheetsSyncManager()
    processor = DataProcessor()
    generator = ReportGenerator()
    
    all_students = []
    processed_students = []
    reports_generated = 0
    errors = []
    
    # Fetch in batches to avoid token limits
    start_row = 5  # Skip header rows
    batch_size = 20
    max_rows = 150  # Adjust based on actual student count
    
    print("=" * 60)
    print("FULL STUDENT SYNC")
    print("=" * 60)
    print(f"Spreadsheet: {SPREADSHEET_ID}")
    print(f"Worksheet: {WORKSHEET_ID}")
    print(f"Batch size: {batch_size}")
    
    # Fetch all batches
    while start_row < max_rows:
        rows = fetch_students_batch(start_row, batch_size)
        
        if not rows:
            # No more data
            break
            
        # Process this batch
        for row_data in rows:
            if row_data and len(row_data) > 2:
                try:
                    # Parse student data
                    student_data = sync_manager.parse_student_sessions(row_data)
                    
                    if student_data['info']['student_id']:
                        all_students.append(student_data)
                except Exception as e:
                    errors.append(f"Parse error row {start_row + len(all_students)}: {str(e)}")
        
        # Check if we got less than batch_size (means we're at the end)
        if len(rows) < batch_size:
            break
            
        start_row += batch_size
    
    print(f"\nTotal students fetched: {len(all_students)}")
    
    # Process all students
    print("\nProcessing students...")
    for i, student_data in enumerate(all_students):
        try:
            student_id = student_data['info']['student_id']
            student_name = student_data['info']['student_name']
            
            # Process data
            processed = processor.process_student(student_data)
            processed_students.append(processed)
            
            # Generate report
            report_path = generator.generate_report(processed)
            reports_generated += 1
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(all_students)} students...")
                
        except Exception as e:
            error_msg = f"Process error {student_id}: {str(e)}"
            errors.append(error_msg)
    
    # Save processed data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save all student data
    os.makedirs('logs', exist_ok=True)
    data_file = f"logs/all_students_{timestamp}.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_students': len(all_students),
            'processed': len(processed_students),
            'reports_generated': reports_generated,
            'students': processed_students
        }, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total students: {len(all_students)}")
    print(f"Processed: {len(processed_students)}")
    print(f"Reports generated: {reports_generated}")
    print(f"Errors: {len(errors)}")
    print(f"Data saved to: {data_file}")
    
    if errors:
        print("\nErrors encountered:")
        for i, error in enumerate(errors[:10]):  # Show first 10 errors
            print(f"  {i+1}. {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    return reports_generated


if __name__ == "__main__":
    try:
        reports = process_all_students()
        print(f"\nSuccess! Generated {reports} student reports.")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)