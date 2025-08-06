#!/usr/bin/env python3
"""
Copy batch8 generated reports to appropriate teacher directories
"""

import os
import shutil
from typing import Dict

def get_teacher_mapping() -> Dict[str, str]:
    """Map student IDs to their primary teachers from batch8"""
    # Based on the processing results, map students to their primary teachers
    return {
        's10789': 'Arrvinna',    # Lee Hiu Ching
        's10333': 'Yasmin',      # Teh Yong Zheng  
        's10369': 'Yasmin',      # Audrey Phuah Jia Yan
        's10481': 'Yasmin',      # Elly Goh Man Ying
        's10334': 'Yasmin',      # Ryan Kong Juin Yue
        's10240': 'Yasmin',      # Tay Zi Xun
    }

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, "scripts", "reports")
    
    teacher_mapping = get_teacher_mapping()
    
    print("Copying batch8 reports to teacher directories...")
    
    for student_id, teacher in teacher_mapping.items():
        # Source report file
        source_file = os.path.join(reports_dir, f"{student_id}.md")
        
        if not os.path.exists(source_file):
            print(f"Warning: Report file not found for {student_id}")
            continue
        
        # Teacher directory
        teacher_dir = os.path.join(base_dir, f"Teacher {teacher}")
        
        # Create teacher directory if it doesn't exist
        os.makedirs(teacher_dir, exist_ok=True)
        
        # Destination file
        dest_file = os.path.join(teacher_dir, f"{student_id}.md")
        
        try:
            # Copy the report
            shutil.copy2(source_file, dest_file)
            print(f"✓ Copied {student_id}.md to Teacher {teacher}/")
        except Exception as e:
            print(f"✗ Error copying {student_id}.md: {e}")
    
    print("\nBatch8 reports copied to teacher directories!")

if __name__ == "__main__":
    main()