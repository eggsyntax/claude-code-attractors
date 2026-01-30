"""
Submission Handler and Preprocessing Module
Part of Collaborative Code Review System - Alice's Implementation

This module handles intake of code submissions and prepares them for analysis
by Bob's Review Engine components.
"""

import os
import uuid
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union, Set
from dataclasses import dataclass, asdict
import json
import fnmatch
import subprocess

@dataclass
class FileInfo:
    """Metadata about a file submitted for review"""
    path: str
    relative_path: str
    size_bytes: int
    language: Optional[str]
    encoding: str
    hash_sha256: str
    last_modified: datetime

@dataclass
class SubmissionContext:
    """Git and project context for the submission"""
    is_git_repo: bool
    current_branch: Optional[str]
    latest_commit: Optional[str]
    uncommitted_changes: bool
    project_root: str
    gitignore_patterns: List[str]

@dataclass
class ReviewSession:
    """Complete review session with all metadata"""
    id: str
    timestamp: datetime
    input_type: str  # 'files', 'directory', 'git_diff'
    source_paths: List[str]
    files: List[FileInfo]
    context: SubmissionContext
    config: Dict
    status: str

    def to_dict(self):
        return asdict(self)

class LanguageDetector:
    """Detects programming language from file extensions and content"""

    EXTENSION_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.rb': 'ruby',
        '.php': 'php',
        '.cs': 'csharp',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.sh': 'shell',
        '.bash': 'shell',
        '.zsh': 'shell',
        '.sql': 'sql',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.vue': 'vue',
        '.svelte': 'svelte',
    }

    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        return self.EXTENSION_MAP.get(ext)

class GitContextExtractor:
    """Extracts Git repository context and respects .gitignore"""

    def extract_context(self, path: str) -> SubmissionContext:
        """Extract git context from a directory"""
        project_root = self._find_project_root(path)

        if self._is_git_repo(project_root):
            return SubmissionContext(
                is_git_repo=True,
                current_branch=self._get_current_branch(project_root),
                latest_commit=self._get_latest_commit(project_root),
                uncommitted_changes=self._has_uncommitted_changes(project_root),
                project_root=project_root,
                gitignore_patterns=self._load_gitignore_patterns(project_root)
            )
        else:
            return SubmissionContext(
                is_git_repo=False,
                current_branch=None,
                latest_commit=None,
                uncommitted_changes=False,
                project_root=project_root,
                gitignore_patterns=[]
            )

    def _find_project_root(self, path: str) -> str:
        """Find the root directory of the project"""
        current = Path(path).resolve()

        # Look for common project indicators
        indicators = ['.git', 'package.json', 'setup.py', 'Cargo.toml', 'go.mod', 'pom.xml']

        while current.parent != current:
            if any((current / indicator).exists() for indicator in indicators):
                return str(current)
            current = current.parent

        return str(Path(path).resolve())

    def _is_git_repo(self, path: str) -> bool:
        """Check if directory is a git repository"""
        return (Path(path) / '.git').exists()

    def _get_current_branch(self, repo_path: str) -> Optional[str]:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return None

    def _get_latest_commit(self, repo_path: str) -> Optional[str]:
        """Get latest commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()[:8] if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return None

    def _has_uncommitted_changes(self, repo_path: str) -> bool:
        """Check if there are uncommitted changes"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return bool(result.stdout.strip()) if result.returncode == 0 else False
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def _load_gitignore_patterns(self, repo_path: str) -> List[str]:
        """Load patterns from .gitignore file"""
        gitignore_path = Path(repo_path) / '.gitignore'
        if not gitignore_path.exists():
            return []

        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                patterns = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
                return patterns
        except (IOError, UnicodeDecodeError):
            return []

class FileFilter:
    """Filters files based on patterns and configuration"""

    def __init__(self, config: Dict):
        self.include_patterns = config.get('review', {}).get('include_patterns', [])
        self.exclude_patterns = config.get('review', {}).get('exclude_patterns', [])
        self.max_file_size_mb = config.get('review', {}).get('max_file_size_mb', 10)
        self.respect_gitignore = config.get('integration', {}).get('git', {}).get('respect_gitignore', True)

    def should_include_file(self, file_path: str, gitignore_patterns: List[str]) -> bool:
        """Determine if a file should be included in analysis"""
        path = Path(file_path)

        # Check file size
        try:
            if path.stat().st_size > self.max_file_size_mb * 1024 * 1024:
                return False
        except OSError:
            return False

        # Check if it's a text file
        if not self._is_text_file(file_path):
            return False

        # Check gitignore patterns
        if self.respect_gitignore and self._matches_gitignore(file_path, gitignore_patterns):
            return False

        # Check exclude patterns
        if self._matches_patterns(file_path, self.exclude_patterns):
            return False

        # Check include patterns (if specified)
        if self.include_patterns and not self._matches_patterns(file_path, self.include_patterns):
            return False

        return True

    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is likely a text file"""
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type:
            return mime_type.startswith('text/') or mime_type in [
                'application/json',
                'application/xml',
                'application/javascript',
                'application/x-python',
                'application/x-sh'
            ]

        # Fallback: check extension
        ext = Path(file_path).suffix.lower()
        text_extensions = {
            '.txt', '.md', '.rst', '.py', '.js', '.ts', '.java', '.go', '.rs',
            '.cpp', '.c', '.h', '.rb', '.php', '.cs', '.swift', '.kt', '.scala',
            '.sh', '.bash', '.zsh', '.sql', '.yaml', '.yml', '.json', '.xml',
            '.html', '.css', '.scss', '.sass', '.vue', '.svelte', '.jsx', '.tsx'
        }

        return ext in text_extensions

    def _matches_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file matches any of the given patterns"""
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def _matches_gitignore(self, file_path: str, gitignore_patterns: List[str]) -> bool:
        """Check if file matches gitignore patterns"""
        return self._matches_patterns(file_path, gitignore_patterns)

