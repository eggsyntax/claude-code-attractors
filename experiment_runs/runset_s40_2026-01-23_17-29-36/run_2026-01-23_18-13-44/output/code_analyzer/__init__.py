"""
Collaborative Code Analyzer

A comprehensive Python code analysis and visualization tool built through
AI pair programming collaboration between Alice and Bob.

This package provides:
- AST-based structural analysis of Python code
- Advanced complexity metrics (cyclomatic and cognitive complexity)
- Interactive web-based visualization dashboards
- Command-line interface for easy integration
- Batch processing capabilities for large codebases

Example usage:
    >>> from code_analyzer import CodeAnalyzer, ComplexityAnalyzer
    >>> analyzer = CodeAnalyzer()
    >>> complexity = ComplexityAnalyzer()
    >>>
    >>> # Analyze a Python file
    >>> results = analyzer.analyze_file("my_script.py")
    >>> complexity_data = complexity.analyze_file("my_script.py")
    >>>
    >>> # Generate interactive dashboard
    >>> from code_analyzer.dashboard import DashboardGenerator
    >>> dashboard = DashboardGenerator()
    >>> dashboard.generate_dashboard("/path/to/project", "output.html")

Authors: Alice & Bob (AI Collaboration)
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Alice & Bob"
__email__ = "ai-collaboration@example.com"
__license__ = "MIT"

# Import main classes for easy access
from .ast_analyzer import CodeAnalyzer
from .complexity_analyzer import ComplexityAnalyzer
from .dashboard_generator import DashboardGenerator

# Define what gets imported with "from code_analyzer import *"
__all__ = [
    "CodeAnalyzer",
    "ComplexityAnalyzer",
    "DashboardGenerator",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

# Package metadata
PACKAGE_INFO = {
    "name": "collaborative-code-analyzer",
    "version": __version__,
    "description": "Interactive code analysis and visualization tool",
    "author": __author__,
    "email": __email__,
    "license": __license__,
    "url": "https://github.com/ai-collaboration/code-analyzer",
    "keywords": ["code analysis", "complexity metrics", "visualization", "static analysis"],
}

def get_version():
    """Return the package version string."""
    return __version__

def get_package_info():
    """Return package metadata dictionary."""
    return PACKAGE_INFO.copy()