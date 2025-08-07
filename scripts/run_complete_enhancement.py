#!/usr/bin/env python3
"""
Complete Enhancement Pipeline
Run all enhancement stages to achieve maximum coverage
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_stage(stage_num, script_name, description):
    """Run a single enhancement stage"""
    print(f"\n{'='*70}")
    print(f"Stage {stage_num}: {description}")
    print(f"{'='*70}")
    
    script_path = Path("scripts") / script_name
    
    if not script_path.exists():
        print(f"⚠️  Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Extract key metrics from output
            output_lines = result.stdout.split('\n')
            for line in output_lines[-20:]:  # Check last 20 lines for results
                if 'coverage' in line.lower() or 'enhanced' in line.lower() or '%' in line:
                    print(f"  ✓ {line.strip()}")
            return True
        else:
            print(f"  ❌ Error: {result.stderr[:200]}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Stage timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"  ❌ Error running stage: {e}")
        return False

def main():
    """Run the complete enhancement pipeline"""
    print("🚀 COMPLETE ENHANCEMENT PIPELINE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    stages = [
        (1, "batches_to_vertical_csv.py", "Convert Horizontal to Vertical Format"),
        (2, "enhance_with_master_index.py", "Direct Matching with Master Index"),
        (3, "enhance_with_inference.py", "Basic Inference Rules"),
        (4, "maximize_coverage.py", "Maximum Coverage Algorithm"),
        (5, "apply_predictive_models.py", "Predictive Modeling"),
        (6, "advanced_ml_models.py", "Advanced Machine Learning"),
        (7, "analyze_final_coverage.py", "Final Coverage Analysis")
    ]
    
    successful_stages = []
    failed_stages = []
    
    for stage_num, script, description in stages:
        success = run_stage(stage_num, script, description)
        
        if success:
            successful_stages.append(stage_num)
        else:
            failed_stages.append(stage_num)
            
            # Ask whether to continue
            response = input(f"\n⚠️  Stage {stage_num} failed. Continue? (y/n): ")
            if response.lower() != 'y':
                break
    
    # Final summary
    print(f"\n{'='*70}")
    print("📊 PIPELINE SUMMARY")
    print(f"{'='*70}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Successful stages: {successful_stages}")
    
    if failed_stages:
        print(f"Failed stages: {failed_stages}")
    
    # Check final results
    latest_files = list(Path("data/vertical_csv").glob("telebort_ml_enhanced_*.csv"))
    if latest_files:
        latest = sorted(latest_files)[-1]
        print(f"\n✅ Final output: {latest}")
        
        # Try to get final metrics
        try:
            import csv
            with open(latest, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
                
            total = len(data)
            has_topic = sum(1 for row in data 
                          if row.get('Lesson_Topic_Standard') and 
                          row['Lesson_Topic_Standard'] not in ['', '-', '_'])
            
            attended = sum(1 for row in data if row.get('Attendance_Normalized') == 'Attended')
            attended_with_topic = sum(1 for row in data 
                                    if row.get('Attendance_Normalized') == 'Attended' and
                                    row.get('Lesson_Topic_Standard') and 
                                    row['Lesson_Topic_Standard'] not in ['', '-', '_'])
            
            print(f"\n🎯 FINAL METRICS:")
            print(f"  Total coverage: {has_topic}/{total} ({has_topic/total*100:.1f}%)")
            print(f"  Attended coverage: {attended_with_topic}/{attended} ({attended_with_topic/attended*100:.1f}%)")
            
            # Calculate improvement
            initial_coverage = 0.106  # 10.6% initial
            final_coverage = has_topic/total
            improvement = final_coverage / initial_coverage
            
            print(f"  Improvement factor: {improvement:.1f}x")
            
        except Exception as e:
            print(f"Could not calculate final metrics: {e}")
    
    print(f"\n{'='*70}")
    print("✨ Pipeline complete!")
    
    # Provide next steps
    print("\n📋 Next Steps:")
    print("1. Review the final enhanced file in data/vertical_csv/")
    print("2. Import to Google Sheets for visualization")
    print("3. Send teacher feedback forms from data/teacher_feedback/")
    print("4. Consider deep learning for remaining 5.3% gaps")

if __name__ == "__main__":
    main()