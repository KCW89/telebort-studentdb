#!/usr/bin/env python3
"""
Deep Cleanup Script
Archive and remove deprecated code after 10-param migration
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

class DeepCleaner:
    """Deep clean deprecated files and code"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.archive_dir = f"archive/{datetime.now().strftime('%Y%m%d')}_pre_10param"
        self.stats = {
            'files_archived': 0,
            'files_deleted': 0,
            'directories_removed': 0,
            'space_freed_mb': 0
        }
        
        # Files to archive/delete
        self.deprecated_scripts = [
            'scripts/analyze_field_relationships.py',
            'scripts/analyze_final_coverage.py',
            'scripts/analyze_lesson_topics.py',
            'scripts/analyze_maximum_coverage.py',
            'scripts/analyze_missing_topics.py',
            'scripts/apply_predictive_models.py',
            'scripts/deep_pattern_analysis.py',
            'scripts/enhance_with_inference.py',
            'scripts/enhance_with_master_index.py',
            'scripts/maximize_coverage.py',
            'scripts/run_complete_enhancement.py',
            'scripts/xgboost_ml_enhancement.py',
            'scripts/advanced_ml_models.py',
            'scripts/auto_correct_lessons.py',
            'scripts/check_enhanced_quality.py',
            'scripts/simple_validation_engine.py',
            'scripts/final_validation_report.py',
            'scripts/batches_to_vertical_csv.py',
            'scripts/sheets_to_vertical_csv.py',
            'scripts/upload_to_sheets_batch.py',
            'scripts/ml_to_google_sheets.py',
            'scripts/analyze_all_parameters.py'
        ]
        
        self.deprecated_data = [
            'data/vertical_csv/telebort_sessions_enhanced_*.csv',
            'data/vertical_csv/telebort_sessions_final_*.csv',
            'data/vertical_csv/telebort_maximum_coverage_*.csv',
            'data/vertical_csv/telebort_predictive_enhanced_*.csv',
            'data/vertical_csv/telebort_ml_enhanced_*.csv',
            'data/vertical_csv/telebort_xgboost_enhanced_*.csv',
            'data/vertical_csv/coverage_audit_*.json',
            'data/vertical_csv/field_analysis_report_*.json',
            'data/vertical_csv/predictive_*.json',
            'data/vertical_csv/ml_enhancement_summary.json',
            'data/vertical_csv/first_batch.json',
            'data/validation/*.csv',
            'data/validation/*.json'
        ]
        
        self.deprecated_docs = [
            'data/vertical_csv/ENHANCEMENT_SUMMARY.md',
            'data/vertical_csv/FINAL_ML_ACHIEVEMENT_REPORT.md',
            'data/vertical_csv/MAXIMUM_COVERAGE_REPORT.md',
            'data/vertical_csv/PREDICTIVE_MODELING_ACHIEVEMENT.md',
            'data/vertical_csv/ml_to_sheets_implementation.md',
            'FINAL_XGBOOST_ACHIEVEMENT.md',
            'ML_METHODS_SUMMARY.md'
        ]
        
        self.directories_to_remove = [
            'database/',  # SQLAlchemy implementation
            'data/validation/'  # Old validation data
        ]
    
    def create_archive(self):
        """Create archive directory structure"""
        if not self.dry_run:
            Path(f"{self.archive_dir}/scripts").mkdir(parents=True, exist_ok=True)
            Path(f"{self.archive_dir}/data").mkdir(parents=True, exist_ok=True)
            Path(f"{self.archive_dir}/docs").mkdir(parents=True, exist_ok=True)
            Path(f"{self.archive_dir}/database").mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Archive directory: {self.archive_dir}")
    
    def archive_file(self, file_path, category):
        """Archive a single file"""
        if Path(file_path).exists():
            size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            
            if self.dry_run:
                print(f"  [DRY RUN] Would archive: {file_path} ({size_mb:.2f} MB)")
            else:
                dest = f"{self.archive_dir}/{category}/{Path(file_path).name}"
                shutil.move(file_path, dest)
                print(f"  ✓ Archived: {file_path} → {dest}")
            
            self.stats['files_archived'] += 1
            self.stats['space_freed_mb'] += size_mb
            return True
        return False
    
    def clean_scripts(self):
        """Archive deprecated scripts"""
        print("\n🧹 Cleaning deprecated scripts...")
        
        for script in self.deprecated_scripts:
            self.archive_file(script, 'scripts')
    
    def clean_data(self):
        """Archive old data files"""
        print("\n🧹 Cleaning deprecated data files...")
        
        for pattern in self.deprecated_data:
            for file in Path('.').glob(pattern):
                self.archive_file(str(file), 'data')
    
    def clean_docs(self):
        """Archive old documentation"""
        print("\n🧹 Cleaning deprecated documentation...")
        
        for doc in self.deprecated_docs:
            self.archive_file(doc, 'docs')
    
    def remove_directories(self):
        """Remove entire deprecated directories"""
        print("\n🧹 Removing deprecated directories...")
        
        for directory in self.directories_to_remove:
            if Path(directory).exists():
                size_mb = sum(f.stat().st_size for f in Path(directory).rglob('*') if f.is_file()) / (1024 * 1024)
                
                if self.dry_run:
                    print(f"  [DRY RUN] Would remove: {directory} ({size_mb:.2f} MB)")
                else:
                    # Archive first
                    dest = f"{self.archive_dir}/{Path(directory).name}"
                    shutil.move(directory, dest)
                    print(f"  ✓ Removed: {directory} → {dest}")
                
                self.stats['directories_removed'] += 1
                self.stats['space_freed_mb'] += size_mb
    
    def create_archive_readme(self):
        """Create README for archive"""
        readme = f"""
# Archived: Pre-10-Parameter Implementation
Date: {datetime.now().strftime('%Y-%m-%d')}
Reason: Migrated to simplified 10-parameter model

## What's Archived
- {self.stats['files_archived']} deprecated scripts
- {self.stats['directories_removed']} directories
- {self.stats['space_freed_mb']:.1f} MB of data

## Why Archived
- Reduced parameters from 24 to 10 (58% reduction)
- ML enhancements already applied (66.8% coverage achieved)
- Moved from database to CSV/Google Sheets
- Simplified validation logic

## How to Restore
```bash
# Restore specific file
cp archive/{datetime.now().strftime('%Y%m%d')}_pre_10param/scripts/file.py scripts/

# Restore everything
cp -r archive/{datetime.now().strftime('%Y%m%d')}_pre_10param/* .

# Or use git
git checkout 0586b5c  # Last commit before cleanup
```

## New Implementation
See `/scripts/core_params/` for the new 10-parameter system
"""
        
        if not self.dry_run:
            with open(f"{self.archive_dir}/README.md", 'w') as f:
                f.write(readme)
        
        print(f"\n📝 Archive README created")
    
    def generate_cleanup_report(self):
        """Generate cleanup report"""
        report = f"""
# DEEP CLEANUP REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Mode: {'DRY RUN' if self.dry_run else 'EXECUTED'}

## Statistics
- Files Archived: {self.stats['files_archived']}
- Files Deleted: {self.stats['files_deleted']}
- Directories Removed: {self.stats['directories_removed']}
- Space Freed: {self.stats['space_freed_mb']:.1f} MB

## Archive Location
{self.archive_dir}/

## Files Cleaned
### Scripts ({len(self.deprecated_scripts)} files)
- ML enhancement scripts
- Data validation scripts
- Conversion utilities
- Analysis tools

### Data Files
- Intermediate CSVs
- Validation reports
- ML model outputs

### Documentation
- Old implementation guides
- ML achievement reports
- Enhancement summaries

## Directories Removed
- database/ (SQLAlchemy implementation)
- data/validation/ (Old validation data)

## Remaining Structure
/scripts/
  /core_params/  # New 10-param implementation
  batch_processor.py
  enhanced_data_processor.py
  generate_reports.py

/data/
  /core_params/  # Consolidated data
  /raw/batches/  # Original JSON batches
  
/reports/  # Student reports (unchanged)

## Next Steps
1. Commit cleanup changes
2. Push to repository
3. Update documentation
4. Train team on new structure
"""
        
        # Save report
        report_file = f"CLEANUP_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📊 Cleanup report saved to: {report_file}")
        
        return report
    
    def run_cleanup(self):
        """Execute the cleanup"""
        print("🚀 DEEP CLEANUP PROCESS")
        print("=" * 60)
        
        if self.dry_run:
            print("⚠️ DRY RUN MODE - No files will be actually moved/deleted")
        else:
            print("⚡ LIVE MODE - Files will be archived/deleted")
        
        # Create archive
        self.create_archive()
        
        # Clean different categories
        self.clean_scripts()
        self.clean_data()
        self.clean_docs()
        self.remove_directories()
        
        # Create documentation
        self.create_archive_readme()
        report = self.generate_cleanup_report()
        
        print("\n" + "=" * 60)
        print("✅ CLEANUP COMPLETE!")
        print(f"📊 {self.stats['files_archived']} files archived")
        print(f"💾 {self.stats['space_freed_mb']:.1f} MB freed")
        
        if self.dry_run:
            print("\n⚠️ This was a DRY RUN. To execute cleanup, run with dry_run=False")
        
        return self.stats

if __name__ == "__main__":
    import sys
    
    # Check for --execute flag
    dry_run = '--execute' not in sys.argv
    
    cleaner = DeepCleaner(dry_run=dry_run)
    stats = cleaner.run_cleanup()
    
    if dry_run:
        print("\n💡 To execute cleanup, run: python scripts/cleanup/deep_clean.py --execute")