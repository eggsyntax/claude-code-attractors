/**
 * K-Means Clustering Algorithm Implementation
 * Educational visualization with step-by-step tracking
 */

class KMeansVisualizer {
    constructor() {
        this.points = [];
        this.centroids = [];
        this.clusters = [];
        this.steps = [];
        this.currentStep = 0;
        this.maxIterations = 50;
        this.tolerance = 0.001;
    }

    /**
     * Generate random data points for clustering
     * @param {number} numPoints - Number of data points to generate
     * @param {number} width - Canvas width
     * @param {number} height - Canvas height
     */
    generateRandomData(numPoints = 50, width = 600, height = 400) {
        this.points = [];
        for (let i = 0; i < numPoints; i++) {
            this.points.push({
                x: Math.random() * width,
                y: Math.random() * height,
                cluster: -1, // -1 means unassigned
                id: i
            });
        }
        this.recordStep('data_generated', 'Generated random data points');
    }

    /**
     * Generate clustered data (more realistic for demonstration)
     * @param {number} numClusters - Number of natural clusters
     * @param {number} pointsPerCluster - Points per cluster
     * @param {number} width - Canvas width
     * @param {number} height - Canvas height
     */
    generateClusteredData(numClusters = 3, pointsPerCluster = 15, width = 600, height = 400) {
        this.points = [];
        let id = 0;

        for (let cluster = 0; cluster < numClusters; cluster++) {
            // Generate cluster center
            const centerX = Math.random() * width;
            const centerY = Math.random() * height;
            const spread = 50; // How spread out the cluster is

            for (let point = 0; point < pointsPerCluster; point++) {
                // Generate points around cluster center with normal distribution
                const angle = Math.random() * 2 * Math.PI;
                const distance = Math.random() * spread;

                this.points.push({
                    x: Math.max(0, Math.min(width, centerX + Math.cos(angle) * distance)),
                    y: Math.max(0, Math.min(height, centerY + Math.sin(angle) * distance)),
                    cluster: -1,
                    id: id++
                });
            }
        }
        this.recordStep('clustered_data_generated', 'Generated realistic clustered data');
    }

    /**
     * Initialize centroids randomly
     * @param {number} k - Number of clusters
     * @param {number} width - Canvas width
     * @param {number} height - Canvas height
     */
    initializeCentroids(k = 3, width = 600, height = 400) {
        this.centroids = [];
        for (let i = 0; i < k; i++) {
            this.centroids.push({
                x: Math.random() * width,
                y: Math.random() * height,
                id: i,
                color: this.getClusterColor(i)
            });
        }
        this.recordStep('centroids_initialized', `Initialized ${k} random centroids`);
    }

    /**
     * Initialize centroids using K-means++ for better initial placement
     * @param {number} k - Number of clusters
     */
    initializeCentroidsKMeansPlusPlus(k = 3) {
        if (this.points.length === 0) return;

        this.centroids = [];

        // Choose first centroid randomly
        const firstCentroid = this.points[Math.floor(Math.random() * this.points.length)];
        this.centroids.push({
            x: firstCentroid.x,
            y: firstCentroid.y,
            id: 0,
            color: this.getClusterColor(0)
        });

        // Choose remaining centroids based on distance from existing centroids
        for (let i = 1; i < k; i++) {
            let maxDistance = 0;
            let bestPoint = null;

            for (const point of this.points) {
                // Find minimum distance to existing centroids
                let minDistToCentroid = Infinity;
                for (const centroid of this.centroids) {
                    const dist = this.calculateDistance(point, centroid);
                    minDistToCentroid = Math.min(minDistToCentroid, dist);
                }

                // Choose point with maximum minimum distance
                if (minDistToCentroid > maxDistance) {
                    maxDistance = minDistToCentroid;
                    bestPoint = point;
                }
            }

            if (bestPoint) {
                this.centroids.push({
                    x: bestPoint.x,
                    y: bestPoint.y,
                    id: i,
                    color: this.getClusterColor(i)
                });
            }
        }

        this.recordStep('centroids_kmeans++', `Initialized ${k} centroids using K-means++`);
    }

