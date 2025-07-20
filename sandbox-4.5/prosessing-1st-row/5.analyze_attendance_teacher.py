import pandas as pd

def locate_columns(file_path):
    """
    Locate attendance and teacher column positions in the CSV file
    """
    print("=" * 50)
    print("LOCATING ATTENDANCE AND TEACHER COLUMNS")
    print("=" * 50)
    
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
    
    # Analyze unique values in attendance and teacher columns
    print(f"\n" + "=" * 50)
    print("UNIQUE VALUES ANALYSIS")
    print("=" * 50)
    
    # Read data with pandas
    df = pd.read_csv(file_path)
    
    if len(df) > 0:
        first_row = df.iloc[0]
        
        # Collect attendance values
        attendance_values = []
        for pos in attendance_positions:
            if pos < len(first_row):
                value = first_row.iloc[pos]
                attendance_values.append(value)
        
        # Collect teacher values
        teacher_values = []
        for pos in teacher_positions:
            if pos < len(first_row):
                value = first_row.iloc[pos]
                teacher_values.append(value)
        
        # Analyze unique attendance values
        unique_attendance = list(set(attendance_values))
        attendance_counts = {}
        for value in attendance_values:
            attendance_counts[value] = attendance_counts.get(value, 0) + 1
        
        print(f"\nATTENDANCE UNIQUE VALUES:")
        print(f"Unique values: {unique_attendance}")
        print(f"Value counts:")
        for value, count in attendance_counts.items():
            print(f"  '{value}': {count} times")
        
        # Analyze unique teacher values
        unique_teachers = list(set(teacher_values))
        teacher_counts = {}
        for value in teacher_values:
            teacher_counts[value] = teacher_counts.get(value, 0) + 1
        
        print(f"\nTEACHER UNIQUE VALUES:")
        print(f"Unique values: {unique_teachers}")
        print(f"Value counts:")
        for value, count in teacher_counts.items():
            print(f"  '{value}': {count} times")
    
    return {
        'total_columns': len(raw_columns),
        'attendance_positions': attendance_positions,
        'teacher_positions': teacher_positions,
        'pattern_length': pattern_length,
        'complete_sessions': complete_sessions
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/prosessing-1st-row/3.extracted-row1-6cols-wide.csv"
    result = locate_columns(csv_file)
    
    print("\n" + "=" * 50)
    print("LOCATION ANALYSIS COMPLETE")
    print("=" * 50) 