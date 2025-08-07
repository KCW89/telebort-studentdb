#!/usr/bin/env python3
"""Check quality of enhanced data"""

import csv

# Read enhanced file
with open('data/vertical_csv/telebort_sessions_final_20250806_233834.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = list(reader)

print('📊 ENHANCED DATA QUALITY REPORT')
print('=' * 60)

# Count enhancements
enhancement_types = {}
for row in data:
    enhancement = row.get('Data_Enhancement', 'Unknown')
    enhancement_types[enhancement] = enhancement_types.get(enhancement, 0) + 1

print('\n🎯 Enhancement Types:')
for etype, count in sorted(enhancement_types.items()):
    pct = count / len(data) * 100
    print(f'  {etype:<20} {count:>5} ({pct:.1f}%)')

# Sample enhanced records
print('\n📝 Sample Enhanced Records (Inferred):')
print('-' * 60)

inferred_samples = [row for row in data if row.get('Data_Enhancement') == 'Enhanced_Inferred'][:3]
for sample in inferred_samples:
    print(f"Student: {sample['Student_Name']} ({sample['Student_ID']})")
    print(f"  Date: {sample['Session_Date']}")
    print(f"  Original Topic: '{sample['Lesson_Topic_Original']}'")
    print(f"  Enhanced Topic: '{sample['Lesson_Topic_Standard']}'")
    print(f"  Lesson ID: {sample.get('Lesson_ID', 'N/A')}")
    print(f"  Type: {sample.get('Lesson_Type', 'N/A')}")
    print()

print('\n📝 Sample Enhanced Records (Direct Match):')
print('-' * 60)

direct_samples = [row for row in data if row.get('Data_Enhancement') == 'Enhanced_Direct'][:3]
for sample in direct_samples:
    print(f"Student: {sample['Student_Name']} ({sample['Student_ID']})")
    print(f"  Date: {sample['Session_Date']}")
    print(f"  Original Topic: '{sample['Lesson_Topic_Original']}'")
    print(f"  Enhanced Topic: '{sample['Lesson_Topic_Standard']}'")
    if sample.get('Exit_Ticket_Link'):
        print(f"  Exit Ticket: {sample.get('Exit_Ticket_Link', 'N/A')[:40]}...")
    print()

# Count filled vs empty lesson topics
has_standard_topic = sum(1 for row in data if row.get('Lesson_Topic_Standard') and row['Lesson_Topic_Standard'] not in ['-', '', '_'])
print(f'\n📈 Lesson Topic Coverage:')
print(f'  Has standardized topic: {has_standard_topic} ({has_standard_topic/len(data)*100:.1f}%)')
print(f'  Missing topic: {len(data) - has_standard_topic} ({(len(data) - has_standard_topic)/len(data)*100:.1f}%)')