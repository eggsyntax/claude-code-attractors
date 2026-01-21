/**
 * Test Suite for Boids Simulation
 *
 * Simple test runner for vector math and boid behavior logic.
 * Run this in a browser console or Node.js environment.
 */

// Simple test framework
class TestRunner {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    test(name, fn) {
        this.tests.push({ name, fn });
    }

    assertEqual(actual, expected, message = '') {
        const match = JSON.stringify(actual) === JSON.stringify(expected);
        if (!match) {
            throw new Error(`${message}\nExpected: ${JSON.stringify(expected)}\nActual: ${JSON.stringify(actual)}`);
        }
    }

    assertAlmostEqual(actual, expected, tolerance = 0.0001, message = '') {
        const diff = Math.abs(actual - expected);
        if (diff > tolerance) {
            throw new Error(`${message}\nExpected: ${expected} (±${tolerance})\nActual: ${actual}\nDiff: ${diff}`);
        }
    }

    assertTrue(condition, message = '') {
        if (!condition) {
            throw new Error(message || 'Assertion failed: expected true');
        }
    }

    run() {
        console.log('Running tests...\n');

        for (const test of this.tests) {
            try {
                test.fn();
                this.passed++;
                console.log(`✓ ${test.name}`);
            } catch (error) {
                this.failed++;
                console.error(`✗ ${test.name}`);
                console.error(`  ${error.message}\n`);
            }
        }

        console.log(`\n${this.passed + this.failed} tests, ${this.passed} passed, ${this.failed} failed`);
        return this.failed === 0;
    }
}

// Create test runner instance
const runner = new TestRunner();

// ===== Vector Math Tests =====

runner.test('Vector creation with x and y', () => {
    const v = new Vector(3, 4);
    runner.assertEqual(v.x, 3);
    runner.assertEqual(v.y, 4);
});

runner.test('Vector addition', () => {
    const v1 = new Vector(1, 2);
    const v2 = new Vector(3, 4);
    const result = v1.add(v2);
    runner.assertEqual(result.x, 4);
    runner.assertEqual(result.y, 6);
});

runner.test('Vector subtraction', () => {
    const v1 = new Vector(5, 7);
    const v2 = new Vector(2, 3);
    const result = v1.subtract(v2);
    runner.assertEqual(result.x, 3);
    runner.assertEqual(result.y, 4);
});

runner.test('Vector multiplication by scalar', () => {
    const v = new Vector(2, 3);
    const result = v.multiply(2.5);
    runner.assertEqual(result.x, 5);
    runner.assertEqual(result.y, 7.5);
});

runner.test('Vector division by scalar', () => {
    const v = new Vector(10, 20);
    const result = v.divide(2);
    runner.assertEqual(result.x, 5);
    runner.assertEqual(result.y, 10);
});

runner.test('Vector magnitude calculation', () => {
    const v = new Vector(3, 4);
    runner.assertAlmostEqual(v.magnitude(), 5);
});

runner.test('Vector magnitude of zero vector', () => {
    const v = new Vector(0, 0);
    runner.assertEqual(v.magnitude(), 0);
});

runner.test('Vector normalization', () => {
    const v = new Vector(3, 4);
    const normalized = v.normalize();
    runner.assertAlmostEqual(normalized.x, 0.6);
    runner.assertAlmostEqual(normalized.y, 0.8);
    runner.assertAlmostEqual(normalized.magnitude(), 1.0);
});

runner.test('Vector normalization of zero vector', () => {
    const v = new Vector(0, 0);
    const normalized = v.normalize();
    runner.assertEqual(normalized.x, 0);
    runner.assertEqual(normalized.y, 0);
});

runner.test('Vector limit when below max', () => {
    const v = new Vector(3, 4);
    const limited = v.limit(10);
    runner.assertEqual(limited.x, 3);
    runner.assertEqual(limited.y, 4);
});

runner.test('Vector limit when above max', () => {
    const v = new Vector(3, 4);
    const limited = v.limit(2);
    runner.assertAlmostEqual(limited.magnitude(), 2.0);
    // Direction should be preserved
    const original = v.normalize();
    const limitedNorm = limited.normalize();
    runner.assertAlmostEqual(original.x, limitedNorm.x);
    runner.assertAlmostEqual(original.y, limitedNorm.y);
});

runner.test('Distance between two vectors', () => {
    const v1 = new Vector(0, 0);
    const v2 = new Vector(3, 4);
    runner.assertAlmostEqual(v1.distance(v2), 5);
});

runner.test('Distance is symmetric', () => {
    const v1 = new Vector(1, 2);
    const v2 = new Vector(4, 6);
    runner.assertAlmostEqual(v1.distance(v2), v2.distance(v1));
});

runner.test('Dot product calculation', () => {
    const v1 = new Vector(2, 3);
    const v2 = new Vector(4, 5);
    // 2*4 + 3*5 = 8 + 15 = 23
    runner.assertEqual(v1.dot(v2), 23);
});

runner.test('Dot product of perpendicular vectors', () => {
    const v1 = new Vector(1, 0);
    const v2 = new Vector(0, 1);
    runner.assertAlmostEqual(v1.dot(v2), 0);
});

runner.test('Vector heading angle', () => {
    const v1 = new Vector(1, 0);
    runner.assertAlmostEqual(v1.heading(), 0);

    const v2 = new Vector(0, 1);
    runner.assertAlmostEqual(v2.heading(), Math.PI / 2);

    const v3 = new Vector(-1, 0);
    runner.assertAlmostEqual(v3.heading(), Math.PI);
});

runner.test('Vector from angle', () => {
    const v1 = Vector.fromAngle(0);
    runner.assertAlmostEqual(v1.x, 1);
    runner.assertAlmostEqual(v1.y, 0);

    const v2 = Vector.fromAngle(Math.PI / 2);
    runner.assertAlmostEqual(v2.x, 0, 0.0001);
    runner.assertAlmostEqual(v2.y, 1);
});

runner.test('Vector copy creates independent instance', () => {
    const v1 = new Vector(3, 4);
    const v2 = v1.copy();
    runner.assertEqual(v2.x, 3);
    runner.assertEqual(v2.y, 4);

    // Modify v2 and ensure v1 is unchanged
    v2.x = 10;
    runner.assertEqual(v1.x, 3);
    runner.assertEqual(v2.x, 10);
});

runner.test('Vector setMagnitude', () => {
    const v = new Vector(3, 4);
    const result = v.setMagnitude(10);
    runner.assertAlmostEqual(result.magnitude(), 10);
    // Direction should be preserved
    runner.assertAlmostEqual(result.x / v.x, result.y / v.y);
});

// Run all tests
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = runner;
} else {
    // Browser environment - run tests immediately if Vector is defined
    if (typeof Vector !== 'undefined') {
        runner.run();
    } else {
        console.log('Vector class not found. Load vector.js first.');
    }
}
