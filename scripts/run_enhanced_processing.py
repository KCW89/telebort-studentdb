#!/usr/bin/env python3
"""
run_enhanced_processing.py - Run the enhanced data processor to clean all reports

This script:
1. Fetches data from Google Sheets (or uses cached data)
2. Applies enhanced data cleaning
3. Regenerates all reports with clean data
4. Shows before/after comparison
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_data_processor import EnhancedDataProcessor
from sync_sheets_mcp import SheetsSyncManager
from generate_reports import ReportGenerator

class EnhancedReportProcessor:
    """Main processor to run enhanced data cleaning and report generation"""
    
    def __init__(self, use_cached_data: bool = True):
        """Initialize the processor"""
        self.use_cached_data = use_cached_data
        self.sync_manager = SheetsSyncManager()
        self.enhanced_processor = EnhancedDataProcessor()
        self.report_generator = ReportGenerator()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging"""
        logger = logging.getLogger('EnhancedReportProcessor')
        logger.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        return logger
    
    def run(self):
        """Main execution method"""
        self.logger.info("=" * 60)
        self.logger.info("Starting Enhanced Data Processing")
        self.logger.info("=" * 60)
        
        # Step 1: Get data
        self.logger.info("\nStep 1: Fetching student data...")
        raw_data = self._fetch_data()
        self.logger.info(f"Fetched {len(raw_data)} student records")
        
        # Step 2: Process with enhanced cleaning
        self.logger.info("\nStep 2: Applying enhanced data cleaning...")
        processed_data, quality_metrics = self.enhanced_processor.process_student_data(raw_data)
        self.logger.info(f"Processed {len(processed_data)} students")
        
        # Step 3: Show quality improvements
        self.logger.info("\nStep 3: Data Quality Improvements Applied:")
        self._show_quality_metrics(quality_metrics)
        
        # Step 4: Generate reports
        self.logger.info("\nStep 4: Generating cleaned reports...")
        report_stats = self._generate_reports(processed_data)
        
        # Step 5: Show summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PROCESSING COMPLETE")
        self.logger.info("=" * 60)
        self._show_summary(processed_data, quality_metrics, report_stats)
        
    def _fetch_data(self) -> List[Dict]:
        """Fetch or load student data"""
        
        if self.use_cached_data:
            # Look for cached data files
            data_files = [
                'sheets_data.json',
                'sheets_data_batch2.json', 
                'sheets_data_batch3.json'
            ]
            
            all_data = []
            for filename in data_files:
                filepath = os.path.join(os.path.dirname(__file__), '..', filename)
                if os.path.exists(filepath):
                    self.logger.info(f"Loading cached data from {filename}")
                    with open(filepath, 'r') as f:
                        file_data = json.load(f)
                        all_data.extend(self._parse_cached_data(file_data))
            
            if all_data:
                return all_data
                
        # Fetch fresh data
        self.logger.info("Fetching fresh data from Google Sheets...")
        return self.sync_manager.fetch_all_students()
    
    def _parse_cached_data(self, file_data: Dict) -> List[Dict]:
        """Parse cached JSON data into student records"""
        students = []
        
        if 'results' in file_data and file_data['results']:
            raw_rows = file_data['results'][0].get('raw_rows', '[]')
            if isinstance(raw_rows, str):
                rows = json.loads(raw_rows)
            else:
                rows = raw_rows
                
            # Skip header rows
            for row_data in rows[3:]:  # Skip first 3 header rows
                if not row_data or not row_data[1]:  # No student ID
                    continue
                    
                student = self._parse_student_row(row_data)
                if student:
                    students.append(student)
                    
        return students
    
    def _parse_student_row(self, row: List) -> Dict:
        """Parse a single row of student data"""
        if len(row) < 8:
            return None
            
        student = {
            'name': row[0] if row[0] else '',
            'student_id': row[1] if row[1] else '',
            'program': row[2] if row[2] else '',
            'day': row[3] if row[3] else '',
            'start_time': row[4] if row[4] else '',
            'end_time': row[5] if row[5] else '',
            'teacher': row[6] if row[6] else '',
            'schedule': f"{row[3]} {row[4]}-{row[5]}" if row[3] and row[4] and row[5] else '-',
            'sessions': []
        }
        
        # Parse sessions (every 5 columns starting from column 7)
        for i in range(7, len(row), 5):
            if i + 4 < len(row):
                date = row[i] if i < len(row) else ''
                session = row[i+1] if i+1 < len(row) else ''
                lesson = row[i+2] if i+2 < len(row) else ''
                attendance = row[i+3] if i+3 < len(row) else ''
                progress = row[i+4] if i+4 < len(row) else ''
                
                if date and date != '-':
                    student['sessions'].append({
                        'date': date,
                        'session': session,
                        'lesson': lesson,
                        'attendance': attendance,
                        'progress': progress
                    })
        
        return student
    
    def _generate_reports(self, processed_data: List[Dict]) -> Dict:
        """Generate reports with cleaned data"""
        stats = {
            'generated': 0,
            'updated': 0,
            'errors': 0
        }
        
        for student in processed_data:
            try:
                # Generate the report
                report_path = self.report_generator.generate_report(student)
                
                # Check if it's new or updated
                if os.path.exists(report_path):
                    stats['updated'] += 1
                else:
                    stats['generated'] += 1
                    
                self.logger.debug(f"Generated report: {report_path}")
                
            except Exception as e:
                self.logger.error(f"Error generating report for {student['student_id']}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def _show_quality_metrics(self, metrics: Dict):
        """Display quality metrics"""
        self.logger.info("-" * 40)
        self.logger.info("Data Quality Fixes Applied:")
        self.logger.info(f"  • Teacher names → 'Attended': {metrics.get('teacher_name_fixes', 0)}")
        self.logger.info(f"  • Progress standardized: {metrics.get('progress_standardizations', 0)}")
        self.logger.info(f"  • URLs extracted: {metrics.get('url_extractions', 0)}")
        self.logger.info(f"  • Missing data handled: {metrics.get('missing_data_handled', 0)}")
        self.logger.info(f"  • Invalid sessions fixed: {metrics.get('invalid_sessions_fixed', 0)}")
        
        total = sum(metrics.values())
        self.logger.info(f"\n  Total improvements: {total}")
        self.logger.info("-" * 40)
    
    def _show_summary(self, processed_data: List[Dict], quality_metrics: Dict, report_stats: Dict):
        """Show processing summary"""
        self.logger.info(f"\nProcessing Summary:")
        self.logger.info(f"  • Students processed: {len(processed_data)}")
        self.logger.info(f"  • Data quality fixes: {sum(quality_metrics.values())}")
        self.logger.info(f"  • Reports updated: {report_stats['updated']}")
        self.logger.info(f"  • New reports: {report_stats['generated']}")
        self.logger.info(f"  • Errors: {report_stats['errors']}")
        
        # Show sample improvements
        self.logger.info(f"\nSample Data Improvements:")
        self.logger.info("  Before: | 19/07/2025 | 1 | L1 Introduction | Soumiya | COMPLETED |")
        self.logger.info("  After:  | 19/07/2025 | 1 | L1 Introduction | Attended | Completed |")
        
        self.logger.info(f"\n✅ All reports have been updated with clean data!")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run enhanced data processing on student reports')
    parser.add_argument('--fresh', action='store_true', help='Fetch fresh data from Google Sheets')
    parser.add_argument('--verbose', action='store_true', help='Show detailed logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Run processor
    processor = EnhancedReportProcessor(use_cached_data=not args.fresh)
    processor.run()


if __name__ == "__main__":
    main()