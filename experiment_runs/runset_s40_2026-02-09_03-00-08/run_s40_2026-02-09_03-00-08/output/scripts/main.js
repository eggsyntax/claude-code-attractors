/**
 * Main coordination script for Cellular Automata Explorer
 * Initializes and connects all components
 */

// Global application state
let app = {
    visualizationEngine: null,
    automataEngine: null,
    uiControls: null,
    currentRuleSystem: null
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔬 Initializing Cellular Automata Explorer...');

    try {
        initializeApplication();
        console.log('✅ Application initialized successfully!');
    } catch (error) {
        console.error('❌ Failed to initialize application:', error);
        showErrorMessage('Failed to initialize the application. Please refresh the page.');
    }
});

function initializeApplication() {
    // Initialize visualization engine
    const canvas = document.getElementById('automata-canvas');
    app.visualizationEngine = new VisualizationEngine(canvas);

    // Wait for Alice's automata engine implementation
    // For now, create a placeholder that matches our interface
    if (typeof AutomataEngine !== 'undefined' && typeof RuleSystem !== 'undefined') {
        // Alice's implementation is available
        initializeWithAlicesEngine();
    } else {
        // Create placeholder implementation
        console.log('⏳ Waiting for automata engine implementation...');
        initializeWithPlaceholder();
    }

    // Initialize UI controls
    app.uiControls = new UIControls(app.visualizationEngine, app.automataEngine);

    // Connect the engine to UI controls
    app.uiControls.setEngine(app.automataEngine);

    // Initial render
    app.uiControls.renderCurrentState();

    console.log('🎨 Visualization Engine initialized');
    console.log('🎛️ UI Controls initialized');
    console.log('🧠 Automata Engine ready');
}

function initializeWithAlicesEngine() {
    // This will be called when Alice's AutomataEngine is available
    const dims = app.visualizationEngine.getDimensions();

    // Create default rule system (Conway's Game of Life)
    app.currentRuleSystem = new ConwaysLifeRuleSystem();

    // Initialize the automata engine
    app.automataEngine = new AutomataEngine(
        dims.gridWidth,
        dims.gridHeight,
        app.currentRuleSystem
    );

    console.log('🚀 Using Alice\'s AutomataEngine implementation');
}

function initializeWithPlaceholder() {
    // Placeholder implementation until Alice's engine is ready
    const dims = app.visualizationEngine.getDimensions();

    app.automataEngine = {
        grid: null,
        width: dims.gridWidth,
        height: dims.gridHeight,
        ruleSystem: null,

        constructor(width, height, ruleSystem) {
            this.width = width;
            this.height = height;
            this.ruleSystem = ruleSystem;
            this.grid = this.createEmptyGrid();
        },

        createEmptyGrid() {
            const grid = [];
            for (let x = 0; x < this.width; x++) {
                grid[x] = [];
                for (let y = 0; y < this.height; y++) {
                    grid[x][y] = 0;
                }
            }
            return grid;
        },

        getGrid() {
            if (!this.grid) {
                this.grid = this.createEmptyGrid();
            }
            return this.grid;
        },

        setCell(x, y, state) {
            if (!this.grid) {
                this.grid = this.createEmptyGrid();
            }
            if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
                this.grid[x][y] = state;
            }
        },

        step() {
            // Placeholder implementation - just a simple random evolution
            if (!this.grid) return;

            const newGrid = this.createEmptyGrid();
            for (let x = 0; x < this.width; x++) {
                for (let y = 0; y < this.height; y++) {
                    // Simple Conway's-like rule for demonstration
                    const neighbors = this.countNeighbors(x, y);
                    const currentState = this.grid[x][y];

                    if (currentState === 1) {
                        // Live cell
                        newGrid[x][y] = (neighbors === 2 || neighbors === 3) ? 1 : 0;
                    } else {
                        // Dead cell
                        newGrid[x][y] = (neighbors === 3) ? 1 : 0;
                    }
                }
            }
            this.grid = newGrid;
        },

        countNeighbors(x, y) {
            let count = 0;
            for (let dx = -1; dx <= 1; dx++) {
                for (let dy = -1; dy <= 1; dy++) {
                    if (dx === 0 && dy === 0) continue;

                    const nx = x + dx;
                    const ny = y + dy;

                    if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height) {
                        count += this.grid[nx][ny];
                    }
                }
            }
            return count;
        },

        reset() {
            this.grid = this.createEmptyGrid();
        },

        clear() {
            this.reset();
        },

        getPopulation() {
            if (!this.grid) return 0;

            let population = 0;
            for (let x = 0; x < this.width; x++) {
                for (let y = 0; y < this.height; y++) {
                    if (this.grid[x][y] > 0) {
                        population++;
                    }
                }
            }
            return population;
        },

        resize(newWidth, newHeight) {
            const oldGrid = this.grid;
            this.width = newWidth;
            this.height = newHeight;
            this.grid = this.createEmptyGrid();

            // Copy over existing cells if they fit
            if (oldGrid) {
                for (let x = 0; x < Math.min(oldGrid.length, newWidth); x++) {
                    for (let y = 0; y < Math.min(oldGrid[0].length, newHeight); y++) {
                        this.grid[x][y] = oldGrid[x][y];
                    }
                }
            }
        }
    };

    // Initialize the placeholder
    app.automataEngine.constructor(dims.gridWidth, dims.gridHeight, null);

    console.log('📝 Using placeholder automata engine');
}

function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #ff6b6b;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        z-index: 1000;
        font-family: Arial, sans-serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    // Remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

// Function to switch rule systems (called by UI)
function switchRuleSystem(ruleSystemName) {
    if (!app.automataEngine) return;

    console.log(`🔄 Switching to rule system: ${ruleSystemName}`);

    // This will be expanded when Alice implements multiple rule systems
    if (typeof window[ruleSystemName] === 'function') {
        app.currentRuleSystem = new window[ruleSystemName]();
        app.automataEngine.setRuleSystem(app.currentRuleSystem);
        app.uiControls.resetSimulation();
    } else {
        console.warn(`Rule system ${ruleSystemName} not yet implemented`);
    }
}

// Export key functions for debugging and development
window.automataApp = {
    app: app,
    switchRuleSystem: switchRuleSystem,
    getStats: () => ({
        generation: app.uiControls ? app.uiControls.generation : 0,
        population: app.automataEngine ? app.automataEngine.getPopulation() : 0,
        isPlaying: app.uiControls ? app.uiControls.isPlaying : false
    }),
    exportImage: () => app.visualizationEngine ? app.visualizationEngine.exportAsImage() : null
};