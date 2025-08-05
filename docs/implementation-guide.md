# Implementation Guide

## Overview

This guide details the technical implementation of the Telebort student report generation system. The system automatically syncs data from Google Sheets via Zapier MCP and generates objective, observational student reports following our "blood test model" philosophy.

## Architecture

```
Google Sheets → Zapier MCP → Python Processing → Markdown Reports → Git Repository
     ↑                                                                      ↓
     └─────────────────── Weekly Schedule ←────────────────────────────────┘
```

## Directory Structure

```
telebort-studentdb/
├── docs/
│   ├── report-design-philosophy.md
│   └── implementation-guide.md
├── scripts/
│   ├── sync_sheets.py          # Fetches data via Zapier MCP
│   ├── process_data.py         # Transforms raw data
│   ├── generate_reports.py     # Creates/updates markdown
│   └── run_weekly_sync.py      # Orchestrates the flow
├── reports/
│   ├── s10769.md              # One file per student
│   ├── s10777.md              # Living documents
│   └── ...
├── templates/
│   └── student_report.md       # Report template
└── logs/
    └── sync_history.log        # Execution logs
```

## Data Source

### Google Sheets Structure
- **Spreadsheet ID**: `1zbw7hLSa-5k83T0d6KrD-eiZv5nM855oYHV_B-tslbU`
- **Worksheet ID**: `891163674`

### Column Layout
Fixed columns (A-H):
- A: Student Name
- B: Status
- C: Student ID
- D: Current Program
- E: Day
- F: StartTime
- G: EndTime
- H: Teacher

Repeating pattern (I onwards, every 5 columns):
1. Date
2. Session
3. Lesson + Link
4. Attendance
5. Progress

## Component Details

### 1. sync_sheets.py

**Purpose**: Connects to Google Sheets via Zapier MCP and fetches all student data.

**Key Functions**:
```python
class SheetsSyncManager:
    def __init__(self):
        """Initialize with spreadsheet configuration"""
        
    def fetch_all_students(self):
        """Fetch all student records from Google Sheets"""
        
    def parse_student_sessions(self, row_data):
        """Extract session data from repeating columns"""
```

**Implementation Notes**:
- Uses Zapier MCP tools for authentication
- Handles pagination for large datasets
- Saves raw data for debugging
- Returns structured JSON

### 2. process_data.py

**Purpose**: Transforms raw data into report-ready format without inference.

**Key Functions**:
```python
class DataProcessor:
    def process_student(self, raw_data):
        """Process one student's data"""
        
    def extract_current_status(self, student_data):
        """Get latest non-empty session info"""
        
    def build_learning_journey(self, session_data):
        """Create chronological session list"""
        
    def calculate_attendance(self, journey_data):
        """Count attendance statistics"""
```

**Processing Rules**:
- No interpretation or inference
- Handle missing data gracefully
- Preserve all available information
- Simple arithmetic only (counts, percentages)

### 3. generate_reports.py

**Purpose**: Generates or updates markdown reports using living document approach.

**Key Functions**:
```python
class ReportGenerator:
    def __init__(self):
        """Load report template"""
        
    def generate_report(self, student_id, processed_data):
        """Create or update student report"""
        
    def format_markdown_table(self, journey_data):
        """Convert journey to markdown table"""
        
    def update_living_document(self, existing_content, new_data):
        """Smart update of existing report"""
```

**Update Strategy**:
- Preserve existing file if no changes
- Add new sessions to top of journey table
- Recalculate all statistics
- Update metadata (last sync time)

### 4. run_weekly_sync.py

**Purpose**: Orchestrates the complete sync process with error handling.

**Flow**:
1. Setup logging
2. Fetch data from Google Sheets
3. Process each student
4. Generate/update reports
5. Commit to git
6. Log summary

**Error Handling**:
- Continue on individual student failures
- Log all errors with context
- Send summary notification
- Retry logic for network issues

## Report Template

