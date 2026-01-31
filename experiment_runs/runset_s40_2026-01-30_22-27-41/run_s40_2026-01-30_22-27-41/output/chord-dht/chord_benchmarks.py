#!/usr/bin/env python3
"""
Comprehensive Benchmarking Suite for Chord DHT
==============================================

This module provides extensive benchmarking and performance analysis
capabilities for our Chord DHT implementation.

Features:
- Scalability benchmarks (10 to 1000+ nodes)
- Lookup performance analysis
- Network churn simulation (joins/leaves)
- Load balancing evaluation
- Fault tolerance testing
- Comparative analysis with theoretical performance

Authors: Bob (Phase 5 - Benchmarking) & Alice (Phases 1-4)
"""

import time
import random
import statistics
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from chord_node import ChordNode
from protocols import JoinLeaveProtocols, NetworkStabilizer
from routing import ChordRouter, RoutingMetrics
from consistent_hash import hash_key
from network_simulator import NetworkSimulator


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    benchmark_name: str
    network_size: int
    total_operations: int
    success_rate: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_hops: float
    theoretical_hops: float
    throughput_ops_per_sec: float
    timestamp: float
    additional_metrics: Dict = None


@dataclass
class ScalabilityResult:
    """Results from scalability testing."""
    network_sizes: List[int]
    lookup_latencies: List[float]
    hop_counts: List[float]
    theoretical_hops: List[float]
    throughput_rates: List[float]


