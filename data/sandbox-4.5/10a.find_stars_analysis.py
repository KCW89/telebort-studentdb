import pandas as pd
import re

def find_stars_analysis(file_path):
    """
    Analyze the CSV file to find any remaining star symbols and their locations
    """
    print("=" * 70)
    print("FINDING STAR SYMBOLS ANALYSIS")
    print("=" * 70)
    
    # Read raw CSV header to get actual column names
    with open(file_path, 'r') as f:
        header_line = f.readline().strip()
    
    raw_columns = header_line.split(',')
    
    print(f"File: {file_path}")
    print(f"Total columns: {len(raw_columns)}")
    
    # Read data with pandas (this will add suffixes to duplicate columns)
    df = pd.read_csv(file_path)
    print(f"Total rows: {len(df)}")
    
    # Rename columns back to original names to remove the suffixes
    df.columns = raw_columns
    
    # Star patterns to look for
    star_patterns = [
        r'★+☆*',  # Full stars followed by empty stars
        r'☆+',     # Empty stars only
        r'★+',     # Full stars only
        r'[★☆]+'   # Any combination of stars
    ]
    
    # Track findings
    star_findings = []
    total_star_cells = 0
    
    print(f"\n" + "=" * 70)
    print("SCANNING FOR STAR SYMBOLS")
    print("=" * 70)
    
    # Scan each cell in the dataframe
    for row_idx in range(len(df)):
        row = df.iloc[row_idx]
        
        for col_idx, col_name in enumerate(df.columns):
            cell_value = row.iloc[col_idx]
            
            # Check if cell value exists and is not empty
            if pd.notna(cell_value) and str(cell_value).strip() not in ['', '-', 'nan']:
                cell_str = str(cell_value).strip()
                
                # Check for star patterns
                for pattern in star_patterns:
                    if re.search(pattern, cell_str):
                        star_findings.append({
                            'row': row_idx + 1,  # 1-indexed for user
                            'column_index': col_idx,
                            'column_name': col_name,
                            'value': cell_str,
                            'pattern_matched': pattern
                        })
                        total_star_cells += 1
                        break  # Only count once per cell
    
    # Group findings by column type
    findings_by_column = {}
    for finding in star_findings:
        col_name = finding['column_name']
        if col_name not in findings_by_column:
            findings_by_column[col_name] = []
        findings_by_column[col_name].append(finding)
    
    # Display results
    print(f"Total cells with star symbols found: {total_star_cells}")
    
    if total_star_cells == 0:
        print("\n✅ No star symbols found in the dataset!")
        return {
            'total_star_cells': 0,
            'findings_by_column': {},
            'summary': 'No stars found'
        }
    
    print(f"\n" + "=" * 70)
    print("STAR SYMBOLS FOUND BY COLUMN TYPE")
    print("=" * 70)
    
    for col_name, findings in findings_by_column.items():
        print(f"\n{col_name} columns: {len(findings)} cells with stars")
        
        # Show first 10 examples for each column type
        for i, finding in enumerate(findings[:10]):
            print(f"  Row {finding['row']}, Col {finding['column_index']}: '{finding['value']}'")
        
        if len(findings) > 10:
            print(f"  ... and {len(findings) - 10} more")
    
    print(f"\n" + "=" * 70)
    print("DETAILED LOCATIONS (First 50 findings)")
    print("=" * 70)
    
    # Show detailed locations
    for i, finding in enumerate(star_findings[:50]):
        print(f"{i+1:2d}. Row {finding['row']:3d}, {finding['column_name']:12s} (col {finding['column_index']:3d}): '{finding['value']}'")
    
    if len(star_findings) > 50:
        print(f"\n... and {len(star_findings) - 50} more locations")
    
    # Summary statistics
    print(f"\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    
    unique_values = set(finding['value'] for finding in star_findings)
    print(f"Unique star patterns found: {len(unique_values)}")
    print("Star patterns:")
    for pattern in sorted(unique_values):
        count = sum(1 for finding in star_findings if finding['value'] == pattern)
        print(f"  '{pattern}': {count} occurrences")
    
    # Check which columns still have stars
    columns_with_stars = list(findings_by_column.keys())
    print(f"\nColumns that still contain star symbols:")
    for col in columns_with_stars:
        count = len(findings_by_column[col])
        print(f"  {col}: {count} cells")
    
    return {
        'total_star_cells': total_star_cells,
        'findings_by_column': findings_by_column,
        'unique_values': list(unique_values),
        'columns_with_stars': columns_with_stars,
        'summary': f'Found {total_star_cells} cells with star symbols across {len(columns_with_stars)} column types'
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/10.lesson_comparison_progress.csv"
    result = find_stars_analysis(csv_file)
    
    print("\n" + "=" * 70)
    print("STAR ANALYSIS COMPLETE")
    print("=" * 70) 