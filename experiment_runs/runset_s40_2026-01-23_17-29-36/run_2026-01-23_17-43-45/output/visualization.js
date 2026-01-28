/**
 * Algorithm Visualization Engine
 * Handles step-by-step algorithm playback and state management
 */

class AlgorithmVisualizer {
    constructor(grid) {
        this.grid = grid;
        this.steps = [];
        this.currentStepIndex = -1;
        this.isPlaying = false;
        this.playbackSpeed = 5; // 1-10 scale
        this.playbackInterval = null;

        // UI elements
        this.elements = {
            stepCounter: document.getElementById('step-counter'),
            stepDescription: document.getElementById('step-description'),
            currentAlgorithm: document.getElementById('current-algorithm'),
            currentNode: document.getElementById('current-node'),
            openSet: document.getElementById('open-set'),
            closedSet: document.getElementById('closed-set'),
            costInfo: document.getElementById('cost-info'),
            nodesExplored: document.getElementById('nodes-explored'),
            pathLength: document.getElementById('path-length'),
            executionTime: document.getElementById('execution-time'),
            playPauseBtn: document.getElementById('play-pause-btn'),
            stepBackBtn: document.getElementById('step-back-btn'),
            stepForwardBtn: document.getElementById('step-forward-btn'),
            resetBtn: document.getElementById('reset-btn')
        };

        this.setupEventListeners();
    }

    /**
     * Setup event listeners for visualization controls
     */
    setupEventListeners() {
        this.elements.playPauseBtn.addEventListener('click', () => this.togglePlayPause());
        this.elements.stepBackBtn.addEventListener('click', () => this.stepBackward());
        this.elements.stepForwardBtn.addEventListener('click', () => this.stepForward());
        this.elements.resetBtn.addEventListener('click', () => this.reset());

        // Speed control
        const speedSlider = document.getElementById('speed-slider');
        const speedDisplay = document.getElementById('speed-display');
        speedSlider.addEventListener('input', (e) => {
            this.playbackSpeed = parseInt(e.target.value);
            speedDisplay.textContent = this.playbackSpeed;

            // Update playback interval if currently playing
            if (this.isPlaying) {
                this.stopPlayback();
                this.startPlayback();
            }
        });
    }

    /**
     * Load algorithm steps for visualization
     */
    loadSteps(steps, algorithmName) {
        this.steps = steps || [];
        this.currentStepIndex = -1;
        this.isPlaying = false;

        this.updateAlgorithmName(algorithmName);
        this.updateUI();
        this.updateControlButtons();

        // Clear previous visualization
        this.grid.clearVisualization();
        this.grid.draw();
    }

    /**
     * Update algorithm name in UI
     */
    updateAlgorithmName(algorithmName) {
        const displayNames = {
            'astar_manhattan': 'A* Search (Manhattan Heuristic)',
            'astar_euclidean': 'A* Search (Euclidean Heuristic)',
            'dijkstra': "Dijkstra's Algorithm",
            'bfs': 'Breadth-First Search'
        };

        this.elements.currentAlgorithm.textContent =
            `Algorithm: ${displayNames[algorithmName] || algorithmName}`;
    }

