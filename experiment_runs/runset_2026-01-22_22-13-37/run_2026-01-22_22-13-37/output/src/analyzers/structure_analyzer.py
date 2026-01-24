"""
Structure Analyzer - Discovers and maps codebase architecture

This module focuses on understanding the high-level structure of a codebase,
including file relationships, dependency graphs, and architectural layers.
"""

from typing import Dict, List, Set, Any
from pathlib import Path
import ast
import re
from dataclasses import dataclass

@dataclass
class FileNode:
    """Represents a file in the codebase structure."""
    path: Path
    file_type: str  # 'python', 'javascript', 'typescript', etc.
    imports: Set[str]
    exports: Set[str]
    classes: List[str]
    functions: List[str]
    lines_of_code: int

@dataclass
class DependencyGraph:
    """Represents the dependency relationships in the codebase."""
    nodes: Dict[str, FileNode]
    edges: List[tuple]  # (from_file, to_file, import_type)

class StructureAnalyzer:
    """
    Analyzes codebase structure and generates dependency graphs.

    This analyzer focuses on understanding:
    - File organization and hierarchy
    - Import/export relationships
    - Module dependencies
    - Architectural layers
    """

    def __init__(self, codebase_path: Path):
        self.codebase_path = Path(codebase_path)
        self.supported_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx'}

    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive structure analysis.

        Returns:
            Dictionary containing structure analysis results
        """
        # Discover all relevant files
        files = self._discover_files()

        # Analyze each file
        file_nodes = {}
        for file_path in files:
            node = self._analyze_file(file_path)
            if node:
                file_nodes[str(file_path)] = node

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(file_nodes)

        # Identify architectural layers
        layers = self._identify_layers(dependency_graph)

        # Calculate structure metrics
        metrics = self._calculate_structure_metrics(dependency_graph, layers)

        return {
            'files': file_nodes,
            'dependency_graph': dependency_graph,
            'layers': layers,
            'metrics': metrics
        }

    def _discover_files(self) -> List[Path]:
        """Discover all relevant source files in the codebase."""
        files = []
        for ext in self.supported_extensions:
            files.extend(self.codebase_path.rglob(f'*{ext}'))

        # Filter out common non-source directories
        excluded_dirs = {'node_modules', '__pycache__', '.git', 'venv', 'env', 'build', 'dist'}
        filtered_files = []

        for file_path in files:
            if not any(part in excluded_dirs for part in file_path.parts):
                filtered_files.append(file_path)

        return filtered_files

    def _analyze_file(self, file_path: Path) -> FileNode:
        """Analyze a single file and extract its structure information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_type = self._determine_file_type(file_path)
            imports = self._extract_imports(content, file_type)
            exports = self._extract_exports(content, file_type)
            classes, functions = self._extract_definitions(content, file_type)
            lines_of_code = len([line for line in content.split('\n') if line.strip()])

            return FileNode(
                path=file_path,
                file_type=file_type,
                imports=imports,
                exports=exports,
                classes=classes,
                functions=functions,
                lines_of_code=lines_of_code
            )

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def _determine_file_type(self, file_path: Path) -> str:
        """Determine the programming language of a file."""
        suffix = file_path.suffix.lower()
        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript'
        }
        return type_map.get(suffix, 'unknown')

    def _extract_imports(self, content: str, file_type: str) -> Set[str]:
        """Extract import statements from file content."""
        imports = set()

        if file_type == 'python':
            # Parse Python imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module)
            except SyntaxError:
                # Fallback to regex for malformed Python
                imports.update(re.findall(r'from\s+(\S+)\s+import', content))
                imports.update(re.findall(r'import\s+(\S+)', content))

        elif file_type in ['javascript', 'typescript']:
            # Extract JS/TS imports
            imports.update(re.findall(r'import.*?from\s+["\']([^"\']+)["\']', content))
            imports.update(re.findall(r'require\(["\']([^"\']+)["\']\)', content))

        return imports

    def _extract_exports(self, content: str, file_type: str) -> Set[str]:
        """Extract export statements from file content."""
        exports = set()

        if file_type == 'python':
            # Python doesn't have explicit exports, but we can look for __all__
            if '__all__' in content:
                all_match = re.search(r'__all__\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if all_match:
                    exports.update(re.findall(r'["\']([^"\']+)["\']', all_match.group(1)))

        elif file_type in ['javascript', 'typescript']:
            # Extract JS/TS exports
            exports.update(re.findall(r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)', content))
            exports.update(re.findall(r'export\s+\{\s*([^}]+)\s*\}', content))

        return exports

    def _extract_definitions(self, content: str, file_type: str) -> tuple:
        """Extract class and function definitions."""
        classes = []
        functions = []

        if file_type == 'python':
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
            except SyntaxError:
                # Fallback to regex
                classes.extend(re.findall(r'class\s+(\w+)', content))
                functions.extend(re.findall(r'def\s+(\w+)', content))

        elif file_type in ['javascript', 'typescript']:
            classes.extend(re.findall(r'class\s+(\w+)', content))
            functions.extend(re.findall(r'function\s+(\w+)', content))
            functions.extend(re.findall(r'const\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=])*?=>', content))

        return classes, functions

    def _build_dependency_graph(self, file_nodes: Dict[str, FileNode]) -> DependencyGraph:
        """Build a dependency graph from file nodes."""
        edges = []

        for file_path, node in file_nodes.items():
            for import_name in node.imports:
                # Try to resolve the import to an actual file
                target_file = self._resolve_import(import_name, Path(file_path))
                if target_file and str(target_file) in file_nodes:
                    edges.append((file_path, str(target_file), 'import'))

        return DependencyGraph(nodes=file_nodes, edges=edges)

    def _resolve_import(self, import_name: str, current_file: Path) -> Path:
        """Resolve an import statement to its actual file path."""
        # This is a simplified resolution - in practice, this would be much more sophisticated
        if import_name.startswith('.'):
            # Relative import
            relative_path = current_file.parent / (import_name.lstrip('.') + '.py')
            if relative_path.exists():
                return relative_path
        else:
            # Try to find the module in the codebase
            potential_paths = [
                self.codebase_path / f"{import_name}.py",
                self.codebase_path / import_name / "__init__.py"
            ]
            for path in potential_paths:
                if path.exists():
                    return path

        return None

    def _identify_layers(self, dependency_graph: DependencyGraph) -> Dict[str, List[str]]:
        """Identify architectural layers based on dependency patterns."""
        # This is a simplified layer detection - could be much more sophisticated
        layers = {
            'presentation': [],
            'business': [],
            'data': [],
            'utility': []
        }

        for file_path, node in dependency_graph.nodes.items():
            file_name = Path(file_path).name.lower()

            # Simple heuristic-based layer classification
            if any(keyword in file_name for keyword in ['view', 'component', 'ui', 'template']):
                layers['presentation'].append(file_path)
            elif any(keyword in file_name for keyword in ['service', 'business', 'logic', 'manager']):
                layers['business'].append(file_path)
            elif any(keyword in file_name for keyword in ['model', 'dao', 'repository', 'database']):
                layers['data'].append(file_path)
            else:
                layers['utility'].append(file_path)

        return layers

    def _calculate_structure_metrics(self, dependency_graph: DependencyGraph, layers: Dict[str, List[str]]) -> Dict[str, float]:
        """Calculate various structural metrics."""
        total_files = len(dependency_graph.nodes)
        total_dependencies = len(dependency_graph.edges)

        # Average dependencies per file
        avg_dependencies = total_dependencies / max(total_files, 1)

        # Layer distribution
        layer_distribution = {layer: len(files) / max(total_files, 1) for layer, files in layers.items()}

        # Coupling metrics (simplified)
        highly_coupled_files = sum(1 for node in dependency_graph.nodes.values() if len(node.imports) > 10)
        coupling_ratio = highly_coupled_files / max(total_files, 1)

        return {
            'total_files': total_files,
            'total_dependencies': total_dependencies,
            'avg_dependencies_per_file': avg_dependencies,
            'coupling_ratio': coupling_ratio,
            **{f'layer_{layer}_ratio': ratio for layer, ratio in layer_distribution.items()}
        }