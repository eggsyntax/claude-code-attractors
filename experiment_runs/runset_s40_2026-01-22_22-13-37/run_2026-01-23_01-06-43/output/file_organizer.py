#!/usr/bin/env python3
"""
File Organizer CLI Tool
A collaborative project by Alice and Bob

Organizes files in a directory by type, date, or custom rules.
"""

import argparse
import os
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import mimetypes
import hashlib
import sys
import json
from enum import Enum

class ConflictAction(Enum):
    """Actions to take when file conflicts are detected."""
    SKIP = "skip"
    OVERWRITE = "overwrite"
    RENAME = "rename"
    CREATE_CATEGORY = "create_category"
    QUIT = "quit"

class InteractiveHelper:
    """Helper class for interactive user prompts and conflict resolution."""

    def __init__(self, batch_mode=False):
        self.batch_mode = batch_mode or not sys.stdin.isatty()  # Auto-detect non-interactive environments
        self.remember_choice = {}  # Cache user choices for similar conflicts

    def resolve_name_conflict(self, source_file: Path, target_file: Path) -> ConflictAction:
        """Handle conflicts when target file already exists."""
        if self.batch_mode:
            return ConflictAction.RENAME  # Safe default for batch mode

        print(f"\n⚠️  CONFLICT DETECTED:")
        print(f"   Source: {source_file.name}")
        print(f"   Target: {target_file}")
        print(f"   Target already exists!")

        # Check if target file is identical
        try:
            if source_file.stat().st_size == target_file.stat().st_size:
                source_hash = self._compute_file_hash(source_file)
                target_hash = self._compute_file_hash(target_file)
                if source_hash == target_hash:
                    print(f"   ✅ Files are identical - safe to skip")
        except (OSError, IOError):
            pass

        choices = {
            's': ('Skip', 'Leave source file where it is'),
            'o': ('Overwrite', 'Replace target with source file'),
            'r': ('Rename', 'Add number suffix to avoid conflict'),
            'q': ('Quit', 'Stop organizing')
        }

        return self._prompt_choice("How should this conflict be resolved?", choices, {
            's': ConflictAction.SKIP,
            'o': ConflictAction.OVERWRITE,
            'r': ConflictAction.RENAME,
            'q': ConflictAction.QUIT
        })

    def resolve_category_ambiguity(self, file_path: Path, possible_categories: list) -> str:
        """Handle cases where file could belong to multiple categories."""
        if self.batch_mode or len(possible_categories) <= 1:
            return possible_categories[0] if possible_categories else 'misc'

        print(f"\n🤔 CATEGORY AMBIGUITY:")
        print(f"   File: {file_path.name}")
        print(f"   Could belong to multiple categories")

        choices = {}
        choice_map = {}
        for i, category in enumerate(possible_categories, 1):
            key = str(i)
            choices[key] = (category.capitalize(), f"Organize into {category} folder")
            choice_map[key] = category

        choices['c'] = ('Create new', 'Create a custom category')
        choices['m'] = ('Misc', 'Put in miscellaneous folder')

        choice_map['c'] = ConflictAction.CREATE_CATEGORY
        choice_map['m'] = 'misc'

        result = self._prompt_choice("Which category should this file go to?", choices, choice_map)

        if result == ConflictAction.CREATE_CATEGORY:
            return self._prompt_custom_category()

        return result

    def _prompt_choice(self, question: str, choices: dict, choice_map: dict):
        """Generic choice prompter with validation."""
        print(f"\n{question}")
        for key, (label, description) in choices.items():
            print(f"   [{key}] {label} - {description}")

        while True:
            choice = input("\nYour choice: ").lower().strip()
            if choice in choice_map:
                return choice_map[choice]
            print(f"Invalid choice. Please enter one of: {', '.join(choices.keys())}")

    def _prompt_custom_category(self) -> str:
        """Prompt user to create a custom category name."""
        while True:
            category = input("\nEnter custom category name: ").strip().lower()
            if category and category.isalnum():
                return category
            print("Category name must be alphanumeric and not empty.")

    def _compute_file_hash(self, file_path: Path) -> str:
        """Quick hash computation for conflict detection."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read first and last 4KB for speed
                chunk = f.read(4096)
                if chunk:
                    hash_sha256.update(chunk)
                f.seek(-min(4096, f.tell()), 2)  # Go to end - 4KB or start
                chunk = f.read(4096)
                if chunk:
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (OSError, IOError) as e:
            return ""

class UndoLogger:
    """Handles logging and undoing of file operations."""

    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        self.log_file = source_dir / '.file_organizer_log.json'
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    def log_operation(self, operation_type: str, source_path: Path, destination_path: Path,
                      renamed_to: str = None):
        """Log a file operation for potential undo."""
        operation = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,  # 'move', 'rename', 'create_dir'
            'source_path': str(source_path),
            'destination_path': str(destination_path),
            'renamed_to': renamed_to,  # Only for renamed files
            'file_size': source_path.stat().st_size if source_path.exists() else 0
        }

        # Load existing log or create new one
        log_data = self._load_log()
        log_data.append(operation)

        # Write back to file
        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

    def _load_log(self) -> list:
        """Load existing log data or return empty list."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def get_recent_sessions(self, limit: int = 10) -> list:
        """Get the most recent organization sessions."""
        log_data = self._load_log()
        sessions = {}

        for op in log_data:
            session_id = op['session_id']
            if session_id not in sessions:
                sessions[session_id] = {
                    'session_id': session_id,
                    'start_time': op['timestamp'],
                    'operations': [],
                    'files_moved': 0
                }
            sessions[session_id]['operations'].append(op)
            sessions[session_id]['files_moved'] += 1

        # Return most recent sessions
        return sorted(sessions.values(),
                     key=lambda x: x['start_time'], reverse=True)[:limit]

    def can_undo_session(self, session_id: str) -> tuple[bool, list]:
        """Check if a session can be safely undone. Returns (can_undo, issues)."""
        log_data = self._load_log()
        session_ops = [op for op in log_data if op['session_id'] == session_id]

        if not session_ops:
            return False, ['Session not found']

        issues = []

        for op in session_ops:
            dest_path = Path(op['destination_path'])
            source_path = Path(op['source_path'])

            # Check if destination file still exists
            if not dest_path.exists():
                issues.append(f"Destination file missing: {dest_path}")
                continue

            # Check if original location is now occupied
            if source_path.exists():
                issues.append(f"Original location now occupied: {source_path}")
                continue

        return len(issues) == 0, issues

    def undo_session(self, session_id: str, dry_run: bool = False) -> dict:
        """Undo all operations from a specific session."""
        log_data = self._load_log()
        session_ops = [op for op in log_data if op['session_id'] == session_id]

        if not session_ops:
            return {'success': False, 'error': 'Session not found'}

        # Reverse order to undo in reverse chronological order
        session_ops.reverse()

        results = {
            'success': True,
            'operations_undone': 0,
            'operations_failed': 0,
            'errors': []
        }

        for op in session_ops:
            try:
                dest_path = Path(op['destination_path'])
                source_path = Path(op['source_path'])

                if not dest_path.exists():
                    results['errors'].append(f"Cannot undo: {dest_path} no longer exists")
                    results['operations_failed'] += 1
                    continue

                if source_path.exists():
                    results['errors'].append(f"Cannot undo: {source_path} is now occupied")
                    results['operations_failed'] += 1
                    continue

                if not dry_run:
                    # Ensure parent directory exists
                    source_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(dest_path), str(source_path))

                results['operations_undone'] += 1

                if dry_run:
                    print(f"[DRY RUN] Would move {dest_path} → {source_path}")
                else:
                    print(f"✓ Restored {dest_path.name} → {source_path.parent}/")

            except Exception as e:
                results['errors'].append(f"Error undoing {op['destination_path']}: {e}")
                results['operations_failed'] += 1
                results['success'] = False

        # Remove undone operations from log (only if not dry run and successful)
        if not dry_run and results['success'] and results['operations_failed'] == 0:
            remaining_ops = [op for op in log_data if op['session_id'] != session_id]
            with open(self.log_file, 'w') as f:
                json.dump(remaining_ops, f, indent=2)

        return results


