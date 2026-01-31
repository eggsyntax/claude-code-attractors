"""
Federated Learning Participant Implementation
===========================================

Implements the client-side logic for federated learning participants,
including local training, gradient computation, and communication with
the federated coordinator.

Author: Bob (Claude Code Agent)
Phase: 2 - Participant Management & Aggregation
"""

import asyncio
import time
import json
import numpy as np
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from federated_protocol import FederatedMessage, MessageType, InMemoryProtocol
from model_base import FederatedModel, ModelMetrics


@dataclass
class TrainingConfig:
    """Configuration for local training parameters"""
    local_epochs: int = 5
    batch_size: int = 32
    learning_rate: float = 0.01
    gradient_compression: bool = True
    compression_ratio: float = 0.1  # Compress to 10% of original size
    differential_privacy: bool = False
    privacy_epsilon: float = 1.0
    max_gradient_norm: float = 1.0


@dataclass
class ParticipantStats:
    """Statistics tracking for participant performance"""
    rounds_participated: int = 0
    total_training_time: float = 0.0
    total_communication_time: float = 0.0
    average_loss: float = 0.0
    data_samples: int = 0
    compression_savings: float = 0.0
    last_update_time: float = field(default_factory=time.time)


class GradientCompressor:
    """Implements gradient compression techniques for bandwidth optimization"""

    @staticmethod
    def top_k_compression(gradients: Dict[str, np.ndarray], k_ratio: float = 0.1) -> Tuple[Dict[str, Any], float]:
        """
        Top-K gradient compression - keep only the largest k% of gradients
        Returns compressed gradients and compression ratio achieved
        """
        compressed = {}
        original_size = 0
        compressed_size = 0

        for layer_name, grad in gradients.items():
            original_size += grad.size
            flat_grad = grad.flatten()

            # Select top k% gradients by magnitude
            k = max(1, int(len(flat_grad) * k_ratio))
            indices = np.argpartition(np.abs(flat_grad), -k)[-k:]

            # Store as sparse representation
            compressed[layer_name] = {
                'indices': indices.tolist(),
                'values': flat_grad[indices].tolist(),
                'shape': grad.shape
            }
            compressed_size += len(indices) * 2  # indices + values

        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        return compressed, compression_ratio

    @staticmethod
    def decompress_top_k(compressed_gradients: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Decompress top-k compressed gradients"""
        decompressed = {}

        for layer_name, compressed in compressed_gradients.items():
            shape = compressed['shape']
            indices = np.array(compressed['indices'])
            values = np.array(compressed['values'])

            # Reconstruct sparse gradient
            flat_grad = np.zeros(np.prod(shape))
            flat_grad[indices] = values
            decompressed[layer_name] = flat_grad.reshape(shape)

        return decompressed

    @staticmethod
    def quantization_compression(gradients: Dict[str, np.ndarray], bits: int = 8) -> Tuple[Dict[str, Any], float]:
        """
        Quantize gradients to reduce precision and bandwidth
        """
        compressed = {}
        original_size = 0
        compressed_size = 0

        for layer_name, grad in gradients.items():
            original_size += grad.size * 32  # 32-bit floats

            # Quantize to specified bit depth
            min_val, max_val = grad.min(), grad.max()
            scale = (max_val - min_val) / (2**bits - 1)

            quantized = np.round((grad - min_val) / scale).astype(np.uint8)

            compressed[layer_name] = {
                'quantized': quantized.tolist(),
                'min_val': float(min_val),
                'scale': float(scale),
                'shape': grad.shape
            }
            compressed_size += grad.size * bits

        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        return compressed, compression_ratio


class DifferentialPrivacy:
    """Implements differential privacy for gradient protection"""

    @staticmethod
    def add_gaussian_noise(gradients: Dict[str, np.ndarray],
                          epsilon: float = 1.0,
                          sensitivity: float = 1.0,
                          delta: float = 1e-5) -> Dict[str, np.ndarray]:
        """
        Add Gaussian noise to gradients for differential privacy
        """
        sigma = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / epsilon

        noisy_gradients = {}
        for layer_name, grad in gradients.items():
            noise = np.random.normal(0, sigma, grad.shape)
            noisy_gradients[layer_name] = grad + noise

        return noisy_gradients

    @staticmethod
    def clip_gradients(gradients: Dict[str, np.ndarray], max_norm: float = 1.0) -> Dict[str, np.ndarray]:
        """
        Clip gradients to bound sensitivity for differential privacy
        """
        clipped = {}

        # Calculate global gradient norm
        total_norm = 0.0
        for grad in gradients.values():
            total_norm += np.sum(grad ** 2)
        total_norm = np.sqrt(total_norm)

        # Clip if necessary
        if total_norm > max_norm:
            clip_factor = max_norm / total_norm
            for layer_name, grad in gradients.items():
                clipped[layer_name] = grad * clip_factor
        else:
            clipped = gradients.copy()

        return clipped


class FederatedParticipant:
    """
    Federated Learning Participant

    Manages local training, gradient computation, and communication
    with the federated coordinator.
    """

    def __init__(self,
                 participant_id: str,
                 model: FederatedModel,
                 protocol: InMemoryProtocol,
                 config: TrainingConfig = None):
        self.participant_id = participant_id
        self.model = model
        self.protocol = protocol
        self.config = config or TrainingConfig()
        self.stats = ParticipantStats()

        # Training data (will be set externally)
        self.train_data: Optional[Tuple[np.ndarray, np.ndarray]] = None
        self.test_data: Optional[Tuple[np.ndarray, np.ndarray]] = None

        # State management
        self.current_round = 0
        self.is_training = False
        self.global_parameters: Optional[Dict[str, np.ndarray]] = None

        # Synchronization
        self._stop_event = threading.Event()

        # Register message handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register message handlers for coordinator communication"""
        self.protocol.register_handler(
            MessageType.MODEL_UPDATE,
            self._handle_model_update
        )
        self.protocol.register_handler(
            MessageType.TRAINING_REQUEST,
            self._handle_training_request
        )

    async def _handle_model_update(self, message: FederatedMessage):
        """Handle global model updates from coordinator"""
        if message.payload and 'parameters' in message.payload:
            self.global_parameters = message.payload['parameters']
            self.model.set_parameters(self.global_parameters)
            print(f"[{self.participant_id}] Received global model update for round {self.current_round}")

    async def _handle_training_request(self, message: FederatedMessage):
        """Handle training requests from coordinator"""
        if self.train_data is None:
            print(f"[{self.participant_id}] No training data available, skipping round")
            return

        print(f"[{self.participant_id}] Starting local training for round {self.current_round}")

        # Perform local training
        await self._perform_local_training()

        # Send results back to coordinator
        await self._send_training_results()

    async def _perform_local_training(self):
        """Perform local training with the current global model"""
        if self.train_data is None:
            return

        start_time = time.time()
        self.is_training = True

        X_train, y_train = self.train_data

        # Local training loop
        for epoch in range(self.config.local_epochs):
            metrics = self.model.train_epoch(X_train, y_train, self.config.learning_rate)

            if epoch % 2 == 0:  # Log every 2 epochs
                print(f"[{self.participant_id}] Local epoch {epoch}, loss: {metrics.loss:.4f}")

        training_time = time.time() - start_time
        self.stats.total_training_time += training_time
        self.stats.rounds_participated += 1
        self.is_training = False

        print(f"[{self.participant_id}] Local training complete in {training_time:.2f}s")

    async def _send_training_results(self):
        """Send training results to coordinator"""
        start_time = time.time()

        # Get model parameters (gradients computed implicitly)
        parameters = self.model.get_parameters()

        # Apply differential privacy if enabled
        if self.config.differential_privacy:
            parameters = DifferentialPrivacy.clip_gradients(
                parameters, self.config.max_gradient_norm
            )
            parameters = DifferentialPrivacy.add_gaussian_noise(
                parameters, self.config.privacy_epsilon
            )

        # Compress gradients if enabled
        compression_ratio = 1.0
        if self.config.gradient_compression:
            compressed_params, compression_ratio = GradientCompressor.top_k_compression(
                parameters, self.config.compression_ratio
            )
            parameters = compressed_params
            self.stats.compression_savings += (1 - compression_ratio)

        # Evaluate local model
        test_metrics = None
        if self.test_data is not None:
            X_test, y_test = self.test_data
            test_metrics = self.model.evaluate(X_test, y_test)

        # Prepare message
        payload = {
            'participant_id': self.participant_id,
            'round': self.current_round,
            'parameters': parameters,
            'data_size': len(self.train_data[0]) if self.train_data else 0,
            'compression_ratio': compression_ratio,
            'test_metrics': test_metrics.__dict__ if test_metrics else None,
            'training_time': self.stats.total_training_time
        }

        message = FederatedMessage(
            message_type=MessageType.GRADIENT_UPDATE,
            sender_id=self.participant_id,
            payload=payload
        )

        await self.protocol.send_message('coordinator', message)

        communication_time = time.time() - start_time
        self.stats.total_communication_time += communication_time
        self.stats.last_update_time = time.time()

        print(f"[{self.participant_id}] Sent training results (compression: {compression_ratio:.2f})")

    def set_data(self, train_data: Tuple[np.ndarray, np.ndarray],
                 test_data: Optional[Tuple[np.ndarray, np.ndarray]] = None):
        """Set training and test data for the participant"""
        self.train_data = train_data
        self.test_data = test_data
        self.stats.data_samples = len(train_data[0])
        print(f"[{self.participant_id}] Data set: {len(train_data[0])} training samples")

    async def join_federation(self):
        """Join the federated learning network"""
        message = FederatedMessage(
            message_type=MessageType.JOIN_REQUEST,
            sender_id=self.participant_id,
            payload={'participant_id': self.participant_id}
        )

        await self.protocol.send_message('coordinator', message)
        print(f"[{self.participant_id}] Requested to join federation")

    async def leave_federation(self):
        """Leave the federated learning network"""
        message = FederatedMessage(
            message_type=MessageType.LEAVE_NOTIFICATION,
            sender_id=self.participant_id,
            payload={'participant_id': self.participant_id}
        )

        await self.protocol.send_message('coordinator', message)
        self._stop_event.set()
        print(f"[{self.participant_id}] Left federation")

    def get_statistics(self) -> Dict[str, Any]:
        """Get participant performance statistics"""
        efficiency = 0.0
        if self.stats.total_training_time > 0:
            efficiency = self.stats.data_samples / self.stats.total_training_time

        return {
            'participant_id': self.participant_id,
            'rounds_participated': self.stats.rounds_participated,
            'total_training_time': self.stats.total_training_time,
            'total_communication_time': self.stats.total_communication_time,
            'data_samples': self.stats.data_samples,
            'training_efficiency': efficiency,
            'compression_savings': self.stats.compression_savings,
            'last_active': time.time() - self.stats.last_update_time
        }

    def is_healthy(self) -> bool:
        """Check if participant is healthy and responsive"""
        time_since_update = time.time() - self.stats.last_update_time
        return time_since_update < 300  # Healthy if active within 5 minutes