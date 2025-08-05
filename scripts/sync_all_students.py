#!/usr/bin/env python3
"""
sync_all_students.py - Sync all students by processing in batches

This script coordinates fetching data in batches and processing them.
"""

import os
import sys
import json
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_sheets_mcp import SheetsSyncManager
from process_data import DataProcessor
from generate_reports import ReportGenerator


class StudentSyncManager:
    """Manages the full sync process for all students"""
    
    def __init__(self):
        self.sync_manager = SheetsSyncManager()
        self.processor = DataProcessor()
        self.generator = ReportGenerator()
        self.all_students = []
        self.processed_students = []
        self.errors = []
        
    def process_batch(self, batch_data, batch_num):
        """Process a batch of student data"""
        print(f"\nProcessing batch {batch_num}...")
        batch_processed = 0
        batch_reports = 0
        
        for i, row_data in enumerate(batch_data):
            if row_data and len(row_data) > 2:
                try:
                    # Parse student data
                    student_data = self.sync_manager.parse_student_sessions(row_data)
                    
                    if not student_data['info']['student_id']:
                        continue
                    
                    student_id = student_data['info']['student_id']
                    student_name = student_data['info']['student_name']
                    
                    # Store raw data
                    self.all_students.append(student_data)
                    
                    # Process data
                    processed = self.processor.process_student(student_data)
                    self.processed_students.append(processed)
                    batch_processed += 1
                    
                    # Generate report
                    report_path = self.generator.generate_report(processed)
                    batch_reports += 1
                    
                    print(f"  ✓ {student_id} - {student_name}")
                    
                except Exception as e:
                    error_msg = f"Batch {batch_num}, Row {i+1}: {str(e)}"
                    self.errors.append(error_msg)
                    print(f"  ✗ Error: {error_msg}")
        
        print(f"Batch {batch_num} complete: {batch_processed} processed, {batch_reports} reports")
        return batch_processed, batch_reports
    
    def save_results(self):
        """Save all processed data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Save processed data
        summary_file = f"logs/sync_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_students': len(self.all_students),
                'processed': len(self.processed_students),
                'errors': len(self.errors),
                'error_details': self.errors
            }, f, indent=2, ensure_ascii=False)
        
        # Save detailed student data
        students_file = f"logs/all_students_{timestamp}.json"
        with open(students_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_students, f, indent=2, ensure_ascii=False)
        
        print(f"\nData saved to:")
        print(f"  - Summary: {summary_file}")
        print(f"  - Students: {students_file}")
        
    def print_summary(self):
        """Print sync summary"""
        print("\n" + "=" * 60)
        print("SYNC SUMMARY")
        print("=" * 60)
        print(f"Total students found: {len(self.all_students)}")
        print(f"Successfully processed: {len(self.processed_students)}")
        print(f"Reports generated: {len(self.processed_students)}")
        print(f"Errors encountered: {len(self.errors)}")
        
        if self.errors:
            print("\nFirst 5 errors:")
            for i, error in enumerate(self.errors[:5]):
                print(f"  {i+1}. {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")


def main():
    """Main function to coordinate the sync"""
    print("=" * 60)
    print("STUDENT REPORT SYNC")
    print("=" * 60)
    print("This script will process student data in batches.")
    print("Make sure to run the MCP fetch commands separately.")
    
    sync_manager = StudentSyncManager()
    
    # Instructions for manual batching
    print("\nTo fetch data, run these commands in Claude Code:")
    print("1. Fetch rows 5-25 (batch 1)")
    print("2. Fetch rows 25-45 (batch 2)")
    print("3. Continue until all students are fetched")
    print("\nThen update this script with the batch data.")
    
    # For now, process the sample batch we already have
    print("\nProcessing sample batch...")
    
    # Sample data from earlier
    sample_batch = [
        ["Nathakit Shotiwoth","","s10769","G (AI-2)","Saturday","10:00","11:00","Soumiya","09/08/2025","2","-","","-","02/08/2025","2","LESSON 2 \r\nC2 Machine Learning\r\nC3 Super Leaning & Unsupervised Learning","Soumiya","In Progress","26/07/2025","1","-","Absent","-","19/07/2025","1","L1 Introduction to AI","Soumiya","Completed","12/07/2025","0","-","No Class","-","05/07/2025","0","-","In Break","-","28/06/2025","0","-","No Class","-","21/06/2025","0","-","No Class","-","14/06/2025","0","-","No Class","-","07/06/2025","0","-","No Class","-","31/05/2025","26","L23 Final Project (Presentation): COMPLETED\nL24 Graduation: COMPLETED","Soumiya","Graduated","24/05/2025","25","L23 Final Project (Presentation): IN PROGRESS","Soumiya","In Progress","17/05/2025","24","L22 Final Project (Report Making) COMPLETED (for final presenatation not yet)","Hafiz","Completed","10/05/2025","23","L21 Final Project (Setup + Data Cleaning + Data Analysis): COMPLETED","Soumiya","Completed","03/05/2025","22","-","Absent","-","26/04/2025","22","L21 Final Project (Setup + Data Cleaning + Data Analysis): IN PROGRESS","Soumiya","In Progress","19/04/2025","21","L20 Quiz 2: COMPLETED\nL21 Final Project (Setup + Data Cleaning + Data Analysis): IN PROGRESS","Soumiya","In Progress","12/04/2025","20","L19 Project 4 Google Play Store (Report): COMPLETED","Soumiya","Completed","05/04/2025","19","Teacher Parent Day","No Class","-","29/03/2025"],
        ["Nathan Chee Ying-Cherng","","s10777","F (AI-1)","Saturday","11:00","12:00","Soumiya","09/08/2025","14","-","","-","02/08/2025","14","C13: Data Visualization using Matplotlib","Soumiya","Completed","26/07/2025","13","L22: Final Project Prototype https://www.telebort.com/demo/ai2/project/7  ","Soumiya","Completed","19/07/2025","12","L9: concept 11 Descriptive Statistics\nL10: concept 12 pretty table \nhttps://www.telebort.com/demo/ai1/lesson/12  \nhttps://www.telebort.com/demo/ai1/activity/12   ","Soumiya","In Progress","12/07/2025","11","L10: concept 12 pretty table https://www.telebort.com/demo/ai1/lesson/12  https://www.telebort.com/demo/ai1/activity/12   concept 13 data visualization https://www.telebort.com/demo/ai1/lesson/13  https://www.telebort.com/demo/ai1/activity/13 ","No Class","-","05/07/2025","11","-","Absent","-","28/06/2025","11","L9 Numpy: COMPLETED","Soumiya","Completed","21/06/2025","10","L8 Project 2 Covid-19 Cases Prediction: COMPLETED","Soumiya","Completed","14/06/2025","9","L8 Project 2 Covid-19 Cases Prediction: IN PROGRESS","Soumiya","In Progress","07/06/2025","8","-","No Class","-","31/05/2025","8","L7 Function: COMPLETED\nL7 Package: COMPLETED","Soumiya","Completed","24/05/2025","7","L6 Dictionary : COMPLETED","Soumiya","Completed","17/05/2025","6","L5 P1 Ice Cream Shop: COMPLETED","Hafiz","Completed","10/05/2025","5","L4 Loops : COMPLETED\nL5 P1 Ice Cream Shop: IN PROGRESS","Soumiya","In Progress","03/05/2025","4","L4 Loops: IN PROGRESS","Soumiya","In Progress","26/04/2025","3","L3 Lists: COMPLETED","Soumiya","Completed","19/04/2025","2","L2 Variable & Operator: COMPLETED","Soumiya","Completed","12/04/2025","1","-","Absent","-","05/04/2025","1","Teacher Parent Day","No Class","-","29/03/2025"],
        ["Shawn Lee Shan Wei","","s10710","F (AI-1)","Saturday","12:00","13:00","Soumiya","09/08/2025","7","-","","-","02/08/2025","7","C7: Dictionary","Soumiya","Completed","26/07/2025","6","L2: Concept 3 Variables & Operators https://www.telebort.com/demo/ai1/lesson/3  https://www.telebort.com/demo/ai1/activity/3 https://forms.gle/EzCaqwFv25TbC2qV9 L3: Concept 4 List https://www.telebort.com/demo/ai1/lesson/4 https://www.telebort.com/demo/ai1/activity/4 https://forms.gle/xoyG4q1JrYxi4CkV6 ","Soumiya","Completed","19/07/2025","5","L4: concept 6 activity https://www.telebort.com/demo/ai1/activity/6  L5: project 1 https://www.telebort.com/demo/ai1/project/1 ","Soumiya","Completed","12/07/2025","4","L4: concept 6 activity https://www.telebort.com/demo/ai1/activity/6  L5: project 1 https://www.telebort.com/demo/ai1/project/1 ","No Class","-","05/07/2025","4","-","Absent","-","28/06/2025","4","L3 Conditional Statement: COMPLETED\nL4 Loops: IN PROGRESS","Soumiya","In Progress","21/06/2025","3","L3 List: COMPLETED","Soumiya","Completed","14/06/2025","2","L2 Variable: COMPLETED","Soumiya","Completed","07/06/2025","1","-","No Class","-","31/05/2025","1","L1 Introduction to Python Programming: COMPLETED\nL1 Jupyter Notebook: COMPLETED","Soumiya","Completed","24/05/2025","0","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-"],
    ]
    
    # Process the sample batch
    sync_manager.process_batch(sample_batch, 1)
    
    # Save results
    sync_manager.save_results()
    
    # Print summary
    sync_manager.print_summary()
    
    print("\nNext steps:")
    print("1. Fetch more batches using MCP")
    print("2. Add them to this script")
    print("3. Run again to process all students")


if __name__ == "__main__":
    main()