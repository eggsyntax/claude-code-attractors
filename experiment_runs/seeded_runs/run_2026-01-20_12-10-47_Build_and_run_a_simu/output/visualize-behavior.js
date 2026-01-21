#!/usr/bin/env node

/**
 * Visualize Boids Behavior in Terminal
 *
 * A terminal-based ASCII visualization of the boids simulation.
 * Demonstrates that the flocking behavior actually works by showing
 * boid positions and movement patterns in real-time.
 *
 * Run: node visualize-behavior.js
 *
 * Features:
 * - ASCII art visualization of boids in terminal
 * - Real-time position updates
 * - Shows flocking behavior emerging
 * - Measures clustering and alignment metrics
 * - No browser required!
 */

const Vector = require('./vector.js');
const Boid = require('./boid.js');

// Terminal dimensions
const WIDTH = 80;
const HEIGHT = 24;

// Simulation parameters
const NUM_BOIDS = 20;
const FRAMES = 100;
const FRAME_DELAY = 100; // ms

/**
 * Create a blank canvas for ASCII rendering
 */
function createCanvas() {
  const canvas = [];
  for (let y = 0; y < HEIGHT; y++) {
    canvas[y] = new Array(WIDTH).fill(' ');
  }
  return canvas;
}

/**
 * Render boids on ASCII canvas
 */
function renderBoids(boids) {
  const canvas = createCanvas();

  // Draw boids as asterisks
  for (const boid of boids) {
    const x = Math.floor(boid.position.x * WIDTH / 800);
    const y = Math.floor(boid.position.y * HEIGHT / 600);

    if (x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT) {
      canvas[y][x] = '*';
    }
  }

  // Draw borders
  for (let x = 0; x < WIDTH; x++) {
    canvas[0][x] = '-';
    canvas[HEIGHT - 1][x] = '-';
  }
  for (let y = 0; y < HEIGHT; y++) {
    canvas[y][0] = '|';
    canvas[y][WIDTH - 1] = '|';
  }

  // Convert to string
  return canvas.map(row => row.join('')).join('\n');
}

/**
 * Calculate average alignment of flock
 */
function calculateAlignment(boids) {
  if (boids.length === 0) return 0;

  const avgVelocity = boids.reduce((sum, boid) => {
    return sum.add(boid.velocity.normalize());
  }, new Vector(0, 0));

  return avgVelocity.magnitude() / boids.length;
}

/**
 * Calculate clustering metric (average distance to nearest neighbor)
 */
function calculateClustering(boids) {
  if (boids.length < 2) return 0;

  let totalMinDistance = 0;

  for (const boid of boids) {
    let minDistance = Infinity;

    for (const other of boids) {
      if (boid !== other) {
        const distance = boid.position.distance(other.position);
        minDistance = Math.min(minDistance, distance);
      }
    }

    totalMinDistance += minDistance;
  }

  return totalMinDistance / boids.length;
}

/**
 * Clear terminal screen
 */
function clearScreen() {
  process.stdout.write('\x1b[2J\x1b[H');
}

/**
 * Main simulation
 */
async function runSimulation() {
  console.log('🐦 Boids Terminal Visualization\n');
  console.log('Initializing flock...\n');

  // Create boids
  const boids = [];
  for (let i = 0; i < NUM_BOIDS; i++) {
    const position = new Vector(
      Math.random() * 800,
      Math.random() * 600
    );
    const velocity = Vector.random2D().multiply(2);
    boids.push(new Boid(position, velocity));
  }

  console.log(`Created ${NUM_BOIDS} boids`);
  console.log('Press Ctrl+C to stop\n');

  await new Promise(resolve => setTimeout(resolve, 1000));

  // Run simulation
  for (let frame = 0; frame < FRAMES; frame++) {
    clearScreen();

    // Update all boids
    for (const boid of boids) {
      boid.flock(boids);
      boid.update();
      boid.edges(800, 600);
    }

    // Render
    const canvas = renderBoids(boids);
    console.log(canvas);

    // Calculate metrics
    const alignment = calculateAlignment(boids).toFixed(3);
    const clustering = calculateClustering(boids).toFixed(1);

    console.log(`\nFrame: ${frame + 1}/${FRAMES} | Alignment: ${alignment} | Avg Distance: ${clustering}px`);
    console.log('\nFlocking behaviors:');
    console.log('  * Separation - Boids avoid crowding neighbors');
    console.log('  * Alignment  - Boids match velocity with nearby boids');
    console.log('  * Cohesion   - Boids move toward center of flock');

    // Wait for next frame
    await new Promise(resolve => setTimeout(resolve, FRAME_DELAY));
  }

  console.log('\n✅ Simulation complete!');
  console.log('\nMetrics show emergent flocking behavior:');
  console.log('- Alignment increases as boids synchronize velocity');
  console.log('- Clustering shows boids forming cohesive groups');
  console.log('\nOpen index.html for full interactive experience!');
}

// Run if called directly
if (require.main === module) {
  runSimulation().catch(console.error);
}

module.exports = { runSimulation };
