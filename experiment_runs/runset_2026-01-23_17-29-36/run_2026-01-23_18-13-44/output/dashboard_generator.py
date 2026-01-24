#!/usr/bin/env python3
"""
Dashboard Generator for Code Analysis Visualization

This module integrates our AST analyzer and complexity analyzer to generate
interactive HTML dashboards with real-time code analysis data.

Author: Alice & Bob (Collaborative AI Development)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import webbrowser
import tempfile
from ast_analyzer import CodeAnalyzer
from complexity_analyzer import ComplexityAnalyzer


class DashboardGenerator:
    """
    Generates interactive HTML dashboards from code analysis results.

    Combines structural analysis (AST) with complexity metrics to create
    comprehensive visualizations of codebase health and maintainability.
    """

    def __init__(self, output_dir: str = None):
        """
        Initialize the dashboard generator.

        Args:
            output_dir: Directory to save generated dashboards. If None, uses temp directory.
        """
        self.ast_analyzer = CodeAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir())
        self.analysis_results = {}

    def analyze_project(self, project_path: str, file_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Analyze an entire project directory for code quality metrics.

        Args:
            project_path: Path to the project root directory
            file_patterns: List of file patterns to analyze (default: ['*.py'])

        Returns:
            Comprehensive analysis results dictionary
        """
        if file_patterns is None:
            file_patterns = ['*.py']

        project_path = Path(project_path)
        all_functions = []
        all_classes = []
        all_dependencies = []
        file_analyses = {}

        # Find all matching files
        python_files = []
        for pattern in file_patterns:
            python_files.extend(project_path.rglob(pattern))

        print(f"📁 Analyzing {len(python_files)} Python files...")

        for file_path in python_files:
            try:
                # Structural analysis
                ast_results = self.ast_analyzer.analyze_file(str(file_path))

                # Complexity analysis for each function
                enhanced_functions = []
                for func_info in ast_results.get('functions', []):
                    try:
                        complexity_results = self.complexity_analyzer.analyze_function_by_name(
                            str(file_path), func_info['name']
                        )

                        enhanced_func = {
                            **func_info,
                            'file': file_path.name,
                            'full_path': str(file_path),
                            'cyclomatic_complexity': complexity_results.get('cyclomatic_complexity', 0),
                            'cognitive_complexity': complexity_results.get('cognitive_complexity', 0),
                            'complexity_rating': complexity_results.get('rating', 'Unknown'),
                            'max_nesting': complexity_results.get('max_nesting_depth', 0)
                        }
                        enhanced_functions.append(enhanced_func)
                        all_functions.append(enhanced_func)

                    except Exception as e:
                        print(f"⚠️  Could not analyze complexity for {func_info['name']}: {e}")
                        # Add function with basic info only
                        enhanced_func = {
                            **func_info,
                            'file': file_path.name,
                            'full_path': str(file_path),
                            'cyclomatic_complexity': 0,
                            'cognitive_complexity': 0,
                            'complexity_rating': 'Unknown',
                            'max_nesting': 0
                        }
                        enhanced_functions.append(enhanced_func)
                        all_functions.append(enhanced_func)

                # Collect classes and dependencies
                all_classes.extend([{**cls, 'file': file_path.name} for cls in ast_results.get('classes', [])])
                all_dependencies.extend([{**dep, 'from_file': file_path.name} for dep in ast_results.get('imports', [])])

                file_analyses[str(file_path)] = {
                    'functions': enhanced_functions,
                    'classes': ast_results.get('classes', []),
                    'imports': ast_results.get('imports', [])
                }

                print(f"✅ Analyzed {file_path.name}: {len(enhanced_functions)} functions")

            except Exception as e:
                print(f"❌ Error analyzing {file_path}: {e}")
                continue

        # Calculate project-level metrics
        total_functions = len(all_functions)
        total_classes = len(all_classes)
        total_files = len(file_analyses)

        complexities = [f['cyclomatic_complexity'] for f in all_functions if f['cyclomatic_complexity'] > 0]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        high_complexity_functions = len([f for f in all_functions if f['cyclomatic_complexity'] > 10])

        # Process dependencies for visualization
        processed_dependencies = []
        for dep in all_dependencies:
            if dep['module'] and not dep['module'].startswith('.'):  # Skip relative imports
                processed_dependencies.append({
                    'from': dep['from_file'],
                    'to': dep['module'],
                    'type': 'import',
                    'alias': dep.get('alias')
                })

        self.analysis_results = {
            'overview': {
                'totalFunctions': total_functions,
                'totalClasses': total_classes,
                'totalFiles': total_files,
                'avgComplexity': round(avg_complexity, 2),
                'highComplexityFunctions': high_complexity_functions
            },
            'functions': all_functions,
            'classes': all_classes,
            'dependencies': processed_dependencies,
            'files': list(file_analyses.keys()),
            'fileAnalyses': file_analyses
        }

        return self.analysis_results

    def generate_dashboard(self, template_path: str = None, output_filename: str = None) -> str:
        """
        Generate an interactive HTML dashboard with analysis results.

        Args:
            template_path: Path to HTML template file
            output_filename: Name for the output HTML file

        Returns:
            Path to the generated dashboard file
        """
        if not self.analysis_results:
            raise ValueError("No analysis results available. Run analyze_project() first.")

        # Use the dashboard template we created
        if template_path is None:
            template_path = self.output_dir / 'visualization_dashboard.html'

        if output_filename is None:
            output_filename = 'code_analysis_dashboard.html'

        # Read the template
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Inject real data into the JavaScript
        analysis_json = json.dumps(self.analysis_results, indent=2)

        # Replace the sample data generation with real data
        updated_content = template_content.replace(
            'analysisData = generateSampleData();',
            f'analysisData = {analysis_json};'
        ).replace(
            '// This would typically load from our Python analysis',
            '// Real data injected from Python analysis'
        )

        # Update title with project info
        project_info = f"Code Analysis Dashboard - {self.analysis_results['overview']['totalFiles']} files analyzed"
        updated_content = updated_content.replace(
            '<title>Code Analysis Dashboard</title>',
            f'<title>{project_info}</title>'
        ).replace(
            'Interactive visualization of code complexity and structure',
            f"Analysis of {self.analysis_results['overview']['totalFiles']} Python files"
        )

        # Save the generated dashboard
        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"🎨 Dashboard generated: {output_path}")
        return str(output_path)

    def analyze_and_visualize(self, project_path: str, open_browser: bool = True) -> str:
        """
        Complete analysis and dashboard generation in one step.

        Args:
            project_path: Path to the project to analyze
            open_browser: Whether to automatically open the dashboard in browser

        Returns:
            Path to the generated dashboard file
        """
        print(f"🔍 Starting complete analysis of: {project_path}")

        # Analyze the project
        self.analyze_project(project_path)

        # Generate dashboard
        dashboard_path = self.generate_dashboard()

        # Optionally open in browser
        if open_browser:
            try:
                webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
                print(f"🌐 Dashboard opened in browser: {dashboard_path}")
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}")
                print(f"📂 Manual access: file://{os.path.abspath(dashboard_path)}")

        return dashboard_path

    def print_summary(self):
        """Print a text summary of the analysis results."""
        if not self.analysis_results:
            print("No analysis results available.")
            return

        overview = self.analysis_results['overview']
        functions = self.analysis_results['functions']

        print("\n" + "="*60)
        print("📊 CODE ANALYSIS SUMMARY")
        print("="*60)
        print(f"📁 Total Files: {overview['totalFiles']}")
        print(f"🔧 Total Functions: {overview['totalFunctions']}")
        print(f"🏗️  Total Classes: {overview['totalClasses']}")
        print(f"📈 Average Complexity: {overview['avgComplexity']}")
        print(f"⚠️  High Complexity Functions: {overview['highComplexityFunctions']}")

        if functions:
            print("\n🔥 TOP 5 MOST COMPLEX FUNCTIONS:")
            sorted_functions = sorted(
                functions,
                key=lambda f: f.get('cyclomatic_complexity', 0),
                reverse=True
            )[:5]

            for i, func in enumerate(sorted_functions, 1):
                print(f"{i}. {func['name']} ({func['file']})")
                print(f"   📊 Cyclomatic: {func.get('cyclomatic_complexity', 'N/A')}, "
                      f"Cognitive: {func.get('cognitive_complexity', 'N/A')}")
                print(f"   📝 Lines: {func.get('end_line', 0) - func.get('start_line', 0)}, "
                      f"Rating: {func.get('complexity_rating', 'Unknown')}")
        print("="*60)


def main():
    """Command-line interface for the dashboard generator."""
    if len(sys.argv) < 2:
        print("Usage: python dashboard_generator.py <project_path>")
        print("Example: python dashboard_generator.py /path/to/your/project")
        sys.exit(1)

    project_path = sys.argv[1]

    if not os.path.exists(project_path):
        print(f"❌ Project path does not exist: {project_path}")
        sys.exit(1)

    # Create dashboard generator
    output_dir = '/tmp/cc-exp/run_2026-01-23_18-13-44/output'
    generator = DashboardGenerator(output_dir)

    try:
        # Run complete analysis and visualization
        dashboard_path = generator.analyze_and_visualize(project_path)

        # Print summary
        generator.print_summary()

        print(f"\n✅ Analysis complete! Dashboard saved to: {dashboard_path}")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()