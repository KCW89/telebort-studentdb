import pandas as pd

# Read the CSV file
df = pd.read_csv("sandbox-4.5/sandbox.csv")

print("=== CSV ANALYSIS ===")
print(f"Shape: {df.shape}")
print(f"Columns: {len(df.columns)}")