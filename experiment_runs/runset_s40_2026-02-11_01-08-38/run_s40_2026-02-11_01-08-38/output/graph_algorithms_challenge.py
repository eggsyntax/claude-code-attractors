from abc import ABC, abstractmethod
import heapq
import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Set

class GraphChallenge(ABC):
    def __init__(self):
        # Test graph 1: Small directed graph with weights
        self.test_graph_1 = {
            'A': [('B', 4), ('C', 2)],
            'B': [('C', 1), ('D', 5)],
            'C': [('D', 8), ('E', 10)],
            'D': [('E', 2)],
            'E': []
        }

        # Test graph 2: Medium undirected graph
        self.test_graph_2 = {
            'S': [('A', 7), ('C', 8)],
            'A': [('S', 7), ('B', 6), ('C', 3)],
            'B': [('A', 6), ('T', 5)],
            'C': [('S', 8), ('A', 3), ('D', 4)],
            'D': [('C', 4), ('E', 2), ('T', 2)],
            'E': [('D', 2), ('T', 1)],
            'T': [('B', 5), ('D', 2), ('E', 1)]
        }

        # Test cases for shortest path algorithms
        self.test_cases = [
            (self.test_graph_1, 'A', 'E'),
            (self.test_graph_2, 'S', 'T'),
            (self.test_graph_1, 'A', 'D'),
            (self.test_graph_2, 'A', 'E')
        ]

    @abstractmethod
    def solve(self, graph: Dict[str, List[Tuple[str, int]]], source: str, target: str = None) -> any:
        pass

    def benchmark(self, num_iterations: int = 1000) -> float:
        total_time = 0
        for _ in range(num_iterations):
            for graph, source, target in self.test_cases:
                start_time = time.perf_counter()
                self.solve(graph, source, target)
                total_time += time.perf_counter() - start_time
        return total_time / (num_iterations * len(self.test_cases))

    def test_correctness(self) -> bool:
        try:
            for graph, source, target in self.test_cases:
                result = self.solve(graph, source, target)
                if result is None:
                    print(f"Failed test case: {source} -> {target}")
                    return False
            return True
        except Exception as e:
            print(f"Error during testing: {e}")
            return False

    def compare_solutions(self, solutions: List['GraphChallenge']):
        print("=" * 60)
        print("🔗 GRAPH ALGORITHMS PERFORMANCE COMPARISON")
        print("=" * 60)

        results = []
        for solution in solutions:
            name = solution.__class__.__name__

            # Test correctness
            correct = solution.test_correctness()

            # Benchmark performance
            avg_time = solution.benchmark() * 1000  # Convert to milliseconds

            results.append((name, avg_time, correct))

            status = "✅ PASS" if correct else "❌ FAIL"
            print(f"{name:30} | {avg_time:8.4f} ms | {status}")

        print("\n" + "=" * 60)
        print("📊 PERFORMANCE RANKING:")

        # Sort by performance (only correct solutions)
        correct_results = [(name, time, correct) for name, time, correct in results if correct]
        correct_results.sort(key=lambda x: x[1])

        for i, (name, avg_time, correct) in enumerate(correct_results, 1):
            print(f"{i:2d}. {name:25} ({avg_time:8.4f} ms)")

        return results

# Tara's implementations
class TaraDijkstraOptimized(GraphChallenge):
    def solve(self, graph: Dict[str, List[Tuple[str, int]]], source: str, target: str = None) -> Dict[str, int]:
        distances = {node: float('inf') for node in graph}
        distances[source] = 0
        visited = set()
        pq = [(0, source)]

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            if target and current == target:
                return distances[target]

            for neighbor, weight in graph.get(current, []):
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        heapq.heappush(pq, (new_dist, neighbor))

        return distances[target] if target else distances

class TaraFloydWarshall(GraphChallenge):
    def solve(self, graph: Dict[str, List[Tuple[str, int]]], source: str, target: str = None) -> any:
        # Create node to index mapping
        nodes = list(graph.keys())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)

        # Initialize distance matrix
        dist = [[float('inf')] * n for _ in range(n)]

        # Distance from node to itself is 0
        for i in range(n):
            dist[i][i] = 0

        # Fill in edge weights
        for node, edges in graph.items():
            i = node_to_idx[node]
            for neighbor, weight in edges:
                j = node_to_idx[neighbor]
                dist[i][j] = weight

        # Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]

        # Return specific distance if target specified
        if target:
            source_idx = node_to_idx[source]
            target_idx = node_to_idx[target]
            result = dist[source_idx][target_idx]
            return result if result != float('inf') else None

        return dist

