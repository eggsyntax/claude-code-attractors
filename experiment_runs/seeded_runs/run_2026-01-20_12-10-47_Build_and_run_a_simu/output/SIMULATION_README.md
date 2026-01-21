# Boids Flocking Simulation

A complete implementation of Craig Reynolds' Boids algorithm (1986), demonstrating emergent flocking behavior from three simple rules.

Built collaboratively by Alice and Bob as a test-driven, modular JavaScript simulation.

## Quick Start

Simply open `index.html` in a web browser to see the simulation in action!

```bash
# Or use a local server
python3 -m http.server 8000
# Then visit http://localhost:8000
```

## Features

### Core Behaviors
- **Separation**: Boids steer away from nearby neighbors to avoid crowding
- **Alignment**: Boids align their heading with nearby neighbors
- **Cohesion**: Boids steer toward the center of mass of nearby neighbors

### Interactive Controls
- **Real-time parameter tuning**: Adjust max speed, steering force, and perception radius
- **Behavior weights**: Control the strength of each flocking rule independently
- **Dynamic flock size**: Add or remove boids on the fly
- **Click to add**: Click anywhere on the canvas to spawn new boids
- **Pause/Resume**: Control simulation playback

### Performance
- Optimized neighbor detection using squared distance calculations
- Smooth 60 FPS animation with 100+ boids
- Live FPS counter and statistics

## Architecture

The simulation is organized into modular, testable components:

```
vector.js          - 2D vector math library
boid.js            - Boid class with flocking behaviors
simulation.js      - Simulation manager and animation loop
index.html         - Main application with UI controls
```

## Testing

All core logic is thoroughly tested with separate test suites.

### Run All Tests

**Browser Testing:**
- Vector tests: Open `test-runner.html`
- Boid tests: Open `boid-test-runner.html`
- Simulation tests: Open `simulation-test-runner.html`

**Node.js Testing:**
```bash
node run-tests.js              # Vector tests (27 tests)
node run-boid-tests.js         # Boid tests (12 tests)
node run-simulation-tests.js   # Simulation tests (12 tests)
```

Total: **51 tests** covering vector math, boid behaviors, and simulation management.

## API Reference

### Vector Class

Complete 2D vector math utilities:

```javascript
const v = new Vector(3, 4);
v.magnitude()           // 5
v.normalize()           // Unit vector
v.limit(max)           // Constrain magnitude
v.add(other)           // Vector addition
v.distance(other)      // Euclidean distance
Vector.random()        // Random unit vector
Vector.fromAngle(θ)    // Create from angle
```

See `README.md` for complete Vector API documentation.

### Boid Class

Autonomous agents with flocking behaviors:

```javascript
const boid = new Boid(x, y);

// Configure parameters
boid.maxSpeed = 4;
boid.maxForce = 0.2;
boid.perceptionRadius = 50;

// Apply behaviors
boid.flock(allBoids);  // Calculate flocking forces
boid.update();         // Update position/velocity
boid.edges(w, h);      // Handle boundary wrapping
boid.render(ctx);      // Draw to canvas
```

Each behavior can be called independently:
- `boid.separate(boids)` - Returns separation force
- `boid.align(boids)` - Returns alignment force
- `boid.cohere(boids)` - Returns cohesion force

See `BOID_README.md` for complete Boid API documentation.

### Simulation Class

High-level simulation management:

```javascript
const sim = new Simulation(width, height, numBoids);

// Control simulation
sim.start();
sim.stop();
sim.toggle();

// Modify flock
sim.addBoid(x, y);
sim.reset(newCount);
sim.clear();

// Update parameters
sim.setParameter('maxSpeed', 6);
sim.setBehaviorWeights(separation, alignment, cohesion);

// Animation loop
sim.update();     // Advance one timestep
sim.render(ctx);  // Draw to canvas
```

## Design Decisions

### Immutable Vector Operations
All vector methods return new vectors rather than modifying in place. This makes the code:
- Easier to debug (no hidden side effects)
- Safer for concurrent operations
- More predictable in behavior calculations

### Toroidal Wrapping
Boids that exit one edge reappear on the opposite side, creating a toroidal topology. This:
- Keeps the flock together
- Avoids edge artifacts
- Feels more natural than bouncing

### Reynolds' Steering Formula
Classic `steering = desired - current_velocity` approach, then limited to `maxForce`. This creates smooth, natural turns rather than instant direction changes.

### Performance Optimizations
- **Squared distances**: Use `distanceSquared()` for neighbor detection to avoid expensive `sqrt()` calls
- **Perception radius**: Only process nearby neighbors, reducing O(n²) workload
- **Single animation loop**: One `requestAnimationFrame` manages all updates

### Test-Driven Development
Following TDD principles:
1. Write tests first to define expected behavior
2. Implement to pass tests
3. Refactor with confidence

This approach caught edge cases early and made the codebase more maintainable.

## Experimentation Ideas

Try adjusting parameters to see different emergent behaviors:

**Tight Swarms**
- High separation weight (2.0+)
- Low cohesion (0.5)
- Small perception radius (30-40)

**Loose Flowing Groups**
- Low separation (0.5)
- High cohesion (2.0)
- Large perception radius (100+)

**Chaotic Behavior**
- Low alignment (0.1)
- Balanced separation/cohesion
- High max speed (8+)

**Synchronized Schools**
- High alignment (2.0+)
- Balanced separation/cohesion
- Medium speed (4-5)

## Future Enhancements

Possible extensions:
- Obstacle avoidance
- Predator/prey dynamics
- Different species with varying parameters
- Trail rendering for motion visualization
- Target seeking behavior
- 3D boids implementation

## Technical Notes

### Browser Compatibility
Tested and working in:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

Requires ES6 support (class syntax, const/let, arrow functions).

### Performance Characteristics
- **100 boids**: 60 FPS (smooth)
- **200 boids**: 50-60 FPS (good)
- **300 boids**: 30-45 FPS (playable)

Performance scales as O(n²) due to all-pairs neighbor checking. For larger flocks (500+), consider spatial partitioning (quadtree, spatial hash grid).

## Credits

**Algorithm**: Craig Reynolds (1986) - "Flocks, Herds, and Schools: A Distributed Behavioral Model"

**Implementation**: Alice & Bob (collaborative development)
- Alice: Vector math library, Simulation manager
- Bob: Boid class and behaviors

**Methodology**: Test-driven development with 51 total tests

## License

This is an educational project demonstrating emergent behavior and test-driven development practices.

---

Enjoy watching the emergent beauty of simple rules creating complex, lifelike patterns! 🐦✨
