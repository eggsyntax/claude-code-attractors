/**
 * Comprehensive Test Suite for Advanced Pathfinding Algorithms
 * Tests Dijkstra's and A* implementations with various graph scenarios
 */

// Test Framework
class TestSuite {
    constructor(name) {
        this.name = name;
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    test(description, testFunction) {
        try {
            testFunction();
            this.passed++;
            console.log(`✅ ${description}`);
        } catch (error) {
            this.failed++;
            console.error(`❌ ${description}: ${error.message}`);
        }
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(message || 'Assertion failed');
        }
    }

    assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(message || `Expected ${expected}, got ${actual}`);
        }
    }

    assertArrayEqual(actual, expected, message) {
        if (JSON.stringify(actual) !== JSON.stringify(expected)) {
            throw new Error(message || `Expected [${expected}], got [${actual}]`);
        }
    }

    run() {
        console.log(`\n🧪 Running ${this.name}`);
        console.log('=' .repeat(50));

        const total = this.passed + this.failed;
        console.log(`\n📊 Results: ${this.passed}/${total} tests passed`);

        if (this.failed > 0) {
            console.log(`⚠️  ${this.failed} tests failed`);
        } else {
            console.log('🎉 All tests passed!');
        }
    }
}

/**
 * Create test graphs for various scenarios
 */
class TestGraphs {
    /**
     * Simple linear graph: A → B → C → D
     */
    static createLinearGraph() {
        const graph = new Graph();
        graph.addNode('A', 0, 0, 'A');
        graph.addNode('B', 1, 0, 'B');
        graph.addNode('C', 2, 0, 'C');
        graph.addNode('D', 3, 0, 'D');

        graph.addEdge('A', 'B', 1);
        graph.addEdge('B', 'C', 2);
        graph.addEdge('C', 'D', 3);

        return graph;
    }

    /**
     * Weighted graph with multiple paths
     *     B(5)
     *   /     \
     * A(1)    D
     *   \     /
     *     C(2)
     */
    static createWeightedGraph() {
        const graph = new Graph();
        graph.addNode('A', 0, 1, 'A');
        graph.addNode('B', 1, 0, 'B');
        graph.addNode('C', 1, 2, 'C');
        graph.addNode('D', 2, 1, 'D');

        graph.addEdge('A', 'B', 5);
        graph.addEdge('A', 'C', 1);
        graph.addEdge('B', 'D', 1);
        graph.addEdge('C', 'D', 2);

        return graph;
    }

    /**
     * Disconnected graph with no path between some nodes
     */
    static createDisconnectedGraph() {
        const graph = new Graph();
        graph.addNode('A', 0, 0, 'A');
        graph.addNode('B', 1, 0, 'B');
        graph.addNode('C', 3, 0, 'C');
        graph.addNode('D', 4, 0, 'D');

        graph.addEdge('A', 'B', 1);
        graph.addEdge('C', 'D', 1);
        // No connection between A-B group and C-D group

        return graph;
    }

    /**
     * Complex graph for comprehensive testing
     */
    static createComplexGraph() {
        const graph = new Graph();

        // Add nodes in a grid-like pattern
        const nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
        const positions = [
            [0, 0], [2, 0], [4, 0], [6, 0],
            [0, 2], [2, 2], [4, 2], [6, 2]
        ];

        for (let i = 0; i < nodes.length; i++) {
            graph.addNode(nodes[i], positions[i][0], positions[i][1], nodes[i]);
        }

        // Add various weighted edges
        graph.addEdge('A', 'B', 4);
        graph.addEdge('A', 'E', 2);
        graph.addEdge('B', 'C', 1);
        graph.addEdge('B', 'F', 5);
        graph.addEdge('C', 'D', 3);
        graph.addEdge('C', 'G', 2);
        graph.addEdge('D', 'H', 1);
        graph.addEdge('E', 'F', 1);
        graph.addEdge('F', 'G', 2);
        graph.addEdge('G', 'H', 3);
        graph.addEdge('E', 'A', 2); // Bidirectional, already added above

        return graph;
    }
}

/**
 * Test Suite for Dijkstra's Algorithm
 */
