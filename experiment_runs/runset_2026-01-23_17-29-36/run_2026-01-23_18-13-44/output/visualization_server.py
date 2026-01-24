#!/usr/bin/env python3
"""
Interactive Web Server for Code Analysis Visualization
A collaborative creation by Alice & Bob

This server provides a REST API endpoint for our code analysis tools,
integrating both AST analysis and complexity metrics into beautiful web visualizations.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import tempfile
import logging
from pathlib import Path

# Import our analyzers (assuming they're in the same directory)
try:
    from ast_analyzer import CodeAnalyzer
    from complexity_analyzer import ComplexityAnalyzer
except ImportError:
    print("Warning: Could not import analyzers. Make sure ast_analyzer.py and complexity_analyzer.py are in the same directory.")
    CodeAnalyzer = None
    ComplexityAnalyzer = None

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalysisServer(BaseHTTPRequestHandler):
    """
    HTTP request handler that serves our web interface and provides analysis API endpoints.

    Endpoints:
    - GET /: Serves the main HTML interface
    - POST /analyze: Accepts Python code and returns analysis results
    - GET /health: Health check endpoint
    """

    def do_GET(self):
        """Handle GET requests for serving static content and health checks."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_html_interface()
        elif parsed_path.path == '/health':
            self.serve_health_check()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests for code analysis."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/analyze':
            self.handle_analysis_request()
        else:
            self.send_error(404, "Not Found")

    def serve_html_interface(self):
        """Serve the main HTML interface."""
        try:
            # Try to read the HTML file from the same directory
            html_path = Path(__file__).parent / 'web_interface.html'
            if html_path.exists():
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
            else:
                self.send_error(404, "HTML interface not found")

        except Exception as e:
            logger.error(f"Error serving HTML interface: {e}")
            self.send_error(500, "Internal Server Error")

    def serve_health_check(self):
        """Serve health check response."""
        health_data = {
            "status": "healthy",
            "analyzers_available": {
                "ast_analyzer": CodeAnalyzer is not None,
                "complexity_analyzer": ComplexityAnalyzer is not None
            },
            "message": "Code Analysis Visualization Server - Alice & Bob's Collaborative Tool"
        }

        self.send_json_response(health_data)

    def handle_analysis_request(self):
        """Handle code analysis requests."""
        try:
            # Parse the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "Empty request body")
                return

            post_data = self.rfile.read(content_length)

            # Try to parse as JSON first
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                code_content = request_data.get('code', '')
                filename = request_data.get('filename', 'unknown.py')
            except json.JSONDecodeError:
                # If not JSON, treat as form data or plain text
                code_content = post_data.decode('utf-8')
                filename = 'uploaded.py'

            if not code_content.strip():
                self.send_error(400, "No code content provided")
                return

            # Perform the analysis
            analysis_result = self.analyze_code(code_content, filename)

            # Send the results
            self.send_json_response(analysis_result)

        except Exception as e:
            logger.error(f"Error handling analysis request: {e}")
            self.send_error(500, f"Analysis failed: {str(e)}")

    def analyze_code(self, code_content: str, filename: str) -> dict:
        """
        Perform comprehensive code analysis using our integrated analyzers.

        Args:
            code_content: The Python code to analyze
            filename: Name of the file being analyzed

        Returns:
            Dictionary containing comprehensive analysis results
        """
        results = {
            "filename": filename,
            "total_lines": len(code_content.split('\n')),
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity_summary": {},
            "analysis_metadata": {
                "analyzer_version": "1.0.0",
                "analyzed_by": "Alice & Bob's Collaborative Tool"
            }
        }

        try:
            if CodeAnalyzer is None or ComplexityAnalyzer is None:
                # Fallback to basic analysis if analyzers aren't available
                return self.basic_analysis_fallback(code_content, filename)

            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code_content)
                temp_file_path = temp_file.name

            try:
                # Perform AST analysis
                ast_analyzer = CodeAnalyzer()
                ast_results = ast_analyzer.analyze_file(temp_file_path)

                # Perform complexity analysis
                complexity_analyzer = ComplexityAnalyzer()
                complexity_results = complexity_analyzer.analyze_file(temp_file_path)

                # Merge results
                results.update({
                    "functions": self.merge_function_data(ast_results.get("functions", []),
                                                        complexity_results.get("functions", [])),
                    "classes": ast_results.get("classes", []),
                    "imports": ast_results.get("imports", []),
                    "complexity_summary": self.calculate_complexity_summary(complexity_results.get("functions", []))
                })

                logger.info(f"Successfully analyzed {filename}: {len(results['functions'])} functions, {len(results['classes'])} classes")

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

        except Exception as e:
            logger.error(f"Error during code analysis: {e}")
            # Return partial results with error information
            results["error"] = f"Analysis partially failed: {str(e)}"
            results["functions"] = []
            results["classes"] = []

        return results

    def merge_function_data(self, ast_functions: list, complexity_functions: list) -> list:
        """
        Merge AST function data with complexity metrics.

        Args:
            ast_functions: List of functions from AST analysis
            complexity_functions: List of functions with complexity metrics

        Returns:
            List of functions with merged data
        """
        merged_functions = []

        # Create lookup dictionary for complexity data
        complexity_lookup = {func["name"]: func for func in complexity_functions}

        for ast_func in ast_functions:
            func_name = ast_func["name"]
            merged_func = ast_func.copy()

            # Add complexity data if available
            if func_name in complexity_lookup:
                complexity_data = complexity_lookup[func_name]
                merged_func.update({
                    "cyclomatic_complexity": complexity_data.get("cyclomatic_complexity", 0),
                    "cognitive_complexity": complexity_data.get("cognitive_complexity", 0),
                    "max_nesting_depth": complexity_data.get("max_nesting_depth", 0),
                    "complexity_rating": complexity_data.get("complexity_rating", "Unknown")
                })
            else:
                # Default values if complexity analysis failed for this function
                merged_func.update({
                    "cyclomatic_complexity": 1,
                    "cognitive_complexity": 1,
                    "max_nesting_depth": 1,
                    "complexity_rating": "Low"
                })

            merged_functions.append(merged_func)

        return merged_functions

    def calculate_complexity_summary(self, complexity_functions: list) -> dict:
        """Calculate summary statistics for complexity metrics."""
        if not complexity_functions:
            return {
                "total_functions": 0,
                "avg_complexity": 0.0,
                "max_complexity": 0,
                "min_complexity": 0,
                "functions_by_complexity": {"low": 0, "moderate": 0, "high": 0, "very_high": 0}
            }

        complexities = [func.get("cyclomatic_complexity", 1) for func in complexity_functions]

        # Calculate distribution
        distribution = {"low": 0, "moderate": 0, "high": 0, "very_high": 0}
        for complexity in complexities:
            if complexity <= 5:
                distribution["low"] += 1
            elif complexity <= 10:
                distribution["moderate"] += 1
            elif complexity <= 15:
                distribution["high"] += 1
            else:
                distribution["very_high"] += 1

        return {
            "total_functions": len(complexity_functions),
            "avg_complexity": sum(complexities) / len(complexities),
            "max_complexity": max(complexities),
            "min_complexity": min(complexities),
            "functions_by_complexity": distribution
        }

    def basic_analysis_fallback(self, code_content: str, filename: str) -> dict:
        """
        Fallback analysis when full analyzers aren't available.
        Provides basic parsing using simple regex patterns.
        """
        import re

        lines = code_content.split('\n')
        functions = []
        classes = []
        imports = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Simple function detection
            func_match = re.match(r'def\s+(\w+)', line)
            if func_match:
                functions.append({
                    "name": func_match.group(1),
                    "line": line_num,
                    "cyclomatic_complexity": 1,  # Default
                    "cognitive_complexity": 1,
                    "max_nesting_depth": 1,
                    "complexity_rating": "Low",
                    "async": "async" in line,
                    "decorators": []
                })

            # Simple class detection
            class_match = re.match(r'class\s+(\w+)', line)
            if class_match:
                classes.append({
                    "name": class_match.group(1),
                    "line": line_num,
                    "methods": [],
                    "inheritance": []
                })

            # Import detection
            import_match = re.match(r'(import|from)\s+(\w+)', line)
            if import_match:
                imports.append(import_match.group(2))

        return {
            "filename": filename,
            "total_lines": len(lines),
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports)),  # Remove duplicates
            "complexity_summary": self.calculate_complexity_summary(functions),
            "analysis_metadata": {
                "analyzer_version": "1.0.0-fallback",
                "analyzed_by": "Alice & Bob's Collaborative Tool (Fallback Mode)"
            }
        }

    def send_json_response(self, data: dict, status_code: int = 200):
        """Send a JSON response with proper headers."""
        json_data = json.dumps(data, indent=2)

        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.info(format % args)


def run_server(port: int = 8080, host: str = 'localhost'):
    """
    Start the visualization server.

    Args:
        port: Port number to run the server on
        host: Host address to bind to
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, AnalysisServer)

    print(f"🚀 Code Analysis Visualization Server starting...")
    print(f"📍 Server running on http://{host}:{port}")
    print(f"🔍 Upload Python files for instant analysis and visualization!")
    print(f"💡 Built collaboratively by Alice & Bob")
    print(f"🛑 Press Ctrl+C to stop the server\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
        httpd.server_close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Code Analysis Visualization Server")
    parser.add_argument('--port', type=int, default=8080, help='Port to run the server on (default: 8080)')
    parser.add_argument('--host', type=str, default='localhost', help='Host to bind to (default: localhost)')

    args = parser.parse_args()

    run_server(port=args.port, host=args.host)