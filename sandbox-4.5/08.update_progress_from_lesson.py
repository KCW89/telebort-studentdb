import pandas as pd
import re

def update_progress_from_lesson(file_path):
    """
    Scan Lesson column values for progress indicators and update Progress columns
    """
    print("=" * 70)
    print("UPDATING PROGRESS FROM LESSON COLUMNS")
    print("=" * 70)
    
    # Read raw CSV header to get actual column names
    with open(file_path, 'r') as f:
        header_line = f.readline().strip()
    
    raw_columns = header_line.split(',')
    
    print(f"File: {file_path}")
    print(f"Total columns: {len(raw_columns)}")
    
    # Find lesson and progress column positions
    lesson_positions = [i for i, col in enumerate(raw_columns) if col == 'Lesson']
    progress_positions = [i for i, col in enumerate(raw_columns) if col == 'Progress']
    
    print(f"Lesson columns: {len(lesson_positions)}")
    print(f"Progress columns: {len(progress_positions)}")
    
    # Read data with pandas
    df = pd.read_csv(file_path)
    print(f"Total rows: {len(df)}")
    
    # Create a copy of the dataframe to modify
    df_modified = df.copy()
    
    # Track changes
    changes_made = 0
    changes_by_type = {'In Progress': 0, 'Completed': 0}
    
    # Progress detection patterns
    progress_patterns = {
        'In Progress': [
            r'\bIN PROGRESS\b',
            r'\bIn Progress\b', 
            r'\bin progress\b',
            r'\bDOING\b',
            r'\bDoing\b',
            r'\bdoing\b',
            r'\bNOT STARTED\b',
            r'\bNot Started\b',
            r'\bnot started\b',
            r'\bIN PROGRESS\b',
            r'\bIN PROGRESS\b'
        ],
        'Completed': [
            r'\bCOMPLETED\b',
            r'\bCompleted\b',
            r'\bcompleted\b',
            r'\bDONE\b',
            r'\bDone\b',
            r'\bdone\b',
            r'\bFINISHED\b',
            r'\bFinished\b',
            r'\bfinished\b'
        ]
    }
    
    print(f"\n" + "=" * 70)
    print("PROCESSING CHANGES")
    print("=" * 70)
    
    # Process each row
    for row_idx in range(len(df)):
        row = df.iloc[row_idx]
        
        # Process each lesson column
        for col_idx, lesson_pos in enumerate(lesson_positions):
            # Find the corresponding progress position (3 columns to the right)
            progress_pos = lesson_pos + 3
            
            # Check if progress position exists and is within bounds
            if progress_pos < len(row) and progress_pos < len(df_modified.columns):
                lesson_value = row.iloc[lesson_pos]
                current_progress_value = row.iloc[progress_pos]
                
                # Check if lesson value exists and is not empty
                if pd.notna(lesson_value) and str(lesson_value).strip() not in ['', '-', 'nan']:
                    lesson_str = str(lesson_value).strip()
                    
                    # Check for progress indicators
                    detected_progress = None
                    
                    # Check for "In Progress" patterns
                    for pattern in progress_patterns['In Progress']:
                        if re.search(pattern, lesson_str, re.IGNORECASE):
                            detected_progress = 'In Progress'
                            break
                    
                    # Check for "Completed" patterns (only if not already detected as In Progress)
                    if not detected_progress:
                        for pattern in progress_patterns['Completed']:
                            if re.search(pattern, lesson_str, re.IGNORECASE):
                                detected_progress = 'Completed'
                                break
                    
                    # Update progress if detected
                    if detected_progress:
                        old_value = str(current_progress_value).strip() if pd.notna(current_progress_value) else ''
                        new_value = detected_progress
                        
                        df_modified.iloc[row_idx, progress_pos] = new_value
                        changes_made += 1
                        changes_by_type[detected_progress] += 1
                        
                        # Show first few changes for verification
                        if changes_made <= 10:
                            print(f"  Row {row_idx + 1}, Session {col_idx + 1}:")
                            print(f"    Lesson: '{lesson_str[:50]}...'")
                            print(f"    Progress: '{old_value}' → '{new_value}'")
                            print()
    
    print(f"\n" + "=" * 70)
    print("CHANGE SUMMARY")
    print("=" * 70)
    print(f"Total changes made: {changes_made}")
    print(f"Changes by type:")
    for change_type, count in changes_by_type.items():
        print(f"  {change_type}: {count} changes")
    
    # Save the modified file
    output_file = 'sandbox-4.5/08.progress_updated.csv'
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
        
        for col_idx, lesson_pos in enumerate(lesson_positions):
            if sample_count >= 10:
                break
                
            progress_pos = lesson_pos + 3
            
            if progress_pos < len(row_original):
                original_progress = row_original.iloc[progress_pos]
                modified_progress = row_modified.iloc[progress_pos]
                lesson_value = row_original.iloc[lesson_pos]
                
                if pd.notna(original_progress) and pd.notna(modified_progress):
                    original_str = str(original_progress).strip()
                    modified_str = str(modified_progress).strip()
                    lesson_str = str(lesson_value).strip() if pd.notna(lesson_value) else ''
                    
                    if original_str != modified_str:
                        print(f"  Row {row_idx + 1}, Session {col_idx + 1}:")
                        print(f"    Lesson: '{lesson_str[:60]}...'")
                        print(f"    Progress: '{original_str}' → '{modified_str}'")
                        print()
                        sample_count += 1
    
    return {
        'total_changes': changes_made,
        'changes_by_type': changes_by_type,
        'output_file': output_file
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/07.modified_attendance_values.csv"
    result = update_progress_from_lesson(csv_file)
    
    print("\n" + "=" * 70)
    print("PROGRESS UPDATE COMPLETE")
    print("=" * 70) 