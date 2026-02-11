/**
 * UI Controls Manager for Cellular Automata Explorer
 * Handles all user interface interactions and controls
 */

class UIControls {
    constructor(visualizationEngine, automataEngine) {
        this.viz = visualizationEngine;
        this.engine = automataEngine;
        this.isPlaying = false;
        this.simulationSpeed = 10; // fps
        this.animationId = null;
        this.lastFrameTime = 0;
        this.generation = 0;
        this.isDrawing = false;
        this.drawState = 1; // What state to draw (1 = alive)

        this.initializeControls();
        this.bindEvents();
    }

    initializeControls() {
        // Get all control elements
        this.elements = {
            playPause: document.getElementById('play-pause'),
            step: document.getElementById('step'),
            reset: document.getElementById('reset'),
            clear: document.getElementById('clear'),
            ruleSelector: document.getElementById('rule-selector'),
            parameterControls: document.getElementById('parameter-controls'),
            speedSlider: document.getElementById('speed-slider'),
            speedDisplay: document.getElementById('speed-display'),
            colorScheme: document.getElementById('color-scheme'),
            showGrid: document.getElementById('show-grid'),
            trailEffect: document.getElementById('trail-effect'),
            generationCount: document.getElementById('generation-count'),
            populationCount: document.getElementById('population-count'),
            density: document.getElementById('density'),
            randomSeed: document.getElementById('random-seed'),
            glider: document.getElementById('glider'),
            oscillator: document.getElementById('oscillator'),
            canvas: document.getElementById('automata-canvas')
        };

        // Initialize control states
        this.updateSpeedDisplay();
        this.updateStats();
    }

    bindEvents() {
        // Simulation controls
        this.elements.playPause.addEventListener('click', () => this.togglePlayPause());
        this.elements.step.addEventListener('click', () => this.stepSimulation());
        this.elements.reset.addEventListener('click', () => this.resetSimulation());
        this.elements.clear.addEventListener('click', () => this.clearGrid());

        // Rule system selection
        this.elements.ruleSelector.addEventListener('change', (e) => {
            this.onRuleSystemChange(e.target.value);
        });

        // Speed control
        this.elements.speedSlider.addEventListener('input', (e) => {
            this.simulationSpeed = parseInt(e.target.value);
            this.updateSpeedDisplay();
        });

        // Visualization controls
        this.elements.colorScheme.addEventListener('change', (e) => {
            this.viz.setColorScheme(e.target.value);
            this.renderCurrentState();
        });

        this.elements.showGrid.addEventListener('change', (e) => {
            this.viz.setShowGrid(e.target.checked);
            this.renderCurrentState();
        });

        this.elements.trailEffect.addEventListener('change', (e) => {
            this.viz.setTrailEffect(e.target.checked);
        });

        // Pattern insertion
        this.elements.randomSeed.addEventListener('click', () => this.insertRandomPattern());
        this.elements.glider.addEventListener('click', () => this.insertGlider());
        this.elements.oscillator.addEventListener('click', () => this.insertOscillator());

        // Canvas interaction
        this.bindCanvasEvents();

        // Keyboard shortcuts
        this.bindKeyboardShortcuts();

        // Window resize handling
        window.addEventListener('resize', () => this.handleResize());
    }

