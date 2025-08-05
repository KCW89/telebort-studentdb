#!/usr/bin/env python3
"""
migrate_to_batch_processor.py - Migration guide and tool for consolidating batch scripts

This script helps migrate from individual batch scripts to the unified batch processor.
"""

import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from batch_processor import BatchProcessor


# Mapping of old batch scripts to their row ranges
BATCH_MIGRATIONS = {
    'process_batch.py': {
        'description': 'Original batch processor (flexible)',
        'usage': 'BatchProcessor().process_range(start_row, end_row)'
    },
    'process_batch2.py': {
        'description': 'Batch 2: rows 25-44',
        'rows': (25, 44),
        'migration': 'BatchProcessor().process_range(25, 44)'
    },
    'process_batch3.py': {
        'description': 'Batch 3: rows 45-64',
        'rows': (45, 64),
        'migration': 'BatchProcessor().process_range(45, 64)'
    },
    'process_batch4.py': {
        'description': 'Batch 4: rows 65-84',
        'rows': (65, 84),
        'migration': 'BatchProcessor().process_range(65, 84)'
    },
    'process_batch5.py': {
        'description': 'Batch 5: rows 85-104',
        'rows': (85, 104),
        'migration': 'BatchProcessor().process_range(85, 104)'
    },
    'process_batch6.py': {
        'description': 'Batch 6: rows 105-111',
        'rows': (105, 111),
        'migration': 'BatchProcessor().process_range(105, 111)'
    },
    'process_batch7.py': {
        'description': 'Batch 7: rows 10-24',
        'rows': (10, 24),
        'migration': 'BatchProcessor().process_range(10, 24)'
    },
    'process_batch8.py': {
        'description': 'Batch 8: specific rows [6, 8]',
        'specific_rows': [6, 8],
        'migration': 'BatchProcessor().process_specific_rows([6, 8])'
    }
}


def print_migration_guide():
    """Print migration guide for all batch scripts"""
    print("=" * 60)
    print("BATCH PROCESSOR MIGRATION GUIDE")
    print("=" * 60)
    print("\nThe unified batch_processor.py replaces all individual batch scripts.")
    print("\nMigration examples:\n")
    
    for script, info in BATCH_MIGRATIONS.items():
        print(f"{script}:")
        print(f"  Description: {info['description']}")
        if 'migration' in info:
            print(f"  Migration:   {info['migration']}")
        print()
    
    print("Command-line usage:")
    print("  python batch_processor.py --start 5 --end 111")
    print("  python batch_processor.py --start 25 --end 44 --batch-size 10")
    print("  python batch_processor.py --rows 5,7,10,15")
    print("\nProgrammatic usage:")
    print("  from batch_processor import BatchProcessor")
    print("  processor = BatchProcessor(batch_size=20)")
    print("  results = processor.process_range(5, 111)")
    print("\n" + "=" * 60)


def demonstrate_migration(batch_name: str):
    """Demonstrate migration for a specific batch"""
    if batch_name not in BATCH_MIGRATIONS:
        print(f"Unknown batch: {batch_name}")
        return
    
    info = BATCH_MIGRATIONS[batch_name]
    print(f"\nMigrating {batch_name}:")
    print(f"Description: {info['description']}")
    
    processor = BatchProcessor()
    
    if 'rows' in info:
        start, end = info['rows']
        print(f"Processing rows {start} to {end}...")
        results = processor.process_range(start, end)
    elif 'specific_rows' in info:
        rows = info['specific_rows']
        print(f"Processing specific rows {rows}...")
        results = processor.process_specific_rows(rows)
    else:
        print("This script requires manual migration")
        return
    
    print(f"\nResults:")
    print(f"  Students processed: {results['students_processed']}")
    print(f"  Reports generated: {results['reports_generated']}")
    print(f"  Errors: {len(results['errors'])}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migration tool for batch processing scripts'
    )
    parser.add_argument(
        '--demonstrate',
        choices=list(BATCH_MIGRATIONS.keys()),
        help='Demonstrate migration for a specific batch script'
    )
    parser.add_argument(
        '--process-all',
        action='store_true',
        help='Process all students (rows 5-111)'
    )
    
    args = parser.parse_args()
    
    if args.demonstrate:
        demonstrate_migration(args.demonstrate)
    elif args.process_all:
        print("Processing all students (rows 5-111)...")
        processor = BatchProcessor()
        results = processor.process_range(5, 111)
        print(f"\nCompleted: {results['students_processed']} students processed")
    else:
        print_migration_guide()
    
    return 0


if __name__ == "__main__":
    exit(main())