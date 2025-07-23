import pandas as pd
import re

def compare_lesson_progress(file_path):
    """
    Compare lesson columns to determine progress status:
    - For each progress column, compare lesson column 2 positions to the left with lesson column 3 positions to the right
    - If they're the same → 'In Progress'
    - If they're different → 'Completed'
    """
    print("=" * 70)
    print("COMPARING LESSON COLUMNS FOR PROGRESS DETERMINATION")
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
    changes_by_type = {'In Progress': 0, 'Completed': 0}
    
    print(f"\n" + "=" * 70)
    print("PROCESSING LESSON COMPARISONS")
    print("=" * 70)
    
    # Process each row
    for row_idx in range(len(df)):
        row = df.iloc[row_idx]
        
        # Process each progress column
        for col_idx, progress_pos in enumerate(progress_positions):
            # Find the lesson column 2 positions to the left of this progress column
            current_lesson_pos = progress_pos - 2
            
            # Find the lesson column 3 positions to the right of this progress column (next week)
            next_lesson_pos = progress_pos + 3
            
            # Check if both lesson positions exist and are within bounds
            if (current_lesson_pos >= 0 and current_lesson_pos < len(row) and 
                next_lesson_pos < len(row) and next_lesson_pos < len(df_modified.columns)):
                
                current_lesson_value = row.iloc[current_lesson_pos]
                next_lesson_value = row.iloc[next_lesson_pos]
                current_progress_value = row.iloc[progress_pos]
                
                # Check if current lesson value exists and is not empty
                if pd.notna(current_lesson_value) and str(current_lesson_value).strip() not in ['', '-', 'nan']:
                    current_lesson_str = str(current_lesson_value).strip()
                    
                    # Check if current progress value contains stars (indicating it needs to be updated)
                    if pd.notna(current_progress_value) and str(current_progress_value).strip() not in ['', '-', 'nan']:
                        current_progress_str = str(current_progress_value).strip()
                        
                        # Check for star patterns (★ or ☆)
                        if re.search(r'[★☆]', current_progress_str):
                            # Check if next lesson exists and is not empty
                            if pd.notna(next_lesson_value) and str(next_lesson_value).strip() not in ['', '-', 'nan']:
                                next_lesson_str = str(next_lesson_value).strip()
                                
                                # Compare lesson values
                                if current_lesson_str == next_lesson_str:
                                    new_progress = 'In Progress'
                                    changes_by_type['In Progress'] += 1
                                else:
                                    new_progress = 'Completed'
                                    changes_by_type['Completed'] += 1
                                
                                # Show first few changes for verification
                                if changes_made <= 10:
                                    print(f"  Row {row_idx + 1}, Session {col_idx + 1}:")
                                    print(f"    Current Lesson: '{current_lesson_str[:50]}...'")
                                    print(f"    Next Lesson: '{next_lesson_str[:50]}...'")
                                    print(f"    Progress: '{current_progress_str}' → '{new_progress}'")
                                    print(f"    Same lesson? {'Yes' if current_lesson_str == next_lesson_str else 'No'}")
                                    print()
                            else:
                                # Next lesson is missing - mark as "In Progress"
                                new_progress = 'In Progress'
                                changes_by_type['In Progress'] += 1
                                
                                # Show first few changes for verification
                                if changes_made <= 10:
                                    print(f"  Row {row_idx + 1}, Session {col_idx + 1}:")
                                    print(f"    Current Lesson: '{current_lesson_str[:50]}...'")
                                    print(f"    Next Lesson: 'MISSING'")
                                    print(f"    Progress: '{current_progress_str}' → '{new_progress}' (no next lesson)")
                                    print()
                            
                            # Update the progress value
                            df_modified.iloc[row_idx, progress_pos] = new_progress
                            changes_made += 1
    
    # Second pass: Convert any remaining stars to dashes
    print(f"\n" + "=" * 70)
    print("CONVERTING REMAINING STARS TO DASHES")
    print("=" * 70)
    
    remaining_stars_changed = 0
    for row_idx in range(len(df_modified)):
        row = df_modified.iloc[row_idx]
        
        for col_idx, col_name in enumerate(df_modified.columns):
            if col_name == 'Progress':
                cell_value = row.iloc[col_idx]
                
                # Check if cell value contains stars
                if pd.notna(cell_value) and str(cell_value).strip() not in ['', '-', 'nan']:
                    cell_str = str(cell_value).strip()
                    
                    # Check for star patterns (★ or ☆)
                    if re.search(r'[★☆]', cell_str):
                        old_value = cell_str
                        new_value = '-'
                        
                        df_modified.iloc[row_idx, col_idx] = new_value
                        remaining_stars_changed += 1
                        
                        # Show first few remaining star changes for verification
                        if remaining_stars_changed <= 10:
                            print(f"  Row {row_idx + 1}, Progress col {col_idx}: '{old_value}' → '{new_value}'")
    
    print(f"\n" + "=" * 70)
    print("CHANGE SUMMARY")
    print("=" * 70)
    print(f"Lesson comparison changes: {changes_made}")
    print(f"Remaining stars converted to dash: {remaining_stars_changed}")
    print(f"Total changes made: {changes_made + remaining_stars_changed}")
    print(f"Changes by type:")
    for change_type, count in changes_by_type.items():
        print(f"  {change_type}: {count} changes")
    print(f"  Stars to Dash: {remaining_stars_changed} changes")
    
    # Save the modified file
    output_file = 'sandbox-4.5/10.lesson_comparison_progress.csv'
    df_modified.to_csv(output_file, index=False)
    print(f"\n✓ Modified file saved as: {output_file}")
    
    return {
        'total_changes': changes_made,
        'changes_by_type': changes_by_type,
        'output_file': output_file
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/09.teacher_columns_dropped.csv"
    result = compare_lesson_progress(csv_file)
    
    print("\n" + "=" * 70)
    print("LESSON COMPARISON PROGRESS COMPLETE")
    print("=" * 70) 