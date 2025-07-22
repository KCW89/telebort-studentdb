import pandas as pd
import numpy as np

def modify_attendance_values(file_path):
    """
    Modify "Attended", "New Program Attended", and "Late" values in attendance columns to match teacher values
    """
    print("=" * 70)
    print("MODIFYING ATTENDANCE VALUES")
    print("=" * 70)
    
    # Read raw CSV header to get actual column names
    with open(file_path, 'r') as f:
        header_line = f.readline().strip()
    
    raw_columns = header_line.split(',')
    
    print(f"File: {file_path}")
    print(f"Total columns: {len(raw_columns)}")
    
    # Find attendance and teacher column positions
    attendance_positions = [i for i, col in enumerate(raw_columns) if col == 'Attendance']
    teacher_positions = [i for i, col in enumerate(raw_columns) if col == 'Teacher']
    
    print(f"Attendance columns: {len(attendance_positions)}")
    print(f"Teacher columns: {len(teacher_positions)}")
    
    # Read data with pandas (this will add suffixes to duplicate columns)
    df = pd.read_csv(file_path)
    print(f"Total rows: {len(df)}")
    
    # Rename columns back to original names to remove the suffixes
    df.columns = raw_columns
    
    # Create a copy of the dataframe to modify
    df_modified = df.copy()
    
    # Track changes
    changes_made = 0
    changes_by_type = {'Attended': 0, 'New Program Attended': 0, 'Late': 0}
    
    print(f"\n" + "=" * 70)
    print("PROCESSING CHANGES")
    print("=" * 70)
    
    # Process each row
    for row_idx in range(len(df)):
        row = df.iloc[row_idx]
        
        # Process each attendance column
        for col_idx, attendance_pos in enumerate(attendance_positions):
            # Find the corresponding teacher position (next column to the right)
            teacher_pos = attendance_pos + 1
            
            # Check if teacher position exists and is within bounds
            if teacher_pos < len(row) and teacher_pos < len(df_modified.columns):
                attendance_value = row.iloc[attendance_pos]
                teacher_value = row.iloc[teacher_pos]
                
                # Check if attendance value is "Attended" or "Late" or "New Program Attended"
                if pd.notna(attendance_value) and str(attendance_value).strip() in ['Attended', 'Late', 'New Program Attended']:
                    # Check if teacher value exists and is not empty
                    if pd.notna(teacher_value) and str(teacher_value).strip() not in ['', '-', 'nan']:
                        # Make the change
                        old_value = str(attendance_value).strip()
                        new_value = str(teacher_value).strip()
                        
                        df_modified.iloc[row_idx, attendance_pos] = new_value
                        changes_made += 1
                        changes_by_type[old_value] += 1
                        
                        # Show first few changes for verification
                        if changes_made <= 10:
                            print(f"  Row {row_idx + 1}, Session {col_idx + 1}: '{old_value}' → '{new_value}'")
    
    print(f"\n" + "=" * 70)
    print("CHANGE SUMMARY")
    print("=" * 70)
    print(f"Total changes made: {changes_made}")
    print(f"Changes by type:")
    for change_type, count in changes_by_type.items():
        print(f"  {change_type}: {count} changes")
    
    # Save the modified file
    output_file = 'sandbox-4.5/07.modified_attendance_values.csv'
    df_modified.to_csv(output_file, index=False)
    print(f"\n✓ Modified file saved as: {output_file}")
    
    # Show sample of changes
    print(f"\n" + "=" * 70)
    print("SAMPLE OF CHANGES (First 10)")
    print("=" * 70)
    
    sample_count = 0
    for row_idx in range(len(df)):
        if sample_count >= 10:
            break
            
        row_original = df.iloc[row_idx]
        row_modified = df_modified.iloc[row_idx]
        
        for col_idx, attendance_pos in enumerate(attendance_positions):
            if sample_count >= 10:
                break
                
            original_value = row_original.iloc[attendance_pos]
            modified_value = row_modified.iloc[attendance_pos]
            
            if pd.notna(original_value) and pd.notna(modified_value):
                original_str = str(original_value).strip()
                modified_str = str(modified_value).strip()
                
                if original_str in ['Attended', 'Late', 'New Program Attended'] and original_str != modified_str:
                    print(f"  Row {row_idx + 1}, Session {col_idx + 1}: '{original_str}' → '{modified_str}'")
                    sample_count += 1
    
    return {
        'total_changes': changes_made,
        'changes_by_type': changes_by_type,
        'output_file': output_file
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/04.all-extractions.csv"
    result = modify_attendance_values(csv_file)
    
    print("\n" + "=" * 70)
    print("MODIFICATION COMPLETE")
    print("=" * 70) 