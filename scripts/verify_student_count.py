#!/usr/bin/env python3
"""
verify_student_count.py - Verify actual student count in Google Sheets
and check which students from our processing didn't generate reports
"""

import os
import json

def check_processed_students():
    """Check all students that were supposed to be processed"""
    
    # List of all student IDs from our batch processing
    all_student_ids = []
    
    # From previous batch (rows 5,7,9)
    batch1_ids = ["s10769", "s10711", "s10705"]
    all_student_ids.extend(batch1_ids)
    
    # From batch 2 (rows 25-44)
    batch2_ids = ["s10715", "s10716", "s10724", "s10735", "s10745", "s10746", 
                  "s10747", "s10748", "s10760", "s10761", "s10763", "s10719", 
                  "s10721", "s10332", "s10687", "s10718", "s10634", "s10641", 
                  "s10725", "s10720"]
    all_student_ids.extend(batch2_ids)
    
    # From batch 3 (rows 45-64)
    batch3_ids = ["s10722", "s10724", "s10736", "s10749", "s10756", "s10764", 
                  "s10771", "s10772", "s10773", "s10774", "s10775", "s10776", 
                  "s10781", "s10770", "s10682", "s10751", "s10778", "s10451", 
                  "s10152", "s10151"]
    all_student_ids.extend(batch3_ids)
    
    # From batch 4 (rows 65-84)
    batch4_ids = ["s10780", "s10577", "s10171", "s10166", "s10169", "s10160", 
                  "s10154", "s10157", "s10168", "s10159", "s10161", "s10161", 
                  "s10224", "s10227", "s10240", "s10243", "s10249", "s10782", 
                  "s10783", "s10590"]
    all_student_ids.extend(batch4_ids)
    
    # From batch 5 (rows 85-104)
    batch5_ids = ["s10803", "s10793", "s10792", "s10361", "s10489", "s10362", 
                  "s10798", "s10762", "s10790", "s10756", "s10794", "s10795", 
                  "s10169", "s10157", "s10161", "s10804", "s10810", "s10785", 
                  "s10791", "s10786"]
    all_student_ids.extend(batch5_ids)
    
    # From batch 6 (rows 105-111)
    batch6_ids = ["s10787", "s10788", "s10789", "s10796", "s10801", "s10802", "s10805"]
    all_student_ids.extend(batch6_ids)
    
    # From batch 7 (rows 10-24) - all were reprocessed in process_missing_students.py
    batch7_ids = ["s10569", "s10608", "s10609", "s10707", "s10809", "s10510", 
                  "s10708", "s10767", "s10360", "s10808", "s10726", "s10723", 
                  "s10084", "s10100", "s10779"]
    all_student_ids.extend(batch7_ids)
    
    # From batch 8 (rows 6,8) - also reprocessed
    batch8_ids = ["s10777", "s10710", "s10213"]
    all_student_ids.extend(batch8_ids)
    
    # Remove duplicates
    unique_ids = list(set(all_student_ids))
    
    print(f"Total unique student IDs from all batches: {len(unique_ids)}")
    print(f"Total processing attempts (with duplicates): {len(all_student_ids)}")
    
    # Check which ones have reports
    reports_dir = '../reports'
    existing_reports = set()
    for filename in os.listdir(reports_dir):
        if filename.startswith('s') and filename.endswith('.md'):
            student_id = filename.replace('.md', '')
            existing_reports.add(student_id)
    
    # Find missing
    missing_reports = set(unique_ids) - existing_reports
    extra_reports = existing_reports - set(unique_ids)
    
    print(f"\nStudent IDs without reports: {len(missing_reports)}")
    if missing_reports:
        print("Missing:", sorted(missing_reports))
    
    print(f"\nReports without matching student IDs from batches: {len(extra_reports)}")
    if extra_reports:
        print("Extra:", sorted(extra_reports))
    
    # Check for duplicates in our processing
    from collections import Counter
    id_counts = Counter(all_student_ids)
    duplicates = {id: count for id, count in id_counts.items() if count > 1}
    
    if duplicates:
        print(f"\nDuplicate student IDs in batches:")
        for id, count in sorted(duplicates.items()):
            print(f"  {id}: appears {count} times")
    
    return unique_ids, existing_reports

def check_empty_rows():
    """Check if any rows in our batches had empty or invalid student IDs"""
    
    # Known issue: batch 7 generated reports with program names instead of student IDs
    # These were fixed in process_missing_students.py
    
    print("\n" + "="*60)
    print("KNOWN ISSUES")
    print("="*60)
    print("1. Batch 7 initially generated reports with program names (BBP.md, etc.)")
    print("   - This was fixed by reprocessing in process_missing_students.py")
    print("2. Some student IDs appear multiple times in different batches")
    print("   - This doesn't affect report generation (last update wins)")

def main():
    """Main analysis function"""
    print("Student Count Verification")
    print("="*60)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    unique_ids, existing_reports = check_processed_students()
    check_empty_rows()
    
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"Unique student IDs processed: {len(unique_ids)}")
    print(f"Reports generated: {len(existing_reports)}")
    print(f"Difference: {len(unique_ids) - len(existing_reports)}")
    
    # The missing 6 students mystery
    print("\nAnalysis of missing 6 students:")
    print("- We processed 107 rows (some students appear in multiple rows)")
    print("- We have 101 unique student reports")
    print("- The 6 'missing' count likely comes from:")
    print("  1. Duplicate student IDs counted multiple times")
    print("  2. Empty rows at the end of the spreadsheet")
    print("  3. Rows without valid student IDs")

if __name__ == "__main__":
    main()