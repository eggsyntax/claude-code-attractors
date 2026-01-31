"""
Advanced Federated Learning Aggregation Engine
Implements multiple aggregation algorithms with byzantine fault tolerance.
Bob's Phase 2 implementation.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time


@dataclass
class AggregationConfig:
    """Configuration for aggregation algorithms."""
    algorithm: str = "fedavg"  # "fedavg", "median", "trimmed_mean", "krum", "bulyan"
    byzantine_tolerance: float = 0.1  # Fraction of byzantine clients tolerated
    trimming_ratio: float = 0.1  # For trimmed mean
    krum_m: int = 1  # Number of closest updates for Krum
    momentum: float = 0.0  # Server-side momentum
    learning_rate_decay: float = 1.0  # Learning rate decay factor


class BaseAggregator(ABC):
    """Abstract base class for aggregation algorithms."""

    @abstractmethod
    def aggregate(self,
                  updates: List[Dict[str, Any]],
                  current_global_model: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Aggregate client updates into a new global model.

        Args:
            updates: List of client update dictionaries
            current_global_model: Current global model parameters

        Returns:
            Tuple of (new_global_model, aggregation_metrics)
        """
        pass


class FedAvgAggregator(BaseAggregator):
    """Federated Averaging (FedAvg) aggregation algorithm."""

    def __init__(self, config: AggregationConfig):
        self.config = config
        self.momentum_buffer = None

    def aggregate(self,
                  updates: List[Dict[str, Any]],
                  current_global_model: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Weighted average aggregation based on number of samples."""
        if not updates:
            return current_global_model, {'error': 'No updates to aggregate'}

        # Extract parameters and weights
        parameter_updates = []
        sample_weights = []

        for update in updates:
            params = np.array(update['parameter_updates'])
            num_samples = update['num_samples']
            parameter_updates.append(params)
            sample_weights.append(num_samples)

        # Convert to numpy arrays
        parameter_updates = np.array(parameter_updates)
        sample_weights = np.array(sample_weights, dtype=float)

        # Normalize weights
        total_samples = np.sum(sample_weights)
        normalized_weights = sample_weights / total_samples

        # Weighted average
        aggregated_update = np.average(parameter_updates, axis=0, weights=normalized_weights)

        # Apply server-side momentum if configured
        if self.config.momentum > 0:
            if self.momentum_buffer is None:
                self.momentum_buffer = np.zeros_like(aggregated_update)

            self.momentum_buffer = (self.config.momentum * self.momentum_buffer +
                                  (1 - self.config.momentum) * aggregated_update)
            aggregated_update = self.momentum_buffer

        # Update global model
        new_global_model = current_global_model + aggregated_update

        # Calculate aggregation metrics
        metrics = {
            'algorithm': 'fedavg',
            'num_participants': len(updates),
            'total_samples': int(total_samples),
            'update_norm': float(np.linalg.norm(aggregated_update)),
            'weight_distribution': normalized_weights.tolist(),
            'parameter_variance': float(np.var(parameter_updates.flatten()))
        }

        return new_global_model, metrics


class MedianAggregator(BaseAggregator):
    """Coordinate-wise median aggregation for byzantine fault tolerance."""

    def aggregate(self,
                  updates: List[Dict[str, Any]],
                  current_global_model: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Coordinate-wise median aggregation."""
        if not updates:
            return current_global_model, {'error': 'No updates to aggregate'}

        parameter_updates = np.array([np.array(update['parameter_updates']) for update in updates])

        # Coordinate-wise median
        aggregated_update = np.median(parameter_updates, axis=0)

        new_global_model = current_global_model + aggregated_update

        metrics = {
            'algorithm': 'median',
            'num_participants': len(updates),
            'update_norm': float(np.linalg.norm(aggregated_update)),
            'coordinate_mad': float(np.median(np.abs(parameter_updates - np.median(parameter_updates, axis=0, keepdims=True))))
        }

        return new_global_model, metrics


class TrimmedMeanAggregator(BaseAggregator):
    """Trimmed mean aggregation for byzantine fault tolerance."""

    def __init__(self, config: AggregationConfig):
        self.config = config

    def aggregate(self,
                  updates: List[Dict[str, Any]],
                  current_global_model: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Trimmed mean aggregation by removing extreme values."""
        if not updates:
            return current_global_model, {'error': 'No updates to aggregate'}

        parameter_updates = np.array([np.array(update['parameter_updates']) for update in updates])

        # Calculate how many updates to trim
        num_updates = len(parameter_updates)
        num_trim = int(num_updates * self.config.trimming_ratio)

        # Sort along each coordinate and trim extremes
        sorted_updates = np.sort(parameter_updates, axis=0)
        trimmed_updates = sorted_updates[num_trim:num_updates-num_trim]

        # Mean of remaining updates
        aggregated_update = np.mean(trimmed_updates, axis=0)

        new_global_model = current_global_model + aggregated_update

        metrics = {
            'algorithm': 'trimmed_mean',
            'num_participants': len(updates),
            'num_trimmed': num_trim * 2,
            'trimming_ratio': self.config.trimming_ratio,
            'update_norm': float(np.linalg.norm(aggregated_update))
        }

        return new_global_model, metrics


class KrumAggregator(BaseAggregator):
    """Krum aggregation algorithm for byzantine fault tolerance."""

    def __init__(self, config: AggregationConfig):
        self.config = config

    def aggregate(self,
                  updates: List[Dict[str, Any]],
                  current_global_model: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Krum aggregation based on distance to closest neighbors."""
        if not updates:
            return current_global_model, {'error': 'No updates to aggregate'}

        parameter_updates = np.array([np.array(update['parameter_updates']) for update in updates])
        num_updates = len(parameter_updates)

        # Calculate pairwise distances
        distances = np.zeros((num_updates, num_updates))
        for i in range(num_updates):
            for j in range(num_updates):
                distances[i, j] = np.linalg.norm(parameter_updates[i] - parameter_updates[j])**2

        # For each update, find sum of distances to m closest neighbors
        m = min(self.config.krum_m, num_updates - 1)
        scores = []

        for i in range(num_updates):
            # Sort distances for update i and sum the m smallest (excluding itself)
            sorted_distances = np.sort(distances[i])
            score = np.sum(sorted_distances[1:m+1])  # Exclude distance to self (0)
            scores.append(score)

        # Select update with smallest score
        best_update_idx = np.argmin(scores)
        aggregated_update = parameter_updates[best_update_idx]

        new_global_model = current_global_model + aggregated_update

        metrics = {
            'algorithm': 'krum',
            'num_participants': len(updates),
            'selected_participant': updates[best_update_idx]['participant_id'],
            'krum_score': float(scores[best_update_idx]),
            'update_norm': float(np.linalg.norm(aggregated_update)),
            'score_distribution': scores
        }

        return new_global_model, metrics


class AggregationEngine:
    """
    Main aggregation engine supporting multiple algorithms and advanced features.
    """

    def __init__(self, config: AggregationConfig = None):
        self.config = config or AggregationConfig()
        self.aggregator = self._create_aggregator()

        # Performance tracking
        self.aggregation_history: List[Dict[str, Any]] = []
        self.round_number = 0

    def _create_aggregator(self) -> BaseAggregator:
        """Create the appropriate aggregator based on configuration."""
        if self.config.algorithm == "fedavg":
            return FedAvgAggregator(self.config)
        elif self.config.algorithm == "median":
            return MedianAggregator(self.config)
        elif self.config.algorithm == "trimmed_mean":
            return TrimmedMeanAggregator(self.config)
        elif self.config.algorithm == "krum":
            return KrumAggregator(self.config)
        else:
            raise ValueError(f"Unknown aggregation algorithm: {self.config.algorithm}")

    def aggregate_updates(self,
                         participant_updates: List[Dict[str, Any]],
                         current_global_model: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Aggregate participant updates with quality checks and monitoring.
        """
        start_time = time.time()

        # Quality checks
        filtered_updates = self._filter_updates(participant_updates)

        if not filtered_updates:
            return current_global_model, {
                'error': 'No valid updates after filtering',
                'original_count': len(participant_updates)
            }

        # Detect potential byzantine behavior
        byzantine_detection = self._detect_byzantine_behavior(filtered_updates)

        # Perform aggregation
        new_global_model, aggregation_metrics = self.aggregator.aggregate(
            filtered_updates, current_global_model
        )

        aggregation_time = time.time() - start_time

        # Comprehensive metrics
        round_metrics = {
            'round': self.round_number,
            'aggregation_time': aggregation_time,
            'participants_count': len(participant_updates),
            'filtered_count': len(filtered_updates),
            'byzantine_detection': byzantine_detection,
            'model_change_norm': float(np.linalg.norm(new_global_model - current_global_model)),
            'global_model_norm': float(np.linalg.norm(new_global_model)),
            **aggregation_metrics
        }

        self.aggregation_history.append(round_metrics)
        self.round_number += 1

        return new_global_model, round_metrics

    def _filter_updates(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out invalid or suspicious updates."""
        filtered = []

        for update in updates:
            # Check for required fields
            if not all(key in update for key in ['parameter_updates', 'num_samples', 'participant_id']):
                continue

            # Check for valid parameter updates
            try:
                params = np.array(update['parameter_updates'])
                if np.any(np.isnan(params)) or np.any(np.isinf(params)):
                    continue
            except (ValueError, TypeError):
                continue

            # Check for reasonable gradient norm (basic sanity check)
            gradient_norm = update.get('gradient_norm', 0)
            if gradient_norm > 1000:  # Very large gradients are suspicious
                continue

            filtered.append(update)

        return filtered

    def _detect_byzantine_behavior(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Basic byzantine behavior detection."""
        if len(updates) < 2:
            return {'suspicious_participants': [], 'detection_method': 'insufficient_data'}

        parameter_updates = np.array([np.array(update['parameter_updates']) for update in updates])

        # Calculate distances from median
        median_update = np.median(parameter_updates, axis=0)
        distances = [np.linalg.norm(params - median_update)
                    for params in parameter_updates]

        # Mark outliers as potentially byzantine
        threshold = np.median(distances) + 2 * np.std(distances)
        suspicious_indices = [i for i, dist in enumerate(distances) if dist > threshold]

        suspicious_participants = [updates[i]['participant_id'] for i in suspicious_indices]

        return {
            'suspicious_participants': suspicious_participants,
            'detection_method': 'distance_from_median',
            'threshold': float(threshold),
            'distances': distances
        }

    def get_aggregation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive aggregation statistics."""
        if not self.aggregation_history:
            return {'error': 'No aggregation history available'}

        recent_rounds = self.aggregation_history[-10:]  # Last 10 rounds

        return {
            'total_rounds': len(self.aggregation_history),
            'config': {
                'algorithm': self.config.algorithm,
                'byzantine_tolerance': self.config.byzantine_tolerance
            },
            'recent_performance': {
                'avg_aggregation_time': np.mean([r['aggregation_time'] for r in recent_rounds]),
                'avg_participants': np.mean([r['participants_count'] for r in recent_rounds]),
                'avg_model_change': np.mean([r['model_change_norm'] for r in recent_rounds])
            },
            'byzantine_detection': {
                'total_detected': sum(len(r['byzantine_detection']['suspicious_participants'])
                                    for r in self.aggregation_history),
                'rounds_with_detection': sum(1 for r in self.aggregation_history
                                           if r['byzantine_detection']['suspicious_participants'])
            },
            'full_history': self.aggregation_history
        }