class ChordBenchmarkSuite:
    """
    Comprehensive benchmarking suite for Chord DHT performance analysis.

    Provides standardized benchmarks for evaluating performance characteristics
    including latency, throughput, scalability, and fault tolerance.
    """

    def __init__(self, m_bits: int = 6):
        """Initialize benchmark suite."""
        self.m_bits = m_bits
        self.ring_size = 2 ** m_bits
        self.results: List[BenchmarkResult] = []

    def run_lookup_performance_benchmark(self, network_size: int,
                                       num_operations: int = 1000) -> BenchmarkResult:
        """
        Benchmark lookup performance for a given network size.

        Args:
            network_size: Number of nodes in the test network
            num_operations: Number of lookup operations to perform

        Returns:
            BenchmarkResult with performance metrics
        """
        print(f"🔍 Running lookup performance benchmark (N={network_size}, ops={num_operations})")

        # Create network
        simulator = NetworkSimulator(self.m_bits)
        nodes = simulator.create_large_network(network_size, initial_keys=network_size * 10)

        if not nodes:
            raise ValueError("Failed to create test network")

        node_list = list(nodes.values())

        # Prepare test keys
        test_keys = [f"benchmark_key_{i:06d}" for i in range(num_operations)]

        # Pre-populate keys for lookup testing
        for i, key in enumerate(test_keys):
            node = node_list[i % len(node_list)]
            router = ChordRouter(node)
            router.put_key(key, f"value_{i}")

        # Benchmark lookup operations
        latencies = []
        hop_counts = []
        successful_operations = 0

        start_time = time.time()

        for key in test_keys:
            # Choose random starting node
            start_node = random.choice(node_list)
            router = ChordRouter(start_node)

            # Measure lookup latency
            lookup_start = time.time()

            try:
                result = router.lookup_key(key)
                lookup_end = time.time()

                latency_ms = (lookup_end - lookup_start) * 1000
                latencies.append(latency_ms)

                # Collect routing metrics
                metrics = router.get_routing_metrics()
                hop_counts.append(metrics.total_hops)

                successful_operations += 1

            except Exception as e:
                print(f"    Lookup failed for key {key}: {e}")

        total_time = time.time() - start_time

        # Calculate performance metrics
        if latencies:
            avg_latency = statistics.mean(latencies)
            p50_latency = statistics.median(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
            p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        else:
            avg_latency = p50_latency = p95_latency = p99_latency = 0.0

        avg_hops = statistics.mean(hop_counts) if hop_counts else 0.0
        theoretical_hops = max(1, int(self.m_bits / 2))  # Theoretical O(log N / 2)
        success_rate = successful_operations / num_operations
        throughput = successful_operations / total_time if total_time > 0 else 0.0

        result = BenchmarkResult(
            benchmark_name="lookup_performance",
            network_size=network_size,
            total_operations=num_operations,
            success_rate=success_rate,
            avg_latency_ms=avg_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            avg_hops=avg_hops,
            theoretical_hops=theoretical_hops,
            throughput_ops_per_sec=throughput,
            timestamp=time.time(),
            additional_metrics={
                'total_time_sec': total_time,
                'network_size': network_size
            }
        )

        self.results.append(result)
        self._print_benchmark_result(result)
        return result

    def run_scalability_benchmark(self, network_sizes: List[int],
                                 operations_per_size: int = 500) -> ScalabilityResult:
        """
        Benchmark scalability across different network sizes.

        Args:
            network_sizes: List of network sizes to test
            operations_per_size: Number of operations per network size

        Returns:
            ScalabilityResult with performance trends
        """
        print(f"📈 Running scalability benchmark across {len(network_sizes)} network sizes")

        lookup_latencies = []
        hop_counts = []
        theoretical_hops = []
        throughput_rates = []

        for size in network_sizes:
            print(f"  Testing network size: {size} nodes...")

            try:
                result = self.run_lookup_performance_benchmark(size, operations_per_size)

                lookup_latencies.append(result.avg_latency_ms)
                hop_counts.append(result.avg_hops)
                theoretical_hops.append(result.theoretical_hops)
                throughput_rates.append(result.throughput_ops_per_sec)

            except Exception as e:
                print(f"    Failed to benchmark size {size}: {e}")
                # Fill with zeros to maintain alignment
                lookup_latencies.append(0.0)
                hop_counts.append(0.0)
                theoretical_hops.append(0.0)
                throughput_rates.append(0.0)

        scalability_result = ScalabilityResult(
            network_sizes=network_sizes,
            lookup_latencies=lookup_latencies,
            hop_counts=hop_counts,
            theoretical_hops=theoretical_hops,
            throughput_rates=throughput_rates
        )

        self._analyze_scalability_results(scalability_result)
        return scalability_result

    def run_churn_benchmark(self, base_network_size: int, churn_events: int,
                          operations_during_churn: int = 200) -> BenchmarkResult:
        """
        Benchmark performance during network churn (nodes joining/leaving).

        Args:
            base_network_size: Initial network size
            churn_events: Number of join/leave events to simulate
            operations_during_churn: Lookup operations to perform during churn

        Returns:
            BenchmarkResult with churn performance metrics
        """
        print(f"🔄 Running churn benchmark (base={base_network_size}, churn={churn_events})")

        # Create initial network
        simulator = NetworkSimulator(self.m_bits)
        nodes = simulator.create_large_network(base_network_size, initial_keys=base_network_size * 5)

        if not nodes:
            raise ValueError("Failed to create initial network")

        protocols = JoinLeaveProtocols()
        latencies = []
        successful_operations = 0

        # Perform operations while introducing churn
        start_time = time.time()

        for churn_round in range(churn_events):
            # Randomly join or leave nodes
            if random.random() < 0.5 and len(nodes) > 5:  # Leave (maintain minimum nodes)
                leaving_node_id = random.choice(list(nodes.keys()))
                leaving_node = nodes[leaving_node_id]
                remaining_nodes = [n for nid, n in nodes.items() if nid != leaving_node_id]

                try:
                    protocols.leave_network(leaving_node, remaining_nodes)
                    del nodes[leaving_node_id]
                    print(f"    Node {leaving_node_id} left network ({len(nodes)} nodes remaining)")
                except Exception as e:
                    print(f"    Failed to remove node {leaving_node_id}: {e}")

            else:  # Join
                new_node_id = random.randint(0, self.ring_size - 1)
                if new_node_id not in nodes:
                    new_node = ChordNode(new_node_id, self.m_bits)
                    existing_node = random.choice(list(nodes.values()))

                    try:
                        protocols.join_network(new_node, existing_node)
                        nodes[new_node_id] = new_node
                        print(f"    Node {new_node_id} joined network ({len(nodes)} nodes total)")
                    except Exception as e:
                        print(f"    Failed to add node {new_node_id}: {e}")

            # Perform lookup operations during churn
            round_operations = operations_during_churn // churn_events
            test_keys = [f"churn_key_{churn_round}_{i}" for i in range(round_operations)]

            for key in test_keys:
                if not nodes:
                    break

                try:
                    start_node = random.choice(list(nodes.values()))
                    router = ChordRouter(start_node)

                    lookup_start = time.time()
                    result = router.lookup_key(key)
                    lookup_end = time.time()

                    latency_ms = (lookup_end - lookup_start) * 1000
                    latencies.append(latency_ms)
                    successful_operations += 1

                except Exception as e:
                    pass  # Expected failures during churn

        total_time = time.time() - start_time

        # Calculate metrics
        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
            p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        else:
            avg_latency = p95_latency = p99_latency = 0.0

        success_rate = successful_operations / operations_during_churn
        throughput = successful_operations / total_time if total_time > 0 else 0.0

        result = BenchmarkResult(
            benchmark_name="churn_performance",
            network_size=len(nodes),  # Final network size
            total_operations=operations_during_churn,
            success_rate=success_rate,
            avg_latency_ms=avg_latency,
            p50_latency_ms=statistics.median(latencies) if latencies else 0.0,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            avg_hops=0.0,  # Not tracked during churn
            theoretical_hops=max(1, int(self.m_bits / 2)),
            throughput_ops_per_sec=throughput,
            timestamp=time.time(),
            additional_metrics={
                'base_network_size': base_network_size,
                'churn_events': churn_events,
                'final_network_size': len(nodes),
                'total_churn_time_sec': total_time
            }
        )

        self.results.append(result)
        self._print_benchmark_result(result)
        return result

    def run_load_balancing_benchmark(self, network_size: int,
                                   num_keys: int = 10000) -> BenchmarkResult:
        """
        Benchmark load balancing characteristics of the DHT.

        Args:
            network_size: Number of nodes in test network
            num_keys: Number of keys to distribute

        Returns:
            BenchmarkResult with load balancing metrics
        """
        print(f"⚖️  Running load balancing benchmark (N={network_size}, keys={num_keys})")

        # Create network
        simulator = NetworkSimulator(self.m_bits)
        nodes = simulator.create_large_network(network_size, initial_keys=0)  # Start empty

        if not nodes:
            raise ValueError("Failed to create test network")

        node_list = list(nodes.values())

        # Distribute keys uniformly by hash
        start_time = time.time()

        for i in range(num_keys):
            key = f"load_key_{i:06d}"
            value = f"load_value_{i}"

            # Use consistent hashing to determine responsible node
            key_hash = hash_key(key)
            responsible_node = self._find_responsible_node(key_hash, nodes)

            if responsible_node:
                responsible_node.store_key(key, value)

        distribution_time = time.time() - start_time

        # Analyze load distribution
        key_counts = [len(node.data) for node in nodes.values()]
        max_load = max(key_counts) if key_counts else 0
        min_load = min(key_counts) if key_counts else 0
        avg_load = sum(key_counts) / len(key_counts) if key_counts else 0
        load_variance = statistics.variance(key_counts) if len(key_counts) > 1 else 0

        # Calculate load balancing metrics
        theoretical_avg = num_keys / network_size
        balance_ratio = min_load / max(max_load, 1)
        load_factor = max_load / max(theoretical_avg, 1)

        result = BenchmarkResult(
            benchmark_name="load_balancing",
            network_size=network_size,
            total_operations=num_keys,
            success_rate=1.0,  # All keys successfully placed
            avg_latency_ms=distribution_time * 1000 / num_keys,
            p50_latency_ms=0.0,
            p95_latency_ms=0.0,
            p99_latency_ms=0.0,
            avg_hops=0.0,  # Direct placement
            theoretical_hops=0.0,
            throughput_ops_per_sec=num_keys / distribution_time,
            timestamp=time.time(),
            additional_metrics={
                'max_load': max_load,
                'min_load': min_load,
                'avg_load': avg_load,
                'load_variance': load_variance,
                'balance_ratio': balance_ratio,
                'load_factor': load_factor,
                'theoretical_avg_load': theoretical_avg,
                'distribution_time_sec': distribution_time
            }
        )

        self.results.append(result)
        self._print_load_balancing_result(result)
        return result

    def _find_responsible_node(self, key_hash: int, nodes: Dict[int, ChordNode]) -> Optional[ChordNode]:
        """Find the node responsible for a given key hash."""
        if not nodes:
            return None

        sorted_node_ids = sorted(nodes.keys())

        # Find first node with ID >= key_hash
        for node_id in sorted_node_ids:
            if node_id >= key_hash:
                return nodes[node_id]

        # Wrap around to first node
        return nodes[sorted_node_ids[0]]

    def run_comprehensive_benchmark_suite(self):
        """Run the complete benchmark suite with various test scenarios."""
        print("🚀 COMPREHENSIVE CHORD DHT BENCHMARK SUITE")
        print("=" * 80)

        # Test scenarios
        scenarios = [
            ("Small Network", [8, 16, 32]),
            ("Medium Network", [64, 128, 256]),
            ("Large Network", [512, 1024]),
        ]

        all_results = {}

        for scenario_name, network_sizes in scenarios:
            print(f"\n📊 {scenario_name} Scenarios")
            print("-" * 40)

            # Scalability benchmark
            scalability_result = self.run_scalability_benchmark(network_sizes, 200)
            all_results[f"{scenario_name.lower().replace(' ', '_')}_scalability"] = scalability_result

            # Load balancing for largest network in scenario
            largest_network = max(network_sizes)
            load_result = self.run_load_balancing_benchmark(largest_network, largest_network * 20)
            all_results[f"{scenario_name.lower().replace(' ', '_')}_load"] = load_result

            # Churn testing for medium network
            if len(network_sizes) >= 2:
                medium_network = network_sizes[len(network_sizes) // 2]
                churn_result = self.run_churn_benchmark(medium_network, 20, 100)
                all_results[f"{scenario_name.lower().replace(' ', '_')}_churn"] = churn_result

        return all_results

    def _print_benchmark_result(self, result: BenchmarkResult):
        """Print formatted benchmark result."""
        print(f"\n📋 Benchmark Results: {result.benchmark_name}")
        print("-" * 50)
        print(f"  Network Size: {result.network_size} nodes")
        print(f"  Operations: {result.total_operations}")
        print(f"  Success Rate: {result.success_rate:.2%}")
        print(f"  Avg Latency: {result.avg_latency_ms:.3f} ms")
        print(f"  95th Percentile: {result.p95_latency_ms:.3f} ms")
        print(f"  99th Percentile: {result.p99_latency_ms:.3f} ms")
        if result.avg_hops > 0:
            print(f"  Avg Hops: {result.avg_hops:.2f}")
            print(f"  Theoretical Hops: {result.theoretical_hops}")
            efficiency = result.theoretical_hops / max(result.avg_hops, 0.1)
            print(f"  Routing Efficiency: {efficiency:.2f}x")
        print(f"  Throughput: {result.throughput_ops_per_sec:.1f} ops/sec")

    def _print_load_balancing_result(self, result: BenchmarkResult):
        """Print formatted load balancing result."""
        metrics = result.additional_metrics or {}

        print(f"\n⚖️  Load Balancing Results")
        print("-" * 50)
        print(f"  Network Size: {result.network_size} nodes")
        print(f"  Total Keys: {result.total_operations}")
        print(f"  Max Load: {metrics.get('max_load', 0)} keys")
        print(f"  Min Load: {metrics.get('min_load', 0)} keys")
        print(f"  Avg Load: {metrics.get('avg_load', 0):.1f} keys")
        print(f"  Load Variance: {metrics.get('load_variance', 0):.1f}")
        print(f"  Balance Ratio: {metrics.get('balance_ratio', 0):.3f}")
        print(f"  Load Factor: {metrics.get('load_factor', 0):.2f}")

        # Interpret balance quality
        balance_ratio = metrics.get('balance_ratio', 0)
        if balance_ratio >= 0.8:
            quality = "Excellent"
        elif balance_ratio >= 0.6:
            quality = "Good"
        elif balance_ratio >= 0.4:
            quality = "Fair"
        else:
            quality = "Poor"

        print(f"  Balance Quality: {quality}")

    def _analyze_scalability_results(self, result: ScalabilityResult):
        """Analyze and print scalability benchmark results."""
        print(f"\n📈 Scalability Analysis")
        print("-" * 50)

        print("Network Size | Avg Latency | Avg Hops | Theoretical | Throughput")
        print("-" * 65)

        for i, size in enumerate(result.network_sizes):
            latency = result.lookup_latencies[i]
            hops = result.hop_counts[i]
            theoretical = result.theoretical_hops[i]
            throughput = result.throughput_rates[i]

            print(f"{size:11d} | {latency:11.3f} | {hops:8.2f} | "
                  f"{theoretical:11.2f} | {throughput:10.1f}")

        # Calculate scalability trends
        if len(result.network_sizes) >= 2:
            size_growth = result.network_sizes[-1] / result.network_sizes[0]
            latency_growth = result.lookup_latencies[-1] / max(result.lookup_latencies[0], 0.001)
            hop_growth = result.hop_counts[-1] / max(result.hop_counts[0], 0.001)

            print(f"\nScalability Summary:")
            print(f"  Network size grew {size_growth:.1f}x")
            print(f"  Latency grew {latency_growth:.2f}x")
            print(f"  Hops grew {hop_growth:.2f}x")
            print(f"  Scalability ratio: {hop_growth / max(size_growth, 0.001):.3f}")

    def export_results(self, filename: str):
        """Export all benchmark results to JSON file."""
        export_data = {
            'benchmark_suite_config': {
                'ring_size_bits': self.m_bits,
                'ring_size': self.ring_size
            },
            'results': [asdict(result) for result in self.results],
            'export_timestamp': time.time()
        }

        filepath = f"/tmp/cc-exp/run_s40_2026-01-30_22-27-41/output/chord-dht/{filename}"
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"📊 Benchmark results exported to {filepath}")


def main():
    """Run comprehensive benchmarking demonstration."""
    print("⚡ Chord DHT Comprehensive Benchmark Suite")
    print("=" * 60)

    # Create benchmark suite
    benchmark = ChordBenchmarkSuite(m_bits=7)  # 128-position ring

    # Run comprehensive benchmarks
    results = benchmark.run_comprehensive_benchmark_suite()

    # Export results
    benchmark.export_results("benchmark_results.json")

    print("\n✅ Comprehensive benchmarking complete!")
    print(f"   Total benchmarks run: {len(benchmark.results)}")
    print(f"   Results exported for analysis")


if __name__ == "__main__":
    main()