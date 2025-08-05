#!/usr/bin/env python3
"""
sync_sheets.py - Fetches student data from Google Sheets via Zapier MCP

This script connects to the Telebort student database Google Sheet and 
extracts all student records with their session data.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Constants for the Google Sheet
SPREADSHEET_ID = "1zbw7hLSa-5k83T0d6KrD-eiZv5nM855oYHV_B-tslbU"
WORKSHEET_ID = "891163674"

# Column indices (0-based)
FIXED_COLUMNS = {
    'student_name': 0,      # A
    'status': 1,           # B
    'student_id': 2,       # C
    'program': 3,          # D
    'day': 4,              # E
    'start_time': 5,       # F
    'end_time': 6,         # G
    'teacher': 7           # H
}

# Repeating pattern starts at column I (index 8)
PATTERN_START = 8
PATTERN_LENGTH = 5  # Date, Session, Lesson, Attendance, Progress


class SheetsSyncManager:
    """Manages synchronization with Google Sheets via Zapier MCP"""
    
    def __init__(self):
        """Initialize the sync manager"""
        self.spreadsheet_id = SPREADSHEET_ID
        self.worksheet_id = WORKSHEET_ID
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('SheetsSyncManager')
        logger.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler('logs/sync_history.log')
        fh.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        
        logger.addHandler(ch)
        logger.addHandler(fh)
        
        return logger
    
    def fetch_all_students(self) -> List[Dict[str, Any]]:
        """
        Fetch all student records from Google Sheets
        
        Returns:
            List of dictionaries containing student data
        """
        self.logger.info(f"Starting fetch from spreadsheet {self.spreadsheet_id}")
        
        try:
            # In a real implementation, this would use Zapier MCP
            # For now, we'll structure the expected output
            students = []
            
            # This is where we would call:
            # mcp__zapier__google_sheets_get_many_spreadsheet_rows_advanced
            
            # Placeholder for actual implementation
            self.logger.info("Fetching student data via Zapier MCP...")
            
            # For development, return empty list
            # In production, this would return parsed data
            
            self.logger.info(f"Fetched {len(students)} student records")
            return students
            
        except Exception as e:
            self.logger.error(f"Error fetching data: {str(e)}")
            raise
    
    def parse_student_sessions(self, row_data: List[Any]) -> Dict[str, Any]:
        """
        Parse a student row into structured data
        
        Args:
            row_data: Raw row data from spreadsheet
            
        Returns:
            Dictionary with student info and sessions
        """
        # Extract fixed columns
        student_info = {
            'student_name': row_data[FIXED_COLUMNS['student_name']] if len(row_data) > FIXED_COLUMNS['student_name'] else '',
            'status': row_data[FIXED_COLUMNS['status']] if len(row_data) > FIXED_COLUMNS['status'] else '',
            'student_id': row_data[FIXED_COLUMNS['student_id']] if len(row_data) > FIXED_COLUMNS['student_id'] else '',
            'program': row_data[FIXED_COLUMNS['program']] if len(row_data) > FIXED_COLUMNS['program'] else '',
            'day': row_data[FIXED_COLUMNS['day']] if len(row_data) > FIXED_COLUMNS['day'] else '',
            'start_time': row_data[FIXED_COLUMNS['start_time']] if len(row_data) > FIXED_COLUMNS['start_time'] else '',
            'end_time': row_data[FIXED_COLUMNS['end_time']] if len(row_data) > FIXED_COLUMNS['end_time'] else '',
            'teacher': row_data[FIXED_COLUMNS['teacher']] if len(row_data) > FIXED_COLUMNS['teacher'] else ''
        }
        
        # Extract session data from repeating columns
        sessions = []
        current_index = PATTERN_START
        
        while current_index + PATTERN_LENGTH <= len(row_data):
            # Extract one session's data
            session_data = {
                'date': row_data[current_index] if current_index < len(row_data) else '',
                'session': row_data[current_index + 1] if current_index + 1 < len(row_data) else '',
                'lesson': row_data[current_index + 2] if current_index + 2 < len(row_data) else '',
                'attendance': row_data[current_index + 3] if current_index + 3 < len(row_data) else '',
                'progress': row_data[current_index + 4] if current_index + 4 < len(row_data) else ''
            }
            
            # Only add non-empty sessions
            if any(session_data.values()):
                sessions.append(session_data)
            
            current_index += PATTERN_LENGTH
        
        return {
            'info': student_info,
            'sessions': sessions
        }
    
    def save_raw_data(self, data: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Save raw data to JSON file for debugging
        
        Args:
            data: Student data to save
            filename: Optional filename, defaults to timestamp
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logs/raw_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved raw data to {filename}")
        return filename
    
    def validate_data(self, students: List[Dict[str, Any]]) -> List[str]:
        """
        Validate student data and return list of issues
        
        Args:
            students: List of student records
            
        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        
        for i, student in enumerate(students):
            # Check required fields
            if not student.get('info', {}).get('student_id'):
                issues.append(f"Row {i+1}: Missing student ID")
            
            if not student.get('info', {}).get('program'):
                issues.append(f"Row {i+1}: Missing program")
            
            # Check for at least one session
            if not student.get('sessions'):
                issues.append(f"Row {i+1}: No session data found")
        
        return issues


def main():
    """Main function for testing"""
    sync_manager = SheetsSyncManager()
    
    try:
        # Fetch all students
        students = sync_manager.fetch_all_students()
        
        # Validate data
        issues = sync_manager.validate_data(students)
        if issues:
            print("Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
        
        # Save raw data
        if students:
            sync_manager.save_raw_data(students)
        
        print(f"Successfully processed {len(students)} students")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())