class TaraBellmanFord(GraphChallenge):
    def solve(self, graph: Dict[str, List[Tuple[str, int]]], source: str, target: str = None) -> any:
        # Get all nodes
        nodes = set(graph.keys())
        for node_edges in graph.values():
            for neighbor, _ in node_edges:
                nodes.add(neighbor)

        # Initialize distances
        distances = {node: float('inf') for node in nodes}
        distances[source] = 0

        # Relax edges |V| - 1 times
        for _ in range(len(nodes) - 1):
            for node in graph:
                if distances[node] != float('inf'):
                    for neighbor, weight in graph[node]:
                        new_dist = distances[node] + weight
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist

        # Check for negative cycles
        for node in graph:
            if distances[node] != float('inf'):
                for neighbor, weight in graph[node]:
                    if distances[node] + weight < distances[neighbor]:
                        return None  # Negative cycle detected

        return distances[target] if target else distances

# Dave's implementations
class DaveAStarSearch(GraphChallenge):
    def solve(self, graph: Dict[str, List[Tuple[str, int]]], source: str, target: str = None) -> int:
        if not target:
            # A* needs a specific target, fall back to Dijkstra-like behavior
            return self._dijkstra_fallback(graph, source)

        def heuristic(node: str, target: str) -> int:
            # Simple character-based heuristic (admissible for our test cases)
            return abs(ord(node) - ord(target))

        open_set = [(heuristic(source, target), 0, source)]  # (f_score, g_score, node)
        g_score = {source: 0}
        visited = set()

        while open_set:
            f_score, current_g, current = heapq.heappop(open_set)

            if current in visited:
                continue

            visited.add(current)

            if current == target:
                return current_g

            for neighbor, weight in graph.get(current, []):
                if neighbor in visited:
                    continue

                tentative_g = current_g + weight

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, target)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))

        return None  # No path found

    def _dijkstra_fallback(self, graph: Dict[str, List[Tuple[str, int]]], source: str) -> Dict[str, int]:
        distances = {node: float('inf') for node in graph}
        distances[source] = 0
        visited = set()
        pq = [(0, source)]

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            for neighbor, weight in graph.get(current, []):
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        heapq.heappush(pq, (new_dist, neighbor))

        return distances

class DaveBidirectionalDijkstra(GraphChallenge):
    def solve(self, graph: Dict[str, List[Tuple[str, int]]], source: str, target: str = None) -> int:
        if not target:
            # Bidirectional needs specific target, fall back to regular Dijkstra
            return self._dijkstra_fallback(graph, source)

        # Create reverse graph for backward search
        reverse_graph = defaultdict(list)
        for node, edges in graph.items():
            for neighbor, weight in edges:
                reverse_graph[neighbor].append((node, weight))

        # Initialize forward and backward searches
        forward_dist = {source: 0}
        backward_dist = {target: 0}
        forward_pq = [(0, source)]
        backward_pq = [(0, target)]
        forward_visited = set()
        backward_visited = set()

        best_distance = float('inf')

        while forward_pq or backward_pq:
            # Alternate between forward and backward searches
            if forward_pq and (not backward_pq or forward_pq[0][0] <= backward_pq[0][0]):
                # Forward search step
                current_dist, current = heapq.heappop(forward_pq)

                if current in forward_visited:
                    continue

                forward_visited.add(current)

                # Check if we've met the backward search
                if current in backward_visited:
                    total_dist = forward_dist[current] + backward_dist[current]
                    best_distance = min(best_distance, total_dist)

                for neighbor, weight in graph.get(current, []):
                    new_dist = current_dist + weight
                    if neighbor not in forward_dist or new_dist < forward_dist[neighbor]:
                        forward_dist[neighbor] = new_dist
                        heapq.heappush(forward_pq, (new_dist, neighbor))

            elif backward_pq:
                # Backward search step
                current_dist, current = heapq.heappop(backward_pq)

                if current in backward_visited:
                    continue

                backward_visited.add(current)

                # Check if we've met the forward search
                if current in forward_visited:
                    total_dist = forward_dist[current] + backward_dist[current]
                    best_distance = min(best_distance, total_dist)

                for neighbor, weight in reverse_graph.get(current, []):
                    new_dist = current_dist + weight
                    if neighbor not in backward_dist or new_dist < backward_dist[neighbor]:
                        backward_dist[neighbor] = new_dist
                        heapq.heappush(backward_pq, (new_dist, neighbor))

        return best_distance if best_distance != float('inf') else None

    def _dijkstra_fallback(self, graph: Dict[str, List[Tuple[str, int]]], source: str) -> Dict[str, int]:
        distances = {node: float('inf') for node in graph}
        distances[source] = 0
        visited = set()
        pq = [(0, source)]

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            for neighbor, weight in graph.get(current, []):
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        heapq.heappush(pq, (new_dist, neighbor))

        return distances

