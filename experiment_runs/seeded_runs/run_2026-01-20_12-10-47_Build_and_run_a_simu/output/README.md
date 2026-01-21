# Boids Flocking Simulation

A collaborative project to build an interactive boids (flocking) simulation in JavaScript.

## Current Status

**Phase 1: Vector Math Foundation** ✓ (Alice)
- Implemented complete 2D vector math library
- Created comprehensive test suite
- All core vector operations tested and working

## Files

### Core Implementation
- **vector.js** - 2D vector math utilities with operations for:
  - Basic arithmetic (add, subtract, multiply, divide)
  - Magnitude and normalization
  - Distance calculations
  - Dot product
  - Angle/heading operations
  - Vector limiting and magnitude setting

### Testing
- **tests.js** - Comprehensive test suite for vector math
- **test-runner.html** - Browser-based test runner with visual output
- **run-tests.js** - Node.js test runner script

## Running Tests

### In Browser:
Open `test-runner.html` in a web browser to see test results with color-coded output.

### In Node.js:
```bash
node run-tests.js
```

## Next Steps

**Phase 2: Boid Implementation** (Bob)
- Create Boid class with position, velocity, and acceleration
- Implement three core steering behaviors:
  - Separation (avoid crowding neighbors)
  - Alignment (steer towards average heading of neighbors)
  - Cohesion (steer towards average position of neighbors)
- Add perception radius and neighbor detection
- Implement steering force accumulation and limits

**Phase 3: Simulation Engine**
- Canvas setup and rendering loop
- Boid visualization (triangles pointing in direction of travel)
- Real-time parameter controls

**Phase 4: Enhancements**
- Trail effects
- Obstacles
- Multiple species
- Performance optimizations

## Vector API Reference

```javascript
// Create vectors
const v1 = new Vector(x, y);
const v2 = Vector.fromAngle(angle, magnitude);
const v3 = Vector.random();

// Operations
v1.add(v2)           // Vector addition
v1.subtract(v2)      // Vector subtraction
v1.multiply(scalar)  // Scalar multiplication
v1.divide(scalar)    // Scalar division

// Properties
v1.magnitude()       // Get length
v1.normalize()       // Get unit vector
v1.limit(max)        // Limit magnitude to max
v1.setMagnitude(mag) // Set specific magnitude

// Comparisons
v1.distance(v2)      // Euclidean distance
v1.dot(v2)           // Dot product

// Angles
v1.heading()         // Get angle in radians
Vector.fromAngle(θ)  // Create from angle

// Utilities
v1.copy()            // Create independent copy
v1.toString()        // String representation
```

## Design Decisions

1. **Immutability**: Vector operations return new vectors rather than modifying in place. This prevents bugs and makes the code easier to reason about.

2. **Performance helpers**: Included `magnitudeSquared()` and `distanceSquared()` methods for distance comparisons that don't need exact values, avoiding expensive sqrt operations.

3. **Comprehensive testing**: All core operations have tests covering normal cases, edge cases (zero vectors), and mathematical properties (symmetry, etc.).

---

Built collaboratively by Alice and Bob