```markdown
# Student Learning Record - {student_id}
*Generated: {date} | Week {week}/{year}*

## Current Status
- **Program:** {program}
- **Schedule:** {schedule}  
- **Teacher:** {teacher}
- **Latest Session:** {session_num} (as of {session_date})
- **Latest Lesson:** {lesson_title}
- **Latest Status:** {progress_status}

## Learning Journey
| Date | Session | Lesson | Attendance | Progress |
|------|---------|--------|------------|----------|
{journey_table_rows}

## Attendance Summary
- **Total Sessions with Attendance Data:** {total}
- **Attended:** {attended}
- **Absent:** {absent}
- **No Class/Break:** {no_class}
- **Attendance Rate:** {rate}% ({attended}/{total})

---
*This is an automated learning record. For interpretation and recommendations, please consult with the teacher.*
```

## Weekly Sync Process

### Schedule
- **Day**: Sunday
- **Time**: 23:00 (after all classes end)
- **Frequency**: Weekly

### Execution Steps
1. **Pre-sync validation**
   - Check Zapier MCP connection
   - Verify sheet structure hasn't changed
   - Ensure git repo is clean

2. **Data sync**
   - Fetch all student records
   - Validate data completeness
   - Log any anomalies

3. **Processing**
   - Transform each student's data
   - Generate/update reports
   - Track changes

4. **Git operations**
   ```bash
   git add reports/*.md
   git commit -m "Weekly sync: Week {week}/{year} - {count} students updated"
   git push origin cw-data-1
   ```

5. **Post-sync**
   - Generate summary statistics
   - Log execution details
   - Send completion notification

## Error Handling

### Connection Errors
- Retry 3 times with exponential backoff
- Log error and continue with cached data
- Alert administrator

### Data Errors
- Skip malformed records
- Log with student ID for investigation
- Continue processing other students

### File System Errors
- Check disk space before starting
- Handle permission issues gracefully
- Maintain backup of previous reports

## Logging

### Log Format
```
2025-08-05 23:00:01 INFO Starting weekly sync for Week 32/2025
2025-08-05 23:00:05 INFO Fetched 107 student records
2025-08-05 23:00:10 INFO Processing student s10769
2025-08-05 23:00:15 INFO Updated report for s10769
...
2025-08-05 23:05:00 INFO Sync complete: 105/107 students updated
2025-08-05 23:05:01 INFO Git commit successful
```

### Log Retention
- Keep logs for 90 days
- Archive monthly summaries
- Alert on error patterns

## Testing

### Unit Tests
- Test each component in isolation
- Mock Zapier MCP calls
- Verify data transformations

### Integration Tests
- Test complete pipeline with sample data
- Verify report generation
- Check git operations

### Manual Verification
- Review sample reports
- Compare with source data
- Validate calculations

## Deployment

### Local Development
```bash
# Clone repository
git clone [repo-url]
cd telebort-studentdb
git checkout cw-data-1

# Install dependencies
pip install -r requirements.txt

# Run manual sync
python scripts/run_weekly_sync.py
```

### Production Setup
1. Set up scheduled job (cron/GitHub Actions)
2. Configure environment variables
3. Set up monitoring alerts
4. Enable error notifications

### Environment Variables
```
ZAPIER_MCP_TOKEN=xxx
SHEETS_ID=1zbw7hLSa-5k83T0d6KrD-eiZv5nM855oYHV_B-tslbU
WORKSHEET_ID=891163674
LOG_LEVEL=INFO
```

## Monitoring

### Key Metrics
- Sync success rate
- Processing time per student
- Report update count
- Error frequency

### Alerts
- Sync failure
- > 10% student processing errors
- Unexpected data structure changes
- Git push failures

## Maintenance

### Weekly
- Review sync logs
- Check error patterns
- Verify report quality

### Monthly
- Archive old logs
- Review system performance
- Update documentation

### Quarterly
- Review data structure changes
- Optimize performance
- Update dependencies

---

*This guide should be updated whenever the implementation changes significantly.*