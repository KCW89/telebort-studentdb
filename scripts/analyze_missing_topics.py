#!/usr/bin/env python3
"""Analyze why sessions are missing lesson topics"""

import csv
from collections import Counter, defaultdict

# Read the enhanced file
with open('data/vertical_csv/telebort_sessions_final_20250806_233834.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = list(reader)

print('🔍 ANALYSIS: Why 63.2% Sessions Still Missing Lesson Topics')
print('=' * 70)

# Categorize missing topics
missing_categories = defaultdict(list)

for row in data:
    has_topic = row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['-', '', '_']
    
    if not has_topic:
        attendance = row.get('Attendance_Normalized', row.get('Attendance', ''))
        program = row.get('Program', '')
        course_code = row.get('Course_Code', '')
        
        # Categorize the reason
        if attendance in ['No Class', 'Public Holiday', 'Teacher Parent Day', 'In Break', 'Off']:
            missing_categories['legitimate_no_class'].append(row)
        elif attendance == 'Absent':
            missing_categories['student_absent'].append(row)
        elif attendance == 'Not Marked':
            missing_categories['attendance_not_marked'].append(row)
        elif not course_code:
            missing_categories['no_course_mapping'].append(row)
        elif attendance == 'Attended':
            missing_categories['attended_but_no_topic'].append(row)
        else:
            missing_categories['other'].append(row)

# Print analysis
total_missing = sum(len(v) for v in missing_categories.values())
print(f'Total sessions missing topics: {total_missing}')
print()

print('📊 Breakdown of Missing Topics:')
print('-' * 70)
for category, sessions in sorted(missing_categories.items(), key=lambda x: len(x[1]), reverse=True):
    count = len(sessions)
    pct = count / total_missing * 100 if total_missing > 0 else 0
    print(f'{category:<30} {count:>5} ({pct:>5.1f}%)')

# Analyze which programs have poor coverage
print('\n📊 Missing Topics by Program:')
print('-' * 70)

program_stats = defaultdict(lambda: {'total': 0, 'missing': 0})
for row in data:
    program = row.get('Program', 'Unknown')
    program_stats[program]['total'] += 1
    
    has_topic = row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['-', '', '_']
    if not has_topic:
        program_stats[program]['missing'] += 1

print(f'{"Program":<15} {"Total":<8} {"Missing":<8} {"Coverage":<10}')
print('-' * 45)
for program, stats in sorted(program_stats.items(), key=lambda x: x[1]['missing'], reverse=True)[:15]:
    coverage = ((stats['total'] - stats['missing']) / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f'{program:<15} {stats["total"]:<8} {stats["missing"]:<8} {coverage:>6.1f}%')

# Sample attended sessions with no topics
print('\n📝 Sample: Attended Sessions Missing Topics')
print('-' * 70)
attended_missing = missing_categories.get('attended_but_no_topic', [])[:5]
for session in attended_missing:
    print(f"Student: {session['Student_Name']} ({session['Student_ID']})")
    print(f"  Program: {session['Program']}, Course: {session.get('Course_Code', 'N/A')}")
    print(f"  Date: {session['Session_Date']}, Session #: {session.get('Session_Number', 'N/A')}")
    print(f"  Original Topic: '{session.get('Lesson_Topic_Original', '')}'")
    print()

# Analyze attendance patterns in missing topics
print('\n📊 Attendance Types in Missing Topics:')
print('-' * 70)
attendance_counts = Counter()
for row in data:
    has_topic = row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['-', '', '_']
    if not has_topic:
        attendance = row.get('Attendance', '')
        attendance_counts[attendance] += 1

for att, count in attendance_counts.most_common(10):
    print(f'{att:<25} {count:>5}')

# Recommendations
print('\n🎯 RECOMMENDATIONS TO REACH 100% COVERAGE:')
print('=' * 70)
print()
print('1. LEGITIMATE GAPS (No action needed):')
print(f'   - No Class/Holidays: {len(missing_categories["legitimate_no_class"])} sessions')
print(f'   - Student Absent: {len(missing_categories["student_absent"])} sessions')
print(f'   → These ~{len(missing_categories["legitimate_no_class"]) + len(missing_categories["student_absent"])} sessions should remain empty')
print()
print('2. FIXABLE GAPS (Action required):')
print(f'   - Attended but no topic: {len(missing_categories["attended_but_no_topic"])} sessions')
print(f'   - Attendance not marked: {len(missing_categories["attendance_not_marked"])} sessions')
print(f'   - No course mapping: {len(missing_categories["no_course_mapping"])} sessions')
print(f'   → These ~{len(missing_categories["attended_but_no_topic"]) + len(missing_categories["attendance_not_marked"]) + len(missing_categories["no_course_mapping"])} sessions can be enhanced')

# Calculate achievable percentage
legitimate_empty = len(missing_categories["legitimate_no_class"]) + len(missing_categories["student_absent"])
fixable = total_missing - legitimate_empty
currently_filled = len(data) - total_missing
max_achievable = currently_filled + fixable
max_percentage = (max_achievable / len(data) * 100) if len(data) > 0 else 0

print()
print('📈 ACHIEVABLE TARGET:')
print(f'   Current coverage: {currently_filled}/{len(data)} ({currently_filled/len(data)*100:.1f}%)')
print(f'   Legitimate gaps: {legitimate_empty} sessions')
print(f'   Fixable gaps: {fixable} sessions')
print(f'   Maximum achievable: {max_achievable}/{len(data)} ({max_percentage:.1f}%)')