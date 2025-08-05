#!/usr/bin/env python3
"""
batch_processor.py - Unified batch processor for student data

This module consolidates all batch processing functionality into a single,
configurable processor that can handle any row range or batch size.
"""

import json
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_sheets_mcp import SheetsSyncManager
from process_data import DataProcessor
from generate_reports import ReportGenerator
from data_validator import DataValidator
from monitoring import SyncMonitor


class BatchProcessor:
    """Unified batch processor for student data"""
    
    # Default batch configurations
    DEFAULT_BATCH_SIZE = 20
    MAX_BATCH_SIZE = 50  # MCP token limit safety
    
    def __init__(self, batch_size: int = DEFAULT_BATCH_SIZE, validate_data: bool = True):
        """
        Initialize the batch processor
        
        Args:
            batch_size: Number of rows to process in each batch
            validate_data: Whether to perform data validation
        """
        self.batch_size = min(batch_size, self.MAX_BATCH_SIZE)
        self.validate_data = validate_data
        self.sync_manager = SheetsSyncManager()
        self.processor = DataProcessor()
        self.generator = ReportGenerator()
        self.validator = DataValidator() if validate_data else None
        self.monitor = SyncMonitor()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('BatchProcessor')
        logger.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(ch)
        
        return logger
    
    def process_range(self, start_row: int, end_row: int) -> Dict[str, Any]:
        """
        Process a range of rows in batches
        
        Args:
            start_row: Starting row (1-indexed, inclusive)
            end_row: Ending row (1-indexed, inclusive)
            
        Returns:
            Summary of processing results
        """
        self.logger.info(f"Processing rows {start_row} to {end_row} in batches of {self.batch_size}")
        
        results = {
            'start_row': start_row,
            'end_row': end_row,
            'batch_size': self.batch_size,
            'batches_processed': 0,
            'students_fetched': 0,
            'students_processed': 0,
            'reports_generated': 0,
            'reports_unchanged': 0,
            'errors': [],
            'student_ids': []
        }
        
        # Process in batches
        current_row = start_row
        batch_num = 1
        
        while current_row <= end_row:
            batch_end = min(current_row + self.batch_size - 1, end_row)
            
            self.logger.info(f"\nBatch {batch_num}: rows {current_row} to {batch_end}")
            
            try:
                # Process this batch
                batch_results = self._process_batch(current_row, batch_end)
                
                # Update results
                results['batches_processed'] += 1
                results['students_fetched'] += batch_results['fetched']
                results['students_processed'] += batch_results['processed']
                results['reports_generated'] += batch_results['generated']
                results['reports_unchanged'] += batch_results['unchanged']
                results['errors'].extend(batch_results['errors'])
                results['student_ids'].extend(batch_results['student_ids'])
                
            except Exception as e:
                error_msg = f"Batch {batch_num} failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
            
            current_row = batch_end + 1
            batch_num += 1
        
        # Log summary
        self._log_summary(results)
        
        # Record metrics
        self.monitor.record_sync_result(results)
        
        # Generate monitoring report
        health_report = self.monitor.generate_health_report()
        self.logger.debug(f"Health report:\n{health_report}")
        
        return results
    
    def _process_batch(self, start_row: int, end_row: int) -> Dict[str, Any]:
        """
        Process a single batch of rows
        
        Args:
            start_row: Starting row
            end_row: Ending row
            
        Returns:
            Batch processing results
        """
        batch_results = {
            'fetched': 0,
            'processed': 0,
            'generated': 0,
            'unchanged': 0,
            'errors': [],
            'student_ids': []
        }
        
        try:
            # Fetch batch from Google Sheets
            students = self.sync_manager.fetch_batch(start_row, end_row)
            batch_results['fetched'] = len(students)
            
            if not students:
                self.logger.warning(f"No students found in rows {start_row}-{end_row}")
                return batch_results
            
            # Validate data if enabled
            if self.validate_data and self.validator:
                self.logger.info("Validating student data...")
                validation_summary, validation_issues = self.validator.validate_batch(students)
                
                if validation_issues:
                    self.logger.warning(
                        f"Found {len(validation_issues)} validation issues "
                        f"in {validation_summary['students_with_issues']} students"
                    )
                    
                    # Add validation errors to batch results
                    for issue in validation_issues[:5]:  # Log first 5 issues
                        batch_results['errors'].append(
                            f"Validation [{issue['severity']}] {issue['student_id']}: {issue['message']}"
                        )
                
                # Log validation summary
                self.logger.info(
                    f"Validation rate: {validation_summary['validation_rate']:.1%} "
                    f"({validation_summary['issues_by_severity']['error']} errors, "
                    f"{validation_summary['issues_by_severity']['warning']} warnings)"
                )
            
            # Process each student
            processed_students = []
            for student_data in students:
                try:
                    student_id = student_data['info']['student_id']
                    student_name = student_data['info']['student_name']
                    
                    self.logger.info(f"Processing {student_id} - {student_name}")
                    
                    # Process the data
                    processed = self.processor.process_student(student_data)
                    processed_students.append(processed)
                    batch_results['processed'] += 1
                    batch_results['student_ids'].append(student_id)
                    
                except Exception as e:
                    error_msg = f"Failed to process student: {str(e)}"
                    self.logger.error(error_msg)
                    batch_results['errors'].append(error_msg)
            
            # Generate reports for processed students
            if processed_students:
                generation_results = self.generator.generate_batch(processed_students)
                batch_results['generated'] = generation_results['generated']
                batch_results['unchanged'] = generation_results.get('unchanged', 0)
                batch_results['errors'].extend(generation_results.get('error_details', []))
            
        except Exception as e:
            error_msg = f"Batch processing failed: {str(e)}"
            self.logger.error(error_msg)
            batch_results['errors'].append(error_msg)
        
        return batch_results
    
    def process_specific_rows(self, row_list: List[int]) -> Dict[str, Any]:
        """
        Process specific rows (not necessarily contiguous)
        
        Args:
            row_list: List of row numbers to process
            
        Returns:
            Summary of processing results
        """
        self.logger.info(f"Processing {len(row_list)} specific rows")
        
        results = {
            'rows': row_list,
            'students_fetched': 0,
            'students_processed': 0,
            'reports_generated': 0,
            'reports_unchanged': 0,
            'errors': [],
            'student_ids': []
        }
        
        # Group consecutive rows into ranges for efficiency
        ranges = self._group_consecutive_rows(row_list)
        
        for start, end in ranges:
            range_results = self.process_range(start, end)
            
            # Aggregate results
            results['students_fetched'] += range_results['students_fetched']
            results['students_processed'] += range_results['students_processed']
            results['reports_generated'] += range_results['reports_generated']
            results['reports_unchanged'] += range_results['reports_unchanged']
            results['errors'].extend(range_results['errors'])
            results['student_ids'].extend(range_results['student_ids'])
        
        return results
    
    def _group_consecutive_rows(self, row_list: List[int]) -> List[Tuple[int, int]]:
        """
        Group consecutive row numbers into ranges
        
        Args:
            row_list: List of row numbers
            
        Returns:
            List of (start, end) tuples
        """
        if not row_list:
            return []
        
        sorted_rows = sorted(set(row_list))
        ranges = []
        
        start = sorted_rows[0]
        end = sorted_rows[0]
        
        for row in sorted_rows[1:]:
            if row == end + 1:
                end = row
            else:
                ranges.append((start, end))
                start = row
                end = row
        
        ranges.append((start, end))
        return ranges
    
    def _log_summary(self, results: Dict[str, Any]) -> None:
        """Log a summary of processing results"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("BATCH PROCESSING SUMMARY")
        self.logger.info("=" * 60)
        
        if 'start_row' in results and 'end_row' in results:
            self.logger.info(f"Row range: {results['start_row']} to {results['end_row']}")
        elif 'rows' in results:
            self.logger.info(f"Specific rows: {len(results['rows'])} rows")
        
        self.logger.info(f"Batches processed: {results.get('batches_processed', 'N/A')}")
        self.logger.info(f"Students fetched: {results['students_fetched']}")
        self.logger.info(f"Students processed: {results['students_processed']}")
        self.logger.info(f"Reports generated: {results['reports_generated']}")
        self.logger.info(f"Reports unchanged: {results['reports_unchanged']}")
        self.logger.info(f"Errors: {len(results['errors'])}")
        
        if results['errors']:
            self.logger.warning("\nErrors encountered:")
            for error in results['errors'][:5]:  # Show first 5 errors
                self.logger.warning(f"  - {error}")
            if len(results['errors']) > 5:
                self.logger.warning(f"  ... and {len(results['errors']) - 5} more errors")
        
        self.logger.info("=" * 60)


def main():
    """Example usage of the batch processor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process student data in batches')
    parser.add_argument('--start', type=int, required=True, help='Starting row (1-indexed)')
    parser.add_argument('--end', type=int, required=True, help='Ending row (inclusive)')
    parser.add_argument('--batch-size', type=int, default=20, help='Batch size (default: 20)')
    parser.add_argument('--rows', type=str, help='Comma-separated list of specific rows')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = BatchProcessor(batch_size=args.batch_size)
    
    # Process based on arguments
    if args.rows:
        # Process specific rows
        row_list = [int(r.strip()) for r in args.rows.split(',')]
        results = processor.process_specific_rows(row_list)
    else:
        # Process range
        results = processor.process_range(args.start, args.end)
    
    # Exit with error code if there were errors
    if results['errors']:
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())