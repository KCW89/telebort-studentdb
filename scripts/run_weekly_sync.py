#!/usr/bin/env python3
"""
run_weekly_sync.py - Main orchestrator for weekly student report sync

This script coordinates the complete weekly sync process:
1. Fetches data from Google Sheets
2. Processes the data
3. Generates/updates reports
4. Commits changes to git
"""

import os
import sys
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_sheets_mcp import SheetsSyncManager
from process_data import DataProcessor
from generate_reports import ReportGenerator
from monitoring import SyncMonitor


class WeeklySyncOrchestrator:
    """Orchestrates the complete weekly sync process"""
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.sync_manager = SheetsSyncManager()
        self.processor = DataProcessor()
        self.generator = ReportGenerator()
        self.monitor = SyncMonitor()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('WeeklySyncOrchestrator')
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
    
    def run_sync(self) -> Dict[str, Any]:
        """
        Run the complete weekly sync process
        
        Returns:
            Summary of sync results
        """
        start_time = datetime.now()
        week_number = start_time.isocalendar()[1]
        year = start_time.year
        
        self.logger.info(f"Starting weekly sync for Week {week_number}/{year}")
        
        results = {
            'start_time': start_time.isoformat(),
            'week': week_number,
            'year': year,
            'students_fetched': 0,
            'students_processed': 0,
            'reports_generated': 0,
            'errors': [],
            'git_commit': None
        }
        
        try:
            # Step 1: Fetch data from Google Sheets
            self.logger.info("Step 1: Fetching data from Google Sheets")
            raw_students = self.sync_manager.fetch_all_students()
            results['students_fetched'] = len(raw_students)
            self.logger.info(f"Fetched {len(raw_students)} student records")
            
            if not raw_students:
                self.logger.warning("No student data fetched, ending sync")
                return results
            
            # Save raw data for debugging
            self.sync_manager.save_raw_data(raw_students)
            
            # Step 2: Process student data
            self.logger.info("Step 2: Processing student data")
            processed_students = self.processor.process_batch(raw_students)
            results['students_processed'] = len(processed_students)
            self.logger.info(f"Processed {len(processed_students)} students")
            
            # Step 3: Generate reports
            self.logger.info("Step 3: Generating reports")
            generation_results = self.generator.generate_batch(processed_students)
            results['reports_generated'] = generation_results['generated']
            results['errors'].extend(generation_results['error_details'])
            
            # Step 4: Commit to git
            if generation_results['generated'] > 0:
                self.logger.info("Step 4: Committing changes to git")
                commit_result = self._commit_to_git(week_number, year, generation_results['generated'])
                results['git_commit'] = commit_result
            else:
                self.logger.info("No reports updated, skipping git commit")
            
        except Exception as e:
            error_msg = f"Fatal error during sync: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        results['duration_seconds'] = duration
        results['end_time'] = end_time.isoformat()
        
        # Log summary
        self._log_summary(results)
        
        # Record metrics in monitoring system
        self.monitor.record_sync_result(results)
        
        # Check data quality
        if raw_students:
            quality_issues = self.monitor.check_data_quality(raw_students)
            if quality_issues:
                self.logger.warning(f"Found {len(quality_issues)} data quality issues")
        
        return results
    
    def _commit_to_git(self, week: int, year: int, count: int) -> Dict[str, Any]:
        """
        Commit report changes to git
        
        Args:
            week: Week number
            year: Year
            count: Number of reports updated
            
        Returns:
            Git operation results
        """
        try:
            # Add all report files
            subprocess.run(['git', 'add', 'reports/*.md'], 
                         check=True, capture_output=True, text=True)
            
            # Create commit message
            commit_message = f"Weekly sync: Week {week}/{year} - {count} students updated"
            
            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"Git commit successful: {commit_message}")
                
                # Get commit hash
                commit_hash = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    capture_output=True, text=True
                ).stdout.strip()
                
                return {
                    'success': True,
                    'message': commit_message,
                    'hash': commit_hash
                }
            else:
                # Check if no changes to commit
                if "nothing to commit" in result.stdout:
                    self.logger.info("No changes to commit")
                    return {
                        'success': True,
                        'message': 'No changes to commit',
                        'hash': None
                    }
                else:
                    self.logger.error(f"Git commit failed: {result.stderr}")
                    return {
                        'success': False,
                        'error': result.stderr
                    }
                    
        except Exception as e:
            self.logger.error(f"Git operation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _log_summary(self, results: Dict[str, Any]) -> None:
        """
        Log a summary of sync results
        
        Args:
            results: Sync results dictionary
        """
        self.logger.info("=" * 60)
        self.logger.info("SYNC SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Week: {results['week']}/{results['year']}")
        self.logger.info(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
        self.logger.info(f"Students fetched: {results['students_fetched']}")
        self.logger.info(f"Students processed: {results['students_processed']}")
        self.logger.info(f"Reports generated: {results['reports_generated']}")
        self.logger.info(f"Errors: {len(results['errors'])}")
        
        if results['errors']:
            self.logger.warning("Errors encountered:")
            for error in results['errors']:
                self.logger.warning(f"  - {error}")
        
        if results.get('git_commit', {}).get('success'):
            self.logger.info(f"Git commit: {results['git_commit'].get('message', 'N/A')}")
        
        self.logger.info("=" * 60)


def main():
    """Main function"""
    orchestrator = WeeklySyncOrchestrator()
    
    # Run the sync
    results = orchestrator.run_sync()
    
    # Exit with error code if there were errors
    if results['errors']:
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())