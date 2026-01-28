/**
 * Neural Network Visualizer - Core Implementation
 * Educational tool for understanding neural network operations
 * Created by Alice & Bob collaboration
 */

class NeuralNetwork {
    constructor(architecture = [2, 4, 3, 1]) {
        this.architecture = architecture; // [input_size, hidden1, hidden2, ..., output_size]
        this.layers = architecture.length - 1; // Number of weight matrices
        this.weights = [];
        this.biases = [];
        this.activations = []; // Store activations for visualization
        this.gradients = []; // Store gradients for backprop visualization
        this.learning_rate = 0.01;

        // Initialize weights and biases
        this.initializeParameters();

        // Visualization state
        this.currentStep = 0;
        this.animationSteps = [];
        this.isTraining = false;
    }

    /**
     * Initialize weights using Xavier/Glorot initialization
     */
    initializeParameters() {
        for (let i = 0; i < this.layers; i++) {
            const inputSize = this.architecture[i];
            const outputSize = this.architecture[i + 1];

            // Xavier initialization: weights ~ Normal(0, sqrt(2/(fan_in + fan_out)))
            const variance = Math.sqrt(2 / (inputSize + outputSize));
            const weights = Array(outputSize).fill().map(() =>
                Array(inputSize).fill().map(() =>
                    (Math.random() * 2 - 1) * variance
                )
            );

            // Initialize biases to small positive values
            const biases = Array(outputSize).fill().map(() => Math.random() * 0.1);

            this.weights.push(weights);
            this.biases.push(biases);
        }
    }

    /**
     * Activation functions
     */
    static activations = {
        relu: (x) => Math.max(0, x),
        reluDerivative: (x) => x > 0 ? 1 : 0,

        sigmoid: (x) => 1 / (1 + Math.exp(-Math.max(-500, Math.min(500, x)))), // Prevent overflow
        sigmoidDerivative: (x) => {
            const s = NeuralNetwork.activations.sigmoid(x);
            return s * (1 - s);
        },

        tanh: (x) => Math.tanh(x),
        tanhDerivative: (x) => 1 - Math.pow(Math.tanh(x), 2),

        linear: (x) => x,
        linearDerivative: (x) => 1
    };

    /**
     * Forward propagation with step tracking for visualization
     */
    forward(input, trackSteps = false) {
        if (trackSteps) {
            this.animationSteps = [];
            this.currentStep = 0;
        }

        this.activations = [input.slice()]; // Store input as first activation

        let currentInput = input.slice();

        for (let layer = 0; layer < this.layers; layer++) {
            const isOutputLayer = layer === this.layers - 1;
            const activationFunc = isOutputLayer ? 'sigmoid' : 'relu';

            // Matrix multiplication: output = weights * input + bias
            const output = [];
            const preActivation = []; // Store for visualization and backprop

            for (let neuron = 0; neuron < this.weights[layer].length; neuron++) {
                let sum = this.biases[layer][neuron];

                // Weighted sum
                for (let input_idx = 0; input_idx < currentInput.length; input_idx++) {
                    sum += this.weights[layer][neuron][input_idx] * currentInput[input_idx];
                }

                preActivation.push(sum);

                // Apply activation function
                const activated = NeuralNetwork.activations[activationFunc](sum);
                output.push(activated);

                // Track step for visualization
                if (trackSteps) {
                    this.animationSteps.push({
                        type: 'neuron_activation',
                        layer: layer + 1,
                        neuron: neuron,
                        preActivation: sum,
                        activation: activated,
                        inputs: currentInput.slice(),
                        weights: this.weights[layer][neuron].slice(),
                        bias: this.biases[layer][neuron]
                    });
                }
            }

            this.activations.push(output.slice());
            currentInput = output;
        }

        return currentInput;
    }

