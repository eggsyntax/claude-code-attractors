/**
 * Main Application Controller
 * Connects frontend components to Python backend API
 */

class AlgorithmLearningStudio {
    constructor() {
        this.baseURL = 'http://localhost:8000'; // Python FastAPI backend
        this.grid = null;
        this.visualizer = null;

        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        // Initialize grid
        this.grid = new InteractiveGrid('grid-canvas', 600, 600, 30);

        // Initialize visualizer
        this.visualizer = new AlgorithmVisualizer(this.grid);

        // Setup event listeners
        this.setupEventListeners();

        // Check backend connection
        await this.checkBackendConnection();

        // Check for demo scenario from localStorage
        this.checkForDemoScenario();

        console.log('🎯 Algorithm Learning Studio initialized!');
    }

    /**
     * Setup application event listeners
     */
    setupEventListeners() {
        // Algorithm selector
        const algorithmSelect = document.getElementById('algorithm-select');
        algorithmSelect.addEventListener('change', () => {
            this.visualizer.updateAlgorithmName(algorithmSelect.value);
        });

        // Run button (integrated into play/pause)
        const playPauseBtn = document.getElementById('play-pause-btn');
        const originalClickHandler = playPauseBtn.onclick;

        playPauseBtn.addEventListener('click', async (e) => {
            // If no steps loaded, run algorithm first
            if (this.visualizer.steps.length === 0) {
                e.stopPropagation();
                await this.runAlgorithm();
            }
        });

        // Reset button also clears algorithm steps
        const resetBtn = document.getElementById('reset-btn');
        resetBtn.addEventListener('click', () => {
            this.visualizer.loadSteps([], algorithmSelect.value);
        });
    }

