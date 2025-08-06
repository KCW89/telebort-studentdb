import pandas as pd

def drop_teacher_columns(file_path):
    """
    Drop all Teacher columns from the CSV file and show the difference in table shape
    """
    print("=" * 70)
    print("DROPPING TEACHER COLUMNS")
    print("=" * 70)
    
    # Read raw CSV header to get actual column names
    with open(file_path, 'r') as f:
        header_line = f.readline().strip()
    
    raw_columns = header_line.split(',')
    
    print(f"File: {file_path}")
    print(f"Total columns: {len(raw_columns)}")
    
    # Find teacher column positions
    teacher_positions = [i for i, col in enumerate(raw_columns) if col == 'Teacher']
    
    print(f"Teacher columns found: {len(teacher_positions)}")
    
    # Read data with pandas (this will add suffixes to duplicate columns)
    df = pd.read_csv(file_path)
    print(f"Total rows: {len(df)}")
    
    # Rename columns back to original names to remove the suffixes
    df.columns = raw_columns
    
    # Show original table shape
    print(f"\n" + "=" * 70)
    print("ORIGINAL TABLE SHAPE")
    print("=" * 70)
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"Total cells: {df.shape[0] * df.shape[1]}")
    
    # Show column distribution
    column_counts = {}
    for col in df.columns:
        if col in column_counts:
            column_counts[col] += 1
        else:
            column_counts[col] = 1
    
    print(f"\nColumn distribution:")
    for col, count in column_counts.items():
        print(f"  {col}: {count} columns")
    
    # Create a copy of the dataframe to modify
    df_modified = df.copy()
    
    # Drop teacher columns
    teacher_columns = [col for col in df_modified.columns if col == 'Teacher']
    df_modified = df_modified.drop(columns=teacher_columns)
    
    # Show modified table shape
    print(f"\n" + "=" * 70)
    print("MODIFIED TABLE SHAPE (AFTER DROPPING TEACHER COLUMNS)")
    print("=" * 70)
    print(f"Rows: {df_modified.shape[0]}")
    print(f"Columns: {df_modified.shape[1]}")
    print(f"Total cells: {df_modified.shape[0] * df_modified.shape[1]}")
    
    # Show new column distribution
    new_column_counts = {}
    for col in df_modified.columns:
        if col in new_column_counts:
            new_column_counts[col] += 1
        else:
            new_column_counts[col] = 1
    
    print(f"\nColumn distribution after dropping Teacher columns:")
    for col, count in new_column_counts.items():
        print(f"  {col}: {count} columns")
    
    # Calculate differences
    rows_diff = df_modified.shape[0] - df.shape[0]
    cols_diff = df_modified.shape[1] - df.shape[1]
    cells_diff = (df_modified.shape[0] * df_modified.shape[1]) - (df.shape[0] * df.shape[1])
    
    print(f"\n" + "=" * 70)
    print("DIFFERENCE SUMMARY")
    print("=" * 70)
    print(f"Rows difference: {rows_diff:+d}")
    print(f"Columns difference: {cols_diff:+d}")
    print(f"Total cells difference: {cells_diff:+d}")
    print(f"Teacher columns dropped: {len(teacher_columns)}")
    
    # Save the modified file
    output_file = 'sandbox-4.5/09.teacher_columns_dropped.csv'
    df_modified.to_csv(output_file, index=False)
    print(f"\n✓ Modified file saved as: {output_file}")
    
    # Show sample of the modified data
    print(f"\n" + "=" * 70)
    print("SAMPLE OF MODIFIED DATA (First 3 rows, first 30 columns)")
    print("=" * 70)
    
    # Get first 30 columns for display
    first_30_cols = df_modified.columns[:30].tolist()
    sample_data = df_modified[first_30_cols].head(3)
    
    # Display column names
    print("Column names:")
    print(", ".join(first_30_cols))
    print()
    
    return {
        'original_shape': df.shape,
        'modified_shape': df_modified.shape,
        'teacher_columns_dropped': len(teacher_columns),
        'output_file': output_file
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/08.progress_updated.csv"
    result = drop_teacher_columns(csv_file)
    
    print("\n" + "=" * 70)
    print("TEACHER COLUMNS DROP COMPLETE")
    print("=" * 70) 