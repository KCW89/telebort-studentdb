import pandas as pd
import re

def diagnose_unchanged_stars(file_path):
    """
    Diagnose why certain star cells weren't changed by the lesson comparison logic
    """
    print("=" * 70)
    print("DIAGNOSING UNCHANGED STAR CELLS")
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
    df.columns = raw_columns
    
    # Track reasons for unchanged stars
    reasons = {
        'missing_current_lesson': 0,
        'missing_next_lesson': 0,
        'boundary_progress': 0,
        'no_stars_in_progress': 0,
        'successfully_changed': 0
    }
    
    unchanged_stars = []
    
    print(f"\n" + "=" * 70)
    print("ANALYZING EACH PROGRESS COLUMN")
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
            
            current_progress_value = row.iloc[progress_pos]
            
            # Check if progress value contains stars
            if pd.notna(current_progress_value) and str(current_progress_value).strip() not in ['', '-', 'nan']:
                current_progress_str = str(current_progress_value).strip()
                
                if re.search(r'[★☆]', current_progress_str):
                    # This is a star cell - let's analyze why it wasn't changed
                    
                    # Check if current lesson position is valid
                    if current_lesson_pos < 0 or current_lesson_pos >= len(row):
                        reasons['boundary_progress'] += 1
                        unchanged_stars.append({
                            'row': row_idx + 1,
                            'progress_col': progress_pos,
                            'session': col_idx + 1,
                            'reason': 'boundary_progress',
                            'progress_value': current_progress_str
                        })
                        continue
                    
                    # Check if next lesson position is valid
                    if next_lesson_pos >= len(row) or next_lesson_pos >= len(df.columns):
                        reasons['boundary_progress'] += 1
                        unchanged_stars.append({
                            'row': row_idx + 1,
                            'progress_col': progress_pos,
                            'session': col_idx + 1,
                            'reason': 'boundary_progress',
                            'progress_value': current_progress_str
                        })
                        continue
                    
                    current_lesson_value = row.iloc[current_lesson_pos]
                    next_lesson_value = row.iloc[next_lesson_pos]
                    
                    # Check if current lesson is missing/empty
                    if pd.isna(current_lesson_value) or str(current_lesson_value).strip() in ['', '-', 'nan']:
                        reasons['missing_current_lesson'] += 1
                        unchanged_stars.append({
                            'row': row_idx + 1,
                            'progress_col': progress_pos,
                            'session': col_idx + 1,
                            'reason': 'missing_current_lesson',
                            'progress_value': current_progress_str,
                            'current_lesson': str(current_lesson_value) if pd.notna(current_lesson_value) else 'MISSING'
                        })
                        continue
                    
                    # Check if next lesson is missing/empty
                    if pd.isna(next_lesson_value) or str(next_lesson_value).strip() in ['', '-', 'nan']:
                        reasons['missing_next_lesson'] += 1
                        unchanged_stars.append({
                            'row': row_idx + 1,
                            'progress_col': progress_pos,
                            'session': col_idx + 1,
                            'reason': 'missing_next_lesson',
                            'progress_value': current_progress_str,
                            'current_lesson': str(current_lesson_value).strip(),
                            'next_lesson': str(next_lesson_value) if pd.notna(next_lesson_value) else 'MISSING'
                        })
                        continue
                    
                    # If we get here, both lessons exist but the cell still has stars
                    # This means the comparison logic didn't work as expected
                    unchanged_stars.append({
                        'row': row_idx + 1,
                        'progress_col': progress_pos,
                        'session': col_idx + 1,
                        'reason': 'logic_error',
                        'progress_value': current_progress_str,
                        'current_lesson': str(current_lesson_value).strip(),
                        'next_lesson': str(next_lesson_value).strip()
                    })
    
    print(f"\n" + "=" * 70)
    print("DIAGNOSIS RESULTS")
    print("=" * 70)
    
    total_unchanged = len(unchanged_stars)
    print(f"Total unchanged star cells: {total_unchanged}")
    
    # Group by reason
    reasons_count = {}
    for star in unchanged_stars:
        reason = star['reason']
        if reason not in reasons_count:
            reasons_count[reason] = 0
        reasons_count[reason] += 1
    
    print(f"\nReasons for unchanged stars:")
    for reason, count in reasons_count.items():
        print(f"  {reason}: {count} cells")
    
    print(f"\n" + "=" * 70)
    print("DETAILED EXAMPLES (First 20)")
    print("=" * 70)
    
    for i, star in enumerate(unchanged_stars[:20]):
        print(f"{i+1:2d}. Row {star['row']:3d}, Session {star['session']:2d}: '{star['progress_value']}'")
        print(f"     Reason: {star['reason']}")
        if 'current_lesson' in star:
            print(f"     Current Lesson: '{star['current_lesson'][:50]}...'")
        if 'next_lesson' in star:
            print(f"     Next Lesson: '{star['next_lesson'][:50]}...'")
        print()
    
    if len(unchanged_stars) > 20:
        print(f"... and {len(unchanged_stars) - 20} more")
    
    return {
        'total_unchanged': total_unchanged,
        'reasons_count': reasons_count,
        'unchanged_stars': unchanged_stars
    }

if __name__ == "__main__":
    csv_file = "sandbox-4.5/10.lesson_comparison_progress.csv"
    result = diagnose_unchanged_stars(csv_file)
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70) 