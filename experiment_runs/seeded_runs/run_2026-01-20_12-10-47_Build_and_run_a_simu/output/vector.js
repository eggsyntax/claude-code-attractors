/**
 * Vector Math Utility for 2D Simulations
 *
 * Provides a Vector class for 2D vector operations commonly needed
 * in physics simulations, boids, and particle systems.
 *
 * Usage:
 *   const v1 = new Vector(3, 4);
 *   const v2 = new Vector(1, 2);
 *   const sum = v1.add(v2);
 *   const magnitude = v1.magnitude();
 *   const normalized = v1.normalize();
 */

class Vector {
    /**
     * Creates a new 2D vector
     * @param {number} x - The x component
     * @param {number} y - The y component
     */
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }

    /**
     * Adds another vector to this vector
     * @param {Vector} other - The vector to add
     * @returns {Vector} A new vector representing the sum
     */
    add(other) {
        return new Vector(this.x + other.x, this.y + other.y);
    }

    /**
     * Subtracts another vector from this vector
     * @param {Vector} other - The vector to subtract
     * @returns {Vector} A new vector representing the difference
     */
    subtract(other) {
        return new Vector(this.x - other.x, this.y - other.y);
    }

    /**
     * Multiplies this vector by a scalar
     * @param {number} scalar - The scalar to multiply by
     * @returns {Vector} A new scaled vector
     */
    multiply(scalar) {
        return new Vector(this.x * scalar, this.y * scalar);
    }

    /**
     * Divides this vector by a scalar
     * @param {number} scalar - The scalar to divide by
     * @returns {Vector} A new scaled vector
     */
    divide(scalar) {
        if (scalar === 0) {
            console.warn('Division by zero in vector division');
            return new Vector(this.x, this.y);
        }
        return new Vector(this.x / scalar, this.y / scalar);
    }

    /**
     * Calculates the magnitude (length) of this vector
     * @returns {number} The magnitude
     */
    magnitude() {
        return Math.sqrt(this.x * this.x + this.y * this.y);
    }

    /**
     * Calculates the squared magnitude (avoids sqrt for performance)
     * Useful for distance comparisons where exact value isn't needed
     * @returns {number} The squared magnitude
     */
    magnitudeSquared() {
        return this.x * this.x + this.y * this.y;
    }

    /**
     * Normalizes this vector to unit length
     * @returns {Vector} A new unit vector in the same direction
     */
    normalize() {
        const mag = this.magnitude();
        if (mag === 0) {
            return new Vector(0, 0);
        }
        return this.divide(mag);
    }

    /**
     * Limits the magnitude of this vector to a maximum value
     * @param {number} max - The maximum magnitude
     * @returns {Vector} A new vector with limited magnitude
     */
    limit(max) {
        const mag = this.magnitude();
        if (mag > max) {
            return this.normalize().multiply(max);
        }
        return new Vector(this.x, this.y);
    }

    /**
     * Sets the magnitude of this vector to a specific value
     * @param {number} newMag - The desired magnitude
     * @returns {Vector} A new vector with the specified magnitude
     */
    setMagnitude(newMag) {
        return this.normalize().multiply(newMag);
    }

    /**
     * Calculates the distance to another vector
     * @param {Vector} other - The other vector
     * @returns {number} The distance between the vectors
     */
    distance(other) {
        const dx = this.x - other.x;
        const dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    /**
     * Calculates the squared distance to another vector
     * Useful for distance comparisons without the sqrt overhead
     * @param {Vector} other - The other vector
     * @returns {number} The squared distance
     */
    distanceSquared(other) {
        const dx = this.x - other.x;
        const dy = this.y - other.y;
        return dx * dx + dy * dy;
    }

    /**
     * Calculates the dot product with another vector
     * @param {Vector} other - The other vector
     * @returns {number} The dot product
     */
    dot(other) {
        return this.x * other.x + this.y * other.y;
    }

    /**
     * Calculates the angle (heading) of this vector in radians
     * @returns {number} The angle in radians (0 to 2π)
     */
    heading() {
        return Math.atan2(this.y, this.x);
    }

    /**
     * Creates a copy of this vector
     * @returns {Vector} A new vector with the same components
     */
    copy() {
        return new Vector(this.x, this.y);
    }

    /**
     * Creates a vector from an angle
     * @param {number} angle - The angle in radians
     * @param {number} magnitude - The magnitude (default: 1)
     * @returns {Vector} A new vector pointing in the specified direction
     */
    static fromAngle(angle, magnitude = 1) {
        return new Vector(
            Math.cos(angle) * magnitude,
            Math.sin(angle) * magnitude
        );
    }

    /**
     * Creates a random unit vector
     * @returns {Vector} A new random unit vector
     */
    static random() {
        const angle = Math.random() * Math.PI * 2;
        return Vector.fromAngle(angle);
    }

    /**
     * Creates a zero vector
     * @returns {Vector} A new vector with x=0, y=0
     */
    static zero() {
        return new Vector(0, 0);
    }

    /**
     * Returns a string representation of this vector
     * @returns {string} The vector as a string
     */
    toString() {
        return `Vector(${this.x.toFixed(2)}, ${this.y.toFixed(2)})`;
    }
}

// Export for Node.js / module environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Vector;
}
