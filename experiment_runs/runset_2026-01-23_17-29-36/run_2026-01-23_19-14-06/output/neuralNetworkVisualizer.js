/**
 * Neural Network Visualizer - Interactive Canvas Visualization
 * Makes neural networks transparent through step-by-step animation
 * Created by Alice & Bob collaboration
 */

class NeuralNetworkVisualizer {
    constructor(canvasId, network) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.network = network;

        // Visualization parameters
        this.nodeRadius = 25;
        this.layerSpacing = 150;
        this.nodeSpacing = 80;
        this.animationSpeed = 1000; // milliseconds per step

        // Animation state
        this.isAnimating = false;
        this.currentAnimationStep = 0;
        this.animationTimer = null;

        // Color scheme
        this.colors = {
            node: '#e3f2fd',
            activeNode: '#2196f3',
            positiveWeight: '#4caf50',
            negativeWeight: '#f44336',
            text: '#333',
            connection: '#bbb',
            activeConnection: '#ff9800',
            gradient: '#9c27b0'
        };

        // Calculate layout
        this.calculateLayout();
        this.render();
    }

    /**
     * Calculate node positions for the network architecture
     */
    calculateLayout() {
        this.nodePositions = [];
        const architecture = this.network.architecture;

        // Calculate canvas dimensions
        const maxNodesInLayer = Math.max(...architecture);
        const totalWidth = (architecture.length - 1) * this.layerSpacing + 100;
        const totalHeight = maxNodesInLayer * this.nodeSpacing + 100;

        this.canvas.width = totalWidth;
        this.canvas.height = totalHeight;

        // Position nodes for each layer
        for (let layer = 0; layer < architecture.length; layer++) {
            const nodesInLayer = architecture[layer];
            const layerX = 50 + layer * this.layerSpacing;

            // Center nodes vertically
            const startY = (totalHeight - (nodesInLayer - 1) * this.nodeSpacing) / 2;

            const layerPositions = [];
            for (let node = 0; node < nodesInLayer; node++) {
                const nodeY = startY + node * this.nodeSpacing;
                layerPositions.push({ x: layerX, y: nodeY });
            }

            this.nodePositions.push(layerPositions);
        }
    }

    /**
     * Render the complete network
     */
    render(highlightStep = null) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw connections first (behind nodes)
        this.drawConnections(highlightStep);

        // Draw nodes
        this.drawNodes(highlightStep);

        // Draw layer labels
        this.drawLabels();

        // Draw step information
        if (highlightStep) {
            this.drawStepInfo(highlightStep);
        }
    }

    /**
     * Draw all connections between layers
     */
    drawConnections(highlightStep) {
        for (let layer = 0; layer < this.network.layers; layer++) {
            const fromLayer = this.nodePositions[layer];
            const toLayer = this.nodePositions[layer + 1];

            for (let fromNode = 0; fromNode < fromLayer.length; fromNode++) {
                for (let toNode = 0; toNode < toLayer.length; toNode++) {
                    const weight = this.network.weights[layer][toNode][fromNode];

                    // Highlight active connection during animation
                    const isActive = highlightStep &&
                        highlightStep.type === 'neuron_activation' &&
                        highlightStep.layer === layer + 1 &&
                        highlightStep.neuron === toNode;

                    this.drawConnection(
                        fromLayer[fromNode],
                        toLayer[toNode],
                        weight,
                        isActive
                    );
                }
            }
        }
    }

    /**
     * Draw a single connection with weight visualization
     */
    drawConnection(from, to, weight, isActive = false) {
        this.ctx.beginPath();
        this.ctx.moveTo(from.x, from.y);
        this.ctx.lineTo(to.x, to.y);

        // Line thickness based on weight magnitude
        const thickness = Math.abs(weight) * 3 + 0.5;
        this.ctx.lineWidth = isActive ? thickness * 2 : thickness;

        // Color based on weight sign and activity
        if (isActive) {
            this.ctx.strokeStyle = this.colors.activeConnection;
        } else {
            this.ctx.strokeStyle = weight >= 0 ? this.colors.positiveWeight : this.colors.negativeWeight;
            this.ctx.globalAlpha = 0.6;
        }

        this.ctx.stroke();
        this.ctx.globalAlpha = 1;

        // Draw weight value on active connections
        if (isActive) {
            const midX = (from.x + to.x) / 2;
            const midY = (from.y + to.y) / 2;
            this.drawText(weight.toFixed(2), midX, midY - 10, '12px', this.colors.text);
        }
    }

    /**
     * Draw all nodes with activation visualization
     */
    drawNodes(highlightStep) {
        for (let layer = 0; layer < this.nodePositions.length; layer++) {
            const positions = this.nodePositions[layer];

            for (let node = 0; node < positions.length; node++) {
                const pos = positions[node];

                // Get activation value if available
                let activation = 0;
                if (this.network.activations && this.network.activations[layer]) {
                    activation = this.network.activations[layer][node];
                }

                // Highlight active node during animation
                const isActive = highlightStep &&
                    highlightStep.type === 'neuron_activation' &&
                    highlightStep.layer === layer &&
                    highlightStep.neuron === node;

                this.drawNode(pos, activation, isActive, layer === 0 ? 'input' :
                              layer === this.nodePositions.length - 1 ? 'output' : 'hidden');
            }
        }
    }

    /**
     * Draw a single node with activation visualization
     */
    drawNode(position, activation, isActive = false, type = 'hidden') {
        // Node circle
        this.ctx.beginPath();
        this.ctx.arc(position.x, position.y, this.nodeRadius, 0, 2 * Math.PI);

        // Color based on activation and state
        if (isActive) {
            this.ctx.fillStyle = this.colors.activeNode;
        } else {
            // Color intensity based on activation
            const intensity = Math.max(0, Math.min(1, activation));
            const alpha = 0.2 + intensity * 0.8;
            this.ctx.fillStyle = `rgba(33, 150, 243, ${alpha})`;
        }

        this.ctx.fill();

        // Border
        this.ctx.strokeStyle = isActive ? this.colors.activeNode : '#ddd';
        this.ctx.lineWidth = isActive ? 3 : 1;
        this.ctx.stroke();

        // Activation value text
        this.drawText(
            activation.toFixed(2),
            position.x,
            position.y,
            isActive ? '14px' : '12px',
            this.colors.text
        );

        // Node type indicator
        if (type === 'input') {
            this.drawText('I', position.x, position.y - this.nodeRadius - 15, '10px', this.colors.text);
        } else if (type === 'output') {
            this.drawText('O', position.x, position.y - this.nodeRadius - 15, '10px', this.colors.text);
        }
    }

    /**
     * Draw layer labels
     */
    drawLabels() {
        for (let layer = 0; layer < this.nodePositions.length; layer++) {
            const x = this.nodePositions[layer][0].x;
            const y = 20;

            let label;
            if (layer === 0) {
                label = 'Input Layer';
            } else if (layer === this.nodePositions.length - 1) {
                label = 'Output Layer';
            } else {
                label = `Hidden Layer ${layer}`;
            }

            this.drawText(label, x, y, '14px', this.colors.text, 'center');
        }
    }

    /**
     * Draw current step information
     */
    drawStepInfo(step) {
        if (!step) return;

        const infoX = this.canvas.width - 200;
        const infoY = 50;

        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        this.ctx.fillRect(infoX - 10, infoY - 10, 190, 120);
        this.ctx.strokeStyle = this.colors.text;
        this.ctx.strokeRect(infoX - 10, infoY - 10, 190, 120);

        let y = infoY;
        this.drawText('Current Step:', infoX, y, '12px', this.colors.text, 'left');
        y += 20;

        if (step.type === 'neuron_activation') {
            this.drawText(`Layer ${step.layer}, Neuron ${step.neuron}`, infoX, y, '11px', this.colors.text, 'left');
            y += 15;
            this.drawText(`Pre-activation: ${step.preActivation.toFixed(3)}`, infoX, y, '10px', this.colors.text, 'left');
            y += 15;
            this.drawText(`Activation: ${step.activation.toFixed(3)}`, infoX, y, '10px', this.colors.text, 'left');
            y += 15;
            this.drawText(`Bias: ${step.bias.toFixed(3)}`, infoX, y, '10px', this.colors.text, 'left');
        }
    }

    /**
     * Helper method to draw text
     */
    drawText(text, x, y, fontSize = '12px', color = '#333', align = 'center') {
        this.ctx.fillStyle = color;
        this.ctx.font = `${fontSize} Arial`;
        this.ctx.textAlign = align;
        this.ctx.fillText(text, x, y);
    }

    /**
     * Start step-by-step animation
     */
    startAnimation() {
        if (this.isAnimating || !this.network.animationSteps.length) return;

        this.isAnimating = true;
        this.currentAnimationStep = 0;
        this.animateNextStep();
    }

    /**
     * Animate the next step
     */
    animateNextStep() {
        if (this.currentAnimationStep >= this.network.animationSteps.length) {
            this.stopAnimation();
            return;
        }

        const step = this.network.animationSteps[this.currentAnimationStep];
        this.render(step);

        this.currentAnimationStep++;
        this.animationTimer = setTimeout(() => this.animateNextStep(), this.animationSpeed);
    }

    /**
     * Stop animation
     */
    stopAnimation() {
        this.isAnimating = false;
        if (this.animationTimer) {
            clearTimeout(this.animationTimer);
            this.animationTimer = null;
        }
        this.render(); // Final render without highlights
    }

    /**
     * Step through animation manually
     */
    stepForward() {
        if (this.currentAnimationStep < this.network.animationSteps.length) {
            const step = this.network.animationSteps[this.currentAnimationStep];
            this.render(step);
            this.currentAnimationStep++;
        }
    }

    stepBackward() {
        if (this.currentAnimationStep > 0) {
            this.currentAnimationStep--;
            const step = this.network.animationSteps[this.currentAnimationStep];
            this.render(step);
        }
    }

    /**
     * Reset animation
     */
    resetAnimation() {
        this.stopAnimation();
        this.currentAnimationStep = 0;
        this.render();
    }

    /**
     * Set animation speed
     */
    setAnimationSpeed(speed) {
        this.animationSpeed = Math.max(100, Math.min(5000, speed));
    }

    /**
     * Update with new network state
     */
    updateNetwork(network) {
        this.network = network;
        this.calculateLayout();
        this.render();
    }
}

// Export for both Node.js and browser environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NeuralNetworkVisualizer };
} else if (typeof window !== 'undefined') {
    window.NeuralNetworkVisualizer = NeuralNetworkVisualizer;
}