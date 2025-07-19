import pandas as pd
import re
from datetime import datetime

def analyze_csv_structure(file_path):
    """
    Analyze the structure of the CSV file and identify where new rows should be created
    """
    print("=" * 60)
    print("CSV STRUCTURE ANALYSIS")
    print("=" * 60)
    
    # Read the raw file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📁 File: {file_path}")
    print(f"📏 Total characters: {len(content)}")
    print(f"📄 Total lines: {len(content.split(chr(10)))}")
    
    # Analyze the header structure
    print(f"\n🔍 HEADER ANALYSIS:")
    
    # Find the repeated header pattern
    header_pattern = r'Date,Attendance,CSguru / Interns ,Session,Submission Link/ Score,Lesson,Exit ticket scores,"Progress\s*\(\s*1\s*to\s*5\s*"'
    headers = re.findall(header_pattern, content)
    
    print(f"   • Header pattern found: {len(headers)} times")
    print(f"   • Header pattern: {header_pattern}")
    
    # Split content by headers to identify data chunks
    data_chunks = re.split(header_pattern, content)
    print(f"   • Data chunks found: {len(data_chunks)}")
    
    # Analyze each chunk
    print(f"\n📊 DATA CHUNK ANALYSIS:")
    
    for i, chunk in enumerate(data_chunks):
        if chunk.strip() == '':
            continue
            
        print(f"\n   Chunk {i+1}:")
        print(f"   • Length: {len(chunk)} characters")
        print(f"   • Lines: {len(chunk.split(chr(10)))}")
        
        # Count commas to estimate number of fields
        comma_count = chunk.count(',')
        print(f"   • Commas: {comma_count}")
        
        # Look for date patterns to identify records
        date_pattern = r'\d{2}/\d{2}/\d{4}'
        dates = re.findall(date_pattern, chunk)
        print(f"   • Date patterns found: {len(dates)}")
        
        if dates:
            print(f"   • Sample dates: {dates[:3]}")
    
    return headers, data_chunks

def identify_new_rows(file_path):
    """
    Identify where new rows should be created in the CSV
    """
    print(f"\n🔄 IDENTIFYING NEW ROW LOCATIONS:")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the field pattern for each record
    # Each record should have 8 fields: Date, Attendance, Teacher, Session, Submission, Lesson, Exit Ticket, Progress
    field_pattern = r'([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)'
    
    # Find all potential records
    records = re.findall(field_pattern, content)
    print(f"   • Potential records found: {len(records)}")
    
    # Filter for valid records (those with dates)
    valid_records = []
    for record in records:
        date_field = record[0].strip()
        if re.match(r'\d{2}/\d{2}/\d{4}', date_field):
            valid_records.append(record)
    
    print(f"   • Valid records with dates: {len(valid_records)}")
    
    # Show sample records
    print(f"\n📋 SAMPLE RECORDS:")
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

def create_proper_csv_structure(file_path, output_path):
    """
    Transform the malformed CSV into proper row-based structure
    """
    print(f"\n🔧 CREATING PROPER CSV STRUCTURE:")
    
    # Get valid records
    valid_records = identify_new_rows(file_path)
    
    if not valid_records:
        print("   ✗ No valid records found!")
        return
    
    # Create proper CSV structure
    columns = ['Date', 'Attendance', 'Teacher', 'Session', 'Submission_Link_Score', 
               'Lesson', 'Exit_Ticket_Scores', 'Progress_Rating']
    
    df = pd.DataFrame(valid_records, columns=columns)
    
    # Clean up the data
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # Convert date column
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    
    # Sort by date
    df = df.sort_values('Date')
    
    # Save the properly structured CSV
    df.to_csv(output_path, index=False)
    
    print(f"   ✓ Proper CSV created: {output_path}")
    print(f"   ✓ Total rows: {len(df)}")
    print(f"   ✓ Total columns: {len(df.columns)}")
    print(f"   ✓ Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    return df

def main():
    """
    Main function to run the CSV structure analysis
    """
    input_file = "CurrentSandbox.csv"
    output_file = "Properly_Structured_Sandbox.csv"
    
    # Analyze the current structure
    headers, chunks = analyze_csv_structure(input_file)
    
    # Identify where new rows should be
    valid_records = identify_new_rows(input_file)
    
    # Create properly structured CSV
    if valid_records:
        df = create_proper_csv_structure(input_file, output_file)
        
        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"   The original file has data spread across {len(headers)} repeated headers")
        print(f"   Proper structure should have {len(valid_records)} separate rows")
        print(f"   Each row represents one session/lesson record")
        print(f"   New properly structured file saved as: {output_file}")
    else:
        print(f"\n❌ NO VALID DATA FOUND!")
        print(f"   The file structure is too malformed to extract meaningful records")

if __name__ == "__main__":
    main() 