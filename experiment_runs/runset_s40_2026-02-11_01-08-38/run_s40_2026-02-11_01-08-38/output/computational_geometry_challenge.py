#!/usr/bin/env python3
"""
Computational Geometry Challenge Framework
Testing local vs global optimization patterns in geometric algorithms

Created by Tara - exploring algorithmic paradigms through geometric problems
"""

import time
import math
import random
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod


class Point:
    """Simple 2D point representation"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9

    def __repr__(self):
        return f"Point({self.x:.2f}, {self.y:.2f})"

    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def cross_product(self, other, third):
        """Cross product for orientation test"""
        return (other.x - self.x) * (third.y - self.y) - (other.y - self.y) * (third.x - self.x)


class GeometryAlgorithm(ABC):
    """Base class for computational geometry algorithms"""

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def convex_hull(self, points: List[Point]) -> List[Point]:
        pass

    @abstractmethod
    def closest_pair(self, points: List[Point]) -> Tuple[Point, Point, float]:
        pass


class TaraGrahamScan(GeometryAlgorithm):
    """Graham Scan - Local angular sorting with incremental hull construction"""

    def name(self) -> str:
        return "Tara's Graham Scan (Local Angular Sort)"

    def convex_hull(self, points: List[Point]) -> List[Point]:
        if len(points) < 3:
            return points

        # Find bottom-most point (or leftmost if tie)
        start = min(points, key=lambda p: (p.y, p.x))

        # Sort by polar angle relative to start point
        def polar_angle(p):
            if p == start:
                return -math.pi  # Start point goes first
            return math.atan2(p.y - start.y, p.x - start.x)

        sorted_points = sorted(points, key=polar_angle)

        # Build hull with local decisions at each step
        hull = []
        for point in sorted_points:
            # Remove points that make right turn (local optimization)
            while len(hull) >= 2:
                if hull[-2].cross_product(hull[-1], point) <= 0:
                    hull.pop()
                else:
                    break
            hull.append(point)

        return hull

    def closest_pair(self, points: List[Point]) -> Tuple[Point, Point, float]:
        """Brute force O(n²) - simple but comprehensive"""
        if len(points) < 2:
            raise ValueError("Need at least 2 points")

        min_dist = float('inf')
        closest_pair = None

        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dist = points[i].distance_to(points[j])
                if dist < min_dist:
                    min_dist = dist
                    closest_pair = (points[i], points[j])

        return closest_pair[0], closest_pair[1], min_dist


class TaraIncrementalHull(GeometryAlgorithm):
    """Incremental Convex Hull - Purely local insertions"""

    def name(self) -> str:
        return "Tara's Incremental Hull (Pure Local Updates)"

    def convex_hull(self, points: List[Point]) -> List[Point]:
        if len(points) < 3:
            return points

        # Start with triangle
        hull = points[:3]
        # Ensure counterclockwise orientation
        if hull[0].cross_product(hull[1], hull[2]) < 0:
            hull[1], hull[2] = hull[2], hull[1]

        # Add points one by one with local updates
        for point in points[3:]:
            if self._point_inside_hull(point, hull):
                continue

            # Find tangent points and update hull locally
            hull = self._update_hull_with_point(hull, point)

        return hull

    def _point_inside_hull(self, point: Point, hull: List[Point]) -> bool:
        """Check if point is inside convex hull"""
        for i in range(len(hull)):
            j = (i + 1) % len(hull)
            if hull[i].cross_product(hull[j], point) < 0:
                return False
        return True

    def _update_hull_with_point(self, hull: List[Point], point: Point) -> List[Point]:
        """Local hull update when adding a point"""
        # Find tangent points
        n = len(hull)
        left_tangent = 0
        right_tangent = 0

        # Find left tangent
        for i in range(n):
            if hull[i].cross_product(point, hull[(i+1) % n]) >= 0:
                left_tangent = i
                break

        # Find right tangent
        for i in range(n):
            if hull[i].cross_product(point, hull[(i-1) % n]) <= 0:
                right_tangent = i
                break

        # Build new hull
        new_hull = [point]
        i = (right_tangent) % n
        while i != left_tangent:
            new_hull.append(hull[i])
            i = (i + 1) % n
        new_hull.append(hull[left_tangent])

        return new_hull

    def closest_pair(self, points: List[Point]) -> Tuple[Point, Point, float]:
        """Grid-based approach - local spatial partitioning"""
        if len(points) < 2:
            raise ValueError("Need at least 2 points")

        # Create spatial grid for local searches
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)

        grid_size = max(1, int(math.sqrt(len(points))))
        cell_width = (max_x - min_x) / grid_size
        cell_height = (max_y - min_y) / grid_size

        if cell_width == 0 or cell_height == 0:
            # Fallback to brute force for degenerate cases
            return TaraGrahamScan().closest_pair(points)

        # Group points by grid cell
        grid = {}
        for point in points:
            cell_x = int((point.x - min_x) / cell_width)
            cell_y = int((point.y - min_y) / cell_height)
            cell = (min(cell_x, grid_size-1), min(cell_y, grid_size-1))

            if cell not in grid:
                grid[cell] = []
            grid[cell].append(point)

        min_dist = float('inf')
        closest_pair = None

        # Check within each cell and neighboring cells (local optimization)
        for (cx, cy), cell_points in grid.items():
            for i in range(len(cell_points)):
                for j in range(i + 1, len(cell_points)):
                    dist = cell_points[i].distance_to(cell_points[j])
                    if dist < min_dist:
                        min_dist = dist
                        closest_pair = (cell_points[i], cell_points[j])

            # Check neighboring cells
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = (cx + dx, cy + dy)
                    if neighbor in grid:
                        for p1 in cell_points:
                            for p2 in grid[neighbor]:
                                dist = p1.distance_to(p2)
                                if dist < min_dist:
                                    min_dist = dist
                                    closest_pair = (p1, p2)

        return closest_pair[0], closest_pair[1], min_dist


class ComputationalGeometryChallenge:
    """Challenge framework for computational geometry algorithms"""

    def __init__(self):
        self.algorithms = []
        self.test_cases = self._generate_test_cases()

    def _generate_test_cases(self):
        """Generate test point sets of varying complexity"""
        test_cases = {}

        # Small regular case
        test_cases["small_square"] = [
            Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1),
            Point(0.5, 0.5), Point(0.3, 0.7)
        ]

        # Medium random case
        random.seed(42)
        medium_points = []
        for _ in range(20):
            medium_points.append(Point(random.uniform(0, 10), random.uniform(0, 10)))
        test_cases["medium_random"] = medium_points

        # Large circular pattern
        large_points = []
        for i in range(50):
            angle = 2 * math.pi * i / 50
            radius = 5 + random.uniform(-0.5, 0.5)
            large_points.append(Point(
                radius * math.cos(angle),
                radius * math.sin(angle)
            ))
        # Add some interior points
        for _ in range(10):
            angle = random.uniform(0, 2*math.pi)
            radius = random.uniform(0, 3)
            large_points.append(Point(
                radius * math.cos(angle),
                radius * math.sin(angle)
            ))
        test_cases["large_circular"] = large_points

        return test_cases

    def add_algorithm(self, algorithm: GeometryAlgorithm):
        """Add an algorithm implementation"""
        self.algorithms.append(algorithm)

    def benchmark_algorithm(self, algorithm: GeometryAlgorithm, operation: str, test_case: str, iterations: int = 100):
        """Benchmark a specific algorithm and operation"""
        points = self.test_cases[test_case]

        start_time = time.perf_counter()
        for _ in range(iterations):
            if operation == "convex_hull":
                result = algorithm.convex_hull(points.copy())
            elif operation == "closest_pair":
                result = algorithm.closest_pair(points.copy())
        end_time = time.perf_counter()

        avg_time_ms = ((end_time - start_time) / iterations) * 1000
        return avg_time_ms, result

    def compare_solutions(self):
        """Compare all algorithms across all test cases and operations"""
        if not self.algorithms:
            print("❌ No algorithms added yet!")
            return

        operations = ["convex_hull", "closest_pair"]
        test_cases = ["small_square", "medium_random", "large_circular"]

        print("🧮 COMPUTATIONAL GEOMETRY ALGORITHM COMPARISON")
        print("=" * 60)

        for operation in operations:
            print(f"\n📐 {operation.upper()} PERFORMANCE:")
            print("-" * 40)

            # Collect results for all algorithms and test cases
            results = []

            for algorithm in self.algorithms:
                total_time = 0
                for test_case in test_cases:
                    try:
                        avg_time, result = self.benchmark_algorithm(algorithm, operation, test_case)
                        total_time += avg_time
                    except Exception as e:
                        print(f"❌ {algorithm.name()} failed on {test_case}: {e}")
                        total_time = float('inf')
                        break

                if total_time != float('inf'):
                    results.append((algorithm.name(), total_time, algorithm))

            # Sort by performance and display
            results.sort(key=lambda x: x[1])

            for i, (name, total_time, algorithm) in enumerate(results, 1):
                print(f"{i}. {name}")
                print(f"   Total time: {total_time:.4f} ms")

                # Show detailed breakdown for top performer
                if i == 1:
                    print("   📊 Detailed breakdown:")
                    for test_case in test_cases:
                        avg_time, result = self.benchmark_algorithm(algorithm, operation, test_case)
                        print(f"      {test_case}: {avg_time:.4f} ms")
                print()

        print("🎯 ALGORITHMIC INSIGHTS:")
        print("- Local vs global optimization patterns")
        print("- Incremental vs batch processing trade-offs")
        print("- Spatial partitioning vs comprehensive search strategies")
        print("=" * 60)


def main():
    """Demonstrate the computational geometry challenge framework"""
    print("🔷 Computational Geometry Challenge Framework")
    print("Testing local vs global optimization patterns!")
    print()

    # Create challenge and add Tara's algorithms
    challenge = ComputationalGeometryChallenge()
    challenge.add_algorithm(TaraGrahamScan())
    challenge.add_algorithm(TaraIncrementalHull())

    # Run comprehensive comparison
    challenge.compare_solutions()

    print("\n🚀 Framework ready for Dave's algorithms!")
    print("Add your implementations with: challenge.add_algorithm(YourAlgorithm())")


if __name__ == "__main__":
    main()