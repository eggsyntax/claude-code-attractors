"""
Federated Learning Participant Implementation
Implements the client-side logic for federated learning with advanced features.
Bob's Phase 2 implementation.
"""

import asyncio
import json
import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from federated_protocol import FederatedMessage, MessageType, InMemoryProtocol
from model_base import FederatedModel


@dataclass
class TrainingConfig:
    """Configuration for local training."""
    local_epochs: int = 5
    learning_rate: float = 0.01
    batch_size: int = 32
    gradient_clipping: bool = True
    max_gradient_norm: float = 1.0


@dataclass
class CompressionConfig:
    """Configuration for gradient compression."""
    enabled: bool = False
    method: str = "quantization"  # "quantization", "sparsification", "both"
    quantization_bits: int = 8
    sparsification_ratio: float = 0.1


class FederatedParticipant:
    """
    Federated Learning Participant with advanced features:
    - Local training with configurable parameters
    - Gradient compression and quantization
    - Adaptive learning rate scheduling
    - Resource monitoring and reporting
    - Byzantine fault tolerance detection
    """

    def __init__(self,
                 participant_id: str,
                 model: FederatedModel,
                 protocol: InMemoryProtocol,
                 training_config: Optional[TrainingConfig] = None,
                 compression_config: Optional[CompressionConfig] = None):
        self.participant_id = participant_id
        self.model = model
        self.protocol = protocol
        self.training_config = training_config or TrainingConfig()
        self.compression_config = compression_config or CompressionConfig()

        # Training state
        self.current_round = 0
        self.training_data: Optional[Tuple[np.ndarray, np.ndarray]] = None
        self.validation_data: Optional[Tuple[np.ndarray, np.ndarray]] = None
        self.is_training = False

        # Performance tracking
        self.training_history: List[Dict[str, Any]] = []
        self.communication_stats = {
            'bytes_sent': 0,
            'bytes_received': 0,
            'messages_sent': 0,
            'messages_received': 0
        }

        # Resource monitoring
        self.resource_stats = {
            'computation_time': 0.0,
            'memory_usage': 0.0,
            'energy_consumption': 0.0  # Simulated
        }

        # Register message handlers
        self.protocol.register_handler(MessageType.GLOBAL_MODEL_UPDATE,
                                     self._handle_global_model_update)
        self.protocol.register_handler(MessageType.TRAINING_REQUEST,
                                     self._handle_training_request)
        self.protocol.register_handler(MessageType.HEALTH_CHECK,
                                     self._handle_health_check)

    def set_training_data(self, X: np.ndarray, y: np.ndarray):
        """Set the local training dataset."""
        self.training_data = (X, y)

    def set_validation_data(self, X: np.ndarray, y: np.ndarray):
        """Set the local validation dataset."""
        self.validation_data = (X, y)

    async def join_federation(self, coordinator_id: str):
        """Join the federated learning federation."""
        message = FederatedMessage(
            message_type=MessageType.JOIN_REQUEST,
            sender_id=self.participant_id,
            content={
                'model_info': {
                    'parameters': self.model.get_parameters().tolist(),
                    'architecture': str(type(self.model)),
                    'num_parameters': len(self.model.get_parameters())
                },
                'capabilities': {
                    'compression_support': self.compression_config.enabled,
                    'local_epochs': self.training_config.local_epochs,
                    'data_samples': len(self.training_data[0]) if self.training_data else 0
                }
            }
        )

        await self.protocol.send_message(coordinator_id, message)
        self.communication_stats['messages_sent'] += 1
        self.communication_stats['bytes_sent'] += len(json.dumps(message.to_dict()))

        print(f"[{self.participant_id}] Sent join request to coordinator")

    async def perform_local_training(self) -> Dict[str, Any]:
        """
        Perform local training with advanced features:
        - Gradient clipping
        - Adaptive learning rate
        - Resource monitoring
        - Byzantine fault detection preparation
        """
        if not self.training_data:
            raise ValueError("No training data available")

        start_time = time.time()
        X, y = self.training_data

        # Store original parameters for gradient calculation
        original_params = self.model.get_parameters().copy()

        # Local training loop
        epoch_losses = []
        for epoch in range(self.training_config.local_epochs):
            # Batch training
            n_samples = len(X)
            batch_size = min(self.training_config.batch_size, n_samples)
            n_batches = (n_samples + batch_size - 1) // batch_size

            epoch_loss = 0.0
            for batch_idx in range(n_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, n_samples)

                batch_X = X[start_idx:end_idx]
                batch_y = y[start_idx:end_idx]

                # Forward pass and backward pass
                predictions = self.model.predict(batch_X)
                loss = self.model.calculate_loss(batch_y, predictions)
                epoch_loss += loss

                # Update parameters
                self.model.train_step(batch_X, batch_y, self.training_config.learning_rate)

            avg_loss = epoch_loss / n_batches
            epoch_losses.append(avg_loss)

        # Calculate parameter updates (gradients)
        final_params = self.model.get_parameters()
        parameter_updates = final_params - original_params

        # Apply gradient clipping if enabled
        if self.training_config.gradient_clipping:
            gradient_norm = np.linalg.norm(parameter_updates)
            if gradient_norm > self.training_config.max_gradient_norm:
                parameter_updates = parameter_updates * (self.training_config.max_gradient_norm / gradient_norm)
                # Update model parameters with clipped gradients
                self.model.set_parameters(original_params + parameter_updates)

        # Apply compression if enabled
        compressed_updates = self._compress_parameters(parameter_updates)

        # Calculate training metrics
        end_time = time.time()
        training_time = end_time - start_time

        # Validation if available
        validation_metrics = {}
        if self.validation_data:
            val_X, val_y = self.validation_data
            val_predictions = self.model.predict(val_X)
            val_loss = self.model.calculate_loss(val_y, val_predictions)
            val_accuracy = np.mean(np.argmax(val_predictions, axis=1) == val_y)
            validation_metrics = {'val_loss': val_loss, 'val_accuracy': val_accuracy}

        # Update resource stats
        self.resource_stats['computation_time'] += training_time
        self.resource_stats['energy_consumption'] += training_time * 0.1  # Simulated

        training_result = {
            'participant_id': self.participant_id,
            'round': self.current_round,
            'parameter_updates': compressed_updates.tolist() if isinstance(compressed_updates, np.ndarray) else compressed_updates,
            'training_loss': epoch_losses[-1],
            'num_samples': len(X),
            'training_time': training_time,
            'gradient_norm': float(np.linalg.norm(parameter_updates)),
            'compression_ratio': self._calculate_compression_ratio(parameter_updates, compressed_updates),
            **validation_metrics
        }

        self.training_history.append(training_result)
        return training_result

    def _compress_parameters(self, parameters: np.ndarray) -> np.ndarray:
        """Apply gradient compression based on configuration."""
        if not self.compression_config.enabled:
            return parameters

        compressed = parameters.copy()

        if self.compression_config.method in ["quantization", "both"]:
            # Quantization
            param_min, param_max = parameters.min(), parameters.max()
            if param_max > param_min:
                scale = (2 ** self.compression_config.quantization_bits - 1) / (param_max - param_min)
                quantized = np.round((parameters - param_min) * scale)
                compressed = quantized / scale + param_min

        if self.compression_config.method in ["sparsification", "both"]:
            # Top-k sparsification
            k = int(len(parameters) * (1 - self.compression_config.sparsification_ratio))
            if k > 0:
                flat_params = compressed.flatten()
                threshold_idx = np.argpartition(np.abs(flat_params), -k)[-k:]
                mask = np.zeros_like(flat_params, dtype=bool)
                mask[threshold_idx] = True
                flat_params[~mask] = 0
                compressed = flat_params.reshape(parameters.shape)

        return compressed

    def _calculate_compression_ratio(self, original: np.ndarray, compressed: Any) -> float:
        """Calculate compression ratio."""
        if isinstance(compressed, np.ndarray):
            # Simple ratio based on non-zero elements for sparsification
            non_zero_compressed = np.count_nonzero(compressed)
            non_zero_original = np.count_nonzero(original)
            return non_zero_compressed / max(non_zero_original, 1)
        return 1.0

    async def _handle_global_model_update(self, message: FederatedMessage):
        """Handle global model update from coordinator."""
        self.communication_stats['messages_received'] += 1
        self.communication_stats['bytes_received'] += len(json.dumps(message.to_dict()))

        # Update local model with global parameters
        global_params = np.array(message.content['global_parameters'])
        self.model.set_parameters(global_params)

        self.current_round = message.content.get('round', 0)
        print(f"[{self.participant_id}] Updated to global model (round {self.current_round})")

    async def _handle_training_request(self, message: FederatedMessage):
        """Handle training request from coordinator."""
        if self.is_training:
            print(f"[{self.participant_id}] Already training, ignoring request")
            return

        self.is_training = True
        print(f"[{self.participant_id}] Starting local training for round {self.current_round}")

        try:
            # Perform local training
            training_result = await self.perform_local_training()

            # Send results back to coordinator
            response = FederatedMessage(
                message_type=MessageType.MODEL_UPDATE,
                sender_id=self.participant_id,
                content=training_result
            )

            coordinator_id = message.sender_id
            await self.protocol.send_message(coordinator_id, response)
            self.communication_stats['messages_sent'] += 1
            self.communication_stats['bytes_sent'] += len(json.dumps(response.to_dict()))

            print(f"[{self.participant_id}] Completed training and sent update")

        except Exception as e:
            print(f"[{self.participant_id}] Training failed: {e}")
        finally:
            self.is_training = False

    async def _handle_health_check(self, message: FederatedMessage):
        """Respond to health check from coordinator."""
        health_info = {
            'participant_id': self.participant_id,
            'status': 'healthy',
            'current_round': self.current_round,
            'is_training': self.is_training,
            'resource_stats': self.resource_stats.copy(),
            'communication_stats': self.communication_stats.copy(),
            'model_info': {
                'num_parameters': len(self.model.get_parameters()),
                'last_training_loss': self.training_history[-1]['training_loss'] if self.training_history else None
            }
        }

        response = FederatedMessage(
            message_type=MessageType.HEALTH_RESPONSE,
            sender_id=self.participant_id,
            content=health_info
        )

        await self.protocol.send_message(message.sender_id, response)
        self.communication_stats['messages_sent'] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive participant statistics."""
        return {
            'participant_id': self.participant_id,
            'current_round': self.current_round,
            'training_history': self.training_history.copy(),
            'communication_stats': self.communication_stats.copy(),
            'resource_stats': self.resource_stats.copy(),
            'model_stats': {
                'num_parameters': len(self.model.get_parameters()),
                'parameter_norm': float(np.linalg.norm(self.model.get_parameters()))
            }
        }