    /**
     * Toggle play/pause
     */
    togglePlayPause() {
        if (this.steps.length === 0) return;

        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    /**
     * Start playback
     */
    play() {
        if (this.steps.length === 0) return;

        this.isPlaying = true;
        this.elements.playPauseBtn.textContent = '⏸️ Pause';
        this.startPlayback();
    }

    /**
     * Pause playback
     */
    pause() {
        this.isPlaying = false;
        this.elements.playPauseBtn.textContent = '▶️ Play';
        this.stopPlayback();
    }

    /**
     * Start the playback interval
     */
    startPlayback() {
        const delay = Math.max(50, 1100 - (this.playbackSpeed * 100));

        this.playbackInterval = setInterval(() => {
            if (this.currentStepIndex < this.steps.length - 1) {
                this.stepForward();
            } else {
                // Reached end, stop playing
                this.pause();
            }
        }, delay);
    }

    /**
     * Stop the playback interval
     */
    stopPlayback() {
        if (this.playbackInterval) {
            clearInterval(this.playbackInterval);
            this.playbackInterval = null;
        }
    }

    /**
     * Step forward to next step
     */
    stepForward() {
        if (this.currentStepIndex < this.steps.length - 1) {
            this.currentStepIndex++;
            this.displayStep(this.steps[this.currentStepIndex]);
            this.updateUI();
            this.updateControlButtons();
        }
    }

    /**
     * Step backward to previous step
     */
    stepBackward() {
        if (this.currentStepIndex > -1) {
            this.currentStepIndex--;

            if (this.currentStepIndex >= 0) {
                this.displayStep(this.steps[this.currentStepIndex]);
            } else {
                // Reset to initial state
                this.grid.clearVisualization();
                this.grid.draw();
                this.resetUI();
            }

            this.updateUI();
            this.updateControlButtons();
        }
    }

    /**
     * Reset visualization to start
     */
    reset() {
        this.pause();
        this.currentStepIndex = -1;
        this.grid.clearVisualization();
        this.grid.draw();
        this.resetUI();
        this.updateControlButtons();
    }

    /**
     * Display a specific step
     */
    displayStep(step) {
        // Update grid visualization
        this.grid.updateVisualization(step);

        // Update step information
        this.updateStepInfo(step);
        this.updateAlgorithmState(step);
        this.updatePerformanceMetrics(step);
    }

    /**
     * Update step information display
     */
    updateStepInfo(step) {
        this.elements.stepDescription.textContent =
            step.description || 'Processing algorithm step...';
    }

    /**
     * Update algorithm state panels
     */
    updateAlgorithmState(step) {
        // Update current node
        if (step.current_node) {
            const node = step.current_node;
            this.elements.currentNode.innerHTML = `
                <div>Position: (${node.row}, ${node.col})</div>
                <div class="cost-display">
                    ${node.g_cost !== undefined ? `G: ${node.g_cost}` : ''}
                    ${node.h_cost !== undefined ? ` | H: ${node.h_cost}` : ''}
                    ${node.f_cost !== undefined ? ` | F: ${node.f_cost}` : ''}
                </div>
            `;
        } else {
            this.elements.currentNode.innerHTML = '<div>Position: -</div><div class="cost-display">-</div>';
        }

        // Update open set
        if (step.open_set && step.open_set.length > 0) {
            const openSetText = step.open_set
                .map(node => `(${node.row},${node.col})`)
                .join(', ');
            this.elements.openSet.textContent = openSetText;
        } else {
            this.elements.openSet.textContent = '-';
        }

        // Update closed set
        if (step.closed_set && step.closed_set.length > 0) {
            const closedSetText = step.closed_set
                .map(node => `(${node.row},${node.col})`)
                .join(', ');
            this.elements.closedSet.textContent = closedSetText;
        } else {
            this.elements.closedSet.textContent = '-';
        }
    }

    /**
     * Update performance metrics
     */
    updatePerformanceMetrics(step) {
        this.elements.nodesExplored.textContent =
            `Nodes Explored: ${step.nodes_explored || this.currentStepIndex + 1}`;

        if (step.path && step.path.length > 0) {
            this.elements.pathLength.textContent = `Path Length: ${step.path.length}`;
        } else {
            this.elements.pathLength.textContent = 'Path Length: -';
        }

        if (step.execution_time) {
            this.elements.executionTime.textContent =
                `Time: ${step.execution_time.toFixed(3)}ms`;
        } else {
            this.elements.executionTime.textContent = 'Time: -';
        }
    }

    /**
     * Update main UI elements
     */
    updateUI() {
        const totalSteps = this.steps.length;
        const currentStep = Math.max(0, this.currentStepIndex + 1);

        this.elements.stepCounter.textContent =
            totalSteps > 0 ? `Step: ${currentStep} / ${totalSteps}` : 'Step: 0 / 0';
    }

    /**
     * Reset UI to initial state
     */
    resetUI() {
        this.elements.stepDescription.textContent = 'Click Play to start visualization';
        this.elements.currentNode.innerHTML = '<div>Position: -</div><div class="cost-display">-</div>';
        this.elements.openSet.textContent = '-';
        this.elements.closedSet.textContent = '-';
        this.elements.nodesExplored.textContent = 'Nodes Explored: -';
        this.elements.pathLength.textContent = 'Path Length: -';
        this.elements.executionTime.textContent = 'Time: -';
    }

    /**
     * Update control button states
     */
    updateControlButtons() {
        const hasSteps = this.steps.length > 0;
        const canStepBack = this.currentStepIndex >= 0;
        const canStepForward = this.currentStepIndex < this.steps.length - 1;

        this.elements.stepBackBtn.disabled = !canStepBack;
        this.elements.stepForwardBtn.disabled = !canStepForward;

        if (!hasSteps) {
            this.elements.playPauseBtn.textContent = '▶️ Play';
            this.elements.playPauseBtn.disabled = true;
        } else {
            this.elements.playPauseBtn.disabled = false;
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        this.elements.stepDescription.textContent = 'Computing algorithm steps...';
        this.elements.playPauseBtn.disabled = true;
        this.elements.stepBackBtn.disabled = true;
        this.elements.stepForwardBtn.disabled = true;
    }

    /**
     * Show error state
     */
    showError(message) {
        this.elements.stepDescription.textContent = `Error: ${message}`;
        this.resetUI();
        this.updateControlButtons();
    }

    /**
     * Get current playback state
     */
    getState() {
        return {
            currentStep: this.currentStepIndex,
            totalSteps: this.steps.length,
            isPlaying: this.isPlaying,
            playbackSpeed: this.playbackSpeed
        };
    }
}