function testDijkstraAlgorithm() {
    const suite = new TestSuite('Dijkstra\'s Algorithm Tests');

    // Test 1: Simple linear path
    suite.test('Linear graph pathfinding', () => {
        const graph = TestGraphs.createLinearGraph();
        const dijkstra = new DijkstraPathfinder(graph);
        const result = dijkstra.findPath('A', 'D');

        suite.assert(result.found, 'Should find a path');
        suite.assertArrayEqual(result.path, ['A', 'B', 'C', 'D'], 'Should find correct path');
        suite.assertEqual(result.totalDistance, 6, 'Should calculate correct total distance (1+2+3)');
        suite.assert(result.steps.length > 0, 'Should generate steps for visualization');
    });

    // Test 2: Shortest path in weighted graph
    suite.test('Weighted graph optimal path', () => {
        const graph = TestGraphs.createWeightedGraph();
        const dijkstra = new DijkstraPathfinder(graph);
        const result = dijkstra.findPath('A', 'D');

        suite.assert(result.found, 'Should find a path');
        suite.assertArrayEqual(result.path, ['A', 'C', 'D'], 'Should find optimal path A→C→D (cost 3)');
        suite.assertEqual(result.totalDistance, 3, 'Should choose cheaper path over A→B→D (cost 6)');
    });

    // Test 3: No path exists
    suite.test('Disconnected graph handling', () => {
        const graph = TestGraphs.createDisconnectedGraph();
        const dijkstra = new DijkstraPathfinder(graph);
        const result = dijkstra.findPath('A', 'C');

        suite.assert(!result.found, 'Should not find a path in disconnected graph');
        suite.assertArrayEqual(result.path, [], 'Should return empty path');
        suite.assertEqual(result.totalDistance, -1, 'Should return -1 for distance when no path exists');
    });

    // Test 4: Same start and end node
    suite.test('Same start and end node', () => {
        const graph = TestGraphs.createLinearGraph();
        const dijkstra = new DijkstraPathfinder(graph);
        const result = dijkstra.findPath('B', 'B');

        suite.assert(result.found, 'Should find path to self');
        suite.assertArrayEqual(result.path, ['B'], 'Should return single-node path');
        suite.assertEqual(result.totalDistance, 0, 'Should have zero distance to self');
    });

    // Test 5: Complex graph pathfinding
    suite.test('Complex graph pathfinding', () => {
        const graph = TestGraphs.createComplexGraph();
        const dijkstra = new DijkstraPathfinder(graph);
        const result = dijkstra.findPath('A', 'H');

        suite.assert(result.found, 'Should find a path');
        suite.assert(result.path.length > 2, 'Should find a multi-hop path');
        suite.assert(result.totalDistance > 0, 'Should have positive total distance');
        suite.assert(result.nodesExplored > 0, 'Should explore multiple nodes');
    });

    suite.run();
    return suite;
}

/**
 * Test Suite for A* Algorithm
 */
function testAStarAlgorithm() {
    const suite = new TestSuite('A* Algorithm Tests');

    // Test 1: Simple pathfinding
    suite.test('Basic A* pathfinding', () => {
        const graph = TestGraphs.createLinearGraph();
        const astar = new AStarPathfinder(graph);
        const result = astar.findPath('A', 'D');

        suite.assert(result.found, 'Should find a path');
        suite.assertArrayEqual(result.path, ['A', 'B', 'C', 'D'], 'Should find correct path');
        suite.assert(result.steps.length > 0, 'Should generate steps for visualization');
    });

    // Test 2: Optimal path in weighted graph
    suite.test('A* optimal pathfinding', () => {
        const graph = TestGraphs.createWeightedGraph();
        const astar = new AStarPathfinder(graph);
        const result = astar.findPath('A', 'D');

        suite.assert(result.found, 'Should find a path');
        suite.assertArrayEqual(result.path, ['A', 'C', 'D'], 'Should find optimal path');
        suite.assertEqual(result.totalDistance, 3, 'Should find optimal distance');
    });

    // Test 3: Heuristic function accuracy
    suite.test('Heuristic calculation', () => {
        const graph = TestGraphs.createWeightedGraph();
        const astar = new AStarPathfinder(graph);

        const h1 = astar.heuristicDistance('A', 'D');
        const h2 = astar.heuristicDistance('D', 'D');

        suite.assert(h1 > 0, 'Heuristic should be positive for different nodes');
        suite.assertEqual(h2, 0, 'Heuristic should be zero for same node');
    });

    // Test 4: No path handling
    suite.test('A* no path handling', () => {
        const graph = TestGraphs.createDisconnectedGraph();
        const astar = new AStarPathfinder(graph);
        const result = astar.findPath('A', 'C');

        suite.assert(!result.found, 'Should not find path in disconnected graph');
        suite.assertArrayEqual(result.path, [], 'Should return empty path');
    });

    // Test 5: Performance comparison with complex graph
    suite.test('A* efficiency on complex graph', () => {
        const graph = TestGraphs.createComplexGraph();
        const astar = new AStarPathfinder(graph);
        const result = astar.findPath('A', 'H');

        suite.assert(result.found, 'Should find a path');
        suite.assert(result.nodesExplored <= 8, 'Should be reasonably efficient (not explore all nodes)');
    });

    suite.run();
    return suite;
}

