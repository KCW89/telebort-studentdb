#!/usr/bin/env python3
"""
monitoring.py - Monitoring and alerting system for student report sync

This module provides monitoring capabilities including:
- Sync status tracking
- Error detection and alerting
- Performance metrics
- Data quality checks
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict


class SyncMonitor:
    """Monitor sync operations and track metrics"""
    
    def __init__(self, metrics_file: str = 'logs/sync_metrics.json'):
        """
        Initialize the sync monitor
        
        Args:
            metrics_file: Path to store metrics data
        """
        self.metrics_file = metrics_file
        self.logger = self._setup_logger()
        self.metrics = self._load_metrics()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('SyncMonitor')
        logger.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # File handler for alerts
        os.makedirs('logs', exist_ok=True)
        fh = logging.FileHandler('logs/alerts.log')
        fh.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(ch)
            logger.addHandler(fh)
        
        return logger
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics from file"""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load metrics: {e}")
        
        return {
            'sync_history': [],
            'error_counts': defaultdict(int),
            'performance_metrics': {},
            'data_quality_issues': []
        }
    
    def _save_metrics(self) -> None:
        """Save metrics to file"""
        try:
            os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
            with open(self.metrics_file, 'w') as f:
                # Convert defaultdict to regular dict for JSON serialization
                metrics_copy = self.metrics.copy()
                metrics_copy['error_counts'] = dict(metrics_copy['error_counts'])
                json.dump(metrics_copy, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")
    
    def record_sync_result(self, result: Dict[str, Any]) -> None:
        """
        Record the result of a sync operation
        
        Args:
            result: Sync result dictionary from batch processor or weekly sync
        """
        timestamp = datetime.now().isoformat()
        
        sync_record = {
            'timestamp': timestamp,
            'students_fetched': result.get('students_fetched', 0),
            'students_processed': result.get('students_processed', 0),
            'reports_generated': result.get('reports_generated', 0),
            'errors': len(result.get('errors', [])),
            'duration_seconds': result.get('duration_seconds', 0)
        }
        
        # Add to history
        self.metrics['sync_history'].append(sync_record)
        
        # Keep only last 100 records
        if len(self.metrics['sync_history']) > 100:
            self.metrics['sync_history'] = self.metrics['sync_history'][-100:]
        
        # Update error counts
        if 'error_counts' not in self.metrics:
            self.metrics['error_counts'] = {}
            
        for error in result.get('errors', []):
            error_type = self._classify_error(error)
            if error_type not in self.metrics['error_counts']:
                self.metrics['error_counts'][error_type] = 0
            self.metrics['error_counts'][error_type] += 1
        
        # Check for alerts
        self._check_alerts(sync_record, result)
        
        # Save metrics
        self._save_metrics()
        
        self.logger.info(f"Recorded sync: {sync_record}")
    
    def _classify_error(self, error_msg: str) -> str:
        """Classify error type from error message"""
        error_lower = error_msg.lower()
        
        if 'connection' in error_lower or 'mcp' in error_lower:
            return 'connection_error'
        elif 'parse' in error_lower or 'parsing' in error_lower:
            return 'parse_error'
        elif 'validation' in error_lower:
            return 'validation_error'
        elif 'timeout' in error_lower:
            return 'timeout_error'
        else:
            return 'other_error'
    
    def _check_alerts(self, sync_record: Dict[str, Any], full_result: Dict[str, Any]) -> None:
        """Check for conditions that require alerts"""
        alerts = []
        
        # Alert 1: High error rate
        if sync_record['errors'] > 5:
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f"High error count: {sync_record['errors']} errors in sync"
            })
        
        # Alert 2: Low processing rate
        if sync_record['students_fetched'] > 0:
            process_rate = sync_record['students_processed'] / sync_record['students_fetched']
            if process_rate < 0.8:
                alerts.append({
                    'type': 'low_process_rate',
                    'severity': 'medium',
                    'message': f"Low processing rate: {process_rate:.1%} of fetched students"
                })
        
        # Alert 3: No reports generated
        if sync_record['students_processed'] > 0 and sync_record['reports_generated'] == 0:
            alerts.append({
                'type': 'no_reports_generated',
                'severity': 'high',
                'message': "No reports generated despite processing students"
            })
        
        # Alert 4: Slow performance
        if sync_record['duration_seconds'] > 300:  # 5 minutes
            alerts.append({
                'type': 'slow_performance',
                'severity': 'low',
                'message': f"Sync took {sync_record['duration_seconds']/60:.1f} minutes"
            })
        
        # Log alerts
        for alert in alerts:
            self._log_alert(alert)
    
    def _log_alert(self, alert: Dict[str, Any]) -> None:
        """Log an alert based on severity"""
        message = f"[{alert['type'].upper()}] {alert['message']}"
        
        if alert['severity'] == 'high':
            self.logger.error(message)
        elif alert['severity'] == 'medium':
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def get_recent_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get metrics for recent sync operations
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Summary of recent metrics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_syncs = [
            sync for sync in self.metrics['sync_history']
            if datetime.fromisoformat(sync['timestamp']) > cutoff_time
        ]
        
        if not recent_syncs:
            return {
                'period_hours': hours,
                'sync_count': 0,
                'message': 'No syncs in period'
            }
        
        total_students = sum(s['students_processed'] for s in recent_syncs)
        total_reports = sum(s['reports_generated'] for s in recent_syncs)
        total_errors = sum(s['errors'] for s in recent_syncs)
        avg_duration = sum(s['duration_seconds'] for s in recent_syncs) / len(recent_syncs)
        
        return {
            'period_hours': hours,
            'sync_count': len(recent_syncs),
            'total_students_processed': total_students,
            'total_reports_generated': total_reports,
            'total_errors': total_errors,
            'average_duration_seconds': avg_duration,
            'success_rate': sum(1 for s in recent_syncs if s['errors'] == 0) / len(recent_syncs)
        }
    
    def check_data_quality(self, students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check data quality issues in student records
        
        Args:
            students: List of student records
            
        Returns:
            List of quality issues found
        """
        issues = []
        
        for student in students:
            student_id = student.get('info', {}).get('student_id', 'Unknown')
            
            # Check 1: Missing required fields
            required_fields = ['student_id', 'student_name', 'program']
            for field in required_fields:
                if not student.get('info', {}).get(field):
                    issues.append({
                        'student_id': student_id,
                        'type': 'missing_field',
                        'field': field,
                        'severity': 'high'
                    })
            
            # Check 2: No sessions
            if not student.get('sessions'):
                issues.append({
                    'student_id': student_id,
                    'type': 'no_sessions',
                    'severity': 'medium'
                })
            
            # Check 3: Invalid dates
            for session in student.get('sessions', []):
                if session.get('date'):
                    try:
                        # Try to parse date
                        datetime.strptime(session['date'], '%d/%m/%Y')
                    except ValueError:
                        issues.append({
                            'student_id': student_id,
                            'type': 'invalid_date',
                            'date': session['date'],
                            'severity': 'low'
                        })
        
        # Record issues
        if issues:
            self.metrics['data_quality_issues'] = issues
            self._save_metrics()
        
        return issues
    
    def generate_health_report(self) -> str:
        """Generate a health report of the sync system"""
        report_lines = [
            "=" * 60,
            "SYNC SYSTEM HEALTH REPORT",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Recent sync metrics
        metrics_24h = self.get_recent_metrics(24)
        metrics_7d = self.get_recent_metrics(24 * 7)
        
        report_lines.extend([
            "## Recent Activity",
            f"Last 24 hours: {metrics_24h['sync_count']} syncs",
        ])
        
        if metrics_24h['sync_count'] > 0:
            report_lines.extend([
                f"  - Students processed: {metrics_24h.get('total_students_processed', 0)}",
                f"  - Reports generated: {metrics_24h.get('total_reports_generated', 0)}",
                f"  - Errors: {metrics_24h.get('total_errors', 0)}",
                f"  - Success rate: {metrics_24h.get('success_rate', 0):.1%}",
            ])
        
        report_lines.extend([
            "",
            f"Last 7 days: {metrics_7d['sync_count']} syncs",
        ])
        
        if metrics_7d['sync_count'] > 0:
            report_lines.extend([
                f"  - Students processed: {metrics_7d.get('total_students_processed', 0)}",
                f"  - Reports generated: {metrics_7d.get('total_reports_generated', 0)}",
                f"  - Errors: {metrics_7d.get('total_errors', 0)}",
            ])
        
        report_lines.append("")
        
        # Error summary
        if self.metrics['error_counts']:
            report_lines.extend([
                "## Error Summary",
                "Error counts by type:"
            ])
            for error_type, count in sorted(self.metrics['error_counts'].items()):
                report_lines.append(f"  - {error_type}: {count}")
            report_lines.append("")
        
        # Data quality
        if self.metrics['data_quality_issues']:
            report_lines.extend([
                "## Data Quality Issues",
                f"Total issues: {len(self.metrics['data_quality_issues'])}"
            ])
            
            # Group by type
            issue_counts = defaultdict(int)
            for issue in self.metrics['data_quality_issues']:
                issue_counts[issue['type']] += 1
            
            for issue_type, count in sorted(issue_counts.items()):
                report_lines.append(f"  - {issue_type}: {count}")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)


def create_webhook_alert(webhook_url: Optional[str], alert: Dict[str, Any]) -> bool:
    """
    Send alert to webhook (Slack, Discord, etc.)
    
    Args:
        webhook_url: Webhook URL to send alert to
        alert: Alert data
        
    Returns:
        True if successful, False otherwise
    """
    if not webhook_url:
        return False
    
    try:
        import requests
        
        # Format message based on webhook type
        if 'discord' in webhook_url:
            # Discord webhook format
            payload = {
                'content': f"**Telebort Sync Alert**\n"
                          f"Type: {alert['type']}\n"
                          f"Severity: {alert['severity']}\n"
                          f"Message: {alert['message']}"
            }
        elif 'slack' in webhook_url:
            # Slack webhook format
            payload = {
                'text': f"*Telebort Sync Alert*\n"
                       f"Type: {alert['type']}\n"
                       f"Severity: {alert['severity']}\n"
                       f"Message: {alert['message']}"
            }
        else:
            # Generic format
            payload = alert
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code in [200, 204]
        
    except Exception as e:
        logging.error(f"Failed to send webhook alert: {e}")
        return False


def main():
    """Example usage and health check"""
    monitor = SyncMonitor()
    
    # Generate health report
    print(monitor.generate_health_report())
    
    # Example: Record a sync result
    example_result = {
        'students_fetched': 50,
        'students_processed': 48,
        'reports_generated': 45,
        'errors': ['Connection timeout', 'Parse error in row 25'],
        'duration_seconds': 120
    }
    
    print("\nRecording example sync result...")
    monitor.record_sync_result(example_result)
    
    print("\nRecent metrics (last 24h):")
    print(json.dumps(monitor.get_recent_metrics(24), indent=2))


if __name__ == "__main__":
    main()