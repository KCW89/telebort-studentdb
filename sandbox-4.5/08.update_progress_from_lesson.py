import pandas as pd
import re

def update_progress_from_lesson(file_path):
    """
    Scan Lesson column values for progress indicators and update Progress columns
    Also replace empty stars (☆☆☆☆☆) with dash (-)
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
    
    # Read data with pandas (this will add suffixes to duplicate columns)
    df = pd.read_csv(file_path)
    print(f"Total rows: {len(df)}")
    
    # Rename columns back to original names to remove the suffixes
    df.columns = raw_columns
    
    # Create a copy of the dataframe to modify
    df_modified = df.copy()
    
    # Track changes
    changes_made = 0
    changes_by_type = {'In Progress': 0, 'Completed': 0, 'Stars to Dash': 0}
    
    # Progress detection patterns
    progress_patterns = {
        'In Progress': [
            r'\bIN PROGRESS\b',
            r'\bIn Progress\b', 
            r'\bin progress\b',
            r'\bIN PROGRESSED\b',
            r'\bIn Progressed\b',
            r'\bin progressed\b',
            r'\bONGOING\b',
            r'\bOngoing\b',
            r'\bongoing\b',
            r'\bDOING\b',
            r'\bDoing\b',
            r'\bdoing\b',
            r'\bNOT STARTED\b',
            r'\bNot Started\b',
            r'\bnot started\b',
            r'\bINCOMPLETE\b',
            r'\bIncomplete\b',
            r'\bincomplete\b',
            r'\bNOT DONE\b',
            r'\bNot Done\b',
            r'\bnot done\b',
            r'\bPENDING\b',
            r'\bPending\b',
            r'\bpending\b'
        ],
        'Completed': [
            r'\bCOMPLETED\b',
            r'\bCompleted\b',
            r'\bcompleted\b',
            r'\bCOMPLETE\b',
            r'\bComplete\b',
            r'\bcomplete\b',
            r'\bDONE\b',
            r'\bDone\b',
            r'\bdone\b',
            r'\bFINISHED\b',
            r'\bFinished\b',
            r'\bfinished\b',
            r'\bACCOMPLISHED\b',
            r'\bAccomplished\b',
            r'\baccomplished\b'
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
    
    # Now process all Progress columns to replace empty stars with dash
    print(f"\n" + "=" * 70)
    print("REPLACING EMPTY STARS WITH DASH")
    print("=" * 70)
    
    star_changes = 0
    for row_idx in range(len(df_modified)):
        row = df_modified.iloc[row_idx]
        
        for col_idx, col_name in enumerate(df_modified.columns):
            if col_name == 'Progress':
                cell_value = row.iloc[col_idx]
                
                # Check if cell value exists and contains empty stars
                if pd.notna(cell_value) and str(cell_value).strip() not in ['', '-', 'nan']:
                    cell_str = str(cell_value).strip()
                    
                    # Check for empty stars pattern (☆☆☆☆☆)
                    if re.match(r'^☆+$', cell_str):
                        old_value = cell_str
                        new_value = '-'
                        
                        df_modified.iloc[row_idx, col_idx] = new_value
                        star_changes += 1
                        changes_by_type['Stars to Dash'] += 1
                        
                        # Show first few star changes for verification
                        if star_changes <= 10:
                            print(f"  Row {row_idx + 1}, Progress col {col_idx}: '{old_value}' → '{new_value}'")
    
    print(f"\n" + "=" * 70)
    print("CHANGE SUMMARY")
    print("=" * 70)
    print(f"Total changes made: {changes_made + star_changes}")
    print(f"Changes by type:")
    for change_type, count in changes_by_type.items():
        print(f"  {change_type}: {count} changes")
    
    # Save the modified file
    output_file = 'sandbox-4.5/08.progress_updated.csv'
    df_modified.to_csv(output_file, index=False)
    print(f"\n✓ Modified file saved as: {output_file}")
    
    return {
        'total_changes': changes_made + star_changes,
        'changes_by_type': changes_by_type,
        'output_file': output_file
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/07.modified_attendance_values.csv"
    result = update_progress_from_lesson(csv_file)
    
    print("\n" + "=" * 70)
    print("PROGRESS UPDATE COMPLETE")
    print("=" * 70) 