import pandas as pd

def analyze_all_extractions(file_path):
    """
    Analyze the all-extractions CSV file to locate attendance and teacher columns
    and analyze unique values across all rows
    """
    print("=" * 60)
    print("ANALYZING ALL EXTRACTIONS CSV")
    print("=" * 60)
    
    # Read raw CSV header to get actual column names
    with open(file_path, 'r') as f:
        header_line = f.readline().strip()
    
    raw_columns = header_line.split(',')
    
    print(f"File: {file_path}")
    print(f"Total columns: {len(raw_columns)}")
    
    # Find attendance and teacher column positions
    attendance_positions = [i for i, col in enumerate(raw_columns) if col == 'Attendance']
    teacher_positions = [i for i, col in enumerate(raw_columns) if col == 'Teacher']
    
    print(f"\nATTENDANCE COLUMNS:")
    print(f"Found {len(attendance_positions)} 'Attendance' columns")
    print(f"Positions: {attendance_positions}")
    
    print(f"\nTEACHER COLUMNS:")
    print(f"Found {len(teacher_positions)} 'Teacher' columns")
    print(f"Positions: {teacher_positions}")
    
    # Pattern analysis
    pattern_length = 6  # Date, Session, Lesson, Attendance, Teacher, Progress
    complete_sessions = len(raw_columns) // pattern_length
    
    print(f"\nPATTERN ANALYSIS:")
    print(f"Pattern: Date, Session, Lesson, Attendance, Teacher, Progress")
    print(f"Pattern length: {pattern_length}")
    print(f"Complete sessions: {complete_sessions}")
    
    # Read data with pandas
    df = pd.read_csv(file_path)
    print(f"\nDATA SHAPE:")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    
    # Analyze unique values across all rows
    print(f"\n" + "=" * 60)
    print("UNIQUE VALUES ANALYSIS (ALL ROWS)")
    print("=" * 60)
    
    # Collect all attendance values from all rows
    all_attendance_values = []
    all_teacher_values = []
    
    for row_idx in range(len(df)):
        row = df.iloc[row_idx]
        
        # Collect attendance values for this row
        for pos in attendance_positions:
            if pos < len(row):
                value = row.iloc[pos]
                if pd.notna(value) and value != '':
                    all_attendance_values.append(str(value).strip())
        
        # Collect teacher values for this row
        for pos in teacher_positions:
            if pos < len(row):
                value = row.iloc[pos]
                if pd.notna(value) and value != '':
                    all_teacher_values.append(str(value).strip())
    
    # Analyze unique attendance values
    unique_attendance = list(set(all_attendance_values))
    attendance_counts = {}
    for value in all_attendance_values:
        attendance_counts[value] = attendance_counts.get(value, 0) + 1
    
    print(f"\nATTENDANCE UNIQUE VALUES (ALL ROWS):")
    print(f"Total attendance records: {len(all_attendance_values)}")
    print(f"Unique values: {unique_attendance}")
    print(f"Value counts:")
    for value, count in sorted(attendance_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  '{value}': {count} times")
    
    # Analyze unique teacher values
    unique_teachers = list(set(all_teacher_values))
    teacher_counts = {}
    for value in all_teacher_values:
        teacher_counts[value] = teacher_counts.get(value, 0) + 1
    
    print(f"\nTEACHER UNIQUE VALUES (ALL ROWS):")
    print(f"Total teacher records: {len(all_teacher_values)}")
    print(f"Unique values: {unique_teachers}")
    print(f"Value counts:")
    for value, count in sorted(teacher_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  '{value}': {count} times")
    
    return {
        'total_columns': len(raw_columns),
        'total_rows': len(df),
        'attendance_positions': attendance_positions,
        'teacher_positions': teacher_positions,
        'pattern_length': pattern_length,
        'complete_sessions': complete_sessions,
        'unique_attendance': unique_attendance,
        'unique_teachers': unique_teachers,
        'attendance_counts': attendance_counts,
        'teacher_counts': teacher_counts
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/04.all-extractions.csv"
    result = analyze_all_extractions(csv_file)
