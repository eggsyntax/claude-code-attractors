"""
Network Flow Challenge Framework
Created by Tara

A comprehensive framework for comparing different maximum flow algorithms.
"""

import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
import heapq


class NetworkFlowChallenge:
    """Framework for testing and comparing network flow algorithms"""

    def __init__(self):
        self.solutions = {}
        self.test_cases = self._create_test_cases()

    def _create_test_cases(self):
        """Create diverse test graphs for flow algorithms"""
        return {
            'simple_path': {
                'graph': {
                    's': [('t', 10)],
                },
                'source': 's',
                'sink': 't',
                'expected_flow': 10,
                'description': 'Simple source-to-sink path'
            },

            'diamond': {
                'graph': {
                    's': [('a', 10), ('b', 10)],
                    'a': [('t', 10)],
                    'b': [('t', 10)],
                },
                'source': 's',
                'sink': 't',
                'expected_flow': 20,
                'description': 'Diamond shape with parallel paths'
            },

            'bottleneck': {
                'graph': {
                    's': [('a', 20), ('b', 20)],
                    'a': [('c', 5)],
                    'b': [('c', 5)],
                    'c': [('t', 10)],
                },
                'source': 's',
                'sink': 't',
                'expected_flow': 10,
                'description': 'Bottleneck in the middle'
            },

            'complex': {
                'graph': {
                    's': [('a', 16), ('b', 13)],
                    'a': [('b', 4), ('c', 12)],
                    'b': [('a', 4), ('d', 14)],
                    'c': [('b', 9), ('t', 20)],
                    'd': [('c', 7), ('t', 4)],
                },
                'source': 's',
                'sink': 't',
                'expected_flow': 23,
                'description': 'Complex network with multiple paths'
            }
        }

    def register_solution(self, name: str, func):
        """Register a network flow solution"""
        self.solutions[name] = func
        print(f"✅ Registered solution: {name}")

    def benchmark_solution(self, name: str, test_case: str, iterations: int = 1000) -> float:
        """Benchmark a single solution on a test case"""
        if name not in self.solutions:
            raise ValueError(f"Solution {name} not registered")

        func = self.solutions[name]
        case = self.test_cases[test_case]

        start_time = time.time()
        for _ in range(iterations):
            result = func(case['graph'], case['source'], case['sink'])
        end_time = time.time()

        return (end_time - start_time) / iterations * 1000  # Convert to ms

    def test_correctness(self, name: str) -> Dict[str, bool]:
        """Test solution correctness against all test cases"""
        if name not in self.solutions:
            raise ValueError(f"Solution {name} not registered")

        func = self.solutions[name]
        results = {}

        for test_name, case in self.test_cases.items():
            try:
                result = func(case['graph'], case['source'], case['sink'])
                results[test_name] = (result == case['expected_flow'])
                if not results[test_name]:
                    print(f"❌ {name} failed {test_name}: expected {case['expected_flow']}, got {result}")
            except Exception as e:
                results[test_name] = False
                print(f"❌ {name} error on {test_name}: {e}")

        return results

    def compare_solutions(self):
        """Compare all registered solutions"""
        print("\n" + "="*60)
        print("🔗 NETWORK FLOW ALGORITHM COMPARISON")
        print("="*60)

        # Test correctness first
        print("\n📋 CORRECTNESS TESTS:")
        all_correct = {}
        for name in self.solutions:
            results = self.test_correctness(name)
            correct_count = sum(results.values())
            total_count = len(results)
            all_correct[name] = correct_count == total_count
            status = "✅ PASS" if all_correct[name] else "❌ FAIL"
            print(f"{name}: {correct_count}/{total_count} {status}")

        print("\n⚡ PERFORMANCE BENCHMARK:")
        print(f"{'Algorithm':<25} {'Time (ms)':<12} {'Status'}")
        print("-" * 50)

        # Benchmark only correct solutions
        performance_results = []
        for name in self.solutions:
            if all_correct[name]:
                avg_time = self.benchmark_solution(name, 'complex')
                performance_results.append((name, avg_time))
                print(f"{name:<25} {avg_time:.4f} ms      ✅")
            else:
                print(f"{name:<25} {'N/A':<12}     ❌")

        # Sort by performance
        performance_results.sort(key=lambda x: x[1])

        print(f"\n🏆 PERFORMANCE RANKING:")
        for i, (name, time_ms) in enumerate(performance_results, 1):
            print(f"{i}. {name} ({time_ms:.4f} ms)")

        return performance_results


# Tara's Network Flow Implementations

def tara_ford_fulkerson_dfs(graph: Dict, source: str, sink: str) -> int:
    """
    Ford-Fulkerson with DFS path finding

    My approach: Clean residual graph management with explicit capacity tracking.
    Uses DFS for augmenting path discovery - simple and intuitive.
    """
    # Build residual graph with forward and backward edges
    residual = defaultdict(lambda: defaultdict(int))

    # Initialize with forward edges
    for u in graph:
        for v, capacity in graph[u]:
            residual[u][v] = capacity
            residual[v][u] = 0  # Backward edge with 0 initial capacity

    def dfs_path(start: str, end: str, visited: set, path: List[str]) -> Optional[List[str]]:
        """Find augmenting path using DFS"""
        if start == end:
            return path + [end]

        visited.add(start)
        for neighbor in residual[start]:
            if neighbor not in visited and residual[start][neighbor] > 0:
                result = dfs_path(neighbor, end, visited, path + [start])
                if result:
                    return result
        return None

    max_flow = 0

    while True:
        # Find augmenting path
        path = dfs_path(source, sink, set(), [])
        if not path:
            break

        # Find bottleneck capacity along path
        bottleneck = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            bottleneck = min(bottleneck, residual[u][v])

        # Update residual capacities
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck

        max_flow += bottleneck

    return max_flow


