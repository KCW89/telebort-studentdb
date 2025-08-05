#!/usr/bin/env python3
"""
process_batch.py - Process a batch of students from Google Sheets data
"""

import json
import os
import sys
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_sheets_mcp import SheetsSyncManager
from process_data import DataProcessor
from generate_reports import ReportGenerator


def process_student_batch(raw_rows):
    """Process a batch of student rows"""
    
    sync_manager = SheetsSyncManager()
    processor = DataProcessor()
    generator = ReportGenerator()
    
    processed_count = 0
    report_count = 0
    errors = []
    
    print(f"Processing {len(raw_rows)} students...")
    
    for i, row_data in enumerate(raw_rows):
        try:
            # Parse student data
            student_data = sync_manager.parse_student_sessions(row_data)
            student_id = student_data['info']['student_id']
            student_name = student_data['info']['student_name']
            
            if not student_id:
                continue
                
            print(f"\n{i+1}. Processing {student_id} - {student_name}")
            
            # Process the data
            processed = processor.process_student(student_data)
            processed_count += 1
            
            # Generate report
            report_path = generator.generate_report(processed)
            report_count += 1
            print(f"   ✓ Report generated: {report_path}")
            
        except Exception as e:
            error_msg = f"Error with row {i+1}: {str(e)}"
            errors.append(error_msg)
            print(f"   ✗ {error_msg}")
    
    # Summary
    print("\n" + "="*60)
    print("BATCH PROCESSING SUMMARY")
    print("="*60)
    print(f"Total rows: {len(raw_rows)}")
    print(f"Processed: {processed_count}")
    print(f"Reports generated: {report_count}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
    
    return processed_count, report_count


# Sample data from our MCP call
sample_data = [
    ["Nathakit Shotiwoth","","s10769","G (AI-2)","Saturday","10:00","11:00","Soumiya","09/08/2025","2","-","","-","02/08/2025","2","LESSON 2 \r\nC2 Machine Learning\r\nC3 Super Leaning & Unsupervised Learning","Soumiya","In Progress","26/07/2025","1","-","Absent","-","19/07/2025","1","L1 Introduction to AI","Soumiya","Completed","12/07/2025","0","-","No Class","-","05/07/2025","0","-","In Break","-","28/06/2025","0","-","No Class","-","21/06/2025","0","-","No Class","-","14/06/2025","0","-","No Class","-","07/06/2025","0","-","No Class","-","31/05/2025","26","L23 Final Project (Presentation): COMPLETED\nL24 Graduation: COMPLETED","Soumiya","Graduated","24/05/2025","25","L23 Final Project (Presentation): IN PROGRESS","Soumiya","In Progress","17/05/2025","24","L22 Final Project (Report Making) COMPLETED (for final presenatation not yet)","Hafiz","Completed","10/05/2025","23","L21 Final Project (Setup + Data Cleaning + Data Analysis): COMPLETED","Soumiya","Completed","03/05/2025","22","-","Absent","-","26/04/2025","22","L21 Final Project (Setup + Data Cleaning + Data Analysis): IN PROGRESS","Soumiya","In Progress","19/04/2025","21","L20 Quiz 2: COMPLETED\nL21 Final Project (Setup + Data Cleaning + Data Analysis): IN PROGRESS","Soumiya","In Progress","12/04/2025","20","L19 Project 4 Google Play Store (Report): COMPLETED","Soumiya","Completed","05/04/2025","19","Teacher Parent Day","No Class","-","29/03/2025"],
    ["Nathan Chee Ying-Cherng","","s10777","F (AI-1)","Saturday","11:00","12:00","Soumiya","09/08/2025","14","-","","-","02/08/2025","14","C13: Data Visualization using Matplotlib","Soumiya","Completed","26/07/2025","13","L22: Final Project Prototype https://www.telebort.com/demo/ai2/project/7  ","Soumiya","Completed","19/07/2025","12","L9: concept 11 Descriptive Statistics\nL10: concept 12 pretty table \nhttps://www.telebort.com/demo/ai1/lesson/12  \nhttps://www.telebort.com/demo/ai1/activity/12   ","Soumiya","In Progress","12/07/2025","11","L10: concept 12 pretty table https://www.telebort.com/demo/ai1/lesson/12  https://www.telebort.com/demo/ai1/activity/12   concept 13 data visualization https://www.telebort.com/demo/ai1/lesson/13  https://www.telebort.com/demo/ai1/activity/13 ","No Class","-","05/07/2025","11","-","Absent","-","28/06/2025","11","L9 Numpy: COMPLETED","Soumiya","Completed","21/06/2025","10","L8 Project 2 Covid-19 Cases Prediction: COMPLETED","Soumiya","Completed","14/06/2025","9","L8 Project 2 Covid-19 Cases Prediction: IN PROGRESS","Soumiya","In Progress","07/06/2025","8","-","No Class","-","31/05/2025","8","L7 Function: COMPLETED\nL7 Package: COMPLETED","Soumiya","Completed","24/05/2025","7","L6 Dictionary : COMPLETED","Soumiya","Completed","17/05/2025","6","L5 P1 Ice Cream Shop: COMPLETED","Hafiz","Completed","10/05/2025","5","L4 Loops : COMPLETED\nL5 P1 Ice Cream Shop: IN PROGRESS","Soumiya","In Progress","03/05/2025","4","L4 Loops: IN PROGRESS","Soumiya","In Progress","26/04/2025","3","L3 Lists: COMPLETED","Soumiya","Completed","19/04/2025","2","L2 Variable & Operator: COMPLETED","Soumiya","Completed","12/04/2025","1","-","Absent","-","05/04/2025","1","Teacher Parent Day","No Class","-","29/03/2025"],
    ["Shawn Lee Shan Wei","","s10710","F (AI-1)","Saturday","12:00","13:00","Soumiya","09/08/2025","7","-","","-","02/08/2025","7","C7: Dictionary","Soumiya","Completed","26/07/2025","6","L2: Concept 3 Variables & Operators https://www.telebort.com/demo/ai1/lesson/3  https://www.telebort.com/demo/ai1/activity/3 https://forms.gle/EzCaqwFv25TbC2qV9 L3: Concept 4 List https://www.telebort.com/demo/ai1/lesson/4 https://www.telebort.com/demo/ai1/activity/4 https://forms.gle/xoyG4q1JrYxi4CkV6 ","Soumiya","Completed","19/07/2025","5","L4: concept 6 activity https://www.telebort.com/demo/ai1/activity/6  L5: project 1 https://www.telebort.com/demo/ai1/project/1 ","Soumiya","Completed","12/07/2025","4","L4: concept 6 activity https://www.telebort.com/demo/ai1/activity/6  L5: project 1 https://www.telebort.com/demo/ai1/project/1 ","No Class","-","05/07/2025","4","-","Absent","-","28/06/2025","4","L3 Conditional Statement: COMPLETED\nL4 Loops: IN PROGRESS","Soumiya","In Progress","21/06/2025","3","L3 List: COMPLETED","Soumiya","Completed","14/06/2025","2","L2 Variable: COMPLETED","Soumiya","Completed","07/06/2025","1","-","No Class","-","31/05/2025","1","L1 Introduction to Python Programming: COMPLETED\nL1 Jupyter Notebook: COMPLETED","Soumiya","Completed","24/05/2025","0","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-"],
]

if __name__ == "__main__":
    # Process the sample batch
    process_student_batch(sample_data)