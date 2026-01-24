/**
 * Comprehensive Test Suite for Neural Network Visualizer
 * Tests mathematical correctness, edge cases, and educational features
 * Created by Alice & Bob collaboration
 */

const { NeuralNetwork } = require('./neuralNetwork.js');

// Test framework - simple but comprehensive
class TestRunner {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    test(description, testFunction) {
        this.tests.push({ description, testFunction });
    }

    async runAll() {
        console.log('🧪 Running Neural Network Test Suite\n');

        for (const { description, testFunction } of this.tests) {
            try {
                await testFunction();
                console.log(`✅ ${description}`);
                this.passed++;
            } catch (error) {
                console.log(`❌ ${description}`);
                console.log(`   Error: ${error.message}\n`);
                this.failed++;
            }
        }

        this.printSummary();
    }

    printSummary() {
        const total = this.passed + this.failed;
        console.log(`\n📊 Test Results: ${this.passed}/${total} passed`);

        if (this.failed === 0) {
            console.log('🎉 All tests passed! Neural network implementation is robust.');
        } else {
            console.log(`⚠️  ${this.failed} test(s) failed. Review implementation.`);
        }
    }
}

// Helper functions for testing
function expect(actual) {
    return {
        toBe: (expected) => {
            if (actual !== expected) {
                throw new Error(`Expected ${expected}, but got ${actual}`);
            }
        },
        toBeCloseTo: (expected, precision = 3) => {
            const diff = Math.abs(actual - expected);
            const tolerance = Math.pow(10, -precision);
            if (diff > tolerance) {
                throw new Error(`Expected ${actual} to be close to ${expected} (within ${tolerance})`);
            }
        },
        toEqual: (expected) => {
            if (JSON.stringify(actual) !== JSON.stringify(expected)) {
                throw new Error(`Expected ${JSON.stringify(expected)}, but got ${JSON.stringify(actual)}`);
            }
        },
        toHaveLength: (length) => {
            if (actual.length !== length) {
                throw new Error(`Expected length ${length}, but got ${actual.length}`);
            }
        },
        toBeBetween: (min, max) => {
            if (actual < min || actual > max) {
                throw new Error(`Expected ${actual} to be between ${min} and ${max}`);
            }
        }
    };
}

// Initialize test runner
const runner = new TestRunner();

// === ARCHITECTURE TESTS ===

runner.test('Network Creation - Basic Architecture', () => {
    const network = new NeuralNetwork([2, 3, 1]);

    expect(network.architecture).toEqual([2, 3, 1]);
    expect(network.layers).toBe(2);
    expect(network.weights).toHaveLength(2);
    expect(network.biases).toHaveLength(2);
});

runner.test('Network Creation - Complex Architecture', () => {
    const network = new NeuralNetwork([4, 8, 6, 4, 2]);

    expect(network.architecture).toEqual([4, 8, 6, 4, 2]);
    expect(network.layers).toBe(4);

    // Check weight matrix dimensions
    expect(network.weights[0]).toHaveLength(8);  // 8 neurons in first hidden layer
    expect(network.weights[0][0]).toHaveLength(4);  // 4 inputs each
    expect(network.weights[3]).toHaveLength(2);  // 2 neurons in output layer
    expect(network.weights[3][0]).toHaveLength(4);  // 4 inputs from previous layer
});

runner.test('Weight Initialization - Xavier/Glorot', () => {
    const network = new NeuralNetwork([10, 20, 1]);

    // Check that weights are initialized with appropriate variance
    const layer0Weights = network.weights[0].flat();
    const mean = layer0Weights.reduce((a, b) => a + b) / layer0Weights.length;
    const variance = layer0Weights.reduce((sum, w) => sum + Math.pow(w - mean, 2), 0) / layer0Weights.length;

    // Xavier initialization: variance ≈ 2/(fan_in + fan_out)
    const expectedVariance = 2 / (10 + 20);

    expect(Math.abs(mean)).toBeBetween(0, 0.2);  // Mean should be close to 0
    expect(variance).toBeBetween(expectedVariance * 0.5, expectedVariance * 2);  // Reasonable variance range
});

// === ACTIVATION FUNCTION TESTS ===