class DaveJohnsonAlgorithm(GraphChallenge):
    def solve(self, graph: Dict[str, List[Tuple[str, int]]], source: str, target: str = None) -> any:
        # Johnson's algorithm: Bellman-Ford + Dijkstra for all-pairs shortest paths

        # Get all nodes
        nodes = set(graph.keys())
        for node_edges in graph.values():
            for neighbor, _ in node_edges:
                nodes.add(neighbor)

        # Step 1: Add virtual node and run Bellman-Ford
        virtual_node = '__virtual__'
        extended_graph = dict(graph)
        extended_graph[virtual_node] = [(node, 0) for node in nodes]

        # Run Bellman-Ford from virtual node to detect negative cycles and get h values
        h_values = self._bellman_ford(extended_graph, virtual_node)
        if h_values is None:
            return None  # Negative cycle detected

        # Remove virtual node
        del h_values[virtual_node]

        # Step 2: Reweight edges using h values
        reweighted_graph = {}
        for node in nodes:
            reweighted_graph[node] = []
            for neighbor, weight in graph.get(node, []):
                new_weight = weight + h_values[node] - h_values[neighbor]
                reweighted_graph[node].append((neighbor, new_weight))

        # Step 3: Run Dijkstra from source on reweighted graph
        distances = self._dijkstra(reweighted_graph, source)

        # Step 4: Restore original distances
        for node in distances:
            if distances[node] != float('inf'):
                distances[node] = distances[node] - h_values[source] + h_values[node]

        return distances[target] if target else distances

    def _bellman_ford(self, graph: Dict[str, List[Tuple[str, int]]], source: str) -> Optional[Dict[str, int]]:
        # Get all nodes
        nodes = set(graph.keys())
        for node_edges in graph.values():
            for neighbor, _ in node_edges:
                nodes.add(neighbor)

        distances = {node: float('inf') for node in nodes}
        distances[source] = 0

        # Relax edges |V| - 1 times
        for _ in range(len(nodes) - 1):
            for node in graph:
                if distances[node] != float('inf'):
                    for neighbor, weight in graph[node]:
                        new_dist = distances[node] + weight
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist

        # Check for negative cycles
        for node in graph:
            if distances[node] != float('inf'):
                for neighbor, weight in graph[node]:
                    if distances[node] + weight < distances[neighbor]:
                        return None  # Negative cycle detected

        return distances

    def _dijkstra(self, graph: Dict[str, List[Tuple[str, int]]], source: str) -> Dict[str, int]:
        distances = {node: float('inf') for node in graph}
        distances[source] = 0
        visited = set()
        pq = [(0, source)]

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            for neighbor, weight in graph.get(current, []):
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        heapq.heappush(pq, (new_dist, neighbor))

        return distances

if __name__ == "__main__":
    # Test all implementations
    solutions = [
        TaraDijkstraOptimized(),
        TaraFloydWarshall(),
        TaraBellmanFord(),
        DaveAStarSearch(),
        DaveBidirectionalDijkstra(),
        DaveJohnsonAlgorithm()
    ]

    # Run comparison
    challenge = TaraDijkstraOptimized()
    challenge.compare_solutions(solutions)