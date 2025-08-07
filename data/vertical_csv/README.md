# Vertical CSV Data for Google Sheets

## Overview
This directory contains student session data transformed from horizontal format (338 columns) to vertical format for easier analysis and Google Sheets import.

## File Structure
Each row represents one session for one student with the following columns:
- **Student_ID**: Unique student identifier (e.g., s10769)
- **Student_Name**: Full name of the student
- **Program**: Current program enrolled (e.g., G (AI-2), BBP, etc.)
- **Session_Date**: Date of the session (YYYY-MM-DD format)
- **Session_Number**: Session number or identifier
- **Attendance**: Attendance status (Attended, Absent, No Class, etc.)
- **Session_Teacher**: Teacher who conducted the session
- **Lesson_Topic**: Clean lesson title/topic
- **Progress**: Progress status (Completed, In Progress, Not Started, Graduated)
- **Schedule_Day**: Regular schedule day
- **Schedule_Time**: Regular schedule time slot
- **Primary_Teacher**: Primary assigned teacher
- **Lesson_Links**: Extracted URLs from lesson materials

## Latest Export
- **File**: `telebort_all_sessions_vertical_20250806_232159.csv`
- **Total Records**: 4,525 sessions
- **Unique Students**: 97
- **Date Range**: 2024-2025 academic year
- **File Size**: 488 KB

## Statistics
### Attendance (4,525 sessions)
- Attended: 2,888 (63.8%)
- Absent: 491 (10.9%)
- No Class: 702 (15.5%)
- Not Marked: 203 (4.5%)
- Other: 241 (5.3%)

### Progress
- Completed: 250 (5.5%)
- In Progress: 113 (2.5%)
- Not Started: 4,155 (91.8%)
- Graduated: 7 (0.2%)

## How to Import to Google Sheets

1. **Open Google Sheets**
   - Go to sheets.google.com
   - Create a new spreadsheet or open existing one

2. **Import the CSV**
   - Click `File` > `Import`
   - Choose `Upload` tab
   - Select the CSV file from this directory
   - Import settings:
     - Import location: Choose "Replace spreadsheet" or "Insert new sheet"
     - Separator type: Comma
     - Convert text: Yes (recommended)

3. **Post-Import Setup**
   - Format date column as Date (Format > Number > Date)
   - Apply filters (Data > Create a filter)
   - Create pivot tables for analysis (Insert > Pivot table)

## Data Processing Script
The CSV was generated using:
```bash
python3 scripts/batches_to_vertical_csv.py
```

This script:
- Reads all 18 batch JSON files from `data/raw/batches/`
- Parses the horizontal 338-column format
- Transforms to vertical format (one row per session)
- Normalizes attendance and progress values
- Extracts and cleans lesson titles
- Exports to CSV with proper escaping

## Benefits of Vertical Format
1. **Easier Filtering**: Filter by date, student, teacher, or status
2. **Better Analysis**: Create pivot tables and charts
3. **Scalable**: Add new sessions without adding columns
4. **Standard Format**: Works with any data analysis tool
5. **Google Sheets Compatible**: Direct import without transformation