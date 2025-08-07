#!/usr/bin/env python3
"""
Analyze final coverage after applying predictive models
"""

import csv
from collections import Counter
from pathlib import Path

def analyze_final_coverage():
    """Analyze the final enhanced coverage"""
    
    print("📊 FINAL COVERAGE ANALYSIS")
    print("=" * 70)
    
    # Find the latest predictive enhanced file
    files = list(Path("data/vertical_csv").glob("telebort_predictive_enhanced_*.csv"))
    if not files:
        print("No predictive enhanced file found!")
        return
    
    latest_file = sorted(files)[-1]
    print(f"Analyzing: {latest_file.name}\n")
    
    # Load the data
    with open(latest_file, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    total = len(data)
    
    # Count sessions with lesson topics
    has_topic = 0
    for row in data:
        if row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['', '-', '_']:
            has_topic += 1
    
    # Analyze by inference status
    status_counts = Counter()
    method_counts = Counter()
    confidence_levels = {'high': 0, 'medium': 0, 'low': 0}
    
    for row in data:
        status = row.get('Inference_Status', 'Original')
        status_counts[status] += 1
        
        method = row.get('Inference_Method', '')
        if method:
            method_counts[method] += 1
            
            # Categorize confidence
            try:
                conf = float(row.get('Inference_Confidence', 0))
                if conf >= 0.7:
                    confidence_levels['high'] += 1
                elif conf >= 0.5:
                    confidence_levels['medium'] += 1
                elif conf > 0:
                    confidence_levels['low'] += 1
            except:
                pass
    
    # Analyze attendance types
    attendance_counts = Counter()
    for row in data:
        attendance = row.get('Attendance_Normalized', row.get('Attendance', 'Unknown'))
        attendance_counts[attendance] += 1
    
    # Calculate coverage by category
    attended_total = sum(1 for row in data if row.get('Attendance_Normalized') == 'Attended')
    attended_with_topic = sum(1 for row in data 
                             if row.get('Attendance_Normalized') == 'Attended' and
                             row.get('Lesson_Topic_Standard') and 
                             row['Lesson_Topic_Standard'] not in ['', '-', '_'])
    
    # Print results
    print("📈 OVERALL COVERAGE")
    print("-" * 50)
    print(f"Total sessions:                  {total:>6}")
    print(f"Sessions with lesson topics:     {has_topic:>6} ({has_topic/total*100:>5.1f}%)")
    print(f"Sessions without lesson topics:  {total-has_topic:>6} ({(total-has_topic)/total*100:>5.1f}%)")
    
    print("\n📊 COVERAGE BY ATTENDANCE TYPE")
    print("-" * 50)
    for att_type, count in attendance_counts.most_common():
        with_topic = sum(1 for row in data 
                        if row.get('Attendance_Normalized') == att_type and
                        row.get('Lesson_Topic_Standard') and 
                        row['Lesson_Topic_Standard'] not in ['', '-', '_'])
        coverage = (with_topic/count*100) if count > 0 else 0
        print(f"{att_type:<20} {count:>5} sessions, {with_topic:>5} with topics ({coverage:>5.1f}%)")
    
    print("\n🎯 ATTENDED SESSION COVERAGE")
    print("-" * 50)
    print(f"Total attended sessions:         {attended_total:>6}")
    print(f"Attended with lesson topics:     {attended_with_topic:>6} ({attended_with_topic/attended_total*100 if attended_total > 0 else 0:>5.1f}%)")
    print(f"Attended without topics:         {attended_total-attended_with_topic:>6} ({(attended_total-attended_with_topic)/attended_total*100 if attended_total > 0 else 0:>5.1f}%)")
    
    print("\n🔧 INFERENCE METHODS BREAKDOWN")
    print("-" * 50)
    for status, count in status_counts.most_common():
        pct = count/total*100
        print(f"{status:<25} {count:>6} ({pct:>5.1f}%)")
    
    if method_counts:
        print("\n📊 PREDICTION METHODS USED")
        print("-" * 50)
        for method, count in method_counts.most_common():
            pct = count/total*100
            print(f"{method:<25} {count:>6} ({pct:>5.1f}%)")
    
    if any(confidence_levels.values()):
        print("\n🎯 CONFIDENCE LEVELS")
        print("-" * 50)
        print(f"High confidence (≥0.7):   {confidence_levels['high']:>6}")
        print(f"Medium confidence (0.5-0.7): {confidence_levels['medium']:>6}")
        print(f"Low confidence (<0.5):    {confidence_levels['low']:>6}")
    
    # Calculate improvement stages
    print("\n📈 COVERAGE IMPROVEMENT JOURNEY")
    print("-" * 50)
    
    original = sum(1 for row in data 
                  if row.get('Inference_Status') in [None, '', 'Unknown'] and
                  row.get('Lesson_Topic_Standard') and 
                  row['Lesson_Topic_Standard'] not in ['', '-', '_'])
    
    enhanced_direct = sum(1 for row in data 
                         if row.get('Inference_Status') == 'Enhanced_Direct')
    
    enhanced_inferred = sum(1 for row in data 
                           if row.get('Inference_Status') == 'Enhanced_Inferred')
    
    enhanced_max = sum(1 for row in data 
                      if row.get('Inference_Status') == 'Enhanced_MaxCoverage')
    
    predictive = sum(1 for row in data 
                    if row.get('Inference_Status') == 'Predictive_Model')
    
    stage1 = original
    stage2 = stage1 + enhanced_direct
    stage3 = stage2 + enhanced_inferred
    stage4 = stage3 + enhanced_max
    stage5 = stage4 + predictive
    
    print(f"1. Initial data:          {stage1:>6} ({stage1/total*100:>5.1f}%)")
    if enhanced_direct > 0:
        print(f"2. + Direct matching:     {stage2:>6} ({stage2/total*100:>5.1f}%) [+{enhanced_direct}]")
    if enhanced_inferred > 0:
        print(f"3. + Basic inference:     {stage3:>6} ({stage3/total*100:>5.1f}%) [+{enhanced_inferred}]")
    if enhanced_max > 0:
        print(f"4. + Max coverage:        {stage4:>6} ({stage4/total*100:>5.1f}%) [+{enhanced_max}]")
    if predictive > 0:
        print(f"5. + Predictive models:   {stage5:>6} ({stage5/total*100:>5.1f}%) [+{predictive}]")
    
    print(f"\n🎯 FINAL COVERAGE:        {has_topic:>6} ({has_topic/total*100:>5.1f}%)")
    print(f"   Total improvement:     {has_topic-stage1:>6} ({(has_topic-stage1)/stage1*100 if stage1 > 0 else 0:>5.1f}% increase)")
    
    # Identify remaining gaps
    remaining_gaps = []
    for row in data:
        if (not row.get('Lesson_Topic_Standard') or 
            row['Lesson_Topic_Standard'] in ['', '-', '_']):
            attendance = row.get('Attendance_Normalized', row.get('Attendance', ''))
            if attendance == 'Attended':
                remaining_gaps.append(row)
    
    if remaining_gaps:
        print(f"\n⚠️  REMAINING GAPS")
        print("-" * 50)
        print(f"Attended sessions still missing topics: {len(remaining_gaps)}")
        
        # Sample gaps
        print("\nSample remaining gaps:")
        for gap in remaining_gaps[:5]:
            print(f"  {gap['Student_Name']} - {gap['Session_Date']} - Session #{gap.get('Session_Number', 'N/A')}")
    
    # Success metrics
    print("\n✨ SUCCESS METRICS")
    print("=" * 70)
    
    improvement_factor = has_topic / stage1 if stage1 > 0 else 0
    print(f"📈 Coverage improved by {improvement_factor:.1f}x")
    print(f"🎯 Reached {has_topic/total*100:.1f}% total coverage")
    print(f"📊 Enhanced {has_topic - stage1} sessions automatically")
    
    # Theoretical maximum
    legitimate_gaps = total - attended_total
    theoretical_max = attended_total
    current_attended_coverage = attended_with_topic
    
    print(f"\n📐 THEORETICAL LIMITS")
    print("-" * 50)
    print(f"Legitimate gaps (absences/holidays): {legitimate_gaps} ({legitimate_gaps/total*100:.1f}%)")
    print(f"Theoretical maximum coverage: {theoretical_max} ({theoretical_max/total*100:.1f}%)")
    print(f"Current attended coverage: {current_attended_coverage} ({current_attended_coverage/theoretical_max*100 if theoretical_max > 0 else 0:.1f}% of maximum)")
    print(f"Room for improvement: {theoretical_max - current_attended_coverage} sessions")

if __name__ == "__main__":
    analyze_final_coverage()