runner.test('Activation Functions - ReLU', () => {
    expect(NeuralNetwork.activations.relu(5)).toBe(5);
    expect(NeuralNetwork.activations.relu(-3)).toBe(0);
    expect(NeuralNetwork.activations.relu(0)).toBe(0);

    expect(NeuralNetwork.activations.reluDerivative(5)).toBe(1);
    expect(NeuralNetwork.activations.reluDerivative(-3)).toBe(0);
    expect(NeuralNetwork.activations.reluDerivative(0)).toBe(0);
});

runner.test('Activation Functions - Sigmoid', () => {
    expect(NeuralNetwork.activations.sigmoid(0)).toBeCloseTo(0.5);
    expect(NeuralNetwork.activations.sigmoid(100)).toBeCloseTo(1.0);  // Large positive
    expect(NeuralNetwork.activations.sigmoid(-100)).toBeCloseTo(0.0);  // Large negative

    // Sigmoid derivative at 0
    expect(NeuralNetwork.activations.sigmoidDerivative(0)).toBeCloseTo(0.25);
});

runner.test('Activation Functions - Tanh', () => {
    expect(NeuralNetwork.activations.tanh(0)).toBe(0);
    expect(NeuralNetwork.activations.tanh(100)).toBeCloseTo(1.0);
    expect(NeuralNetwork.activations.tanh(-100)).toBeCloseTo(-1.0);

    expect(NeuralNetwork.activations.tanhDerivative(0)).toBe(1);
});

// === FORWARD PROPAGATION TESTS ===

runner.test('Forward Propagation - Basic Functionality', () => {
    const network = new NeuralNetwork([2, 2, 1]);
    const input = [0.5, 0.8];

    const output = network.forward(input);

    expect(output).toHaveLength(1);
    expect(output[0]).toBeBetween(0, 1);  // Sigmoid output
    expect(network.activations).toHaveLength(3);  // Input + 2 layers
});

runner.test('Forward Propagation - Step Tracking', () => {
    const network = new NeuralNetwork([2, 3, 1]);
    const input = [0.5, 0.8];

    network.forward(input, true);  // Track steps

    expect(network.animationSteps.length).toBe(4);  // 3 neurons in hidden + 1 in output

    // Check step structure
    const step = network.animationSteps[0];
    expect(step.type).toBe('neuron_activation');
    expect(step.layer).toBe(1);  // First hidden layer
    expect(step.neuron).toBe(0);  // First neuron
    expect(typeof step.preActivation).toBe('number');
    expect(typeof step.activation).toBe('number');
});

runner.test('Forward Propagation - Deterministic Output', () => {
    const network = new NeuralNetwork([2, 3, 1]);
    const input = [0.5, 0.8];

    const output1 = network.forward(input);
    const output2 = network.forward(input);

    // Should produce same output with same input
    expect(output1[0]).toBeCloseTo(output2[0]);
});

// === BACKPROPAGATION TESTS ===

runner.test('Backpropagation - Gradient Calculation', () => {
    const network = new NeuralNetwork([2, 2, 1]);
    const input = [0.5, 0.8];
    const target = [0.7];

    // Forward pass first
    network.forward(input);

    // Backward pass
    const gradients = network.backward(input, target, true);

    expect(gradients).toHaveLength(2);  // 2 layers
    expect(gradients[0].weights).toHaveLength(2);  // 2 neurons in hidden layer
    expect(gradients[0].weights[0]).toHaveLength(2);  // 2 inputs
    expect(gradients[1].weights).toHaveLength(1);  // 1 output neuron
});

runner.test('Backpropagation - Gradient Tracking', () => {
    const network = new NeuralNetwork([2, 2, 1]);
    const input = [0.5, 0.8];
    const target = [0.7];

    network.forward(input);
    network.backward(input, target, true);

    expect(network.gradients.length).toBe(3);  // 2 hidden + 1 output

    const gradient = network.gradients[0];
    expect(gradient.type).toBe('gradient_calculation');
    expect(typeof gradient.localGradient).toBe('number');
    expect(gradient.weightGradients).toHaveLength(2);  // 2 inputs
});

// === TRAINING TESTS ===

runner.test('Training Step - Loss Calculation', () => {
    const network = new NeuralNetwork([2, 3, 1]);
    const input = [0.5, 0.8];
    const target = [0.7];

    const result = network.trainStep(input, target);

    expect(typeof result.loss).toBe('number');
    expect(result.loss).toBeBetween(0, 10);  // Reasonable loss range
    expect(result.output).toHaveLength(1);
});

