/**
 * Comprehensive Test Suite for K-Means Clustering Implementation
 * Tests algorithm correctness, edge cases, and performance characteristics
 */

// Simple test framework
class TestFramework {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    test(name, testFunction) {
        this.tests.push({ name, testFunction });
    }

    assertEqual(actual, expected, message = '') {
        if (actual !== expected) {
            throw new Error(`Expected ${expected}, but got ${actual}. ${message}`);
        }
    }

    assertApproxEqual(actual, expected, tolerance = 0.001, message = '') {
        if (Math.abs(actual - expected) > tolerance) {
            throw new Error(`Expected ~${expected}, but got ${actual} (tolerance: ${tolerance}). ${message}`);
        }
    }

    assertTrue(condition, message = '') {
        if (!condition) {
            throw new Error(`Expected true, but got ${condition}. ${message}`);
        }
    }

    assertFalse(condition, message = '') {
        if (condition) {
            throw new Error(`Expected false, but got ${condition}. ${message}`);
        }
    }

    assertArrayLength(array, expectedLength, message = '') {
        if (array.length !== expectedLength) {
            throw new Error(`Expected array length ${expectedLength}, but got ${array.length}. ${message}`);
        }
    }

    run() {
        console.log('🧪 Running K-Means Tests...\n');

        for (const test of this.tests) {
            try {
                test.testFunction();
                console.log(`✅ ${test.name}`);
                this.passed++;
            } catch (error) {
                console.log(`❌ ${test.name}: ${error.message}`);
                this.failed++;
            }
        }

        console.log(`\n📊 Test Results: ${this.passed} passed, ${this.failed} failed`);

        if (this.failed === 0) {
            console.log('🎉 All tests passed!');
        } else {
            console.log(`⚠️  ${this.failed} test(s) failed`);
        }

        return this.failed === 0;
    }
}