    bindCanvasEvents() {
        const canvas = this.elements.canvas;

        // Mouse drawing
        canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        canvas.addEventListener('mousemove', (e) => this.continueDrawing(e));
        canvas.addEventListener('mouseup', () => this.stopDrawing());
        canvas.addEventListener('mouseleave', () => this.stopDrawing());

        // Touch support for mobile
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            canvas.dispatchEvent(mouseEvent);
        });

        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            canvas.dispatchEvent(mouseEvent);
        });

        canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            const mouseEvent = new MouseEvent('mouseup', {});
            canvas.dispatchEvent(mouseEvent);
        });

        // Right-click context menu for erase mode
        canvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            return false;
        });
    }

    bindKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            switch(e.code) {
                case 'Space':
                    e.preventDefault();
                    this.togglePlayPause();
                    break;
                case 'ArrowRight':
                    if (!this.isPlaying) {
                        this.stepSimulation();
                    }
                    break;
                case 'KeyR':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.resetSimulation();
                    }
                    break;
                case 'KeyC':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.clearGrid();
                    }
                    break;
                case 'KeyG':
                    this.elements.showGrid.checked = !this.elements.showGrid.checked;
                    this.viz.setShowGrid(this.elements.showGrid.checked);
                    this.renderCurrentState();
                    break;
            }
        });
    }

    startDrawing(e) {
        this.isDrawing = true;

        // Determine draw state based on mouse button
        if (e.button === 2) { // Right click = erase
            this.drawState = 0;
        } else { // Left click = draw alive cells
            this.drawState = 1;
        }

        this.drawAtPosition(e);
    }

    continueDrawing(e) {
        if (this.isDrawing) {
            this.drawAtPosition(e);
        }
    }

    stopDrawing() {
        this.isDrawing = false;
    }

    drawAtPosition(e) {
        const rect = this.elements.canvas.getBoundingClientRect();
        const canvasX = e.clientX - rect.left;
        const canvasY = e.clientY - rect.top;

        const gridPos = this.viz.canvasToGrid(canvasX, canvasY);

        if (this.engine && gridPos.x >= 0 && gridPos.y >= 0) {
            const dims = this.viz.getDimensions();
            if (gridPos.x < dims.gridWidth && gridPos.y < dims.gridHeight) {
                this.engine.setCell(gridPos.x, gridPos.y, this.drawState);
                this.renderCurrentState();
                this.updateStats();
            }
        }
    }

    togglePlayPause() {
        this.isPlaying = !this.isPlaying;

        if (this.isPlaying) {
            this.elements.playPause.textContent = 'Pause';
            this.elements.playPause.classList.add('active');
            this.elements.canvas.classList.add('playing');
            this.startAnimation();
        } else {
            this.elements.playPause.textContent = 'Play';
            this.elements.playPause.classList.remove('active');
            this.elements.canvas.classList.remove('playing');
            this.stopAnimation();
        }
    }

    stepSimulation() {
        if (this.engine) {
            this.engine.step();
            this.generation++;
            this.renderCurrentState();
            this.updateStats();
        }
    }

    resetSimulation() {
        this.generation = 0;
        if (this.engine) {
            this.engine.reset();
            this.renderCurrentState();
        }
        this.updateStats();

        if (this.isPlaying) {
            this.togglePlayPause();
        }
    }

    clearGrid() {
        this.generation = 0;
        if (this.engine) {
            this.engine.clear();
            this.renderCurrentState();
        }
        this.updateStats();
    }

    startAnimation() {
        const frameInterval = 1000 / this.simulationSpeed;

        const animate = (currentTime) => {
            if (!this.isPlaying) return;

            if (currentTime - this.lastFrameTime >= frameInterval) {
                this.stepSimulation();
                this.lastFrameTime = currentTime;
            }

            this.animationId = requestAnimationFrame(animate);
        };

        this.animationId = requestAnimationFrame(animate);
    }

    stopAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    updateSpeedDisplay() {
        this.elements.speedDisplay.textContent = `${this.simulationSpeed} fps`;
    }

    updateStats() {
        this.elements.generationCount.textContent = this.generation;

        if (this.engine) {
            const population = this.engine.getPopulation();
            const dims = this.viz.getDimensions();
            const totalCells = dims.gridWidth * dims.gridHeight;
            const density = totalCells > 0 ? ((population / totalCells) * 100).toFixed(1) : 0;

            this.elements.populationCount.textContent = population;
            this.elements.density.textContent = `${density}%`;
        }
    }

    renderCurrentState() {
        if (this.engine && this.viz) {
            const grid = this.engine.getGrid();
            this.viz.renderGrid(grid, this.generation);
        }
    }

    onRuleSystemChange(ruleSystemName) {
        // This will be connected to the engine when Alice implements it
        console.log(`Rule system changed to: ${ruleSystemName}`);

        // Clear parameter controls and rebuild them based on new rule system
        this.updateParameterControls(ruleSystemName);

        // Reset simulation when rule changes
        this.resetSimulation();
    }

    updateParameterControls(ruleSystemName) {
        const container = this.elements.parameterControls;
        container.innerHTML = '';

        // This will be populated based on the rule system's parameters
        // For now, show a placeholder
        const placeholder = document.createElement('div');
        placeholder.textContent = `Parameters for ${ruleSystemName} will appear here`;
        placeholder.style.fontStyle = 'italic';
        placeholder.style.color = '#666';
        container.appendChild(placeholder);
    }

    insertRandomPattern() {
        if (this.engine) {
            const dims = this.viz.getDimensions();
            const density = 0.3; // 30% of cells alive

            for (let x = 0; x < dims.gridWidth; x++) {
                for (let y = 0; y < dims.gridHeight; y++) {
                    if (Math.random() < density) {
                        this.engine.setCell(x, y, 1);
                    }
                }
            }

            this.renderCurrentState();
            this.updateStats();
        }
    }

    insertGlider() {
        if (this.engine) {
            const dims = this.viz.getDimensions();
            const centerX = Math.floor(dims.gridWidth / 2);
            const centerY = Math.floor(dims.gridHeight / 2);

            // Classic glider pattern
            const glider = [
                [0, 1, 0],
                [0, 0, 1],
                [1, 1, 1]
            ];

            for (let dx = 0; dx < glider.length; dx++) {
                for (let dy = 0; dy < glider[dx].length; dy++) {
                    const x = centerX + dx - 1;
                    const y = centerY + dy - 1;
                    if (x >= 0 && x < dims.gridWidth && y >= 0 && y < dims.gridHeight) {
                        this.engine.setCell(x, y, glider[dx][dy]);
                    }
                }
            }

            this.renderCurrentState();
            this.updateStats();
        }
    }

    insertOscillator() {
        if (this.engine) {
            const dims = this.viz.getDimensions();
            const centerX = Math.floor(dims.gridWidth / 2);
            const centerY = Math.floor(dims.gridHeight / 2);

            // Blinker pattern (simple oscillator)
            for (let i = -1; i <= 1; i++) {
                const x = centerX + i;
                const y = centerY;
                if (x >= 0 && x < dims.gridWidth && y >= 0 && y < dims.gridHeight) {
                    this.engine.setCell(x, y, 1);
                }
            }

            this.renderCurrentState();
            this.updateStats();
        }
    }

    handleResize() {
        const newDims = this.viz.handleResize();
        // Notify engine of new dimensions if needed
        if (this.engine && this.engine.resize) {
            this.engine.resize(newDims.gridWidth, newDims.gridHeight);
        }
        this.renderCurrentState();
    }

    // Method to connect the automata engine (called from main.js)
    setEngine(engine) {
        this.engine = engine;
        this.renderCurrentState();
        this.updateStats();
    }
}