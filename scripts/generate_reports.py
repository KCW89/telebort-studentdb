#!/usr/bin/env python3
"""
generate_reports.py - Generates or updates student markdown reports

This script takes processed student data and generates markdown reports
following the living document approach - one file per student that gets
updated weekly.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional


class ReportGenerator:
    """Generates markdown reports from processed student data"""
    
    def __init__(self, reports_dir: str = "reports", template_dir: str = "templates"):
        """
        Initialize the report generator
        
        Args:
            reports_dir: Directory to save reports
            template_dir: Directory containing templates
        """
        self.reports_dir = reports_dir
        self.template_dir = template_dir
        self.logger = self._setup_logger()
        
        # Ensure directories exist
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('ReportGenerator')
        logger.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        
        return logger
    
    def generate_report(self, student_data: Dict[str, Any]) -> str:
        """
        Generate or update a student report
        
        Args:
            student_data: Processed student data
            
        Returns:
            Path to generated report
        """
        student_id = student_data['student_id']
        report_path = os.path.join(self.reports_dir, f"{student_id}.md")
        
        self.logger.debug(f"Generating report for {student_id}")
        
        # Generate report content
        content = self._generate_content(student_data)
        
        # Check if content has changed
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            if existing_content == content:
                self.logger.debug(f"No changes for {student_id}, skipping update")
                return report_path
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Generated report: {report_path}")
        return report_path
    
    def _generate_content(self, data: Dict[str, Any]) -> str:
        """
        Generate markdown content from student data
        
        Args:
            data: Processed student data
            
        Returns:
            Markdown content as string
        """
        # Extract data sections
        student_id = data['student_id']
        status = data['current_status']
        journey = data['learning_journey']
        attendance = data['attendance_summary']
        metadata = data['metadata']
        
        # Build markdown content
        lines = []
        
        # Header
        lines.append(f"# Student Learning Record - {student_id}")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d')} | Week {metadata['week_number']}/{metadata['year']}*")
        lines.append("")
        
        # Current Status section
        lines.append("## Current Status")
        lines.append(f"- **Program:** {status['program']}")
        lines.append(f"- **Schedule:** {status['schedule']}")
        lines.append(f"- **Teacher:** {status['teacher']}")
        
        if status['latest_session']:
            lines.append(f"- **Latest Session:** {status['latest_session']} (as of {status['latest_session_date']})")
        else:
            lines.append("- **Latest Session:** No session data available")
            
        if status['latest_lesson']:
            lines.append(f"- **Latest Lesson:** {status['latest_lesson']}")
        else:
            lines.append("- **Latest Lesson:** -")
            
        if status['latest_status']:
            lines.append(f"- **Latest Status:** {status['latest_status']}")
        else:
            lines.append("- **Latest Status:** -")
        
        lines.append("")
        
        # Learning Journey section
        lines.append("## Learning Journey")
        
        if journey:
            # Table header
            lines.append("| Date | Session | Lesson | Attendance | Progress |")
            lines.append("|------|---------|--------|------------|----------|")
            
            # Table rows
            for session in journey:
                date = session['date'] or '-'
                session_num = session['session'] or '-'
                lesson = self._escape_markdown(session['lesson']) or '-'
                attendance_val = session['attendance'] or '-'
                progress = session['progress'] or '-'
                
                lines.append(f"| {date} | {session_num} | {lesson} | {attendance_val} | {progress} |")
        else:
            lines.append("*No session data available*")
        
        lines.append("")
        
        # Attendance Summary section
        lines.append("## Attendance Summary")
        
        if attendance['total_sessions'] > 0:
            lines.append(f"- **Total Sessions with Attendance Data:** {attendance['total_sessions']}")
            lines.append(f"- **Attended:** {attendance['attended']}")
            lines.append(f"- **Absent:** {attendance['absent']}")
            lines.append(f"- **No Class/Break:** {attendance['no_class']}")
            lines.append(f"- **Attendance Rate:** {attendance['attendance_rate']}% ({attendance['attended']}/{attendance['countable_sessions']})")
        else:
            lines.append("*No attendance data available*")
        
        lines.append("")
        lines.append("---")
        lines.append("*This is an automated learning record. For interpretation and recommendations, please consult with the teacher.*")
        
        return '\n'.join(lines)
    
    def _escape_markdown(self, text: str) -> str:
        """
        Escape special markdown characters in text
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        if not text:
            return text
        
        # Replace newlines with space for table cells
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Escape pipe characters
        text = text.replace('|', '\\|')
        
        return text
    
    def generate_batch(self, students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate reports for multiple students
        
        Args:
            students: List of processed student data
            
        Returns:
            Summary of generation results
        """
        results = {
            'total': len(students),
            'generated': 0,
            'unchanged': 0,
            'errors': 0,
            'error_details': []
        }
        
        for student in students:
            try:
                student_id = student.get('student_id', 'Unknown')
                report_path = self.generate_report(student)
                
                # Check if file was actually updated
                if report_path:
                    results['generated'] += 1
                else:
                    results['unchanged'] += 1
                    
            except Exception as e:
                results['errors'] += 1
                error_msg = f"Student {student_id}: {str(e)}"
                results['error_details'].append(error_msg)
                self.logger.error(error_msg)
        
        # Log summary
        self.logger.info(
            f"Report generation complete: "
            f"{results['generated']} generated, "
            f"{results['unchanged']} unchanged, "
            f"{results['errors']} errors"
        )
        
        return results


def main():
    """Main function for testing"""
    generator = ReportGenerator()
    
    # Test data
    test_data = {
        'student_id': 's12345',
        'current_status': {
            'program': 'G (AI-2)',
            'schedule': 'Saturday 10:00-11:00',
            'teacher': 'Soumiya',
            'latest_session': '2',
            'latest_session_date': '09/08/2025',
            'latest_lesson': 'C2 Machine Learning',
            'latest_status': 'In Progress'
        },
        'learning_journey': [
            {
                'date': '09/08/2025',
                'session': '2',
                'lesson': 'C2 Machine Learning',
                'attendance': 'Soumiya',
                'progress': 'In Progress'
            },
            {
                'date': '02/08/2025',
                'session': '1',
                'lesson': 'C1 Introduction to AI',
                'attendance': 'Soumiya',
                'progress': 'Completed'
            }
        ],
        'attendance_summary': {
            'total_sessions': 2,
            'attended': 2,
            'absent': 0,
            'no_class': 0,
            'attendance_rate': 100.0,
            'countable_sessions': 2
        },
        'metadata': {
            'processed_at': datetime.now().isoformat(),
            'week_number': datetime.now().isocalendar()[1],
            'year': datetime.now().year
        }
    }
    
    # Generate test report
    report_path = generator.generate_report(test_data)
    print(f"Generated report: {report_path}")
    
    # Show content
    with open(report_path, 'r', encoding='utf-8') as f:
        print("\nReport content:")
        print(f.read())
    
    return 0


if __name__ == "__main__":
    exit(main())