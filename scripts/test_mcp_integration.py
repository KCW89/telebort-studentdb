#!/usr/bin/env python3
"""
test_mcp_integration.py - Test MCP integration in Claude Code environment
"""

import os
import sys
import logging

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_sheets_mcp import SheetsSyncManager


def test_mcp_integration():
    """Test that MCP integration works in Claude Code environment"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('TestMCPIntegration')
    
    try:
        # Initialize sync manager
        logger.info("Initializing SheetsSyncManager...")
        sync_manager = SheetsSyncManager()
        
        # Test fetching a small batch
        logger.info("Testing MCP fetch for rows 5-7...")
        result = sync_manager.fetch_with_mcp(first_row=5, row_count=3)
        
        # Check if we got data
        if result and 'results' in result and len(result['results']) > 0:
            rows = result['results'][0].get('rows', [])
            logger.info(f"Successfully fetched {len(rows)} rows from Google Sheets")
            
            # Display student IDs found
            logger.info("Student IDs found:")
            for row in rows:
                if len(row) > 2:
                    student_id = row[2]  # Student ID is in column C (index 2)
                    student_name = row[0]  # Student name is in column A (index 0)
                    logger.info(f"  - {student_id}: {student_name}")
            
            logger.info("\nMCP integration test PASSED!")
            return 0
        else:
            logger.error("No data received from MCP call")
            return 1
            
    except Exception as e:
        logger.error(f"MCP integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(test_mcp_integration())