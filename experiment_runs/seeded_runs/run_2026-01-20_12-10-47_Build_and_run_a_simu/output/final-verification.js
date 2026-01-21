#!/usr/bin/env node

/**
 * Final Verification Script
 *
 * This script performs a comprehensive verification of the boids simulation project
 * to ensure everything is ready for deployment, education, and portfolio use.
 *
 * Run with: node final-verification.js
 *
 * Verification Categories:
 * 1. Core Implementation Files
 * 2. Test Infrastructure
 * 3. Interactive Tools
 * 4. Documentation
 * 5. Production Readiness
 *
 * Exit codes:
 * - 0: All verifications passed
 * - 1: One or more verifications failed
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

// Verification state
let passedChecks = 0;
let failedChecks = 0;
let warnings = 0;

/**
 * Print a section header
 */
function printHeader(title) {
  console.log(`\n${colors.bright}${colors.cyan}${'='.repeat(60)}${colors.reset}`);
  console.log(`${colors.bright}${colors.cyan}${title}${colors.reset}`);
  console.log(`${colors.bright}${colors.cyan}${'='.repeat(60)}${colors.reset}\n`);
}

/**
 * Print a check result
 */
function printCheck(name, passed, details = '') {
  const symbol = passed ? '✓' : '✗';
  const color = passed ? colors.green : colors.red;
  const status = passed ? 'PASS' : 'FAIL';

  console.log(`${color}${symbol} ${name}: ${status}${colors.reset}`);
  if (details) {
    console.log(`  ${details}`);
  }

  if (passed) {
    passedChecks++;
  } else {
    failedChecks++;
  }
}

/**
 * Print a warning
 */
function printWarning(message) {
  console.log(`${colors.yellow}⚠ WARNING: ${message}${colors.reset}`);
  warnings++;
}

/**
 * Check if file exists and optionally verify content
 */
function verifyFile(filepath, checks = {}) {
  const exists = fs.existsSync(filepath);

  if (!exists) {
    return { passed: false, reason: 'File not found' };
  }

  const stats = fs.statSync(filepath);
  const content = fs.readFileSync(filepath, 'utf8');

  // Optional size check
  if (checks.minSize && stats.size < checks.minSize) {
    return {
      passed: false,
      reason: `File too small (${stats.size} bytes < ${checks.minSize} bytes)`
    };
  }

  // Optional content checks
  if (checks.contains) {
    const missing = checks.contains.filter(str => !content.includes(str));
    if (missing.length > 0) {
      return {
        passed: false,
        reason: `Missing content: ${missing.join(', ')}`
      };
    }
  }

  return {
    passed: true,
    size: stats.size,
    lines: content.split('\n').length
  };
}

/**
 * Verify core implementation files
 */
function verifyImplementation() {
  printHeader('1. CORE IMPLEMENTATION FILES');

  const files = [
    {
      path: 'vector.js',
      checks: {
        minSize: 3000,
        contains: ['class Vector', 'add(', 'normalize(', 'distance(']
      },
      description: 'Vector math library'
    },
    {
      path: 'boid.js',
      checks: {
        minSize: 5000,
        contains: ['class Boid', 'separate(', 'align(', 'cohere(']
      },
      description: 'Boid class with flocking behaviors'
    },
    {
      path: 'simulation.js',
      checks: {
        minSize: 3000,
        contains: ['class Simulation', 'update(', 'render(']
      },
      description: 'Simulation manager'
    },
    {
      path: 'index.html',
      checks: {
        minSize: 8000,
        contains: ['<canvas', 'script', 'Boids Flocking Simulation']
      },
      description: 'Main interactive UI'
    }
  ];

  files.forEach(file => {
    const result = verifyFile(file.path, file.checks);
    printCheck(
      file.description,
      result.passed,
      result.passed
        ? `${result.size} bytes, ${result.lines} lines`
        : result.reason
    );
  });
}

/**
 * Verify test infrastructure
 */
function verifyTests() {
  printHeader('2. TEST INFRASTRUCTURE');

  const testFiles = [
    {
      path: 'tests.js',
      description: 'Vector math tests',
      expectedTests: 27
    },
    {
      path: 'boid-tests.js',
      description: 'Boid behavior tests',
      expectedTests: 12
    },
    {
      path: 'simulation-tests.js',
      description: 'Simulation tests',
      expectedTests: 12
    }
  ];

  let totalTests = 0;

  testFiles.forEach(file => {
    const result = verifyFile(file.path, { minSize: 1000 });
    if (result.passed) {
      // Try to count test cases
      const content = fs.readFileSync(file.path, 'utf8');
      const testMatches = content.match(/name:\s*['"][^'"]+['"]/g) || [];
      const foundTests = testMatches.length;
      totalTests += foundTests;

      printCheck(
        file.description,
        result.passed,
        `${foundTests} tests found (expected ~${file.expectedTests})`
      );
    } else {
      printCheck(file.description, false, result.reason);
    }
  });

  console.log(`\n  ${colors.bright}Total tests found: ${totalTests}${colors.reset}`);
  if (totalTests >= 51) {
    console.log(`  ${colors.green}✓ Comprehensive test coverage!${colors.reset}`);
  } else if (totalTests >= 40) {
    printWarning(`Expected ~51 tests, found ${totalTests}`);
  }
}

/**
 * Verify interactive tools
 */
