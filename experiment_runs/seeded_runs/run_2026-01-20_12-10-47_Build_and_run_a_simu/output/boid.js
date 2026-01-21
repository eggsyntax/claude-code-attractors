/**
 * Boid Class - Autonomous agent for flocking simulation
 *
 * Implements three core flocking behaviors:
 * 1. Separation - Avoid crowding neighbors
 * 2. Alignment - Steer towards average heading of neighbors
 * 3. Cohesion - Steer towards average position of neighbors
 *
 * Based on Craig Reynolds' boids algorithm (1986)
 *
 * Usage:
 *   const boid = new Boid(x, y);
 *   boid.flock(allBoids);  // Apply flocking behaviors
 *   boid.update();          // Update position and velocity
 *   boid.edges(width, height);  // Handle boundary wrapping
 */

if (typeof Vector === 'undefined' && typeof require !== 'undefined') {
    Vector = require('./vector.js');
}

class Boid {
    /**
     * Creates a new boid at the specified position
     * @param {number} x - Initial x position
     * @param {number} y - Initial y position
     */
    constructor(x, y) {
        this.position = new Vector(x, y);
        this.velocity = Vector.random().multiply(2);
        this.acceleration = new Vector(0, 0);

        // Behavior parameters
        this.maxSpeed = 4;
        this.maxForce = 0.2;

        // Perception radius for neighbor detection
        this.perceptionRadius = 50;
    }

    /**
     * Applies a force to the boid's acceleration
     * @param {Vector} force - The force vector to apply
     */
    applyForce(force) {
        this.acceleration = this.acceleration.add(force);
    }

    /**
     * Calculates separation force to avoid crowding neighbors
     * Steers away from nearby boids
     * @param {Array<Boid>} boids - Array of all boids in the simulation
     * @returns {Vector} The separation steering force
     */
    separate(boids) {
        let steering = new Vector(0, 0);
        let total = 0;
        const perceptionRadiusSq = this.perceptionRadius * this.perceptionRadius;

        for (let other of boids) {
            // Skip self
            if (other === this) continue;

            const distSq = this.position.distanceSquared(other.position);

            // Only consider nearby boids
            if (distSq < perceptionRadiusSq && distSq > 0) {
                // Calculate vector pointing away from neighbor
                let diff = this.position.subtract(other.position);

                // Weight by distance (closer boids have more influence)
                diff = diff.divide(distSq);

                steering = steering.add(diff);
                total++;
            }
        }

        if (total > 0) {
            // Average the steering direction
            steering = steering.divide(total);

            // Implement Reynolds' steering = desired - velocity
            steering = steering.setMagnitude(this.maxSpeed);
            steering = steering.subtract(this.velocity);
            steering = steering.limit(this.maxForce);
        }

        return steering;
    }

    /**
     * Calculates alignment force to match velocity with neighbors
     * Steers towards the average heading of nearby boids
     * @param {Array<Boid>} boids - Array of all boids in the simulation
     * @returns {Vector} The alignment steering force
     */
    align(boids) {
        let steering = new Vector(0, 0);
        let total = 0;
        const perceptionRadiusSq = this.perceptionRadius * this.perceptionRadius;

        for (let other of boids) {
            // Skip self
            if (other === this) continue;

            const distSq = this.position.distanceSquared(other.position);

            // Only consider nearby boids
            if (distSq < perceptionRadiusSq) {
                steering = steering.add(other.velocity);
                total++;
            }
        }

        if (total > 0) {
            // Calculate average velocity
            steering = steering.divide(total);

            // Implement Reynolds' steering formula
            steering = steering.setMagnitude(this.maxSpeed);
            steering = steering.subtract(this.velocity);
            steering = steering.limit(this.maxForce);
        }

        return steering;
    }

    /**
     * Calculates cohesion force to move toward center of neighbors
     * Steers towards the average position of nearby boids
     * @param {Array<Boid>} boids - Array of all boids in the simulation
     * @returns {Vector} The cohesion steering force
     */
    cohere(boids) {
        let steering = new Vector(0, 0);
        let total = 0;
        const perceptionRadiusSq = this.perceptionRadius * this.perceptionRadius;

        for (let other of boids) {
            // Skip self
            if (other === this) continue;

            const distSq = this.position.distanceSquared(other.position);

            // Only consider nearby boids
            if (distSq < perceptionRadiusSq) {
                steering = steering.add(other.position);
                total++;
            }
        }

        if (total > 0) {
            // Calculate center of mass
            steering = steering.divide(total);

            // Seek towards center of mass
            steering = steering.subtract(this.position);
            steering = steering.setMagnitude(this.maxSpeed);
            steering = steering.subtract(this.velocity);
            steering = steering.limit(this.maxForce);
        }

        return steering;
    }

    /**
     * Applies all flocking behaviors (separation, alignment, cohesion)
     * Weights can be adjusted to tune behavior
     * @param {Array<Boid>} boids - Array of all boids in the simulation
     */
    flock(boids) {
        // Calculate forces from each behavior
        let separation = this.separate(boids);
        let alignment = this.align(boids);
        let cohesion = this.cohere(boids);

        // Apply weights to each force
        // These can be exposed as parameters for tuning
        separation = separation.multiply(1.5);
        alignment = alignment.multiply(1.0);
        cohesion = cohesion.multiply(1.0);

        // Apply all forces
        this.applyForce(separation);
        this.applyForce(alignment);
        this.applyForce(cohesion);
    }

    /**
     * Updates the boid's position and velocity
     * Applies acceleration, limits speed, and resets acceleration
     */
    update() {
        // Update velocity with acceleration
        this.velocity = this.velocity.add(this.acceleration);

        // Limit speed
        this.velocity = this.velocity.limit(this.maxSpeed);

        // Update position
        this.position = this.position.add(this.velocity);

        // Reset acceleration for next frame
        this.acceleration = new Vector(0, 0);
    }

    /**
     * Handles boundary wrapping (toroidal topology)
     * Boids that go off one edge reappear on the opposite edge
     * @param {number} width - Width of the simulation space
     * @param {number} height - Height of the simulation space
     */
    edges(width, height) {
        if (this.position.x > width) {
            this.position.x = 0;
        } else if (this.position.x < 0) {
            this.position.x = width;
        }

        if (this.position.y > height) {
            this.position.y = 0;
        } else if (this.position.y < 0) {
            this.position.y = height;
        }
    }

    /**
     * Renders the boid on a canvas context
     * Draws as a triangle pointing in the direction of movement
     * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
     */
    render(ctx) {
        const angle = this.velocity.heading();
        const size = 6;

        ctx.save();
        ctx.translate(this.position.x, this.position.y);
        ctx.rotate(angle);

        // Draw triangle
        ctx.beginPath();
        ctx.moveTo(size, 0);
        ctx.lineTo(-size, size / 2);
        ctx.lineTo(-size, -size / 2);
        ctx.closePath();

        ctx.fillStyle = 'rgba(100, 200, 255, 0.8)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(50, 150, 255, 1)';
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.restore();
    }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Boid;
}
