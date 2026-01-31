"""
Base classes for federated learning models and training.
Provides abstractions for different ML frameworks (PyTorch, TensorFlow, etc.)

Phase 1: Alice's Model Abstraction Layer
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class TrainingConfig:
    """Configuration for local training on participants"""
    learning_rate: float = 0.01
    batch_size: int = 32
    local_epochs: int = 1
    optimizer: str = "sgd"  # sgd, adam, rmsprop
    loss_function: str = "cross_entropy"  # cross_entropy, mse, binary_cross_entropy
    regularization: Optional[float] = None
    max_grad_norm: Optional[float] = None  # For gradient clipping

    def to_dict(self) -> Dict[str, Any]:
        return {
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "local_epochs": self.local_epochs,
            "optimizer": self.optimizer,
            "loss_function": self.loss_function,
            "regularization": self.regularization,
            "max_grad_norm": self.max_grad_norm
        }


@dataclass
class TrainingMetrics:
    """Metrics from local training"""
    loss: float
    accuracy: Optional[float] = None
    num_samples: int = 0
    training_time: float = 0.0
    convergence_info: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loss": self.loss,
            "accuracy": self.accuracy,
            "num_samples": self.num_samples,
            "training_time": self.training_time,
            "convergence_info": self.convergence_info
        }


class FederatedModel(ABC):
    """
    Abstract base class for federated learning models.
    Enables support for multiple ML frameworks.
    """

    def __init__(self, model_config: Dict[str, Any]):
        self.model_config = model_config
        self.model = None
        self.training_config: Optional[TrainingConfig] = None

    @abstractmethod
    def initialize_model(self) -> bool:
        """Initialize the model architecture"""
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, np.ndarray]:
        """Get model parameters as numpy arrays"""
        pass

    @abstractmethod
    def set_parameters(self, parameters: Dict[str, np.ndarray]) -> bool:
        """Set model parameters from numpy arrays"""
        pass

    @abstractmethod
    def train_local(self, data: Any, labels: Any, config: TrainingConfig) -> TrainingMetrics:
        """Train the model locally on provided data"""
        pass

    @abstractmethod
    def evaluate(self, data: Any, labels: Any) -> TrainingMetrics:
        """Evaluate the model on provided data"""
        pass

    @abstractmethod
    def get_gradients(self) -> Dict[str, np.ndarray]:
        """Get model gradients as numpy arrays"""
        pass

    def get_model_size(self) -> int:
        """Get total number of parameters in the model"""
        parameters = self.get_parameters()
        return sum(param.size for param in parameters.values())

    def serialize_parameters(self) -> str:
        """Serialize parameters to JSON string"""
        parameters = self.get_parameters()
        # Convert numpy arrays to lists for JSON serialization
        serializable = {name: param.tolist() for name, param in parameters.items()}
        return json.dumps(serializable)

    def deserialize_parameters(self, json_str: str) -> bool:
        """Deserialize parameters from JSON string"""
        try:
            data = json.loads(json_str)
            parameters = {name: np.array(param_list) for name, param_list in data.items()}
            return self.set_parameters(parameters)
        except Exception:
            return False


class SimpleNeuralNetwork(FederatedModel):
    """
    Simple neural network implementation for federated learning.
    Uses numpy for computations (framework-agnostic).

    TODO for Bob (Phase 2): Optimize this implementation
    - Add support for different optimizers
    - Implement gradient compression
    - Add regularization techniques
    """

    def __init__(self, input_dim: int, hidden_dims: List[int], output_dim: int,
                 activation: str = "relu"):
        model_config = {
            "input_dim": input_dim,
            "hidden_dims": hidden_dims,
            "output_dim": output_dim,
            "activation": activation
        }
        super().__init__(model_config)

        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim
        self.activation = activation

        # Model parameters
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []

        # Training state
        self.last_gradients: Optional[Dict[str, np.ndarray]] = None

    def initialize_model(self) -> bool:
        """Initialize network weights and biases"""
        try:
            # Xavier initialization
            layers = [self.input_dim] + self.hidden_dims + [self.output_dim]

            self.weights = []
            self.biases = []

            for i in range(len(layers) - 1):
                # Xavier/Glorot initialization
                fan_in, fan_out = layers[i], layers[i + 1]
                limit = np.sqrt(6.0 / (fan_in + fan_out))

                weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
                bias = np.zeros(fan_out)

                self.weights.append(weight)
                self.biases.append(bias)

            return True
        except Exception:
            return False

    def get_parameters(self) -> Dict[str, np.ndarray]:
        """Get all model parameters"""
        parameters = {}

        for i, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            parameters[f"weight_{i}"] = weight.copy()
            parameters[f"bias_{i}"] = bias.copy()

        return parameters

    def set_parameters(self, parameters: Dict[str, np.ndarray]) -> bool:
        """Set model parameters"""
        try:
            # Extract weights and biases
            num_layers = len([k for k in parameters.keys() if k.startswith("weight_")])

            new_weights = []
            new_biases = []

            for i in range(num_layers):
                new_weights.append(parameters[f"weight_{i}"].copy())
                new_biases.append(parameters[f"bias_{i}"].copy())

            self.weights = new_weights
            self.biases = new_biases
            return True
        except Exception:
            return False

    def _activation_function(self, x: np.ndarray) -> np.ndarray:
        """Apply activation function"""
        if self.activation == "relu":
            return np.maximum(0, x)
        elif self.activation == "sigmoid":
            return 1 / (1 + np.exp(-np.clip(x, -250, 250)))  # Clip to prevent overflow
        elif self.activation == "tanh":
            return np.tanh(x)
        else:
            return x  # Linear activation

    def _activation_derivative(self, x: np.ndarray) -> np.ndarray:
        """Compute activation function derivative"""
        if self.activation == "relu":
            return (x > 0).astype(float)
        elif self.activation == "sigmoid":
            sig = self._activation_function(x)
            return sig * (1 - sig)
        elif self.activation == "tanh":
            tanh = self._activation_function(x)
            return 1 - tanh ** 2
        else:
            return np.ones_like(x)

    def _forward_pass(self, X: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Forward pass through the network"""
        activations = [X]

        current_input = X
        for i, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            z = np.dot(current_input, weight) + bias

            if i == len(self.weights) - 1:
                # Output layer - no activation (or softmax for classification)
                activation = z
            else:
                # Hidden layers
                activation = self._activation_function(z)

            activations.append(activation)
            current_input = activation

        return current_input, activations

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax activation for output layer"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    def train_local(self, data: np.ndarray, labels: np.ndarray,
                    config: TrainingConfig) -> TrainingMetrics:
        """Train the model locally using mini-batch SGD"""
        start_time = time.time()
        n_samples = data.shape[0]

        total_loss = 0.0
        correct_predictions = 0

        for epoch in range(config.local_epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            data_shuffled = data[indices]
            labels_shuffled = labels[indices]

            # Mini-batch training
            for i in range(0, n_samples, config.batch_size):
                batch_end = min(i + config.batch_size, n_samples)
                batch_X = data_shuffled[i:batch_end]
                batch_y = labels_shuffled[i:batch_end]

                # Forward pass
                predictions, activations = self._forward_pass(batch_X)

                # Compute loss and accuracy
                if self.model_config.get("task_type") == "classification":
                    # Softmax + cross-entropy
                    probs = self._softmax(predictions)
                    loss = -np.mean(np.sum(batch_y * np.log(probs + 1e-15), axis=1))

                    # Accuracy
                    pred_classes = np.argmax(probs, axis=1)
                    true_classes = np.argmax(batch_y, axis=1)
                    correct_predictions += np.sum(pred_classes == true_classes)
                else:
                    # Mean squared error for regression
                    loss = np.mean((predictions - batch_y) ** 2)

                total_loss += loss

                # Backward pass
                self._backward_pass(batch_X, batch_y, predictions, activations, config)

        # Calculate final metrics
        avg_loss = total_loss / (n_samples * config.local_epochs / config.batch_size)
        accuracy = correct_predictions / (n_samples * config.local_epochs) if self.model_config.get("task_type") == "classification" else None
        training_time = time.time() - start_time

        return TrainingMetrics(
            loss=avg_loss,
            accuracy=accuracy,
            num_samples=n_samples,
            training_time=training_time
        )

    def _backward_pass(self, X: np.ndarray, y: np.ndarray, predictions: np.ndarray,
                       activations: List[np.ndarray], config: TrainingConfig):
        """Backward pass and parameter updates"""
        batch_size = X.shape[0]

        # Compute gradients
        if self.model_config.get("task_type") == "classification":
            # Softmax + cross-entropy gradient
            probs = self._softmax(predictions)
            d_output = (probs - y) / batch_size
        else:
            # MSE gradient
            d_output = 2 * (predictions - y) / batch_size

        # Initialize gradient storage
        weight_gradients = []
        bias_gradients = []

        # Backpropagate through layers
        d_current = d_output
        for i in reversed(range(len(self.weights))):
            # Gradient w.r.t. weights and biases
            weight_grad = np.dot(activations[i].T, d_current)
            bias_grad = np.sum(d_current, axis=0)

            weight_gradients.insert(0, weight_grad)
            bias_gradients.insert(0, bias_grad)

            # Gradient w.r.t. previous layer activation
            if i > 0:
                d_current = np.dot(d_current, self.weights[i].T)
                d_current = d_current * self._activation_derivative(activations[i])

        # Apply gradient clipping if specified
        if config.max_grad_norm:
            total_norm = 0
            for grad in weight_gradients + bias_gradients:
                total_norm += np.sum(grad ** 2)
            total_norm = np.sqrt(total_norm)

            if total_norm > config.max_grad_norm:
                clip_factor = config.max_grad_norm / total_norm
                weight_gradients = [grad * clip_factor for grad in weight_gradients]
                bias_gradients = [grad * clip_factor for grad in bias_gradients]

        # Store gradients for federated aggregation
        self.last_gradients = {}
        for i, (w_grad, b_grad) in enumerate(zip(weight_gradients, bias_gradients)):
            self.last_gradients[f"weight_{i}"] = w_grad.copy()
            self.last_gradients[f"bias_{i}"] = b_grad.copy()

        # Update parameters using specified optimizer
        if config.optimizer == "sgd":
            for i, (w_grad, b_grad) in enumerate(zip(weight_gradients, bias_gradients)):
                self.weights[i] -= config.learning_rate * w_grad
                self.biases[i] -= config.learning_rate * b_grad
        # TODO: Add other optimizers (Adam, RMSprop, etc.)

    def evaluate(self, data: np.ndarray, labels: np.ndarray) -> TrainingMetrics:
        """Evaluate model on provided data"""
        predictions, _ = self._forward_pass(data)

        if self.model_config.get("task_type") == "classification":
            probs = self._softmax(predictions)
            loss = -np.mean(np.sum(labels * np.log(probs + 1e-15), axis=1))

            pred_classes = np.argmax(probs, axis=1)
            true_classes = np.argmax(labels, axis=1)
            accuracy = np.mean(pred_classes == true_classes)
        else:
            loss = np.mean((predictions - labels) ** 2)
            accuracy = None

        return TrainingMetrics(
            loss=loss,
            accuracy=accuracy,
            num_samples=data.shape[0],
            training_time=0.0
        )

    def get_gradients(self) -> Dict[str, np.ndarray]:
        """Get the most recent gradients"""
        if self.last_gradients is None:
            return {}
        return {name: grad.copy() for name, grad in self.last_gradients.items()}


# TODO for Bob (Phase 2): Add PyTorch integration
"""
class PyTorchFederatedModel(FederatedModel):
    PyTorch-based federated model implementation.

    Should support:
    - Standard PyTorch models and optimizers
    - Efficient gradient computation and aggregation
    - GPU acceleration
    - Model checkpointing and serialization
"""

# TODO for Bob (Phase 2): Add TensorFlow integration
"""
class TensorFlowFederatedModel(FederatedModel):
    TensorFlow/Keras-based federated model implementation.

    Should support:
    - Keras Sequential and Functional API models
    - TensorFlow optimizers and loss functions
    - Distributed training capabilities
    - TensorBoard integration for monitoring
"""


# Import time module (forgot to import earlier)
import time

if __name__ == "__main__":
    # Test the SimpleNeuralNetwork
    print("Testing SimpleNeuralNetwork...")

    # Create a simple classification dataset
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    n_classes = 3

    # Generate synthetic data
    X = np.random.randn(n_samples, n_features)
    # Create some pattern in the data
    weights_true = np.random.randn(n_features, n_classes)
    logits = np.dot(X, weights_true) + np.random.randn(n_samples, n_classes) * 0.1
    y_classes = np.argmax(logits, axis=1)

    # One-hot encode labels
    y = np.zeros((n_samples, n_classes))
    y[np.arange(n_samples), y_classes] = 1

    # Create and initialize model
    model = SimpleNeuralNetwork(
        input_dim=n_features,
        hidden_dims=[64, 32],
        output_dim=n_classes,
        activation="relu"
    )
    model.model_config["task_type"] = "classification"

    success = model.initialize_model()
    print(f"Model initialization: {'Success' if success else 'Failed'}")
    print(f"Model size: {model.get_model_size()} parameters")

    # Test training
    config = TrainingConfig(
        learning_rate=0.01,
        batch_size=32,
        local_epochs=5
    )

    metrics = model.train_local(X, y, config)
    print(f"Training metrics: Loss={metrics.loss:.4f}, Accuracy={metrics.accuracy:.4f}")

    # Test evaluation
    eval_metrics = model.evaluate(X, y)
    print(f"Evaluation metrics: Loss={eval_metrics.loss:.4f}, Accuracy={eval_metrics.accuracy:.4f}")

    # Test parameter serialization
    params_json = model.serialize_parameters()
    print(f"Serialized parameters size: {len(params_json)} characters")

    # Test parameter loading
    new_model = SimpleNeuralNetwork(n_features, [64, 32], n_classes)
    new_model.model_config["task_type"] = "classification"
    new_model.initialize_model()

    load_success = new_model.deserialize_parameters(params_json)
    print(f"Parameter loading: {'Success' if load_success else 'Failed'}")

    print("SimpleNeuralNetwork test completed!")