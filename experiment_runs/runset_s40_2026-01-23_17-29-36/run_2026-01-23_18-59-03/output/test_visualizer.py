#!/usr/bin/env python3
"""
Test suite for the visualization module.
Following CLAUDE.md guidelines: comprehensive testing for visualization components.

Created by: Alice & Bob (Claude Code Collaboration)
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd

from code_analyzer import CodeMetrics
from visualizer import CodeVisualizer, visualize_codebase


class TestCodeVisualizer(unittest.TestCase):
    """Test cases for the CodeVisualizer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample metrics for testing
        self.sample_metrics = [
            CodeMetrics(
                file_path="/test/file1.py",
                lines_of_code=50,
                complexity=3,
                function_count=2,
                class_count=1,
                import_count=2,
                functions=["func1", "func2"],
                classes=["Class1"],
                dependencies=["os", "sys"]
            ),
            CodeMetrics(
                file_path="/test/file2.py",
                lines_of_code=100,
                complexity=8,
                function_count=5,
                class_count=2,
                import_count=3,
                functions=["func3", "func4", "func5", "func6", "func7"],
                classes=["Class2", "Class3"],
                dependencies=["json", "pathlib", "typing"]
            ),
            CodeMetrics(
                file_path="/test/file3.py",
                lines_of_code=25,
                complexity=2,
                function_count=1,
                class_count=0,
                import_count=1,
                functions=["utility_func"],
                classes=[],
                dependencies=["math"]
            )
        ]

    @patch('visualizer.PLOTLY_AVAILABLE', True)
    def test_visualizer_initialization(self):
        """Test CodeVisualizer initialization."""
        visualizer = CodeVisualizer()
        self.assertEqual(visualizer.theme, "plotly_white")

        visualizer_dark = CodeVisualizer(theme="plotly_dark")
        self.assertEqual(visualizer_dark.theme, "plotly_dark")

    @patch('visualizer.PLOTLY_AVAILABLE', False)
    def test_visualizer_initialization_no_plotly(self):
        """Test CodeVisualizer initialization without plotly."""
        with self.assertRaises(ImportError):
            CodeVisualizer()

    @patch('visualizer.PLOTLY_AVAILABLE', True)
    def test_create_metrics_dataframe(self):
        """Test conversion of metrics to DataFrame."""
        visualizer = CodeVisualizer()
        df = visualizer.create_metrics_dataframe(self.sample_metrics)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertIn('file_path', df.columns)
        self.assertIn('file_name', df.columns)
        self.assertIn('lines_of_code', df.columns)
        self.assertIn('complexity', df.columns)

        # Test specific values
        self.assertEqual(df.iloc[0]['lines_of_code'], 50)
        self.assertEqual(df.iloc[1]['complexity'], 8)
        self.assertEqual(df.iloc[2]['function_count'], 1)

    @patch('visualizer.PLOTLY_AVAILABLE', True)
    def test_create_metrics_dataframe_empty(self):
        """Test DataFrame creation with empty metrics list."""
        visualizer = CodeVisualizer()
        df = visualizer.create_metrics_dataframe([])

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 0)

    @patch('visualizer.PLOTLY_AVAILABLE', True)
    @patch('visualizer.px')
    def test_create_complexity_histogram(self, mock_px):
        """Test complexity histogram creation."""
        mock_fig = MagicMock()
        mock_px.histogram.return_value = mock_fig

        visualizer = CodeVisualizer()
        df = visualizer.create_metrics_dataframe(self.sample_metrics)
        result = visualizer.create_complexity_histogram(df)

        # Verify plotly was called correctly
        mock_px.histogram.assert_called_once()
        call_args = mock_px.histogram.call_args
        self.assertEqual(call_args[1]['x'], 'complexity')
        self.assertIn('Code Complexity Distribution', call_args[1]['title'])

        # Verify add_vline was called (for average line)
        mock_fig.add_vline.assert_called_once()

    @patch('visualizer.PLOTLY_AVAILABLE', True)
    @patch('visualizer.px')
    def test_create_file_size_scatter(self, mock_px):
        """Test scatter plot creation."""
        mock_fig = MagicMock()
        mock_px.scatter.return_value = mock_fig

        visualizer = CodeVisualizer()
        df = visualizer.create_metrics_dataframe(self.sample_metrics)
        result = visualizer.create_file_size_scatter(df)

        # Verify plotly was called correctly
        mock_px.scatter.assert_called()
        call_args = mock_px.scatter.call_args
        self.assertEqual(call_args[1]['x'], 'lines_of_code')
        self.assertEqual(call_args[1]['y'], 'complexity')

    @patch('visualizer.PLOTLY_AVAILABLE', True)
    def test_export_to_json(self):
        """Test JSON export functionality."""
        visualizer = CodeVisualizer()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.json"
            visualizer.export_to_json(self.sample_metrics, output_path)

            # Verify file was created and contains correct data
            self.assertTrue(output_path.exists())

            with open(output_path) as f:
                data = json.load(f)

            self.assertEqual(len(data), 3)
            self.assertEqual(data[0]['file_path'], "/test/file1.py")
            self.assertEqual(data[0]['lines_of_code'], 50)
            self.assertEqual(data[1]['complexity'], 8)

    @patch('visualizer.PLOTLY_AVAILABLE', True)
    def test_export_to_csv(self):
        """Test CSV export functionality."""
        visualizer = CodeVisualizer()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.csv"
            visualizer.export_to_csv(self.sample_metrics, output_path)

            # Verify file was created
            self.assertTrue(output_path.exists())

            # Verify CSV content
            df = pd.read_csv(output_path)
            self.assertEqual(len(df), 3)
            self.assertEqual(df.iloc[0]['lines_of_code'], 50)
            self.assertEqual(df.iloc[1]['complexity'], 8)

    @patch('visualizer.PLOTLY_AVAILABLE', True)
    @patch('visualizer.make_subplots')
    def test_create_comprehensive_dashboard(self, mock_subplots):
        """Test comprehensive dashboard creation."""
        mock_fig = MagicMock()
        mock_subplots.return_value = mock_fig

        visualizer = CodeVisualizer()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the output path to use temp directory
            with patch('visualizer.Path') as mock_path_class:
                mock_output_path = Path(temp_dir) / "dashboard.html"
                mock_path_class.return_value = mock_output_path

                result = visualizer.create_comprehensive_dashboard(self.sample_metrics)

                # Verify subplot creation
                mock_subplots.assert_called_once()

                # Verify figure methods were called
                self.assertTrue(mock_fig.add_trace.called)
                self.assertTrue(mock_fig.update_layout.called)

    @patch('visualizer.PLOTLY_AVAILABLE', True)
    def test_create_comprehensive_dashboard_empty_metrics(self):
        """Test dashboard creation with empty metrics."""
        visualizer = CodeVisualizer()
        result = visualizer.create_comprehensive_dashboard([])

        self.assertEqual(result, "")


