# How to Launch the Boids Simulation

## Quick Start

### Option 1: Direct File Open
Simply open `index.html` in your web browser:
```bash
open index.html
```

### Option 2: Local Server (Recommended)
For best results, serve via HTTP:

**Python 3:**
```bash
python3 -m http.server 8000
# Then visit: http://localhost:8000
```

**Python 2:**
```bash
python -m SimpleHTTPServer 8000
# Then visit: http://localhost:8000
```

**Node.js (if you have npx):**
```bash
npx http-server -p 8000
# Then visit: http://localhost:8000
```

## What You'll See

- 100 blue triangular boids flocking together
- Real-time parameter controls
- FPS counter
- Click anywhere on the canvas to add more boids
- Pause/resume button

## Fun Things to Try

1. **Tight Swarms**
   - Separation: 2.0
   - Cohesion: 0.5
   - Perception Radius: 30

2. **Flowing Schools**
   - Separation: 0.5
   - Cohesion: 2.0
   - Perception Radius: 100

3. **Chaotic Scatter**
   - Alignment: 0.1
   - Max Speed: 8
   - Max Force: 0.8

4. **Slow Ballet**
   - Max Speed: 2
   - All weights: 1.0
   - Large perception radius

## Testing

Run all test suites:
```bash
# Vector math tests
node run-tests.js

# Boid behavior tests
node run-boid-tests.js

# Simulation tests
node run-simulation-tests.js

# Integration verification
node verify-integration.js
```

Or open the browser-based test runners:
- `test-runner.html` - Vector tests
- `boid-test-runner.html` - Boid tests
- `simulation-test-runner.html` - Simulation tests

## Project Structure

```
.
├── index.html                    # Main application
├── vector.js                     # 2D vector math
├── boid.js                       # Boid flocking behaviors
├── simulation.js                 # Simulation management
├── tests.js                      # Vector tests
├── boid-tests.js                 # Boid tests
├── simulation-tests.js           # Simulation tests
├── verify-integration.js         # Integration check
└── README.md, BOID_README.md, SIMULATION_README.md
```

## Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- No dependencies or build steps required!
- Pure vanilla JavaScript

Enjoy watching the emergent flocking behavior!
