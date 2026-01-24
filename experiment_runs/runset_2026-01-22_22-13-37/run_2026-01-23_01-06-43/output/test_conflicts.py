#!/usr/bin/env python3
"""
Test script to create file conflicts and ambiguous cases for our file organizer.
This will help us test the interactive features Alice and I built together.
"""

import os
import tempfile
import shutil
from pathlib import Path

def create_test_conflicts():
    """Create a test directory with various conflict scenarios."""
    # Create a temporary test directory
    test_dir = Path("/tmp/cc-exp/run_2026-01-23_01-06-43/output/conflict_tests")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    print(f"Creating test conflicts in: {test_dir}")

    # Scenario 1: Naming conflicts when organizing
    (test_dir / "script.py").write_text("# Original script")

    # Create a 'code' subdirectory with existing content
    code_dir = test_dir / "code"
    code_dir.mkdir()
    (code_dir / "script.py").write_text("# Existing script in code directory")

    # Scenario 2: Ambiguous file types
    (test_dir / "data_analysis.R").write_text("# R script - could be code or data")
    (test_dir / "config.json").write_text('{"setting": "value"}')
    (test_dir / "README").write_text("Documentation without extension")
    (test_dir / "Makefile").write_text("build:\n\techo 'building'")

    # Scenario 3: Files that could fit multiple categories
    (test_dir / "presentation.html").write_text("<html><body>Slideshow</body></html>")
    (test_dir / "data.xml").write_text("<data><item>value</item></data>")
    (test_dir / "notes.md").write_text("# Meeting Notes\n\nSome important stuff")

    # Scenario 4: Very large files (simulated)
    large_content = "x" * 1000000  # 1MB of content
    (test_dir / "big_dataset.csv").write_text("name,value\n" + large_content)

    print("✅ Created test scenarios:")
    print("  - Naming conflict: script.py exists in both root and code/")
    print("  - Ambiguous extensions: .R, .json, README, Makefile")
    print("  - Multi-category files: .html, .xml, .md")
    print("  - Large file: big_dataset.csv")
    print(f"\nRun: python file_organizer.py organize {test_dir} --interactive")

    return test_dir

if __name__ == "__main__":
    test_dir = create_test_conflicts()
    print(f"\n🚀 Test directory ready: {test_dir}")
    print("\nTry these commands:")
    print(f"  python file_organizer.py report {test_dir}")
    print(f"  python file_organizer.py organize {test_dir} --dry-run")
    print(f"  python file_organizer.py organize {test_dir} --interactive")