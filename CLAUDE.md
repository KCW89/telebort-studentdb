# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Telebort studentdb is an educational data management system for Telebort Academy, tracking student progress, attendance, and academic performance across programming courses (AI/ML, Web Development, Python).

## Core Architecture

### Data Organization
```
/Teacher [Name]/
  └── s[StudentID].md     # Individual student reports (anonymized)

/sandbox-4.5/
  ├── *.py               # Data processing scripts
  ├── *.csv              # Student data files
  └── *.ipynb            # Jupyter notebooks
```

### Data Processing Pipeline
1. **Raw Data**: `sandbox.csv` (111 students, 480 columns - 8 columns per time period)
2. **Column Extraction**: Scripts extract 6 key columns (Date, Session, Lesson, Attendance, Teacher, Progress)
3. **Data Transformation**: Wide format conversion for analysis
4. **Report Generation**: Markdown files with student performance metrics

## Common Commands

### Data Analysis Scripts
```bash
# Basic CSV analysis
python sandbox-4.5/01.analysis_script.py

# Extract all student data
python sandbox-4.5/04.all-extractions.py

# Analyze teacher attendance
python sandbox-4.5/05.analyze_attendance_teacher.py

# Graduation processing
python sandbox-4.5/11.graduate_session_1.py

# Jupyter analysis
jupyter notebook sandbox-4.5/checking-csv-file.ipynb
```

## Data Schema

### CSV Structure (Repeating 8-column pattern)
- Column 0: Date (DD/MM/YYYY)
- Column 1: Attendance (Attended/Absent/No Class/Public Holiday)
- Column 2: Teacher name
- Column 3: Session number
- Column 4: Submission Link/Score
- Column 5: Lesson title and status
- Column 6: Exit ticket scores
- Column 7: Progress (1-5 stars: ★★★★★)

### Student Report Format
```markdown
# Student Attendance & Progress Report - [Teacher Name]
**Student:** [Teacher Name]
**Course:** [Program Name]
**Total Sessions:** X
**Date Range:** [Start] - [End]

## Summary Statistics
- Classes Attended: X/Y (%)
- Average Rating: X/5 stars

## Detailed Session Log
| Session | Date | Student | Attendance | Lesson/Topic |
```

## Key Files

### Data Files
- `sandbox-4.5/sandbox.csv` - Current semester data
- `sandbox-4.5/oldsandbox.csv` - Historical data
- `sandbox-4.5/CurrentSandbox.csv` - Active semester

### Processing Scripts
- `01.analysis_script.py` - Basic CSV structure analysis
- `04.all-extractions.py` - Extract 6 key columns from all students
- `07.modify_attendance_values.py` - Normalize attendance values
- `08.update_progress_from_lesson.py` - Update progress ratings

## Data Processing Patterns

### Reading Student Data
```python
import pandas as pd
df = pd.read_csv("sandbox-4.5/sandbox.csv")
# Process every 8 columns as one time period
for week_num in range(0, len(row), 8):
    date = row.iloc[week_num]
    attendance = row.iloc[week_num + 1]
    teacher = row.iloc[week_num + 2]
    session = row.iloc[week_num + 3]
    lesson = row.iloc[week_num + 5]
    progress = row.iloc[week_num + 7]
```

### Attendance Values
- "Attended" - Student present
- "Absent" - Student absent
- "No Class" - Scheduled holiday
- "Public Holiday" - National holiday

### Progress Ratings
- ★★★★★ (5 stars) - Excellent
- ★★★★☆ (4 stars) - Good
- ★★★☆☆ (3 stars) - Satisfactory
- ★★☆☆☆ (2 stars) - Needs improvement
- ★☆☆☆☆ (1 star) - Struggling

## Programs Tracked

### AI & Machine Learning (Program AI-2)
- L1: Introduction to AI
- L2: Supervised & Unsupervised Learning
- L3: Data Preparation
- L4: Regression
- L5: Project 1 - Instagram Reach Analysis
- L6: Classification
- L7: Clustering
- L8: Project 3 - Mall Customer Segmentation
- L9: NLP Concepts

### Web Development (Programs C/D)
- HTML/CSS Basics
- Bootstrap Framework
- JavaScript Fundamentals
- React.js Introduction

### Python Programming
- Functions and Loops
- Data Structures
- File Handling
- Final Projects

## Privacy and Security

- Student IDs are anonymized (s10XXX format)
- No personal information in reports
- Access via secure WhatsApp links only
- Teacher-based data segregation

## Development Guidelines

- Always preserve the 8-column structure when processing CSV files
- Maintain consistent date formats (DD/MM/YYYY)
- Use pandas for all data manipulation
- Generate reports in markdown format
- Follow the established file naming convention: s[StudentID].md