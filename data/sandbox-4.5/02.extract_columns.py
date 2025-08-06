import pandas as pd
import numpy as np

print("=== EXTRACTING SPECIFIC COLUMNS ===")

# Read the original CSV
df = pd.read_csv("sandbox-4.5/oldsandbox.csv")
print(f"Original shape: {df.shape}")

# Define the 6 columns we want to extract
# Mapping from sandbox.csv columns to new columns
column_mapping = {
    'Date': 'Date',
    'Session': 'Session', 
    'Lesson': 'Lesson',
    'Attendance': 'Attendance',
    'CSguru / Interns': 'Teacher',  # Map the teacher column
    'Progress (1 to 5)': 'Progress'  # Map the progress column
}

print(f"\nColumn mapping:")
for old_col, new_col in column_mapping.items():
    print(f"  {old_col} → {new_col}")

# Get the first row data
first_row = df.iloc[0]

# Create a list to store the extracted data
extracted_data = []

# Process every 8 columns (one week) and extract the 6 columns we want
for week_num in range(0, len(first_row), 8):
    if week_num + 7 < len(first_row):  # Make sure we have all 8 columns
        week_data = {}
        
        # Extract the 6 columns we want
        week_data['Date'] = first_row.iloc[week_num]  # Column 0
        week_data['Session'] = first_row.iloc[week_num + 3]  # Column 3
        week_data['Lesson'] = first_row.iloc[week_num + 5]  # Column 5
        week_data['Attendance'] = first_row.iloc[week_num + 1]  # Column 1
        week_data['Teacher'] = first_row.iloc[week_num + 2]  # Column 2
        week_data['Progress'] = first_row.iloc[week_num + 7]  # Column 7
        
        extracted_data.append(week_data)

# Create new DataFrame with extracted data
new_df = pd.DataFrame(extracted_data)

print(f"\nExtracted shape: {new_df.shape}")
print(f"New columns: {list(new_df.columns)}")

# Clean up the data
print("\n=== CLEANING DATA ===")

# Remove rows where all values are empty or '-'
new_df = new_df.replace(['', '-', 'nan', 'NaN'], np.nan)
new_df = new_df.dropna(how='all')

# Clean up specific columns
new_df['Session'] = pd.to_numeric(new_df['Session'], errors='coerce')
new_df['Date'] = pd.to_datetime(new_df['Date'], errors='coerce')

print(f"After cleaning: {new_df.shape}")

# Sort by date
new_df = new_df.sort_values('Date', ascending=False)

print("\n=== EXTRACTED DATA PREVIEW ===")
print(new_df.head(10))

# Save the new CSV
output_file = "sandbox-4.5/02.extracted-row1.csv"
new_df.to_csv(output_file, index=False)
print(f"\nNew CSV saved as: {output_file}")

print("\n=== SUMMARY ===")
print(f"Original columns: 8 columns × 60 weeks = 480 columns")
print(f"Extracted columns: 6 columns × {len(new_df)} weeks = {len(new_df)} rows")
print(f"Columns extracted: {list(new_df.columns)}")

# Show some statistics
print(f"\n=== STATISTICS ===")
print(f"Date range: {new_df['Date'].min()} to {new_df['Date'].max()}")
print(f"Session range: {new_df['Session'].min()} to {new_df['Session'].max()}")
print(f"Teachers: {new_df['Teacher'].nunique()}")
print(f"Attendance breakdown:")
print(new_df['Attendance'].value_counts()) 