    /**
     * Check if backend is available
     */
    async checkBackendConnection() {
        try {
            const response = await fetch(`${this.baseURL}/`, {
                method: 'GET',
                mode: 'cors'
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Backend connected:', data.message || 'Connected');
                return true;
            } else {
                throw new Error('Backend not responding correctly');
            }
        } catch (error) {
            console.warn('⚠️ Backend not available:', error.message);
            this.showBackendError();
            return false;
        }
    }

    /**
     * Show backend connection error
     */
    showBackendError() {
        const stepDescription = document.getElementById('step-description');
        stepDescription.innerHTML = `
            <div style="color: #f44336;">
                <strong>Backend not available</strong><br>
                Start the Python backend server:<br>
                <code style="background: #f5f5f5; padding: 2px 4px;">uvicorn main:app --reload</code>
            </div>
        `;
    }

    /**
     * Run selected algorithm
     */
    async runAlgorithm() {
        const algorithmSelect = document.getElementById('algorithm-select');
        const selectedAlgorithm = algorithmSelect.value;

        // Validate that start and end points are set
        if (!this.grid.startPoint || !this.grid.endPoint) {
            this.visualizer.showError('Please set both start (green) and end (red) points by left-clicking on the grid');
            return;
        }

        // Show loading state
        this.visualizer.showLoading();

        try {
            // Get current grid state
            const gridState = this.grid.getGridState();

            // Prepare API request
            const requestData = {
                grid: gridState,
                start: gridState.start,
                end: gridState.end,
                obstacles: gridState.obstacles
            };

            // Make API request
            const response = await fetch(`${this.baseURL}/run-algorithm/${selectedAlgorithm}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
                mode: 'cors'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            const result = await response.json();

            // Load steps into visualizer
            this.visualizer.loadSteps(result.steps, selectedAlgorithm);

            // Show success message
            const stepDescription = document.getElementById('step-description');
            stepDescription.textContent = result.path_found
                ? `✅ Path found! ${result.steps.length} steps computed. Click Play to visualize.`
                : `❌ No path exists between start and end points. ${result.steps.length} steps computed.`;

            console.log('Algorithm executed:', {
                algorithm: selectedAlgorithm,
                pathFound: result.path_found,
                steps: result.steps.length,
                nodesExplored: result.nodes_explored,
                executionTime: result.execution_time
            });

        } catch (error) {
            console.error('Algorithm execution failed:', error);
            this.visualizer.showError(`Failed to run algorithm: ${error.message}`);
        }
    }

    /**
     * Export current state (for debugging/sharing)
     */
    exportState() {
        const state = {
            gridState: this.grid.getGridState(),
            visualizerState: this.visualizer.getState(),
            selectedAlgorithm: document.getElementById('algorithm-select').value
        };

        const dataStr = JSON.stringify(state, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });

        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'algorithm-state.json';
        link.click();

        console.log('State exported:', state);
    }

    /**
     * Check for demo scenario from localStorage
     */
    checkForDemoScenario() {
        const scenarioData = localStorage.getItem('algorithmStudioScenario');
        if (scenarioData) {
            try {
                const scenario = JSON.parse(scenarioData);
                this.loadState(scenario);
                localStorage.removeItem('algorithmStudioScenario'); // Clear after loading

                // Show welcome message
                const stepDescription = document.getElementById('step-description');
                stepDescription.innerHTML = `
                    <div style="color: #28a745; font-weight: bold;">
                        ✨ Demo scenario loaded! Set up as shown and click Play to see the algorithm in action.
                    </div>
                `;
            } catch (error) {
                console.warn('Failed to load demo scenario:', error);
            }
        }
    }

    /**
     * Load state from JSON (for debugging/sharing)
     */
    async loadState(stateData) {
        try {
            // Set algorithm
            const algorithmSelect = document.getElementById('algorithm-select');
            algorithmSelect.value = stateData.selectedAlgorithm || 'astar_manhattan';

            // Restore grid state
            if (stateData.gridState) {
                const { start, end, obstacles } = stateData.gridState;

                // Reset grid
                this.grid.reset();

                // Set start point
                if (start) {
                    this.grid.startPoint = start;
                    this.grid.grid[start.row][start.col] = 'start';
                }

                // Set end point
                if (end) {
                    this.grid.endPoint = end;
                    this.grid.grid[end.row][end.col] = 'end';
                }

                // Set obstacles
                if (obstacles) {
                    obstacles.forEach(obstacle => {
                        const cellKey = `${obstacle.row},${obstacle.col}`;
                        this.grid.obstacles.add(cellKey);
                        this.grid.grid[obstacle.row][obstacle.col] = 'obstacle';
                    });
                }

                this.grid.draw();
            }

            console.log('State loaded successfully');
        } catch (error) {
            console.error('Failed to load state:', error);
            this.visualizer.showError(`Failed to load state: ${error.message}`);
        }
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.algorithmStudio = new AlgorithmLearningStudio();

    // Add some helpful global functions for debugging
    window.exportState = () => window.algorithmStudio.exportState();

    // File input for loading state
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json';
    fileInput.style.display = 'none';
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const stateData = JSON.parse(e.target.result);
                    window.algorithmStudio.loadState(stateData);
                } catch (error) {
                    console.error('Invalid state file:', error);
                }
            };
            reader.readAsText(file);
        }
    });
    document.body.appendChild(fileInput);

    window.loadState = () => fileInput.click();

    console.log('🎯 Use exportState() and loadState() for debugging!');
});

// Add some sample scenarios for quick testing
const SampleScenarios = {
    /**
     * Simple straight path
     */
    simplePath: {
        selectedAlgorithm: 'astar_manhattan',
        gridState: {
            width: 30,
            height: 30,
            start: { row: 5, col: 5 },
            end: { row: 5, col: 20 },
            obstacles: []
        }
    },

    /**
     * Path with obstacles requiring navigation
     */
    obstacleNavigation: {
        selectedAlgorithm: 'astar_manhattan',
        gridState: {
            width: 30,
            height: 30,
            start: { row: 5, col: 5 },
            end: { row: 20, col: 20 },
            obstacles: [
                // Vertical wall
                { row: 10, col: 10 }, { row: 11, col: 10 }, { row: 12, col: 10 },
                { row: 13, col: 10 }, { row: 14, col: 10 }, { row: 15, col: 10 },
                // Horizontal wall
                { row: 15, col: 11 }, { row: 15, col: 12 }, { row: 15, col: 13 },
                { row: 15, col: 14 }, { row: 15, col: 15 }
            ]
        }
    },

    /**
     * Maze-like scenario
     */
    maze: {
        selectedAlgorithm: 'astar_manhattan',
        gridState: {
            width: 30,
            height: 30,
            start: { row: 1, col: 1 },
            end: { row: 25, col: 25 },
            obstacles: [
                // Create a simple maze pattern
                { row: 3, col: 1 }, { row: 3, col: 2 }, { row: 3, col: 3 },
                { row: 5, col: 5 }, { row: 5, col: 6 }, { row: 5, col: 7 },
                { row: 7, col: 3 }, { row: 8, col: 3 }, { row: 9, col: 3 },
                { row: 11, col: 8 }, { row: 11, col: 9 }, { row: 11, col: 10 }
            ]
        }
    }
};

// Make sample scenarios available globally
window.loadSample = (scenarioName) => {
    if (SampleScenarios[scenarioName] && window.algorithmStudio) {
        window.algorithmStudio.loadState(SampleScenarios[scenarioName]);
    } else {
        console.log('Available samples:', Object.keys(SampleScenarios));
    }
};