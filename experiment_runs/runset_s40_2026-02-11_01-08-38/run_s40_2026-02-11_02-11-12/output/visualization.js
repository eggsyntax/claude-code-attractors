class PathfindingVisualizer {
    constructor(canvasId, gridSize = 25) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = gridSize;
        this.cellSize = 20;

        // Set canvas dimensions
        this.canvas.width = this.gridSize * this.cellSize;
        this.canvas.height = this.gridSize * this.cellSize;

        // Grid state
        this.grid = this.initializeGrid();
        this.startPos = { x: 2, y: 2 };
        this.endPos = { x: this.gridSize - 3, y: this.gridSize - 3 };

        // Drawing state
        this.isDrawing = false;
        this.currentMode = 'walls';

        // Animation state
        this.isAnimating = false;
        this.animationSpeed = 50;
        this.activeAlgorithms = new Set(['astar', 'dijkstra']);

        // Colors for different algorithms
        this.algorithmColors = {
            astar: {
                explored: 'rgba(255, 107, 107, 0.3)',
                path: 'rgba(255, 107, 107, 0.8)',
                current: 'rgba(255, 107, 107, 1)'
            },
            dijkstra: {
                explored: 'rgba(78, 205, 196, 0.3)',
                path: 'rgba(78, 205, 196, 0.8)',
                current: 'rgba(78, 205, 196, 1)'
            },
            bfs: {
                explored: 'rgba(69, 183, 209, 0.3)',
                path: 'rgba(69, 183, 209, 0.8)',
                current: 'rgba(69, 183, 209, 1)'
            },
            dfs: {
                explored: 'rgba(243, 156, 18, 0.3)',
                path: 'rgba(243, 156, 18, 0.8)',
                current: 'rgba(243, 156, 18, 1)'
            }
        };

        // Algorithm results
        this.algorithmResults = new Map();

        this.setupEventListeners();
        this.render();
    }

    initializeGrid() {
        const grid = [];
        for (let y = 0; y < this.gridSize; y++) {
            grid[y] = [];
            for (let x = 0; x < this.gridSize; x++) {
                grid[y][x] = {
                    type: 'empty',
                    algorithmStates: new Map() // Track state for each algorithm
                };
            }
        }
        return grid;
    }

    setupEventListeners() {
        // Mouse events for grid interaction
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.handleMouseUp());
        this.canvas.addEventListener('mouseleave', () => this.handleMouseUp());

        // UI controls
        document.querySelectorAll('input[name="algorithm"]').forEach(input => {
            input.addEventListener('change', () => this.updateActiveAlgorithms());
        });

        document.querySelectorAll('input[name="mode"]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.currentMode = e.target.value;
            });
        });

        document.getElementById('speed-slider').addEventListener('input', (e) => {
            this.animationSpeed = parseInt(e.target.value);
            this.updateSpeedDisplay();
        });

        // Grid manipulation buttons
        document.getElementById('clear-grid').addEventListener('click', () => this.clearGrid());
        document.getElementById('generate-maze').addEventListener('click', () => this.generateRandomMaze());
        document.getElementById('clear-path').addEventListener('click', () => this.clearPaths());

        // Animation controls
        document.getElementById('start-race').addEventListener('click', () => this.startRace());
        document.getElementById('stop-animation').addEventListener('click', () => this.stopAnimation());
    }

    getCellFromMouse(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / this.cellSize);
        const y = Math.floor((e.clientY - rect.top) / this.cellSize);
        return { x, y };
    }

    handleMouseDown(e) {
        this.isDrawing = true;
        this.handleCellInteraction(e);
    }

    handleMouseMove(e) {
        if (this.isDrawing) {
            this.handleCellInteraction(e);
        }
    }

    handleMouseUp() {
        this.isDrawing = false;
    }

    handleCellInteraction(e) {
        if (this.isAnimating) return;

        const { x, y } = this.getCellFromMouse(e);
        if (x < 0 || x >= this.gridSize || y < 0 || y >= this.gridSize) return;

        switch (this.currentMode) {
            case 'walls':
                if (this.grid[y][x].type === 'empty') {
                    this.grid[y][x].type = 'wall';
                } else if (this.grid[y][x].type === 'wall') {
                    this.grid[y][x].type = 'empty';
                }
                break;
            case 'start':
                if (this.grid[y][x].type !== 'wall') {
                    this.startPos = { x, y };
                }
                break;
            case 'end':
                if (this.grid[y][x].type !== 'wall') {
                    this.endPos = { x, y };
                }
                break;
        }

        this.render();
    }

    updateActiveAlgorithms() {
        this.activeAlgorithms.clear();
        document.querySelectorAll('input[name="algorithm"]:checked').forEach(input => {
            this.activeAlgorithms.add(input.value);
        });
    }

    updateSpeedDisplay() {
        const speedText = this.animationSpeed < 25 ? 'Slow' :
                         this.animationSpeed < 75 ? 'Medium' : 'Fast';
        document.getElementById('speed-value').textContent = speedText;
    }

    clearGrid() {
        this.grid = this.initializeGrid();
        this.algorithmResults.clear();
        this.updateStatsDisplay();
        this.render();
    }

    clearPaths() {
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                this.grid[y][x].algorithmStates.clear();
            }
        }
        this.algorithmResults.clear();
        this.updateStatsDisplay();
        this.render();
    }

    generateRandomMaze() {
        this.clearGrid();

        // Generate random walls (about 30% of the grid)
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                if (Math.random() < 0.3) {
                    this.grid[y][x].type = 'wall';
                }
            }
        }

        // Ensure start and end are not walls
        this.grid[this.startPos.y][this.startPos.x].type = 'empty';
        this.grid[this.endPos.y][this.endPos.x].type = 'empty';

        this.render();
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid lines
        this.ctx.strokeStyle = '#e2e8f0';
        this.ctx.lineWidth = 1;

        for (let i = 0; i <= this.gridSize; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.cellSize, 0);
            this.ctx.lineTo(i * this.cellSize, this.canvas.height);
            this.ctx.stroke();

            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.cellSize);
            this.ctx.lineTo(this.canvas.width, i * this.cellSize);
            this.ctx.stroke();
        }

        // Draw cells
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                const cell = this.grid[y][x];

                // Draw base cell type
                if (cell.type === 'wall') {
                    this.ctx.fillStyle = '#2d3748';
                    this.ctx.fillRect(x * this.cellSize + 1, y * this.cellSize + 1,
                                    this.cellSize - 2, this.cellSize - 2);
                }

                // Draw algorithm-specific states
                const activeStates = Array.from(cell.algorithmStates.entries())
                    .filter(([alg, _]) => this.activeAlgorithms.has(alg));

                if (activeStates.length > 0) {
                    // If multiple algorithms, divide the cell
                    if (activeStates.length === 1) {
                        const [algorithm, state] = activeStates[0];
                        this.drawCellState(x, y, algorithm, state);
                    } else {
                        this.drawMultiAlgorithmCell(x, y, activeStates);
                    }
                }

                // Draw start and end positions
                if (x === this.startPos.x && y === this.startPos.y) {
                    this.ctx.fillStyle = '#48bb78';
                    this.ctx.fillRect(x * this.cellSize + 2, y * this.cellSize + 2,
                                    this.cellSize - 4, this.cellSize - 4);
                    this.ctx.fillStyle = 'white';
                    this.ctx.font = '12px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.fillText('S', (x + 0.5) * this.cellSize, (y + 0.6) * this.cellSize);
                }

                if (x === this.endPos.x && y === this.endPos.y) {
                    this.ctx.fillStyle = '#ed8936';
                    this.ctx.fillRect(x * this.cellSize + 2, y * this.cellSize + 2,
                                    this.cellSize - 4, this.cellSize - 4);
                    this.ctx.fillStyle = 'white';
                    this.ctx.font = '12px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.fillText('E', (x + 0.5) * this.cellSize, (y + 0.6) * this.cellSize);
                }
            }
        }
    }

    drawCellState(x, y, algorithm, state) {
        const colors = this.algorithmColors[algorithm];
        let color = colors.explored;

        if (state === 'path') color = colors.path;
        else if (state === 'current') color = colors.current;

        this.ctx.fillStyle = color;
        this.ctx.fillRect(x * this.cellSize + 1, y * this.cellSize + 1,
                         this.cellSize - 2, this.cellSize - 2);
    }

    drawMultiAlgorithmCell(x, y, algorithmStates) {
        const numAlgorithms = algorithmStates.length;
        const cellWidth = (this.cellSize - 2) / numAlgorithms;

        algorithmStates.forEach(([algorithm, state], index) => {
            const colors = this.algorithmColors[algorithm];
            let color = colors.explored;

            if (state === 'path') color = colors.path;
            else if (state === 'current') color = colors.current;

            this.ctx.fillStyle = color;
            this.ctx.fillRect(x * this.cellSize + 1 + index * cellWidth, y * this.cellSize + 1,
                             cellWidth, this.cellSize - 2);
        });
    }

    async startRace() {
        if (this.isAnimating || this.activeAlgorithms.size === 0) return;

        this.clearPaths();
        this.isAnimating = true;

        // Update UI
        document.getElementById('start-race').disabled = true;
        document.getElementById('stop-animation').disabled = false;

        // Start all selected algorithms concurrently
        const algorithmPromises = Array.from(this.activeAlgorithms).map(algorithm =>
            this.runAlgorithmVisualization(algorithm)
        );

        try {
            await Promise.all(algorithmPromises);
        } catch (error) {
            console.error('Animation error:', error);
        } finally {
            this.stopAnimation();
        }
    }

    stopAnimation() {
        this.isAnimating = false;
        document.getElementById('start-race').disabled = false;
        document.getElementById('stop-animation').disabled = true;
    }

    async runAlgorithmVisualization(algorithmName) {
        // Check if the algorithm implementation exists
        if (!window.pathfindingAlgorithms || !window.pathfindingAlgorithms[algorithmName]) {
            console.error(`Algorithm ${algorithmName} not found!`);
            return;
        }

        const startTime = performance.now();

        try {
            // Call Dave's algorithm implementation
            const result = await window.pathfindingAlgorithms[algorithmName](this, algorithmName);

            const endTime = performance.now();

            // Store results
            this.algorithmResults.set(algorithmName, {
                nodesExplored: result.nodesExplored,
                pathLength: result.path ? result.path.length : 0,
                executionTime: Math.round(endTime - startTime),
                completed: result.success
            });

            this.updateStatsDisplay();
            this.render(); // Final render to show completed state

        } catch (error) {
            console.error(`Error running algorithm ${algorithmName}:`, error);
        }
    }

    updateStatsDisplay() {
        const statsContainer = document.getElementById('algorithm-stats');
        statsContainer.innerHTML = '';

        this.algorithmResults.forEach((result, algorithmName) => {
            const statCard = document.createElement('div');
            statCard.className = `stat-card ${algorithmName}`;

            statCard.innerHTML = `
                <h4>${algorithmName.toUpperCase()}</h4>
                <div class="stat-metrics">
                    <div class="metric">
                        <span class="metric-value">${result.nodesExplored}</span>
                        <span class="metric-label">Nodes</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${result.pathLength}</span>
                        <span class="metric-label">Path Length</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${result.executionTime}ms</span>
                        <span class="metric-label">Time</span>
                    </div>
                </div>
            `;

            statsContainer.appendChild(statCard);
        });
    }

    // Interface methods that Dave's algorithms will use
    markCellAsExplored(x, y, algorithm) {
        if (this.grid[y] && this.grid[y][x]) {
            this.grid[y][x].algorithmStates.set(algorithm, 'explored');
        }
    }

    markCellAsCurrent(x, y, algorithm) {
        if (this.grid[y] && this.grid[y][x]) {
            this.grid[y][x].algorithmStates.set(algorithm, 'current');
        }
    }

    markCellAsPath(x, y, algorithm) {
        if (this.grid[y] && this.grid[y][x]) {
            this.grid[y][x].algorithmStates.set(algorithm, 'path');
        }
    }

    isValidCell(x, y) {
        return x >= 0 && x < this.gridSize && y >= 0 && y < this.gridSize &&
               this.grid[y][x].type !== 'wall';
    }

    getGridSize() {
        return { width: this.gridSize, height: this.gridSize };
    }

    getStartPosition() {
        return { ...this.startPos };
    }

    getEndPosition() {
        return { ...this.endPos };
    }

    getAnimationSpeed() {
        // Convert slider value (1-100) to delay in milliseconds (100-1ms)
        return 101 - this.animationSpeed;
    }

    // Add width and height properties for algorithm compatibility
    get width() {
        return this.gridSize;
    }

    get height() {
        return this.gridSize;
    }
}