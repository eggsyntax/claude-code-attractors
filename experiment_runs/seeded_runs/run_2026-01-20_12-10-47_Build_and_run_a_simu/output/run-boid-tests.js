#!/usr/bin/env node

/**
 * Node.js test runner for Boid tests
 * Run with: node run-boid-tests.js
 */

const Vector = require('./vector.js');
const Boid = require('./boid.js');
const BoidTests = require('./boid-tests.js');

console.log('Running Boid Tests...\n');

const result = BoidTests.runAll();

// Display results
result.results.forEach(test => {
    const status = test.passed ? '✓' : '✗';
    const color = test.passed ? '\x1b[32m' : '\x1b[31m';
    const reset = '\x1b[0m';

    console.log(`${color}${status}${reset} ${test.name}`);

    if (!test.passed) {
        console.log(`  ${test.error}`);
    }
});

console.log(`\n${result.passed} passed, ${result.failed} failed, ${result.total} total`);

process.exit(result.failed > 0 ? 1 : 0);
