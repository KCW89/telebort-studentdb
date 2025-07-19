import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re

def analyze_sandbox_data():
    """
    Comprehensive analysis of the CurrentSandbox.csv file
    """
    print("=== TELEBORT STUDENT DATABASE ANALYSIS ===\n")
    
    # Read the CSV file
    try:
        df = pd.read_csv('sandbox-4.5/ CurrentSandbox.csv')
        print(f"✓ Successfully loaded CSV file")
        print(f"✓ File shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
    except Exception as e:
        print(f"✗ Error reading CSV file: {e}")
        return
    
    # Display basic information
    print("1. DATA STRUCTURE ANALYSIS")
    print("=" * 50)
    print(f"Columns in the dataset: {len(df.columns)}")
    print(f"First few column names: {list(df.columns[:10])}")
    print(f"Data types: {df.dtypes.value_counts()}\n")
    
    # Check for missing values
    print("2. MISSING VALUES ANALYSIS")
    print("=" * 50)
    missing_values = df.isnull().sum()
    missing_percentage = (missing_values / len(df)) * 100
    missing_df = pd.DataFrame({
        'Column': missing_values.index,
        'Missing_Count': missing_values.values,
        'Missing_Percentage': missing_percentage.values
    })
    missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
    
    if len(missing_df) > 0:
        print("Columns with missing values:")
        print(missing_df.head(10))
    else:
        print("✓ No missing values found in the dataset")
    print()
    
    # Analyze the first row to understand the structure
    print("3. DATA CONTENT ANALYSIS")
    print("=" * 50)
    
    # Look for actual data rows (skip header rows)
    data_rows = []
    for idx, row in df.iterrows():
        # Check if this row contains actual data (not just headers)
        if any(pd.notna(cell) and str(cell).strip() != '' for cell in row):
            data_rows.append(row)
    
    if data_rows:
        actual_data = pd.DataFrame(data_rows)
        print(f"✓ Found {len(actual_data)} rows with actual data")
        
        # Analyze attendance patterns
        print("\n4. ATTENDANCE ANALYSIS")
        print("=" * 50)
        
        # Find attendance columns
        attendance_cols = [col for col in actual_data.columns if 'Attendance' in str(col)]
        if attendance_cols:
            print(f"Found {len(attendance_cols)} attendance columns")
            
            # Get unique attendance values
            all_attendance = []
            for col in attendance_cols:
                values = actual_data[col].dropna()
                all_attendance.extend(values)
            
            attendance_counts = pd.Series(all_attendance).value_counts()
            print("Attendance distribution:")
            for status, count in attendance_counts.items():
                print(f"  {status}: {count}")
        
        # Analyze progress ratings
        print("\n5. PROGRESS RATING ANALYSIS")
        print("=" * 50)
        
        progress_cols = [col for col in actual_data.columns if 'Progress' in str(col)]
        if progress_cols:
            print(f"Found {len(progress_cols)} progress columns")
            
            # Get unique progress values
            all_progress = []
            for col in progress_cols:
                values = actual_data[col].dropna()
                all_progress.extend(values)
            
            progress_counts = pd.Series(all_progress).value_counts()
            print("Progress rating distribution:")
            for rating, count in progress_counts.items():
                print(f"  {rating}: {count}")
        
        # Analyze teachers/instructors
        print("\n6. TEACHER/INSTRUCTOR ANALYSIS")
        print("=" * 50)
        
        teacher_cols = [col for col in actual_data.columns if 'CSguru' in str(col) or 'Interns' in str(col)]
        if teacher_cols:
            print(f"Found {len(teacher_cols)} teacher columns")
            
            # Get unique teacher values
            all_teachers = []
            for col in teacher_cols:
                values = actual_data[col].dropna()
                all_teachers.extend(values)
            
            teacher_counts = pd.Series(all_teachers).value_counts()
            print("Teacher distribution:")
            for teacher, count in teacher_counts.items():
                print(f"  {teacher}: {count}")
        
        # Analyze lessons and sessions
        print("\n7. LESSON AND SESSION ANALYSIS")
        print("=" * 50)
        
        lesson_cols = [col for col in actual_data.columns if 'Lesson' in str(col)]
        session_cols = [col for col in actual_data.columns if 'Session' in str(col)]
        
        if lesson_cols:
            print(f"Found {len(lesson_cols)} lesson columns")
        if session_cols:
            print(f"Found {len(session_cols)} session columns")
        
        # Get unique session numbers
        all_sessions = []
        for col in session_cols:
            values = actual_data[col].dropna()
            all_sessions.extend(values)
        
        if all_sessions:
            session_counts = pd.Series(all_sessions).value_counts().sort_index()
            print("Session distribution:")
            for session, count in session_counts.items():
                print(f"  Session {session}: {count}")
        
        # Analyze dates
        print("\n8. DATE ANALYSIS")
        print("=" * 50)
        
        date_cols = [col for col in actual_data.columns if 'Date' in str(col)]
        if date_cols:
            print(f"Found {len(date_cols)} date columns")
            
            # Get unique dates
            all_dates = []
            for col in date_cols:
                values = actual_data[col].dropna()
                all_dates.extend(values)
            
            if all_dates:
                # Convert to datetime and analyze
                try:
                    date_series = pd.to_datetime(all_dates, errors='coerce')
                    valid_dates = date_series.dropna()
                    
                    if len(valid_dates) > 0:
                        print(f"Date range: {valid_dates.min()} to {valid_dates.max()}")
                        print(f"Total unique dates: {valid_dates.nunique()}")
                        
                        # Monthly distribution
                        monthly_counts = valid_dates.dt.to_period('M').value_counts().sort_index()
                        print("Monthly distribution:")
                        for month, count in monthly_counts.items():
                            print(f"  {month}: {count} sessions")
                except Exception as e:
                    print(f"Could not parse dates: {e}")
    
    else:
        print("✗ No actual data rows found in the dataset")
    
    print("\n9. DATA QUALITY ISSUES")
    print("=" * 50)
    
    # Check for data quality issues
    issues = []
    
    # Check for duplicate columns
    if len(df.columns) != len(set(df.columns)):
        issues.append("Duplicate column names detected")
    
    # Check for empty rows
    empty_rows = df.isnull().all(axis=1).sum()
    if empty_rows > 0:
        issues.append(f"{empty_rows} completely empty rows")
    
    # Check for inconsistent data types
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if numeric data is stored as strings
            numeric_count = 0
            total_count = 0
            for value in df[col].dropna():
                total_count += 1
                if str(value).replace('.', '').replace('-', '').isdigit():
                    numeric_count += 1
            
            if total_count > 0 and numeric_count / total_count > 0.5:
                issues.append(f"Column '{col}' contains mostly numeric data stored as strings")
    
    if issues:
        print("Data quality issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ No major data quality issues detected")
    
    print("\n10. RECOMMENDATIONS")
    print("=" * 50)
    print("1. The CSV structure appears to have repeated column patterns, suggesting")
    print("   multiple sessions or time periods in a wide format")
    print("2. Consider restructuring data into a long format for easier analysis")
    print("3. Standardize date formats across all date columns")
    print("4. Create consistent naming conventions for lesson and session identifiers")
    print("5. Implement data validation for attendance and progress ratings")
    print("6. Consider adding student IDs for better tracking across sessions")

if __name__ == "__main__":
    analyze_sandbox_data() 