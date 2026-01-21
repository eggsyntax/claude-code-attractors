/**
 * Test Suite for Simulation
 *
 * Tests the simulation manager that handles the flock lifecycle,
 * animation loop, and parameter updates.
 */

if (typeof Vector === 'undefined' && typeof require !== 'undefined') {
    Vector = require('./vector.js');
    Boid = require('./boid.js');
}

// Simple test framework
const tests = [];
function test(name, fn) {
    tests.push({ name, fn });
}

function assertEquals(actual, expected, message = '') {
    if (actual !== expected) {
        throw new Error(`${message}\nExpected: ${expected}\nActual: ${actual}`);
    }
}

function assertTrue(value, message = '') {
    if (!value) {
        throw new Error(`${message}\nExpected truthy value, got: ${value}`);
    }
}

function assertApprox(actual, expected, tolerance = 0.001, message = '') {
    if (Math.abs(actual - expected) > tolerance) {
        throw new Error(`${message}\nExpected: ${expected} ± ${tolerance}\nActual: ${actual}`);
    }
}

// Mock canvas context for testing
class MockCanvas {
    constructor(width, height) {
        this.width = width;
        this.height = height;
        this.drawCalls = [];
    }

    getContext(type) {
        return {
            clearRect: (...args) => this.drawCalls.push(['clearRect', args]),
            save: () => this.drawCalls.push(['save']),
            restore: () => this.drawCalls.push(['restore']),
            translate: (...args) => this.drawCalls.push(['translate', args]),
            rotate: (...args) => this.drawCalls.push(['rotate', args]),
            beginPath: () => this.drawCalls.push(['beginPath']),
            moveTo: (...args) => this.drawCalls.push(['moveTo', args]),
            lineTo: (...args) => this.drawCalls.push(['lineTo', args]),
            closePath: () => this.drawCalls.push(['closePath']),
            fill: () => this.drawCalls.push(['fill']),
            stroke: () => this.drawCalls.push(['stroke']),
            fillStyle: null,
            strokeStyle: null,
            lineWidth: 1
        };
    }
}

// ============================================================
// TESTS
// ============================================================

test('Simulation initializes with correct default parameters', () => {
    const sim = new Simulation(800, 600);

    assertEquals(sim.width, 800, 'Width should be 800');
    assertEquals(sim.height, 600, 'Height should be 600');
    assertTrue(sim.flock.length > 0, 'Flock should not be empty');
    assertEquals(sim.isRunning, false, 'Simulation should not be running initially');
});

test('Simulation creates boids within canvas bounds', () => {
    const sim = new Simulation(800, 600, 50);

    assertEquals(sim.flock.length, 50, 'Should create 50 boids');

    for (let boid of sim.flock) {
        assertTrue(boid.position.x >= 0 && boid.position.x <= 800,
            'Boid x position should be within bounds');
        assertTrue(boid.position.y >= 0 && boid.position.y <= 600,
            'Boid y position should be within bounds');
    }
});

test('Simulation can add individual boids', () => {
    const sim = new Simulation(800, 600, 0);
    assertEquals(sim.flock.length, 0, 'Flock should be empty');

    sim.addBoid(100, 200);
    assertEquals(sim.flock.length, 1, 'Flock should have one boid');
    assertEquals(sim.flock[0].position.x, 100, 'Boid should be at x=100');
    assertEquals(sim.flock[0].position.y, 200, 'Boid should be at y=200');
});

test('Simulation can clear all boids', () => {
    const sim = new Simulation(800, 600, 20);
    assertEquals(sim.flock.length, 20, 'Should start with 20 boids');

    sim.clear();
    assertEquals(sim.flock.length, 0, 'Flock should be empty after clear');
});

test('Simulation can reset to new flock size', () => {
    const sim = new Simulation(800, 600, 10);
    assertEquals(sim.flock.length, 10, 'Should start with 10 boids');

    sim.reset(30);
    assertEquals(sim.flock.length, 30, 'Should have 30 boids after reset');
});

