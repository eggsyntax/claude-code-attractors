/**
 * Visualization Engine for Cellular Automata Explorer
 * Handles canvas rendering, color schemes, and visual effects
 */

class VisualizationEngine {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.cellSize = 8;
        this.gridWidth = 0;
        this.gridHeight = 0;
        this.showGrid = false;
        this.trailEffect = false;
        this.currentColorScheme = 'classic';
        this.colorSchemes = this.initColorSchemes();

        this.setupCanvas();
    }

    initColorSchemes() {
        return {
            classic: {
                dead: '#ffffff',
                alive: '#000000',
                background: '#f8f9fa'
            },
            heatmap: {
                dead: '#1a1a2e',
                alive: '#ff6b6b',
                intermediate: ['#16213e', '#0f3460', '#e94560', '#f16866'],
                background: '#1a1a2e'
            },
            ocean: {
                dead: '#003554',
                alive: '#51c4d3',
                intermediate: ['#006494', '#0582ca', '#00a6fb'],
                background: '#001d3d'
            },
            forest: {
                dead: '#2d5016',
                alive: '#83c239',
                intermediate: ['#3d6020', '#4d7c2a', '#6aa237'],
                background: '#1a2e0a'
            }
        };
    }

    setupCanvas() {
        const container = this.canvas.parentElement;
        const maxWidth = container.clientWidth - 40;
        const maxHeight = window.innerHeight * 0.6;

        // Calculate optimal cell size and grid dimensions
        this.cellSize = Math.max(4, Math.min(12, Math.floor(maxWidth / 80)));
        this.gridWidth = Math.floor(maxWidth / this.cellSize);
        this.gridHeight = Math.floor(maxHeight / this.cellSize);

        this.canvas.width = this.gridWidth * this.cellSize;
        this.canvas.height = this.gridHeight * this.cellSize;

        // Set up smooth rendering
        this.ctx.imageSmoothingEnabled = false;

        console.log(`Canvas initialized: ${this.gridWidth}x${this.gridHeight} grid, ${this.cellSize}px cells`);
    }

    setColorScheme(schemeName) {
        if (this.colorSchemes[schemeName]) {
            this.currentColorScheme = schemeName;
            this.clearCanvas();
        }
    }

    setShowGrid(show) {
        this.showGrid = show;
    }

    setTrailEffect(enabled) {
        this.trailEffect = enabled;
    }

    clearCanvas() {
        const scheme = this.colorSchemes[this.currentColorScheme];
        this.ctx.fillStyle = scheme.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    renderGrid(automataGrid, generation = 0) {
        if (!automataGrid) return;

        const scheme = this.colorSchemes[this.currentColorScheme];

        // Apply trail effect by partially clearing instead of full clear
        if (this.trailEffect) {
            this.ctx.fillStyle = scheme.background + '20'; // Semi-transparent
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        } else {
            this.clearCanvas();
        }

        // Render cells
        for (let x = 0; x < this.gridWidth && x < automataGrid.length; x++) {
            for (let y = 0; y < this.gridHeight && y < automataGrid[0].length; y++) {
                const cellState = automataGrid[x][y];
                this.renderCell(x, y, cellState, generation);
            }
        }

        // Render grid lines if enabled
        if (this.showGrid) {
            this.renderGridLines();
        }
    }

    renderCell(x, y, state, generation = 0) {
        const scheme = this.colorSchemes[this.currentColorScheme];
        const pixelX = x * this.cellSize;
        const pixelY = y * this.cellSize;

        let color;
        if (state === 0) {
            color = scheme.dead;
        } else if (state === 1) {
            color = scheme.alive;
        } else {
            // Handle multi-state automata (like Brian's Brain)
            if (scheme.intermediate && state < scheme.intermediate.length + 2) {
                color = scheme.intermediate[state - 2] || scheme.alive;
            } else {
                color = scheme.alive;
            }
        }

        // Add subtle generation-based color variation for heat effect
        if (this.currentColorScheme === 'heatmap' && state > 0) {
            const intensity = Math.min(1, generation / 100);
            color = this.interpolateColor(scheme.alive, '#ffffff', intensity * 0.3);
        }

        this.ctx.fillStyle = color;
        this.ctx.fillRect(pixelX, pixelY, this.cellSize, this.cellSize);
    }

    renderGridLines() {
        this.ctx.strokeStyle = 'rgba(100, 100, 100, 0.3)';
        this.ctx.lineWidth = 0.5;

        // Vertical lines
        for (let x = 0; x <= this.gridWidth; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.cellSize, 0);
            this.ctx.lineTo(x * this.cellSize, this.canvas.height);
            this.ctx.stroke();
        }

        // Horizontal lines
        for (let y = 0; y <= this.gridHeight; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.cellSize);
            this.ctx.lineTo(this.canvas.width, y * this.cellSize);
            this.ctx.stroke();
        }
    }

    // Utility function to interpolate between two colors
    interpolateColor(color1, color2, factor) {
        const hex1 = color1.replace('#', '');
        const hex2 = color2.replace('#', '');

        const r1 = parseInt(hex1.substr(0, 2), 16);
        const g1 = parseInt(hex1.substr(2, 2), 16);
        const b1 = parseInt(hex1.substr(4, 2), 16);

        const r2 = parseInt(hex2.substr(0, 2), 16);
        const g2 = parseInt(hex2.substr(2, 2), 16);
        const b2 = parseInt(hex2.substr(4, 2), 16);

        const r = Math.round(r1 + factor * (r2 - r1));
        const g = Math.round(g1 + factor * (g2 - g1));
        const b = Math.round(b1 + factor * (b2 - b1));

        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    // Convert canvas coordinates to grid coordinates
    canvasToGrid(canvasX, canvasY) {
        return {
            x: Math.floor(canvasX / this.cellSize),
            y: Math.floor(canvasY / this.cellSize)
        };
    }

    // Get canvas dimensions info
    getDimensions() {
        return {
            gridWidth: this.gridWidth,
            gridHeight: this.gridHeight,
            cellSize: this.cellSize,
            canvasWidth: this.canvas.width,
            canvasHeight: this.canvas.height
        };
    }

    // Animation helpers for smooth transitions
    animateColorSchemeChange(newScheme, duration = 500) {
        // Could implement smooth color transitions here
        this.setColorScheme(newScheme);
    }

    // Export current canvas as image
    exportAsImage() {
        return this.canvas.toDataURL('image/png');
    }

    // Resize handler for responsive design
    handleResize() {
        this.setupCanvas();
        return this.getDimensions();
    }
}