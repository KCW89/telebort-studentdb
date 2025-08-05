# Telebort Student Database - Technical Documentation

This repository contains an automated student progress tracking and reporting system for Telebort Academy.

## Overview

The Telebort Student Report System automatically generates individual progress reports for students by:
- Fetching data from Google Sheets via Zapier MCP
- Processing and validating student attendance and progress data
- Generating markdown reports for each student
- Committing updates to Git for version control
- Monitoring system health and data quality

## Quick Start

### Prerequisites
- Python 3.9+
- Git
- Access to Claude Code (for MCP integration)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd telebort-studentdb

# Install dependencies
pip install -r requirements.txt

# Run tests
cd scripts
python test_batch_processor.py
```

### Basic Usage
```bash
# Process all students
cd scripts
python batch_processor.py --start 5 --end 111

# Run weekly sync
python run_weekly_sync.py

# Check system health
python monitoring.py
```

## Documentation

- [Implementation Guide](docs/implementation-guide.md) - Technical architecture and design
- [Deployment Guide](docs/deployment-guide.md) - Setup and operational procedures
- [Report Design Philosophy](docs/report-design-philosophy.md) - Report format and principles

## Key Features

### 🤖 Automated Processing
- Weekly automated sync via GitHub Actions
- Batch processing with configurable sizes
- Retry logic with exponential backoff

### ✅ Data Quality
- Comprehensive validation checks
- Format verification (dates, IDs, values)
- Cross-validation of related fields
- Detailed validation reports

### 📊 Monitoring & Alerts
- Performance metrics tracking
- Error classification and counting
- Health report generation
- Webhook support for external alerts

### 🔄 Flexible Processing
- Process all students or specific ranges
- Handle individual rows or batches
- Manual or automated execution
- Git integration for version control

## Project Structure
```
telebort-studentdb/
├── scripts/              # Python processing scripts
│   ├── batch_processor.py       # Main batch processor
│   ├── run_weekly_sync.py       # Weekly sync orchestrator
│   ├── sync_sheets_mcp.py       # Google Sheets integration
│   ├── data_validator.py        # Data validation
│   └── monitoring.py            # System monitoring
├── reports/              # Generated student reports (*.md)
├── docs/                 # Documentation
├── logs/                 # System logs and metrics
├── templates/            # Report templates
└── .github/workflows/    # GitHub Actions automation
```

## Automation

The system includes GitHub Actions workflows for:
- **Weekly Sync**: Automatic sync every Sunday at 11 PM SGT
- **Manual Sync**: On-demand processing with custom parameters
- **Test Suite**: CI/CD validation on pull requests

## Recent Updates (August 2025)

### Completed Enhancements
1. **MCP Integration**: Updated to use actual Zapier MCP calls in Claude Code
2. **Batch Processing**: Consolidated 8 separate scripts into unified `batch_processor.py`
3. **Error Handling**: Implemented retry logic with exponential backoff
4. **Data Validation**: Added comprehensive validation with detailed reporting
5. **Monitoring System**: Created metrics tracking and alert generation
6. **GitHub Actions**: Set up automated workflows for weekly and manual syncs

### System Improvements
- Resolved "missing 6 students" issue (duplicates and header rows)
- All 101 unique students successfully processed
- Production-ready with full automation support

## Support

For detailed setup and troubleshooting, see the [Deployment Guide](docs/deployment-guide.md).

## License

Internal use only - Telebort Academy