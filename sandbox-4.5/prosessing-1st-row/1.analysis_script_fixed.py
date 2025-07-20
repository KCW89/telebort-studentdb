import pandas as pd

def read_csv_with_encoding(file_path):
    """
    Try to read CSV file with different encodings to handle encoding issues
    """
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-8-sig']
    
    for encoding in encodings:
        try:
            print(f"Trying to read with encoding: {encoding}")
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"✓ Successfully read with encoding: {encoding}")
            return df
        except UnicodeDecodeError as e:
            print(f"✗ Failed with encoding {encoding}: {e}")
            continue
        except Exception as e:
            print(f"✗ Other error with encoding {encoding}: {e}")
            continue
    
    print("❌ Failed to read file with any encoding")
    return None

# Read the CSV file with encoding handling
print("=== CSV ANALYSIS WITH ENCODING FIX ===")
df = read_csv_with_encoding("sandbox-4.5/prosessing-1st-row/sandbox.csv")

if df is not None:
    print(f"\nShape: {df.shape}")
    print(f"Columns: {len(df.columns)}")
    print(f"Rows: {len(df)}")
    
    # Show first few columns
    print(f"\nFirst 10 column names:")
    for i, col in enumerate(df.columns[:10]):
        print(f"  {i+1}: {col}")
    
    if len(df.columns) > 10:
        print(f"  ... and {len(df.columns) - 10} more columns")
    
    # Show first few rows
    print(f"\nFirst 3 rows (first 5 columns):")
    print(df.head(3).iloc[:, :5])
else:
    print("Could not read the CSV file. Please check the file path and encoding.") 