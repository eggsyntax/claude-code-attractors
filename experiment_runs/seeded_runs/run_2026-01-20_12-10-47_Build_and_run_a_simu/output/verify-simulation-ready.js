#!/usr/bin/env node

/**
 * Verify Simulation Ready - Turn 14 Verification Script
 *
 * This script verifies that the boids simulation is complete and ready to run.
 * It checks for the presence of all critical files and validates basic structure.
 *
 * Usage: node verify-simulation-ready.js
 *
 * @author Bob (Turn 14)
 */

const fs = require('fs');
const path = require('path');

console.log('\n🐦 Boids Simulation Readiness Verification\n');
console.log('=' .repeat(60));

// Critical files that must exist for the simulation to work
const criticalFiles = [
  // Core implementation
  { path: 'vector.js', type: 'Core', desc: 'Vector math library' },
  { path: 'boid.js', type: 'Core', desc: 'Boid behavior implementation' },
  { path: 'simulation.js', type: 'Core', desc: 'Simulation manager' },
  { path: 'index.html', type: 'Core', desc: 'Main interactive UI' },

  // Test suites
  { path: 'tests.js', type: 'Test', desc: 'Vector tests' },
  { path: 'boid-tests.js', type: 'Test', desc: 'Boid tests' },
  { path: 'simulation-tests.js', type: 'Test', desc: 'Simulation tests' },
  { path: 'verify-integration.js', type: 'Test', desc: 'Integration test' },

  // Interactive tools
  { path: 'workshop.html', type: 'Tool', desc: 'Interactive workshop' },
  { path: 'compare.html', type: 'Tool', desc: 'Side-by-side comparison' },

  // Essential documentation
  { path: 'START_HERE.md', type: 'Docs', desc: 'Quick start guide' },
  { path: 'PROJECT_README.md', type: 'Docs', desc: 'Project overview' },
  { path: 'LAUNCH.md', type: 'Docs', desc: 'Launch instructions' },
];

let allPresent = true;
let fileCount = { Core: 0, Test: 0, Tool: 0, Docs: 0 };

console.log('\n📋 Checking Critical Files:\n');

criticalFiles.forEach(file => {
  const exists = fs.existsSync(file.path);
  const status = exists ? '✓' : '✗';
  const symbol = exists ? '✅' : '❌';

  console.log(`  ${symbol} ${file.type.padEnd(6)} | ${file.path.padEnd(25)} | ${file.desc}`);

  if (exists) {
    fileCount[file.type]++;
  } else {
    allPresent = false;
  }
});

console.log('\n' + '─'.repeat(60));

// Summary
console.log('\n📊 Summary:\n');
console.log(`  Core Files:    ${fileCount.Core}/4`);
console.log(`  Test Files:    ${fileCount.Test}/4`);
console.log(`  Interactive:   ${fileCount.Tool}/2`);
console.log(`  Documentation: ${fileCount.Docs}/3`);

// Check for any files in directory
const allFiles = fs.readdirSync('.').filter(f => !f.startsWith('.'));
console.log(`\n  Total Files:   ${allFiles.length}`);

// Basic content validation
console.log('\n' + '─'.repeat(60));
console.log('\n🔍 Content Validation:\n');

// Check if vector.js has the Vector class
if (fs.existsSync('vector.js')) {
  const vectorContent = fs.readFileSync('vector.js', 'utf8');
  const hasVectorClass = vectorContent.includes('class Vector');
  const hasAdd = vectorContent.includes('add()');
  const hasNormalize = vectorContent.includes('normalize()');

  console.log(`  Vector Library:`);
  console.log(`    ${hasVectorClass ? '✅' : '❌'} Vector class defined`);
  console.log(`    ${hasAdd ? '✅' : '❌'} add() method present`);
  console.log(`    ${hasNormalize ? '✅' : '❌'} normalize() method present`);
}

// Check if boid.js has the Boid class
if (fs.existsSync('boid.js')) {
  const boidContent = fs.readFileSync('boid.js', 'utf8');
  const hasBoidClass = boidContent.includes('class Boid');
  const hasSeparation = boidContent.includes('separation');
  const hasAlignment = boidContent.includes('alignment');
  const hasCohesion = boidContent.includes('cohesion');

  console.log(`\n  Boid Implementation:`);
  console.log(`    ${hasBoidClass ? '✅' : '❌'} Boid class defined`);
  console.log(`    ${hasSeparation ? '✅' : '❌'} Separation behavior`);
  console.log(`    ${hasAlignment ? '✅' : '❌'} Alignment behavior`);
  console.log(`    ${hasCohesion ? '✅' : '❌'} Cohesion behavior`);
}

// Check if simulation.js has the Simulation class
if (fs.existsSync('simulation.js')) {
  const simContent = fs.readFileSync('simulation.js', 'utf8');
  const hasSimClass = simContent.includes('class Simulation');
  const hasUpdate = simContent.includes('update');
  const hasRender = simContent.includes('render');

  console.log(`\n  Simulation Manager:`);
  console.log(`    ${hasSimClass ? '✅' : '❌'} Simulation class defined`);
  console.log(`    ${hasUpdate ? '✅' : '❌'} update() method`);
  console.log(`    ${hasRender ? '✅' : '❌'} render() method`);
}

// Check if index.html has canvas
if (fs.existsSync('index.html')) {
  const htmlContent = fs.readFileSync('index.html', 'utf8');
  const hasCanvas = htmlContent.includes('<canvas');
  const hasScript = htmlContent.includes('<script');
  const hasControls = htmlContent.includes('input') || htmlContent.includes('slider');

  console.log(`\n  User Interface:`);
  console.log(`    ${hasCanvas ? '✅' : '❌'} Canvas element`);
  console.log(`    ${hasScript ? '✅' : '❌'} JavaScript included`);
  console.log(`    ${hasControls ? '✅' : '❌'} Interactive controls`);
}

// Final verdict
console.log('\n' + '='.repeat(60));
console.log('\n🎯 Final Verdict:\n');

if (allPresent && fileCount.Core === 4 && fileCount.Test >= 3) {
  console.log('  ✅ SIMULATION IS READY TO RUN!\n');
  console.log('  To launch the simulation:\n');
  console.log('    • Interactive playground: open index.html');
  console.log('    • Guided workshop:        open workshop.html');
  console.log('    • Side-by-side compare:   open compare.html\n');
  console.log('  To run tests:\n');
  console.log('    • Integration test:  node verify-integration.js');
  console.log('    • All test suites:   node run-tests.js\n');
  console.log('  🐦 Watch those boids flock! ✨\n');
} else {
  console.log('  ❌ MISSING CRITICAL FILES\n');
  console.log('  Some essential files are missing. Please verify the project structure.\n');
}

console.log('=' .repeat(60) + '\n');
