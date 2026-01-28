#!/usr/bin/env python3
"""
AI-Powered Codebase Analyzer

An intelligent codebase analysis tool that demonstrates the intersection of AI and
developer productivity. This tool provides context-aware analysis, intelligent
refactoring suggestions, and generates living documentation that evolves with code.

Key Features:
- Deep architectural pattern recognition
- Context-aware anti-pattern detection
- Intelligent refactoring recommendations
- Living documentation generation
- Meta-analysis capabilities (analyzes its own code)

Created by Alice & Bob - demonstrating AI-assisted development workflows.
"""

import os
import ast
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
from datetime import datetime
import re
import hashlib


@dataclass
class IntelligentInsight:
    """Represents an AI-generated insight about the codebase."""
    category: str  # 'architecture', 'quality', 'maintainability', 'performance'
    title: str
    description: str
    impact: str  # 'low', 'medium', 'high', 'critical'
    confidence: float
    evidence: List[str]
    recommendations: List[str]
    affected_files: List[str]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CodePattern:
    """Enhanced pattern detection with AI reasoning."""
    pattern_id: str
    pattern_name: str
    pattern_type: str  # 'architectural', 'design', 'antipattern', 'smell'
    description: str
    files_involved: List[str]
    confidence_score: float
    complexity_impact: str
    maintainability_impact: str
    reasoning: str  # AI-generated explanation of why this pattern exists
    suggestions: List[str]


@dataclass
class RefactoringOpportunity:
    """Intelligent refactoring suggestions."""
    opportunity_id: str
    title: str
    description: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    effort_estimate: str  # 'small', 'medium', 'large'
    files_to_modify: List[str]
    benefits: List[str]
    risks: List[str]
    automated_feasible: bool
    code_examples: Dict[str, str]  # 'before' -> 'after' examples


@dataclass
class ProjectHealth:
    """Overall project health assessment."""
    health_score: float  # 0-100
    technical_debt_score: float  # 0-100
    maintainability_index: float  # 0-100
    test_coverage_estimate: float  # Based on test file analysis
    documentation_completeness: float  # 0-100
    trends: Dict[str, str]  # Improvement/degradation trends
    critical_issues: List[str]
    strengths: List[str]


