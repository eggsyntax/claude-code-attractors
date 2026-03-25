"""
Collaboration Pattern Detection Engine

This module analyzes codebase data to identify opportunities and patterns for collaboration.
It processes the structured output from CodebaseAnalyzer to detect various collaboration signals.
"""

import json
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
import networkx as nx
from datetime import datetime, timedelta


@dataclass
class CollaborationPattern:
    """Represents a detected collaboration opportunity or pattern"""
    pattern_type: str
    confidence: float  # 0-1 score
    files: List[str]
    description: str
    recommendation: str
    metadata: Dict[str, Any]


class PatternDetector:
    """Main engine for detecting collaboration patterns in codebases"""

    def __init__(self, analysis_data: Dict[str, Any]):
        self.files = analysis_data.get('files', {})
        self.entities = analysis_data.get('entities', {})
        self.dependency_graph = self._build_dependency_graph()

    def detect_all_patterns(self) -> List[CollaborationPattern]:
        """Run all pattern detection algorithms and return findings"""
        patterns = []

        patterns.extend(self.detect_temporal_clusters())
        patterns.extend(self.detect_structural_dependencies())
        patterns.extend(self.detect_knowledge_clusters())
        patterns.extend(self.detect_integration_points())
        patterns.extend(self.detect_coordination_needs())

        # Sort by confidence score
        return sorted(patterns, key=lambda p: p.confidence, reverse=True)

    def detect_temporal_clusters(self) -> List[CollaborationPattern]:
        """Identify files that are frequently modified together"""
        patterns = []

        # Analyze modification patterns (simulated with file sizes as proxy)
        # In real implementation, would use git log data
        modification_clusters = self._find_temporal_clusters()

        for cluster in modification_clusters:
            if len(cluster) >= 2:
                confidence = min(1.0, len(cluster) / 5)  # Higher confidence for larger clusters
                patterns.append(CollaborationPattern(
                    pattern_type="temporal_cluster",
                    confidence=confidence,
                    files=list(cluster),
                    description=f"These {len(cluster)} files are often modified together",
                    recommendation="Consider assigning to same developer or coordinating changes",
                    metadata={"cluster_size": len(cluster)}
                ))

        return patterns

    def detect_structural_dependencies(self) -> List[CollaborationPattern]:
        """Find modules with strong structural coupling"""
        patterns = []

        # Analyze import relationships and shared entities
        for file_path, entities in self.entities.items():
            imports = [e for e in entities if e.get('type') == 'import']

            # Find files with shared dependencies
            for other_path, other_entities in self.entities.items():
                if file_path >= other_path:  # Avoid duplicates
                    continue

                other_imports = [e for e in other_entities if e.get('type') == 'import']
                shared_deps = self._count_shared_dependencies(imports, other_imports)

                if shared_deps > 2:  # Threshold for significant coupling
                    confidence = min(1.0, shared_deps / 10)
                    patterns.append(CollaborationPattern(
                        pattern_type="structural_dependency",
                        confidence=confidence,
                        files=[file_path, other_path],
                        description=f"Strong structural coupling with {shared_deps} shared dependencies",
                        recommendation="Coordinate development to avoid integration conflicts",
                        metadata={"shared_dependencies": shared_deps}
                    ))

        return patterns

    def detect_knowledge_clusters(self) -> List[CollaborationPattern]:
        """Identify areas where domain knowledge overlaps"""
        patterns = []

        # Group files by domain indicators (directory structure, naming patterns)
        domain_clusters = self._cluster_by_domain()

        for domain, files in domain_clusters.items():
            if len(files) >= 3:  # Minimum cluster size
                # Analyze complexity indicators
                total_entities = sum(len(self.entities.get(f, [])) for f in files)
                avg_complexity = total_entities / len(files) if files else 0

                if avg_complexity > 5:  # High complexity threshold
                    confidence = min(1.0, (avg_complexity - 5) / 15)
                    patterns.append(CollaborationPattern(
                        pattern_type="knowledge_cluster",
                        confidence=confidence,
                        files=files,
                        description=f"Complex {domain} domain requiring specialized knowledge",
                        recommendation="Assign developers with domain expertise or pair programming",
                        metadata={"domain": domain, "complexity": avg_complexity}
                    ))

        return patterns

    def detect_integration_points(self) -> List[CollaborationPattern]:
        """Find critical integration points where work converges"""
        patterns = []

        # Analyze dependency graph for high-degree nodes
        if self.dependency_graph:
            for node in self.dependency_graph.nodes():
                in_degree = self.dependency_graph.in_degree(node)
                out_degree = self.dependency_graph.out_degree(node)

                # High fan-in or fan-out indicates integration point
                if in_degree > 3 or out_degree > 3:
                    confidence = min(1.0, max(in_degree, out_degree) / 10)

                    connected_files = list(self.dependency_graph.predecessors(node)) + \
                                    list(self.dependency_graph.successors(node))

                    patterns.append(CollaborationPattern(
                        pattern_type="integration_point",
                        confidence=confidence,
                        files=[node] + connected_files[:5],  # Limit for readability
                        description=f"Critical integration point (in:{in_degree}, out:{out_degree})",
                        recommendation="Establish clear interfaces and coordinate changes carefully",
                        metadata={"in_degree": in_degree, "out_degree": out_degree}
                    ))

        return patterns

    def detect_coordination_needs(self) -> List[CollaborationPattern]:
        """Identify files that would benefit from coordinated development"""
        patterns = []

        # Look for files with similar entity patterns (similar "shape")
        file_signatures = {}
        for file_path, entities in self.entities.items():
            signature = self._compute_file_signature(entities)
            file_signatures[file_path] = signature

        # Find files with similar signatures
        for file1, sig1 in file_signatures.items():
            for file2, sig2 in file_signatures.items():
                if file1 >= file2:
                    continue

                similarity = self._compute_signature_similarity(sig1, sig2)
                if similarity > 0.7:  # High similarity threshold
                    patterns.append(CollaborationPattern(
                        pattern_type="coordination_need",
                        confidence=similarity,
                        files=[file1, file2],
                        description=f"Similar structure suggests parallel development ({similarity:.1%} similarity)",
                        recommendation="Consider shared design patterns or code review",
                        metadata={"similarity_score": similarity}
                    ))

        return patterns

    # Helper methods

    def _build_dependency_graph(self) -> nx.DiGraph:
        """Build a directed graph of file dependencies"""
        graph = nx.DiGraph()

        for file_path, entities in self.entities.items():
            graph.add_node(file_path)

            # Add edges for imports (simplified - real implementation would resolve imports)
            imports = [e for e in entities if e.get('type') == 'import']
            for imp in imports:
                module = imp.get('name', '')
                if module in self.entities:  # Only internal dependencies
                    graph.add_edge(file_path, module)

        return graph

    def _find_temporal_clusters(self) -> List[Set[str]]:
        """Group files by modification patterns (simplified implementation)"""
        # In real implementation, would analyze git log data
        # For demo, group by file size ranges as proxy
        size_groups = defaultdict(set)

        for file_path, file_info in self.files.items():
            size_bucket = file_info.get('size', 0) // 1000  # Group by KB
            size_groups[size_bucket].add(file_path)

        return [group for group in size_groups.values() if len(group) > 1]

    def _count_shared_dependencies(self, imports1: List[Dict], imports2: List[Dict]) -> int:
        """Count shared dependencies between two import lists"""
        names1 = {imp.get('name', '') for imp in imports1}
        names2 = {imp.get('name', '') for imp in imports2}
        return len(names1.intersection(names2))

    def _cluster_by_domain(self) -> Dict[str, List[str]]:
        """Group files by domain based on path structure"""
        clusters = defaultdict(list)

        for file_path in self.entities.keys():
            # Extract domain from path (simplified)
            parts = file_path.split('/')
            if len(parts) > 1:
                domain = parts[-2]  # Parent directory as domain
            else:
                domain = "root"

            clusters[domain].append(file_path)

        return dict(clusters)

    def _compute_file_signature(self, entities: List[Dict]) -> Dict[str, int]:
        """Compute a signature representing the file's structure"""
        signature = Counter()

        for entity in entities:
            entity_type = entity.get('type', 'unknown')
            signature[entity_type] += 1

        return dict(signature)

    def _compute_signature_similarity(self, sig1: Dict[str, int], sig2: Dict[str, int]) -> float:
        """Compute similarity between two file signatures"""
        all_keys = set(sig1.keys()) | set(sig2.keys())

        if not all_keys:
            return 0.0

        # Simple cosine similarity
        dot_product = sum(sig1.get(key, 0) * sig2.get(key, 0) for key in all_keys)
        norm1 = sum(v * v for v in sig1.values()) ** 0.5
        norm2 = sum(v * v for v in sig2.values()) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