class SubmissionHandler:
    """Main handler for code submission intake and preprocessing"""

    def __init__(self, config: Dict):
        self.config = config
        self.language_detector = LanguageDetector()
        self.git_extractor = GitContextExtractor()
        self.file_filter = FileFilter(config)

    def process_submission(self, input_paths: Union[str, List[str]], input_type: str = 'auto') -> ReviewSession:
        """
        Process a code submission and create a review session

        Args:
            input_paths: File path(s) or directory to analyze
            input_type: 'files', 'directory', 'git_diff', or 'auto'

        Returns:
            ReviewSession with all metadata and processed files
        """
        session_id = str(uuid.uuid4())

        # Normalize input paths
        if isinstance(input_paths, str):
            input_paths = [input_paths]

        # Auto-detect input type if needed
        if input_type == 'auto':
            input_type = self._detect_input_type(input_paths)

        # Extract git context from first path
        context = self.git_extractor.extract_context(input_paths[0])

        # Discover and process files
        files = self._discover_files(input_paths, input_type, context)

        # Create review session
        session = ReviewSession(
            id=session_id,
            timestamp=datetime.now(),
            input_type=input_type,
            source_paths=input_paths,
            files=files,
            context=context,
            config=self.config,
            status='initialized'
        )

        return session

    def _detect_input_type(self, paths: List[str]) -> str:
        """Auto-detect the type of input"""
        if len(paths) == 1:
            path = Path(paths[0])
            if path.is_dir():
                return 'directory'
            elif path.is_file():
                return 'files'

        return 'files'

    def _discover_files(self, input_paths: List[str], input_type: str, context: SubmissionContext) -> List[FileInfo]:
        """Discover all files to be analyzed"""
        all_files = set()

        for input_path in input_paths:
            if input_type == 'directory':
                all_files.update(self._scan_directory(input_path, context.gitignore_patterns))
            elif input_type == 'files':
                if self.file_filter.should_include_file(input_path, context.gitignore_patterns):
                    all_files.add(input_path)

        # Process file metadata
        processed_files = []
        for file_path in sorted(all_files):
            file_info = self._process_file(file_path, context.project_root)
            if file_info:
                processed_files.append(file_info)

        return processed_files

    def _scan_directory(self, directory: str, gitignore_patterns: List[str]) -> Set[str]:
        """Recursively scan directory for files to analyze"""
        files = set()

        for root, dirs, filenames in os.walk(directory):
            # Filter out directories that should be ignored
            dirs[:] = [d for d in dirs if not self._should_skip_directory(os.path.join(root, d))]

            for filename in filenames:
                file_path = os.path.join(root, filename)
                if self.file_filter.should_include_file(file_path, gitignore_patterns):
                    files.add(file_path)

        return files

    def _should_skip_directory(self, dir_path: str) -> bool:
        """Check if a directory should be skipped entirely"""
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'build', 'dist'}
        return Path(dir_path).name in skip_dirs

    def _process_file(self, file_path: str, project_root: str) -> Optional[FileInfo]:
        """Process a single file and extract metadata"""
        try:
            path = Path(file_path)
            stat = path.stat()

            # Calculate relative path
            try:
                relative_path = str(path.relative_to(project_root))
            except ValueError:
                relative_path = str(path)

            # Detect encoding
            encoding = self._detect_encoding(file_path)
            if not encoding:
                return None  # Skip binary or unreadable files

            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)

            return FileInfo(
                path=str(path),
                relative_path=relative_path,
                size_bytes=stat.st_size,
                language=self.language_detector.detect_language(file_path),
                encoding=encoding,
                hash_sha256=file_hash,
                last_modified=datetime.fromtimestamp(stat.st_mtime)
            )

        except (OSError, IOError):
            return None

    def _detect_encoding(self, file_path: str) -> Optional[str]:
        """Detect file encoding, return None for binary files"""
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(1024)

            # Try common encodings
            for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
                try:
                    sample.decode(encoding)
                    return encoding
                except UnicodeDecodeError:
                    continue

            return None
        except IOError:
            return None

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file contents"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except IOError:
            return ""

# Integration interface for Bob's Review Engine
def create_review_session(input_paths: Union[str, List[str]], config: Dict) -> ReviewSession:
    """
    Main entry point for creating a review session
    This is the interface Bob's analyzers will use
    """
    handler = SubmissionHandler(config)
    return handler.process_submission(input_paths)

if __name__ == "__main__":
    # Basic testing/demo
    sample_config = {
        "review": {
            "include_patterns": ["**/*.py", "**/*.js"],
            "exclude_patterns": ["**/node_modules/**"],
            "max_file_size_mb": 10
        },
        "integration": {
            "git": {
                "respect_gitignore": True
            }
        }
    }

    # This would create a session for the current directory
    # session = create_review_session(".", sample_config)
    # print(f"Created session {session.id} with {len(session.files)} files")