import pandas as pd

def find_specific_values(file_path):
    """
    Find specific locations of 'Soumiya' in attendance columns and '6' in teacher columns
    """
    print("=" * 70)
    print("FINDING SPECIFIC VALUES IN COLUMNS")
    print("=" * 70)
    
    # Read raw CSV header to get actual column names
    with open(file_path, 'r') as f:
        header_line = f.readline().strip()
    
    raw_columns = header_line.split(',')
    
    # Find attendance and teacher column positions
    attendance_positions = [i for i, col in enumerate(raw_columns) if col == 'Attendance']
    teacher_positions = [i for i, col in enumerate(raw_columns) if col == 'Teacher']
    
    print(f"File: {file_path}")
    print(f"Total columns: {len(raw_columns)}")
    print(f"Attendance columns: {len(attendance_positions)}")
    print(f"Teacher columns: {len(teacher_positions)}")
    
    # Read data with pandas
    df = pd.read_csv(file_path)
    print(f"Total rows: {len(df)}")
    
    # Find 'Soumiya' in attendance columns
    print(f"\n" + "=" * 70)
    print("FINDING 'Soumiya' IN ATTENDANCE COLUMNS")
    print("=" * 70)
    
    soumiya_attendance_locations = []
    
    for row_idx in range(len(df)):
        row = df.iloc[row_idx]
        
        for col_idx, pos in enumerate(attendance_positions):
            if pos < len(row):
                value = row.iloc[pos]
                if pd.notna(value) and str(value).strip() == 'Soumiya':
                    session_num = col_idx + 1
                    soumiya_attendance_locations.append({
                        'row': row_idx + 1,
                        'session': session_num,
                        'column_position': pos,
                        'value': value
                    })
    
    print(f"Found 'Soumiya' in attendance columns: {len(soumiya_attendance_locations)} times")
    
    if soumiya_attendance_locations:
        print(f"\nLocations where 'Soumiya' appears in attendance columns:")
        for loc in soumiya_attendance_locations:
            print(f"  Row {loc['row']}, Session {loc['session']}, Column {loc['column_position']}: '{loc['value']}'")
    else:
        print("  No 'Soumiya' found in attendance columns")
    
    # Find '6' in teacher columns
    print(f"\n" + "=" * 70)
    print("FINDING '6' IN TEACHER COLUMNS")
    print("=" * 70)
    
    six_teacher_locations = []
    
    for row_idx in range(len(df)):
        row = df.iloc[row_idx]
        
        for col_idx, pos in enumerate(teacher_positions):
            if pos < len(row):
                value = row.iloc[pos]
                if pd.notna(value) and str(value).strip() == '6':
                    session_num = col_idx + 1
                    six_teacher_locations.append({
                        'row': row_idx + 1,
                        'session': session_num,
                        'column_position': pos,
                        'value': value
                    })
    
    print(f"Found '6' in teacher columns: {len(six_teacher_locations)} times")
    
    if six_teacher_locations:
        print(f"\nLocations where '6' appears in teacher columns:")
        for loc in six_teacher_locations:
            print(f"  Row {loc['row']}, Session {loc['session']}, Column {loc['column_position']}: '{loc['value']}'")
    else:
        print("  No '6' found in teacher columns")
    
    # Summary
    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"• 'Soumiya' in attendance columns: {len(soumiya_attendance_locations)} occurrences")
    print(f"• '6' in teacher columns: {len(six_teacher_locations)} occurrences")
    
    if soumiya_attendance_locations:
        print(f"• 'Soumiya' appears in rows: {list(set([loc['row'] for loc in soumiya_attendance_locations]))}")
    if six_teacher_locations:
        print(f"• '6' appears in rows: {list(set([loc['row'] for loc in six_teacher_locations]))}")
    
    return {
        'soumiya_attendance_locations': soumiya_attendance_locations,
        'six_teacher_locations': six_teacher_locations
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/04.all-extractions.csv"
    result = find_specific_values(csv_file)
    
    print("\n" + "=" * 70)
    print("SEARCH COMPLETE")
    print("=" * 70) 