runner.test('Training Step - Learning Occurs', () => {
    const network = new NeuralNetwork([2, 3, 1]);
    const input = [0.5, 0.8];
    const target = [0.7];

    // Train for several steps
    let previousLoss = Infinity;
    let lossDecreased = false;

    for (let i = 0; i < 100; i++) {
        const result = network.trainStep(input, target);

        if (result.loss < previousLoss) {
            lossDecreased = true;
        }

        if (i > 20 && result.loss < 0.1) {
            break;  // Good enough convergence
        }

        previousLoss = result.loss;
    }

    expect(lossDecreased).toBe(true);  // Loss should decrease at some point
});

// === EDGE CASE TESTS ===

runner.test('Edge Case - Single Node Network', () => {
    const network = new NeuralNetwork([1, 1]);
    const input = [0.5];
    const target = [0.7];

    const output = network.forward(input);
    const result = network.trainStep(input, target);

    expect(output).toHaveLength(1);
    expect(typeof result.loss).toBe('number');
});

runner.test('Edge Case - Large Input Values', () => {
    const network = new NeuralNetwork([2, 3, 1]);
    const input = [100, -100];  // Large values

    const output = network.forward(input);

    expect(output[0]).toBeBetween(0, 1);  // Should still be valid sigmoid output
    expect(!isNaN(output[0])).toBe(true);
});

runner.test('Edge Case - Zero Learning Rate', () => {
    const network = new NeuralNetwork([2, 2, 1]);
    network.setLearningRate(0);

    const input = [0.5, 0.8];
    const target = [0.7];

    const initialWeights = JSON.stringify(network.weights);
    network.trainStep(input, target);
    const finalWeights = JSON.stringify(network.weights);

    expect(initialWeights).toBe(finalWeights);  // Weights shouldn't change
});

runner.test('Edge Case - Learning Rate Bounds', () => {
    const network = new NeuralNetwork([2, 2, 1]);

    // Test bounds
    network.setLearningRate(-0.1);
    expect(network.learning_rate).toBe(0.001);  // Should clamp to minimum

    network.setLearningRate(5.0);
    expect(network.learning_rate).toBe(1.0);  // Should clamp to maximum

    network.setLearningRate(0.05);
    expect(network.learning_rate).toBe(0.05);  // Should accept valid value
});

// === XOR PROBLEM TEST (Classic Non-Linear Problem) ===

runner.test('XOR Problem - Network Can Learn Non-Linear Function', () => {
    const network = new NeuralNetwork([2, 4, 1]);
    network.setLearningRate(0.1);

    const xorData = [
        { input: [0, 0], target: [0] },
        { input: [0, 1], target: [1] },
        { input: [1, 0], target: [1] },
        { input: [1, 1], target: [0] }
    ];

    // Train for many epochs
    for (let epoch = 0; epoch < 1000; epoch++) {
        for (const { input, target } of xorData) {
            network.trainStep(input, target);
        }
    }

    // Test final accuracy
    let correct = 0;
    for (const { input, target } of xorData) {
        const output = network.forward(input);
        const predicted = output[0] > 0.5 ? 1 : 0;
        if (predicted === target[0]) correct++;
    }

    const accuracy = correct / xorData.length;
    expect(accuracy).toBeBetween(0.75, 1.0);  // Should achieve high accuracy
});

// === VISUALIZATION STATE TESTS ===

runner.test('Visualization State - Complete State Export', () => {
    const network = new NeuralNetwork([2, 3, 1]);
    const input = [0.5, 0.8];

    network.forward(input, true);
    const state = network.getVisualizationState();

    expect(state.architecture).toEqual([2, 3, 1]);
    expect(state.weights).toHaveLength(2);
    expect(state.biases).toHaveLength(2);
    expect(state.activations).toHaveLength(3);
    expect(state.animationSteps.length).toBe(4);
});

// === NUMERICAL STABILITY TESTS ===

runner.test('Numerical Stability - Extreme Values', () => {
    const network = new NeuralNetwork([1, 1]);

    // Test sigmoid with extreme values
    const extremePositive = NeuralNetwork.activations.sigmoid(1000);
    const extremeNegative = NeuralNetwork.activations.sigmoid(-1000);

    expect(extremePositive).toBeCloseTo(1.0);
    expect(extremeNegative).toBeCloseTo(0.0);
    expect(!isNaN(extremePositive)).toBe(true);
    expect(!isNaN(extremeNegative)).toBe(true);
});

// Run all tests
if (require.main === module) {
    runner.runAll().catch(console.error);
}

module.exports = { TestRunner, expect };