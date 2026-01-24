#!/usr/bin/env python3
"""
Project Organizer - A CLI tool for managing development projects

This tool helps developers:
- Discover projects in a directory tree
- View project status and metadata
- Perform common project operations

Usage:
    python project_organizer.py scan [directory]
    python project_organizer.py list
    python project_organizer.py status <project_name>
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Project:
    """Represents a development project"""
    name: str
    path: str
    type: str  # 'python', 'node', 'rust', 'git', 'other'
    last_modified: str
    git_status: Optional[str] = None
    dependencies_file: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class ProjectDetector:
    """Detects different types of development projects"""

    PROJECT_INDICATORS = {
        'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
        'node': ['package.json', 'yarn.lock', 'package-lock.json'],
        'rust': ['Cargo.toml'],
        'go': ['go.mod', 'go.sum'],
        'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
        'ruby': ['Gemfile', 'Rakefile'],
    }

    def detect_project_type(self, path: Path) -> str:
        """Determine the project type based on files present"""
        files_in_dir = {f.name for f in path.iterdir() if f.is_file()}

        for project_type, indicators in self.PROJECT_INDICATORS.items():
            if any(indicator in files_in_dir for indicator in indicators):
                return project_type

        # Check if it's a git repository
        if (path / '.git').exists():
            return 'git'

        return 'other'

    def get_git_status(self, path: Path) -> Optional[str]:
        """Get git status for a project if it's a git repository"""
        if not (path / '.git').exists():
            return None

        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if not result.stdout.strip():
                    return 'clean'
                return f'{len(lines)} changes'
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        return 'unknown'

    def find_dependency_file(self, path: Path, project_type: str) -> Optional[str]:
        """Find the main dependency file for a project type"""
        dep_files = {
            'python': ['requirements.txt', 'pyproject.toml', 'Pipfile'],
            'node': ['package.json'],
            'rust': ['Cargo.toml'],
            'go': ['go.mod'],
            'java': ['pom.xml', 'build.gradle'],
            'ruby': ['Gemfile'],
        }

        if project_type in dep_files:
            for dep_file in dep_files[project_type]:
                if (path / dep_file).exists():
                    return dep_file
        return None


class ProjectOrganizer:
    """Main class for organizing and managing projects"""

    def __init__(self, config_dir: str = "~/.project_organizer"):
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(exist_ok=True)
        self.projects_file = self.config_dir / "projects.json"
        self.detector = ProjectDetector()

    def scan_directory(self, directory: str, max_depth: int = 3) -> List[Project]:
        """Scan a directory for development projects"""
        projects = []
        start_path = Path(directory).expanduser().resolve()

        def scan_recursive(path: Path, current_depth: int = 0):
            if current_depth > max_depth:
                return

            try:
                for item in path.iterdir():
                    if not item.is_dir():
                        continue

                    # Skip hidden directories and common non-project directories
                    if item.name.startswith('.') or item.name in {'node_modules', '__pycache__', 'target', 'build', 'dist'}:
                        continue

                    project_type = self.detector.detect_project_type(item)
                    if project_type != 'other':
                        # Get last modified time
                        try:
                            last_modified = datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        except OSError:
                            last_modified = "unknown"

                        project = Project(
                            name=item.name,
                            path=str(item),
                            type=project_type,
                            last_modified=last_modified,
                            git_status=self.detector.get_git_status(item),
                            dependencies_file=self.detector.find_dependency_file(item, project_type)
                        )
                        projects.append(project)

                        # Don't recurse into detected projects
                        continue

                    # Recurse into subdirectories
                    scan_recursive(item, current_depth + 1)

            except PermissionError:
                print(f"Permission denied: {path}", file=sys.stderr)
            except OSError as e:
                print(f"Error accessing {path}: {e}", file=sys.stderr)

        scan_recursive(start_path)
        return projects

    def save_projects(self, projects: List[Project]):
        """Save projects to the config file"""
        with open(self.projects_file, 'w') as f:
            json.dump([p.to_dict() for p in projects], f, indent=2)

    def load_projects(self) -> List[Project]:
        """Load projects from the config file"""
        if not self.projects_file.exists():
            return []

        try:
            with open(self.projects_file, 'r') as f:
                data = json.load(f)
                return [Project(**p) for p in data]
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading projects: {e}", file=sys.stderr)
            return []


def main():
    """Main CLI entry point"""
    organizer = ProjectOrganizer()

    if len(sys.argv) < 2:
        print("Usage: python project_organizer.py <command> [args]")
        print("Commands:")
        print("  scan <directory>   - Scan directory for projects")
        print("  list              - List discovered projects")
        print("  status <name>     - Show detailed project status")
        return

    command = sys.argv[1]

    if command == "scan":
        directory = sys.argv[2] if len(sys.argv) > 2 else "."
        print(f"Scanning {directory} for projects...")

        projects = organizer.scan_directory(directory)
        organizer.save_projects(projects)

        print(f"Found {len(projects)} projects:")
        for project in projects:
            status_info = f" [{project.git_status}]" if project.git_status else ""
            print(f"  {project.name} ({project.type}){status_info}")

    elif command == "list":
        projects = organizer.load_projects()
        if not projects:
            print("No projects found. Run 'scan <directory>' first.")
            return

        print(f"Found {len(projects)} projects:")
        for project in projects:
            status_info = f" [{project.git_status}]" if project.git_status else ""
            print(f"  {project.name:20} {project.type:10} {status_info}")

    elif command == "status":
        if len(sys.argv) < 3:
            print("Usage: python project_organizer.py status <project_name>")
            return

        project_name = sys.argv[2]
        projects = organizer.load_projects()

        project = next((p for p in projects if p.name == project_name), None)
        if not project:
            print(f"Project '{project_name}' not found.")
            return

        print(f"Project: {project.name}")
        print(f"Path: {project.path}")
        print(f"Type: {project.type}")
        print(f"Last Modified: {project.last_modified}")
        if project.git_status:
            print(f"Git Status: {project.git_status}")
        if project.dependencies_file:
            print(f"Dependencies: {project.dependencies_file}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()