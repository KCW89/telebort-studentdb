#!/usr/bin/env python3
"""
Process all batch files to generate complete student reports
"""
import json
import logging
import sys
from pathlib import Path
from process_complete_data import process_batch_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Process all batch files"""
    base_dir = Path("/Users/chongwei/Telebort Engineering/telebort-studentdb")
    
    # List of all batches to process
    batches_to_process = [
        "batch2_complete.json",
        "batch5_complete.json", 
        "batch6_complete.json",
        "batch7_complete.json",
        "batch8_complete.json",
        "batch9_complete.json",
        "batch10_complete.json",
        "batch11_complete.json",
        "batch12_complete.json",
        "batch13_complete.json",
        "batch14_complete.json",
        "batch15_complete.json",
        "batch16_complete.json",
        "batch17_complete.json",
        "batch18_complete.json"
    ]
    
    print("=" * 70)
    print("PROCESSING ALL REMAINING BATCHES")
    print("=" * 70)
    
    total_students = 0
    total_sessions = 0
    total_reports = 0
    failed_batches = []
    
    for batch_file in batches_to_process:
        batch_path = base_dir / batch_file
        
        if not batch_path.exists():
            logging.warning(f"Batch file not found: {batch_file}")
            failed_batches.append(batch_file)
            continue
            
        print(f"\n📁 Processing {batch_file}...")
        
        try:
            # Process the batch
            result = process_batch_file(str(batch_path))
            
            if result:
                students = result.get('students_processed', 0)
                sessions = result.get('total_sessions', 0)
                reports = result.get('reports_generated', 0)
                
                total_students += students
                total_sessions += sessions
                total_reports += reports
                
                print(f"   ✅ Processed {students} students with {sessions} sessions")
                print(f"   📄 Generated {reports} reports")
            else:
                failed_batches.append(batch_file)
                
        except Exception as e:
            logging.error(f"Error processing {batch_file}: {e}")
            failed_batches.append(batch_file)
    
    # Print summary
    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   • Total students processed: {total_students}")
    print(f"   • Total sessions: {total_sessions}")
    print(f"   • Total reports generated: {total_reports}")
    print(f"   • Average sessions per student: {total_sessions/total_students:.1f}" if total_students > 0 else "")
    
    if failed_batches:
        print(f"\n⚠️  Failed batches: {', '.join(failed_batches)}")
    else:
        print(f"\n✅ All batches processed successfully!")
    
    return 0 if not failed_batches else 1

if __name__ == "__main__":
    sys.exit(main())