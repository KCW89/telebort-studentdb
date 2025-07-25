import pandas as pd
import re

def graduate_session_1(file_path):
    """
    Change Progress column values to "Graduated" if Session column (8 columns to the left) has value 1
    """
    print("=" * 70)
    print("GRADUATING STUDENTS WITH SESSION 1")
    print("=" * 70)
    
    # Read raw CSV header to get actual column names
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        header_line = f.readline().strip()
    
    raw_columns = header_line.split(',')
    
    print(f"File: {file_path}")
    print(f"Total columns: {len(raw_columns)}")
    
    # Find session and progress column positions
    session_positions = [i for i, col in enumerate(raw_columns) if col == 'Session']
    progress_positions = [i for i, col in enumerate(raw_columns) if col == 'Progress']
    
    print(f"Session columns: {len(session_positions)}")
    print(f"Progress columns: {len(progress_positions)}")
    
    # Read data with pandas
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    print(f"Total rows: {len(df)}")
    
    # Rename columns back to original names to remove the suffixes
    df.columns = raw_columns
    
    # Create a copy of the dataframe to modify
    df_modified = df.copy()
    
    # Track changes
    changes_made = 0
    
    print(f"\n" + "=" * 70)
    print("PROCESSING SESSION 1 GRADUATIONS")
    print("=" * 70)
    
    # Process each row
    for row_idx in range(len(df)):
        row = df.iloc[row_idx]
        
        # Process each progress column
        for col_idx, progress_pos in enumerate(progress_positions):
            # Find the session column 8 positions to the left of this progress column
            session_pos = progress_pos - 8
            
            # Check if session position exists and is within bounds
            if session_pos >= 0 and session_pos < len(row):
                session_value = row.iloc[session_pos]
                progress_value = row.iloc[progress_pos]
                
                # Check if session value is 1
                if pd.notna(session_value) and str(session_value).strip() == '1':
                    # Check if progress value exists and is not already "Graduated"
                    if pd.notna(progress_value) and str(progress_value).strip() not in ['', '-', 'nan', 'Graduated']:
                        old_progress = str(progress_value).strip()
                        new_progress = 'Graduated'
                        
                        # Update the progress value
                        df_modified.iloc[row_idx, progress_pos] = new_progress
                        changes_made += 1
                        
                        # Show first few changes for verification
                        if changes_made <= 10:
                            print(f"  Row {row_idx + 1}, Session {col_idx + 1}:")
                            print(f"    Session value: '{session_value}'")
                            print(f"    Progress: '{old_progress}' → '{new_progress}'")
                            print()
    
    print(f"\n" + "=" * 70)
    print("CHANGE SUMMARY")
    print("=" * 70)
    print(f"Total graduations made: {changes_made}")
    
    # Save the modified file with proper encoding
    output_file = 'sandbox-4.5/11.graduated_session_1.csv'
    df_modified.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Modified file saved as: {output_file}")
    
    return {
        'total_graduations': changes_made,
        'output_file': output_file
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/10.lesson_comparison_progress.csv"
    result = graduate_session_1(csv_file)
    
    print("\n" + "=" * 70)
    print("SESSION 1 GRADUATION COMPLETE")
    print("=" * 70) 