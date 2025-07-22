import pandas as pd
import numpy as np

print("=== CREATING WIDE FORMAT CSV ===")

# Read the original CSV
df = pd.read_csv("sandbox-4.5/oldsandbox.csv")
print(f"Original shape: {df.shape}")

# Get the first row data
first_row = df.iloc[0]

# Define the 6 columns we want to extract
target_columns = ['Date', 'Session', 'Lesson', 'Attendance', 'Teacher', 'Progress']

# Create a list to store the wide format data
wide_data = []

# Process every 8 columns (one week) and extract the 6 columns we want
for week_num in range(0, len(first_row), 8):
    if week_num + 7 < len(first_row):  # Make sure we have all 8 columns
        # Extract the 6 columns we want
        date = first_row.iloc[week_num]  # Column 0
        session = first_row.iloc[week_num + 3]  # Column 3
        lesson = first_row.iloc[week_num + 5]  # Column 5
        attendance = first_row.iloc[week_num + 1]  # Column 1
        teacher = first_row.iloc[week_num + 2]  # Column 2
        progress = first_row.iloc[week_num + 7]  # Column 7
        
        # Add to wide data list
        wide_data.extend([date, session, lesson, attendance, teacher, progress])

print(f"Extracted {len(wide_data)} values from {len(wide_data)//6} weeks")

# Create column names for the wide format - KEEPING ORIGINAL NAMES
column_names = []
for week in range(len(wide_data) // 6):
    for col in target_columns:
        # Keep the original column names without incrementing
        column_names.append(col)

print(f"Created {len(column_names)} column names")

# Create the wide format DataFrame
wide_df = pd.DataFrame([wide_data], columns=column_names)

print(f"Wide format shape: {wide_df.shape}")
print(f"Columns: {len(wide_df.columns)}")

# Show the first few column names
print(f"\nFirst 12 column names:")
for i, col in enumerate(column_names[:12]):
    print(f"  Column {i}: {col}")

# Save the wide format CSV
output_file = "sandbox-4.5/03.extracted-row1-6cols-wide.csv"
wide_df.to_csv(output_file, index=False)
print(f"\nWide format CSV saved as: {output_file}")

print("\n=== VERIFICATION ===")
# Verify the structure
print(f"Shape: {wide_df.shape}")
print(f"Expected: (1, {len(wide_data)})")
print(f"Actual: {wide_df.shape}")

# Check if we have the right number of repetitions
expected_weeks = len(first_row) // 8
actual_weeks = len(wide_data) // 6
print(f"Expected weeks: {expected_weeks}")
print(f"Actual weeks: {actual_weeks}")