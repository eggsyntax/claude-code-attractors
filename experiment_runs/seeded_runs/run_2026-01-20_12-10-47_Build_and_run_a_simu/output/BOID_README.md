# Boid Implementation

Implementation of the Boid class for flocking simulation, following Craig Reynolds' classic boids algorithm (1986).

## Overview

This module implements autonomous agents (boids) that exhibit emergent flocking behavior through three simple rules:

1. **Separation** - Avoid crowding neighbors
2. **Alignment** - Steer towards average heading of neighbors
3. **Cohesion** - Steer towards average position of neighbors

## Files

- `boid.js` - Main Boid class implementation
- `boid-tests.js` - Comprehensive test suite (12 tests)
- `boid-test-runner.html` - Browser-based test runner
- `run-boid-tests.js` - Node.js test runner

## Boid Class API

### Constructor

```javascript
const boid = new Boid(x, y);
```

Creates a new boid at position (x, y) with random initial velocity.

### Properties

- `position` (Vector) - Current position
- `velocity` (Vector) - Current velocity
- `acceleration` (Vector) - Current acceleration (reset each frame)
- `maxSpeed` (number) - Maximum velocity magnitude (default: 4)
- `maxForce` (number) - Maximum steering force (default: 0.2)
- `perceptionRadius` (number) - How far boid can see neighbors (default: 50)

### Core Methods

#### `flock(boids)`
Applies all three flocking behaviors (separation, alignment, cohesion) to the boid.

**Parameters:**
- `boids` (Array<Boid>) - Array of all boids in the simulation

**Behavior weights (currently hardcoded):**
- Separation: 1.5x (strongest - avoids collisions)
- Alignment: 1.0x
- Cohesion: 1.0x

#### `update()`
Updates the boid's position and velocity based on accumulated forces.
- Applies acceleration to velocity
- Limits velocity to maxSpeed
- Updates position
- Resets acceleration to zero

#### `edges(width, height)`
Handles toroidal boundary wrapping.

**Parameters:**
- `width` (number) - Width of simulation space
- `height` (number) - Height of simulation space

Boids that move off one edge reappear on the opposite edge.

#### `render(ctx)`
Renders the boid as a triangle on a canvas.

**Parameters:**
- `ctx` (CanvasRenderingContext2D) - Canvas rendering context

### Individual Behavior Methods

These are called internally by `flock()` but can be used independently:

#### `separate(boids)` → Vector
Returns steering force to avoid crowding neighbors.

#### `align(boids)` → Vector
Returns steering force to match velocity with neighbors.

#### `cohere(boids)` → Vector
Returns steering force to move toward center of neighbors.

#### `applyForce(force)`
Accumulates a force vector to acceleration.

## Algorithm Details

### Steering Behavior

All three behaviors use Reynolds' steering formula:

```
steering = desired_velocity - current_velocity
steering = limit(steering, maxForce)
```

This creates smooth, natural-looking steering rather than instant direction changes.

### Neighbor Detection

Uses squared distance for performance (avoids sqrt):

```javascript
const perceptionRadiusSq = this.perceptionRadius * this.perceptionRadius;
const distSq = this.position.distanceSquared(other.position);
if (distSq < perceptionRadiusSq) {
    // This boid is a neighbor
}
```

### Separation Weighting

Closer boids have stronger influence:

```javascript
diff = diff.divide(distSq);  // Inverse square weighting
```

## Testing

The test suite covers:
- Initialization
- Update mechanics
- Speed limiting
- All three flocking behaviors
- Neighbor detection
- Force accumulation
- Edge wrapping

### Running Tests

**In browser:**
```
open boid-test-runner.html
```

**In Node.js:**
```bash
node run-boid-tests.js
```

All 12 tests should pass.

## Usage Example

```javascript
// Create flock
const flock = [];
for (let i = 0; i < 100; i++) {
    flock.push(new Boid(
        Math.random() * width,
        Math.random() * height
    ));
}

// Animation loop
function animate() {
    // Apply flocking behavior to each boid
    for (let boid of flock) {
        boid.flock(flock);
        boid.update();
        boid.edges(width, height);
    }

    // Render
    ctx.clearRect(0, 0, width, height);
    for (let boid of flock) {
        boid.render(ctx);
    }

    requestAnimationFrame(animate);
}
```

## Performance Considerations

- **O(n²) complexity**: Each boid checks all others for neighbors
- For large flocks (>500 boids), consider spatial partitioning (quadtree, grid)
- Using `distanceSquared()` instead of `distance()` reduces sqrt calls
- Perception radius limits how many neighbors are processed

## Tuning Parameters

For different behaviors, adjust these properties:

**Tighter flocks:**
- Increase cohesion weight
- Increase perception radius

**Looser flocks:**
- Increase separation weight
- Decrease cohesion weight

**More chaotic:**
- Increase maxSpeed
- Increase maxForce

**Smoother movement:**
- Decrease maxForce
- Decrease maxSpeed

## Dependencies

Requires `vector.js` - provides Vector class for 2D math operations.

## Next Steps

For the complete simulation, we still need:
- `simulation.js` - Main loop and flock management
- `index.html` - UI with canvas and parameter controls
- Interactive sliders for tuning weights and parameters in real-time

## References

- [Craig Reynolds' Boids](http://www.red3d.com/cwr/boids/) - Original algorithm
- [Nature of Code - Flocking](https://natureofcode.com/book/chapter-6-autonomous-agents/) - Excellent tutorial
