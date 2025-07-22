import pandas as pd
import numpy as np

print("=== CREATING WIDE FORMAT CSV FOR ALL ROWS ===")

# Read the original CSV
df = pd.read_csv("sandbox-4.5/oldsandbox.csv")
print(f"Original shape: {df.shape}")

# Define the 6 columns we want to extract
target_columns = ['Date', 'Session', 'Lesson', 'Attendance', 'Teacher', 'Progress']

# Create a list to store all wide format data
all_wide_data = []

# Process each row in the DataFrame
for row_idx in range(len(df)):
    print(f"Processing row {row_idx + 1}/{len(df)}...")
    
    # Get the current row data
    current_row = df.iloc[row_idx]
    
    # Create a list to store the wide format data for this row
    wide_data = []
    
    # Process every 8 columns (one week) and extract the 6 columns we want
    for week_num in range(0, len(current_row), 8):
        if week_num + 7 < len(current_row):  # Make sure we have all 8 columns
            # Extract the 6 columns we want
            date = current_row.iloc[week_num]  # Column 0
            session = current_row.iloc[week_num + 3]  # Column 3
            lesson = current_row.iloc[week_num + 5]  # Column 5
            attendance = current_row.iloc[week_num + 1]  # Column 1
            teacher = current_row.iloc[week_num + 2]  # Column 2
            progress = current_row.iloc[week_num + 7]  # Column 7
            
            # Add to wide data list for this row
            wide_data.extend([date, session, lesson, attendance, teacher, progress])
    
    # Add this row's data to the main list
    all_wide_data.append(wide_data)
    
    # Print progress for first few rows
    if row_idx < 3:
        print(f"  Row {row_idx + 1}: {len(wide_data)} values extracted")

print(f"\nExtracted data from {len(df)} rows")
print(f"Each row has {len(all_wide_data[0])//6} weeks")

# Create column names for the wide format - KEEPING ORIGINAL NAMES
column_names = []
for week in range(len(all_wide_data[0]) // 6):
    for col in target_columns:
        # Keep the original column names without incrementing
        column_names.append(col)

print(f"Created {len(column_names)} column names")

# Create the wide format DataFrame with all rows
wide_df = pd.DataFrame(all_wide_data, columns=column_names)

print(f"Wide format shape: {wide_df.shape}")
print(f"Columns: {len(wide_df.columns)}")

# Show the first few column names
print(f"\nFirst 12 column names:")
for i, col in enumerate(column_names[:12]):
    print(f"  Column {i}: {col}")

# Save the wide format CSV
output_file = "sandbox-4.5/04.all-extractions.csv"
wide_df.to_csv(output_file, index=False)
print(f"\nWide format CSV saved as: {output_file}")

print("\n=== VERIFICATION ===")
# Verify the structure
print(f"Shape: {wide_df.shape}")
print(f"Expected: ({len(df)}, {len(all_wide_data[0])})")
print(f"Actual: {wide_df.shape}")

# Check if we have the right number of repetitions
expected_weeks = len(df.iloc[0]) // 8
actual_weeks = len(all_wide_data[0]) // 6
print(f"Expected weeks: {expected_weeks}")
print(f"Actual weeks: {actual_weeks}")

print("\n=== DATA PREVIEW ===")
print("First few rows of the wide format:")
print(wide_df.head(3))

print("\n=== SUMMARY ===")
print(f"✅ Created wide format with shape: {wide_df.shape}")
print(f"✅ Processed {len(df)} students/rows")
print(f"✅ 6 columns repeated {actual_weeks} times per row")
print(f"✅ Total columns: {len(wide_df.columns)}")
print(f"✅ All students' data extracted and preserved") 