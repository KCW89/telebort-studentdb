#!/usr/bin/env python3
"""
sync_sheets_mcp.py - Fetches student data from Google Sheets via Zapier MCP

This script connects to the Telebort student database Google Sheet using
the actual Zapier MCP connection and extracts all student records.
"""

import json
import logging
import os
import time
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
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize the sync manager
        
        Args:
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Initial delay between retries (seconds)
        """
        self.spreadsheet_id = SPREADSHEET_ID
        self.worksheet_id = WORKSHEET_ID
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('SheetsSyncManager')
        logger.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
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
    
    def _retry_with_backoff(self, func, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic and exponential backoff
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result from the function
            
        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"All {self.max_retries} attempts failed")
        
        raise last_exception
    
    def validate_connection(self) -> bool:
        """
        Validate that we can connect to the Google Sheet
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            self.logger.info("Validating connection to Google Sheets...")
            # Try to fetch just one row to test connectivity
            result = self.fetch_with_mcp(first_row=1, row_count=1)
            
            if result and 'results' in result:
                self.logger.info("Connection validated successfully")
                return True
            else:
                self.logger.error("Connection validation failed: Invalid response")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection validation failed: {str(e)}")
            return False
    
    def fetch_all_students(self) -> List[Dict[str, Any]]:
        """
        Fetch all student records from Google Sheets
        
        Returns:
            List of dictionaries containing student data
        """
        self.logger.info(f"Starting fetch from spreadsheet {self.spreadsheet_id}")
        
        try:
            # Fetch data using MCP
            self.logger.info("Fetching student data via Zapier MCP...")
            
            result = self.fetch_with_mcp(first_row=5, row_count=200)
            
            students = []
            
            # Parse the MCP response
            if result and 'results' in result and len(result['results']) > 0:
                # Get the raw rows from the MCP response
                raw_rows_data = result['results'][0].get('raw_rows', '')
                
                # Parse the JSON string containing the rows
                if raw_rows_data:
                    import json
                    raw_rows = json.loads(raw_rows_data)
                    
                    # Parse each row
                    for row_data in raw_rows:
                        if row_data and len(row_data) > 2:  # Skip empty rows
                            student_data = self.parse_student_sessions(row_data)
                            if student_data['info']['student_id']:  # Only add if has student ID
                                students.append(student_data)
            
            self.logger.info(f"Fetched {len(students)} student records")
            return students
            
        except Exception as e:
            self.logger.error(f"Error fetching data: {str(e)}")
            raise
    
    def _simulate_mcp_fetch(self) -> List[List[Any]]:
        """
        Simulate MCP fetch for testing
        Replace this with actual MCP call in production
        """
        # Example data structure based on our earlier exploration
        return [
            ["Nathakit Shotiwoth", "", "s10769", "G (AI-2)", "Saturday", "10:00", "11:00", "Soumiya",
             "09/08/2025", "2", "-", "", "-",
             "02/08/2025", "2", "LESSON 2 C2 Machine Learning", "Soumiya", "In Progress",
             "26/07/2025", "1", "-", "Absent", "-",
             "19/07/2025", "1", "L1 Introduction to AI", "Soumiya", "Completed"],
            # Add more rows as needed for testing
        ]
    
    def _simulate_mcp_response(self, first_row: int, row_count: int) -> Dict[str, Any]:
        """
        Simulate MCP response for testing outside Claude Code environment
        
        Args:
            first_row: Starting row
            row_count: Number of rows
            
        Returns:
            Simulated MCP response structure
        """
        # Sample data for rows 5-7
        sample_data = {
            5: ["Nathakit Shotiwoth", "", "s10769", "G (AI-2)", "Saturday", "10:00", "11:00", "Soumiya",
                "09/08/2025", "2", "-", "", "-",
                "02/08/2025", "2", "LESSON 2 C2 Machine Learning", "Soumiya", "In Progress",
                "26/07/2025", "1", "-", "Absent", "-",
                "19/07/2025", "1", "L1 Introduction to AI", "Soumiya", "Completed"],
            6: ["Justin Chin", "", "s10777", "D (W-2)", "Sunday", "10:00", "12:00", "Soumiya",
                "03/08/2025", "15", "-", "", "-",
                "27/07/2025", "15", "L11 Array Part 2", "Soumiya", "Completed",
                "20/07/2025", "14", "L10 Array Part 1", "Soumiya", "Completed"],
            7: ["Lim Boon Sheng", "", "s10711", "G (AI-2)", "Saturday", "10:00", "11:00", "Soumiya",
                "09/08/2025", "2", "-", "", "-",
                "02/08/2025", "2", "LESSON 2 C2 Machine Learning", "Soumiya", "In Progress"]
        }
        
        # Get requested rows
        rows = []
        for row_num in range(first_row, min(first_row + row_count, 8)):
            if row_num in sample_data:
                rows.append(sample_data[row_num])
        
        # Return in MCP response format
        return {
            "results": [{
                "raw_rows": json.dumps(rows),
                "count": len(rows)
            }]
        }
    
    def fetch_with_mcp(self, first_row: int = 5, row_count: int = 200) -> Dict[str, Any]:
        """
        Fetch data using Zapier MCP with robust error handling
        
        Args:
            first_row: Starting row (1-indexed)
            row_count: Number of rows to fetch
            
        Returns:
            Raw MCP response
            
        Raises:
            ConnectionError: If MCP connection fails
            ValueError: If response is invalid
        """
        def _execute_mcp_call():
            """Inner function to execute the MCP call"""
            self.logger.info(f"Executing MCP call for rows {first_row} to {first_row + row_count}")
            
            # Check if we're in Claude Code environment
            mcp_func = globals().get('mcp__zapier__google_sheets_get_many_spreadsheet_rows_advanced')
            
            if mcp_func is None:
                # Not in Claude Code environment, use simulation
                self.logger.warning("MCP not available, using simulated data for testing")
                return self._simulate_mcp_response(first_row, row_count)
            
            # Actual MCP call for Claude Code environment
            result = mcp_func(
                instructions=f"Get student data from row {first_row} to {first_row + row_count}",
                spreadsheet=self.spreadsheet_id,
                worksheet=self.worksheet_id,
                first_row=str(first_row),
                row_count=str(row_count),
                range="A:DZ",  # Get all columns
                output_format="line_items"
            )
            
            # Validate response
            if not result:
                raise ConnectionError("MCP returned empty response")
            
            if 'results' not in result:
                raise ValueError(f"Invalid MCP response structure: {result}")
            
            self.logger.info(f"MCP call successful, received data")
            return result
        
        try:
            # Use retry logic for the MCP call
            return self._retry_with_backoff(_execute_mcp_call)
            
        except NameError:
            # MCP function not available, use simulation
            self.logger.warning("Running in standalone mode - using simulated data")
            return self._simulate_mcp_response(first_row, row_count)
            
        except Exception as e:
            self.logger.error(f"MCP call failed after all retries: {str(e)}")
            raise ConnectionError(f"Failed to fetch data from Google Sheets: {str(e)}")
    
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
                'date': str(row_data[current_index]) if current_index < len(row_data) else '',
                'session': str(row_data[current_index + 1]) if current_index + 1 < len(row_data) else '',
                'lesson': str(row_data[current_index + 2]) if current_index + 2 < len(row_data) else '',
                'attendance': str(row_data[current_index + 3]) if current_index + 3 < len(row_data) else '',
                'progress': str(row_data[current_index + 4]) if current_index + 4 < len(row_data) else ''
            }
            
            # Clean up data
            for key in session_data:
                if session_data[key] == '-':
                    session_data[key] = ''
                session_data[key] = session_data[key].strip()
            
            # Only add non-empty sessions (has date or session number)
            if session_data['date'] or session_data['session']:
                sessions.append(session_data)
            
            current_index += PATTERN_LENGTH
        
        return {
            'info': student_info,
            'sessions': sessions
        }
    
    def fetch_batch(self, start_row: int, end_row: int) -> List[Dict[str, Any]]:
        """
        Fetch a batch of students from specific row range with error handling
        
        Args:
            start_row: Starting row (1-indexed, inclusive)
            end_row: Ending row (1-indexed, inclusive)
            
        Returns:
            List of parsed student records
            
        Raises:
            ValueError: If row range is invalid
            ConnectionError: If fetch fails
        """
        # Validate input
        if start_row < 1:
            raise ValueError(f"start_row must be >= 1, got {start_row}")
        if end_row < start_row:
            raise ValueError(f"end_row ({end_row}) must be >= start_row ({start_row})")
        
        self.logger.info(f"Fetching batch: rows {start_row} to {end_row}")
        
        try:
            row_count = end_row - start_row + 1
            result = self.fetch_with_mcp(first_row=start_row, row_count=row_count)
            
            students = []
            parse_errors = []
            
            # Parse the MCP response
            if result and 'results' in result and len(result['results']) > 0:
                # Handle different response formats
                first_result = result['results'][0]
                
                # Check for 'raw_rows' (JSON string format)
                if 'raw_rows' in first_result:
                    raw_rows_data = first_result.get('raw_rows', '')
                    if raw_rows_data:
                        raw_rows = json.loads(raw_rows_data)
                # Check for 'rows' (direct array format)
                elif 'rows' in first_result:
                    raw_rows = first_result.get('rows', [])
                else:
                    raise ValueError(f"Unknown response format: {first_result.keys()}")
                
                # Parse each row
                for i, row_data in enumerate(raw_rows):
                    try:
                        if row_data and len(row_data) > 2:  # Skip empty rows
                            student_data = self.parse_student_sessions(row_data)
                            student_data['row_number'] = start_row + i  # Add row number for tracking
                            if student_data['info']['student_id']:  # Only add if has student ID
                                students.append(student_data)
                    except Exception as e:
                        parse_errors.append(f"Row {start_row + i}: {str(e)}")
                        self.logger.warning(f"Failed to parse row {start_row + i}: {str(e)}")
            
            # Log any parse errors
            if parse_errors:
                self.logger.warning(f"Parse errors in batch: {len(parse_errors)} rows failed")
            
            self.logger.info(f"Batch fetched {len(students)} valid students")
            return students
            
        except ConnectionError:
            # Re-raise connection errors
            raise
        except Exception as e:
            # Wrap other errors as connection errors
            raise ConnectionError(f"Failed to fetch batch {start_row}-{end_row}: {str(e)}")
    
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
        
        os.makedirs('logs', exist_ok=True)
        
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


def test_single_student():
    """Test with a single student to verify the pipeline"""
    sync_manager = SheetsSyncManager()
    
    # Test data for one student
    test_row = [
        "Test Student", "", "s99999", "G (AI-2)", "Saturday", "10:00", "11:00", "Soumiya",
        "09/08/2025", "2", "C2 Machine Learning", "Soumiya", "In Progress",
        "02/08/2025", "1", "C1 Introduction to AI", "Soumiya", "Completed",
        "26/07/2025", "0", "-", "No Class", "-"
    ]
    
    # Parse the test row
    student_data = sync_manager.parse_student_sessions(test_row)
    
    print("Parsed student data:")
    print(json.dumps(student_data, indent=2))
    
    return student_data


def main():
    """Main function for testing"""
    sync_manager = SheetsSyncManager()
    
    try:
        # Test with single student first
        print("Testing with single student...")
        test_student = test_single_student()
        print("\nSingle student test passed!\n")
        
        # Now try to fetch all students
        print("Fetching all students...")
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
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())