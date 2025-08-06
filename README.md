# Telebort StudentDB

## Overview

Telebort StudentDB is a comprehensive educational data management system for Telebort Academy, designed to track and analyze student progress, attendance, and academic performance across various programming courses including AI/ML, Web Development, and Python programming.

## Features

- **Complete Historical Data Tracking**: Maintains full session history for all students (average 40+ sessions per student)
- **Automated Report Generation**: Creates detailed markdown reports for individual students
- **Teacher-Based Organization**: Segregates data by instructor for easy access
- **Enhanced Data Processing**: Applies intelligent data cleaning and standardization
- **Batch Processing**: Efficiently handles large datasets with parallel processing capabilities

## Project Structure

```
telebort-studentdb/
├── data/                         # All data files
│   ├── raw/                     # Original unprocessed data (gitignored)
│   │   ├── batches/              # Batch JSON files (gitignored)
│   │   └── sheets/               # Google Sheets exports
│   ├── processed/                # Cleaned and processed data
│   │   └── summaries/            # Processing summaries
│   └── sandbox-4.5/              # Analysis scripts and tools
│
├── reports/                      # Original reports with names (gitignored)
├── reports_anonymized/           # Anonymized reports (public)
├── scripts/                      # Processing and utility scripts
├── templates/                    # Report and document templates
├── docs/                         # Documentation
└── logs/                         # Processing and error logs
```

## Key Statistics

- **Total Students**: 107
- **Total Sessions Tracked**: 4,467+
- **Average Sessions per Student**: 41.7
- **Active Teachers**: 13
- **Programs**: AI/ML, Web Development, Python

## Quick Start

1. Process batch data:
   ```bash
   python scripts/batch_processor.py
   ```

2. Generate reports:
   ```bash
   python scripts/generate_reports.py
   ```

## Privacy & Data Protection

This repository follows strict privacy guidelines:

- **Student Names**: All student names have been anonymized in public-facing reports
- **Student IDs**: Uses anonymous ID format (s10XXX) throughout
- **Raw Data**: Original data files containing personal information are gitignored
- **Public Reports**: Only anonymized versions are included in the repository

To generate anonymized reports from original data:
```bash
python scripts/anonymize_reports.py
```

## License

Proprietary to Telebort Academy. All rights reserved.

---
*Last Updated: August 2025*
EOF < /dev/null