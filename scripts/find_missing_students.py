#!/usr/bin/env python3
"""
find_missing_students.py - Identify missing students by checking all rows in Google Sheets
"""

import os
import sys

def analyze_existing_reports():
    """Analyze which student reports have been generated"""
    reports_dir = '../reports'
    
    # Get all student IDs from existing reports
    existing_ids = set()
    for filename in os.listdir(reports_dir):
        if filename.startswith('s') and filename.endswith('.md'):
            student_id = filename.replace('.md', '')
            existing_ids.add(student_id)
    
    print(f"Total reports found: {len(existing_ids)}")
    print(f"Report IDs range: {min(existing_ids)} to {max(existing_ids)}")
    
    # Sort and display all IDs
    sorted_ids = sorted(existing_ids)
    print("\nAll student IDs with reports:")
    for i in range(0, len(sorted_ids), 10):
        print(" ".join(sorted_ids[i:i+10]))
    
    return existing_ids

def check_row_coverage():
    """Check which rows have been processed in our batches"""
    processed_rows = []
    
    # From our batch processing summary
    batch_coverage = [
        ("Batch 1 (previous)", [5, 7, 9]),
        ("Batch 2", list(range(25, 45))),
        ("Batch 3", list(range(45, 65))),
        ("Batch 4", list(range(65, 85))),
        ("Batch 5", list(range(85, 105))),
        ("Batch 6", list(range(105, 112))),
        ("Batch 7", list(range(10, 25))),
        ("Batch 8", [6, 8])  # s10777, s10710, s10213
    ]
    
    all_processed = []
    print("\nBatch processing coverage:")
    for batch_name, rows in batch_coverage:
        print(f"{batch_name}: rows {rows[0]}-{rows[-1] if len(rows) > 1 else rows[0]} ({len(rows)} students)")
        all_processed.extend(rows)
    
    # Find gaps
    all_processed_set = set(all_processed)
    max_row = max(all_processed)
    
    print(f"\nTotal rows processed: {len(all_processed_set)}")
    print(f"Row range: 5 to {max_row}")
    
    # Check for gaps in row coverage
    gaps = []
    for i in range(5, max_row + 1):
        if i not in all_processed_set:
            gaps.append(i)
    
    if gaps:
        print(f"\nGaps in row coverage: {gaps}")
    else:
        print("\nNo gaps in row coverage from 5 to", max_row)
    
    # Check specific unprocessed rows in early range
    early_unprocessed = []
    for i in range(1, 5):
        if i not in all_processed_set:
            early_unprocessed.append(i)
    
    if early_unprocessed:
        print(f"Unprocessed early rows (1-4): {early_unprocessed}")
    
    return all_processed_set, gaps, early_unprocessed

def main():
    """Main function to find missing students"""
    print("Finding Missing Students Analysis")
    print("=" * 60)
    
    # Analyze existing reports
    existing_ids = analyze_existing_reports()
    
    # Check row coverage
    processed_rows, gaps, early_rows = check_row_coverage()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total reports generated: {len(existing_ids)}")
    print(f"Target number of students: 107")
    print(f"Missing students: {107 - len(existing_ids)}")
    
    if gaps:
        print(f"\nRow gaps to check: {gaps}")
    
    if early_rows:
        print(f"Early rows to check: {early_rows}")
        print("\nNote: Rows 1-4 might contain headers or non-student data")
    
    print("\nNext steps:")
    print("1. Check rows 1-4 in Google Sheets (might be headers)")
    print("2. Verify if there are students after row 111")
    print("3. Check for any students with invalid/missing IDs that couldn't generate reports")

if __name__ == "__main__":
    # Change to scripts directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()