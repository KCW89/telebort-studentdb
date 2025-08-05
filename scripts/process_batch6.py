#!/usr/bin/env python3
"""
Process final batch of students from Google Sheets (rows 105-111)
Generated: 2025-08-05
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.sync_sheets_mcp import SheetsSyncManager
from scripts.process_data import DataProcessor
from scripts.generate_reports import ReportGenerator

# Raw data from Google Sheets MCP call (rows 105-111)
# Only including rows with actual student data
raw_data = [
    ["03/08/2025", "11", "-", "-", "-", "27/07/2025", "11", "L8: Concept 6 Variables and Data Types https://www.telebort.com/demo/f1/lesson/6 https://www.telebort.com/demo/f1/activity/6 https://forms.gle/E79J2hfbYGVDtZGz9 ", "Rahmat", "-", "20/07/2025", "10", "L8: Variables and Data Types", "Rahmat", "In Progress", "13/07/2025", "9", "L8: Variables and Data Types", "Rahmat", "In Progress", "06/07/2025", "8", "L7: Conditionals and Operators\n+\nL8: Variables and Data Types", "Rahmat", "-", "29/06/2025", "7", "-", "Rahmat"],
    ["02/08/2025", "13", "-", "-", "-", "26/07/2025", "12", "L11: Concept 9 Python Turtle Graphics Library https://www.telebort.com/demo/bbp/lesson/9 https://www.telebort.com/demo/bbp/activity/9 https://forms.gle/6J1SxXieuz5YHzt89 ", "Rahmat", "-", "19/07/2025", "11", "L11: concept 9 notes & activity https://www.telebort.com/demo/bbp/lesson/9 https://www.telebort.com/demo/bbp/activity/9 ", "Absent", "-", "12/07/2025", "10", "L11: concept 9 notes & activity https://www.telebort.com/demo/bbp/lesson/9 https://www.telebort.com/demo/bbp/activity/9 ", "No Class", "-", "05/07/2025", "10", "-", "Absent", "-", "28/06/2025", "9", "L9: Functions", "Rahmat"],
    ["03/08/2025", "13", "-", "-", "-", "27/07/2025", "13", "", "Rahmat", "-", "20/07/2025", "11", "-", "Absent", "In Progress", "13/07/2025", "11", "-", "Rahmat", "In Progress", "06/07/2025", "10", "-", "Absent", "-", "29/06/2025", "10", "L10:Functions (Extra)", "Rahmat"],
    ["03/08/2025", "28", "-", "-", "-", "27/07/2025", "28", "L24: Graduation", "Rahmat", "Completed", "20/07/2025", "27", "L18: project scientific calculator https://www.telebort.com/demo/bbp/project/3 then proceed with L22 revision quiz 2 https://docs.google.com/presentation/d/1wJLrRoRX6aLTwgStpqcGYum3Y_DyoRmORIfFT7aq6H0/edit?usp=sharing , L23 quiz 2, https://forms.gle/peNfj8yeyS1C4tZa6  L24 graduation", "Rahmat", "Completed", "13/07/2025", "26", "L18: project scientific calculator https://www.telebort.com/demo/bbp/project/3 then proceed with L22 revision quiz 2 https://docs.google.com/presentation/d/1wJLrRoRX6aLTwgStpqcGYum3Y_DyoRmORIfFT7aq6H0/edit?usp=sharing , L23 quiz 2, https://forms.gle/peNfj8yeyS1C4tZa6  L24 graduation", "Rahmat", "In Progress", "06/07/2025", "25", "-", "Absent", "-", "29/06/2025", "25", "Lesson 20: Python Math Module", "Rahmat"],
    ["03/08/2025", "33", "-", "-", "-", "27/07/2025", "33", "L22: Final Project (Part 3) https://www.telebort.com/demo/bbd/project/4 https://forms.gle/6x49UfWEhQ3Rn5LC9 ", "Absent", "-", "20/07/2025", "33", "L22: final project Part 3 https://www.telebort.com/demo/bbd/project/4 ", "Rahmat", "In Progress", "13/07/2025", "32", "L22: final project Part 3 https://www.telebort.com/demo/bbd/project/4 ", "Rahmat", "In Progress", "06/07/2025", "31", "L21:Final Project (Part 2) - Wireframe", "Rahmat", "-", "29/06/2025", "30", "L20: Final Project (P1)", "Puvin"],
    ["03/08/2025", "16", "-", "-", "-", "27/07/2025", "16", "Debugging Challenge", "Rahmat", "Completed", "20/07/2025", "15", "Digital Playground Part (3) + Debugging Challenge", "Rahmat", "Completed", "13/07/2025", "14", "Digital Playground Part (2)", "Rahmat", "In Progress", "06/07/2025", "13", "Digital Playground Part (1)", "Absent", "-", "29/06/2025", "13", "Lesson 19: Maze Runner (Part 2)\n+\nLesson 17: Debugging Challenge", "Rahmat"],
    ["03/08/2025", "19", "-", "-", "-", "27/07/2025", "19", "L16: Concept 11 Interactive Data Visualization with Pygal https://www.telebort.com/demo/bbp/lesson/11 https://www.telebort.com/demo/bbp/activity/11 https://forms.gle/5jkwm91qNuL6hmsA8 ", "Absent", "-", "20/07/2025", "19", "L15: Picasso Art", "Rahmat", "Completed", "13/07/2025", "18", "L14: racing turtle Part 2 https://www.telebort.com/demo/bbp/project/1 ", "Rahmat", "Completed", "06/07/2025", "17", "L13:Project: Racing Turtles (Part 1)", "Rahmat", "-", "29/06/2025", "16", "L12:Loops", "Rahmat"]
]

# Student IDs corresponding to rows 105-111
student_ids = [
    "s10787",  # Row 105
    "s10788",  # Row 106
    "s10789",  # Row 107
    "s10796",  # Row 108
    "s10801",  # Row 109
    "s10802",  # Row 110
    "s10805"   # Row 111
]

# Student names extracted from row 3 of the Google Sheet
student_names = [
    "Elham Akbarian",      # s10787
    "Luke Tan Jia Le",     # s10788
    "See Ming Hong",       # s10789
    "Lim Wen Yang",        # s10796
    "Shanteal Khor Khye Nee",  # s10801
    "Jonas Wee Jing Hang", # s10802
    "Tham Zi Xiang"        # s10805
]

def process_student_batch(raw_rows):
    """Process a batch of student data from raw Google Sheets rows"""
    processor = DataProcessor()
    generator = ReportGenerator()
    
    processed_count = 0
    error_count = 0
    
    for i, row_data in enumerate(raw_rows):
        try:
            student_id = student_ids[i]
            student_name = student_names[i]
            
            print(f"\n{i+1}. Processing {student_id} - {student_name}")
            
            # Parse sessions from the repeating column pattern
            sessions = []
            current_index = 0
            
            while current_index + 5 <= len(row_data):
                # Extract one session's data (5 columns: Date, Session, Lesson, Attendance, Progress)
                date = str(row_data[current_index]) if row_data[current_index] else ''
                session_num = str(row_data[current_index + 1]) if row_data[current_index + 1] else ''
                lesson = str(row_data[current_index + 2]) if row_data[current_index + 2] else ''
                attendance = str(row_data[current_index + 3]) if row_data[current_index + 3] else ''
                progress = str(row_data[current_index + 4]) if row_data[current_index + 4] else ''
                
                # Only add sessions with valid dates
                if date and date != '-':
                    sessions.append({
                        'date': date,
                        'session': session_num,
                        'lesson': lesson,
                        'attendance': attendance,
                        'progress': progress
                    })
                
                current_index += 5
            
            # Create student data structure
            student_data = {
                'info': {
                    'student_id': student_id,
                    'student_name': student_name,
                    'program': '',  # Not available in this batch
                    'day': '',      # Not available in this batch
                    'start_time': '',  # Not available in this batch
                    'end_time': '',    # Not available in this batch
                    'teacher': ''      # Not available in this batch
                },
                'sessions': sessions
            }
            
            # Process the data
            processed_data = processor.process_student(student_data)
            
            # Generate report
            report_path = generator.generate_report(processed_data)
            print(f"   ✓ Report generated: {report_path}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"   ✗ Error processing {student_id}: {str(e)}")
            error_count += 1
    
    return processed_count, error_count

def main():
    print("Processing final batch of 7 students...")
    
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