#!/usr/bin/env python3
"""
Process batch 7 of students from Google Sheets (rows 10-24)
Generated: 2025-08-05
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.sync_sheets_mcp import SheetsSyncManager
from scripts.process_data import DataProcessor
from scripts.generate_reports import ReportGenerator

# Raw data from Google Sheets MCP call (rows 10-24)
raw_data = [
    ["Josiah Hoo En Yi", "s10569", "BBP", "Saturday", "17:00", "19:00", "Soumiya", "02/08/2025", "19", "-", "-", "-", "26/07/2025", "19", "L1: Concept 2 Jupyter Notebook  https://www.telebort.com/demo/ai1/lesson/2 https://www.telebort.com/demo/ai1/activity/2 https://forms.gle/uLTj2zspLYciMmkV8 ", "Soumiya", "In Progress", "19/07/2025", "18", "Lesson 1: Introduction to Python\r\nLesson 2: Jupyter Notebook\r\nLesson 3: Variables & Operators", "Soumiya", "In Progress", "12/07/2025", "17", "L24: Graduation https://forms.gle/PeS4pRvbWBF7czr96  https://forms.gle/jWiufwDrj9UrrxRB6 ", "No Class", "-", "05/07/2025", "17", "L21: Project: Scientific Calculator COMPLETED\nL22: Revision Quiz 2 8/11\nL23: Quiz 2 90/100", "Han Yang", "Completed", "28/06/2025", "16", "L20: Python Math Module COMPLETED", "Han Yang"],
    ["Lee Chong Tatt", "s10608", "D (W-2)", "Sunday", "10:00", "12:00", "Soumiya", "03/08/2025", "0", "-", "-", "-", "27/07/2025", "20", "L22: Final Project (Part 2)\nL23: Quiz 2\nL24: Graduation", "Soumiya", "Graduated", "20/07/2025", "19", "L23: Calorie counter part 2 https://www.telebort.com/demo/w2/project/6 ", "Soumiya", "In Progress", "13/07/2025", "18", "L22 calorie counter part 1 https://www.telebort.com/demo/w2/project/6", "Soumiya", "Completed", "06/07/2025", "17", "L20 Final Project (Calorie Calculator Part 1): IN PROGRESS", "Soumiya", "Completed", "29/06/2025", "16", "L19 Mini Project 5: COMPLETED", "Soumiya"],
    ["Lee Xuen Ni", "s10609", "D (W-2)", "Sunday", "10:00", "12:00", "Soumiya", "03/08/2025", "0", "-", "-", "-", "27/07/2025", "20", "L23: Quiz 2\nL24: Graduation", "Soumiya", "Graduated", "20/07/2025", "19", "quiz 2  https://forms.gle/vAPNXoE7RJ1N83ZH6", "Soumiya", "In Progress", "13/07/2025", "18", "L22 calorie counter part 1 https://www.telebort.com/demo/w2/project/6\nL23 calorie counter part 2 https://www.telebort.com/demo/w2/project/6", "Soumiya", "Completed", "06/07/2025", "17", "L20 Final Project (Calorie Calculator Part 1): IN PROGRESS\n", "Soumiya", "In Progress", "29/06/2025", "16", "L19 Mini Project 5: COMPLETED", "Soumiya"],
    ["Lim Jia Sheng", "s10707", "F (AI-1)", "Sunday", "10:00", "12:00", "Soumiya", "03/08/2025", "6", "-", "-", "-", "27/07/2025", "6", "L4: Concept 4 Control Flow https://www.telebort.com/demo/w2/lesson/4  https://www.telebort.com/demo/w2/activity/4 https://forms.gle/qJXapV5TVKJXLP4e6 ", "Soumiya", "Completed", "20/07/2025", "5", "L3: concept 4 List https://www.telebort.com/demo/ai1/lesson/4 https://www.telebort.com/demo/ai1/activity/4   ", "Soumiya", "In Progress", "13/07/2025", "4", "L2: concept 3 variables& operators  notes & activity ", "Soumiya", "Completed", "06/07/2025", "3", "L1 Jupyter Notebook: COMPLETED", "Soumiya", "In Progress", "29/06/2025", "2", "L1 Introduction to Python Programming: COMPLETED\nL1 Jupyter Notebook: IN PROGRESS", "Soumiya"],
    ["Felicia P'ng Wei Xing", "s10809", "F (AI-1)", "Sunday", "11:00", "12:00", "Soumiya", "03/08/2025", "-", "-", "-", "-", "27/07/2025", "3", "L2 Variables & Operators", "Soumiya", "Completed", "20/07/2025", "2", "L1: concept 1 notes & activity", "Soumiya", "Completed", "13/07/2025", "1", "L1: concept 1 notes & activity", "Soumiya", "In Progress", "06/07/2025", "0", "-", "No Class", "-", "29/06/2025", "-", "-", "-"],
    ["Justin Kang Yoong Ming", "s10510", "C (W-1)", "Sunday", "14:00", "16:00", "Soumiya", "03/08/2025", "10", "-", "-", "-", "27/07/2025", "10", "L10 & L11: my holiday part 3 & Part 4 https://www.telebort.com/demo/w1/project/3 ", "Soumiya", "In Progress", "20/07/2025", "9", "L11: my holiday part 3  https://www.telebort.com/demo/w1/project/3 ", "Soumiya", "-", "13/07/2025", "8", "L10: project 3 my holiday part 1 https://www.telebort.com/demo/w1/project/3", "Soumiya", "Completed", "06/07/2025", "7", "L8: My Holiday Part 1: IN PROGRESS", "Soumiya", "In Progress", "29/06/2025", "6", "L7: CSS Display & Flexbox: COMPLETED", "Soumiya"],
    ["Teoh Wei Lynn", "s10708", "C (W-1)", "Sunday", "14:00", "16:00", "Soumiya", "03/08/2025", "7", "-", "-", "-", "27/07/2025", "7", "L8: concept 7&8 CSS Display + CSS Flexbox https://www.telebort.com/demo/w1/lesson/7  https://www.telebort.com/demo/w1/activity/7  https://www.telebort.com/demo/w1/lesson/8 https://www.telebort.com/demo/w1/activity/8 ", "Soumiya", "Completed", "20/07/2025", "6", "L8: concept 7&8 CSS Display + CSS Flexbox https://www.telebort.com/demo/w1/lesson/7  https://www.telebort.com/demo/w1/activity/7  https://www.telebort.com/demo/w1/lesson/8 https://www.telebort.com/demo/w1/activity/8 ", "Absent", "-", "13/07/2025", "6", "L7: concept 5 notes+activity https://www.telebort.com/demo/w1/lesson/5 https://www.telebort.com/demo/w1/activity/5 & 6 notes+activity https://www.telebort.com/demo/w1/lesson/6 https://www.telebort.com/demo/w1/activity/6 ", "Soumiya", "Completed", "06/07/2025", "5", "L6 HTML Content Division & CSS Box Model: IN PROGRESS", "Soumiya", "In Progress", "29/06/2025", "4", "L5 CSS Selector: COMPLETED", "Soumiya"],
    ["Klarixa Joli Ramesh", "s10767", "D (W-2)", "Sunday", "16:30", "17:30", "Soumiya", "03/08/2025", "4", "-", "-", "-", "27/07/2025", "4", "L4: Concept 4 Control Flow https://www.telebort.com/demo/w2/lesson/4  https://www.telebort.com/demo/w2/activity/4 https://forms.gle/qJXapV5TVKJXLP4e6 ", "Soumiya", "In Progress", "20/07/2025", "3", "L1-L3", "Soumiya", "Completed", "13/07/2025", "2", "L1: concept 1 notes & activity https://www.telebort.com/demo/w2/activity/1 ", "Soumiya", "Completed", "06/07/2025", "1", "L1: concept 1 notes & activity https://www.telebort.com/demo/w2/activity/1 ", "Soumiya", "In Progress", "29/06/2025", "0", "-", "No Class"],
    ["Hadi Imran Bin Hayazi", "s10360", "D (W-2)", "Sunday", "17:00", "18:00", "Soumiya", "03/08/2025", "13", "-", "-", "-", "27/07/2025", "13", " L9: Revision & Quiz 1 https://docs.google.com/presentation/d/1zKfCB5MyMlpGfrR1IuVXri-cD7gizJjEXIXgXjtwXWU/edit?usp=sharing https://forms.gle/GqbLV9z5WsEGZ1EM8 ", "Soumiya", "Completed", "20/07/2025", "12", "L7: concept 6 notes & activity https://www.telebort.com/demo/w2/lesson/6 https://www.telebort.com/demo/w2/activity/6 \nL10: Array Part 1", "Soumiya", "In Progress", "13/07/2025", "11", "L7: concept 6 notes & activity https://www.telebort.com/demo/w2/lesson/6 https://www.telebort.com/demo/w2/activity/6 ", "Soumiya", "In Progress", "06/07/2025", "10", "L6 Mini Project BMI Calculator: COMPLETED", "Soumiya", "Completed", "29/06/2025", "9", "L5 Loops: COMPLETED", "Soumiya"],
    ["Ravio Reinhart Sianipar", "s10808", "C (W-1)", "Sunday", "11:00", "12:00", "Syahin", "03/08/2025", "2", "-", "-", "-", "27/07/2025", "2", "L20: Final Project (Part 1) https://www.telebort.com/demo/bbd/project/4  https://forms.gle/9HmphJYq8on865AcA  L21: Final Project (Part 2) https://forms.gle/8v5Qtyu4TqFs6snW8 ", "No Class", "-", "20/07/2025", "2", "L2: concept 2 activity https://www.telebort.com/demo/w1/activity/2  then continue with L3: project 1 https://www.telebort.com/demo/w1/project/1 ", "No Class", "In Progress", "13/07/2025", "2", "L2: concept 2 activity https://www.telebort.com/demo/w1/activity/2  then continue with L3: project 1 https://www.telebort.com/demo/w1/project/1 ", "Absent", "In Progress", "06/07/2025", "2", "L2\nIntroduction to HTML: DONE\n\nExercise: DOING", "Syahin", "In Progress", "29/06/2025", "1", "L1\nIntroduction to Web Design: DONE\n\nSetup GitHub & Stackblitz", "Syahin"],
    ["Too U-Gyrn", "s10726", "BBP", "Sunday", "14:00", "16:00", "Syahin", "03/08/2025", "30", "-", "-", "-", "27/07/2025", "30", "L24: Graduation  https://forms.gle/NMcQPXCijBgjHigL9  https://forms.gle/AFRP1NsjPn78g1Q4A ", "Nurafrina", "In Progress", "20/07/2025", "29", "L18: Project: My Quiz Game (Basic) https://www.telebort.com/demo/bbp/project/4 ", "Nurafrina", "In Progress", "13/07/2025", "28", "L17: Project: Nutritious Meal https://www.telebort.com/demo/bbp/project/5  https://dashboard.telebort.me/training/learningPlan/63e3715442b65c4edbaa6c70", "Syahin", "Completed", "06/07/2025", "27", "Quiz 1", "Syahin", "Completed", "29/06/2025", "26", "L17 Project: Nutritious Meal (Part 2): \nONGOING", "Syahin"],
    ["Yashvid Daryl Kumar", "s10723", "BBP", "Sunday", "14:00", "16:00", "Syahin", "03/08/2025", "0", "-", "-", "-", "27/07/2025", "0", "L9: Concept 8 AI Coding with IDE https://www.telebort.com/demo/ai3/lesson/8 https://www.telebort.com/demo/ai3/activity/8 https://forms.gle/6AruKFm38vR1oES38 ", "No Class", "-", "20/07/2025", "0", "L1: concept 1 notes & activity https://www.telebort.com/demo/w1/lesson/1 https://www.telebort.com/demo/w1/activity/1 ", "In Break", "-", "13/07/2025", "0", "L1: concept 1 notes & activity https://www.telebort.com/demo/w1/lesson/1 https://www.telebort.com/demo/w1/activity/1 ", "In Break", "-", "06/07/2025", "29", "GRADUATION", "Syahin", "Graduated", "29/06/2025", "28", "Quiz 2:\nCOMPLETED", "Syahin"],
    ["Jiwoo Kim", "s10084", "H (BBD)", "Saturday", "17:00", "19:00", "Khairina", "02/08/2025", "25", "-", "-", "-", "26/07/2025", "25", "L9: Quiz 1 https://forms.gle/5zeDUwKQnd12oRdSA + Concept 8 AI Coding with IDE https://www.telebort.com/demo/ai3/lesson/8 https://www.telebort.com/demo/ai3/activity/8 https://forms.gle/6AruKFm38vR1oES38 ", "No Class", "-", "19/07/2025", "25", "L19: quiz 2 revision quiz link  L20: https://docs.google.com/document/d/1IwVrL_HXIg-ENfpn67vOVCKTE7xvo8ncHO_Eol5NtCo/edit?usp=sharing ", "Khairina", "In Progress", "12/07/2025", "24", "L19: quiz 2 revision quiz link ", "No Class", "-", "05/07/2025", "24", "L18 Exercise\nAI Application Interfaces: \n\nL19 Quiz 2\n", "Khairina", "Completed", "28/06/2025", "23", "L16 MP3\nPrototyping Web Apps: Done\n\nL17 Excercise\nIntroduction to AI-First Applications: Done", "Khairina"],
    ["Cheng Hao Wen", "s10100", "H (BBD)", "Saturday", "17:00", "19:00", "Khairina", "02/08/2025", "30", "-", "-", "-", "26/07/2025", "30", "L9: Concept 10 Text Processing in NLP https://www.telebort.com/demo/ai2/lesson/10 https://www.telebort.com/demo/ai2/activity/10 https://forms.gle/nivVu9aGjRbcFvq17 ", "No Class", "-", "19/07/2025", "30", "L23: part 4 project presentation https://www.telebort.com/demo/bbd/project/4      https://www.figma.com/design/clK3I2Z2o0NUgCz79QD1rE/Untitled?node-id=0-1&p=f&t=RgDtnayyXGgSFKe3-0", "Khairina", "Completed", "12/07/2025", "29", "L23: part 4 project presentation https://www.telebort.com/demo/bbd/project/4 ", "No Class", "-", "05/07/2025", "29", "L21 Final Project\n(Part 2) - Wireframe\n\nL22 Final Project\n(Part 3) - Portfolio Building", "Khairina", "Completed", "28/06/2025", "28", "L20 Final Project\n(Part 1) - Analysis: Done\n\nL21 Final Project\n(Part 2) - Wireframe", "Khairina"],
    ["Tew Jae Fung", "s10779", "D (W-2)", "Saturday", "12:00", "13:00", "Han Yang", "02/08/2025", "8", "-", "-", "-", "26/07/2025", "8", "based on previous lessons & progress, havent done L4: Concept 4 Control Flow https://www.telebort.com/demo/W2/lesson/4 https://www.telebort.com/demo/W2/activity/4 https://forms.gle/qZ2c5Fy6TJ8eRURP8 after done with C4 proceed with L7: Concept 6 Functions https://www.telebort.com/demo/W2/lesson/6 https://www.telebort.com/demo/W2/activity/6 https://forms.gle/cAg6qP3u1K3fYiBv5 ", "Soumiya", "Completed", "19/07/2025", "7", "L6: project 1  ", "Han Yang", "Completed", "12/07/2025", "6", "L6: project 1 https://www.telebort.com/demo/w2/project/1 ", "No Class", "-", "05/07/2025", "6", "L6: project 1 https://www.telebort.com/demo/w2/project/1 ", "Han Yang", "In Progress", "28/06/2025", "5", "L5: Loops IN PROGRESS", "Han Yang"]
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
            
            # Create full row data structure for parsing
            full_row = row_data  # Already has all columns
            
            # Parse the row using the sync manager
            student_data = sync_manager.parse_student_sessions(full_row)
            
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
    print("Processing batch 7 of 15 students (rows 10-24)...")
    
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