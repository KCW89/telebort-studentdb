#!/usr/bin/env python3
"""Analyze lesson topic data quality issues"""

import csv
from collections import Counter

# Read the vertical CSV
with open('data/vertical_csv/telebort_all_sessions_vertical_20250806_232159.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = list(reader)

# Analyze lesson topics
lesson_topics = [row['Lesson_Topic'] for row in data]

# Count empty/missing
empty_count = sum(1 for topic in lesson_topics if not topic or topic == '-')
print(f'📊 LESSON TOPIC ANALYSIS')
print(f'=' * 60)
print(f'Total sessions: {len(lesson_topics)}')
print(f'Empty/missing topics: {empty_count} ({empty_count/len(lesson_topics)*100:.1f}%)')
print(f'Has content: {len(lesson_topics) - empty_count} ({(len(lesson_topics) - empty_count)/len(lesson_topics)*100:.1f}%)')

# Find common patterns
print(f'\n🔍 Sample of problematic entries:')
problems = []
for topic in lesson_topics[:500]:  # Sample first 500
    if topic and topic != '-':
        # Check for incomplete entries
        if len(topic) < 5 or (topic.startswith('L') and ':' not in topic):
            problems.append(topic)
            
for p in set(list(problems)[:10]):
    print(f'  - "{p}"')

# Check for lesson numbering patterns
print(f'\n📝 Common lesson patterns found:')
patterns = {
    'L[num]:': 0,
    'L[num] ': 0,
    'Lesson [num]': 0,
    'concept [num]': 0,
    'Project': 0,
    'Quiz': 0,
    'Exercise': 0
}

for topic in lesson_topics:
    if not topic:
        continue
    topic_lower = topic.lower()
    if topic.startswith('L') and any(c.isdigit() for c in topic[:4]):
        patterns['L[num]:'] += 1
    elif 'lesson' in topic_lower:
        patterns['Lesson [num]'] += 1
    elif 'concept' in topic_lower:
        patterns['concept [num]'] += 1
    elif 'project' in topic_lower:
        patterns['Project'] += 1
    elif 'quiz' in topic_lower:
        patterns['Quiz'] += 1
    elif 'exercise' in topic_lower:
        patterns['Exercise'] += 1
        
for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f'  {pattern}: {count} occurrences')