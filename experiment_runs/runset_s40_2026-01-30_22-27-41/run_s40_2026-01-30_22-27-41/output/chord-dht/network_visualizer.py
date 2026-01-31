#!/usr/bin/env python3
"""
Network Visualization for Chord DHT
===================================

This module provides advanced visualization capabilities for analyzing
and understanding Chord DHT network topology, routing paths, and data distribution.

Features:
- ASCII ring topology visualization
- Routing path visualization
- Data distribution heatmaps
- Network health dashboards
- Real-time monitoring displays
- Export to various formats

Authors: Bob (Phase 5 - Visualization) & Alice (Phases 1-4)
"""

import math
import json
import time
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass

from chord_node import ChordNode
from routing import ChordRouter
from consistent_hash import hash_key
from network_simulator import NetworkSimulator, SimulationMetrics


@dataclass
class VisualizationStyle:
    """Configuration for visualization appearance."""
    ring_radius: int = 20
    node_symbol: str = "●"
    key_symbol: str = "◆"
    successor_symbol: str = "→"
    finger_symbol: str = "⟶"
    empty_symbol: str = "·"
    highlight_symbol: str = "★"


class NetworkVisualizer:
    """
    Advanced visualization engine for Chord DHT networks.

    Provides multiple visualization modes for understanding network topology,
    routing behavior, and system performance.
    """

    def __init__(self, style: Optional[VisualizationStyle] = None):
        """Initialize visualizer with specified style."""
        self.style = style or VisualizationStyle()
        self.width = 120  # Console width for visualizations
        self.height = 40  # Console height for visualizations

    def visualize_ring_topology(self, nodes: Dict[int, ChordNode],
                               ring_size: int, highlight_nodes: Set[int] = None):
        """
        Create ASCII art visualization of the Chord ring topology.

        Args:
            nodes: Dictionary of node_id -> ChordNode
            ring_size: Size of the hash ring (2^m)
            highlight_nodes: Set of node IDs to highlight
        """
        if not nodes:
            print("❌ No nodes to visualize")
            return

        highlight_nodes = highlight_nodes or set()

        print(f"\n🔄 CHORD RING TOPOLOGY (Ring Size: {ring_size})")
        print("=" * 80)

        # Calculate positions for nodes on a circle
        center_x, center_y = self.style.ring_radius, self.style.ring_radius
        node_positions = {}

        # Sort nodes by ID for consistent visualization
        sorted_nodes = sorted(nodes.items())

        # Calculate angular positions
        for node_id, node in sorted_nodes:
            angle = 2 * math.pi * node_id / ring_size
            x = center_x + int(self.style.ring_radius * math.cos(angle))
            y = center_y + int(self.style.ring_radius * math.sin(angle))
            node_positions[node_id] = (x, y)

        # Create visualization grid
        grid_size = 2 * self.style.ring_radius + 10
        grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]

        # Place nodes on grid
        for node_id, (x, y) in node_positions.items():
            if 0 <= x < grid_size and 0 <= y < grid_size:
                if node_id in highlight_nodes:
                    grid[y][x] = self.style.highlight_symbol
                else:
                    grid[y][x] = self.style.node_symbol

        # Draw ring outline
        for angle_deg in range(0, 360, 5):
            angle = math.radians(angle_deg)
            x = center_x + int(self.style.ring_radius * math.cos(angle))
            y = center_y + int(self.style.ring_radius * math.sin(angle))
            if 0 <= x < grid_size and 0 <= y < grid_size and grid[y][x] == ' ':
                grid[y][x] = self.style.empty_symbol

        # Print grid
        for row in grid:
            print(''.join(row))

        # Print node legend
        print("\n📍 NODE INFORMATION:")
        for node_id in sorted(nodes.keys())[:10]:  # Show first 10 nodes
            node = nodes[node_id]
            symbol = self.style.highlight_symbol if node_id in highlight_nodes else self.style.node_symbol
            successor_id = node.successor if node.successor else "None"
            key_count = len(node.data)
            print(f"  {symbol} Node {node_id:3d}: successor={successor_id:>3}, keys={key_count:3d}")

        if len(nodes) > 10:
            print(f"  ... and {len(nodes) - 10} more nodes")

    def visualize_routing_path(self, start_node: ChordNode, target_key: str,
                             nodes: Dict[int, ChordNode]):
        """
        Visualize the routing path for a key lookup.

        Args:
            start_node: Node initiating the lookup
            target_key: Key being looked up
            nodes: All nodes in the network
        """
        print(f"\n🎯 ROUTING PATH VISUALIZATION")
        print("=" * 80)
        print(f"Key: '{target_key}' (hash: {hash_key(target_key)})")
        print(f"Starting from Node {start_node.node_id}")

        # Perform lookup and capture routing path
        router = ChordRouter(start_node)

        try:
            # Capture routing path (this would need to be enhanced in the routing module)
            result = router.lookup_key(target_key)
            path = self._trace_routing_path(start_node, target_key, nodes)

            print(f"\n📋 Routing Path:")
            for i, (node_id, action) in enumerate(path):
                prefix = "  └─" if i == len(path) - 1 else "  ├─"
                print(f"{prefix} Node {node_id:3d}: {action}")

            metrics = router.get_routing_metrics()
            print(f"\n📊 Routing Statistics:")
            print(f"  Total Hops: {metrics.total_hops}")
            print(f"  Cache Hits: {metrics.cache_hits}")
            print(f"  Cache Misses: {metrics.cache_misses}")

        except Exception as e:
            print(f"❌ Routing failed: {e}")

    def _trace_routing_path(self, start_node: ChordNode, key: str,
                           nodes: Dict[int, ChordNode]) -> List[Tuple[int, str]]:
        """
        Trace the actual routing path taken for a key lookup.

        This is a simplified version - in practice, we'd need to modify
        the routing code to capture the actual path taken.
        """
        path = []
        current_node = start_node
        target_hash = hash_key(key)

        path.append((current_node.node_id, f"Start lookup for key hash {target_hash}"))

        # Simulate routing path using finger table
        max_hops = 20  # Prevent infinite loops

        for hop in range(max_hops):
            # Check if current node is responsible for the key
            if current_node.is_responsible_for_key(key):
                path.append((current_node.node_id, f"Found! Node is responsible for key"))
                break

            # Find next hop using finger table or successor
            if hasattr(current_node, 'finger_table') and current_node.finger_table:
                # Use finger table to find closest preceding node
                best_node_id = current_node.node_id
                for finger in current_node.finger_table.fingers:
                    if finger.node and finger.node in nodes:
                        finger_node = nodes[finger.node]
                        # Simple heuristic: choose finger that gets us closer to target
                        if self._is_closer_to_target(finger_node.node_id, target_hash,
                                                   current_node.node_id, len(nodes)):
                            best_node_id = finger_node.node_id

                if best_node_id != current_node.node_id:
                    path.append((current_node.node_id, f"Route via finger table to Node {best_node_id}"))
                    current_node = nodes[best_node_id]
                    continue

            # Fall back to successor
            if current_node.successor and current_node.successor in nodes:
                path.append((current_node.node_id, f"Route to successor Node {current_node.successor}"))
                current_node = nodes[current_node.successor]
            else:
                path.append((current_node.node_id, "No successor available - routing failed"))
                break

        return path

    def _is_closer_to_target(self, candidate_id: int, target_hash: int,
                           current_id: int, ring_size: int) -> bool:
        """Simple heuristic to determine if a candidate node is closer to target."""
        # Calculate distances in ring
        current_distance = (target_hash - current_id) % ring_size
        candidate_distance = (target_hash - candidate_id) % ring_size

        return candidate_distance < current_distance

    def visualize_data_distribution(self, nodes: Dict[int, ChordNode], ring_size: int):
        """
        Create a visualization of data distribution across nodes.

        Args:
            nodes: Dictionary of node_id -> ChordNode
            ring_size: Size of the hash ring
        """
        print(f"\n📊 DATA DISTRIBUTION ANALYSIS")
        print("=" * 80)

        if not nodes:
            print("❌ No nodes to analyze")
            return

        # Collect data distribution statistics
        node_data = []
        total_keys = 0

        for node_id in sorted(nodes.keys()):
            node = nodes[node_id]
            key_count = len(node.data)
            total_keys += key_count

            # Calculate ring segment size this node is responsible for
            segment_size = self._calculate_segment_size(node_id, nodes, ring_size)

            node_data.append({
                'node_id': node_id,
                'key_count': key_count,
                'segment_size': segment_size,
                'density': key_count / max(segment_size, 1) * ring_size
            })

        # Sort by node ID for display
        node_data.sort(key=lambda x: x['node_id'])

        # Display distribution table
        print("Node ID | Keys | Segment Size | Density | Load Bar")
        print("-" * 60)

        max_keys = max(data['key_count'] for data in node_data) if node_data else 1

        for data in node_data:
            # Create load bar visualization
            bar_length = 20
            load_ratio = data['key_count'] / max(max_keys, 1)
            filled_blocks = int(load_ratio * bar_length)

            load_bar = "█" * filled_blocks + "░" * (bar_length - filled_blocks)

            print(f"{data['node_id']:7d} | {data['key_count']:4d} | "
                  f"{data['segment_size']:12.1f} | {data['density']:7.3f} | {load_bar}")

        # Calculate and display statistics
        if node_data:
            key_counts = [data['key_count'] for data in node_data]
            avg_keys = sum(key_counts) / len(key_counts)
            max_keys = max(key_counts)
            min_keys = min(key_counts)

            print(f"\n📈 Distribution Statistics:")
            print(f"  Total Keys: {total_keys}")
            print(f"  Average Keys per Node: {avg_keys:.2f}")
            print(f"  Max Keys on Node: {max_keys}")
            print(f"  Min Keys on Node: {min_keys}")
            print(f"  Load Balance Ratio: {min_keys / max(max_keys, 1):.3f}")

    def _calculate_segment_size(self, node_id: int, nodes: Dict[int, ChordNode],
                              ring_size: int) -> float:
        """Calculate the ring segment size a node is responsible for."""
        sorted_ids = sorted(nodes.keys())

        if len(sorted_ids) <= 1:
            return ring_size

        try:
            idx = sorted_ids.index(node_id)
            prev_idx = (idx - 1) % len(sorted_ids)
            prev_id = sorted_ids[prev_idx]

            # Calculate segment size (distance from predecessor to this node)
            if node_id > prev_id:
                segment_size = node_id - prev_id
            else:
                segment_size = ring_size - prev_id + node_id

            return segment_size

        except ValueError:
            return ring_size / len(nodes)

    def create_network_dashboard(self, simulator: NetworkSimulator):
        """
        Create a comprehensive network health dashboard.

        Args:
            simulator: NetworkSimulator instance with current network state
        """
        print(f"\n🖥️  CHORD DHT NETWORK DASHBOARD")
        print("=" * 100)

        # Collect current metrics
        metrics = simulator.collect_network_metrics()

        # Header with timestamp
        print(f"📅 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(metrics.timestamp))}")
        print(f"🔧 Ring Configuration: 2^{simulator.m_bits} positions ({simulator.ring_size} total)")

        # Network Health Overview
        print(f"\n🌐 NETWORK HEALTH OVERVIEW")
        print("-" * 50)

        # Create health indicators
        health_indicators = [
            ("Connectivity", metrics.ring_connectivity, 0.95, "%"),
            ("Success Rate", metrics.lookup_success_rate, 0.90, "%"),
            ("Load Balance", 1.0 - (metrics.data_distribution_variance / 100), 0.80, "%"),
        ]

        for indicator, value, threshold, unit in health_indicators:
            status = "🟢" if value >= threshold else "🟡" if value >= threshold * 0.8 else "🔴"
            if unit == "%":
                display_value = f"{value:.1%}"
            else:
                display_value = f"{value:.2f}"
            print(f"  {status} {indicator:<15}: {display_value:>8}")

        # Performance Metrics
        print(f"\n⚡ PERFORMANCE METRICS")
        print("-" * 50)
        print(f"  📊 Average Hops per Lookup: {metrics.average_hops:.2f}")
        print(f"  📏 Network Diameter: {metrics.network_diameter}")
        print(f"  📈 Total Operations: {getattr(metrics, 'total_operations', 'N/A')}")

        # Node Statistics
        print(f"\n🖥️  NODE STATISTICS")
        print("-" * 50)
        print(f"  🔢 Total Nodes: {metrics.total_nodes}")
        print(f"  ✅ Active Nodes: {metrics.active_nodes}")
        print(f"  📁 Total Keys Stored: {metrics.total_keys}")
        print(f"  📊 Keys per Node: {metrics.total_keys / max(metrics.active_nodes, 1):.2f}")

        # Network Topology Visualization
        if simulator.nodes:
            print(f"\n🔄 RING TOPOLOGY SUMMARY")
            print("-" * 50)

            # Show ring coverage
            ring_coverage = self._calculate_ring_coverage(simulator.nodes, simulator.ring_size)
            print(f"  Ring Coverage: {ring_coverage:.1%}")

            # Show largest gap
            largest_gap = self._find_largest_gap(simulator.nodes, simulator.ring_size)
            print(f"  Largest Gap: {largest_gap} positions")

            # Show node distribution balance
            balance_score = self._calculate_balance_score(simulator.nodes, simulator.ring_size)
            print(f"  Balance Score: {balance_score:.3f}")

        # Historical Trends (if available)
        if len(simulator.metrics_history) > 1:
            print(f"\n📈 HISTORICAL TRENDS")
            print("-" * 50)

            current = simulator.metrics_history[-1]
            previous = simulator.metrics_history[-2]

            trends = [
                ("Connectivity", current.ring_connectivity, previous.ring_connectivity),
                ("Success Rate", current.lookup_success_rate, previous.lookup_success_rate),
                ("Avg Hops", current.average_hops, previous.average_hops),
            ]

            for metric_name, current_val, previous_val in trends:
                if previous_val != 0:
                    change = ((current_val - previous_val) / previous_val) * 100
                    trend_icon = "📈" if change > 1 else "📉" if change < -1 else "➡️"
                    print(f"  {trend_icon} {metric_name}: {change:+.1f}%")

        print("=" * 100)

    def _calculate_ring_coverage(self, nodes: Dict[int, ChordNode], ring_size: int) -> float:
        """Calculate what fraction of the ring has nodes."""
        if not nodes:
            return 0.0

        # This is a simplified metric - in practice, we'd calculate actual coverage
        return len(nodes) / ring_size if ring_size > 0 else 0.0

    def _find_largest_gap(self, nodes: Dict[int, ChordNode], ring_size: int) -> int:
        """Find the largest gap between consecutive nodes."""
        if len(nodes) <= 1:
            return ring_size

        sorted_ids = sorted(nodes.keys())

        max_gap = 0
        for i in range(len(sorted_ids)):
            current = sorted_ids[i]
            next_node = sorted_ids[(i + 1) % len(sorted_ids)]

            if next_node > current:
                gap = next_node - current
            else:
                gap = ring_size - current + next_node

            max_gap = max(max_gap, gap)

        return max_gap

    def _calculate_balance_score(self, nodes: Dict[int, ChordNode], ring_size: int) -> float:
        """Calculate how well-balanced the node distribution is."""
        if len(nodes) <= 1:
            return 1.0

        # Calculate expected distance between nodes
        expected_distance = ring_size / len(nodes)

        # Calculate actual distances
        sorted_ids = sorted(nodes.keys())
        distances = []

        for i in range(len(sorted_ids)):
            current = sorted_ids[i]
            next_node = sorted_ids[(i + 1) % len(sorted_ids)]

            if next_node > current:
                distance = next_node - current
            else:
                distance = ring_size - current + next_node

            distances.append(distance)

        # Calculate coefficient of variation
        if not distances:
            return 1.0

        mean_distance = sum(distances) / len(distances)
        variance = sum((d - mean_distance) ** 2 for d in distances) / len(distances)
        std_dev = math.sqrt(variance)

        if mean_distance == 0:
            return 1.0

        cv = std_dev / mean_distance

        # Convert to balance score (lower CV = higher balance)
        balance_score = max(0.0, 1.0 - cv)
        return balance_score


