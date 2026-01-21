/**
 * Test Suite for Boid Class
 *
 * Tests the core boid behavior including:
 * - Separation (avoid crowding neighbors)
 * - Alignment (steer towards average heading of neighbors)
 * - Cohesion (steer towards average position of neighbors)
 * - Movement and boundary wrapping
 */

// Import dependencies
if (typeof Vector === 'undefined') {
    if (typeof require !== 'undefined') {
        Vector = require('./vector.js');
        Boid = require('./boid.js');
    }
}

const BoidTests = {
    results: [],

    // Helper to assert approximate equality for floating point
    assertApprox(actual, expected, tolerance = 0.01, message = '') {
        const diff = Math.abs(actual - expected);
        if (diff > tolerance) {
            throw new Error(`${message}: expected ${expected}, got ${actual} (diff: ${diff})`);
        }
    },

    // Test: Boid initialization
    testBoidInitialization() {
        const boid = new Boid(100, 200);

        if (boid.position.x !== 100 || boid.position.y !== 200) {
            throw new Error('Boid position not initialized correctly');
        }

        if (boid.velocity.magnitude() === 0) {
            throw new Error('Boid should have initial velocity');
        }

        if (boid.acceleration.x !== 0 || boid.acceleration.y !== 0) {
            throw new Error('Boid acceleration should start at zero');
        }
    },

    // Test: Boid update applies velocity and acceleration
    testBoidUpdate() {
        const boid = new Boid(0, 0);
        boid.velocity = new Vector(10, 0);
        boid.acceleration = new Vector(1, 0);

        boid.update();

        if (boid.velocity.x !== 11) {
            throw new Error('Velocity not updated from acceleration');
        }

        if (boid.position.x !== 11) {
            throw new Error('Position not updated from velocity');
        }

        if (boid.acceleration.x !== 0 || boid.acceleration.y !== 0) {
            throw new Error('Acceleration should reset to zero after update');
        }
    },

    // Test: Boid respects max speed
    testMaxSpeedLimit() {
        const boid = new Boid(0, 0);
        boid.velocity = new Vector(100, 100);

        boid.update();

        const speed = boid.velocity.magnitude();
        if (speed > boid.maxSpeed + 0.01) {
            throw new Error(`Speed ${speed} exceeds maxSpeed ${boid.maxSpeed}`);
        }
    },

    // Test: Separation behavior (avoid crowding)
    testSeparation() {
        const boid = new Boid(50, 50);
        boid.velocity = new Vector(1, 0);

        // Create a nearby boid that's very close
        const neighbor = new Boid(52, 50);
        const flock = [boid, neighbor];

        const separationForce = boid.separate(flock);

        // Separation should push away from the neighbor (negative x direction)
        if (separationForce.x >= 0) {
            throw new Error('Separation should push boid away from neighbor');
        }
    },

    // Test: Separation ignores distant boids
    testSeparationIgnoresDistantBoids() {
        const boid = new Boid(50, 50);
        const distantBoid = new Boid(200, 200);
        const flock = [boid, distantBoid];

        const separationForce = boid.separate(flock);

        // Should be zero vector since neighbor is too far
        this.assertApprox(separationForce.magnitude(), 0, 0.01,
            'Separation should be zero for distant boids');
    },

    // Test: Alignment behavior (match velocity)
    testAlignment() {
        const boid = new Boid(50, 50);
        boid.velocity = new Vector(1, 0);

        // Create neighbors all moving upward
        const neighbor1 = new Boid(55, 50);
        neighbor1.velocity = new Vector(0, 5);
        const neighbor2 = new Boid(45, 50);
        neighbor2.velocity = new Vector(0, 5);

        const flock = [boid, neighbor1, neighbor2];

        const alignmentForce = boid.align(flock);

        // Alignment should steer toward upward movement
        if (alignmentForce.y <= 0) {
            throw new Error('Alignment should steer toward neighbors\' direction');
        }
    },

    // Test: Alignment ignores self
    testAlignmentIgnoresSelf() {
        const boid = new Boid(50, 50);
        boid.velocity = new Vector(1, 0);

        const flock = [boid];

        const alignmentForce = boid.align(flock);

        // Should be zero since no other boids
        this.assertApprox(alignmentForce.magnitude(), 0, 0.01,
            'Alignment should be zero when alone');
    },

    // Test: Cohesion behavior (move toward center)
    testCohesion() {
        const boid = new Boid(50, 50);
        boid.velocity = new Vector(0, 0);

        // Create neighbors to the right
        const neighbor1 = new Boid(60, 50);
        const neighbor2 = new Boid(70, 50);

        const flock = [boid, neighbor1, neighbor2];

        const cohesionForce = boid.cohere(flock);

        // Cohesion should pull toward the right (positive x)
        if (cohesionForce.x <= 0) {
            throw new Error('Cohesion should pull toward neighbors\' center');
        }
    },

    // Test: Cohesion ignores self
    testCohesionIgnoresSelf() {
        const boid = new Boid(50, 50);
        const flock = [boid];

        const cohesionForce = boid.cohere(flock);

        this.assertApprox(cohesionForce.magnitude(), 0, 0.01,
            'Cohesion should be zero when alone');
    },

    // Test: applyForce accumulates acceleration
    testApplyForce() {
        const boid = new Boid(0, 0);
        const force1 = new Vector(1, 0);
        const force2 = new Vector(0, 2);

        boid.applyForce(force1);
        boid.applyForce(force2);

        this.assertApprox(boid.acceleration.x, 1, 0.01, 'X acceleration');
        this.assertApprox(boid.acceleration.y, 2, 0.01, 'Y acceleration');
    },

    // Test: flock method combines all behaviors
    testFlockCombinesBehaviors() {
        const boid = new Boid(50, 50);
        boid.velocity = new Vector(1, 0);

        const neighbor = new Boid(55, 50);
        neighbor.velocity = new Vector(0, 1);

        const flock = [boid, neighbor];

        // Store initial acceleration
        const initialAccel = boid.acceleration.magnitude();

        // Apply flocking
        boid.flock(flock);

        // Acceleration should have been updated
        if (boid.acceleration.magnitude() === initialAccel) {
            throw new Error('Flock should apply forces to acceleration');
        }
    },

    // Test: edges method wraps around boundaries
    testEdgeWrapping() {
        const width = 800;
        const height = 600;

        // Test right edge
        const boid1 = new Boid(width + 10, 300);
        boid1.edges(width, height);
        if (boid1.position.x >= width) {
            throw new Error('Boid should wrap from right edge');
        }

        // Test left edge
        const boid2 = new Boid(-10, 300);
        boid2.edges(width, height);
        if (boid2.position.x <= 0) {
            throw new Error('Boid should wrap from left edge');
        }

        // Test bottom edge
        const boid3 = new Boid(400, height + 10);
        boid3.edges(width, height);
        if (boid3.position.y >= height) {
            throw new Error('Boid should wrap from bottom edge');
        }

        // Test top edge
        const boid4 = new Boid(400, -10);
        boid4.edges(width, height);
        if (boid4.position.y <= 0) {
            throw new Error('Boid should wrap from top edge');
        }
    },

    // Run all tests
    runAll() {
        const tests = [
            'testBoidInitialization',
            'testBoidUpdate',
            'testMaxSpeedLimit',
            'testSeparation',
            'testSeparationIgnoresDistantBoids',
            'testAlignment',
            'testAlignmentIgnoresSelf',
            'testCohesion',
            'testCohesionIgnoresSelf',
            'testApplyForce',
            'testFlockCombinesBehaviors',
            'testEdgeWrapping'
        ];

        this.results = [];
        let passed = 0;
        let failed = 0;

        tests.forEach(testName => {
            try {
                this[testName]();
                this.results.push({ name: testName, passed: true });
                passed++;
            } catch (error) {
                this.results.push({
                    name: testName,
                    passed: false,
                    error: error.message
                });
                failed++;
            }
        });

        return { passed, failed, total: tests.length, results: this.results };
    }
};

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BoidTests;
}
