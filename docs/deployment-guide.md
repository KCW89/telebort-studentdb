# Telebort Student Report System - Deployment Guide

This guide covers the deployment and operation of the Telebort student report generation system.

## Table of Contents
- [System Overview](#system-overview)
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Configuration](#configuration)
- [Running the System](#running-the-system)
- [Automation Setup](#automation-setup)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## System Overview

The Telebort Student Report System automatically:
1. Fetches student data from Google Sheets via Zapier MCP
2. Processes and validates the data
3. Generates individual markdown reports for each student
4. Commits changes to Git for version control
5. Monitors system health and sends alerts

### Architecture
```
Google Sheets → Zapier MCP → Python Scripts → Markdown Reports → Git
                     ↓
                Monitoring & Validation
```

## Prerequisites

### Required Software
- Python 3.9 or higher
- Git
- Access to Claude Code (for MCP integration)

### Required Access
- Google Sheets containing student data
- Zapier MCP connection configured
- Git repository with write access
- (Optional) Webhook URL for alerts

## Initial Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd telebort-studentdb
git checkout cw-data-1  # Use the designated data branch
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Directory Structure
```
telebort-studentdb/
├── scripts/           # All Python scripts
├── reports/          # Generated student reports
├── logs/            # System logs and metrics
├── docs/            # Documentation
├── templates/       # Report templates
└── .github/         # GitHub Actions workflows
```

### 4. Test Installation
```bash
cd scripts
python test_error_handling.py
python test_batch_processor.py
```

## Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root:
```bash
# Webhook for alerts (optional)
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Git branch for reports
REPORT_BRANCH=cw-data-1
```

### Google Sheets Configuration
The system expects a Google Sheet with:
- **Spreadsheet ID**: `1zbw7hLSa-5k83T0d6KrD-eiZv5nM855oYHV_B-tslbU`
- **Worksheet ID**: `891163674`
- **Structure**: Fixed columns A-H, then repeating 5-column pattern

### MCP Configuration
Ensure Zapier MCP is connected in Claude Code with access to:
- `mcp__zapier__google_sheets_get_many_spreadsheet_rows_advanced`

## Running the System

### Manual Sync Options

#### 1. Process All Students
```bash
cd scripts
python batch_processor.py --start 5 --end 111
```

#### 2. Process Specific Range
```bash
python batch_processor.py --start 25 --end 50 --batch-size 10
```

#### 3. Process Specific Students
```bash
python batch_processor.py --rows 5,10,15,20
```

#### 4. Run Weekly Sync
```bash
python run_weekly_sync.py
```

### Command-Line Options
- `--start`: Starting row (1-indexed)
- `--end`: Ending row (inclusive)
- `--batch-size`: Number of rows per batch (default: 20, max: 50)
- `--rows`: Comma-separated list of specific rows

## Automation Setup

### GitHub Actions

The system includes three automated workflows:

#### 1. Weekly Sync (Automatic)
- **Schedule**: Every Sunday at 11:00 PM SGT
- **File**: `.github/workflows/weekly-sync.yml`
- **Function**: Fetches all data, generates reports, commits changes

#### 2. Manual Sync (On-Demand)
- **Trigger**: Manual via GitHub Actions UI
- **File**: `.github/workflows/manual-sync.yml`
- **Options**:
  - Start/end row range
  - Batch size
  - Specific rows
  - Commit changes option

#### 3. Test Sync (CI/CD)
- **Trigger**: Pull requests affecting scripts
- **File**: `.github/workflows/test-sync.yml`
- **Function**: Validates code changes

### Setting Up GitHub Actions

1. Ensure workflows are in `.github/workflows/`
2. Go to repository Settings → Actions → General
3. Enable "Allow all actions and reusable workflows"
4. Workflows will appear under the Actions tab

### Running Workflows Manually

1. Go to Actions tab in GitHub
2. Select "Manual Student Report Sync"
3. Click "Run workflow"
4. Fill in parameters:
   - Starting row: 5
   - Ending row: 111
   - Batch size: 20
   - Commit changes: true
5. Click "Run workflow"

## Monitoring & Maintenance

### View System Health
```bash
cd scripts
python monitoring.py
```

### Check Logs
```bash
# View sync history
cat logs/sync_history.log

# View alerts
cat logs/alerts.log

# View metrics
cat logs/sync_metrics.json
```

### Validation Reports
After each sync, check for validation issues:
```bash
cd scripts
python data_validator.py
```

### Common Validation Issues
- **Invalid date format**: Should be DD/MM/YYYY
- **Invalid attendance**: Must be one of: Attended, Absent, No Class, Public Holiday
- **Invalid progress**: Must be one of: Completed, In Progress, Not Started, Graduated
- **Missing fields**: Student ID, name, and program are required

## Troubleshooting

### Issue: MCP Connection Failed
**Symptoms**: "MCP not available" warnings
**Solution**: 
1. Ensure running in Claude Code environment
2. Check Zapier MCP is connected
3. Verify spreadsheet/worksheet IDs

### Issue: No Reports Generated
**Symptoms**: Processing completes but no `.md` files created
**Checklist**:
1. Check `reports/` directory exists
2. Verify student IDs are valid (format: s#####)
3. Check logs for specific errors
4. Ensure write permissions

### Issue: Git Commit Failed
**Symptoms**: Reports generated but not committed
**Solution**:
```bash
# Check git status
git status

# Configure git if needed
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Manually commit if needed
git add reports/*.md
git commit -m "Manual sync: student reports"
git push origin cw-data-1
```

### Issue: High Error Rate
**Symptoms**: Many validation errors or processing failures
**Steps**:
1. Run validation separately:
   ```bash
   python data_validator.py
   ```
2. Check specific student data in Google Sheets
3. Review error patterns in logs
4. Consider processing smaller batches

### Issue: Slow Performance
**Symptoms**: Sync takes longer than 5 minutes
**Optimizations**:
1. Reduce batch size (try 10 instead of 20)
2. Process specific ranges instead of all students
3. Check network connectivity
4. Review monitoring metrics for patterns

## Best Practices

### Regular Maintenance
1. **Weekly**: Review sync logs and error counts
2. **Monthly**: Clean up old logs in `logs/` directory
3. **Quarterly**: Review and update validation rules

### Before Major Changes
1. Test in development environment first
2. Create backup of current reports
3. Run validation on sample data
4. Monitor first sync after changes

### Data Quality
1. Regularly review validation reports
2. Fix data issues at source (Google Sheets)
3. Update validation rules as needed
4. Document any data format changes

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review validation reports
3. Consult `docs/implementation-guide.md` for technical details
4. Check GitHub Actions run history for automation issues

## Appendix: Quick Reference

### Key Files
- **Main orchestrator**: `scripts/run_weekly_sync.py`
- **Batch processor**: `scripts/batch_processor.py`
- **Data validator**: `scripts/data_validator.py`
- **Monitoring**: `scripts/monitoring.py`
- **MCP integration**: `scripts/sync_sheets_mcp.py`

### Key Commands
```bash
# Process all students
python batch_processor.py --start 5 --end 111

# Run weekly sync
python run_weekly_sync.py

# Check system health
python monitoring.py

# Validate data quality
python data_validator.py

# Test specific batch
python test_batch_processor.py
```

### Log Locations
- Sync history: `logs/sync_history.log`
- Alerts: `logs/alerts.log`
- Metrics: `logs/sync_metrics.json`
- GitHub Actions: Actions tab in repository