#!/usr/bin/env python3
"""
Interactive Tree Evolution Visualizer
Author: Dave
Parent: 9866f6e4 (Tara's Self-Balancing AVL BST)

A real-time visualization system that brings our evolutionary code garden to life!
This system creates beautiful, animated visualizations of tree operations,
evolution history playback, and performance analytics dashboards.

Features:
- Real-time tree structure rendering with ASCII art
- Animation system for rotations and insertions
- Evolution history playback with step-by-step visualization
- Performance metrics dashboard
- Interactive exploration of our garden's growth
"""

import time
import json
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import sys

# Import our evolved BST
sys.path.append('/tmp/cc-exp/run_s40_2026-02-11_01-30-46/output/garden_data')
from variant_9866f6e4 import SelfBalancingBST, AVLNode


class TreeVisualizer:
    """Real-time ASCII tree visualization with animation support."""

    def __init__(self, width=120, height=30):
        self.width = width
        self.height = height
        self.animation_delay = 0.5  # seconds between animation frames

    def visualize_tree(self, root: AVLNode, title: str = "") -> str:
        """Create a beautiful ASCII representation of the tree."""
        if root is None:
            return f"\n{title}\n{'='*50}\n🌿 Empty tree 🌿\n"

        lines = []
        if title:
            lines.append(f"\n{title}")
            lines.append("=" * len(title))

        # Build tree representation
        tree_lines = self._build_tree_lines(root)
        lines.extend(tree_lines)

        return "\n".join(lines)

    def _build_tree_lines(self, node: AVLNode) -> List[str]:
        """Build ASCII art lines for the tree structure."""
        if node is None:
            return [""]

        # Get subtrees
        left_lines = self._build_tree_lines(node.left) if node.left else [""]
        right_lines = self._build_tree_lines(node.right) if node.right else [""]

        # Create node representation with balance info
        balance = self._get_balance(node)
        node_str = f"[{node.value}|h:{node.height}|b:{balance:+d}]"

        # Calculate widths
        left_width = max(len(line) for line in left_lines) if left_lines[0] else 0
        right_width = max(len(line) for line in right_lines) if right_lines[0] else 0
        node_width = len(node_str)

        # Pad lines to equal length
        left_lines = [line.ljust(left_width) for line in left_lines]
        right_lines = [line.ljust(right_width) for line in right_lines]

        # Create the combined structure
        total_width = left_width + node_width + right_width + 2
        result_lines = []

        # Add node line
        left_padding = left_width + 1 if left_width > 0 else 0
        node_line = " " * left_padding + node_str
        result_lines.append(node_line)

        # Add connector lines if children exist
        if node.left or node.right:
            connector_line = ""
            if left_width > 0:
                connector_line += " " * (left_width // 2) + "┌" + "─" * (left_width // 2)
            else:
                connector_line += " "

            connector_line += "┴"

            if right_width > 0:
                connector_line += "─" * (right_width // 2) + "┐" + " " * (right_width // 2)
            else:
                connector_line += " "

            result_lines.append(connector_line)

        # Combine left and right subtrees
        max_lines = max(len(left_lines), len(right_lines))
        for i in range(max_lines):
            line = ""

            # Add left subtree line
            if i < len(left_lines):
                line += left_lines[i]
            else:
                line += " " * left_width

            # Add spacing
            line += " "

            # Add right subtree line
            if i < len(right_lines):
                line += right_lines[i]
            else:
                line += " " * right_width

            result_lines.append(line)

        return result_lines

    def _get_balance(self, node: AVLNode) -> int:
        """Calculate balance factor for a node."""
        if node is None:
            return 0
        left_height = node.left.height if node.left else 0
        right_height = node.right.height if node.right else 0
        return left_height - right_height

    def animate_insertion(self, bst: SelfBalancingBST, value: int):
        """Show animated insertion process."""
        print(f"\n🎬 ANIMATING INSERTION of {value}")
        print("=" * 50)

        # Show before state
        print("📸 BEFORE:")
        print(self.visualize_tree(bst.root, f"Tree before inserting {value}"))

        # Show during insertion message
        print(f"\n⚡ Inserting {value}...")
        time.sleep(self.animation_delay)

        # Perform insertion
        old_rotations = bst.rotation_count
        bst.insert(value)
        new_rotations = bst.rotation_count

        # Show after state
        print("📸 AFTER:")
        print(self.visualize_tree(bst.root, f"Tree after inserting {value}"))

        # Show rotation info
        rotations_performed = new_rotations - old_rotations
        if rotations_performed > 0:
            print(f"🔄 Performed {rotations_performed} rotation(s) to maintain balance")
        else:
            print("✅ No rotations needed - tree remained balanced")

        print(f"📊 Tree Stats: Height={bst.get_tree_height()}, Size={bst.get_size()}")

    def animate_search(self, bst: SelfBalancingBST, value: int):
        """Show animated search process."""
        print(f"\n🔍 ANIMATING SEARCH for {value}")
        print("=" * 50)

        # Check if in cache
        cache_hit = value in bst.search_cache
        if cache_hit:
            print(f"⚡ CACHE HIT! Found {value} in search cache")
        else:
            print(f"🔎 Cache miss - searching tree for {value}")

        # Show the path through the tree
        path = self._trace_search_path(bst.root, value)

        print(f"🛤️  Search path: {' → '.join(map(str, path))}")

        result = bst.search(value)
        result_emoji = "✅ FOUND" if result else "❌ NOT FOUND"
        print(f"{result_emoji}: {value}")

    def _trace_search_path(self, node: AVLNode, value: int) -> List[int]:
        """Trace the path taken during search."""
        path = []
        current = node

        while current is not None:
            path.append(current.value)
            if current.value == value:
                break
            elif value < current.value:
                current = current.left
            else:
                current = current.right

        return path


class EvolutionPlayback:
    """System for playing back the evolution history with visualizations."""

    def __init__(self, garden_path: str):
        self.garden_path = Path(garden_path)
        self.visualizer = TreeVisualizer()

    def load_evolution_history(self) -> Dict[str, Any]:
        """Load the complete evolution history."""
        history_file = self.garden_path / "evolution_history.json"

        if not history_file.exists():
            return {}

        with open(history_file, 'r') as f:
            return json.load(f)

    def play_evolution_story(self):
        """Play through our entire evolutionary journey."""
        history = self.load_evolution_history()

        if not history:
            print("🌱 No evolution history found!")
            return

        print("🎭 EVOLUTIONARY CODE GARDEN STORY")
        print("=" * 60)
        print("🎬 Playing back our collaborative journey...")

        # Sort evolutions chronologically
        evolutions = sorted(history.values(), key=lambda x: x['timestamp'])

        for i, evolution in enumerate(evolutions, 1):
            print(f"\n🎞️  SCENE {i}: {evolution['author']}'s Evolution")
            print(f"🎯 ID: {evolution['id']}")
            print(f"⏰ Time: {evolution['timestamp']}")
            print(f"🧬 Parent: {evolution['parent_id'] or 'SEED'}")
            print(f"💭 Reasoning: {evolution['reasoning']}")

            # Show key metrics
            if 'metrics' in evolution:
                metrics = evolution['metrics']
                print("📊 Key Metrics:")
                for key, value in metrics.items():
                    print(f"   {key}: {value}")

            # Show test results summary
            if 'test_results' in evolution:
                test_results = evolution['test_results']
                passed = test_results.get('functionality_tests', {}).get('all_passed', False)
                status = "✅ PASSED" if passed else "❌ FAILED"
                print(f"🧪 Tests: {status}")

            print(f"🏷️  Tags: {', '.join(evolution.get('tags', []))}")

            # Pause between scenes
            time.sleep(1)

        print(f"\n🎉 Evolution Story Complete!")
        print(f"📈 Total Evolutions: {len(evolutions)}")
        authors = set(evo['author'] for evo in evolutions)
        print(f"👥 Collaborators: {', '.join(authors)}")


class PerformanceDashboard:
    """Real-time performance monitoring dashboard."""

    def __init__(self):
        self.metrics_history = []

    def create_dashboard(self, bst: SelfBalancingBST) -> str:
        """Create a comprehensive performance dashboard."""
        lines = []

        lines.append("🎛️  PERFORMANCE DASHBOARD")
        lines.append("=" * 60)

        # Tree Statistics
        balance_stats = bst.get_balance_stats()
        cache_stats = bst.get_cache_stats()

        lines.append("\n📏 TREE STRUCTURE METRICS:")
        lines.append(f"├─ Total Nodes: {balance_stats['total_nodes']}")
        lines.append(f"├─ Tree Height: {balance_stats['tree_height']}")
        lines.append(f"├─ Theoretical Min Height: {balance_stats['theoretical_min_height']}")
        lines.append(f"├─ Height Efficiency: {balance_stats['height_efficiency']:.2f}")
        lines.append(f"├─ Total Rotations: {balance_stats['rotation_count']}")
        lines.append(f"└─ Is Balanced: {'✅' if balance_stats['is_balanced'] else '❌'}")

        lines.append("\n🧠 CACHE PERFORMANCE:")
        lines.append(f"├─ Cache Usage: {cache_stats['cache_size']}/{cache_stats['cache_max_size']}")
        cache_utilization = cache_stats['cache_size'] / cache_stats['cache_max_size'] * 100
        lines.append(f"├─ Cache Utilization: {cache_utilization:.1f}%")
        lines.append(f"└─ Cached Values: {cache_stats['cached_values']}")

        # Performance Indicators
        lines.append("\n⚡ PERFORMANCE INDICATORS:")

        # Height efficiency indicator
        if balance_stats['height_efficiency'] <= 1.2:
            height_status = "🟢 EXCELLENT"
        elif balance_stats['height_efficiency'] <= 1.5:
            height_status = "🟡 GOOD"
        else:
            height_status = "🔴 POOR"
        lines.append(f"├─ Height Efficiency: {height_status}")

        # Balance status
        balance_status = "🟢 BALANCED" if balance_stats['is_balanced'] else "🔴 UNBALANCED"
        lines.append(f"├─ Tree Balance: {balance_status}")

        # Cache efficiency
        if cache_utilization >= 80:
            cache_status = "🟢 HIGH USAGE"
        elif cache_utilization >= 50:
            cache_status = "🟡 MODERATE"
        else:
            cache_status = "🔴 LOW USAGE"
        lines.append(f"└─ Cache Efficiency: {cache_status}")

        return "\n".join(lines)

    def benchmark_operations(self, bst: SelfBalancingBST) -> str:
        """Run performance benchmarks and return results."""
        lines = []
        lines.append("\n🏃 PERFORMANCE BENCHMARKS")
        lines.append("=" * 40)

        # Benchmark insertions
        print("Running insertion benchmark...")
        insert_times = []
        test_bst = SelfBalancingBST()

        for i in range(100):
            start_time = time.perf_counter()
            test_bst.insert(i)
            end_time = time.perf_counter()
            insert_times.append((end_time - start_time) * 1000)  # Convert to ms

        avg_insert_time = sum(insert_times) / len(insert_times)
        lines.append(f"📊 Average Insertion Time: {avg_insert_time:.4f}ms")

        # Benchmark searches
        print("Running search benchmark...")
        search_times = []

        for i in range(100):
            start_time = time.perf_counter()
            test_bst.search(i // 2)  # Mix of hits and misses
            end_time = time.perf_counter()
            search_times.append((end_time - start_time) * 1000)

        avg_search_time = sum(search_times) / len(search_times)
        lines.append(f"🔍 Average Search Time: {avg_search_time:.4f}ms")

        # Cache effectiveness
        cache_hits = sum(1 for i in range(50) if (i // 2) in test_bst.search_cache)
        cache_hit_rate = (cache_hits / 50) * 100
        lines.append(f"🎯 Cache Hit Rate: {cache_hit_rate:.1f}%")

        return "\n".join(lines)


class InteractiveDemo:
    """Interactive demonstration of our evolved BST."""

    def __init__(self):
        self.visualizer = TreeVisualizer()
        self.dashboard = PerformanceDashboard()
        self.playback = EvolutionPlayback("/tmp/cc-exp/run_s40_2026-02-11_01-30-46/output/garden_data")

    def run_complete_demo(self):
        """Run the complete interactive demonstration."""
        print("🎪 WELCOME TO THE EVOLUTIONARY CODE GARDEN SHOWCASE!")
        print("=" * 70)
        print("🤖 Created by Dave & Tara - Two Claude Code instances collaborating")
        print("🌱 Watch our BST evolve through performance optimization and self-balancing!")

        # Play evolution story
        self.playback.play_evolution_story()

        # Interactive tree demo
        print("\n" + "=" * 70)
        print("🎮 INTERACTIVE BST DEMONSTRATION")
        print("=" * 70)

        # Create our evolved BST
        bst = SelfBalancingBST(cache_size=10)

        # Demo pathological insertion (this would break regular BST)
        print("\n🎭 SCENE 1: The Pathological Challenge")
        print("💥 Regular BST would create a degenerate tree with sequential insertions")
        print("🦾 Our AVL evolution handles this gracefully!")

        pathological_values = [1, 2, 3, 4, 5, 6, 7, 8]

        for value in pathological_values:
            self.visualizer.animate_insertion(bst, value)
            time.sleep(0.3)

        # Show final dashboard
        print("\n" + "=" * 70)
        print(self.dashboard.create_dashboard(bst))

        # Demo search performance
        print("\n🎭 SCENE 2: Search Performance Showcase")
        print("🧠 Demonstrating Dave's caching optimization...")

        # Perform searches to demonstrate caching
        for search_value in [4, 6, 4, 8, 4, 6]:  # Repeated searches
            self.visualizer.animate_search(bst, search_value)
            time.sleep(0.5)

        # Final performance benchmarks
        benchmark_results = self.dashboard.benchmark_operations(bst)
        print(benchmark_results)

        # Grand finale
        print("\n" + "🎉" * 70)
        print("🏆 EVOLUTIONARY SUCCESS!")
        print("🤝 This BST represents the power of AI collaboration:")
        print("   🔹 Dave's contribution: Performance optimization & caching")
        print("   🔹 Tara's contribution: Self-balancing AVL architecture")
        print("   🔹 Combined result: A robust, fast, self-maintaining data structure")
        print("🌟 Neither could have achieved this alone - collaboration is key!")
        print("🎉" * 70)


if __name__ == "__main__":
    print("🎬 Starting Interactive Tree Evolution Visualization...")
    demo = InteractiveDemo()
    demo.run_complete_demo()