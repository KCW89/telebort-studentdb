# Scripts Directory

This directory contains the core processing and utility scripts for the Telebort StudentDB system.

## Core Processing Scripts

### `batch_processor.py`
Main batch processing engine that handles all 18 batches of student data. Processes complete 338-column data from Google Sheets and generates comprehensive reports.

### `enhanced_data_processor.py`
Data cleaning and standardization engine that:
- Fixes teacher name inconsistencies
- Normalizes progress ratings
- Extracts submission URLs
- Tracks data quality metrics

### `generate_reports.py`
Generates individual markdown reports for each student from processed batch data.

### `anonymize_reports.py`
Creates anonymized versions of student reports by removing real names, suitable for public repository.

## Data Sync & Validation

### `sync_sheets.py` / `sync_sheets_mcp.py`
Synchronizes data from Google Sheets using MCP (Model Context Protocol) integration.

### `sync_all_students.py`
Batch synchronization for all student records.

### `full_sync.py`
Complete system synchronization including all data sources.

### `data_validator.py`
Validates data integrity and consistency across the system.

### `verify_student_count.py`
Verifies that all 107 students are properly tracked and processed.

## Monitoring & Utilities

### `monitoring.py`
System monitoring and performance tracking utilities.

## Usage Examples

```bash
# Process all batch data
python batch_processor.py

# Generate student reports
python generate_reports.py

# Anonymize reports for public release
python anonymize_reports.py

# Validate data integrity
python data_validator.py
```

## Notes

- All scripts assume Python 3.7+ environment
- MCP integration requires proper Google Sheets API configuration
- Raw data files containing personal information should never be committed