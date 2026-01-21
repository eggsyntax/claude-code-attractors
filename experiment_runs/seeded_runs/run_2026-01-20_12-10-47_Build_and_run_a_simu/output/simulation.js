/**
 * Simulation Manager for Boids Flocking
 *
 * Manages the flock lifecycle, animation loop, and parameter updates.
 * Provides methods to start/stop animation, update boid parameters,
 * and control behavior weights.
 *
 * Usage:
 *   const canvas = document.getElementById('canvas');
 *   const ctx = canvas.getContext('2d');
 *   const sim = new Simulation(canvas.width, canvas.height, 100);
 *
 *   // Animation loop
 *   function animate() {
 *     sim.update();
 *     sim.render(ctx);
 *     if (sim.isRunning) {
 *       requestAnimationFrame(animate);
 *     }
 *   }
 *
 *   sim.start();
 *   animate();
 */

if (typeof Vector === 'undefined' && typeof require !== 'undefined') {
    Vector = require('./vector.js');
    Boid = require('./boid.js');
}

class Simulation {
    /**
     * Creates a new simulation
     * @param {number} width - Width of the simulation space
     * @param {number} height - Height of the simulation space
     * @param {number} numBoids - Number of boids to create (default: 100)
     */
    constructor(width, height, numBoids = 100) {
        this.width = width;
        this.height = height;
        this.flock = [];
        this.isRunning = false;

        // Behavior weights (applied during flock calculations)
        this.separationWeight = 1.5;
        this.alignmentWeight = 1.0;
        this.cohesionWeight = 1.0;

        // Initialize flock
        this.reset(numBoids);
    }

    /**
     * Initializes the flock with random boids
     * @param {number} numBoids - Number of boids to create
     */
    reset(numBoids) {
        this.flock = [];
        for (let i = 0; i < numBoids; i++) {
            const x = Math.random() * this.width;
            const y = Math.random() * this.height;
            this.flock.push(new Boid(x, y));
        }
    }

    /**
     * Adds a single boid at the specified position
     * @param {number} x - X position
     * @param {number} y - Y position
     */
    addBoid(x, y) {
        this.flock.push(new Boid(x, y));
    }

    /**
     * Removes all boids from the simulation
     */
    clear() {
        this.flock = [];
    }

    /**
     * Sets a parameter on all boids in the flock
     * @param {string} paramName - Name of the parameter to set
     * @param {number} value - Value to set
     */
    setParameter(paramName, value) {
        for (let boid of this.flock) {
            if (paramName in boid) {
                boid[paramName] = value;
            }
        }
    }

    /**
     * Updates the behavior weights for flocking
     * @param {number} separation - Weight for separation behavior
     * @param {number} alignment - Weight for alignment behavior
     * @param {number} cohesion - Weight for cohesion behavior
     */
    setBehaviorWeights(separation, alignment, cohesion) {
        this.separationWeight = separation;
        this.alignmentWeight = alignment;
        this.cohesionWeight = cohesion;
    }

    /**
     * Updates all boids for one simulation step
     * Applies flocking behaviors and updates positions
     */
    update() {
        // Apply flocking behaviors to all boids
        for (let boid of this.flock) {
            // Calculate steering forces
            let separation = boid.separate(this.flock);
            let alignment = boid.align(this.flock);
            let cohesion = boid.cohere(this.flock);

            // Apply custom weights
            separation = separation.multiply(this.separationWeight);
            alignment = alignment.multiply(this.alignmentWeight);
            cohesion = cohesion.multiply(this.cohesionWeight);

            // Apply forces
            boid.applyForce(separation);
            boid.applyForce(alignment);
            boid.applyForce(cohesion);
        }

        // Update positions and handle edges
        for (let boid of this.flock) {
            boid.update();
            boid.edges(this.width, this.height);
        }
    }

    /**
     * Renders all boids to the canvas
     * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
     */
    render(ctx) {
        // Clear canvas
        ctx.clearRect(0, 0, this.width, this.height);

        // Draw all boids
        for (let boid of this.flock) {
            boid.render(ctx);
        }
    }

    /**
     * Starts the simulation
     */
    start() {
        this.isRunning = true;
    }

    /**
     * Stops the simulation
     */
    stop() {
        this.isRunning = false;
    }

    /**
     * Toggles the simulation running state
     * @returns {boolean} The new running state
     */
    toggle() {
        this.isRunning = !this.isRunning;
        return this.isRunning;
    }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Simulation;
}