/**
 * Test Suite for Algorithm Comparison
 */
function testAlgorithmComparison() {
    const suite = new TestSuite('Algorithm Comparison Tests');

    // Test 1: Compare Dijkstra vs A* results
    suite.test('Dijkstra vs A* result consistency', () => {
        const graph = TestGraphs.createComplexGraph();

        const dijkstra = new DijkstraPathfinder(graph);
        const dijkstraResult = dijkstra.findPath('A', 'H');

        const astar = new AStarPathfinder(graph);
        const astarResult = astar.findPath('A', 'H');

        suite.assertEqual(dijkstraResult.found, astarResult.found, 'Both should find or not find path consistently');

        if (dijkstraResult.found && astarResult.found) {
            suite.assertEqual(
                dijkstraResult.totalDistance.toFixed(2),
                astarResult.totalDistance.toFixed(2),
                'Both should find optimal path with same cost'
            );
        }
    });

    // Test 2: Performance analyzer
    suite.test('Performance analyzer functionality', () => {
        const analyzer = new PathfindingAnalyzer();

        // Add some mock results
        analyzer.addResult('Dijkstra', {
            found: true,
            pathLength: 4,
            totalDistance: 10,
            nodesExplored: 6
        });

        analyzer.addResult('A*', {
            found: true,
            pathLength: 4,
            totalDistance: 10,
            nodesExplored: 4
        });

        const comparison = analyzer.getComparison();

        suite.assert(comparison.algorithms.includes('Dijkstra'), 'Should include Dijkstra');
        suite.assert(comparison.algorithms.includes('A*'), 'Should include A*');
        suite.assertEqual(comparison.metrics.pathFound['Dijkstra'], true, 'Should track path found');
        suite.assertEqual(comparison.metrics.nodesExplored['A*'], 4, 'Should track nodes explored');
    });

    suite.run();
    return suite;
}

/**
 * Run all test suites
 */
function runAllTests() {
    console.log('🚀 Starting Advanced Pathfinding Algorithm Test Suite');
    console.log('='.repeat(60));

    const dijkstraResults = testDijkstraAlgorithm();
    const astarResults = testAStarAlgorithm();
    const comparisonResults = testAlgorithmComparison();

    const totalTests = dijkstraResults.passed + dijkstraResults.failed +
                      astarResults.passed + astarResults.failed +
                      comparisonResults.passed + comparisonResults.failed;

    const totalPassed = dijkstraResults.passed + astarResults.passed + comparisonResults.passed;
    const totalFailed = dijkstraResults.failed + astarResults.failed + comparisonResults.failed;

    console.log('\n' + '='.repeat(60));
    console.log('🏆 FINAL RESULTS');
    console.log('='.repeat(60));
    console.log(`📊 Total Tests: ${totalTests}`);
    console.log(`✅ Passed: ${totalPassed}`);
    console.log(`❌ Failed: ${totalFailed}`);

    if (totalFailed === 0) {
        console.log('\n🎉 ALL TESTS PASSED! Advanced algorithms are working correctly.');
    } else {
        console.log(`\n⚠️  ${totalFailed} tests failed. Please review the implementations.`);
    }

    return {
        total: totalTests,
        passed: totalPassed,
        failed: totalFailed
    };
}

// Auto-run tests if this file is loaded directly
if (typeof window !== 'undefined') {
    // Browser environment - wait for DOM
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(runAllTests, 100); // Small delay to ensure all scripts are loaded
    });
} else if (typeof module !== 'undefined' && require.main === module) {
    // Node.js environment
    runAllTests();
}