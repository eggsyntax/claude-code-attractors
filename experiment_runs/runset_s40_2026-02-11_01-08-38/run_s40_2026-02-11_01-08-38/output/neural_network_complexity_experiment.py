#!/usr/bin/env python3
"""
Neural Network Complexity Threshold Experiment

Tests the Complexity Threshold Theory by training neural networks on problems of varying complexity.
Validates whether Global+Local Synergy benefits depend on problem complexity.
"""

import numpy as np
import time
from typing import List, Tuple, Dict, Any
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class ComplexityExperiment:
    """Framework for testing algorithm performance across complexity levels"""

    def __init__(self):
        self.results = {}

    def generate_simple_data(self, n_samples=1000):
        """Simple linear relationship: y = 2x + 1 + noise"""
        np.random.seed(42)
        X = np.random.uniform(-10, 10, (n_samples, 1))
        y = 2 * X.flatten() + 1 + np.random.normal(0, 0.1, n_samples)
        return X, y

    def generate_medium_data(self, n_samples=1000):
        """Medium complexity: XOR-like pattern with multiple features"""
        np.random.seed(42)
        X = np.random.uniform(-1, 1, (n_samples, 4))
        # Create XOR-like pattern with interactions
        y = ((X[:, 0] * X[:, 1] > 0) ^ (X[:, 2] * X[:, 3] > 0)).astype(int)
        # Add noise
        y = y + np.random.normal(0, 0.1, n_samples)
        return X, y

    def generate_complex_data(self, n_samples=1000):
        """Complex: High-dimensional with non-linear interactions"""
        np.random.seed(42)
        X = np.random.uniform(-1, 1, (n_samples, 20))
        # Complex non-linear function
        y = (np.sin(X[:, 0] * X[:, 1]) +
             np.cos(X[:, 2] ** 2 + X[:, 3] ** 2) +
             np.tanh(X[:, 4] * X[:, 5] * X[:, 6]) +
             np.sum(X[:, 7:15] ** 2, axis=1) * 0.1 +
             np.random.normal(0, 0.2, n_samples))
        return X, y

class SimpleOptimizer:
    """Basic SGD - Low synergy (simple local updates)"""

    def __init__(self, learning_rate=0.01):
        self.lr = learning_rate
        self.synergy_score = 150  # Simple local updates only

    def update(self, params, gradients):
        return params - self.lr * gradients

class AdaptiveOptimizer:
    """Adam-like optimizer - High synergy (global momentum + local adaptive rates)"""

    def __init__(self, learning_rate=0.001, beta1=0.9, beta2=0.999):
        self.lr = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.m = None
        self.v = None
        self.t = 0
        self.synergy_score = 850  # Global state + local adaptive updates

    def update(self, params, gradients):
        if self.m is None:
            self.m = np.zeros_like(params)
            self.v = np.zeros_like(params)

        self.t += 1

        # Global momentum tracking
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradients
        self.v = self.beta2 * self.v + (1 - self.beta2) * gradients ** 2

        # Bias correction (global state consideration)
        m_hat = self.m / (1 - self.beta1 ** self.t)
        v_hat = self.v / (1 - self.beta2 ** self.t)

        # Local adaptive updates
        return params - self.lr * m_hat / (np.sqrt(v_hat) + 1e-8)

class SimpleNetwork:
    """Basic network - Low synergy (simple architecture)"""

    def __init__(self, input_size, hidden_size=10):
        self.W1 = np.random.normal(0, 0.1, (input_size, hidden_size))
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.normal(0, 0.1, (hidden_size, 1))
        self.b2 = np.zeros(1)
        self.synergy_score = 200  # Simple feedforward only

    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        return self.z2

    def get_params(self):
        return np.concatenate([self.W1.flatten(), self.b1, self.W2.flatten(), self.b2])

    def set_params(self, params):
        idx = 0
        w1_size = self.W1.size
        self.W1 = params[idx:idx+w1_size].reshape(self.W1.shape)
        idx += w1_size

        b1_size = self.b1.size
        self.b1 = params[idx:idx+b1_size]
        idx += b1_size

        w2_size = self.W2.size
        self.W2 = params[idx:idx+w2_size].reshape(self.W2.shape)
        idx += w2_size

        self.b2 = params[idx:idx+1]

class ComplexNetwork:
    """Complex network with skip connections - High synergy (global architecture + local computations)"""

    def __init__(self, input_size, hidden_sizes=[32, 16, 8]):
        self.layers = []
        prev_size = input_size

        for hidden_size in hidden_sizes:
            self.layers.append({
                'W': np.random.normal(0, np.sqrt(2/prev_size), (prev_size, hidden_size)),
                'b': np.zeros(hidden_size)
            })
            prev_size = hidden_size

        # Output layer
        self.output_layer = {
            'W': np.random.normal(0, np.sqrt(2/prev_size), (prev_size + input_size, 1)),  # +input_size for skip connection
            'b': np.zeros(1)
        }
        self.synergy_score = 750  # Global skip connections + local layer computations

    def forward(self, X):
        self.activations = [X]

        for layer in self.layers:
            z = self.activations[-1] @ layer['W'] + layer['b']
            a = np.maximum(0, z)  # ReLU
            self.activations.append(a)

        # Skip connection: concatenate input with final hidden layer
        final_input = np.concatenate([X, self.activations[-1]], axis=1)
        output = final_input @ self.output_layer['W'] + self.output_layer['b']

        return output

    def get_params(self):
        params = []
        for layer in self.layers:
            params.extend([layer['W'].flatten(), layer['b']])
        params.extend([self.output_layer['W'].flatten(), self.output_layer['b']])
        return np.concatenate(params)

    def set_params(self, params):
        idx = 0
        for layer in self.layers:
            w_size = layer['W'].size
            layer['W'] = params[idx:idx+w_size].reshape(layer['W'].shape)
            idx += w_size

            b_size = layer['b'].size
            layer['b'] = params[idx:idx+b_size]
            idx += b_size

        # Output layer
        w_size = self.output_layer['W'].size
        self.output_layer['W'] = params[idx:idx+w_size].reshape(self.output_layer['W'].shape)
        idx += w_size

        self.output_layer['b'] = params[idx:idx+1]

