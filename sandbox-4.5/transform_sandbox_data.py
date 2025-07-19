import pandas as pd
import re
from datetime import datetime
import numpy as np

def clean_and_transform_sandbox_data(input_file, output_file):
    """
    Transform the messy CurrentSandbox.csv into a clean weekly student progress format
    """
    
    # Read the raw CSV file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split the content by the repeated header pattern
    # The pattern is: Date,Attendance,CSguru / Interns ,Session,Submission Link/ Score,Lesson,Exit ticket scores,"Progress (1 to 5)"
    header_pattern = r'Date,Attendance,CSguru / Interns ,Session,Submission Link/ Score,Lesson,Exit ticket scores,"Progress\s*\(\s*1\s*to\s*5\s*"'
    
    # Find all occurrences of the header
    headers = re.findall(header_pattern, content)
    
    # Split the content by headers to get data chunks
    data_chunks = re.split(header_pattern, content)
    
    # Remove the first empty chunk if it exists
    if data_chunks[0].strip() == '':
        data_chunks = data_chunks[1:]
    
    # Process each data chunk
    all_records = []
    
    for i, chunk in enumerate(data_chunks):
        if chunk.strip() == '':
            continue
            
        # Split the chunk by commas, but be careful with quoted fields
        # This is a simplified approach - in practice, you might need a more robust CSV parser
        fields = chunk.split(',')
        
        # Each record should have 8 fields
        # We'll process them in groups of 8
        for j in range(0, len(fields), 8):
            if j + 7 < len(fields):
                record = fields[j:j+8]
                
                # Clean up the record
                cleaned_record = []
                for field in record:
                    # Remove quotes and extra whitespace
                    cleaned_field = field.strip().strip('"').strip("'")
                    cleaned_record.append(cleaned_field)
                
                # Only add records that have meaningful data
                if len(cleaned_record) == 8 and cleaned_record[0] and cleaned_record[0] != '-':
                    all_records.append(cleaned_record)
    
    # Create DataFrame
    columns = ['Date', 'Attendance', 'Teacher', 'Session', 'Submission_Link_Score', 'Lesson', 'Exit_Ticket_Scores', 'Progress']
    df = pd.DataFrame(all_records, columns=columns)
    
    # Clean up the data
    df = df[df['Date'].str.contains(r'\d{2}/\d{2}/\d{4}', na=False)]  # Only keep rows with valid dates
    
    # Convert date column
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    
    # Sort by date
    df = df.sort_values('Date')
    
    # Clean up attendance values
    df['Attendance'] = df['Attendance'].replace({
        'PH': 'Public Holiday',
        'No Class': 'No Class'
    })
    
    # Clean up progress values - convert star ratings to numbers
    def convert_stars_to_number(stars):
        if pd.isna(stars) or stars == '-':
            return np.nan
        star_count = stars.count('★')
        return star_count
    
    df['Progress_Score'] = df['Progress'].apply(convert_stars_to_number)
    
    # Extract session numbers
    df['Session_Number'] = df['Session'].str.extract(r'(\d+)').astype(float)
    
    # Create a summary by week
    weekly_summary = df.groupby(['Date', 'Teacher', 'Session_Number']).agg({
        'Attendance': 'first',
        'Lesson': lambda x: ' | '.join([str(i) for i in x if str(i) != '-']),
        'Exit_Ticket_Scores': lambda x: ' | '.join([str(i) for i in x if str(i) != '-']),
        'Progress_Score': 'mean'
    }).reset_index()
    
    # Add week number
    weekly_summary['Week_Number'] = weekly_summary['Date'].dt.isocalendar().week
    weekly_summary['Year'] = weekly_summary['Date'].dt.year
    
    # Reorder columns
    weekly_summary = weekly_summary[['Date', 'Year', 'Week_Number', 'Teacher', 'Session_Number', 'Attendance', 'Lesson', 'Exit_Ticket_Scores', 'Progress_Score']]
    
    # Save the cleaned data
    weekly_summary.to_csv(output_file, index=False)
    
    # Also save the detailed records
    detailed_output = output_file.replace('.csv', '_detailed.csv')
    df.to_csv(detailed_output, index=False)
    
    print(f"Transformation complete!")
    print(f"Weekly summary saved to: {output_file}")
    print(f"Detailed records saved to: {detailed_output}")
    print(f"\nSummary statistics:")
    print(f"Total records processed: {len(df)}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Teachers: {', '.join(df['Teacher'].unique())}")
    print(f"Average progress score: {df['Progress_Score'].mean():.2f}")
    
    return weekly_summary, df

if __name__ == "__main__":
    input_file = "CurrentSandbox.csv"
    output_file = "Weekly_Student_Progress.csv"
    
    weekly_summary, detailed_data = clean_and_transform_sandbox_data(input_file, output_file)
    
    # Display first few rows of the weekly summary
    print("\nWeekly Summary Preview:")
    print(weekly_summary.head(10)) 