// Test the K-Means implementation
function runKMeansTests() {
    const test = new TestFramework();

    // Test 1: Basic Initialization
    test.test('Basic KMeansVisualizer Initialization', () => {
        const kmeans = new KMeansVisualizer();
        test.assertEqual(kmeans.points.length, 0, 'Points should be empty initially');
        test.assertEqual(kmeans.centroids.length, 0, 'Centroids should be empty initially');
        test.assertEqual(kmeans.steps.length, 0, 'Steps should be empty initially');
        test.assertEqual(kmeans.currentStep, 0, 'Current step should be 0');
    });

    // Test 2: Random Data Generation
    test.test('Random Data Generation', () => {
        const kmeans = new KMeansVisualizer();
        kmeans.generateRandomData(20, 100, 100);

        test.assertEqual(kmeans.points.length, 20, 'Should generate 20 points');
        test.assertTrue(kmeans.steps.length > 0, 'Should record generation step');

        // Check that points are within bounds
        for (const point of kmeans.points) {
            test.assertTrue(point.x >= 0 && point.x <= 100, 'Point X should be within bounds');
            test.assertTrue(point.y >= 0 && point.y <= 100, 'Point Y should be within bounds');
            test.assertEqual(point.cluster, -1, 'Points should be unassigned initially');
            test.assertTrue(typeof point.id === 'number', 'Point should have numeric ID');
        }
    });

    // Test 3: Clustered Data Generation
    test.test('Clustered Data Generation', () => {
        const kmeans = new KMeansVisualizer();
        kmeans.generateClusteredData(3, 10, 200, 200);

        test.assertEqual(kmeans.points.length, 30, 'Should generate 30 points (3 clusters × 10 points)');

        // All points should be within bounds
        for (const point of kmeans.points) {
            test.assertTrue(point.x >= 0 && point.x <= 200, 'Point X should be within bounds');
            test.assertTrue(point.y >= 0 && point.y <= 200, 'Point Y should be within bounds');
        }
    });

    // Test 4: Distance Calculation
    test.test('Distance Calculation', () => {
        const kmeans = new KMeansVisualizer();

        const point1 = { x: 0, y: 0 };
        const point2 = { x: 3, y: 4 };

        const distance = kmeans.calculateDistance(point1, point2);
        test.assertApproxEqual(distance, 5.0, 0.001, 'Distance should be 5.0 (3-4-5 triangle)');

        // Test distance to self
        const selfDistance = kmeans.calculateDistance(point1, point1);
        test.assertApproxEqual(selfDistance, 0.0, 0.001, 'Distance to self should be 0');
    });

    // Test 5: Centroid Initialization
    test.test('Random Centroid Initialization', () => {
        const kmeans = new KMeansVisualizer();
        kmeans.initializeCentroids(3, 100, 100);

        test.assertEqual(kmeans.centroids.length, 3, 'Should create 3 centroids');

        for (let i = 0; i < kmeans.centroids.length; i++) {
            const centroid = kmeans.centroids[i];
            test.assertEqual(centroid.id, i, 'Centroid should have correct ID');
            test.assertTrue(centroid.x >= 0 && centroid.x <= 100, 'Centroid X should be within bounds');
            test.assertTrue(centroid.y >= 0 && centroid.y <= 100, 'Centroid Y should be within bounds');
            test.assertTrue(typeof centroid.color === 'string', 'Centroid should have color');
        }
    });

    // Test 6: K-means++ Initialization
    test.test('K-means++ Initialization', () => {
        const kmeans = new KMeansVisualizer();

        // Create some well-separated points
        kmeans.points = [
            { x: 10, y: 10, cluster: -1, id: 0 },
            { x: 15, y: 15, cluster: -1, id: 1 },
            { x: 80, y: 80, cluster: -1, id: 2 },
            { x: 85, y: 85, cluster: -1, id: 3 }
        ];

        kmeans.initializeCentroidsKMeansPlusPlus(2);

        test.assertEqual(kmeans.centroids.length, 2, 'Should create 2 centroids');

        // Centroids should be reasonably far apart
        const distance = kmeans.calculateDistance(kmeans.centroids[0], kmeans.centroids[1]);
        test.assertTrue(distance > 20, 'K-means++ should choose well-separated centroids');
    });

    // Test 7: Point Assignment
    test.test('Point Assignment to Clusters', () => {
        const kmeans = new KMeansVisualizer();

        // Create points and centroids in known positions
        kmeans.points = [
            { x: 10, y: 10, cluster: -1, id: 0 },
            { x: 15, y: 15, cluster: -1, id: 1 },
            { x: 80, y: 80, cluster: -1, id: 2 },
            { x: 85, y: 85, cluster: -1, id: 3 }
        ];

        kmeans.centroids = [
            { x: 12, y: 12, id: 0, color: '#FF0000' },
            { x: 82, y: 82, id: 1, color: '#00FF00' }
        ];

        const changes = kmeans.assignPointsToClusters();

        test.assertEqual(changes, 4, 'All 4 points should be assigned');
        test.assertEqual(kmeans.points[0].cluster, 0, 'Point 0 should be in cluster 0');
        test.assertEqual(kmeans.points[1].cluster, 0, 'Point 1 should be in cluster 0');
        test.assertEqual(kmeans.points[2].cluster, 1, 'Point 2 should be in cluster 1');
        test.assertEqual(kmeans.points[3].cluster, 1, 'Point 3 should be in cluster 1');
    });

    // Test 8: Centroid Update
    test.test('Centroid Update', () => {
        const kmeans = new KMeansVisualizer();

        // Create points assigned to clusters
        kmeans.points = [
            { x: 10, y: 10, cluster: 0, id: 0 },
            { x: 20, y: 20, cluster: 0, id: 1 },
            { x: 80, y: 80, cluster: 1, id: 2 },
            { x: 90, y: 90, cluster: 1, id: 3 }
        ];

        kmeans.centroids = [
            { x: 0, y: 0, id: 0, color: '#FF0000' },
            { x: 100, y: 100, id: 1, color: '#00FF00' }
        ];

        const movement = kmeans.updateCentroids();

        // Centroid 0 should move to (15, 15) - mean of (10,10) and (20,20)
        test.assertApproxEqual(kmeans.centroids[0].x, 15, 0.001, 'Centroid 0 X should move to mean');
        test.assertApproxEqual(kmeans.centroids[0].y, 15, 0.001, 'Centroid 0 Y should move to mean');

        // Centroid 1 should move to (85, 85) - mean of (80,80) and (90,90)
        test.assertApproxEqual(kmeans.centroids[1].x, 85, 0.001, 'Centroid 1 X should move to mean');
        test.assertApproxEqual(kmeans.centroids[1].y, 85, 0.001, 'Centroid 1 Y should move to mean');

        test.assertTrue(movement > 0, 'Total movement should be positive');
    });

    // Test 9: WCSS Calculation
    test.test('WCSS Calculation', () => {
        const kmeans = new KMeansVisualizer();

        // Create a simple scenario where WCSS can be calculated manually
        kmeans.points = [
            { x: 1, y: 1, cluster: 0, id: 0 },
            { x: 2, y: 2, cluster: 0, id: 1 }
        ];

        kmeans.centroids = [
            { x: 1.5, y: 1.5, id: 0, color: '#FF0000' }
        ];

        const wcss = kmeans.calculateWCSS();

        // Distance from (1,1) to (1.5,1.5) = sqrt(0.5) ≈ 0.707
        // Distance from (2,2) to (1.5,1.5) = sqrt(0.5) ≈ 0.707
        // WCSS = 0.5 + 0.5 = 1.0
        test.assertApproxEqual(wcss, 1.0, 0.001, 'WCSS should be 1.0');
    });

    // Test 10: Complete Algorithm Run
    test.test('Complete K-Means Algorithm', () => {
        const kmeans = new KMeansVisualizer();

        // Generate some clustered data for a realistic test
        kmeans.generateClusteredData(2, 5, 100, 100);

        const steps = kmeans.runKMeans(2, 'kmeans++');

        test.assertTrue(steps.length > 0, 'Algorithm should produce steps');
        test.assertTrue(kmeans.centroids.length === 2, 'Should have 2 centroids');
        test.assertTrue(kmeans.points.every(p => p.cluster >= 0), 'All points should be assigned');

        // Check that algorithm recorded proper steps
        const hasInitialization = steps.some(s => s.type === 'centroids_kmeans++');
        const hasAssignment = steps.some(s => s.type === 'points_assigned');
        const hasUpdate = steps.some(s => s.type === 'centroids_updated');

        test.assertTrue(hasInitialization, 'Should record initialization step');
        test.assertTrue(hasAssignment, 'Should record assignment step');
        test.assertTrue(hasUpdate, 'Should record update step');
    });

    // Test 11: Step Navigation
    test.test('Step Navigation', () => {
        const kmeans = new KMeansVisualizer();
        kmeans.generateRandomData(10, 50, 50);
        kmeans.runKMeans(2);

        const totalSteps = kmeans.steps.length;
        test.assertTrue(totalSteps > 0, 'Should have steps');

        // Test going to specific step
        const midStep = Math.floor(totalSteps / 2);
        const step = kmeans.goToStep(midStep);
        test.assertTrue(step !== null, 'Should return valid step');
        test.assertEqual(kmeans.currentStep, midStep, 'Current step should be updated');

        // Test next step
        const nextStep = kmeans.nextStep();
        test.assertEqual(kmeans.currentStep, midStep + 1, 'Should advance to next step');

        // Test previous step
        const prevStep = kmeans.previousStep();
        test.assertEqual(kmeans.currentStep, midStep, 'Should go back to previous step');
    });

    // Test 12: Edge Cases
    test.test('Edge Cases', () => {
        const kmeans = new KMeansVisualizer();

        // Test with no points
        kmeans.points = [];
        kmeans.initializeCentroids(2, 100, 100);
        const changes = kmeans.assignPointsToClusters();
        test.assertEqual(changes, 0, 'No changes when no points');

        // Test with more clusters than points
        kmeans.generateRandomData(2, 100, 100);
        const steps = kmeans.runKMeans(5); // More clusters than points
        test.assertTrue(steps.length > 0, 'Should handle more clusters than points');

        // Test with single point
        kmeans.points = [{ x: 50, y: 50, cluster: -1, id: 0 }];
        kmeans.runKMeans(1);
        test.assertEqual(kmeans.points[0].cluster, 0, 'Single point should be assigned to cluster');
    });

    // Test 13: Color Assignment
    test.test('Color Assignment', () => {
        const kmeans = new KMeansVisualizer();

        const color0 = kmeans.getClusterColor(0);
        const color1 = kmeans.getClusterColor(1);
        const color8 = kmeans.getClusterColor(8); // Should wrap around
        const color0Again = kmeans.getClusterColor(0);

        test.assertTrue(typeof color0 === 'string', 'Color should be string');
        test.assertTrue(color0.startsWith('#'), 'Color should be hex format');
        test.assertEqual(color0, color0Again, 'Same cluster ID should return same color');
        test.assertTrue(color0 !== color1, 'Different clusters should have different colors');
        test.assertEqual(color0, color8, 'Color should wrap around after 8 clusters');
    });

    // Test 14: Performance Test
    test.test('Performance with Larger Dataset', () => {
        const kmeans = new KMeansVisualizer();

        const startTime = performance.now();

        // Test with larger dataset
        kmeans.generateRandomData(200, 500, 500);
        kmeans.runKMeans(5);

        const endTime = performance.now();
        const duration = endTime - startTime;

        test.assertTrue(duration < 5000, 'Should complete within 5 seconds');
        test.assertEqual(kmeans.points.length, 200, 'Should handle 200 points');
        test.assertTrue(kmeans.points.every(p => p.cluster >= 0), 'All points should be clustered');
    });

    // Test 15: Convergence Detection
    test.test('Convergence Detection', () => {
        const kmeans = new KMeansVisualizer();

        // Create a scenario that should converge quickly
        kmeans.points = [
            { x: 10, y: 10, cluster: -1, id: 0 },
            { x: 11, y: 11, cluster: -1, id: 1 },
            { x: 90, y: 90, cluster: -1, id: 2 },
            { x: 91, y: 91, cluster: -1, id: 3 }
        ];

        const steps = kmeans.runKMeans(2, 'kmeans++');

        // Should converge in just a few iterations
        const iterationSteps = steps.filter(s => s.type === 'iteration_start');
        test.assertTrue(iterationSteps.length <= 5, 'Should converge quickly with well-separated data');

        // Should have convergence step
        const convergedStep = steps.find(s => s.type === 'converged');
        test.assertTrue(convergedStep !== undefined, 'Should detect convergence');
    });

    return test.run();
}

// Run tests when script loads
if (typeof window !== 'undefined') {
    // Browser environment
    window.addEventListener('load', () => {
        console.log('Running K-Means Tests in Browser...');
        runKMeansTests();
    });
} else if (typeof module !== 'undefined') {
    // Node.js environment
    module.exports = { runKMeansTests, TestFramework };
}

// If running directly in browser console
if (typeof KMeansVisualizer !== 'undefined') {
    runKMeansTests();
}