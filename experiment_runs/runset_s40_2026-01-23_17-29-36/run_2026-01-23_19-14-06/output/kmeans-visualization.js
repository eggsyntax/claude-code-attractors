/**
 * K-Means Clustering Visualization Component
 * Interactive canvas-based visualization with step-by-step animation
 */

class KMeansVisualization {
    constructor(canvasId, controlsId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.controls = document.getElementById(controlsId);

        this.kmeans = new KMeansVisualizer();
        this.animating = false;
        this.animationSpeed = 1000; // milliseconds between steps
        this.animationTimer = null;

        this.setupCanvas();
        this.setupControls();
        this.setupEventListeners();
    }

    setupCanvas() {
        // Set canvas size
        this.canvas.width = 800;
        this.canvas.height = 500;

        // Set up canvas styling
        this.canvas.style.border = '2px solid #333';
        this.canvas.style.borderRadius = '8px';
        this.canvas.style.backgroundColor = '#f8f9fa';
    }

    setupControls() {
        this.controls.innerHTML = `
            <div class="kmeans-controls">
                <div class="control-row">
                    <div class="control-group">
                        <label for="numClusters">Number of Clusters (k):</label>
                        <input type="range" id="numClusters" min="2" max="8" value="3">
                        <span id="numClustersValue">3</span>
                    </div>

                    <div class="control-group">
                        <label for="numPoints">Number of Points:</label>
                        <input type="range" id="numPoints" min="20" max="100" value="50" step="10">
                        <span id="numPointsValue">50</span>
                    </div>

                    <div class="control-group">
                        <label for="dataType">Data Type:</label>
                        <select id="dataType">
                            <option value="clustered">Clustered Data</option>
                            <option value="random">Random Data</option>
                        </select>
                    </div>
                </div>

                <div class="control-row">
                    <div class="control-group">
                        <label for="initMethod">Initialization:</label>
                        <select id="initMethod">
                            <option value="kmeans++">K-means++</option>
                            <option value="random">Random</option>
                        </select>
                    </div>

                    <div class="control-group">
                        <label for="animationSpeed">Animation Speed:</label>
                        <input type="range" id="animationSpeed" min="100" max="2000" value="1000" step="100">
                        <span id="animationSpeedValue">1.0s</span>
                    </div>
                </div>

                <div class="control-row">
                    <button id="generateData" class="btn btn-secondary">Generate New Data</button>
                    <button id="runKMeans" class="btn btn-primary">Run K-Means</button>
                    <button id="playPause" class="btn btn-success" disabled>Play</button>
                    <button id="stepForward" class="btn btn-info" disabled>Step →</button>
                    <button id="stepBackward" class="btn btn-info" disabled>← Step</button>
                    <button id="reset" class="btn btn-warning" disabled>Reset</button>
                </div>

                <div class="progress-section">
                    <div class="progress-info">
                        <span id="stepInfo">Ready to generate data</span>
                        <span id="wcssInfo"></span>
                    </div>
                    <div class="progress-bar">
                        <div id="progressFill" class="progress-fill"></div>
                    </div>
                </div>

                <div class="metrics-section" style="display: none;">
                    <h4>Algorithm Metrics</h4>
                    <div id="metricsDisplay"></div>
                </div>
            </div>

            <style>
                .kmeans-controls {
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }

                .control-row {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 15px;
                    align-items: center;
                    flex-wrap: wrap;
                }

                .control-group {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .control-group label {
                    font-weight: 500;
                    min-width: 120px;
                }

                .btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: all 0.2s;
                }

                .btn:hover:not(:disabled) { transform: translateY(-1px); }
                .btn:disabled { opacity: 0.6; cursor: not-allowed; }

                .btn-primary { background: #007bff; color: white; }
                .btn-secondary { background: #6c757d; color: white; }
                .btn-success { background: #28a745; color: white; }
                .btn-info { background: #17a2b8; color: white; }
                .btn-warning { background: #ffc107; color: #212529; }

                .progress-section {
                    margin-top: 20px;
                }

                .progress-info {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                    font-weight: 500;
                }

                .progress-bar {
                    height: 6px;
                    background: #e9ecef;
                    border-radius: 3px;
                    overflow: hidden;
                }

                .progress-fill {
                    height: 100%;
                    background: #007bff;
                    width: 0%;
                    transition: width 0.3s ease;
                }

                .metrics-section {
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                }

                #metricsDisplay {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 10px;
                }

                .metric-card {
                    background: white;
                    padding: 12px;
                    border-radius: 6px;
                    border: 1px solid #dee2e6;
                }

                .metric-title {
                    font-weight: 600;
                    color: #495057;
                    margin-bottom: 4px;
                }

                .metric-value {
                    font-size: 1.2em;
                    font-weight: 700;
                    color: #007bff;
                }
            </style>
        `;
    }

