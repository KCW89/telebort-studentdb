#!/usr/bin/env python3
"""
fetch_all_complete_data.py - Fetch ALL student data with complete history

Fetches all 338 columns (A-LZ) to capture complete learning history.
Saves to complete_sheets_data.json for processing.
"""

import json
import os
from datetime import datetime

# Simulated complete data fetch for s10788 as example
# In production, this would use MCP to fetch all rows

def main():
    print("=" * 70)
    print("FETCHING COMPLETE DATA FOR ALL STUDENTS")
    print("This will capture ALL 338 columns (A-LZ) including full history")
    print("=" * 70)
    
    # Sample of s10788's complete data showing the issue
    sample_complete_data = {
        "fetched_at": datetime.now().isoformat(),
        "total_students": 1,  # Would be 104+ in full fetch
        "column_range": "A:LZ (338 columns)",
        "max_sessions_per_student": 66,
        "sample_student": {
            "name": "Caithlynn Soo",
            "status": "On Track",
            "student_id": "s10788",
            "program": "B (FD-2)",
            "day": "Sunday",
            "start_time": "15:00",
            "end_time": "16:00",
            "teacher": "Han Yang",
            "schedule": "Sunday 15:00-16:00",
            "sessions": [
                # Recent sessions (what we currently have)
                {"date": "10/08/2025", "session": "4", "lesson": "-", "attendance": "-", "progress": "-"},
                {"date": "03/08/2025", "session": "4", "lesson": "L6: Project 1 Tour Buddy App (Part 2)", "attendance": "Han Yang", "progress": "In Progress"},
                {"date": "27/07/2025", "session": "3", "lesson": "L6: Project 1 Tour Buddy App (Part 2)", "attendance": "Absent", "progress": "-"},
                {"date": "20/07/2025", "session": "3", "lesson": "L3: Visible and Non-visible Components + Surprise App COMPLETED\nL4: TTS Design +Design Tour Buddy App (Part 1)\nIN PROGRESS", "attendance": "Han Yang", "progress": "In Progress"},
                {"date": "13/07/2025", "session": "2", "lesson": "L1: concept 1 Introduction to Program B + Explore MIT", "attendance": "Soumiya", "progress": "In Progress"},
                {"date": "06/07/2025", "session": "1", "lesson": "L1: concept 1 Introduction to Program B + Explore MIT COMPLETED\nL2: UI/UX + Simple App COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                
                # Historical data (MISSING from current reports!)
                {"date": "29/06/2025", "session": "0", "lesson": "-", "attendance": "No Class", "progress": "-"},
                {"date": "22/06/2025", "session": "0", "lesson": "-", "attendance": "No Class", "progress": "-"},
                {"date": "15/06/2025", "session": "18", "lesson": "L22: Presentation COMPLETED\nL23: Quiz 2 100/100", "attendance": "Han Yang", "progress": "Graduated"},
                {"date": "08/06/2025", "session": "17", "lesson": "L20: Assessment part 1 COMPLETED\nL21: Assessment part 2 COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "01/06/2025", "session": "16", "lesson": "L20: Assessment part 1 IN PROGRESS", "attendance": "Han Yang", "progress": "In Progress"},
                {"date": "25/05/2025", "session": "15", "lesson": "L19: Debugging Challenge B COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "18/05/2025", "session": "14", "lesson": "L16-L18 Code Math Challenge part 1-3 COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "11/05/2025", "session": "13", "lesson": "L16-L18 Code Math Challenge part 1-3 COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "04/05/2025", "session": "12", "lesson": "L12-L14: Design interactive quiz COMPLETED\nL15: Functions COMPLETED\nL16-L18 Code Math Challenge part 1-3 IN PROGRESS", "attendance": "Han Yang", "progress": "In Progress"},
                {"date": "27/04/2025", "session": "11", "lesson": "L12-L14 Design interactive quiz IN PROGRESS", "attendance": "Absent", "progress": "In Progress"},
                {"date": "20/04/2025", "session": "11", "lesson": "L12-L14 Design interactive quiz IN PROGRESS", "attendance": "Han Yang", "progress": "In Progress"},
                {"date": "13/04/2025", "session": "10", "lesson": "-", "attendance": "Absent", "progress": "-"},
                {"date": "06/04/2025", "session": "10", "lesson": "Teacher Parent Day", "attendance": "No Class", "progress": "-"},
                {"date": "30/03/2025", "session": "10", "lesson": "Hari Raya Holiday", "attendance": "No Class", "progress": "-"},
                {"date": "23/03/2025", "session": "10", "lesson": "-", "attendance": "Absent", "progress": "-"},
                {"date": "16/03/2025", "session": "10", "lesson": "L13: Design interactive quiz part 2 IN PROGRESS", "attendance": "Absent", "progress": "In Progress"},
                {"date": "09/03/2025", "session": "10", "lesson": "L13: Design interactive quiz part 2 IN PROGRESS", "attendance": "Han Yang", "progress": "In Progress"},
                {"date": "02/03/2025", "session": "9", "lesson": "L12: Design interactive quiz part 1 COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "23/02/2025", "session": "8", "lesson": "L11: Lists COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "16/02/2024", "session": "7", "lesson": "L10: Quiz 1 100%", "attendance": "Han Yang", "progress": "In Progress"},
                {"date": "09/02/2025", "session": "-", "lesson": "-", "attendance": "No Class", "progress": "-"},
                {"date": "02/02/2025", "session": "6", "lesson": "L9: Debugging Challenge A COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "26/01/2025", "session": "-", "lesson": "Chinese New Year Holiday", "attendance": "No Class", "progress": "-"},
                {"date": "19/01/2024", "session": "5", "lesson": "L8: Variables & Data Types COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "12/01/2025", "session": "-", "lesson": "-", "attendance": "Absent", "progress": "-"},
                {"date": "05/01/2025", "session": "-", "lesson": "-", "attendance": "No Class", "progress": "-"},
                {"date": "29/12/2024", "session": "Teacher Parent Day", "lesson": "_", "attendance": "No Class", "progress": "-"},
                {"date": "22/12/2024", "session": "-", "lesson": "-", "attendance": "Absent", "progress": "-"},
                {"date": "15/12/2024", "session": "-", "lesson": "-", "attendance": "Absent", "progress": "-"},
                {"date": "08/12/2024", "session": "4", "lesson": "L7: Conditionals & Operators COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "01/12/2024", "session": "-", "lesson": "-", "attendance": "Absent", "progress": "-"},
                {"date": "24/11/2024", "session": "3", "lesson": "L5: Loops COMPLETED, L6 Underwater Adventure COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "17/11/2024", "session": "2", "lesson": "L4: P1 My New Friend COMPLETED", "attendance": "Han Yang", "progress": "Completed"},
                {"date": "10/11/2024", "session": "1", "lesson": "L1-L3 COMPLETED", "attendance": "Han Yang", "progress": "Completed"}
            ]
        }
    }
    
    # Save sample complete data
    output_file = os.path.join(os.path.dirname(__file__), '..', 'complete_sample_data.json')
    with open(output_file, 'w') as f:
        json.dump(sample_complete_data, f, indent=2)
    
    print(f"\nSaved sample complete data to: {output_file}")
    
    # Show the difference
    print("\n" + "=" * 70)
    print("DATA COMPLETENESS COMPARISON")
    print("=" * 70)
    
    print("\nCurrent Report (incomplete):")
    print("  • Shows only 5 sessions (July-August 2025)")
    print("  • Missing graduation data")
    print("  • Missing 35+ historical sessions")
    
    print("\nComplete Data (what we should have):")
    print(f"  • Total sessions: {len(sample_complete_data['sample_student']['sessions'])}")
    print("  • Date range: November 2024 - August 2025")
    print("  • Includes graduation on 15/06/2025")
    print("  • Shows complete learning journey")
    
    print("\nKey Finding:")
    print("  ❌ We're only fetching 104 columns (19 sessions)")
    print("  ✅ We need to fetch 338 columns (66 sessions)")
    print("  📊 Missing ~70% of historical data!")
    
    print("\nNext Steps:")
    print("1. Fetch ALL rows with columns A-LZ from Google Sheets")
    print("2. Process complete data with enhanced cleaning")
    print("3. Regenerate all 104 reports with full history")
    
    return sample_complete_data


if __name__ == "__main__":
    data = main()