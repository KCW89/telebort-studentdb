#!/usr/bin/env python3
"""
test_batch_processor.py - Test the unified batch processor
"""

import os
import sys
import logging

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from batch_processor import BatchProcessor


def test_batch_processor():
    """Test various batch processing scenarios"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('TestBatchProcessor')
    
    logger.info("=" * 60)
    logger.info("TESTING BATCH PROCESSOR")
    logger.info("=" * 60)
    
    # Test 1: Small batch processing
    logger.info("\nTest 1: Small Batch (rows 5-7)")
    processor = BatchProcessor(batch_size=5)
    results = processor.process_range(5, 7)
    
    logger.info(f"Results: {results['students_processed']} students processed")
    
    # Test 2: Specific rows
    logger.info("\nTest 2: Specific Rows")
    results = processor.process_specific_rows([5, 7, 10, 11, 15])
    
    logger.info(f"Results: {results['students_processed']} students processed")
    
    # Test 3: Row grouping
    logger.info("\nTest 3: Row Grouping")
    test_rows = [1, 2, 3, 5, 7, 8, 9, 15, 20, 21]
    ranges = processor._group_consecutive_rows(test_rows)
    logger.info(f"Grouped {test_rows} into ranges: {ranges}")
    
    # Test 4: Large batch size
    logger.info("\nTest 4: Large Batch Size")
    large_processor = BatchProcessor(batch_size=100)  # Should be capped at MAX_BATCH_SIZE
    logger.info(f"Batch size capped at: {large_processor.batch_size}")
    
    logger.info("\n" + "=" * 60)
    logger.info("BATCH PROCESSOR TEST COMPLETE")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(test_batch_processor())