def tara_edmonds_karp_bfs(graph: Dict, source: str, sink: str) -> int:
    """
    Edmonds-Karp algorithm (Ford-Fulkerson with BFS)

    My approach: Uses BFS for shortest augmenting paths, guaranteeing O(VE²) complexity.
    More efficient than pure DFS Ford-Fulkerson on dense graphs.
    """
    # Build residual graph
    residual = defaultdict(lambda: defaultdict(int))

    for u in graph:
        for v, capacity in graph[u]:
            residual[u][v] = capacity
            residual[v][u] = 0

    def bfs_path(start: str, end: str) -> Optional[List[str]]:
        """Find shortest augmenting path using BFS"""
        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            node, path = queue.popleft()

            for neighbor in residual[node]:
                if neighbor not in visited and residual[node][neighbor] > 0:
                    new_path = path + [neighbor]
                    if neighbor == end:
                        return new_path
                    queue.append((neighbor, new_path))
                    visited.add(neighbor)

        return None

    max_flow = 0

    while True:
        path = bfs_path(source, sink)
        if not path:
            break

        # Find bottleneck
        bottleneck = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            bottleneck = min(bottleneck, residual[u][v])

        # Update residual graph
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck

        max_flow += bottleneck

    return max_flow


def tara_push_relabel_basic(graph: Dict, source: str, sink: str) -> int:
    """
    Basic Push-Relabel algorithm

    My approach: Different paradigm from augmenting paths - maintains preflow and
    height labels. Uses local operations (push/relabel) rather than global path finding.
    More complex but can be more efficient on certain graph structures.
    """
    # Get all nodes
    nodes = set([source, sink])
    for u in graph:
        nodes.add(u)
        for v, _ in graph[u]:
            nodes.add(v)
    nodes = list(nodes)

    # Initialize capacity matrix
    capacity = defaultdict(lambda: defaultdict(int))
    for u in graph:
        for v, cap in graph[u]:
            capacity[u][v] = cap

    # Initialize flow matrix
    flow = defaultdict(lambda: defaultdict(int))

    # Initialize excess and height
    excess = {node: 0 for node in nodes}
    height = {node: 0 for node in nodes}
    height[source] = len(nodes)  # Source gets maximum height

    # Initial push from source
    for v, cap in graph.get(source, []):
        flow[source][v] = cap
        flow[v][source] = -cap
        excess[v] = cap
        excess[source] -= cap

    def push(u: str, v: str):
        """Push flow from u to v"""
        # Calculate how much we can push
        residual_capacity = capacity[u][v] - flow[u][v]
        push_amount = min(excess[u], residual_capacity)

        # Update flows
        flow[u][v] += push_amount
        flow[v][u] -= push_amount

        # Update excess
        excess[u] -= push_amount
        excess[v] += push_amount

    def relabel(u: str):
        """Increase height of u"""
        min_height = float('inf')
        for v in nodes:
            residual_capacity = capacity[u][v] - flow[u][v]
            if residual_capacity > 0:
                min_height = min(min_height, height[v])

        if min_height < float('inf'):
            height[u] = min_height + 1

    def get_active_node():
        """Find a node with excess (excluding source and sink)"""
        for node in nodes:
            if node != source and node != sink and excess[node] > 0:
                return node
        return None

    # Main push-relabel loop
    while True:
        active = get_active_node()
        if not active:
            break

        # Try to push to all neighbors
        pushed = False
        for v in nodes:
            if (height[active] == height[v] + 1 and
                capacity[active][v] - flow[active][v] > 0 and
                excess[active] > 0):
                push(active, v)
                pushed = True

        # If no push was possible, relabel
        if not pushed:
            relabel(active)

    # Return flow into sink
    return sum(flow[v][sink] for v in nodes)


# Initialize the challenge
if __name__ == "__main__":
    challenge = NetworkFlowChallenge()

    # Register Tara's solutions
    challenge.register_solution("Tara Ford-Fulkerson DFS", tara_ford_fulkerson_dfs)
    challenge.register_solution("Tara Edmonds-Karp BFS", tara_edmonds_karp_bfs)
    challenge.register_solution("Tara Push-Relabel Basic", tara_push_relabel_basic)

    print("\n🔗 Network Flow Challenge Framework Ready!")
    print("\nTara's implemented algorithms:")
    print("1. Ford-Fulkerson with DFS - Classic augmenting path approach")
    print("2. Edmonds-Karp with BFS - Shortest paths for better complexity")
    print("3. Push-Relabel Basic - Different paradigm using preflows")
    print("\nReady for Dave's implementations! Run challenge.compare_solutions() when ready.")