#!/usr/bin/env python3
"""
Process final batch of students from Google Sheets (rows 6-8)
Generated: 2025-08-05
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.sync_sheets_mcp import SheetsSyncManager
from scripts.process_data import DataProcessor
from scripts.generate_reports import ReportGenerator

# Raw data from Google Sheets MCP call (rows 6-8)
# Note: s10769 was already processed in batch 1
raw_data = [
    ["Nathan Chee Ying-Cherng", "s10777", "F (AI-1)", "Saturday", "11:00", "12:00", "Soumiya", "02/08/2025", "13", "-", "-", "-", "26/07/2025", "13", "L22: Final Project Prototype https://www.telebort.com/demo/ai2/project/7  ", "Soumiya", "Completed", "19/07/2025", "12", "L9: concept 11 Descriptive Statistics\nL10: concept 12 pretty table \nhttps://www.telebort.com/demo/ai1/lesson/12  \nhttps://www.telebort.com/demo/ai1/activity/12   ", "Soumiya", "In Progress", "12/07/2025", "11", "L10: concept 12 pretty table https://www.telebort.com/demo/ai1/lesson/12  https://www.telebort.com/demo/ai1/activity/12   concept 13 data visualization https://www.telebort.com/demo/ai1/lesson/13  https://www.telebort.com/demo/ai1/activity/13 ", "No Class", "-", "05/07/2025", "11", "-", "Absent", "-", "28/06/2025", "11", "L9 Numpy: COMPLETED", "Soumiya"],
    ["Shawn Lee Shan Wei", "s10710", "F (AI-1)", "Saturday", "12:00", "13:00", "Soumiya", "02/08/2025", "6", "-", "-", "-", "26/07/2025", "6", "L2: Concept 3 Variables & Operators https://www.telebort.com/demo/ai1/lesson/3  https://www.telebort.com/demo/ai1/activity/3 https://forms.gle/EzCaqwFv25TbC2qV9 L3: Concept 4 List https://www.telebort.com/demo/ai1/lesson/4 https://www.telebort.com/demo/ai1/activity/4 https://forms.gle/xoyG4q1JrYxi4CkV6 ", "Soumiya", "Completed", "19/07/2025", "5", "L4: concept 6 activity https://www.telebort.com/demo/ai1/activity/6  L5: project 1 https://www.telebort.com/demo/ai1/project/1 ", "Soumiya", "Completed", "12/07/2025", "4", "L4: concept 6 activity https://www.telebort.com/demo/ai1/activity/6  L5: project 1 https://www.telebort.com/demo/ai1/project/1 ", "No Class", "-", "05/07/2025", "4", "-", "Absent", "-", "28/06/2025", "4", "L3 Conditional Statement: COMPLETED\nL4 Loops: IN PROGRESS", "Soumiya"],
    ["Low Yue Yuan", "s10213", "G (AI-2)", "Saturday", "14:00", "16:00", "Soumiya", "02/08/2025", "24", "-", "-", "-", "26/07/2025", "24", "Quiz 2 https://forms.gle/VE31bFQVGTczFWnX9 ", "Soumiya", "Completed", "19/07/2025", "23", "L23 prepare presentation https://www.telebort.com/demo/ai2/project/7", "Soumiya", "In Progress", "12/07/2025", "22", "L23 prepare presentation https://www.telebort.com/demo/ai2/project/7", "No Class", "-", "05/07/2025", "22", "L22 Project Prototype: COMPLETED", "Soumiya", "Completed", "28/06/2025", "21", "L22 Project Prototype: IN PROGRESS", "Soumiya"]
]

def process_student_batch(raw_rows):
    """Process a batch of student data from raw Google Sheets rows"""
    sync_manager = SheetsSyncManager()
    processor = DataProcessor()
    generator = ReportGenerator()
    
    processed_count = 0
    error_count = 0
    
    for row_data in raw_rows:
        try:
            # Extract student info from fixed columns
            student_name = row_data[0]
            student_id = row_data[1]
            program = row_data[2]
            day = row_data[3]
            start_time = row_data[4]
            end_time = row_data[5]
            teacher = row_data[6]
            
            print(f"\n{processed_count+1}. Processing {student_id} - {student_name}")
            
            # Parse the row using the sync manager
            student_data = sync_manager.parse_student_sessions(row_data)
            
            # Process the data
            processed_data = processor.process_student(student_data)
            
            # Generate report
            report_path = generator.generate_report(processed_data)
            print(f"   ✓ Report generated: {report_path}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"   ✗ Error processing {student_id if 'student_id' in locals() else 'unknown'}: {str(e)}")
            error_count += 1
    
    return processed_count, error_count

def main():
    print("Processing final batch of 3 students (rows 6-8)...")
    
    processed, errors = process_student_batch(raw_data)
    
    print("\n" + "="*60)
    print("BATCH PROCESSING SUMMARY")
    print("="*60)
    print(f"Total rows: {len(raw_data)}")
    print(f"Processed: {processed}")
    print(f"Reports generated: {processed}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()