function verifyTools() {
  printHeader('3. INTERACTIVE TOOLS');

  const tools = [
    {
      path: 'index.html',
      description: 'Main simulation UI'
    },
    {
      path: 'workshop.html',
      description: 'Guided workshop (optional)',
      optional: true
    },
    {
      path: 'compare.html',
      description: 'Side-by-side comparison (optional)',
      optional: true
    },
    {
      path: 'data-export.html',
      description: 'Data export tool (optional)',
      optional: true
    }
  ];

  tools.forEach(tool => {
    const result = verifyFile(tool.path, { minSize: 1000 });
    if (tool.optional && !result.passed) {
      console.log(`${colors.yellow}○ ${tool.description}: OPTIONAL (not found)${colors.reset}`);
    } else {
      printCheck(tool.description, result.passed);
    }
  });
}

/**
 * Verify documentation
 */
function verifyDocumentation() {
  printHeader('4. DOCUMENTATION');

  const criticalDocs = [
    'START_HERE.md',
    'README.md',
    'BOID_README.md',
    'SIMULATION_README.md'
  ];

  const optionalDocs = [
    'DEPLOYMENT_GUIDE.md',
    'LAUNCH.md',
    'PROJECT_SUMMARY.md',
    'COLLABORATION_NOTES.md'
  ];

  console.log(`${colors.bright}Critical Documentation:${colors.reset}`);
  criticalDocs.forEach(doc => {
    const result = verifyFile(doc, { minSize: 500 });
    printCheck(doc, result.passed);
  });

  console.log(`\n${colors.bright}Optional Documentation:${colors.reset}`);
  let foundOptional = 0;
  optionalDocs.forEach(doc => {
    const result = verifyFile(doc);
    if (result.passed) {
      console.log(`${colors.green}✓ ${doc}${colors.reset}`);
      foundOptional++;
    } else {
      console.log(`${colors.yellow}○ ${doc} (optional)${colors.reset}`);
    }
  });

  console.log(`\n  Found ${foundOptional}/${optionalDocs.length} optional docs`);
}

/**
 * Verify production readiness
 */
function verifyProductionReadiness() {
  printHeader('5. PRODUCTION READINESS');

  // Check for integration test
  const integrationTest = verifyFile('verify-integration.js', { minSize: 500 });
  printCheck('Integration test exists', integrationTest.passed);

  // Check for performance benchmark
  const benchmark = verifyFile('performance-benchmark.js', { minSize: 500 });
  printCheck('Performance benchmark exists', benchmark.passed);

  // Verify no obvious TODOs in implementation files
  const implFiles = ['vector.js', 'boid.js', 'simulation.js'];
  let todoCount = 0;
  implFiles.forEach(file => {
    if (fs.existsSync(file)) {
      const content = fs.readFileSync(file, 'utf8');
      const todos = (content.match(/TODO|FIXME|XXX/gi) || []).length;
      todoCount += todos;
    }
  });

  printCheck(
    'No unresolved TODOs in core code',
    todoCount === 0,
    todoCount > 0 ? `Found ${todoCount} TODO markers` : 'Clean implementation'
  );

  // Check for deployment guide
  const deployGuide = verifyFile('DEPLOYMENT_GUIDE.md', { minSize: 1000 });
  if (deployGuide.passed) {
    printCheck('Deployment guide exists', true);
  } else {
    printWarning('DEPLOYMENT_GUIDE.md not found (recommended for production)');
  }
}

/**
 * Print final summary
 */
function printSummary() {
  printHeader('VERIFICATION SUMMARY');

  const total = passedChecks + failedChecks;
  const passRate = total > 0 ? Math.round((passedChecks / total) * 100) : 0;

  console.log(`${colors.bright}Total Checks: ${total}${colors.reset}`);
  console.log(`${colors.green}Passed: ${passedChecks}${colors.reset}`);

  if (failedChecks > 0) {
    console.log(`${colors.red}Failed: ${failedChecks}${colors.reset}`);
  }

  if (warnings > 0) {
    console.log(`${colors.yellow}Warnings: ${warnings}${colors.reset}`);
  }

  console.log(`\n${colors.bright}Pass Rate: ${passRate}%${colors.reset}`);

  console.log('\n' + '─'.repeat(60) + '\n');

  if (failedChecks === 0) {
    console.log(`${colors.bright}${colors.green}✓ PROJECT READY TO SHIP! 🚀${colors.reset}`);
    console.log('\nNext steps:');
    console.log('  1. Open index.html in a browser');
    console.log('  2. Deploy to GitHub Pages, Netlify, or Vercel');
    console.log('  3. Share with the world!');
    console.log('\nThe boids are ready to fly! 🐦✨\n');
  } else {
    console.log(`${colors.bright}${colors.red}✗ VERIFICATION FAILED${colors.reset}`);
    console.log(`\n${failedChecks} critical issue(s) found. Please address before shipping.\n`);
  }
}

/**
 * Main execution
 */
function main() {
  console.log(`${colors.bright}${colors.magenta}`);
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║     BOIDS SIMULATION - FINAL VERIFICATION SCRIPT           ║');
  console.log('║     Ensuring Production Readiness                          ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log(colors.reset);

  verifyImplementation();
  verifyTests();
  verifyTools();
  verifyDocumentation();
  verifyProductionReadiness();
  printSummary();

  // Exit with appropriate code
  process.exit(failedChecks > 0 ? 1 : 0);
}

// Run the verification
main();
