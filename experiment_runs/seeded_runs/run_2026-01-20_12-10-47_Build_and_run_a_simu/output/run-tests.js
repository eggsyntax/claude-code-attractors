#!/usr/bin/env node

const Vector = require('./vector.js');
global.Vector = Vector;
const runner = require('./tests.js');
const success = runner.run();
process.exit(success ? 0 : 1);
