#!/usr/bin/env node

const fs = require('fs');

// Load the K-means implementation
const kmeansCode = fs.readFileSync('kmeans.js', 'utf8');
const testCode = fs.readFileSync('kmeans-tests.js', 'utf8');

// Execute the K-means code
eval(kmeansCode.replace('if (typeof module !== \'undefined\' && module.exports) {', 'if (true) {'));

// Execute the test code
eval(testCode);

// Run the tests
runKMeansTests();