def main():
    """Demonstrate network visualization capabilities."""
    print("🎨 Advanced Chord DHT Network Visualizer")
    print("=" * 50)

    # Create sample network
    simulator = NetworkSimulator(m_bits=6)  # 64-position ring
    nodes = simulator.create_large_network(num_nodes=12, initial_keys=50)

    # Initialize visualizer
    visualizer = NetworkVisualizer()

    # Demo 1: Ring topology visualization
    print("\n🔍 Demo 1: Ring Topology Visualization")
    highlight_set = {list(nodes.keys())[0], list(nodes.keys())[1]}  # Highlight first two nodes
    visualizer.visualize_ring_topology(nodes, simulator.ring_size, highlight_set)

    # Demo 2: Routing path visualization
    print("\n🔍 Demo 2: Routing Path Visualization")
    start_node = list(nodes.values())[0]
    test_key = "test_routing_key"
    visualizer.visualize_routing_path(start_node, test_key, nodes)

    # Demo 3: Data distribution visualization
    print("\n🔍 Demo 3: Data Distribution Visualization")
    visualizer.visualize_data_distribution(nodes, simulator.ring_size)

    # Demo 4: Network dashboard
    print("\n🔍 Demo 4: Network Health Dashboard")
    visualizer.create_network_dashboard(simulator)

    print("\n✅ Visualization demonstration complete!")


if __name__ == "__main__":
    main()