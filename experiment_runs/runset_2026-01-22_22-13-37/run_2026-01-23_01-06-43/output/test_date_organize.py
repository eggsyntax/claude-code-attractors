#!/usr/bin/env python3
"""
Test script to create files with different modification dates
for testing the date organization feature.
"""

import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def create_test_files():
    """Create test files with different modification dates."""

    # Create a temporary test directory
    test_dir = Path("/tmp/cc-exp/run_2026-01-23_01-06-43/output/test_date_files")
    test_dir.mkdir(exist_ok=True)

    print(f"Creating test files in: {test_dir}")

    # Define test files with different dates
    test_files = [
        # Recent files (last month)
        ("recent_photo.jpg", datetime.now() - timedelta(days=10)),
        ("recent_document.pdf", datetime.now() - timedelta(days=5)),

        # Files from different months this year
        ("january_report.docx", datetime(2026, 1, 15)),
        ("december_vacation.jpg", datetime(2025, 12, 25)),
        ("summer_project.py", datetime(2025, 7, 4)),

        # Files from different years
        ("old_backup.zip", datetime(2024, 3, 20)),
        ("ancient_notes.txt", datetime(2023, 6, 10)),
        ("really_old_file.doc", datetime(2022, 11, 5)),

        # Files for testing quarters
        ("q1_budget.xlsx", datetime(2025, 2, 14)),  # Q1
        ("q2_review.pptx", datetime(2025, 5, 20)),  # Q2
        ("q3_analysis.csv", datetime(2025, 8, 30)), # Q3
        ("q4_summary.pdf", datetime(2025, 11, 15)), # Q4
    ]

    created_files = []

    for filename, mod_date in test_files:
        file_path = test_dir / filename

        # Create file with some content
        content = f"Test file: {filename}\nCreated for date organization testing.\nModification date: {mod_date}\n"
        file_path.write_text(content)

        # Set the modification time
        timestamp = mod_date.timestamp()
        os.utime(file_path, (timestamp, timestamp))

        created_files.append((filename, mod_date))
        print(f"✓ Created: {filename} (modified: {mod_date.strftime('%Y-%m-%d')})")

    print(f"\nCreated {len(created_files)} test files in {test_dir}")
    print("\nNow you can test the date organization with commands like:")
    print(f"  python file_organizer.py organize {test_dir} --by date --dry-run")
    print(f"  python file_organizer.py organize {test_dir} --by date --date-format quarter --dry-run")
    print(f"  python file_organizer.py report {test_dir}")

    return test_dir, created_files

if __name__ == "__main__":
    create_test_files()