#!/usr/bin/env python3
"""
Collaborative Code Analysis Tool
Created by Dave & Tara - Two Claude Code instances working together

This tool analyzes codebases to provide structural and quality insights.
Architecture: Modular design allowing different AI contributors to focus on different aspects.
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class FileInfo:
    """Information about a single file in the codebase."""
    path: str
    size: int
    lines: int
    language: str
    imports: List[str]
    functions: List[str]
    classes: List[str]


class StructuralAnalyzer:
    """
    Dave's contribution: Focuses on codebase structure, organization, and dependencies.

    This analyzer examines:
    - File and directory organization
    - Import relationships and dependencies
    - Module structure and hierarchy
    - Architectural patterns
    """

    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'header'
        }

    def analyze_directory_structure(self, root_path: str) -> Dict[str, Any]:
        """Analyze the overall directory structure and organization."""
        structure = {
            'total_files': 0,
            'languages': defaultdict(int),
            'directory_depth': 0,
            'largest_directories': [],
            'file_distribution': {}
        }

        for root, dirs, files in os.walk(root_path):
            level = root.replace(root_path, '').count(os.sep)
            structure['directory_depth'] = max(structure['directory_depth'], level)

            for file in files:
                ext = Path(file).suffix.lower()
                if ext in self.supported_extensions:
                    structure['total_files'] += 1
                    lang = self.supported_extensions[ext]
                    structure['languages'][lang] += 1

        return structure

    def analyze_python_file(self, file_path: str) -> FileInfo:
        """Analyze a Python file for structural information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            imports = []
            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

            return FileInfo(
                path=file_path,
                size=len(content),
                lines=len(content.split('\n')),
                language='python',
                imports=imports,
                functions=functions,
                classes=classes
            )

        except Exception as e:
            return FileInfo(file_path, 0, 0, 'python', [], [], [])

    def analyze_codebase(self, root_path: str) -> Dict[str, Any]:
        """Main entry point for structural analysis."""
        results = {
            'structure': self.analyze_directory_structure(root_path),
            'files': [],
            'dependencies': defaultdict(list),
            'analyzer': 'Dave (StructuralAnalyzer)'
        }

        # Analyze individual files
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_info = self.analyze_python_file(file_path)
                    results['files'].append(file_info.__dict__)

                    # Build dependency graph
                    for imp in file_info.imports:
                        results['dependencies'][file_info.path].append(imp)

        return results


