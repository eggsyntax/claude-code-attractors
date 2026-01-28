#!/usr/bin/env python3
"""
Collaborative Code Analyzer - Visualization Module
Interactive visualization and dashboard functionality for code analysis results.

Created by: Alice & Bob (Claude Code Collaboration)
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

import pandas as pd

from code_analyzer import CodeMetrics, analyze_codebase

# Configure logging
logger = logging.getLogger(__name__)


class CodeVisualizer:
    """Interactive visualization engine for code analysis results."""

    def __init__(self, theme: str = "plotly_white"):
        """
        Initialize the visualizer.

        Args:
            theme: Plotly theme to use for visualizations
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("plotly is required for visualization. Install with: pip install plotly pandas")

        self.theme = theme
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def create_metrics_dataframe(self, metrics_list: List[CodeMetrics]) -> pd.DataFrame:
        """
        Convert list of CodeMetrics to pandas DataFrame for easier manipulation.

        Args:
            metrics_list: List of CodeMetrics objects

        Returns:
            DataFrame with metrics data
        """
        if not metrics_list:
            return pd.DataFrame()

        data = []
        for metrics in metrics_list:
            data.append({
                'file_path': metrics.file_path,
                'file_name': Path(metrics.file_path).name,
                'lines_of_code': metrics.lines_of_code,
                'complexity': metrics.complexity,
                'function_count': metrics.function_count,
                'class_count': metrics.class_count,
                'import_count': metrics.import_count,
                'functions': ', '.join(metrics.functions),
                'classes': ', '.join(metrics.classes),
                'dependencies': ', '.join(metrics.dependencies)
            })

        return pd.DataFrame(data)

    def create_complexity_histogram(self, df: pd.DataFrame) -> go.Figure:
        """Create histogram of code complexity distribution."""
        fig = px.histogram(
            df, x='complexity',
            title='Code Complexity Distribution',
            labels={'complexity': 'Cyclomatic Complexity', 'count': 'Number of Files'},
            template=self.theme
        )

        fig.add_vline(
            x=df['complexity'].mean(),
            line_dash="dash",
            line_color="red",
            annotation_text=f"Average: {df['complexity'].mean():.1f}"
        )

        return fig

    def create_file_size_scatter(self, df: pd.DataFrame) -> go.Figure:
        """Create scatter plot of file size vs complexity."""
        fig = px.scatter(
            df, x='lines_of_code', y='complexity',
            hover_data=['file_name', 'function_count', 'class_count'],
            title='File Size vs Complexity',
            labels={'lines_of_code': 'Lines of Code', 'complexity': 'Cyclomatic Complexity'},
            template=self.theme
        )

        # Add trend line
        fig.add_traces(px.scatter(df, x='lines_of_code', y='complexity', trendline="ols").data[1:])

        return fig

    def create_metrics_summary_bar(self, df: pd.DataFrame) -> go.Figure:
        """Create bar chart summarizing key metrics."""
        summary = {
            'Total Files': len(df),
            'Total Functions': df['function_count'].sum(),
            'Total Classes': df['class_count'].sum(),
            'Total Lines': df['lines_of_code'].sum(),
            'Avg Complexity': df['complexity'].mean()
        }

        fig = go.Figure([
            go.Bar(
                x=list(summary.keys()),
                y=list(summary.values()),
                text=[f"{v:.1f}" if k == 'Avg Complexity' else f"{int(v)}" for k, v in summary.items()],
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='Codebase Summary Metrics',
            yaxis_title='Count/Value',
            template=self.theme
        )

        return fig

    def create_dependency_network(self, df: pd.DataFrame) -> go.Figure:
        """Create network visualization of dependencies (simplified)."""
        # Count dependency frequencies
        all_deps = []
        for deps_str in df['dependencies'].dropna():
            if deps_str:  # Check for non-empty strings
                all_deps.extend(deps_str.split(', '))

        dep_counts = pd.Series(all_deps).value_counts().head(20)  # Top 20 dependencies

        fig = go.Figure([
            go.Bar(
                x=dep_counts.index,
                y=dep_counts.values,
                text=dep_counts.values,
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='Top Dependencies',
            xaxis_title='Module/Package',
            yaxis_title='Usage Count',
            template=self.theme,
            xaxis_tickangle=-45
        )

        return fig

    def create_comprehensive_dashboard(self, metrics_list: List[CodeMetrics]) -> str:
        """
        Create a comprehensive dashboard with multiple visualizations.

        Args:
            metrics_list: List of CodeMetrics objects

        Returns:
            Path to the generated HTML dashboard file
        """
        if not metrics_list:
            self.logger.warning("No metrics provided for dashboard creation")
            return ""

        df = self.create_metrics_dataframe(metrics_list)
        self.logger.info(f"Creating dashboard for {len(df)} files")

        # Create subplot figure with multiple charts
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Complexity Distribution', 'File Size vs Complexity',
                          'Codebase Summary', 'Top Dependencies'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Add complexity histogram
        complexity_hist = px.histogram(df, x='complexity').data[0]
        fig.add_trace(complexity_hist, row=1, col=1)

        # Add scatter plot
        scatter = px.scatter(df, x='lines_of_code', y='complexity').data[0]
        fig.add_trace(scatter, row=1, col=2)

        # Add summary bars
        summary = {
            'Files': len(df),
            'Functions': df['function_count'].sum(),
            'Classes': df['class_count'].sum(),
            'Lines': df['lines_of_code'].sum()
        }
        summary_bar = go.Bar(x=list(summary.keys()), y=list(summary.values()))
        fig.add_trace(summary_bar, row=2, col=1)

        # Add dependency chart
        all_deps = []
        for deps_str in df['dependencies'].dropna():
            if deps_str:
                all_deps.extend(deps_str.split(', '))

        if all_deps:
            dep_counts = pd.Series(all_deps).value_counts().head(10)
            dep_bar = go.Bar(x=dep_counts.index, y=dep_counts.values)
            fig.add_trace(dep_bar, row=2, col=2)

        fig.update_layout(
            height=800,
            title_text="Code Analysis Dashboard",
            template=self.theme,
            showlegend=False
        )

        # Generate HTML file
        output_path = Path("/tmp/cc-exp/run_2026-01-23_18-59-03/output/dashboard.html")
        fig.write_html(str(output_path))

        self.logger.info(f"Dashboard saved to: {output_path}")
        return str(output_path)

    def export_to_json(self, metrics_list: List[CodeMetrics],
                      output_path: Union[str, Path]) -> None:
        """
        Export metrics data to JSON format.

        Args:
            metrics_list: List of CodeMetrics objects
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)

        # Convert to serializable format
        data = []
        for metrics in metrics_list:
            data.append({
                'file_path': metrics.file_path,
                'lines_of_code': metrics.lines_of_code,
                'complexity': metrics.complexity,
                'function_count': metrics.function_count,
                'class_count': metrics.class_count,
                'import_count': metrics.import_count,
                'functions': metrics.functions,
                'classes': metrics.classes,
                'dependencies': metrics.dependencies
            })

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        self.logger.info(f"Data exported to: {output_path}")

    def export_to_csv(self, metrics_list: List[CodeMetrics],
                     output_path: Union[str, Path]) -> None:
        """
        Export metrics data to CSV format.

        Args:
            metrics_list: List of CodeMetrics objects
            output_path: Path to save CSV file
        """
        df = self.create_metrics_dataframe(metrics_list)
        df.to_csv(output_path, index=False)

        self.logger.info(f"Data exported to: {output_path}")


def visualize_codebase(directory: Union[str, Path],
                      output_format: str = "html") -> str:
    """
    Convenience function to analyze and visualize a codebase.

    Args:
        directory: Path to the codebase directory
        output_format: Output format ("html", "json", "csv")

    Returns:
        Path to the generated output file
    """
    # Analyze the codebase using Bob's analyzer
    metrics = analyze_codebase(directory)

    if not metrics:
        logger.warning(f"No Python files found in {directory}")
        return ""

    # Create visualizer and generate output
    visualizer = CodeVisualizer()

    if output_format.lower() == "html":
        return visualizer.create_comprehensive_dashboard(metrics)
    elif output_format.lower() == "json":
        output_path = Path("/tmp/cc-exp/run_2026-01-23_18-59-03/output/analysis_results.json")
        visualizer.export_to_json(metrics, output_path)
        return str(output_path)
    elif output_format.lower() == "csv":
        output_path = Path("/tmp/cc-exp/run_2026-01-23_18-59-03/output/analysis_results.csv")
        visualizer.export_to_csv(metrics, output_path)
        return str(output_path)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


if __name__ == "__main__":
    # Command line interface for visualization
    import sys

    if len(sys.argv) < 2:
        print("Usage: python visualizer.py <directory> [output_format]")
        print("Output formats: html (default), json, csv")
        sys.exit(1)

    directory = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "html"

    try:
        output_path = visualize_codebase(directory, output_format)
        if output_path:
            print(f"Visualization saved to: {output_path}")
        else:
            print("No files to analyze!")
    except Exception as e:
        print(f"Error creating visualization: {e}")
        sys.exit(1)