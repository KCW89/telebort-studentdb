#!/usr/bin/env python3
"""
fetch_real_data.py - Fetches real data from Google Sheets using Zapier MCP

This script is designed to run within Claude Code environment where
MCP functions are available.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Import our modules
from sync_sheets_mcp import SheetsSyncManager, SPREADSHEET_ID, WORKSHEET_ID
from process_data import DataProcessor
from generate_reports import ReportGenerator


def fetch_students_from_sheets():
    """
    Fetch all students from Google Sheets using Zapier MCP
    
    This function should be run in Claude Code environment
    """
    print("Fetching student data from Google Sheets...")
    print(f"Spreadsheet ID: {SPREADSHEET_ID}")
    print(f"Worksheet ID: {WORKSHEET_ID}")
    
    try:
        # Call the MCP function directly
        # Note: This will only work in Claude Code environment
        result = mcp__zapier__google_sheets_get_many_spreadsheet_rows_advanced(
            instructions="Get all student data from row 5 onwards (skip headers)",
            spreadsheet=SPREADSHEET_ID,
            worksheet=WORKSHEET_ID,
            first_row="5",
            row_count="200",
            range="A:DZ",  # Get all columns up to DZ
            output_format="line_items"
        )
        
        # Extract rows from result
        if result and 'results' in result and len(result['results']) > 0:
            rows = result['results'][0].get('rows', [])
            print(f"Fetched {len(rows)} rows from Google Sheets")
            return rows
        else:
            print("No data received from Google Sheets")
            return []
            
    except Exception as e:
        print(f"Error calling MCP function: {str(e)}")
        print("Make sure you're running this in Claude Code environment")
        return []


def process_fetched_data(rows: List[List[Any]]):
    """
    Process the fetched rows into student records
    """
    sync_manager = SheetsSyncManager()
    processor = DataProcessor()
    generator = ReportGenerator()
    
    students = []
    processed_students = []
    
    print(f"\nProcessing {len(rows)} rows...")
    
    # Parse each row
    for i, row_data in enumerate(rows):
        if row_data and len(row_data) > 2:  # Skip empty rows
            try:
                # Parse student data
                student_data = sync_manager.parse_student_sessions(row_data)
                
                # Only process if has valid student ID
                if student_data['info']['student_id']:
                    students.append(student_data)
                    
                    # Process the student data
                    processed = processor.process_student(student_data)
                    processed_students.append(processed)
                    
                    print(f"  Processed student {student_data['info']['student_id']} - {student_data['info']['student_name']}")
                    
            except Exception as e:
                print(f"  Error processing row {i+1}: {str(e)}")
    
    print(f"\nSuccessfully processed {len(processed_students)} students")
    
    # Save processed data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save raw parsed data
    os.makedirs('logs', exist_ok=True)
    raw_file = f"logs/parsed_students_{timestamp}.json"
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=2, ensure_ascii=False)
    print(f"Saved parsed data to {raw_file}")
    
    # Save processed data
    processed_file = f"logs/processed_students_{timestamp}.json"
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(processed_students, f, indent=2, ensure_ascii=False)
    print(f"Saved processed data to {processed_file}")
    
    return processed_students


def generate_sample_reports(processed_students: List[Dict[str, Any]], limit: int = 5):
    """
    Generate sample reports for the first few students
    """
    generator = ReportGenerator()
    
    print(f"\nGenerating sample reports for first {limit} students...")
    
    for i, student in enumerate(processed_students[:limit]):
        try:
            report_path = generator.generate_report(student)
            print(f"  Generated report: {report_path}")
        except Exception as e:
            print(f"  Error generating report for {student['student_id']}: {str(e)}")


def main():
    """Main function"""
    print("=" * 60)
    print("GOOGLE SHEETS DATA FETCH TEST")
    print("=" * 60)
    
    # Fetch data from Google Sheets
    rows = fetch_students_from_sheets()
    
    if not rows:
        print("\nNo data fetched. Exiting.")
        return 1
    
    # Process the data
    processed_students = process_fetched_data(rows)
    
    if not processed_students:
        print("\nNo students processed. Exiting.")
        return 1
    
    # Generate sample reports
    generate_sample_reports(processed_students, limit=5)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"Total students processed: {len(processed_students)}")
    print("\nNext steps:")
    print("1. Review the generated sample reports in the 'reports' directory")
    print("2. Check the logs directory for parsed and processed data")
    print("3. Run full sync if sample reports look good")
    
    return 0


if __name__ == "__main__":
    exit(main())