    /**
     * Backpropagation with gradient tracking for visualization
     */
    backward(input, target, trackSteps = false) {
        if (trackSteps) {
            this.gradients = [];
        }

        // Calculate output error
        const output = this.activations[this.activations.length - 1];
        const outputError = output.map((out, i) => 2 * (out - target[i])); // MSE derivative

        // Store gradients for each layer (working backwards)
        const layerGradients = [];
        let currentError = outputError.slice();

        for (let layer = this.layers - 1; layer >= 0; layer--) {
            const isOutputLayer = layer === this.layers - 1;
            const activationFunc = isOutputLayer ? 'sigmoidDerivative' : 'reluDerivative';

            const weightGradients = [];
            const biasGradients = [];
            const nextError = Array(this.architecture[layer]).fill(0);

            for (let neuron = 0; neuron < this.weights[layer].length; neuron++) {
                // Calculate activation derivative
                const preActivation = this.calculatePreActivation(layer, neuron);
                const activationDerivative = NeuralNetwork.activations[activationFunc](preActivation);

                // Local gradient
                const localGradient = currentError[neuron] * activationDerivative;

                // Weight gradients
                const neuronWeightGrads = [];
                for (let input_idx = 0; input_idx < this.activations[layer].length; input_idx++) {
                    const weightGradient = localGradient * this.activations[layer][input_idx];
                    neuronWeightGrads.push(weightGradient);

                    // Propagate error backwards
                    nextError[input_idx] += localGradient * this.weights[layer][neuron][input_idx];
                }

                weightGradients.push(neuronWeightGrads);
                biasGradients.push(localGradient);

                if (trackSteps) {
                    this.gradients.push({
                        type: 'gradient_calculation',
                        layer: layer,
                        neuron: neuron,
                        localGradient: localGradient,
                        weightGradients: neuronWeightGrads.slice(),
                        biasGradient: localGradient,
                        error: currentError[neuron]
                    });
                }
            }

            layerGradients.unshift({
                weights: weightGradients,
                biases: biasGradients
            });

            currentError = nextError;
        }

        return layerGradients;
    }

    /**
     * Helper method to calculate pre-activation value
     */
    calculatePreActivation(layer, neuron) {
        let sum = this.biases[layer][neuron];
        for (let i = 0; i < this.activations[layer].length; i++) {
            sum += this.weights[layer][neuron][i] * this.activations[layer][i];
        }
        return sum;
    }

    /**
     * Update weights using gradients
     */
    updateWeights(gradients) {
        for (let layer = 0; layer < this.layers; layer++) {
            for (let neuron = 0; neuron < this.weights[layer].length; neuron++) {
                // Update weights
                for (let input_idx = 0; input_idx < this.weights[layer][neuron].length; input_idx++) {
                    this.weights[layer][neuron][input_idx] -=
                        this.learning_rate * gradients[layer].weights[neuron][input_idx];
                }

                // Update bias
                this.biases[layer][neuron] -=
                    this.learning_rate * gradients[layer].biases[neuron];
            }
        }
    }

    /**
     * Train on a single example
     */
    trainStep(input, target, trackSteps = false) {
        const output = this.forward(input, trackSteps);
        const gradients = this.backward(input, target, trackSteps);
        this.updateWeights(gradients);

        // Calculate loss (MSE)
        const loss = output.reduce((sum, out, i) =>
            sum + Math.pow(out - target[i], 2), 0) / output.length;

        return { output, loss };
    }

    /**
     * Get network state for visualization
     */
    getVisualizationState() {
        return {
            architecture: this.architecture,
            weights: this.weights.map(layer =>
                layer.map(neuron => neuron.slice())
            ),
            biases: this.biases.map(layer => layer.slice()),
            activations: this.activations.map(layer => layer.slice()),
            animationSteps: this.animationSteps.slice(),
            currentStep: this.currentStep
        };
    }

    /**
     * Set learning rate
     */
    setLearningRate(rate) {
        this.learning_rate = Math.max(0.001, Math.min(1.0, rate));
    }
}

// Export for both Node.js and browser environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NeuralNetwork };
} else if (typeof window !== 'undefined') {
    window.NeuralNetwork = NeuralNetwork;
}