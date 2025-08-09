#!/usr/bin/env python3
"""
Core Parameter Validator
Ensure data quality in 10-param model
"""

import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Tuple

class CoreParamValidator:
    """Validate core parameter data quality"""
    
    RULES = {
        'student_id': {
            'type': 'regex',
            'pattern': r'^s10\d{3,4}$',
            'required': True
        },
        'primary_teacher': {
            'type': 'string',
            'required': True,
            'min_length': 2
        },
        'session_teacher': {
            'type': 'string',
            'required': True,
            'min_length': 2
        },
        'lesson_topic': {
            'type': 'string',
            'required': False,  # Can be missing
            'min_length': 3
        },
        'progress_status': {
            'type': 'enum',
            'values': ['Completed', 'InProgress', 'NotStarted', 'Unknown'],
            'required': True
        },
        'session_date': {
            'type': 'date',
            'min_date': '2024-01-01',
            'max_date': '2025-12-31',
            'required': True
        },
        'session_sequence': {
            'type': 'integer',
            'min_value': 0,
            'max_value': 100,
            'required': True
        },
        'program_code': {
            'type': 'enum',
            'values': ['AI-1', 'AI-2', 'W-1', 'W-2', 'W-3', 'BBD', 'BBP', 'BBW', 'FD-1', 'FD-2', 'JC'],
            'required': True
        },
        'attendance_status': {
            'type': 'enum',
            'values': ['Attended', 'Absent', 'No Class', 'Not Marked', 'In Break', 'Off'],
            'required': True
        },
        'data_confidence': {
            'type': 'float',
            'min_value': 0.0,
            'max_value': 1.0,
            'required': True
        }
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_records': 0,
            'valid_records': 0,
            'records_with_errors': 0,
            'records_with_warnings': 0,
            'field_errors': {},
            'field_warnings': {}
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate entire dataframe"""
        self.stats['total_records'] = len(df)
        
        for idx, row in df.iterrows():
            record_errors, record_warnings = self.validate_record(row.to_dict())
            
            if record_errors:
                self.stats['records_with_errors'] += 1
                for error in record_errors:
                    self.errors.append(f"Row {idx}: {error}")
            
            if record_warnings:
                self.stats['records_with_warnings'] += 1
                for warning in record_warnings:
                    self.warnings.append(f"Row {idx}: {warning}")
        
        self.stats['valid_records'] = self.stats['total_records'] - self.stats['records_with_errors']
        
        return len(self.errors) == 0, self.stats
    
    def validate_record(self, record: Dict) -> Tuple[List[str], List[str]]:
        """Validate single record"""
        errors = []
        warnings = []
        
        # Validate each field
        for field, rules in self.RULES.items():
            if field not in record:
                if rules['required']:
                    errors.append(f"Missing required field: {field}")
                continue
            
            value = record[field]
            
            # Check required
            if rules['required'] and pd.isna(value):
                errors.append(f"{field}: Required field is empty")
                continue
            
            # Skip validation for null optional fields
            if not rules['required'] and pd.isna(value):
                continue
            
            # Type validation
            if rules['type'] == 'regex':
                if not re.match(rules['pattern'], str(value)):
                    errors.append(f"{field}: Invalid format '{value}'")
            
            elif rules['type'] == 'enum':
                if value not in rules['values']:
                    errors.append(f"{field}: Invalid value '{value}'")
            
            elif rules['type'] == 'date':
                try:
                    date_val = pd.to_datetime(value)
                    if 'min_date' in rules and date_val < pd.to_datetime(rules['min_date']):
                        errors.append(f"{field}: Date {value} before minimum {rules['min_date']}")
                    if 'max_date' in rules and date_val > pd.to_datetime(rules['max_date']):
                        errors.append(f"{field}: Date {value} after maximum {rules['max_date']}")
                except:
                    errors.append(f"{field}: Invalid date format '{value}'")
            
            elif rules['type'] == 'integer':
                try:
                    int_val = int(value)
                    if 'min_value' in rules and int_val < rules['min_value']:
                        warnings.append(f"{field}: Value {int_val} below minimum {rules['min_value']}")
                    if 'max_value' in rules and int_val > rules['max_value']:
                        warnings.append(f"{field}: Value {int_val} above maximum {rules['max_value']}")
                except:
                    errors.append(f"{field}: Invalid integer '{value}'")
            
            elif rules['type'] == 'float':
                try:
                    float_val = float(value)
                    if 'min_value' in rules and float_val < rules['min_value']:
                        errors.append(f"{field}: Value {float_val} below minimum {rules['min_value']}")
                    if 'max_value' in rules and float_val > rules['max_value']:
                        errors.append(f"{field}: Value {float_val} above maximum {rules['max_value']}")
                except:
                    errors.append(f"{field}: Invalid float '{value}'")
            
            elif rules['type'] == 'string':
                if 'min_length' in rules and len(str(value)) < rules['min_length']:
                    warnings.append(f"{field}: Too short (min {rules['min_length']} chars)")
        
        # Logical validations
        if record.get('attendance_status') == 'Absent' and record.get('progress_status') == 'Completed':
            warnings.append("Progress marked as Completed but student was Absent")
        
        if record.get('attendance_status') == 'Attended' and pd.isna(record.get('lesson_topic')):
            warnings.append("Student attended but no lesson topic recorded")
        
        if record.get('data_confidence', 0) < 0.5:
            warnings.append(f"Low data confidence: {record.get('data_confidence', 0):.2f}")
        
        return errors, warnings
    
    def generate_validation_report(self) -> str:
        """Generate validation report"""
        report = f"""
# Core Parameter Validation Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary
- Total Records: {self.stats['total_records']:,}
- Valid Records: {self.stats['valid_records']:,} ({self.stats['valid_records']/self.stats['total_records']*100:.1f}%)
- Records with Errors: {self.stats['records_with_errors']:,}
- Records with Warnings: {self.stats['records_with_warnings']:,}

## Validation Results
"""
        
        if len(self.errors) == 0:
            report += "✅ No critical errors found!\n"
        else:
            report += f"❌ {len(self.errors)} errors found:\n"
            for error in self.errors[:10]:  # Show first 10
                report += f"  - {error}\n"
            if len(self.errors) > 10:
                report += f"  ... and {len(self.errors) - 10} more\n"
        
        if len(self.warnings) > 0:
            report += f"\n⚠️ {len(self.warnings)} warnings:\n"
            for warning in self.warnings[:10]:  # Show first 10
                report += f"  - {warning}\n"
            if len(self.warnings) > 10:
                report += f"  ... and {len(self.warnings) - 10} more\n"
        
        return report

if __name__ == "__main__":
    # Load core parameters
    df = pd.read_csv("data/core_params/telebort_core_params_20250809.csv")
    
    # Validate
    validator = CoreParamValidator()
    is_valid, stats = validator.validate_dataframe(df)
    
    # Generate report
    report = validator.generate_validation_report()
    
    # Save report
    with open("data/core_params/validation_report.md", 'w') as f:
        f.write(report)
    
    print(report)
    
    if is_valid:
        print("\n✅ Validation passed!")
    else:
        print(f"\n❌ Validation failed with {len(validator.errors)} errors")