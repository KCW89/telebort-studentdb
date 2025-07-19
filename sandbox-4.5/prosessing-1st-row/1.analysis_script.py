import pandas as pd

# Read the CSV file
df = pd.read_csv("sandbox-4.5/prosessing-1st-row/sandbox.csv")

print("=== CSV ANALYSIS ===")
print(f"Shape: {df.shape}")
print(f"Columns: {len(df.columns)}")

# print("\n=== COLUMN NAMES ===")
# for i, col in enumerate(df.columns):
#     print(f"Column {i}: '{col}'")

# print("\n=== FIRST ROW DATA ===")
# for i, col in enumerate(df.columns):
#     print(f"Column {i} ('{col}'): {df.iloc[0, i]}")

# print("\n=== DATA TYPES ===")
# print(df.dtypes)

# print("\n=== MISSING VALUES ===")
# print(df.isnull().sum())

# print("\n=== FIRST FEW COLUMNS ===")
# print(df.columns[:10].tolist())

# print("\n=== SAMPLE DATA ===")
# print(df.head()) 