    setupEventListeners() {
        // Control updates
        document.getElementById('numClusters').addEventListener('input', (e) => {
            document.getElementById('numClustersValue').textContent = e.target.value;
        });

        document.getElementById('numPoints').addEventListener('input', (e) => {
            document.getElementById('numPointsValue').textContent = e.target.value;
        });

        document.getElementById('animationSpeed').addEventListener('input', (e) => {
            this.animationSpeed = parseInt(e.target.value);
            document.getElementById('animationSpeedValue').textContent = (this.animationSpeed / 1000).toFixed(1) + 's';
        });

        // Button actions
        document.getElementById('generateData').addEventListener('click', () => this.generateData());
        document.getElementById('runKMeans').addEventListener('click', () => this.runAlgorithm());
        document.getElementById('playPause').addEventListener('click', () => this.toggleAnimation());
        document.getElementById('stepForward').addEventListener('click', () => this.stepForward());
        document.getElementById('stepBackward').addEventListener('click', () => this.stepBackward());
        document.getElementById('reset').addEventListener('click', () => this.reset());
    }

    generateData() {
        const numPoints = parseInt(document.getElementById('numPoints').value);
        const dataType = document.getElementById('dataType').value;

        if (dataType === 'clustered') {
            this.kmeans.generateClusteredData(3, Math.floor(numPoints / 3), this.canvas.width - 50, this.canvas.height - 50);
        } else {
            this.kmeans.generateRandomData(numPoints, this.canvas.width - 50, this.canvas.height - 50);
        }

        this.draw();
        this.updateUI('Data generated. Ready to run K-Means algorithm.');

        // Enable run button, disable others
        document.getElementById('runKMeans').disabled = false;
        document.getElementById('playPause').disabled = true;
        document.getElementById('stepForward').disabled = true;
        document.getElementById('stepBackward').disabled = true;
        document.getElementById('reset').disabled = true;
    }

    runAlgorithm() {
        const k = parseInt(document.getElementById('numClusters').value);
        const initMethod = document.getElementById('initMethod').value;

        // Run the algorithm and get all steps
        const steps = this.kmeans.runKMeans(k, initMethod);

        // Reset to first step
        this.kmeans.goToStep(0);
        this.draw();

        // Enable playback controls
        document.getElementById('runKMeans').disabled = true;
        document.getElementById('playPause').disabled = false;
        document.getElementById('stepForward').disabled = false;
        document.getElementById('stepBackward').disabled = false;
        document.getElementById('reset').disabled = false;

        this.updateUI(`Algorithm complete. ${steps.length} steps recorded.`);
        this.updateProgress();
        this.showMetrics();
    }

    toggleAnimation() {
        const button = document.getElementById('playPause');

        if (this.animating) {
            this.stopAnimation();
            button.textContent = 'Play';
            button.className = 'btn btn-success';
        } else {
            this.startAnimation();
            button.textContent = 'Pause';
            button.className = 'btn btn-danger';
        }
    }

    startAnimation() {
        this.animating = true;
        this.animationTimer = setInterval(() => {
            if (!this.stepForward()) {
                this.stopAnimation();
                document.getElementById('playPause').textContent = 'Play';
                document.getElementById('playPause').className = 'btn btn-success';
            }
        }, this.animationSpeed);
    }

    stopAnimation() {
        this.animating = false;
        if (this.animationTimer) {
            clearInterval(this.animationTimer);
            this.animationTimer = null;
        }
    }

    stepForward() {
        const step = this.kmeans.nextStep();
        if (step) {
            this.draw();
            this.updateUI(step.description);
            this.updateProgress();
            return true;
        }
        return false;
    }

    stepBackward() {
        const step = this.kmeans.previousStep();
        if (step) {
            this.draw();
            this.updateUI(step.description);
            this.updateProgress();
            return true;
        }
        return false;
    }

    reset() {
        this.stopAnimation();
        this.kmeans.goToStep(0);
        this.draw();
        this.updateUI('Reset to beginning');
        this.updateProgress();

        const button = document.getElementById('playPause');
        button.textContent = 'Play';
        button.className = 'btn btn-success';
    }

    draw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const state = this.kmeans.getCurrentState();

        // Draw connection lines from points to their assigned centroids
        this.ctx.globalAlpha = 0.3;
        this.ctx.lineWidth = 1;
        for (const point of state.points) {
            if (point.cluster >= 0 && point.cluster < state.centroids.length) {
                const centroid = state.centroids[point.cluster];
                this.ctx.strokeStyle = centroid.color;
                this.ctx.beginPath();
                this.ctx.moveTo(point.x + 25, point.y + 25);
                this.ctx.lineTo(centroid.x + 25, centroid.y + 25);
                this.ctx.stroke();
            }
        }
        this.ctx.globalAlpha = 1;