class QualityAnalyzer:
    """
    Tara's contribution: Focuses on code quality, maintainability, and potential issues.

    This analyzer examines:
    - Cyclomatic complexity and maintainability metrics
    - Code smell detection and anti-patterns
    - Readability and documentation quality
    - Potential security and performance issues
    """

    def __init__(self):
        self.quality_thresholds = {
            'max_function_length': 50,
            'max_complexity': 10,
            'min_docstring_coverage': 0.7,
            'max_nesting_depth': 4
        }

    def analyze_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of an AST node."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Decision points that increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try,
                                ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp)):
                complexity += 1

        return complexity

    def detect_code_smells(self, file_info: Dict[str, Any], content: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect various code smells and anti-patterns."""
        smells = []

        # Analyze function-level issues
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Long functions
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > self.quality_thresholds['max_function_length']:
                    smells.append({
                        'type': 'long_function',
                        'severity': 'medium',
                        'location': f"Function '{node.name}' at line {node.lineno}",
                        'message': f"Function is {func_lines} lines long (threshold: {self.quality_thresholds['max_function_length']})"
                    })

                # High complexity
                complexity = self.analyze_complexity(node)
                if complexity > self.quality_thresholds['max_complexity']:
                    smells.append({
                        'type': 'high_complexity',
                        'severity': 'high',
                        'location': f"Function '{node.name}' at line {node.lineno}",
                        'message': f"Cyclomatic complexity is {complexity} (threshold: {self.quality_thresholds['max_complexity']})"
                    })

                # Missing docstrings
                if not ast.get_docstring(node):
                    smells.append({
                        'type': 'missing_docstring',
                        'severity': 'low',
                        'location': f"Function '{node.name}' at line {node.lineno}",
                        'message': "Function lacks documentation"
                    })

        # Global file-level smells
        lines = content.split('\n')

        # Too many imports
        import_count = sum(1 for line in lines if line.strip().startswith(('import ', 'from ')))
        if import_count > 20:
            smells.append({
                'type': 'too_many_imports',
                'severity': 'medium',
                'location': 'File level',
                'message': f"File has {import_count} import statements"
            })

        # Very long files
        if len(lines) > 500:
            smells.append({
                'type': 'long_file',
                'severity': 'medium',
                'location': 'File level',
                'message': f"File is {len(lines)} lines long"
            })

        return smells

    def analyze_maintainability(self, file_info: Dict[str, Any], content: str, tree: ast.AST) -> Dict[str, Any]:
        """Calculate maintainability metrics."""
        metrics = {
            'avg_function_complexity': 0,
            'total_functions': 0,
            'documented_functions': 0,
            'max_nesting_depth': 0,
            'maintainability_score': 0
        }

        function_complexities = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['total_functions'] += 1

                # Complexity
                complexity = self.analyze_complexity(node)
                function_complexities.append(complexity)

                # Documentation
                if ast.get_docstring(node):
                    metrics['documented_functions'] += 1

                # Nesting depth (simplified estimation)
                max_depth = self._estimate_nesting_depth(node)
                metrics['max_nesting_depth'] = max(metrics['max_nesting_depth'], max_depth)

        if function_complexities:
            metrics['avg_function_complexity'] = sum(function_complexities) / len(function_complexities)

        # Calculate overall maintainability score (0-100)
        doc_ratio = metrics['documented_functions'] / max(metrics['total_functions'], 1)
        complexity_penalty = min(metrics['avg_function_complexity'] / 5, 1)  # Normalize to 0-1
        nesting_penalty = min(metrics['max_nesting_depth'] / 6, 1)  # Normalize to 0-1

        metrics['maintainability_score'] = max(0, 100 - (
            (1 - doc_ratio) * 30 +  # Documentation weight: 30%
            complexity_penalty * 40 +  # Complexity weight: 40%
            nesting_penalty * 30  # Nesting weight: 30%
        ))

        return metrics

    def _estimate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Estimate maximum nesting depth in a function."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._estimate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._estimate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def analyze_file_quality(self, file_path: str) -> Dict[str, Any]:
        """Analyze quality metrics for a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Get basic file info (reusing some of Dave's logic)
            file_info = {
                'path': file_path,
                'size': len(content),
                'lines': len(content.split('\n'))
            }

            return {
                'file_info': file_info,
                'code_smells': self.detect_code_smells(file_info, content, tree),
                'maintainability': self.analyze_maintainability(file_info, content, tree),
                'analyzer': 'Tara (QualityAnalyzer)'
            }

        except Exception as e:
            return {
                'file_info': {'path': file_path, 'error': str(e)},
                'code_smells': [],
                'maintainability': {},
                'analyzer': 'Tara (QualityAnalyzer)'
            }

    def analyze_codebase_quality(self, root_path: str) -> Dict[str, Any]:
        """Main entry point for quality analysis."""
        results = {
            'overall_quality': {
                'total_smells': 0,
                'avg_maintainability': 0,
                'quality_distribution': {'high': 0, 'medium': 0, 'low': 0}
            },
            'files': [],
            'analyzer': 'Tara (QualityAnalyzer)'
        }

        file_scores = []
        total_smells = 0

        # Analyze each Python file
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    quality_analysis = self.analyze_file_quality(file_path)
                    results['files'].append(quality_analysis)

                    # Track overall metrics
                    if 'maintainability' in quality_analysis and 'maintainability_score' in quality_analysis['maintainability']:
                        score = quality_analysis['maintainability']['maintainability_score']
                        file_scores.append(score)

                        # Categorize quality
                        if score >= 75:
                            results['overall_quality']['quality_distribution']['high'] += 1
                        elif score >= 50:
                            results['overall_quality']['quality_distribution']['medium'] += 1
                        else:
                            results['overall_quality']['quality_distribution']['low'] += 1

                    total_smells += len(quality_analysis.get('code_smells', []))

        # Calculate averages
        if file_scores:
            results['overall_quality']['avg_maintainability'] = sum(file_scores) / len(file_scores)
        results['overall_quality']['total_smells'] = total_smells

        return results


class CollaborativeCodeAnalyzer:
    """
    Combined analyzer that coordinates both structural and quality analysis.
    Demonstrates how two AI agents can work together on complementary aspects.
    """

    def __init__(self):
        self.structural_analyzer = StructuralAnalyzer()
        self.quality_analyzer = QualityAnalyzer()

    def analyze(self, root_path: str) -> Dict[str, Any]:
        """Run both structural and quality analysis, then merge results."""
        print("🏗️  Dave analyzing structure and dependencies...")
        structural_results = self.structural_analyzer.analyze_codebase(root_path)

        print("🔍 Tara analyzing code quality and maintainability...")
        quality_results = self.quality_analyzer.analyze_codebase_quality(root_path)

        # Merge and cross-reference results
        combined_results = {
            'meta': {
                'collaboration': 'Dave (Structure) + Tara (Quality)',
                'timestamp': str(Path('.').stat().st_mtime),
                'analyzed_path': root_path
            },
            'structural_analysis': structural_results,
            'quality_analysis': quality_results,
            'insights': self._generate_insights(structural_results, quality_results)
        }

        return combined_results

    def _generate_insights(self, structural: Dict, quality: Dict) -> List[str]:
        """Generate collaborative insights by combining both analyses."""
        insights = []

        # Cross-analyze structure vs quality
        total_files = len(structural.get('files', []))
        if total_files > 0 and quality['overall_quality']['avg_maintainability'] < 60:
            insights.append(f"📊 Codebase has {total_files} files with below-average maintainability ({quality['overall_quality']['avg_maintainability']:.1f}/100)")

        # Language diversity vs complexity
        languages = structural['structure']['languages']
        if len(languages) > 3 and quality['overall_quality']['total_smells'] > total_files * 2:
            insights.append(f"🌐 Multi-language codebase ({len(languages)} languages) with high smell density - consider consolidation")

        # Dependency complexity
        total_deps = sum(len(deps) for deps in structural['dependencies'].values())
        if total_deps > total_files * 3:
            insights.append(f"🕸️  High dependency density detected ({total_deps} imports across {total_files} files)")

        return insights

def main():
    """Main entry point for the collaborative analysis tool."""
    import sys

    print("🤖 Collaborative Code Analysis Tool")
    print("Created by Dave (Structure) & Tara (Quality) - Two Claude Code instances")
    print()

    if len(sys.argv) < 2:
        print("Usage: python codebase_analyzer.py <path_to_analyze>")
        print("Example: python codebase_analyzer.py /path/to/your/project")
        return

    target_path = sys.argv[1]
    if not os.path.exists(target_path):
        print(f"❌ Error: Path '{target_path}' does not exist")
        return

    print(f"📂 Analyzing: {target_path}")
    print("-" * 50)

    # Run collaborative analysis
    analyzer = CollaborativeCodeAnalyzer()
    results = analyzer.analyze(target_path)

    # Display results
    print("\n📋 ANALYSIS RESULTS:")
    print("=" * 50)

    # Structural summary
    struct = results['structural_analysis']['structure']
    print(f"📁 Total Files: {struct['total_files']}")
    print(f"🏗️  Directory Depth: {struct['directory_depth']}")
    print(f"💬 Languages: {dict(struct['languages'])}")

    # Quality summary
    quality = results['quality_analysis']['overall_quality']
    print(f"🎯 Avg Maintainability: {quality['avg_maintainability']:.1f}/100")
    print(f"⚠️  Total Code Smells: {quality['total_smells']}")
    print(f"📊 Quality Distribution: {dict(quality['quality_distribution'])}")

    # Collaborative insights
    if results['insights']:
        print("\n💡 COLLABORATIVE INSIGHTS:")
        for insight in results['insights']:
            print(f"   {insight}")

    # Save detailed results
    output_file = "analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Detailed results saved to: {output_file}")

    print("\n🤝 Analysis complete! This was a collaboration between:")
    print("   🏗️  Dave: Structural analysis & dependencies")
    print("   🔍 Tara: Quality metrics & maintainability")


if __name__ == "__main__":
    main()