test('Update advances all boids one step', () => {
    const sim = new Simulation(800, 600, 5);

    // Record initial positions
    const initialPositions = sim.flock.map(b => ({
        x: b.position.x,
        y: b.position.y
    }));

    // Update simulation
    sim.update();

    // At least some boids should have moved (they have random initial velocities)
    let someMovement = false;
    for (let i = 0; i < sim.flock.length; i++) {
        const dx = Math.abs(sim.flock[i].position.x - initialPositions[i].x);
        const dy = Math.abs(sim.flock[i].position.y - initialPositions[i].y);
        if (dx > 0.01 || dy > 0.01) {
            someMovement = true;
            break;
        }
    }
    assertTrue(someMovement, 'At least some boids should have moved');
});

test('Render clears canvas and draws all boids', () => {
    const mockCanvas = new MockCanvas(800, 600);
    const ctx = mockCanvas.getContext('2d');
    const sim = new Simulation(800, 600, 3);

    sim.render(ctx);

    // Should have called clearRect
    const clearCalls = ctx.drawCalls.filter(call => call[0] === 'clearRect');
    assertEquals(clearCalls.length, 1, 'Should clear canvas once');

    // Should have save/restore pairs for each boid
    const saveCalls = ctx.drawCalls.filter(call => call[0] === 'save');
    const restoreCalls = ctx.drawCalls.filter(call => call[0] === 'restore');
    assertEquals(saveCalls.length, 3, 'Should save context for each boid');
    assertEquals(restoreCalls.length, 3, 'Should restore context for each boid');
});

test('Can update boid parameters globally', () => {
    const sim = new Simulation(800, 600, 10);

    sim.setParameter('maxSpeed', 8);
    sim.setParameter('perceptionRadius', 75);

    for (let boid of sim.flock) {
        assertEquals(boid.maxSpeed, 8, 'All boids should have updated maxSpeed');
        assertEquals(boid.perceptionRadius, 75, 'All boids should have updated perceptionRadius');
    }
});

test('Can update behavior weights', () => {
    const sim = new Simulation(800, 600, 5);

    sim.setBehaviorWeights(2.0, 1.5, 0.8);

    assertEquals(sim.separationWeight, 2.0, 'Separation weight should be 2.0');
    assertEquals(sim.alignmentWeight, 1.5, 'Alignment weight should be 1.5');
    assertEquals(sim.cohesionWeight, 0.8, 'Cohesion weight should be 0.8');
});

test('Behavior weights are applied during update', () => {
    const sim = new Simulation(800, 600, 3);

    // Create a controlled scenario with specific positions
    sim.clear();
    sim.addBoid(400, 300);
    sim.addBoid(410, 300);
    sim.addBoid(405, 310);

    // Set weights to verify they're applied
    sim.setBehaviorWeights(2.0, 1.0, 1.0);

    // Record initial state
    const initialVelocity = sim.flock[0].velocity.copy();

    // Update once
    sim.update();

    // Velocity should have changed (forces were applied)
    const velocityChanged = !sim.flock[0].velocity.subtract(initialVelocity).magnitude() < 0.001;
    assertTrue(velocityChanged, 'Boid velocity should change after update with nearby neighbors');
});

test('Start and stop control animation loop state', () => {
    const sim = new Simulation(800, 600, 10);

    assertEquals(sim.isRunning, false, 'Should not be running initially');

    sim.start();
    assertEquals(sim.isRunning, true, 'Should be running after start');

    sim.stop();
    assertEquals(sim.isRunning, false, 'Should not be running after stop');
});

// ============================================================
// TEST RUNNER
// ============================================================

function runTests() {
    let passed = 0;
    let failed = 0;

    console.log('\n' + '='.repeat(60));
    console.log('Running Simulation Tests');
    console.log('='.repeat(60) + '\n');

    for (let { name, fn } of tests) {
        try {
            fn();
            console.log('✓ ' + name);
            passed++;
        } catch (error) {
            console.log('✗ ' + name);
            console.log('  ' + error.message);
            failed++;
        }
    }

    console.log('\n' + '='.repeat(60));
    console.log(`Results: ${passed} passed, ${failed} failed`);
    console.log('='.repeat(60) + '\n');

    return failed === 0;
}

// Export for browser and Node.js
if (typeof window !== 'undefined') {
    window.runSimulationTests = runTests;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runTests, tests };
}