        // Draw data points
        for (const point of state.points) {
            if (point.cluster >= 0) {
                this.ctx.fillStyle = state.centroids[point.cluster].color;
            } else {
                this.ctx.fillStyle = '#666';
            }

            this.ctx.beginPath();
            this.ctx.arc(point.x + 25, point.y + 25, 4, 0, 2 * Math.PI);
            this.ctx.fill();

            // Add subtle border
            this.ctx.strokeStyle = '#333';
            this.ctx.lineWidth = 0.5;
            this.ctx.stroke();
        }

        // Draw centroids
        for (const centroid of state.centroids) {
            // Draw centroid shadow
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            this.ctx.beginPath();
            this.ctx.arc(centroid.x + 27, centroid.y + 27, 8, 0, 2 * Math.PI);
            this.ctx.fill();

            // Draw centroid
            this.ctx.fillStyle = centroid.color;
            this.ctx.beginPath();
            this.ctx.arc(centroid.x + 25, centroid.y + 25, 8, 0, 2 * Math.PI);
            this.ctx.fill();

            // Draw centroid border
            this.ctx.strokeStyle = '#000';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();

            // Draw centroid cross
            this.ctx.strokeStyle = '#fff';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.moveTo(centroid.x + 20, centroid.y + 25);
            this.ctx.lineTo(centroid.x + 30, centroid.y + 25);
            this.ctx.moveTo(centroid.x + 25, centroid.y + 20);
            this.ctx.lineTo(centroid.x + 25, centroid.y + 30);
            this.ctx.stroke();
        }

        // Draw legend
        this.drawLegend();
    }

    drawLegend() {
        const legendX = this.canvas.width - 150;
        const legendY = 20;

        // Legend background
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        this.ctx.fillRect(legendX - 10, legendY - 10, 140, 60);
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(legendX - 10, legendY - 10, 140, 60);

        // Legend items
        this.ctx.fillStyle = '#333';
        this.ctx.font = '12px sans-serif';
        this.ctx.fillText('Legend:', legendX, legendY + 5);

        // Data point
        this.ctx.fillStyle = '#666';
        this.ctx.beginPath();
        this.ctx.arc(legendX + 10, legendY + 20, 3, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.fillStyle = '#333';
        this.ctx.fillText('Data Point', legendX + 20, legendY + 24);

        // Centroid
        this.ctx.fillStyle = '#FF6B6B';
        this.ctx.beginPath();
        this.ctx.arc(legendX + 10, legendY + 35, 6, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
        this.ctx.fillStyle = '#333';
        this.ctx.fillText('Centroid', legendX + 20, legendY + 39);
    }

    updateUI(message) {
        document.getElementById('stepInfo').textContent = message;

        const state = this.kmeans.getCurrentState();
        if (state.wcss > 0) {
            document.getElementById('wcssInfo').textContent = `WCSS: ${state.wcss.toFixed(2)}`;
        }
    }

    updateProgress() {
        const state = this.kmeans.getCurrentState();
        const progress = state.totalSteps > 0 ? (state.step + 1) / state.totalSteps * 100 : 0;
        document.getElementById('progressFill').style.width = progress + '%';
    }

    showMetrics() {
        const metricsSection = document.querySelector('.metrics-section');
        const metricsDisplay = document.getElementById('metricsDisplay');

        const state = this.kmeans.getCurrentState();
        const steps = this.kmeans.steps;

        // Calculate metrics
        const iterations = steps.filter(s => s.type === 'iteration_start').length;
        const finalWCSS = state.wcss;
        const convergenceStep = steps.findIndex(s => s.type === 'converged');

        metricsDisplay.innerHTML = `
            <div class="metric-card">
                <div class="metric-title">Total Iterations</div>
                <div class="metric-value">${iterations}</div>
            </div>

            <div class="metric-card">
                <div class="metric-title">Final WCSS</div>
                <div class="metric-value">${finalWCSS.toFixed(2)}</div>
            </div>

            <div class="metric-card">
                <div class="metric-title">Convergence</div>
                <div class="metric-value">${convergenceStep >= 0 ? 'Yes' : 'No'}</div>
            </div>

            <div class="metric-card">
                <div class="metric-title">Data Points</div>
                <div class="metric-value">${state.points.length}</div>
            </div>
        `;

        metricsSection.style.display = 'block';
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('kmeansCanvas') && document.getElementById('kmeansControls')) {
        window.kmeansViz = new KMeansVisualization('kmeansCanvas', 'kmeansControls');
    }
});