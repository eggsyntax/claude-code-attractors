#!/usr/bin/env python3
"""
Smart File Organizer CLI Tool

A collaborative project by Alice and Bob to create an intelligent file organization utility.
Automatically sorts files in directories based on configurable criteria.
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class FileOrganizer:
    """
    Core file organization logic with support for multiple organization strategies.
    """

    def __init__(self, target_directory: str, dry_run: bool = True):
        self.target_directory = Path(target_directory)
        self.dry_run = dry_run
        self.file_stats = {}

    def scan_files(self) -> List[Path]:
        """
        Scan the target directory and return a list of files to organize.
        Excludes directories and hidden files by default.
        """
        if not self.target_directory.exists():
            raise FileNotFoundError(f"Directory not found: {self.target_directory}")

        files = []
        for item in self.target_directory.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                files.append(item)
                # Gather file stats for organization decisions
                stat = item.stat()
                self.file_stats[item] = {
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'extension': item.suffix.lower()
                }

        print(f"Found {len(files)} files to organize")
        return files

    def organize_by_type(self, files: List[Path]) -> Dict[str, List[Path]]:
        """
        Group files by their file extensions.
        """
        type_groups = {}

        # Define common file type categories
        categories = {
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'},
            'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'},
            'spreadsheets': {'.xls', '.xlsx', '.csv', '.ods'},
            'presentations': {'.ppt', '.pptx', '.odp'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
            'code': {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php'},
            'media': {'.mp4', '.avi', '.mkv', '.mp3', '.wav', '.flac'}
        }

        for file in files:
            extension = self.file_stats[file]['extension']

            # Find the category for this file type
            category = 'misc'
            for cat_name, extensions in categories.items():
                if extension in extensions:
                    category = cat_name
                    break

            if category not in type_groups:
                type_groups[category] = []
            type_groups[category].append(file)

        return type_groups

    def create_organization_plan(self, files: List[Path], strategy: str = 'type') -> Dict[str, List[Path]]:
        """
        Create a plan for organizing files based on the chosen strategy.
        """
        if strategy == 'type':
            return self.organize_by_type(files)
        else:
            raise ValueError(f"Unknown organization strategy: {strategy}")

    def execute_plan(self, plan: Dict[str, List[Path]]) -> None:
        """
        Execute the organization plan, creating directories and moving files.
        """
        for category, file_list in plan.items():
            if not file_list:
                continue

            # Create category directory
            category_dir = self.target_directory / category

            if self.dry_run:
                print(f"\n[DRY RUN] Would create directory: {category_dir}")
                for file in file_list:
                    new_path = category_dir / file.name
                    print(f"  Would move: {file} -> {new_path}")
            else:
                category_dir.mkdir(exist_ok=True)
                print(f"\nCreated directory: {category_dir}")

                for file in file_list:
                    new_path = category_dir / file.name
                    try:
                        shutil.move(str(file), str(new_path))
                        print(f"  Moved: {file} -> {new_path}")
                    except Exception as e:
                        print(f"  Error moving {file}: {e}")


def main():
    """
    CLI entry point with argument parsing and main execution flow.
    """
    parser = argparse.ArgumentParser(
        description="Smart File Organizer - Automatically organize files in directories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python organizer.py /path/to/messy/directory
  python organizer.py . --strategy type --execute
  python organizer.py ~/Downloads --dry-run
        """
    )

    parser.add_argument(
        'directory',
        help='Directory to organize'
    )

    parser.add_argument(
        '--strategy',
        choices=['type'],
        default='type',
        help='Organization strategy to use (default: type)'
    )

    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually move files (default is dry-run mode)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Show what would be done without making changes (default)'
    )

    args = parser.parse_args()

    # Handle the dry-run logic
    dry_run = not args.execute

    try:
        organizer = FileOrganizer(args.directory, dry_run=dry_run)

        # Scan for files
        files = organizer.scan_files()
        if not files:
            print("No files to organize!")
            return

        # Create organization plan
        plan = organizer.create_organization_plan(files, args.strategy)

        # Show summary
        print(f"\nOrganization Plan ({args.strategy} strategy):")
        for category, file_list in plan.items():
            print(f"  {category}: {len(file_list)} files")

        # Execute the plan
        organizer.execute_plan(plan)

        if dry_run:
            print(f"\n[DRY RUN] Use --execute to actually move files")
        else:
            print(f"\nOrganization complete!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()