/**
 * Interactive Grid System for Algorithm Visualization
 * Handles canvas drawing, user interactions, and grid state management
 */

class InteractiveGrid {
    constructor(canvasId, width = 600, height = 600, gridSize = 30) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = width;
        this.height = height;
        this.gridSize = gridSize;
        this.cellSize = Math.min(width / gridSize, height / gridSize);

        // Grid state
        this.grid = [];
        this.startPoint = null;
        this.endPoint = null;
        this.obstacles = new Set();

        // Drawing state
        this.isDrawing = false;
        this.drawMode = 'obstacle'; // 'obstacle', 'clear'

        // Visualization state
        this.openSet = new Set();
        this.closedSet = new Set();
        this.currentNode = null;
        this.pathNodes = new Set();

        this.initializeGrid();
        this.setupEventListeners();
        this.draw();
    }

    /**
     * Initialize empty grid
     */
    initializeGrid() {
        for (let row = 0; row < this.gridSize; row++) {
            this.grid[row] = [];
            for (let col = 0; col < this.gridSize; col++) {
                this.grid[row][col] = 'empty';
            }
        }
    }

    /**
     * Setup mouse event listeners for interactive drawing
     */
    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.handleMouseUp());
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
        this.canvas.addEventListener('mouseleave', () => this.handleMouseUp());
    }

    /**
     * Get grid coordinates from mouse position
     */
    getGridCoordinates(mouseX, mouseY) {
        const rect = this.canvas.getBoundingClientRect();
        const x = mouseX - rect.left;
        const y = mouseY - rect.top;
        const col = Math.floor(x / this.cellSize);
        const row = Math.floor(y / this.cellSize);

        if (row >= 0 && row < this.gridSize && col >= 0 && col < this.gridSize) {
            return { row, col };
        }
        return null;
    }

    /**
     * Handle mouse down events
     */
    handleMouseDown(e) {
        const coords = this.getGridCoordinates(e.clientX, e.clientY);
        if (!coords) return;

        const { row, col } = coords;

        if (e.button === 0) { // Left click
            this.handleLeftClick(row, col);
        } else if (e.button === 2) { // Right click
            this.isDrawing = true;
            this.drawMode = 'obstacle';
            this.setObstacle(row, col);
        } else if (e.button === 1) { // Middle click
            e.preventDefault();
            this.clearCell(row, col);
        }
    }

    /**
     * Handle mouse move events for dragging
     */
    handleMouseMove(e) {
        if (this.isDrawing) {
            const coords = this.getGridCoordinates(e.clientX, e.clientY);
            if (!coords) return;

            const { row, col } = coords;
            if (this.drawMode === 'obstacle') {
                this.setObstacle(row, col);
            }
        }
    }

    /**
     * Handle mouse up events
     */
    handleMouseUp() {
        this.isDrawing = false;
    }

    /**
     * Handle left click - set start/end points
     */
    handleLeftClick(row, col) {
        // Clear any existing algorithm visualization
        this.clearVisualization();

        const cellKey = `${row},${col}`;

        // If clicking on an obstacle, clear it first
        if (this.obstacles.has(cellKey)) {
            this.obstacles.delete(cellKey);
            this.grid[row][col] = 'empty';
        }

        // Set start point if none exists
        if (!this.startPoint) {
            this.startPoint = { row, col };
            this.grid[row][col] = 'start';
        }
        // Set end point if start exists but end doesn't
        else if (!this.endPoint && !(row === this.startPoint.row && col === this.startPoint.col)) {
            this.endPoint = { row, col };
            this.grid[row][col] = 'end';
        }
        // Reset start/end points if both exist
        else {
            this.resetStartEnd();
            this.startPoint = { row, col };
            this.grid[row][col] = 'start';
        }

        this.draw();
    }

    /**
     * Set obstacle at position
     */
    setObstacle(row, col) {
        const cellKey = `${row},${col}`;

        // Don't place obstacles on start/end points
        if (this.startPoint && row === this.startPoint.row && col === this.startPoint.col) return;
        if (this.endPoint && row === this.endPoint.row && col === this.endPoint.col) return;

        this.obstacles.add(cellKey);
        this.grid[row][col] = 'obstacle';
        this.clearVisualization();
        this.draw();
    }

    /**
     * Clear cell at position
     */
    clearCell(row, col) {
        const cellKey = `${row},${col}`;

        // Clear start point
        if (this.startPoint && row === this.startPoint.row && col === this.startPoint.col) {
            this.startPoint = null;
        }

        // Clear end point
        if (this.endPoint && row === this.endPoint.row && col === this.endPoint.col) {
            this.endPoint = null;
        }

        // Clear obstacle
        this.obstacles.delete(cellKey);

        this.grid[row][col] = 'empty';
        this.clearVisualization();
        this.draw();
    }

    /**
     * Reset start and end points
     */
    resetStartEnd() {
        if (this.startPoint) {
            this.grid[this.startPoint.row][this.startPoint.col] = 'empty';
            this.startPoint = null;
        }
        if (this.endPoint) {
            this.grid[this.endPoint.row][this.endPoint.col] = 'empty';
            this.endPoint = null;
        }
    }

    /**
     * Clear visualization state (keep obstacles and start/end)
     */
    clearVisualization() {
        this.openSet.clear();
        this.closedSet.clear();
        this.currentNode = null;
        this.pathNodes.clear();
    }

    /**
     * Reset entire grid
     */
    reset() {
        this.initializeGrid();
        this.startPoint = null;
        this.endPoint = null;
        this.obstacles.clear();
        this.clearVisualization();
        this.draw();
    }

    /**
     * Update visualization state from algorithm step
     */
    updateVisualization(stepData) {
        this.clearVisualization();

        if (stepData.open_set) {
            stepData.open_set.forEach(pos => {
                this.openSet.add(`${pos.row},${pos.col}`);
            });
        }

        if (stepData.closed_set) {
            stepData.closed_set.forEach(pos => {
                this.closedSet.add(`${pos.row},${pos.col}`);
            });
        }

        if (stepData.current_node) {
            this.currentNode = stepData.current_node;
        }

        if (stepData.path) {
            stepData.path.forEach(pos => {
                this.pathNodes.add(`${pos.row},${pos.col}`);
            });
        }

        this.draw();
    }

    /**
     * Get current grid state for API
     */
    getGridState() {
        return {
            width: this.gridSize,
            height: this.gridSize,
            start: this.startPoint,
            end: this.endPoint,
            obstacles: Array.from(this.obstacles).map(key => {
                const [row, col] = key.split(',').map(Number);
                return { row, col };
            })
        };
    }

    /**
     * Main drawing function
     */
    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.width, this.height);

        // Draw grid lines
        this.drawGridLines();

        // Draw cells
        for (let row = 0; row < this.gridSize; row++) {
            for (let col = 0; col < this.gridSize; col++) {
                this.drawCell(row, col);
            }
        }
    }

    /**
     * Draw grid lines
     */
    drawGridLines() {
        this.ctx.strokeStyle = '#e0e0e0';
        this.ctx.lineWidth = 1;

        // Vertical lines
        for (let col = 0; col <= this.gridSize; col++) {
            const x = col * this.cellSize;
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.height);
            this.ctx.stroke();
        }

        // Horizontal lines
        for (let row = 0; row <= this.gridSize; row++) {
            const y = row * this.cellSize;
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.width, y);
            this.ctx.stroke();
        }
    }

    /**
     * Draw individual cell
     */
    drawCell(row, col) {
        const x = col * this.cellSize;
        const y = row * this.cellSize;
        const cellKey = `${row},${col}`;

        // Determine cell color based on state
        let fillColor = null;

        // Path has highest priority for visualization
        if (this.pathNodes.has(cellKey)) {
            fillColor = '#2196f3'; // Blue for path
        }
        // Current node being processed
        else if (this.currentNode && this.currentNode.row === row && this.currentNode.col === col) {
            fillColor = '#ff9800'; // Orange for current
        }
        // Closed set (already processed)
        else if (this.closedSet.has(cellKey)) {
            fillColor = '#e57373'; // Light red for closed
        }
        // Open set (to be processed)
        else if (this.openSet.has(cellKey)) {
            fillColor = '#81c784'; // Light green for open
        }
        // Static elements
        else if (this.startPoint && row === this.startPoint.row && col === this.startPoint.col) {
            fillColor = '#4caf50'; // Green for start
        }
        else if (this.endPoint && row === this.endPoint.row && col === this.endPoint.col) {
            fillColor = '#f44336'; // Red for end
        }
        else if (this.obstacles.has(cellKey)) {
            fillColor = '#424242'; // Dark gray for obstacles
        }

        // Draw cell if it has a color
        if (fillColor) {
            this.ctx.fillStyle = fillColor;
            this.ctx.fillRect(x + 1, y + 1, this.cellSize - 2, this.cellSize - 2);
        }

        // Draw cost information for current node (A* specific)
        if (this.currentNode && this.currentNode.row === row && this.currentNode.col === col &&
            this.currentNode.g_cost !== undefined) {
            this.drawCostInfo(x, y, this.currentNode);
        }
    }

    /**
     * Draw cost information in cell (for A* algorithm)
     */
    drawCostInfo(x, y, nodeInfo) {
        this.ctx.fillStyle = 'white';
        this.ctx.font = '10px Arial';
        this.ctx.textAlign = 'center';

        const centerX = x + this.cellSize / 2;
        const centerY = y + this.cellSize / 2;

        if (nodeInfo.f_cost !== undefined) {
            this.ctx.fillText(`F:${nodeInfo.f_cost}`, centerX, centerY - 5);
        }
        if (nodeInfo.g_cost !== undefined) {
            this.ctx.fillText(`G:${nodeInfo.g_cost}`, centerX - 7, centerY + 8);
        }
        if (nodeInfo.h_cost !== undefined) {
            this.ctx.fillText(`H:${nodeInfo.h_cost}`, centerX + 7, centerY + 8);
        }
    }
}