/**
 * Test suite for Graph Algorithms
 * Run this in the browser console to verify everything works correctly
 */

function testGraphAlgorithms() {
    console.log('🧪 Testing Graph Algorithms...\n');

    // Create sample graph
    const graph = GraphAlgorithms.createSampleGraph();
    console.log('✅ Graph created with nodes:', graph.getNodes());
    console.log('✅ Graph created with edges:', graph.getEdges().length, 'edges');

    // Test BFS
    console.log('\n🔍 Testing BFS from A:');
    const bfsSteps = Array.from(GraphAlgorithms.breadthFirstSearch(graph, 'A'));
    console.log(`BFS completed with ${bfsSteps.length} steps`);
    console.log('Final visited nodes:', bfsSteps[bfsSteps.length - 1]?.visited || []);

    // Test DFS
    console.log('\n🔍 Testing DFS from A:');
    const dfsSteps = Array.from(GraphAlgorithms.depthFirstSearch(graph, 'A'));
    console.log(`DFS completed with ${dfsSteps.length} steps`);
    console.log('Final visited nodes:', dfsSteps[dfsSteps.length - 1]?.visited || []);

    // Test Dijkstra
    console.log('\n🔍 Testing Dijkstra from A to G:');
    const dijkstraSteps = Array.from(GraphAlgorithms.dijkstraShortestPath(graph, 'A', 'G'));
    console.log(`Dijkstra completed with ${dijkstraSteps.length} steps`);
    const lastDijkstraStep = dijkstraSteps[dijkstraSteps.length - 1];
    if (lastDijkstraStep?.path) {
        console.log('Shortest path:', lastDijkstraStep.path.join(' → '));
        console.log('Total distance:', lastDijkstraStep.totalDistance);
    }

    // Test A*
    console.log('\n🔍 Testing A* from A to G:');
    const astarSteps = Array.from(GraphAlgorithms.aStarPathfinding(graph, 'A', 'G'));
    console.log(`A* completed with ${astarSteps.length} steps`);
    const lastAstarStep = astarSteps[astarSteps.length - 1];
    if (lastAstarStep?.path) {
        console.log('Optimal path:', lastAstarStep.path.join(' → '));
        console.log('Total cost:', lastAstarStep.totalCost);
    }

    console.log('\n✅ All graph algorithm tests completed!');
    console.log('\n💡 Try switching to Graph Algorithms in the UI and running the algorithms visually!');
}

// Run tests if this file is loaded
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        // Wait a moment for other scripts to load
        setTimeout(testGraphAlgorithms, 1000);
    });
}