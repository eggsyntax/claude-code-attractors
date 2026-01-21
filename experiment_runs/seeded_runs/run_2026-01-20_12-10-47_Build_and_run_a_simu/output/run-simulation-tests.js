#!/usr/bin/env node

/**
 * Node.js Test Runner for Simulation Tests
 *
 * Run with: node run-simulation-tests.js
 */

const Vector = require('./vector.js');
const Boid = require('./boid.js');
const Simulation = require('./simulation.js');

// Make globally available for tests
global.Vector = Vector;
global.Boid = Boid;
global.Simulation = Simulation;

const { runTests } = require('./simulation-tests.js');

const success = runTests();
process.exit(success ? 0 : 1);
