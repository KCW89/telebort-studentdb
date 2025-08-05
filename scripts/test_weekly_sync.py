#!/usr/bin/env python3
"""
test_weekly_sync.py - Test the weekly sync process with a small batch
"""

import os
import sys
import logging
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_sheets_mcp import SheetsSyncManager
from process_data import DataProcessor
from generate_reports import ReportGenerator


def test_sync_small_batch():
    """Test the sync process with a small batch"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('TestWeeklySync')
    
    try:
        # Initialize components
        logger.info("Initializing sync components...")
        sync_manager = SheetsSyncManager()
        processor = DataProcessor()
        generator = ReportGenerator()
        
        # Test with a small batch (rows 5-7)
        logger.info("Testing with rows 5-7...")
        students = sync_manager.fetch_batch(start_row=5, end_row=7)
        
        if not students:
            logger.warning("No students fetched from test batch")
            return
        
        logger.info(f"Fetched {len(students)} students from test batch")
        
        # Process the students
        logger.info("Processing student data...")
        processed = processor.process_batch(students)
        logger.info(f"Processed {len(processed)} students")
        
        # Generate reports
        logger.info("Generating reports...")
        results = generator.generate_batch(processed)
        
        # Log results
        logger.info("=" * 60)
        logger.info("TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"Students fetched: {len(students)}")
        logger.info(f"Students processed: {len(processed)}")
        logger.info(f"Reports generated: {results['generated']}")
        logger.info(f"Reports unchanged: {results.get('unchanged', 0)}")
        logger.info(f"Reports with errors: {results.get('errors', 0)}")
        
        if results.get('errors', 0) > 0 or results.get('error_details', []):
            logger.warning("Failed reports:")
            for error in results.get('error_details', []):
                logger.warning(f"  - {error}")
        
        # List generated reports
        if results['generated'] > 0:
            logger.info("\nGenerated reports:")
            # Check the reports directory
            reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
            for filename in os.listdir(reports_dir):
                if filename.endswith('.md') and filename.startswith('s10'):
                    # Check if this was one of our test students
                    student_id = filename.replace('.md', '')
                    if student_id in ['s10769', 's10777', 's10711']:
                        logger.info(f"  - {filename}")
        
        logger.info("\nTest completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(test_sync_small_batch())