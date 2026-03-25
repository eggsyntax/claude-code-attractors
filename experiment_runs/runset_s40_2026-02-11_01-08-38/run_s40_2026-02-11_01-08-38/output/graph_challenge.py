"""
Graph Algorithms Challenge - Collaborative Implementation
Tara & Dave's exploration of graph algorithm efficiency and design patterns
"""

from abc import ABC, abstractmethod
import time
from collections import defaultdict, deque
import heapq
from typing import List, Tuple, Dict, Set, Optional


class GraphChallenge(ABC):
    """Base class for graph algorithm challenges"""

    def __init__(self, name: str):
        self.name = name
        self.solutions = {}

    def add_solution(self, solution_name: str, solution_func):
        """Add a solution to compare"""
        self.solutions[solution_name] = solution_func

    def create_test_graphs(self):
        """Create standard test graphs for comparison"""
        # Test Graph 1: Small directed graph
        graph1 = {
            'A': [('B', 4), ('C', 2)],
            'B': [('C', 1), ('D', 5)],
            'C': [('D', 8), ('E', 10)],
            'D': [('E', 2)],
            'E': []
        }

        # Test Graph 2: Medium undirected graph (represented as bidirectional)
        graph2 = defaultdict(list)
        edges = [('1', '2', 1), ('1', '3', 4), ('2', '3', 2), ('2', '4', 5),
                ('3', '4', 1), ('4', '5', 3), ('3', '5', 6)]
        for u, v, w in edges:
            graph2[u].append((v, w))
            graph2[v].append((u, w))

        return {'small_directed': graph1, 'medium_undirected': dict(graph2)}

    def benchmark_solution(self, solution_func, *args, iterations=1000):
        """Benchmark a solution with given arguments"""
        total_time = 0
        for _ in range(iterations):
            start = time.perf_counter()
            result = solution_func(*args)
            end = time.perf_counter()
            total_time += (end - start)

        avg_time_ms = (total_time / iterations) * 1000
        return result, avg_time_ms

    def compare_solutions(self):
        """Compare all solutions for correctness and performance"""
        print(f"\n🔗 {self.name} - Solution Comparison")
        print("=" * 60)

        test_graphs = self.create_test_graphs()

        for graph_name, graph in test_graphs.items():
            print(f"\n📊 Testing on {graph_name}:")
            results = []

            for solution_name, solution_func in self.solutions.items():
                try:
                    result, avg_time = self.benchmark_solution(solution_func, graph)
                    results.append((solution_name, result, avg_time))
                    print(f"  {solution_name}: {avg_time:.4f} ms")
                except Exception as e:
                    print(f"  {solution_name}: ERROR - {e}")

            # Sort by performance
            results.sort(key=lambda x: x[2])

            print(f"\n🏆 Performance Ranking for {graph_name}:")
            for i, (name, result, time_ms) in enumerate(results, 1):
                print(f"  {i}. {name}: {time_ms:.4f} ms")

            # Verify correctness by comparing results
            if len(results) > 1:
                first_result = results[0][1]
                all_match = all(result == first_result for _, result, _ in results)
                if all_match:
                    print("  ✅ All solutions produce identical results")
                else:
                    print("  ⚠️  Results differ between solutions:")
                    for name, result, _ in results:
                        print(f"    {name}: {result}")


class ShortestPathChallenge(GraphChallenge):
    """Challenge focused on shortest path algorithms"""

    def __init__(self):
        super().__init__("Shortest Path Algorithms")


# Tara's Shortest Path Implementations

def tara_dijkstra_optimized(graph):
    """
    Tara's Dijkstra implementation with priority queue optimization
    Focus: Clean, readable code with efficient data structures
    """
    if not graph:
        return {}

    # Start from first node in the graph
    start = next(iter(graph))

    # Initialize distances
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    # Priority queue: (distance, node)
    pq = [(0, start)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current in visited:
            continue

        visited.add(current)

        # Check all neighbors
        for neighbor, weight in graph.get(current, []):
            if neighbor not in visited:
                new_dist = current_dist + weight
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))

    return distances


def tara_floyd_warshall_optimized(graph):
    """
    Tara's Floyd-Warshall with space-efficient representation
    Focus: All-pairs shortest path with clean initialization
    """
    # Extract all nodes
    nodes = set(graph.keys())
    for node in graph:
        for neighbor, _ in graph[node]:
            nodes.add(neighbor)

    nodes = list(nodes)
    n = len(nodes)

    # Node to index mapping
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # Initialize distance matrix
    dist = [[float('inf')] * n for _ in range(n)]

    # Distance from node to itself is 0
    for i in range(n):
        dist[i][i] = 0

    # Fill in direct edges
    for node in graph:
        i = node_to_idx[node]
        for neighbor, weight in graph[node]:
            j = node_to_idx[neighbor]
            dist[i][j] = weight

    # Floyd-Warshall algorithm
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Convert back to dictionary format
    result = {}
    for i, node in enumerate(nodes):
        result[node] = {}
        for j, target in enumerate(nodes):
            if dist[i][j] != float('inf'):
                result[node][target] = dist[i][j]

    return result


def tara_bellman_ford_practical(graph):
    """
    Tara's Bellman-Ford with negative cycle detection
    Focus: Robust handling of edge cases and clear error reporting
    """
    if not graph:
        return {}

    # Start from first node
    start = next(iter(graph))

    # Extract all nodes and edges
    nodes = set(graph.keys())
    edges = []

    for node in graph:
        for neighbor, weight in graph[node]:
            nodes.add(neighbor)
            edges.append((node, neighbor, weight))

    # Initialize distances
    distances = {node: float('inf') for node in nodes}
    distances[start] = 0

    # Relax edges |V|-1 times
    for _ in range(len(nodes) - 1):
        for u, v, weight in edges:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight

    # Check for negative cycles
    for u, v, weight in edges:
        if distances[u] != float('inf') and distances[u] + weight < distances[v]:
            # Negative cycle detected - return None to indicate this
            return None

    return distances


# Initialize the challenge
challenge = ShortestPathChallenge()
challenge.add_solution("Tara's Optimized Dijkstra", tara_dijkstra_optimized)
challenge.add_solution("Tara's Floyd-Warshall", tara_floyd_warshall_optimized)
challenge.add_solution("Tara's Bellman-Ford", tara_bellman_ford_practical)

print("🔗 Graph Algorithms Challenge Framework Created!")
print("\nTara's Implementations:")
print("✅ Dijkstra's Algorithm - Optimized with priority queue")
print("✅ Floyd-Warshall - Space-efficient all-pairs shortest path")
print("✅ Bellman-Ford - Robust negative cycle detection")
print("\nReady for Dave's implementations and comparison!")