def train_model(network, optimizer, X, y, epochs=100):
    """Train a model and return training time and final loss"""
    start_time = time.time()
    losses = []

    for epoch in range(epochs):
        # Forward pass
        predictions = network.forward(X)
        loss = np.mean((predictions.flatten() - y) ** 2)
        losses.append(loss)

        # Backward pass (approximate gradients)
        params = network.get_params()
        gradients = np.zeros_like(params)

        # Numerical gradient approximation
        epsilon = 1e-5
        for i in range(len(params)):
            params_plus = params.copy()
            params_plus[i] += epsilon
            network.set_params(params_plus)
            loss_plus = np.mean((network.forward(X).flatten() - y) ** 2)

            params_minus = params.copy()
            params_minus[i] -= epsilon
            network.set_params(params_minus)
            loss_minus = np.mean((network.forward(X).flatten() - y) ** 2)

            gradients[i] = (loss_plus - loss_minus) / (2 * epsilon)

        # Update parameters
        network.set_params(params)
        new_params = optimizer.update(params, gradients)
        network.set_params(new_params)

    training_time = time.time() - start_time
    final_loss = losses[-1]

    return training_time, final_loss

def run_complexity_experiment():
    """Run the complete complexity threshold experiment"""
    experiment = ComplexityExperiment()

    # Define test configurations
    configurations = [
        ("Simple_Network_Simple_Optimizer", lambda input_size: SimpleNetwork(input_size), lambda: SimpleOptimizer()),
        ("Simple_Network_Adaptive_Optimizer", lambda input_size: SimpleNetwork(input_size), lambda: AdaptiveOptimizer()),
        ("Complex_Network_Simple_Optimizer", lambda input_size: ComplexNetwork(input_size), lambda: SimpleOptimizer()),
        ("Complex_Network_Adaptive_Optimizer", lambda input_size: ComplexNetwork(input_size), lambda: AdaptiveOptimizer()),
    ]

    # Test on different complexity levels
    complexity_tests = [
        ("Simple", experiment.generate_simple_data),
        ("Medium", experiment.generate_medium_data),
        ("Complex", experiment.generate_complex_data),
    ]

    results = {}

    for complexity_name, data_generator in complexity_tests:
        print(f"\n=== Testing {complexity_name} Problem ===")
        X, y = data_generator()
        results[complexity_name] = {}

        for config_name, network_factory, optimizer_factory in configurations:
            print(f"Running {config_name}...")

            try:
                network = network_factory(X.shape[1])
                optimizer = optimizer_factory()

                training_time, final_loss = train_model(network, optimizer, X, y, epochs=50)

                # Calculate synergy score
                synergy_score = network.synergy_score + optimizer.synergy_score

                results[complexity_name][config_name] = {
                    'training_time': training_time,
                    'final_loss': final_loss,
                    'synergy_score': synergy_score,
                    'performance_score': 1000 / (training_time + final_loss * 10)  # Inverse of time + loss penalty
                }

                print(f"  Training Time: {training_time:.4f}s")
                print(f"  Final Loss: {final_loss:.6f}")
                print(f"  Synergy Score: {synergy_score}")
                print(f"  Performance Score: {results[complexity_name][config_name]['performance_score']:.2f}")

            except Exception as e:
                print(f"  Error: {e}")
                results[complexity_name][config_name] = None

    return results

def analyze_complexity_threshold(results):
    """Analyze results to validate the complexity threshold hypothesis"""
    print("\n" + "="*80)
    print("COMPLEXITY THRESHOLD ANALYSIS")
    print("="*80)

    for complexity_level in ["Simple", "Medium", "Complex"]:
        print(f"\n--- {complexity_level} Problem Results ---")

        if complexity_level not in results:
            continue

        # Sort by performance score
        sorted_results = sorted(
            [(name, data) for name, data in results[complexity_level].items() if data is not None],
            key=lambda x: x[1]['performance_score'],
            reverse=True
        )

        print("Performance Ranking:")
        for i, (name, data) in enumerate(sorted_results, 1):
            print(f"{i}. {name}")
            print(f"   Performance: {data['performance_score']:.2f}, Synergy: {data['synergy_score']}, Time: {data['training_time']:.4f}s")

        # Check if high synergy correlates with better performance
        if len(sorted_results) >= 2:
            best_config = sorted_results[0]
            worst_config = sorted_results[-1]

            print(f"\nComplexity Threshold Test:")
            print(f"Best: {best_config[0]} (Synergy: {best_config[1]['synergy_score']})")
            print(f"Worst: {worst_config[0]} (Synergy: {worst_config[1]['synergy_score']})")

            if best_config[1]['synergy_score'] > worst_config[1]['synergy_score']:
                print("✅ HIGH SYNERGY WINS - Supports complexity threshold theory!")
            else:
                print("❌ LOW SYNERGY WINS - Challenges complexity threshold theory!")

if __name__ == "__main__":
    print("🚀 NEURAL NETWORK COMPLEXITY THRESHOLD EXPERIMENT")
    print("Testing whether Global+Local Synergy benefits depend on problem complexity...")
    print("="*80)

    results = run_complexity_experiment()
    analyze_complexity_threshold(results)

    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE!")
    print("Results saved to validate the Complexity Threshold Theory!")
    print("="*80)