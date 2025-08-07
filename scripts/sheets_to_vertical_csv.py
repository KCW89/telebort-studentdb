#!/usr/bin/env python3
"""
Transform horizontal Google Sheets data (338 columns) to vertical CSV format
Each row in the output represents one session for one student
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import re

def parse_horizontal_to_vertical(raw_rows):
    """
    Convert horizontal format to vertical format
    Input: 338 columns per student
    Output: One row per session per student
    """
    
    vertical_data = []
    
    # Skip header rows (first 4 rows are headers/instructions)
    data_rows = raw_rows[4:] if len(raw_rows) > 4 else []
    
    for row in data_rows:
        if not row or len(row) < 7:
            continue
            
        # Extract student metadata (first 7 columns)
        student_name = row[0] if len(row) > 0 else ""
        student_id = row[1] if len(row) > 1 else ""
        program = row[2] if len(row) > 2 else ""
        day = row[3] if len(row) > 3 else ""
        start_time = row[4] if len(row) > 4 else ""
        end_time = row[5] if len(row) > 5 else ""
        primary_teacher = row[6] if len(row) > 6 else ""
        
        # Skip if no student ID
        if not student_id or student_id == "-":
            continue
        
        # Process sessions (starting from column 7, in groups of 5)
        # Pattern: Date, Session, Lesson + Link, Attendance, Progress
        session_number = 0
        
        for i in range(7, len(row), 5):
            if i + 4 >= len(row):
                break
                
            date = row[i] if i < len(row) else ""
            session = row[i + 1] if i + 1 < len(row) else ""
            lesson_link = row[i + 2] if i + 2 < len(row) else ""
            attendance = row[i + 3] if i + 3 < len(row) else ""
            progress = row[i + 4] if i + 4 < len(row) else ""
            
            # Skip empty sessions
            if not date or date == "-" or date == "Teacher Parent Day":
                continue
            
            # Parse date
            date_parsed = parse_date(date)
            if not date_parsed:
                continue
                
            session_number += 1
            
            # Determine attendance status
            attendance_status = parse_attendance(attendance)
            
            # Parse lesson title
            lesson_title = parse_lesson(lesson_link)
            
            # Parse progress status
            progress_status = parse_progress(progress)
            
            # Extract teacher from attendance field if it's a name
            session_teacher = ""
            teacher_names = ["Soumiya", "Han Yang", "Khairina", "Arrvinna", "Syahin", 
                           "Hafiz", "Yasmin", "Nurafrina", "Rahmat", "Fatin", 
                           "Aisyah", "Puvin", "Afiqah", "Aaron", "Farah"]
            if attendance in teacher_names:
                session_teacher = attendance
                attendance_status = "Attended"
            
            # Create vertical row
            vertical_row = {
                "Student_ID": student_id,
                "Student_Name": student_name,
                "Program": program,
                "Schedule_Day": day,
                "Schedule_Time": f"{start_time}-{end_time}" if start_time and end_time else "",
                "Primary_Teacher": primary_teacher,
                "Session_Date": date_parsed,
                "Session_Number": session if session and session != "-" else str(session_number),
                "Attendance": attendance_status,
                "Session_Teacher": session_teacher or primary_teacher,
                "Lesson_Topic": lesson_title,
                "Progress": progress_status,
                "Lesson_Link": extract_links(lesson_link),
                "Raw_Lesson_Data": lesson_link if lesson_link != "-" else ""
            }
            
            vertical_data.append(vertical_row)
    
    return vertical_data

def parse_date(date_str):
    """Parse date string to standard format"""
    if not date_str or date_str == "-":
        return ""
    
    # Try different date formats
    formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")  # Standard ISO format
        except:
            continue
    
    return ""  # Return empty if can't parse

def parse_attendance(attendance_str):
    """Normalize attendance status"""
    if not attendance_str:
        return "Not Marked"
    
    attendance_lower = attendance_str.lower().strip()
    
    if "attended" in attendance_lower or attendance_lower in ["soumiya", "han yang", "khairina", 
                                                               "arrvinna", "syahin", "hafiz", 
                                                               "yasmin", "nurafrina", "rahmat", 
                                                               "fatin", "aisyah", "puvin", 
                                                               "afiqah", "aaron", "farah"]:
        return "Attended"
    elif "absent" in attendance_lower:
        return "Absent"
    elif "no class" in attendance_lower:
        return "No Class"
    elif "holiday" in attendance_lower:
        return "Public Holiday"
    elif "break" in attendance_lower:
        return "In Break"
    elif "teacher parent" in attendance_lower:
        return "Teacher Parent Day"
    elif attendance_str == "-":
        return "Not Marked"
    else:
        return attendance_str

def parse_lesson(lesson_str):
    """Extract lesson title from lesson string"""
    if not lesson_str or lesson_str == "-":
        return ""
    
    # Remove URLs
    lesson_clean = re.sub(r'https?://\S+', '', lesson_str)
    
    # Clean up common patterns
    lesson_clean = lesson_clean.replace("COMPLETED", "")
    lesson_clean = lesson_clean.replace("IN PROGRESS", "")
    lesson_clean = lesson_clean.replace("NOT STARTED", "")
    lesson_clean = lesson_clean.replace("\\n", " ")
    lesson_clean = lesson_clean.replace("\\r", " ")
    
    # Trim and clean
    lesson_clean = re.sub(r'\s+', ' ', lesson_clean)
    lesson_clean = lesson_clean.strip()
    
    return lesson_clean

def parse_progress(progress_str):
    """Parse progress status"""
    if not progress_str or progress_str == "-":
        return "Not Started"
    
    progress_lower = progress_str.lower().strip()
    
    if "completed" in progress_lower:
        return "Completed"
    elif "in progress" in progress_lower:
        return "In Progress"
    elif "graduated" in progress_lower:
        return "Graduated"
    elif "not started" in progress_lower:
        return "Not Started"
    else:
        return progress_str

def extract_links(text):
    """Extract URLs from text"""
    if not text:
        return ""
    
    urls = re.findall(r'https?://\S+', text)
    return " | ".join(urls) if urls else ""

def save_to_csv(vertical_data, output_file):
    """Save vertical data to CSV file"""
    if not vertical_data:
        print("No data to save")
        return
    
    # Define column order
    columns = [
        "Student_ID",
        "Student_Name", 
        "Program",
        "Session_Date",
        "Session_Number",
        "Attendance",
        "Session_Teacher",
        "Lesson_Topic",
        "Progress",
        "Schedule_Day",
        "Schedule_Time",
        "Primary_Teacher",
        "Lesson_Link",
        "Raw_Lesson_Data"
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(vertical_data)
    
    print(f"✅ Saved {len(vertical_data)} session records to {output_file}")

def main():
    """Main function to process Google Sheets data"""
    
    # For now, we'll use the sample data we fetched
    # In production, this would fetch all data from Google Sheets
    
    print("🔄 Transforming Google Sheets data to vertical CSV format...")
    
    # Load the sample data (replace with actual Google Sheets fetch)
    # This is just a demonstration with the 10 rows we fetched
    sample_data = """[[\"👋 Hello Teachers, As mentioned in WhatsApp, we are now using Sandbox 4.5 — same link, just a new look and layout. Let's keep updating weekly. Thanks and happy teaching! 😊

📽️ Tutorial video:
👉 https://youtu.be/arqWWRFT9Ek 

-----------------------------------------------------------------------------

Blue Columns = Fixed Columns throughout the programs\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"🟢 Green Columns = Auto\", \"\", \"🟠 Columns to fill in (orange):\"], [\"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"Date & Session update automatically every week\", \"\", \"Lesson what was/will be taught, 
and any materials (links)\", \"write your name if student attended, 
or use "Absent", "In Break", "No Class"\", \"use Graduated if student completed 24 lessons\"], [], [\"Student Name\", \"Student ID\", \"Current Program\", \"Day\", \"StartTime\", \"EndTIme\", \"Teacher\", \"Date\", \"Session\", \"Lesson + Link\", \"Attendance\", \"Progress\", \"Date\", \"Session\", \"Lesson + Link\", \"Attendance\", \"Progress\"], [\"Nathakit Shotiwoth\", \"s10769\", \"G (AI-2)\", \"Saturday\", \"10:00\", \"11:00\", \"Soumiya\", \"02/08/2025\", \"1\", \"-\", \"-\", \"-\", \"26/07/2025\", \"1\", \"L23: Final Project Presentation https://forms.gle/pRfur6DwG7ALV3om6 https://forms.gle/SrSSMZQj9tLuXGE48 \", \"Absent\", \"-\", \"19/07/2025\", \"1\", \"L1 Introduction to AI\", \"Soumiya\", \"Completed\"], [\"Nathan Chee Ying-Cherng\", \"s10777\", \"F (AI-1)\", \"Saturday\", \"11:00\", \"12:00\", \"Soumiya\", \"02/08/2025\", \"13\", \"-\", \"-\", \"-\", \"26/07/2025\", \"13\", \"L22: Final Project Prototype https://www.telebort.com/demo/ai2/project/7  \", \"Soumiya\", \"Completed\", \"19/07/2025\", \"12\", \"L9: concept 11 Descriptive Statistics
L10: concept 12 pretty table 
https://www.telebort.com/demo/ai1/lesson/12  
https://www.telebort.com/demo/ai1/activity/12   \", \"Soumiya\", \"In Progress\"]]"""
    
    # Parse the JSON string
    raw_rows = json.loads(sample_data)
    
    # Transform to vertical format
    vertical_data = parse_horizontal_to_vertical(raw_rows)
    
    # Create output directory
    output_dir = Path("data/vertical_csv")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"telebort_sessions_vertical_{timestamp}.csv"
    save_to_csv(vertical_data, output_file)
    
    # Print summary
    if vertical_data:
        print(f"\n📊 Summary:")
        print(f"  - Total sessions: {len(vertical_data)}")
        
        # Count unique students
        unique_students = set(row["Student_ID"] for row in vertical_data)
        print(f"  - Unique students: {len(unique_students)}")
        
        # Count by attendance
        attendance_counts = {}
        for row in vertical_data:
            status = row["Attendance"]
            attendance_counts[status] = attendance_counts.get(status, 0) + 1
        
        print(f"\n  Attendance breakdown:")
        for status, count in sorted(attendance_counts.items()):
            print(f"    - {status}: {count}")
        
        print(f"\n📁 Output file: {output_file}")
        print("\n✨ This CSV is ready to import into Google Sheets!")
        print("   Simply open Google Sheets and use File > Import to load this CSV")

if __name__ == "__main__":
    main()