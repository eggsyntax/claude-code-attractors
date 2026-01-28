#!/usr/bin/env python3
"""
Setup script for CodeAnalyzer - Interactive Code Analysis and Visualization Tool

This package provides comprehensive code analysis capabilities including:
- AST-based structural analysis of Python codebases
- Advanced complexity metrics (cyclomatic and cognitive complexity)
- Interactive web-based visualization dashboards
- Command-line interface for easy integration
- Batch processing for large projects

Built collaboratively by Alice & Bob as a demonstration of AI pair programming.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="collaborative-code-analyzer",
    version="1.0.0",
    description="Interactive code analysis and visualization tool with advanced complexity metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alice & Bob",
    author_email="ai-collaboration@example.com",
    url="https://github.com/ai-collaboration/code-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "plotly>=5.0.0",
        "jinja2>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "code-analyzer=code_analyzer.cli:main",
            "analyze-code=code_analyzer.cli:main",
        ],
    },
    package_data={
        "code_analyzer": [
            "templates/*.html",
            "static/*.css",
            "static/*.js",
        ],
    },
    include_package_data=True,
    keywords="code analysis, complexity metrics, visualization, static analysis, software quality",
    project_urls={
        "Bug Reports": "https://github.com/ai-collaboration/code-analyzer/issues",
        "Source": "https://github.com/ai-collaboration/code-analyzer",
        "Documentation": "https://collaborative-code-analyzer.readthedocs.io/",
    },
)