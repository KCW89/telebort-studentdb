import pandas as pd
import re
from datetime import datetime

def analyze_csv_line_by_line(file_path):
    """
    Analyze the CSV file line by line to understand its structure
    """
    print("=" * 60)
    print("LINE-BY-LINE CSV ANALYSIS")
    print("=" * 60)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📁 File: {file_path}")
    print(f"📄 Total lines: {len(lines)}")
    
    # Analyze the first line (header)
    print(f"\n🔍 HEADER LINE ANALYSIS:")
    header_line = lines[0].strip()
    print(f"   Header length: {len(header_line)} characters")
    print(f"   Header content: {header_line[:200]}...")
    
    # Count commas in header
    comma_count = header_line.count(',')
    print(f"   Commas in header: {comma_count}")
    
    # Split header by commas to see the structure
    header_fields = header_line.split(',')
    print(f"   Header fields: {len(header_fields)}")
    
    # Look for repeated patterns in header
    print(f"\n📊 HEADER PATTERN ANALYSIS:")
    
    # Find the base header pattern
    base_header = "Date,Attendance,CSguru / Interns ,Session,Submission Link/ Score,Lesson,Exit ticket scores,\"Progress (1 to 5)\""
    print(f"   Base header pattern: {base_header}")
    
    # Count how many times this pattern repeats
    pattern_count = header_line.count("Date,Attendance,CSguru / Interns ,Session")
    print(f"   Pattern repetitions: {pattern_count}")
    
    # Analyze data lines
    print(f"\n📋 DATA LINE ANALYSIS:")
    
    for i, line in enumerate(lines[1:6]):  # Look at first 5 data lines
        if line.strip():
            print(f"\n   Line {i+2}:")
            print(f"   • Length: {len(line.strip())} characters")
            print(f"   • Commas: {line.count(',')}")
            
            # Look for date patterns
            date_pattern = r'\d{2}/\d{2}/\d{4}'
            dates = re.findall(date_pattern, line)
            print(f"   • Dates found: {len(dates)}")
            if dates:
                print(f"   • Sample dates: {dates[:3]}")
            
            # Show first 200 characters
            print(f"   • Content preview: {line.strip()[:200]}...")
    
    return lines, header_fields

def extract_records_from_line(line):
    """
    Extract individual records from a single line
    """
    # Split by the pattern that indicates a new record
    # Look for date patterns as record separators
    date_pattern = r'\d{2}/\d{2}/\d{4}'
    
    # Find all date positions
    date_matches = list(re.finditer(date_pattern, line))
    
    records = []
    for i, match in enumerate(date_matches):
        start_pos = match.start()
        
        # Extract the record starting from this date
        if i < len(date_matches) - 1:
            end_pos = date_matches[i + 1].start()
            record_text = line[start_pos:end_pos]
        else:
            record_text = line[start_pos:]
        
        # Split by commas to get fields
        fields = record_text.split(',')
        
        # Clean up fields
        cleaned_fields = []
        for field in fields[:8]:  # Take first 8 fields
            cleaned_field = field.strip().strip('"').strip("'")
            cleaned_fields.append(cleaned_field)
        
        # Pad with empty strings if less than 8 fields
        while len(cleaned_fields) < 8:
            cleaned_fields.append('')
        
        records.append(cleaned_fields[:8])
    
    return records

def analyze_all_records(file_path):
    """
    Extract and analyze all records from the CSV file
    """
    print(f"\n🔄 EXTRACTING ALL RECORDS:")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    all_records = []
    
    for line_num, line in enumerate(lines[1:], 1):  # Skip header
        if line.strip():
            records = extract_records_from_line(line)
            all_records.extend(records)
            print(f"   Line {line_num}: Found {len(records)} records")
    
    print(f"\n📊 RECORD SUMMARY:")
    print(f"   Total records extracted: {len(all_records)}")
    
    # Filter valid records (those with proper dates)
    valid_records = []
    for record in all_records:
        if record[0] and re.match(r'\d{2}/\d{2}/\d{4}', record[0]):
            valid_records.append(record)
    
    print(f"   Valid records with dates: {len(valid_records)}")
    
    # Show sample records
    print(f"\n📋 SAMPLE VALID RECORDS:")
    for i, record in enumerate(valid_records[:5]):
        print(f"   Record {i+1}:")
        print(f"     Date: {record[0]}")
        print(f"     Attendance: {record[1]}")
        print(f"     Teacher: {record[2]}")
        print(f"     Session: {record[3]}")
        print(f"     Submission: {record[4]}")
        print(f"     Lesson: {record[5]}")
        print(f"     Exit Ticket: {record[6]}")
        print(f"     Progress: {record[7]}")
        print()
    
    return valid_records

def create_clean_csv(records, output_path):
    """
    Create a clean, properly structured CSV file
    """
    print(f"\n🔧 CREATING CLEAN CSV:")
    
    if not records:
        print("   ✗ No valid records to process!")
        return None
    
    # Create DataFrame
    columns = ['Date', 'Attendance', 'Teacher', 'Session', 'Submission_Link_Score', 
               'Lesson', 'Exit_Ticket_Scores', 'Progress_Rating']
    
    df = pd.DataFrame(records, columns=columns)
    
    # Clean up the data
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # Convert date column
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    
    # Remove rows with invalid dates
    df = df.dropna(subset=['Date'])
    
    # Sort by date
    df = df.sort_values('Date')
    
    # Save the clean CSV
    df.to_csv(output_path, index=False)
    
    print(f"   ✓ Clean CSV created: {output_path}")
    print(f"   ✓ Total rows: {len(df)}")
    print(f"   ✓ Total columns: {len(df.columns)}")
    print(f"   ✓ Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    return df

def main():
    """
    Main function to run the improved CSV analysis
    """
    input_file = "CurrentSandbox.csv"
    output_file = "Clean_Structured_Sandbox.csv"
    
    # Analyze the file structure
    lines, header_fields = analyze_csv_line_by_line(input_file)
    
    # Extract all records
    valid_records = analyze_all_records(input_file)
    
    # Create clean CSV
    if valid_records:
        df = create_clean_csv(valid_records, output_file)
        
        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"   Original file had data spread across multiple columns")
        print(f"   Extracted {len(valid_records)} individual session records")
        print(f"   Each record represents one lesson/session")
        print(f"   Clean structured file saved as: {output_file}")
        
        # Show summary statistics
        if df is not None:
            print(f"\n📈 SUMMARY STATISTICS:")
            print(f"   Unique teachers: {df['Teacher'].nunique()}")
            print(f"   Unique sessions: {df['Session'].nunique()}")
            print(f"   Attendance distribution:")
            print(df['Attendance'].value_counts())
    else:
        print(f"\n❌ NO VALID DATA FOUND!")
        print(f"   Could not extract meaningful records from the file")

if __name__ == "__main__":
    main() 