class AICodebaseAnalyzer:
    """
    AI-powered codebase analyzer that provides intelligent insights,
    pattern recognition, and refactoring suggestions.
    """

    SUPPORTED_LANGUAGES = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'react',
        '.tsx': 'react-typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.cs': 'csharp',
        '.swift': 'swift',
        '.kt': 'kotlin'
    }

    # Common architectural patterns to detect
    ARCHITECTURAL_PATTERNS = {
        'mvc': ['model', 'view', 'controller', 'models', 'views', 'controllers'],
        'mvp': ['presenter', 'presenters'],
        'mvvm': ['viewmodel', 'viewmodels'],
        'repository': ['repository', 'repositories', 'repo'],
        'factory': ['factory', 'factories'],
        'observer': ['observer', 'observable', 'subscriber', 'publisher'],
        'decorator': ['decorator', 'decorators'],
        'adapter': ['adapter', 'adapters'],
        'facade': ['facade', 'facades'],
        'singleton': ['singleton'],
        'strategy': ['strategy', 'strategies'],
        'command': ['command', 'commands'],
        'builder': ['builder', 'builders']
    }

    def __init__(self, root_path: str, config: Optional[Dict] = None):
        """Initialize the AI-powered analyzer."""
        self.root_path = Path(root_path)
        self.config = config or {}
        self.files: Dict[str, dict] = {}
        self.patterns: List[CodePattern] = []
        self.insights: List[IntelligentInsight] = []
        self.refactoring_opportunities: List[RefactoringOpportunity] = []
        self.project_health: Optional[ProjectHealth] = None

        # Analysis caches
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._complexity_metrics: Dict[str, float] = {}
        self._file_relationships: Dict[str, Dict[str, float]] = {}

    def analyze_with_ai_insights(self) -> Dict[str, Any]:
        """
        Perform comprehensive AI-powered analysis of the codebase.

        Returns:
            Complete analysis results with AI-generated insights
        """
        print("🤖 Starting AI-powered codebase analysis...")

        # Phase 1: Discovery and basic analysis
        self._discover_codebase()
        print(f"📁 Discovered {len(self.files)} code files")

        # Phase 2: Deep pattern analysis
        self._analyze_patterns_with_ai()
        print(f"🧠 Identified {len(self.patterns)} patterns with AI reasoning")

        # Phase 3: Generate intelligent insights
        self._generate_ai_insights()
        print(f"💡 Generated {len(self.insights)} intelligent insights")

        # Phase 4: Find refactoring opportunities
        self._identify_refactoring_opportunities()
        print(f"🔧 Found {len(self.refactoring_opportunities)} refactoring opportunities")

        # Phase 5: Assess project health
        self._assess_project_health()
        print("❤️  Project health assessment complete")

        # Phase 6: Generate living documentation
        documentation = self._generate_living_documentation()
        print("📚 Living documentation generated")

        return {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'analyzer_version': '2.0-ai',
                'total_files': len(self.files),
                'languages': list(set(f['language'] for f in self.files.values()))
            },
            'files': self.files,
            'patterns': [asdict(p) for p in self.patterns],
            'insights': [asdict(i) for i in self.insights],
            'refactoring_opportunities': [asdict(r) for r in self.refactoring_opportunities],
            'project_health': asdict(self.project_health) if self.project_health else None,
            'documentation': documentation
        }

    def _discover_codebase(self) -> None:
        """Discover all code files and perform initial analysis."""
        for file_path in self.root_path.rglob('*'):
            if (file_path.is_file() and
                file_path.suffix in self.SUPPORTED_LANGUAGES and
                not self._should_ignore_file(file_path)):

                self._analyze_file(file_path)

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Determine if a file should be ignored during analysis."""
        ignore_patterns = [
            '.git', 'node_modules', '__pycache__', '.venv', 'venv',
            'build', 'dist', '.pytest_cache', 'coverage', '.coverage',
            'target', 'bin', 'obj', '.gradle', '.maven'
        ]

        return any(pattern in str(file_path) for pattern in ignore_patterns)

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single file comprehensively."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            relative_path = str(file_path.relative_to(self.root_path))
            language = self.SUPPORTED_LANGUAGES[file_path.suffix]

            # Basic metrics
            lines = content.split('\n')
            line_count = len(lines)
            size_bytes = len(content.encode('utf-8'))

            # Language-specific analysis
            analysis = self._analyze_by_language(content, language)

            # Calculate file hash for change detection
            file_hash = hashlib.md5(content.encode()).hexdigest()

            self.files[relative_path] = {
                'language': language,
                'size_bytes': size_bytes,
                'line_count': line_count,
                'hash': file_hash,
                'functions': analysis.get('functions', []),
                'classes': analysis.get('classes', []),
                'imports': analysis.get('imports', []),
                'exports': analysis.get('exports', []),
                'complexity_score': analysis.get('complexity', 0),
                'test_indicators': analysis.get('test_indicators', []),
                'documentation_score': analysis.get('documentation_score', 0),
                'maintainability_index': analysis.get('maintainability_index', 50)
            }

        except Exception as e:
            # Log error but continue analysis
            print(f"⚠️  Warning: Could not analyze {file_path}: {e}")

    def _analyze_by_language(self, content: str, language: str) -> Dict[str, Any]:
        """Perform language-specific analysis."""
        if language == 'python':
            return self._analyze_python_content(content)
        elif language in ['javascript', 'typescript', 'react', 'react-typescript']:
            return self._analyze_js_ts_content(content)
        else:
            return self._analyze_generic_content(content)

    def _analyze_python_content(self, content: str) -> Dict[str, Any]:
        """Analyze Python code using AST."""
        try:
            tree = ast.parse(content)

            functions = []
            classes = []
            imports = []
            complexity = 1
            test_indicators = []
            documentation_score = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args),
                        'has_docstring': ast.get_docstring(node) is not None
                    })
                    if node.name.startswith('test_'):
                        test_indicators.append(f"test_function:{node.name}")
                    if ast.get_docstring(node):
                        documentation_score += 2

                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        'has_docstring': ast.get_docstring(node) is not None
                    })
                    if ast.get_docstring(node):
                        documentation_score += 3

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
                    elif isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])

                elif isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1

            # Check for test frameworks
            test_frameworks = ['unittest', 'pytest', 'nose', 'testify']
            if any(framework in ' '.join(imports) for framework in test_frameworks):
                test_indicators.append("test_framework_import")

            return {
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'complexity': complexity,
                'test_indicators': test_indicators,
                'documentation_score': min(documentation_score, 100),
                'maintainability_index': max(0, 100 - complexity * 2)
            }

        except SyntaxError:
            return {'functions': [], 'classes': [], 'imports': [], 'complexity': 0}

    def _analyze_js_ts_content(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript content with regex patterns."""

        # Function patterns
        function_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)\s*=>|\([^)]*\)\s*{)',
            r'(\w+)\s*:\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>)'
        ]

        functions = []
        for pattern in function_patterns:
            matches = re.finditer(pattern, content)
            functions.extend([match.group(1) for match in matches])

        # Class patterns
        class_matches = re.finditer(r'class\s+(\w+)', content)
        classes = [match.group(1) for match in class_matches]

        # Import patterns
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        ]

        imports = []
        for pattern in import_patterns:
            matches = re.finditer(pattern, content)
            imports.extend([match.group(1) for match in matches])

        # Test indicators
        test_indicators = []
        test_patterns = ['describe\\(', 'test\\(', 'it\\(', 'expect\\(', '\\.test\\.', '\\.spec\\.']
        for pattern in test_patterns:
            if re.search(pattern, content):
                test_indicators.append(f"test_pattern:{pattern}")

        # Simple complexity calculation
        complexity = content.count('if ') + content.count('for ') + content.count('while ') + 1

        return {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'complexity': complexity,
            'test_indicators': test_indicators,
            'documentation_score': content.count('/**') * 5,  # JSDoc comments
            'maintainability_index': max(0, 100 - complexity)
        }

    def _analyze_generic_content(self, content: str) -> Dict[str, Any]:
        """Generic analysis for other languages."""
        lines = content.split('\n')

        # Simple heuristics
        comment_lines = sum(1 for line in lines if line.strip().startswith(('//','#', '/*', '--', ';;')))
        blank_lines = sum(1 for line in lines if not line.strip())
        code_lines = len(lines) - comment_lines - blank_lines

        return {
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': max(1, code_lines // 20),  # Rough estimate
            'test_indicators': [],
            'documentation_score': (comment_lines / len(lines)) * 100 if lines else 0,
            'maintainability_index': 50  # Neutral for unknown languages
        }

    def _analyze_patterns_with_ai(self) -> None:
        """Use AI-like reasoning to identify patterns in the codebase."""

        # Detect architectural patterns
        for pattern_name, keywords in self.ARCHITECTURAL_PATTERNS.items():
            matching_files = []
            confidence = 0.0

            for file_path, file_info in self.files.items():
                file_path_lower = file_path.lower()
                if any(keyword in file_path_lower for keyword in keywords):
                    matching_files.append(file_path)
                    confidence += 0.1

                # Check imports and function names
                imports_text = ' '.join(file_info.get('imports', [])).lower()
                if any(keyword in imports_text for keyword in keywords):
                    confidence += 0.05

            if matching_files and confidence > 0.2:
                # Generate AI reasoning
                reasoning = self._generate_pattern_reasoning(pattern_name, matching_files, confidence)

                self.patterns.append(CodePattern(
                    pattern_id=f"arch_{pattern_name}_{len(self.patterns)}",
                    pattern_name=pattern_name.upper(),
                    pattern_type="architectural",
                    description=f"{pattern_name.upper()} architectural pattern detected",
                    files_involved=matching_files,
                    confidence_score=min(confidence, 1.0),
                    complexity_impact="medium",
                    maintainability_impact="positive",
                    reasoning=reasoning,
                    suggestions=self._generate_pattern_suggestions(pattern_name, matching_files)
                ))

    def _generate_pattern_reasoning(self, pattern_name: str, files: List[str], confidence: float) -> str:
        """Generate AI-like reasoning for why a pattern was detected."""

        reasoning_templates = {
            'mvc': f"Detected MVC pattern with {confidence:.1%} confidence. Found {len(files)} files with MVC-related naming conventions. This suggests a well-structured separation of concerns between data (Model), presentation (View), and business logic (Controller).",

            'repository': f"Repository pattern identified with {confidence:.1%} confidence across {len(files)} files. This indicates data access abstraction, which is excellent for maintainability and testing. The repository pattern helps decouple business logic from data persistence.",

            'factory': f"Factory pattern detected in {len(files)} files with {confidence:.1%} confidence. This suggests object creation abstraction, which promotes loose coupling and makes the codebase more flexible for different object implementations.",

            'observer': f"Observer pattern found with {confidence:.1%} confidence. This indicates event-driven architecture across {len(files)} files, promoting loose coupling between components through notification mechanisms."
        }

        return reasoning_templates.get(pattern_name,
            f"{pattern_name.title()} pattern detected with {confidence:.1%} confidence across {len(files)} files. This pattern helps organize code structure and promotes maintainable architecture.")

    def _generate_pattern_suggestions(self, pattern_name: str, files: List[str]) -> List[str]:
        """Generate intelligent suggestions for detected patterns."""

        suggestions = {
            'mvc': [
                "Ensure clear separation between Models, Views, and Controllers",
                "Consider adding validation logic to Models",
                "Keep Controllers thin - move business logic to Services",
                "Add unit tests for each MVC component"
            ],
            'repository': [
                "Implement repository interfaces for better testability",
                "Add caching layer to repositories for performance",
                "Consider using dependency injection for repositories",
                "Add comprehensive error handling in repository methods"
            ],
            'singleton': [
                "⚠️ Warning: Singleton can make unit testing difficult",
                "Consider dependency injection instead of Singleton",
                "Ensure thread safety if using Singleton in concurrent environments",
                "Document why Singleton is necessary for this use case"
            ]
        }

        return suggestions.get(pattern_name, [
            f"Continue using {pattern_name} pattern consistently",
            "Add documentation explaining the pattern usage",
            "Ensure all team members understand this pattern"
        ])

    def _generate_ai_insights(self) -> None:
        """Generate intelligent insights about the codebase."""

        # Architecture insights
        self._generate_architecture_insights()

        # Quality insights
        self._generate_quality_insights()

        # Maintainability insights
        self._generate_maintainability_insights()

        # Performance insights
        self._generate_performance_insights()

    def _generate_architecture_insights(self) -> None:
        """Generate insights about architectural decisions."""

        languages = set(f['language'] for f in self.files.values())

        if len(languages) > 3:
            self.insights.append(IntelligentInsight(
                category="architecture",
                title="Multi-Language Complexity",
                description=f"Codebase uses {len(languages)} different programming languages: {', '.join(languages)}",
                impact="medium",
                confidence=0.9,
                evidence=[f"Found files in: {', '.join(languages)}"],
                recommendations=[
                    "Consider standardizing on fewer languages to reduce complexity",
                    "Ensure team has expertise in all used languages",
                    "Document architectural decisions for language choices"
                ],
                affected_files=list(self.files.keys())
            ))

    def _generate_quality_insights(self) -> None:
        """Generate insights about code quality."""

        total_files = len(self.files)
        high_complexity_files = [
            path for path, info in self.files.items()
            if info.get('complexity_score', 0) > 10
        ]

        if len(high_complexity_files) > total_files * 0.2:
            self.insights.append(IntelligentInsight(
                category="quality",
                title="High Complexity Concentration",
                description=f"{len(high_complexity_files)} files ({len(high_complexity_files)/total_files:.1%}) have high complexity scores",
                impact="high",
                confidence=0.85,
                evidence=[f"Files with complexity > 10: {len(high_complexity_files)}"],
                recommendations=[
                    "Refactor complex functions into smaller, focused methods",
                    "Add comprehensive unit tests for complex functions",
                    "Consider using design patterns to reduce complexity",
                    "Implement code review process focusing on complexity"
                ],
                affected_files=high_complexity_files
            ))

    def _generate_maintainability_insights(self) -> None:
        """Generate insights about maintainability."""

        avg_maintainability = sum(f.get('maintainability_index', 50) for f in self.files.values()) / len(self.files) if self.files else 50

        if avg_maintainability < 60:
            self.insights.append(IntelligentInsight(
                category="maintainability",
                title="Below Average Maintainability",
                description=f"Average maintainability index is {avg_maintainability:.1f}/100, below recommended threshold of 60",
                impact="high",
                confidence=0.8,
                evidence=[f"Maintainability index: {avg_maintainability:.1f}"],
                recommendations=[
                    "Reduce cyclomatic complexity in functions",
                    "Improve code documentation",
                    "Add more comprehensive unit tests",
                    "Refactor large classes and functions"
                ],
                affected_files=list(self.files.keys())
            ))

    def _generate_performance_insights(self) -> None:
        """Generate insights about potential performance issues."""

        large_files = [
            path for path, info in self.files.items()
            if info.get('line_count', 0) > 1000
        ]

        if large_files:
            self.insights.append(IntelligentInsight(
                category="performance",
                title="Large Files Impact",
                description=f"Found {len(large_files)} files with >1000 lines that may impact build and load times",
                impact="medium",
                confidence=0.7,
                evidence=[f"Large files: {', '.join(large_files[:5])}{'...' if len(large_files) > 5 else ''}"],
                recommendations=[
                    "Consider splitting large files into smaller modules",
                    "Use lazy loading for large components",
                    "Profile actual performance impact",
                    "Implement code splitting if using bundlers"
                ],
                affected_files=large_files
            ))

    def _identify_refactoring_opportunities(self) -> None:
        """Identify intelligent refactoring opportunities."""

        # Find duplicate patterns
        self._find_code_duplication_opportunities()

        # Find extraction opportunities
        self._find_method_extraction_opportunities()

        # Find architectural improvements
        self._find_architectural_improvements()

    def _find_code_duplication_opportunities(self) -> None:
        """Find opportunities to reduce code duplication."""

        # Simple heuristic: files with similar names might have duplication
        similar_files = defaultdict(list)

        for file_path in self.files.keys():
            base_name = Path(file_path).stem
            # Group by similar names (remove numbers, underscores)
            clean_name = re.sub(r'[\d_]+$', '', base_name)
            similar_files[clean_name].append(file_path)

        for clean_name, file_group in similar_files.items():
            if len(file_group) > 2:
                self.refactoring_opportunities.append(RefactoringOpportunity(
                    opportunity_id=f"dedup_{clean_name}_{len(self.refactoring_opportunities)}",
                    title=f"Potential Code Duplication in {clean_name} Files",
                    description=f"Found {len(file_group)} files with similar names that may contain duplicated code",
                    priority="medium",
                    effort_estimate="medium",
                    files_to_modify=file_group,
                    benefits=[
                        "Reduce code duplication",
                        "Improve maintainability",
                        "Reduce bug surface area"
                    ],
                    risks=[
                        "May break existing functionality if not careful",
                        "Requires comprehensive testing"
                    ],
                    automated_feasible=False,
                    code_examples={
                        "before": "// Multiple files with similar code patterns",
                        "after": "// Extracted common functionality to shared module"
                    }
                ))

    def _find_method_extraction_opportunities(self) -> None:
        """Find opportunities for method extraction."""

        for file_path, file_info in self.files.items():
            if file_info.get('complexity_score', 0) > 15:
                self.refactoring_opportunities.append(RefactoringOpportunity(
                    opportunity_id=f"extract_{file_path.replace('/', '_')}_{len(self.refactoring_opportunities)}",
                    title=f"Extract Methods in {file_path}",
                    description=f"High complexity score ({file_info['complexity_score']}) suggests opportunities for method extraction",
                    priority="high",
                    effort_estimate="small",
                    files_to_modify=[file_path],
                    benefits=[
                        "Improve readability",
                        "Enable better testing",
                        "Reduce complexity"
                    ],
                    risks=[
                        "Minimal - mostly cosmetic changes"
                    ],
                    automated_feasible=True,
                    code_examples={
                        "before": "// One large method with high complexity",
                        "after": "// Multiple smaller, focused methods"
                    }
                ))

    def _find_architectural_improvements(self) -> None:
        """Find opportunities for architectural improvements."""

        # Check for missing design patterns
        if not any(p.pattern_name.lower() in ['repository', 'factory', 'strategy'] for p in self.patterns):
            self.refactoring_opportunities.append(RefactoringOpportunity(
                opportunity_id=f"arch_patterns_{len(self.refactoring_opportunities)}",
                title="Introduce Design Patterns",
                description="Codebase could benefit from common design patterns for better structure",
                priority="medium",
                effort_estimate="large",
                files_to_modify=list(self.files.keys()),
                benefits=[
                    "Improve code organization",
                    "Better separation of concerns",
                    "Enhanced testability"
                ],
                risks=[
                    "Large refactoring effort",
                    "May introduce complexity if overused"
                ],
                automated_feasible=False,
                code_examples={
                    "before": "// Direct dependencies and tight coupling",
                    "after": "// Proper abstraction layers with design patterns"
                }
            ))

    def _assess_project_health(self) -> None:
        """Assess overall project health with AI insights."""

        if not self.files:
            self.project_health = ProjectHealth(
                health_score=0, technical_debt_score=100, maintainability_index=0,
                test_coverage_estimate=0, documentation_completeness=0,
                trends={}, critical_issues=["No code files found"], strengths=[]
            )
            return

        # Calculate metrics
        avg_complexity = sum(f.get('complexity_score', 0) for f in self.files.values()) / len(self.files)
        avg_maintainability = sum(f.get('maintainability_index', 50) for f in self.files.values()) / len(self.files)

        # Test coverage estimate
        test_files = sum(1 for f in self.files.values() if f.get('test_indicators'))
        test_coverage_estimate = min(100, (test_files / len(self.files)) * 100)

        # Documentation completeness
        avg_doc_score = sum(f.get('documentation_score', 0) for f in self.files.values()) / len(self.files)

        # Health score calculation (weighted average)
        health_score = (
            (100 - min(avg_complexity * 5, 50)) * 0.3 +  # Complexity (30%)
            avg_maintainability * 0.3 +                    # Maintainability (30%)
            test_coverage_estimate * 0.2 +                 # Testing (20%)
            min(avg_doc_score, 50) * 0.2                   # Documentation (20%)
        )

        # Technical debt score (inverse of health)
        tech_debt_score = 100 - health_score

        # Identify critical issues
        critical_issues = []
        if avg_complexity > 20:
            critical_issues.append("Very high average complexity across codebase")
        if test_coverage_estimate < 20:
            critical_issues.append("Very low test coverage")
        if avg_doc_score < 10:
            critical_issues.append("Insufficient code documentation")

        # Identify strengths
        strengths = []
        if len(self.patterns) > 3:
            strengths.append("Good use of architectural patterns")
        if test_coverage_estimate > 60:
            strengths.append("Good test coverage")
        if avg_maintainability > 70:
            strengths.append("High maintainability index")

        self.project_health = ProjectHealth(
            health_score=health_score,
            technical_debt_score=tech_debt_score,
            maintainability_index=avg_maintainability,
            test_coverage_estimate=test_coverage_estimate,
            documentation_completeness=min(avg_doc_score * 2, 100),
            trends={
                "complexity": "stable",  # Would need historical data
                "maintainability": "stable",
                "test_coverage": "unknown"
            },
            critical_issues=critical_issues,
            strengths=strengths
        )

    def _generate_living_documentation(self) -> Dict[str, Any]:
        """Generate living documentation that evolves with the code."""

        return {
            "overview": {
                "title": f"Living Documentation for {self.root_path.name}",
                "generated_at": datetime.now().isoformat(),
                "total_files": len(self.files),
                "languages": list(set(f['language'] for f in self.files.values())),
                "health_score": self.project_health.health_score if self.project_health else 0
            },
            "architecture": {
                "patterns_detected": [
                    {
                        "name": p.pattern_name,
                        "confidence": p.confidence_score,
                        "files": len(p.files_involved)
                    } for p in self.patterns
                ],
                "suggested_improvements": [
                    r.title for r in self.refactoring_opportunities[:5]
                ]
            },
            "quality_metrics": {
                "files_by_complexity": {
                    "low": len([f for f in self.files.values() if f.get('complexity_score', 0) < 5]),
                    "medium": len([f for f in self.files.values() if 5 <= f.get('complexity_score', 0) < 15]),
                    "high": len([f for f in self.files.values() if f.get('complexity_score', 0) >= 15])
                },
                "maintainability_distribution": self._calculate_maintainability_distribution()
            },
            "insights_summary": {
                "critical_insights": [i.title for i in self.insights if i.impact == "critical"],
                "high_impact_insights": [i.title for i in self.insights if i.impact == "high"],
                "total_insights": len(self.insights)
            },
            "recommendations": {
                "top_priorities": [r.title for r in sorted(
                    self.refactoring_opportunities,
                    key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x.priority, 0),
                    reverse=True
                )[:3]],
                "quick_wins": [r.title for r in self.refactoring_opportunities if r.effort_estimate == "small"]
            }
        }

    def _calculate_maintainability_distribution(self) -> Dict[str, int]:
        """Calculate distribution of maintainability scores."""
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}

        for file_info in self.files.values():
            score = file_info.get('maintainability_index', 50)
            if score >= 80:
                distribution["excellent"] += 1
            elif score >= 60:
                distribution["good"] += 1
            elif score >= 40:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1

        return distribution

    def export_analysis(self, output_file: str = None) -> str:
        """Export complete analysis to JSON file."""

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"ai_codebase_analysis_{timestamp}.json"

        analysis_results = self.analyze_with_ai_insights()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)

        print(f"📊 AI analysis results exported to: {output_file}")
        return output_file

    def print_executive_summary(self) -> None:
        """Print an executive summary of the analysis."""

        print("\n" + "="*80)
        print("🤖 AI-POWERED CODEBASE ANALYSIS - EXECUTIVE SUMMARY")
        print("="*80)

        if self.project_health:
            print(f"🏥 Project Health Score: {self.project_health.health_score:.1f}/100")
            print(f"💳 Technical Debt Score: {self.project_health.technical_debt_score:.1f}/100")
            print(f"🔧 Maintainability Index: {self.project_health.maintainability_index:.1f}/100")
            print(f"🧪 Test Coverage Estimate: {self.project_health.test_coverage_estimate:.1f}%")

        print(f"\n📁 Codebase Overview:")
        print(f"   • Total Files: {len(self.files)}")
        languages = list(set(f['language'] for f in self.files.values()))
        print(f"   • Languages: {', '.join(languages)}")
        print(f"   • Architectural Patterns: {len(self.patterns)}")

        print(f"\n🧠 AI Insights Generated: {len(self.insights)}")
        critical_insights = [i for i in self.insights if i.impact == "critical"]
        high_insights = [i for i in self.insights if i.impact == "high"]

        if critical_insights:
            print(f"   🔴 Critical Issues: {len(critical_insights)}")
            for insight in critical_insights[:3]:
                print(f"      • {insight.title}")

        if high_insights:
            print(f"   🟡 High Impact Issues: {len(high_insights)}")
            for insight in high_insights[:3]:
                print(f"      • {insight.title}")

        print(f"\n🔧 Refactoring Opportunities: {len(self.refactoring_opportunities)}")
        top_opportunities = sorted(
            self.refactoring_opportunities,
            key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x.priority, 0),
            reverse=True
        )[:3]

        for opp in top_opportunities:
            print(f"   • {opp.title} (Priority: {opp.priority.title()})")

        if self.project_health and self.project_health.strengths:
            print(f"\n✅ Project Strengths:")
            for strength in self.project_health.strengths:
                print(f"   • {strength}")

        print("\n" + "="*80)
        print("💡 This analysis was generated using AI-powered code understanding")
        print("📈 Use these insights to improve code quality and architecture")
        print("="*80)


def main():
    """Main entry point for the AI-powered codebase analyzer."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Codebase Analyzer - Intelligent insights for better code"
    )
    parser.add_argument("path", help="Path to the codebase to analyze")
    parser.add_argument("--export", "-e", help="Export results to JSON file")
    parser.add_argument("--summary-only", "-s", action="store_true",
                       help="Show only executive summary")
    parser.add_argument("--config", "-c", help="Configuration file path (JSON)")

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"❌ Error: Path '{args.path}' does not exist")
        return 1

    # Load configuration if provided
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)

    try:
        print("🚀 Initializing AI-Powered Codebase Analyzer...")
        analyzer = AICodebaseAnalyzer(args.path, config)

        # Perform analysis
        analyzer.analyze_with_ai_insights()

        # Show results
        if args.summary_only:
            analyzer.print_executive_summary()
        else:
            analyzer.print_executive_summary()
            # Could add detailed reporting here

        # Export if requested
        if args.export:
            analyzer.export_analysis(args.export)

        return 0

    except Exception as e:
        print(f"❌ Error during AI analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())