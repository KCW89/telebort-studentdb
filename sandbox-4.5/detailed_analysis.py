import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def detailed_sandbox_analysis():
    """
    Detailed analysis of the CurrentSandbox.csv file with visualizations
    """
    print("=" * 70)
    print("DETAILED CURRENT SANDBOX DATA ANALYSIS")
    print("=" * 70)
    
    # Read the CSV file
    try:
        df = pd.read_csv('CurrentSandbox.csv')
        print(f"✓ Successfully loaded CSV file with {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        print(f"✗ Error reading CSV file: {e}")
        return
    
    # Set up plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # 1. DATA STRUCTURE ANALYSIS
    print(f"\n🔍 DETAILED DATA STRUCTURE ANALYSIS:")
    
    # Analyze the wide format structure
    column_groups = {}
    for col in df.columns:
        if 'Date' in col:
            if 'Date' not in column_groups:
                column_groups['Date'] = []
            column_groups['Date'].append(col)
        elif 'Attendance' in col:
            if 'Attendance' not in column_groups:
                column_groups['Attendance'] = []
            column_groups['Attendance'].append(col)
        elif 'CSguru' in col:
            if 'CSguru' not in column_groups:
                column_groups['CSguru'] = []
            column_groups['CSguru'].append(col)
        elif 'Session' in col:
            if 'Session' not in column_groups:
                column_groups['Session'] = []
            column_groups['Session'].append(col)
        elif 'Submission' in col:
            if 'Submission' not in column_groups:
                column_groups['Submission'] = []
            column_groups['Submission'].append(col)
        elif 'Lesson' in col:
            if 'Lesson' not in column_groups:
                column_groups['Lesson'] = []
            column_groups['Lesson'].append(col)
        elif 'Exit ticket' in col:
            if 'Exit ticket' not in column_groups:
                column_groups['Exit ticket'] = []
            column_groups['Exit ticket'].append(col)
        elif 'Progress' in col:
            if 'Progress' not in column_groups:
                column_groups['Progress'] = []
            column_groups['Progress'].append(col)
    
    print(f"   Column groups found:")
    for group, cols in column_groups.items():
        print(f"     • {group}: {len(cols)} columns")
    
    # 2. STUDENT ANALYSIS
    print(f"\n👥 STUDENT ANALYSIS:")
    
    # Count students (rows with actual data)
    students_with_data = 0
    for idx, row in df.iterrows():
        if row.notna().sum() > 10:  # More than 10 non-null values
            students_with_data += 1
    
    print(f"   • Students with significant data: {students_with_data}")
    print(f"   • Empty student records: {len(df) - students_with_data}")
    
    # 3. ATTENDANCE PATTERN ANALYSIS
    print(f"\n📅 ATTENDANCE PATTERN ANALYSIS:")
    
    attendance_data = []
    for col in column_groups.get('Attendance', []):
        if col in df.columns:
            values = df[col].dropna()
            attendance_data.extend(values.tolist())
    
    if attendance_data:
        attendance_series = pd.Series(attendance_data)
        attendance_counts = attendance_series.value_counts()
        
        # Create attendance pie chart
        plt.figure(figsize=(10, 6))
        plt.subplot(1, 2, 1)
        plt.pie(attendance_counts.values, labels=attendance_counts.index, autopct='%1.1f%%')
        plt.title('Attendance Distribution')
        
        # Create attendance bar chart
        plt.subplot(1, 2, 2)
        attendance_counts.plot(kind='bar')
        plt.title('Attendance Counts')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('attendance_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ Attendance visualization saved as 'attendance_analysis.png'")
    
    # 4. PROGRESS TREND ANALYSIS
    print(f"\n⭐ PROGRESS TREND ANALYSIS:")
    
    progress_data = []
    for col in column_groups.get('Progress', []):
        if col in df.columns:
            values = df[col].dropna()
            progress_data.extend(values.tolist())
    
    if progress_data:
        progress_series = pd.Series(progress_data)
        progress_counts = progress_series.value_counts()
        
        # Create progress visualization
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        progress_counts.plot(kind='bar')
        plt.title('Progress Rating Distribution')
        plt.xticks(rotation=45)
        
        # Calculate progress statistics
        progress_stats = {
            'Excellent (★★★★★)': progress_counts.get('★★★★★', 0),
            'Good (★★★★☆)': progress_counts.get('★★★★☆', 0),
            'Poor (☆☆☆☆☆)': progress_counts.get('☆☆☆☆☆', 0),
            'No Rating (-)': progress_counts.get('-', 0)
        }
        
        plt.subplot(1, 2, 2)
        plt.pie(progress_stats.values(), labels=progress_stats.keys(), autopct='%1.1f%%')
        plt.title('Progress Rating Summary')
        plt.tight_layout()
        plt.savefig('progress_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✓ Progress visualization saved as 'progress_analysis.png'")
        
        # Progress insights
        total_progress = sum(progress_stats.values())
        if total_progress > 0:
            excellent_rate = (progress_stats['Excellent (★★★★★)'] / total_progress) * 100
            good_rate = (progress_stats['Good (★★★★☆)'] / total_progress) * 100
            poor_rate = (progress_stats['Poor (☆☆☆☆☆)'] / total_progress) * 100
            
            print(f"   • Excellent progress rate: {excellent_rate:.1f}%")
            print(f"   • Good progress rate: {good_rate:.1f}%")
            print(f"   • Poor progress rate: {poor_rate:.1f}%")
    
    # 5. LESSON COMPLETION ANALYSIS
    print(f"\n📚 LESSON COMPLETION ANALYSIS:")
    
    lesson_data = []
    for col in column_groups.get('Lesson', []):
        if col in df.columns:
            values = df[col].dropna()
            lesson_data.extend(values.tolist())
    
    if lesson_data:
        lesson_series = pd.Series(lesson_data)
        lesson_counts = lesson_series.value_counts()
        
        # Filter out empty entries
        lesson_counts = lesson_counts[lesson_counts.index != '-']
        
        if len(lesson_counts) > 0:
            print(f"   • Total lesson records: {len(lesson_data)}")
            print(f"   • Completed lessons: {len(lesson_counts)}")
            print(f"   • Most common lessons:")
            for lesson, count in lesson_counts.head(5).items():
                percentage = (count / len(lesson_data)) * 100
                print(f"     - {lesson}: {count} ({percentage:.1f}%)")
    
    # 6. EXIT TICKET PERFORMANCE
    print(f"\n🎯 EXIT TICKET PERFORMANCE ANALYSIS:")
    
    exit_ticket_data = []
    for col in column_groups.get('Exit ticket', []):
        if col in df.columns:
            values = df[col].dropna()
            exit_ticket_data.extend(values.tolist())
    
    if exit_ticket_data:
        exit_ticket_series = pd.Series(exit_ticket_data)
        exit_ticket_counts = exit_ticket_series.value_counts()
        
        # Filter out empty entries
        exit_ticket_counts = exit_ticket_counts[exit_ticket_counts.index != '-']
        
        if len(exit_ticket_counts) > 0:
            print(f"   • Total exit ticket records: {len(exit_ticket_data)}")
            print(f"   • Completed exit tickets: {len(exit_ticket_counts)}")
            
            # Analyze scores
            scores = []
            for entry in exit_ticket_counts.index:
                if '/' in str(entry):
                    try:
                        score_part = entry.split('ET: ')[-1]
                        if '/' in score_part:
                            score = score_part.split('/')[0].strip()
                            if score.isdigit():
                                scores.append(int(score))
                    except:
                        continue
            
            if scores:
                avg_score = np.mean(scores)
                max_score = max(scores)
                min_score = min(scores)
                print(f"   • Average exit ticket score: {avg_score:.1f}")
                print(f"   • Score range: {min_score} - {max_score}")
    
    # 7. DATA QUALITY ASSESSMENT
    print(f"\n🔍 DATA QUALITY ASSESSMENT:")
    
    # Calculate completeness by column group
    completeness_by_group = {}
    for group, cols in column_groups.items():
        total_cells = len(cols) * len(df)
        filled_cells = 0
        for col in cols:
            if col in df.columns:
                filled_cells += df[col].notna().sum()
        completeness = (filled_cells / total_cells) * 100
        completeness_by_group[group] = completeness
    
    # Create completeness visualization
    plt.figure(figsize=(12, 6))
    groups = list(completeness_by_group.keys())
    completeness_values = list(completeness_by_group.values())
    
    plt.bar(groups, completeness_values)
    plt.title('Data Completeness by Column Group')
    plt.ylabel('Completeness (%)')
    plt.xticks(rotation=45)
    plt.ylim(0, 100)
    
    # Add percentage labels on bars
    for i, v in enumerate(completeness_values):
        plt.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('data_completeness.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✓ Data completeness visualization saved as 'data_completeness.png'")
    
    for group, completeness in completeness_by_group.items():
        print(f"   • {group}: {completeness:.1f}% complete")
    
    # 8. RECOMMENDATIONS
    print(f"\n📈 STRATEGIC RECOMMENDATIONS:")
    
    print(f"\n   🔧 IMMEDIATE ACTIONS:")
    print(f"     • Restructure data to long format for better analysis")
    print(f"     • Implement data validation rules")
    print(f"     • Add unique student identifiers")
    print(f"     • Standardize progress rating system")
    
    print(f"\n   📊 ANALYSIS OPPORTUNITIES:")
    print(f"     • Track individual student progress over time")
    print(f"     • Identify at-risk students early")
    print(f"     • Analyze lesson effectiveness")
    print(f"     • Monitor attendance patterns")
    
    print(f"\n   🎯 IMPROVEMENT AREAS:")
    print(f"     • Data entry consistency (currently {completeness_by_group.get('Progress', 0):.1f}% complete)")
    print(f"     • Exit ticket completion rate")
    print(f"     • Lesson completion tracking")
    print(f"     • Attendance monitoring")
    
    print(f"\n" + "=" * 70)
    print("DETAILED ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"📁 Generated visualizations:")
    print(f"   • attendance_analysis.png")
    print(f"   • progress_analysis.png") 
    print(f"   • data_completeness.png")

if __name__ == "__main__":
    detailed_sandbox_analysis() 