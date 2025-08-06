#!/usr/bin/env python3
"""
process_batch3_complete.py - Process batch3_complete.json and generate enhanced student reports

This script processes the batch3_complete.json data containing student session data 
in structured format and generates markdown reports using the enhanced data processor 
for comprehensive data quality improvements.

Key features:
- Loads structured JSON data (different from raw CSV format)
- Uses enhanced_data_processor.py for data cleaning and standardization
- Handles 338 columns of session data with metadata parsing
- Generates comprehensive markdown reports with session history
- Saves reports to scripts/reports/ directory
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Add the scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_data_processor import EnhancedDataProcessor

class Batch3CompleteProcessor:
    """Process batch3 complete data and generate enhanced student reports"""
    
    def __init__(self, base_dir: str):
        """Initialize processor with base directory"""
        self.base_dir = base_dir
        self.scripts_dir = os.path.join(base_dir, "scripts")
        self.batch_file = os.path.join(base_dir, "batch3_complete.json")
        self.enhanced_processor = EnhancedDataProcessor()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_batch_data(self) -> List[Dict[str, Any]]:
        """Load the batch3_complete.json data"""
        try:
            with open(self.batch_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Data is already in structured format (list of student objects)
            student_count = len(data) if isinstance(data, list) else 0
            self.logger.info(f"Loaded batch3 complete data with {student_count} students")
            
            return data if isinstance(data, list) else []
        
        except FileNotFoundError:
            self.logger.error(f"Batch file not found: {self.batch_file}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in batch file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading batch data: {e}")
            raise
    
    def analyze_data_structure(self, students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the data structure to understand the format"""
        
        analysis = {
            'total_students': len(students),
            'student_fields': set(),
            'session_fields': set(),
            'programs': set(),
            'teachers': set(),
            'total_sessions': 0,
            'sessions_per_student': [],
            'date_range': {'earliest': None, 'latest': None}
        }
        
        for student in students:
            # Collect student-level fields
            analysis['student_fields'].update(student.keys())
            
            # Collect program and teacher info
            if student.get('program'):
                analysis['programs'].add(student['program'])
            if student.get('teacher'):
                analysis['teachers'].add(student['teacher'])
            
            # Analyze sessions
            sessions = student.get('sessions', [])
            analysis['total_sessions'] += len(sessions)
            analysis['sessions_per_student'].append({
                'student_id': student.get('student_id', 'unknown'),
                'session_count': len(sessions)
            })
            
            # Collect session fields and date range
            for session in sessions:
                analysis['session_fields'].update(session.keys())
                
                # Track date range
                date_str = session.get('date', '')
                if date_str and date_str != '-':
                    try:
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                        if not analysis['date_range']['earliest'] or date_obj < analysis['date_range']['earliest']:
                            analysis['date_range']['earliest'] = date_obj
                        if not analysis['date_range']['latest'] or date_obj > analysis['date_range']['latest']:
                            analysis['date_range']['latest'] = date_obj
                    except ValueError:
                        pass
        
        # Convert sets to lists for JSON serialization
        analysis['student_fields'] = list(analysis['student_fields'])
        analysis['session_fields'] = list(analysis['session_fields'])
        analysis['programs'] = list(analysis['programs'])
        analysis['teachers'] = list(analysis['teachers'])
        
        # Format dates
        if analysis['date_range']['earliest']:
            analysis['date_range']['earliest'] = analysis['date_range']['earliest'].strftime('%d/%m/%Y')
        if analysis['date_range']['latest']:
            analysis['date_range']['latest'] = analysis['date_range']['latest'].strftime('%d/%m/%Y')
        
        return analysis
    
    def validate_student_data(self, students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the student data for completeness"""
        
        validation_report = {
            'valid_students': 0,
            'invalid_students': 0,
            'missing_student_ids': [],
            'missing_names': [],
            'students_with_no_sessions': [],
            'students_with_invalid_sessions': [],
            'total_valid_sessions': 0,
            'total_invalid_sessions': 0
        }
        
        for student in students:
            student_id = student.get('student_id', '').strip()
            name = student.get('name', '').strip()
            sessions = student.get('sessions', [])
            
            # Check basic student info
            if not student_id:
                validation_report['missing_student_ids'].append(student.get('name', 'Unknown'))
                validation_report['invalid_students'] += 1
                continue
            
            if not name:
                validation_report['missing_names'].append(student_id)
            
            # Check sessions
            if not sessions:
                validation_report['students_with_no_sessions'].append(student_id)
            
            valid_sessions = 0
            invalid_sessions = 0
            
            for session in sessions:
                date = session.get('date', '').strip()
                if date and date != '-':
                    # Check if date format is valid
                    try:
                        datetime.strptime(date, '%d/%m/%Y')
                        valid_sessions += 1
                    except ValueError:
                        invalid_sessions += 1
                else:
                    invalid_sessions += 1
            
            validation_report['total_valid_sessions'] += valid_sessions
            validation_report['total_invalid_sessions'] += invalid_sessions
            
            if invalid_sessions > valid_sessions:
                validation_report['students_with_invalid_sessions'].append(student_id)
            
            validation_report['valid_students'] += 1
        
        return validation_report
    
    def process_students(self, students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process students using enhanced data processor"""
        
        self.logger.info(f"Processing {len(students)} students with enhanced data processor")
        
        # The data is already in structured format, so we can process directly
        processed_data, quality_metrics = self.enhanced_processor.process_student_data(students)
        
        self.logger.info(f"Enhanced processing complete. Quality metrics: {quality_metrics}")
        
        return processed_data
    
    def generate_student_report(self, student_data: Dict[str, Any]) -> str:
        """Generate comprehensive markdown report for a student"""
        
        student_id = student_data['student_id']
        name = student_data['name']
        program = student_data['program']
        schedule = student_data.get('schedule', 'Not specified')
        teacher = student_data['teacher']
        sessions = student_data['sessions']
        attendance_stats = student_data.get('attendance_stats', {})
        
        # Generate report content
        report_lines = []
        report_lines.append(f"# Student Attendance & Progress Report - {name}")
        report_lines.append(f"**Student:** {name}")
        report_lines.append(f"**Student ID:** {student_id}")
        report_lines.append(f"**Program:** {program}")
        report_lines.append(f"**Schedule:** {schedule}")
        report_lines.append(f"**Primary Teacher:** {teacher}")
        report_lines.append(f"**Total Sessions:** {len(sessions)}")
        report_lines.append("")
        
        # Add attendance statistics
        if attendance_stats:
            report_lines.append("## Summary Statistics")
            report_lines.append(f"- Classes Attended: {attendance_stats.get('attended', 0)}")
            report_lines.append(f"- Classes Absent: {attendance_stats.get('absent', 0)}")
            report_lines.append(f"- No Class/Holiday: {attendance_stats.get('no_class', 0)}")
            report_lines.append(f"- Attendance Rate: {attendance_stats.get('attendance_rate', 0):.1f}%")
            report_lines.append("")
        
        # Add program-specific insights
        program_insights = self._generate_program_insights(student_data)
        if program_insights:
            report_lines.append("## Program Progress Analysis")
            report_lines.extend(program_insights)
            report_lines.append("")
        
        # Add detailed session log
        report_lines.append("## Detailed Session Log")
        report_lines.append("| Date | Session | Attendance | Teacher | Progress | Lesson/Topic |")
        report_lines.append("|------|---------|------------|---------|----------|--------------|")
        
        for session in sessions:
            date = session['date']
            session_num = session['session']
            attendance = session['attendance']
            teacher_present = session.get('teacher_present', teacher)
            progress = session['progress']
            lesson_title = session.get('lesson_title', session.get('lesson', ''))
            
            # Clean lesson title for table display
            lesson_display = lesson_title.replace('|', '\\|').replace('\n', ' ')[:80]
            if len(lesson_title) > 80:
                lesson_display += "..."
            
            report_lines.append(f"| {date} | {session_num} | {attendance} | {teacher_present} | {progress} | {lesson_display} |")
        
        # Add lesson resources section if any sessions have URLs
        url_sessions = [s for s in sessions if s.get('lesson_url') or s.get('activity_url')]
        if url_sessions:
            report_lines.append("")
            report_lines.append("## Lesson Resources")
            for session in url_sessions:
                if session.get('lesson_url'):
                    report_lines.append(f"- **{session['date']} (Session {session['session']})**: {session.get('lesson_title', 'Lesson')}")
                    report_lines.append(f"  - Lesson: {session['lesson_url']}")
                    if session.get('activity_url'):
                        report_lines.append(f"  - Activity: {session['activity_url']}")
                    if session.get('exit_ticket'):
                        report_lines.append(f"  - Exit Ticket Score: {session['exit_ticket']}")
        
        # Add data quality improvements section
        report_lines.append("")
        report_lines.append("## Data Quality Enhancements")
        report_lines.append("This report includes the following data quality improvements:")
        report_lines.append("- Teacher name standardization in attendance fields")
        report_lines.append("- Progress value normalization (Completed, In Progress, Graduated)")
        report_lines.append("- URL extraction from lesson descriptions")
        report_lines.append("- Missing data handling and validation")
        report_lines.append("- Session numbering consistency")
        
        # Add footer
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("*Report generated with enhanced data processing and comprehensive quality improvements*")
        report_lines.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        report_lines.append(f"*Data processed from batch3_complete.json with {len(sessions)} total sessions*")
        
        return '\n'.join(report_lines)
    
    def _generate_program_insights(self, student_data: Dict[str, Any]) -> List[str]:
        """Generate program-specific insights for the student"""
        insights = []
        program = student_data.get('program', '')
        sessions = student_data.get('sessions', [])
        
        if not sessions:
            return insights
        
        # Count progress types
        progress_counts = {}
        for session in sessions:
            progress = session.get('progress', 'Unknown')
            progress_counts[progress] = progress_counts.get(progress, 0) + 1
        
        # Calculate completion rate
        completed_sessions = progress_counts.get('Completed', 0)
        graduated_sessions = progress_counts.get('Graduated', 0)
        total_learning_sessions = sum(progress_counts.get(p, 0) for p in ['Completed', 'In Progress', 'Graduated', 'Not Started'])
        
        if total_learning_sessions > 0:
            completion_rate = ((completed_sessions + graduated_sessions) / total_learning_sessions) * 100
            insights.append(f"- **Completion Rate**: {completion_rate:.1f}% ({completed_sessions + graduated_sessions}/{total_learning_sessions})")
        
        # Program-specific analysis
        if 'AI' in program:
            insights.append("- **Program Type**: AI & Machine Learning")
            insights.append("- **Focus Areas**: Supervised/Unsupervised Learning, Data Preparation, Regression, Classification")
        elif 'W' in program or 'Web' in program:
            insights.append("- **Program Type**: Web Development")
            insights.append("- **Focus Areas**: HTML/CSS, Bootstrap, JavaScript, React.js")
        elif 'BBP' in program or 'BBD' in program:
            insights.append("- **Program Type**: Block-Based Programming")
            insights.append("- **Focus Areas**: Python Fundamentals, Functions, Data Structures")
        
        # Recent activity
        if sessions:
            recent_sessions = sessions[:3]  # Last 3 sessions
            insights.append("- **Recent Activity**:")
            for session in recent_sessions:
                date = session.get('date', 'Unknown')
                progress = session.get('progress', 'Unknown')
                lesson = session.get('lesson_title', session.get('lesson', ''))[:50]
                insights.append(f"  - {date}: {progress} - {lesson}")
        
        return insights
    
    def save_reports(self, processed_students: List[Dict[str, Any]]) -> Dict[str, str]:
        """Save individual student reports and return summary"""
        
        results = {}
        reports_dir = os.path.join(self.scripts_dir, "reports")
        
        # Ensure reports directory exists
        os.makedirs(reports_dir, exist_ok=True)
        
        for student_data in processed_students:
            student_id = student_data['student_id']
            
            # Generate report
            report_content = self.generate_student_report(student_data)
            
            # Save to file
            report_file = os.path.join(reports_dir, f"{student_id}.md")
            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                results[student_id] = report_file
                self.logger.info(f"Saved report for {student_id}: {report_file}")
                
            except Exception as e:
                self.logger.error(f"Error saving report for {student_id}: {e}")
                results[student_id] = f"Error: {e}"
        
        return results
    
    def process_batch3_complete(self) -> Dict[str, Any]:
        """Main processing method"""
        
        self.logger.info("Starting batch3 complete data processing")
        
        # Load batch data
        students = self.load_batch_data()
        
        # Analyze data structure
        structure_analysis = self.analyze_data_structure(students)
        self.logger.info(f"Data structure analysis: {structure_analysis['total_students']} students, {structure_analysis['total_sessions']} total sessions")
        
        # Validate data
        validation_report = self.validate_student_data(students)
        self.logger.info(f"Data validation: {validation_report['valid_students']} valid students")
        
        # Process with enhanced cleaning
        processed_students = self.process_students(students)
        
        # Save reports
        report_files = self.save_reports(processed_students)
        
        # Generate comprehensive summary
        summary = {
            'batch_name': 'batch3_complete',
            'students_processed': len(processed_students),
            'report_files': report_files,
            'data_structure_analysis': structure_analysis,
            'validation_report': validation_report,
            'data_quality_metrics': self.enhanced_processor.data_quality_metrics,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # Generate detailed session count summary
        session_counts = {}
        program_distribution = {}
        teacher_distribution = {}
        
        for student in processed_students:
            student_id = student['student_id']
            session_count = len(student['sessions'])
            program = student.get('program', 'Unknown')
            teacher = student.get('teacher', 'Unknown')
            
            session_counts[student_id] = session_count
            program_distribution[program] = program_distribution.get(program, 0) + 1
            teacher_distribution[teacher] = teacher_distribution.get(teacher, 0) + 1
        
        summary['session_counts'] = session_counts
        summary['program_distribution'] = program_distribution
        summary['teacher_distribution'] = teacher_distribution
        
        self.logger.info(f"Batch3 complete processing finished: {len(processed_students)} students processed")
        
        return summary


def main():
    """Main execution function"""
    
    # Determine base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize and run processor
    processor = Batch3CompleteProcessor(base_dir)
    
    try:
        results = processor.process_batch3_complete()
        
        print("\n=== Batch3 Complete Processing Results ===")
        print(f"Students processed: {results['students_processed']}")
        print(f"Total data quality improvements: {sum(results['data_quality_metrics'].values())}")
        
        print(f"\nData structure analysis:")
        structure = results['data_structure_analysis']
        print(f"  Total sessions: {structure['total_sessions']}")
        print(f"  Date range: {structure['date_range']['earliest']} to {structure['date_range']['latest']}")
        print(f"  Programs: {', '.join(structure['programs'])}")
        print(f"  Teachers: {', '.join(structure['teachers'])}")
        
        print(f"\nProgram distribution:")
        for program, count in results['program_distribution'].items():
            print(f"  {program}: {count} students")
        
        print(f"\nTeacher distribution:")
        for teacher, count in results['teacher_distribution'].items():
            print(f"  {teacher}: {count} students")
        
        print(f"\nSession counts per student:")
        for student_id, count in results['session_counts'].items():
            print(f"  {student_id}: {count} sessions")
        
        print(f"\nData quality metrics:")
        for metric, count in results['data_quality_metrics'].items():
            print(f"  {metric}: {count}")
        
        print(f"\nValidation report:")
        validation = results['validation_report']
        print(f"  Valid students: {validation['valid_students']}")
        print(f"  Invalid students: {validation['invalid_students']}")
        print(f"  Valid sessions: {validation['total_valid_sessions']}")
        print(f"  Invalid sessions: {validation['total_invalid_sessions']}")
        
        if validation['students_with_no_sessions']:
            print(f"  Students with no sessions: {', '.join(validation['students_with_no_sessions'])}")
        
        print(f"\nReport files generated:")
        for student_id, file_path in results['report_files'].items():
            if not file_path.startswith('Error'):
                print(f"  {student_id}: {os.path.basename(file_path)}")
            else:
                print(f"  {student_id}: {file_path}")
        
        # Generate and display quality report
        quality_report = processor.enhanced_processor.generate_quality_report()
        print(f"\n{quality_report}")
        
        return results
        
    except Exception as e:
        logging.error(f"Batch3 complete processing failed: {e}")
        raise


if __name__ == "__main__":
    main()