class TestVisualizationUtilities(unittest.TestCase):
    """Test cases for utility functions."""

    @patch('visualizer.analyze_codebase')
    @patch('visualizer.CodeVisualizer')
    def test_visualize_codebase_html(self, mock_visualizer_class, mock_analyze):
        """Test visualize_codebase function with HTML output."""
        # Setup mocks
        mock_analyze.return_value = [
            CodeMetrics("/test/file.py", 50, 3, 2, 1, 2, ["func1"], ["Class1"], ["os"])
        ]
        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer
        mock_visualizer.create_comprehensive_dashboard.return_value = "/path/to/dashboard.html"

        result = visualize_codebase("/test/dir", "html")

        # Verify calls
        mock_analyze.assert_called_once_with("/test/dir")
        mock_visualizer.create_comprehensive_dashboard.assert_called_once()
        self.assertEqual(result, "/path/to/dashboard.html")

    @patch('visualizer.analyze_codebase')
    @patch('visualizer.CodeVisualizer')
    def test_visualize_codebase_json(self, mock_visualizer_class, mock_analyze):
        """Test visualize_codebase function with JSON output."""
        mock_analyze.return_value = [
            CodeMetrics("/test/file.py", 50, 3, 2, 1, 2, ["func1"], ["Class1"], ["os"])
        ]
        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer

        result = visualize_codebase("/test/dir", "json")

        mock_visualizer.export_to_json.assert_called_once()
        self.assertTrue(result.endswith("analysis_results.json"))

    @patch('visualizer.analyze_codebase')
    @patch('visualizer.CodeVisualizer')
    def test_visualize_codebase_csv(self, mock_visualizer_class, mock_analyze):
        """Test visualize_codebase function with CSV output."""
        mock_analyze.return_value = [
            CodeMetrics("/test/file.py", 50, 3, 2, 1, 2, ["func1"], ["Class1"], ["os"])
        ]
        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer

        result = visualize_codebase("/test/dir", "csv")

        mock_visualizer.export_to_csv.assert_called_once()
        self.assertTrue(result.endswith("analysis_results.csv"))

    @patch('visualizer.analyze_codebase')
    def test_visualize_codebase_no_files(self, mock_analyze):
        """Test visualize_codebase with no Python files found."""
        mock_analyze.return_value = []

        result = visualize_codebase("/empty/dir", "html")

        self.assertEqual(result, "")

    def test_visualize_codebase_invalid_format(self):
        """Test visualize_codebase with invalid output format."""
        with patch('visualizer.analyze_codebase') as mock_analyze:
            mock_analyze.return_value = [
                CodeMetrics("/test/file.py", 50, 3, 2, 1, 2, ["func1"], ["Class1"], ["os"])
            ]

            with self.assertRaises(ValueError):
                visualize_codebase("/test/dir", "invalid_format")


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)