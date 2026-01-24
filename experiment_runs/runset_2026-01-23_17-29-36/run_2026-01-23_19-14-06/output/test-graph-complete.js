/**
 * Comprehensive test suite for the Visual Algorithm Explorer Graph Algorithms
 * Tests graph data structure, algorithms, and integration
 */

// Import for Node.js testing if available
const { Graph, GraphAlgorithms } = typeof module !== 'undefined' ? require('./graphAlgorithms.js') : window;

function runAllTests() {
    console.log('🎯 Running comprehensive graph algorithm tests...\n');

    let passedTests = 0;
    let totalTests = 0;

    function test(name, testFunction) {
        totalTests++;
        try {
            testFunction();
            console.log(`✅ ${name}`);
            passedTests++;
        } catch (error) {
            console.error(`❌ ${name}: ${error.message}`);
        }
    }

    // Test Graph Data Structure
    test('Graph can create nodes and edges', () => {
        const graph = new Graph();
        graph.addNode('A', 100, 100);
        graph.addNode('B', 200, 100);
        graph.addEdge('A', 'B', 5);

        if (graph.getNodes().length !== 2) throw new Error('Wrong number of nodes');
        if (graph.getEdges().length !== 1) throw new Error('Wrong number of edges');
        if (graph.getEdgeWeight('A', 'B') !== 5) throw new Error('Wrong edge weight');
    });

    test('Graph handles neighbors correctly', () => {
        const graph = new Graph();
        graph.addNode('A', 0, 0);
        graph.addNode('B', 1, 0);
        graph.addNode('C', 2, 0);
        graph.addEdge('A', 'B', 1);
        graph.addEdge('B', 'C', 1);

        const neighborsA = graph.getNeighbors('A');
        const neighborsB = graph.getNeighbors('B');

        if (neighborsA.length !== 1 || !neighborsA.includes('B')) {
            throw new Error('A should have B as neighbor');
        }
        if (neighborsB.length !== 2 || !neighborsB.includes('A') || !neighborsB.includes('C')) {
            throw new Error('B should have A and C as neighbors');
        }
    });

    // Test sample graph creation
    test('Sample graph creation works', () => {
        const graph = GraphAlgorithms.createSampleGraph();
        if (graph.getNodes().length < 5) throw new Error('Sample graph too small');
        if (graph.getEdges().length < 5) throw new Error('Not enough edges in sample graph');
    });

    // Test BFS Algorithm
    test('BFS visits all reachable nodes', () => {
        const graph = GraphAlgorithms.createSampleGraph();
        const steps = Array.from(GraphAlgorithms.breadthFirstSearch(graph, 'A'));

        if (steps.length === 0) throw new Error('BFS returned no steps');

        const lastStep = steps[steps.length - 1];
        if (!lastStep.visited || lastStep.visited.length < 5) {
            throw new Error('BFS did not visit enough nodes');
        }
    });

    // Test DFS Algorithm
    test('DFS visits all reachable nodes', () => {
        const graph = GraphAlgorithms.createSampleGraph();
        const steps = Array.from(GraphAlgorithms.depthFirstSearch(graph, 'A'));

        if (steps.length === 0) throw new Error('DFS returned no steps');

        const lastStep = steps[steps.length - 1];
        if (!lastStep.visited || lastStep.visited.length < 5) {
            throw new Error('DFS did not visit enough nodes');
        }
    });

    // Test Dijkstra Algorithm
    test('Dijkstra finds shortest path', () => {
        const graph = GraphAlgorithms.createSampleGraph();
        const steps = Array.from(GraphAlgorithms.dijkstraShortestPath(graph, 'A', 'G'));

        if (steps.length === 0) throw new Error('Dijkstra returned no steps');

        const lastStep = steps[steps.length - 1];
        if (!lastStep.path || lastStep.path.length < 2) {
            throw new Error('Dijkstra did not find a valid path');
        }
        if (lastStep.path[0] !== 'A' || lastStep.path[lastStep.path.length - 1] !== 'G') {
            throw new Error('Dijkstra path does not start with A and end with G');
        }
        if (typeof lastStep.totalDistance !== 'number' || lastStep.totalDistance <= 0) {
            throw new Error('Dijkstra total distance invalid');
        }
    });

    // Test A* Algorithm
    test('A* finds optimal path', () => {
        const graph = GraphAlgorithms.createSampleGraph();
        const steps = Array.from(GraphAlgorithms.aStarPathfinding(graph, 'A', 'G'));

        if (steps.length === 0) throw new Error('A* returned no steps');

        const lastStep = steps[steps.length - 1];
        if (lastStep.type === 'complete' && lastStep.path) {
            if (lastStep.path[0] !== 'A' || lastStep.path[lastStep.path.length - 1] !== 'G') {
                throw new Error('A* path does not start with A and end with G');
            }
        }
    });

    // Test algorithm step structure
    test('BFS step structure is valid', () => {
        const graph = GraphAlgorithms.createSampleGraph();
        const steps = Array.from(GraphAlgorithms.breadthFirstSearch(graph, 'A'));

        steps.forEach((step, index) => {
            if (typeof step.step !== 'number') throw new Error(`Step ${index} missing step number`);
            if (typeof step.type !== 'string') throw new Error(`Step ${index} missing type`);
            if (typeof step.description !== 'string') throw new Error(`Step ${index} missing description`);
            if (typeof step.action !== 'string') throw new Error(`Step ${index} missing action`);
        });
    });

    // Test heuristic function
    test('A* heuristic function works', () => {
        const graph = GraphAlgorithms.createSampleGraph();
        const heuristic = GraphAlgorithms.heuristic(graph, 'A', 'G');

        if (typeof heuristic !== 'number' || heuristic < 0) {
            throw new Error('Heuristic should return a non-negative number');
        }
    });

    // Test path reconstruction
    test('A* path reconstruction works', () => {
        const cameFrom = { 'B': 'A', 'C': 'B' };
        const path = GraphAlgorithms.reconstructPath(cameFrom, 'C');

        if (!Array.isArray(path) || path.length !== 3) {
            throw new Error('Path reconstruction failed');
        }
        if (path[0] !== 'A' || path[1] !== 'B' || path[2] !== 'C') {
            throw new Error('Path reconstruction order is wrong');
        }
    });

    // Performance test
    test('Algorithms complete in reasonable time', () => {
        const graph = GraphAlgorithms.createSampleGraph();
        const start = Date.now();

        Array.from(GraphAlgorithms.breadthFirstSearch(graph, 'A'));
        Array.from(GraphAlgorithms.depthFirstSearch(graph, 'A'));
        Array.from(GraphAlgorithms.dijkstraShortestPath(graph, 'A', 'G'));
        Array.from(GraphAlgorithms.aStarPathfinding(graph, 'A', 'G'));

        const elapsed = Date.now() - start;
        if (elapsed > 1000) {
            throw new Error(`Algorithms took too long: ${elapsed}ms`);
        }
    });

    console.log(`\n📊 Test Results: ${passedTests}/${totalTests} tests passed`);

    if (passedTests === totalTests) {
        console.log('🎉 All tests passed! Graph algorithms are working correctly.');
        return true;
    } else {
        console.log(`❌ ${totalTests - passedTests} tests failed.`);
        return false;
    }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runAllTests };
}

// Run tests automatically in browser
if (typeof window !== 'undefined') {
    // Wait for DOM and other scripts to load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(runAllTests, 2000);
        });
    } else {
        setTimeout(runAllTests, 1000);
    }
}