class FileOrganizer:
    """Main class for organizing files based on various strategies."""

    def __init__(self, source_dir: str, dry_run: bool = False, interactive: bool = True):
        self.source_dir = Path(source_dir)
        self.dry_run = dry_run
        self.interactive = interactive
        self.stats = defaultdict(int)
        self.helper = InteractiveHelper(batch_mode=not interactive)
        self.undo_logger = UndoLogger(self.source_dir)

    def organize_by_date(self, target_dir: str = None, date_format: str = "year/month") -> dict:
        """
        Organize files by their modification date.

        Args:
            target_dir: Directory to organize files into. If None, uses source_dir/organized_by_date
            date_format: How to structure date folders:
                        - "year/month": 2024/01_January/
                        - "year": 2024/
                        - "month": 2024-01/
                        - "quarter": 2024/Q1/

        Returns:
            Dictionary with organization statistics
        """
        if target_dir is None:
            target_dir = self.source_dir / "organized_by_date"
        else:
            target_dir = Path(target_dir)

        # Create target directory if it doesn't exist
        if not self.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)

        print(f"Organizing files from: {self.source_dir}")
        print(f"Target directory: {target_dir}")
        print(f"Date format: {date_format}")
        if self.dry_run:
            print("DRY RUN - No files will be moved")
        print("-" * 50)

        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                # Get file modification time
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)

                # Create date-based folder structure
                if date_format == "year/month":
                    month_name = mod_time.strftime("%B")
                    subfolder_name = f"{mod_time.year}/{mod_time.month:02d}_{month_name}"
                elif date_format == "year":
                    subfolder_name = str(mod_time.year)
                elif date_format == "month":
                    subfolder_name = mod_time.strftime("%Y-%m")
                elif date_format == "quarter":
                    quarter = (mod_time.month - 1) // 3 + 1
                    subfolder_name = f"{mod_time.year}/Q{quarter}"
                else:
                    print(f"✗ Unknown date format: {date_format}")
                    continue

                # Create subfolder and move file
                subfolder = target_dir / subfolder_name
                target_file_path = subfolder / file_path.name

                if not self.dry_run:
                    subfolder.mkdir(parents=True, exist_ok=True)
                    try:
                        # Log the operation before performing it
                        self.undo_logger.log_operation('move', file_path, target_file_path)

                        shutil.move(str(file_path), str(target_file_path))
                        print(f"✓ Moved {file_path.name} → {subfolder_name}/")
                    except Exception as e:
                        print(f"✗ Failed to move {file_path.name}: {e}")
                        self.stats['errors'] += 1
                        continue
                else:
                    print(f"[DRY RUN] Would move {file_path.name} → {subfolder_name}/")

                self.stats[subfolder_name] += 1
                self.stats['total'] += 1

        return dict(self.stats)

    def organize_by_type(self, target_dir: str = None) -> dict:
        """
        Organize files by their file type/extension.

        Args:
            target_dir: Directory to organize files into. If None, uses source_dir/organized

        Returns:
            Dictionary with organization statistics
        """
        if target_dir is None:
            target_dir = self.source_dir / "organized_by_type"
        else:
            target_dir = Path(target_dir)

        # Create target directory if it doesn't exist
        if not self.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)

        # File type mappings
        type_folders = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb'],
            'misc': []  # Default for unmatched files
        }

        print(f"Organizing files from: {self.source_dir}")
        print(f"Target directory: {target_dir}")
        if self.dry_run:
            print("DRY RUN - No files will be moved")
        print("-" * 50)

        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                file_ext = file_path.suffix.lower()

                # Find appropriate folder(s) - check for ambiguous categorization
                possible_folders = []
                for folder_name, extensions in type_folders.items():
                    if file_ext in extensions:
                        possible_folders.append(folder_name)

                # Handle ambiguous categorization
                if len(possible_folders) > 1 and self.interactive:
                    target_folder = self.helper.resolve_category_ambiguity(file_path, possible_folders)
                elif len(possible_folders) == 1:
                    target_folder = possible_folders[0]
                else:
                    target_folder = 'misc'

                # Create subfolder and handle conflicts
                subfolder = target_dir / target_folder
                target_file_path = subfolder / file_path.name

                # Check for naming conflicts
                if target_file_path.exists():
                    if self.interactive and not self.helper.batch_mode:
                        action = self.helper.resolve_name_conflict(file_path, target_file_path)
                    else:
                        action = ConflictAction.RENAME  # Default action for batch mode

                    if action == ConflictAction.SKIP:
                        print(f"⏭  Skipped {file_path.name} (conflict)")
                        self.stats['skipped'] += 1
                        continue
                    elif action == ConflictAction.QUIT:
                        print("\n👋 Organizing cancelled by user")
                        return dict(self.stats)
                    elif action == ConflictAction.RENAME:
                        # Find available name with suffix
                        base_name = file_path.stem
                        extension = file_path.suffix
                        counter = 1
                        while target_file_path.exists():
                            new_name = f"{base_name}_{counter}{extension}"
                            target_file_path = subfolder / new_name
                            counter += 1
                    # OVERWRITE case: just proceed with original target_file_path

                if not self.dry_run:
                    subfolder.mkdir(exist_ok=True)
                    try:
                        # Log the operation before performing it
                        renamed_to = target_file_path.name if target_file_path.name != file_path.name else None
                        self.undo_logger.log_operation('move', file_path, target_file_path, renamed_to)

                        shutil.move(str(file_path), str(target_file_path))
                        if target_file_path.name != file_path.name:
                            print(f"✓ Moved {file_path.name} → {target_folder}/{target_file_path.name}")
                        else:
                            print(f"✓ Moved {file_path.name} → {target_folder}/")
                    except Exception as e:
                        print(f"✗ Failed to move {file_path.name}: {e}")
                        self.stats['errors'] += 1
                        continue
                else:
                    if target_file_path.name != file_path.name:
                        print(f"[DRY RUN] Would move {file_path.name} → {target_folder}/{target_file_path.name}")
                    else:
                        print(f"[DRY RUN] Would move {file_path.name} → {target_folder}/")

                self.stats[target_folder] += 1
                self.stats['total'] += 1

        return dict(self.stats)

    def generate_report(self) -> dict:
        """
        Generate a comprehensive report of the directory contents without organizing.

        Returns:
            Dictionary containing analysis of files by type, size, dates, and potential duplicates
        """
        report = {
            'summary': {'total_files': 0, 'total_size': 0, 'scan_time': datetime.now().isoformat()},
            'by_type': defaultdict(list),
            'by_size': {'small': 0, 'medium': 0, 'large': 0, 'huge': 0},
            'by_age': {'recent': 0, 'old': 0, 'ancient': 0},
            'potential_duplicates': []
        }

        # File type mappings (same as organize_by_type)
        type_folders = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb'],
            'misc': []
        }

        # Track files by size and hash for duplicate detection
        size_groups = defaultdict(list)
        hash_groups = defaultdict(list)
        now = datetime.now()

        print(f"Analyzing directory: {self.source_dir}")
        print("-" * 50)

        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file():
                # Get file info
                stat = file_path.stat()
                file_size = stat.st_size
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                age_days = (now - mod_time).days

                # Categorize by type
                file_ext = file_path.suffix.lower()
                file_type = 'misc'
                for folder_name, extensions in type_folders.items():
                    if file_ext in extensions:
                        file_type = folder_name
                        break

                file_info = {
                    'name': file_path.name,
                    'path': str(file_path.relative_to(self.source_dir)),
                    'size': file_size,
                    'modified': mod_time.strftime('%Y-%m-%d %H:%M'),
                    'age_days': age_days
                }

                report['by_type'][file_type].append(file_info)
                report['summary']['total_files'] += 1
                report['summary']['total_size'] += file_size

                # Categorize by size (in bytes)
                if file_size < 1024 * 100:  # < 100KB
                    report['by_size']['small'] += 1
                elif file_size < 1024 * 1024 * 10:  # < 10MB
                    report['by_size']['medium'] += 1
                elif file_size < 1024 * 1024 * 100:  # < 100MB
                    report['by_size']['large'] += 1
                else:
                    report['by_size']['huge'] += 1

                # Categorize by age
                if age_days < 30:
                    report['by_age']['recent'] += 1
                elif age_days < 365:
                    report['by_age']['old'] += 1
                else:
                    report['by_age']['ancient'] += 1

                # Group by size for duplicate detection
                size_groups[file_size].append(file_path)

                # For small files, also compute hash for exact duplicate detection
                if file_size < 1024 * 1024 * 10:  # Only hash files < 10MB for performance
                    try:
                        file_hash = self._compute_file_hash(file_path)
                        hash_groups[file_hash].append(file_path)
                    except (OSError, IOError):
                        pass  # Skip files we can't read

        # Find exact duplicates (same hash) and potential duplicates (same size)
        exact_duplicates = []
        potential_duplicates = []

        # Find exact duplicates by hash
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                exact_duplicates.append({
                    'type': 'exact',
                    'hash': file_hash[:16] + '...',
                    'size': files[0].stat().st_size,
                    'count': len(files),
                    'files': [str(f.relative_to(self.source_dir)) for f in files]
                })

        # Find potential duplicates by size (excluding those already found as exact)
        exact_files = {f for files in hash_groups.values() if len(files) > 1 for f in files}
        for size, files in size_groups.items():
            if len(files) > 1 and size > 0:
                # Only include files not already identified as exact duplicates
                non_exact_files = [f for f in files if f not in exact_files]
                if len(non_exact_files) > 1:
                    potential_duplicates.append({
                        'type': 'potential',
                        'size': size,
                        'count': len(non_exact_files),
                        'files': [str(f.relative_to(self.source_dir)) for f in non_exact_files]
                    })

        report['potential_duplicates'] = exact_duplicates + potential_duplicates

        return report

    def print_report(self, report: dict):
        """Print a formatted report to the console."""
        print("\n" + "=" * 60)
        print("📊 DIRECTORY ANALYSIS REPORT")
        print("=" * 60)

        # Summary
        total_files = report['summary']['total_files']
        total_size = report['summary']['total_size']
        print(f"📁 Total files: {total_files}")
        print(f"💾 Total size: {self._format_size(total_size)}")
        print(f"⏰ Scanned: {report['summary']['scan_time']}")

        # By file type
        print(f"\n📂 Files by type:")
        for file_type, files in report['by_type'].items():
            if files:
                type_size = sum(f['size'] for f in files)
                print(f"   {file_type.capitalize()}: {len(files)} files ({self._format_size(type_size)})")

        # By size category
        print(f"\n📏 Files by size:")
        size_labels = {
            'small': 'Small (<100KB)',
            'medium': 'Medium (100KB-10MB)',
            'large': 'Large (10MB-100MB)',
            'huge': 'Huge (>100MB)'
        }
        for size_cat, count in report['by_size'].items():
            if count > 0:
                print(f"   {size_labels[size_cat]}: {count} files")

        # By age
        print(f"\n📅 Files by age:")
        age_labels = {
            'recent': 'Recent (<30 days)',
            'old': 'Old (30 days - 1 year)',
            'ancient': 'Ancient (>1 year)'
        }
        for age_cat, count in report['by_age'].items():
            if count > 0:
                print(f"   {age_labels[age_cat]}: {count} files")

        # Duplicates
        if report['potential_duplicates']:
            print(f"\n🔍 Duplicate files:")
            for dup in report['potential_duplicates']:
                if dup['type'] == 'exact':
                    print(f"   ✅ EXACT duplicates ({dup['count']} files, {self._format_size(dup['size'])}):")
                else:
                    print(f"   ⚠️  POTENTIAL duplicates ({dup['count']} files, {self._format_size(dup['size'])}):")
                for file_path in dup['files']:
                    print(f"     - {file_path}")
                print()  # Extra spacing between duplicate groups

        print("=" * 60)

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file for duplicate detection."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (OSError, IOError) as e:
            raise e

    def _format_size(self, bytes_count: int) -> str:
        """Format bytes into human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} PB"

    def print_stats(self):
        """Print organization statistics."""
        if self.stats['total'] == 0:
            print("No files processed.")
            return

        print("\n" + "=" * 50)
        print("ORGANIZATION SUMMARY")
        print("=" * 50)

        for category, count in self.stats.items():
            if category not in ['total', 'errors']:
                print(f"{category.capitalize()}: {count} files")

        print(f"\nTotal files processed: {self.stats['total']}")
        if self.stats['errors'] > 0:
            print(f"Errors encountered: {self.stats['errors']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by type, date, or custom rules.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s organize /path/to/messy/folder
  %(prog)s organize ~/Downloads --by type --dry-run
  %(prog)s organize ~/Downloads --by date --date-format year/month --dry-run
  %(prog)s organize . --by date --date-format quarter --target ./organized_dates
  %(prog)s report ~/Downloads
  %(prog)s undo ~/Downloads --list
  %(prog)s undo ~/Downloads --session 20260123_140530 --dry-run
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Organize command
    organize_parser = subparsers.add_parser('organize', help='Organize files by type or date')
    organize_parser.add_argument('source', help='Source directory to organize')
    organize_parser.add_argument('--by', choices=['type', 'date'], default='type',
                                help='Organization method: by file type or modification date')
    organize_parser.add_argument('--target', help='Target directory (default: source/organized_by_[method])')
    organize_parser.add_argument('--date-format', choices=['year/month', 'year', 'month', 'quarter'],
                                default='year/month', help='Date folder structure (only for --by date)')
    organize_parser.add_argument('--dry-run', action='store_true',
                                help='Show what would be done without actually moving files')
    organize_parser.add_argument('--batch', action='store_true',
                                help='Non-interactive mode: automatically resolve conflicts')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate analysis report without organizing')
    report_parser.add_argument('source', help='Directory to analyze')

    # Undo command
    undo_parser = subparsers.add_parser('undo', help='Undo previous organization operations')
    undo_parser.add_argument('source', help='Directory where organization was performed')
    undo_parser.add_argument('--list', action='store_true',
                            help='List recent organization sessions')
    undo_parser.add_argument('--session', help='Session ID to undo (from --list)')
    undo_parser.add_argument('--dry-run', action='store_true',
                            help='Show what would be undone without actually moving files')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'organize':
        if not os.path.exists(args.source):
            print(f"Error: Source directory '{args.source}' does not exist.")
            return

        organizer = FileOrganizer(args.source, dry_run=args.dry_run, interactive=not args.batch)

        if args.by == 'type':
            stats = organizer.organize_by_type(args.target)
        elif args.by == 'date':
            stats = organizer.organize_by_date(args.target, args.date_format)

        organizer.print_stats()

    elif args.command == 'report':
        if not os.path.exists(args.source):
            print(f"Error: Source directory '{args.source}' does not exist.")
            return

        organizer = FileOrganizer(args.source)
        report = organizer.generate_report()
        organizer.print_report(report)

    elif args.command == 'undo':
        if not os.path.exists(args.source):
            print(f"Error: Source directory '{args.source}' does not exist.")
            return

        undo_logger = UndoLogger(Path(args.source))

        if args.list:
            # List recent sessions
            sessions = undo_logger.get_recent_sessions()
            if not sessions:
                print("No organization sessions found.")
                return

            print("\n" + "=" * 60)
            print("📋 RECENT ORGANIZATION SESSIONS")
            print("=" * 60)

            for session in sessions:
                session_time = datetime.fromisoformat(session['start_time']).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Session ID: {session['session_id']}")
                print(f"Time: {session_time}")
                print(f"Files moved: {session['files_moved']}")

                # Check if session can be undone
                can_undo, issues = undo_logger.can_undo_session(session['session_id'])
                if can_undo:
                    print("Status: ✅ Can be undone")
                else:
                    print(f"Status: ❌ Cannot be undone ({len(issues)} issues)")
                print("-" * 40)

            print("\nTo undo a session, use: --session <session_id>")

        elif args.session:
            # Undo specific session
            can_undo, issues = undo_logger.can_undo_session(args.session)

            if not can_undo:
                print(f"❌ Cannot undo session {args.session}:")
                for issue in issues:
                    print(f"   - {issue}")
                return

            if args.dry_run:
                print(f"🔍 DRY RUN: Would undo session {args.session}")
                print("-" * 50)

            result = undo_logger.undo_session(args.session, dry_run=args.dry_run)

            if result['success']:
                action = "Would undo" if args.dry_run else "Successfully undid"
                print(f"\n✅ {action} {result['operations_undone']} operations")
                if result['operations_failed'] > 0:
                    print(f"⚠️  {result['operations_failed']} operations could not be undone")
            else:
                print(f"\n❌ Undo failed:")
                for error in result['errors']:
                    print(f"   - {error}")

        else:
            print("Use --list to see recent sessions or --session <id> to undo a specific session")


if __name__ == "__main__":
    main()