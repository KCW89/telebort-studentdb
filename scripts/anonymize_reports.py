#!/usr/bin/env python3
"""
Anonymize student reports by removing real names.
Creates anonymized versions suitable for public repository.
"""

import os
import re
from pathlib import Path

def anonymize_report(file_path):
    """Anonymize a single report file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract student ID from filename
    student_id = Path(file_path).stem
    
    # Replace name line with anonymized version
    content = re.sub(
        r'\*\*Name:\*\* .+',
        f'**Name:** [Anonymized]',
        content
    )
    
    # Replace any teacher names in "Primary Teacher" field with "Teacher"
    content = re.sub(
        r'\*\*Primary Teacher:\*\* (?!Teacher)(?!\d{2}/\d{2}/\d{4}).+',
        '**Primary Teacher:** Teacher',
        content
    )
    
    return content

def create_anonymized_reports(source_dir, dest_dir):
    """Create anonymized versions of all reports."""
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    
    # Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Process all .md files
    report_files = list(source_path.glob('*.md'))
    
    print(f"Found {len(report_files)} reports to anonymize")
    
    for report_file in report_files:
        if report_file.name == 'Not Enrolled Yet.md':
            # Skip this special file
            continue
            
        try:
            anonymized_content = anonymize_report(report_file)
            
            # Write anonymized version
            dest_file = dest_path / report_file.name
            with open(dest_file, 'w') as f:
                f.write(anonymized_content)
                
            print(f"Anonymized: {report_file.name}")
            
        except Exception as e:
            print(f"Error processing {report_file.name}: {e}")
    
    print(f"\nAnonymization complete. Anonymized reports saved to {dest_dir}")

if __name__ == "__main__":
    # Anonymize reports from /reports to /reports_anonymized
    source_directory = "/Users/chongwei/Telebort Engineering/telebort-studentdb/reports"
    dest_directory = "/Users/chongwei/Telebort Engineering/telebort-studentdb/reports_anonymized"
    
    create_anonymized_reports(source_directory, dest_directory)