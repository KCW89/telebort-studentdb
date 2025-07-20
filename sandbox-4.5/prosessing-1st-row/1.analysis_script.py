import pandas as pd

# Read the CSV file
df = pd.read_csv("sandbox-4.5/prosessing-1st-row/sandbox.csv")

print("=== CSV ANALYSIS ===")
print(f"Shape: {df.shape}")
print(f"Columns: {len(df.columns)}")