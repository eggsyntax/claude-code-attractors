#!/usr/bin/env python3
"""
Test example showing how the project organizer works

This creates some mock project structures and demonstrates the scanner
"""

import os
import tempfile
from pathlib import Path
from project_organizer import ProjectOrganizer

def create_mock_projects():
    """Create some mock project structures for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Creating mock projects in: {temp_dir}")

    # Python project
    python_proj = temp_dir / "my_python_app"
    python_proj.mkdir()
    (python_proj / "requirements.txt").write_text("requests==2.28.0\nflask==2.2.0\n")
    (python_proj / "main.py").write_text("print('Hello from Python!')")

    # Node.js project
    node_proj = temp_dir / "my_web_app"
    node_proj.mkdir()
    (node_proj / "package.json").write_text('{"name": "my-app", "version": "1.0.0"}')
    (node_proj / "index.js").write_text("console.log('Hello from Node!');")

    # Rust project
    rust_proj = temp_dir / "my_rust_cli"
    rust_proj.mkdir()
    (rust_proj / "Cargo.toml").write_text('[package]\nname = "my-cli"\nversion = "0.1.0"')
    (rust_proj / "main.rs").write_text('fn main() { println!("Hello from Rust!"); }')

    # Non-project directory (should be ignored)
    other_dir = temp_dir / "random_files"
    other_dir.mkdir()
    (other_dir / "some_file.txt").write_text("Just a text file")

    return temp_dir

if __name__ == "__main__":
    # Create test projects
    test_dir = create_mock_projects()

    # Test the organizer
    organizer = ProjectOrganizer()
    projects = organizer.scan_directory(str(test_dir))

    print("\nDiscovered projects:")
    for project in projects:
        print(f"  {project.name:15} ({project.type}) - {project.dependencies_file}")

    print(f"\nTest directory: {test_dir}")
    print("You can also run:")
    print(f"  python project_organizer.py scan {test_dir}")
    print(f"  python project_organizer.py list")