    /**
     * Calculate Euclidean distance between two points
     */
    calculateDistance(point1, point2) {
        const dx = point1.x - point2.x;
        const dy = point1.y - point2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    /**
     * Assign each point to the nearest centroid
     */
    assignPointsToClusters() {
        let changes = 0;

        for (const point of this.points) {
            let minDistance = Infinity;
            let nearestCentroid = -1;

            // Find nearest centroid
            for (let i = 0; i < this.centroids.length; i++) {
                const distance = this.calculateDistance(point, this.centroids[i]);
                if (distance < minDistance) {
                    minDistance = distance;
                    nearestCentroid = i;
                }
            }

            // Record if assignment changed
            if (point.cluster !== nearestCentroid) {
                changes++;
                point.cluster = nearestCentroid;
            }
        }

        this.recordStep('points_assigned', `Assigned points to clusters (${changes} changes)`);
        return changes;
    }

    /**
     * Update centroids to the mean of their assigned points
     */
    updateCentroids() {
        const newCentroids = [];
        let totalMovement = 0;

        for (let i = 0; i < this.centroids.length; i++) {
            const clusterPoints = this.points.filter(point => point.cluster === i);

            if (clusterPoints.length > 0) {
                // Calculate mean position
                const meanX = clusterPoints.reduce((sum, point) => sum + point.x, 0) / clusterPoints.length;
                const meanY = clusterPoints.reduce((sum, point) => sum + point.y, 0) / clusterPoints.length;

                // Calculate movement
                const movement = this.calculateDistance(
                    { x: meanX, y: meanY },
                    this.centroids[i]
                );
                totalMovement += movement;

                newCentroids.push({
                    x: meanX,
                    y: meanY,
                    id: i,
                    color: this.centroids[i].color
                });
            } else {
                // Keep centroid in same place if no points assigned
                newCentroids.push({ ...this.centroids[i] });
            }
        }

        this.centroids = newCentroids;
        this.recordStep('centroids_updated', `Updated centroids (total movement: ${totalMovement.toFixed(2)})`);
        return totalMovement;
    }

    /**
     * Run the complete K-means algorithm
     * @param {number} k - Number of clusters
     */
    runKMeans(k = 3, initMethod = 'kmeans++') {
        this.steps = [];
        this.currentStep = 0;

        // Initialize centroids
        if (initMethod === 'kmeans++') {
            this.initializeCentroidsKMeansPlusPlus(k);
        } else {
            this.initializeCentroids(k);
        }

        let iteration = 0;
        let converged = false;

        while (iteration < this.maxIterations && !converged) {
            this.recordStep('iteration_start', `Starting iteration ${iteration + 1}`);

            // Assign points to clusters
            const pointChanges = this.assignPointsToClusters();

            // Update centroids
            const centroidMovement = this.updateCentroids();

            // Check convergence
            if (pointChanges === 0 || centroidMovement < this.tolerance) {
                converged = true;
                this.recordStep('converged', `Algorithm converged after ${iteration + 1} iterations`);
            }

            iteration++;
        }

        if (!converged) {
            this.recordStep('max_iterations', `Stopped after ${this.maxIterations} iterations (may not have converged)`);
        }

        return this.steps;
    }

    /**
     * Calculate Within-Cluster Sum of Squares (WCSS) for evaluating clustering quality
     */
    calculateWCSS() {
        let wcss = 0;

        for (let i = 0; i < this.centroids.length; i++) {
            const clusterPoints = this.points.filter(point => point.cluster === i);
            for (const point of clusterPoints) {
                wcss += Math.pow(this.calculateDistance(point, this.centroids[i]), 2);
            }
        }

        return wcss;
    }

    /**
     * Record a step in the algorithm for visualization
     */
    recordStep(type, description) {
        this.steps.push({
            step: this.steps.length,
            type: type,
            description: description,
            points: JSON.parse(JSON.stringify(this.points)),
            centroids: JSON.parse(JSON.stringify(this.centroids)),
            wcss: this.calculateWCSS(),
            timestamp: Date.now()
        });
    }

    /**
     * Get color for cluster visualization
     */
    getClusterColor(clusterId) {
        const colors = [
            '#FF6B6B', // Red
            '#4ECDC4', // Teal
            '#45B7D1', // Blue
            '#96CEB4', // Green
            '#FFEAA7', // Yellow
            '#DDA0DD', // Plum
            '#98D8C8', // Mint
            '#FDCB6E'  // Orange
        ];
        return colors[clusterId % colors.length];
    }

    /**
     * Get current algorithm state for visualization
     */
    getCurrentState() {
        return {
            points: this.points,
            centroids: this.centroids,
            step: this.currentStep,
            totalSteps: this.steps.length,
            wcss: this.calculateWCSS(),
            isComplete: this.currentStep >= this.steps.length - 1
        };
    }

    /**
     * Navigate to specific step
     */
    goToStep(stepNumber) {
        if (stepNumber >= 0 && stepNumber < this.steps.length) {
            this.currentStep = stepNumber;
            const step = this.steps[stepNumber];
            this.points = JSON.parse(JSON.stringify(step.points));
            this.centroids = JSON.parse(JSON.stringify(step.centroids));
            return step;
        }
        return null;
    }

    /**
     * Go to next step
     */
    nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.currentStep++;
            return this.goToStep(this.currentStep);
        }
        return null;
    }

    /**
     * Go to previous step
     */
    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            return this.goToStep(this.currentStep);
        }
        return null;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KMeansVisualizer;
}