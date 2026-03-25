"""
Collaborative Codebase Analyzer - Core Architecture
Built by Dave & Tara as a demonstration of AI-AI collaboration

This module provides the foundational architecture for analyzing codebases
to identify collaboration opportunities and patterns.
"""

import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class FileInfo:
    """Core information about a source file"""
    path: str
    language: str
    size_bytes: int
    last_modified: datetime
    hash: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['last_modified'] = self.last_modified.isoformat()
        return data


@dataclass
class CodeEntity:
    """Represents a code entity (function, class, variable, etc.)"""
    name: str
    entity_type: str  # 'function', 'class', 'method', 'variable'
    file_path: str
    line_start: int
    line_end: int
    complexity_score: Optional[int] = None
    dependencies: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CodebaseAnalyzer:
    """
    Core analyzer that discovers and parses source files

    This class handles the foundational work of:
    1. File discovery and filtering
    2. Language detection
    3. AST parsing and entity extraction
    4. Building the foundational data model
    """

    SUPPORTED_LANGUAGES = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust'
    }

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.files: Dict[str, FileInfo] = {}
        self.entities: Dict[str, List[CodeEntity]] = {}
        self.parse_errors: List[str] = []

    def discover_files(self) -> None:
        """Discover all source files in the codebase"""
        print(f"🔍 Discovering files in {self.root_path}...")

        for file_path in self.root_path.rglob("*"):
            if self._should_analyze_file(file_path):
                try:
                    file_info = self._create_file_info(file_path)
                    self.files[str(file_path)] = file_info
                    print(f"  📄 Found {file_info.language}: {file_path.name}")
                except Exception as e:
                    self.parse_errors.append(f"Error processing {file_path}: {e}")

        print(f"✅ Discovered {len(self.files)} files")

    def parse_entities(self) -> None:
        """Extract code entities from discovered files"""
        print(f"🔬 Parsing code entities...")

        for file_path, file_info in self.files.items():
            if file_info.language == 'python':
                entities = self._parse_python_file(file_path)
                self.entities[file_path] = entities
                print(f"  🐍 Parsed {len(entities)} entities from {Path(file_path).name}")
            else:
                # Placeholder for other language parsers
                self.entities[file_path] = []

        total_entities = sum(len(entities) for entities in self.entities.values())
        print(f"✅ Extracted {total_entities} code entities")

    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if a file should be analyzed"""
        if file_path.is_dir():
            return False

        # Skip common non-source directories
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
        if any(part in skip_dirs for part in file_path.parts):
            return False

        # Check file extension
        return file_path.suffix in self.SUPPORTED_LANGUAGES

    def _create_file_info(self, file_path: Path) -> FileInfo:
        """Create FileInfo object for a given file"""
        stat = file_path.stat()

        # Calculate file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        return FileInfo(
            path=str(file_path),
            language=self.SUPPORTED_LANGUAGES[file_path.suffix],
            size_bytes=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            hash=file_hash
        )

    def _parse_python_file(self, file_path: str) -> List[CodeEntity]:
        """Parse Python file and extract entities"""
        entities = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    entities.append(CodeEntity(
                        name=node.name,
                        entity_type='function',
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=getattr(node, 'end_lineno', node.lineno)
                    ))
                elif isinstance(node, ast.ClassDef):
                    entities.append(CodeEntity(
                        name=node.name,
                        entity_type='class',
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=getattr(node, 'end_lineno', node.lineno)
                    ))

        except Exception as e:
            self.parse_errors.append(f"Error parsing {file_path}: {e}")

        return entities

    def export_analysis(self, output_file: str) -> None:
        """Export analysis results to JSON"""
        analysis_data = {
            'metadata': {
                'root_path': str(self.root_path),
                'analysis_timestamp': datetime.now().isoformat(),
                'total_files': len(self.files),
                'total_entities': sum(len(entities) for entities in self.entities.values()),
                'parse_errors': len(self.parse_errors)
            },
            'files': {path: file_info.to_dict() for path, file_info in self.files.items()},
            'entities': {path: [entity.to_dict() for entity in entities]
                        for path, entities in self.entities.items()},
            'errors': self.parse_errors
        }

        with open(output_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)

        print(f"📊 Analysis exported to {output_file}")


if __name__ == "__main__":
    # Example usage
    analyzer = CodebaseAnalyzer("/path/to/your/codebase")
    analyzer.discover_files()
    analyzer.parse_entities()
    analyzer.export_analysis("analysis_results.json")