def generate_collaboration_report(patterns: List[CollaborationPattern]) -> str:
    """Generate a human-readable report of collaboration patterns"""
    if not patterns:
        return "No significant collaboration patterns detected."

    report = ["# Collaboration Analysis Report\n"]

    # Group by pattern type
    by_type = defaultdict(list)
    for pattern in patterns:
        by_type[pattern.pattern_type].append(pattern)

    for pattern_type, type_patterns in by_type.items():
        report.append(f"## {pattern_type.replace('_', ' ').title()}")
        report.append(f"Found {len(type_patterns)} patterns\n")

        for i, pattern in enumerate(type_patterns[:3], 1):  # Show top 3
            report.append(f"### Pattern {i} (Confidence: {pattern.confidence:.1%})")
            report.append(f"**Files:** {', '.join(pattern.files)}")
            report.append(f"**Description:** {pattern.description}")
            report.append(f"**Recommendation:** {pattern.recommendation}\n")

    return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    sample_data = {
        "files": {
            "src/auth.py": {"size": 2500, "lines": 100},
            "src/user.py": {"size": 1800, "lines": 75},
            "tests/test_auth.py": {"size": 1200, "lines": 50}
        },
        "entities": {
            "src/auth.py": [
                {"type": "import", "name": "hashlib"},
                {"type": "import", "name": "jwt"},
                {"type": "function", "name": "login"},
                {"type": "class", "name": "AuthManager"}
            ],
            "src/user.py": [
                {"type": "import", "name": "hashlib"},
                {"type": "import", "name": "database"},
                {"type": "class", "name": "User"}
            ]
        }
    }

    detector = PatternDetector(sample_data)
    patterns = detector.detect_all_patterns()
    report = generate_collaboration_report(patterns)
    print(report)