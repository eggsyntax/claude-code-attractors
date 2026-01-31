"""
Advanced Aggregation Algorithms for Federated Learning
=====================================================

Implements sophisticated aggregation algorithms including FedAvg,
Byzantine fault tolerance, and weighted aggregation strategies.

Author: Bob (Claude Code Agent)
Phase: 2 - Advanced Aggregation & Optimization
"""

import numpy as np
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

from federated_participant import GradientCompressor


class AggregationStrategy(Enum):
    """Available aggregation strategies"""
    FEDAVG = "federated_averaging"
    WEIGHTED_FEDAVG = "weighted_federated_averaging"
    BYZANTINE_ROBUST = "byzantine_robust"
    MEDIAN = "coordinate_wise_median"
    TRIMMED_MEAN = "trimmed_mean"
    KRUM = "krum"


@dataclass
class AggregationResult:
    """Result of parameter aggregation"""
    aggregated_parameters: Dict[str, np.ndarray]
    participant_weights: Dict[str, float]
    strategy_used: AggregationStrategy
    convergence_metrics: Dict[str, float]
    byzantine_detected: List[str]  # IDs of participants detected as byzantine
    aggregation_time: float


class BaseAggregator(ABC):
    """Abstract base class for aggregation algorithms"""

    @abstractmethod
    def aggregate(self,
                  participant_updates: Dict[str, Dict[str, np.ndarray]],
                  participant_data_sizes: Dict[str, int],
                  global_parameters: Dict[str, np.ndarray]) -> AggregationResult:
        """Aggregate participant updates into global parameters"""
        pass

    def _decompress_if_needed(self, parameters: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Decompress parameters if they're in compressed format"""
        if not parameters:
            return {}

        # Check if parameters are compressed (contain 'indices' key)
        first_key = next(iter(parameters.keys()))
        if isinstance(parameters[first_key], dict) and 'indices' in parameters[first_key]:
            return GradientCompressor.decompress_top_k(parameters)
        return parameters


class FedAvgAggregator(BaseAggregator):
    """Standard Federated Averaging (FedAvg) algorithm"""

    def aggregate(self,
                  participant_updates: Dict[str, Dict[str, np.ndarray]],
                  participant_data_sizes: Dict[str, int],
                  global_parameters: Dict[str, np.ndarray]) -> AggregationResult:
        start_time = time.time()

        # Decompress parameters if needed
        decompressed_updates = {}
        for participant_id, params in participant_updates.items():
            decompressed_updates[participant_id] = self._decompress_if_needed(params)

        # Calculate weights based on data size
        total_data = sum(participant_data_sizes.values())
        weights = {pid: size / total_data for pid, size in participant_data_sizes.items()}

        # Aggregate parameters
        aggregated = {}
        layer_names = next(iter(decompressed_updates.values())).keys()

        for layer_name in layer_names:
            weighted_sum = None
            for participant_id, params in decompressed_updates.items():
                weight = weights[participant_id]
                if weighted_sum is None:
                    weighted_sum = weight * params[layer_name]
                else:
                    weighted_sum += weight * params[layer_name]

            aggregated[layer_name] = weighted_sum

        # Calculate convergence metrics
        convergence_metrics = self._calculate_convergence_metrics(
            aggregated, global_parameters, decompressed_updates
        )

        return AggregationResult(
            aggregated_parameters=aggregated,
            participant_weights=weights,
            strategy_used=AggregationStrategy.WEIGHTED_FEDAVG,
            convergence_metrics=convergence_metrics,
            byzantine_detected=[],
            aggregation_time=time.time() - start_time
        )

    def _calculate_convergence_metrics(self,
                                     aggregated: Dict[str, np.ndarray],
                                     global_parameters: Dict[str, np.ndarray],
                                     participant_updates: Dict[str, Dict[str, np.ndarray]]) -> Dict[str, float]:
        """Calculate convergence metrics for monitoring"""
        metrics = {}

        # Parameter change magnitude
        if global_parameters:
            total_change = 0.0
            total_params = 0.0

            for layer_name in aggregated.keys():
                if layer_name in global_parameters:
                    change = np.sum((aggregated[layer_name] - global_parameters[layer_name]) ** 2)
                    total_change += change
                    total_params += np.sum(global_parameters[layer_name] ** 2)

            metrics['parameter_change_norm'] = np.sqrt(total_change)
            metrics['relative_change'] = np.sqrt(total_change / (total_params + 1e-8))

        # Participant agreement (variance in updates)
        if len(participant_updates) > 1:
            variances = []
            for layer_name in aggregated.keys():
                layer_updates = [params[layer_name] for params in participant_updates.values()]
                layer_var = np.var(layer_updates, axis=0).mean()
                variances.append(layer_var)

            metrics['participant_variance'] = np.mean(variances)

        return metrics


class ByzantineRobustAggregator(BaseAggregator):
    """Byzantine fault-tolerant aggregation using Krum and Trimmed Mean"""

    def __init__(self, byzantine_ratio: float = 0.2, use_krum: bool = True):
        self.byzantine_ratio = byzantine_ratio
        self.use_krum = use_krum

    def aggregate(self,
                  participant_updates: Dict[str, Dict[str, np.ndarray]],
                  participant_data_sizes: Dict[str, int],
                  global_parameters: Dict[str, np.ndarray]) -> AggregationResult:
        start_time = time.time()

        # Decompress parameters
        decompressed_updates = {}
        for participant_id, params in participant_updates.items():
            decompressed_updates[participant_id] = self._decompress_if_needed(params)

        # Detect and filter byzantine participants
        if self.use_krum:
            filtered_updates, byzantine_detected = self._krum_selection(decompressed_updates)
        else:
            filtered_updates, byzantine_detected = self._trimmed_mean_selection(decompressed_updates)

        # Aggregate remaining participants using FedAvg
        if filtered_updates:
            filtered_data_sizes = {pid: participant_data_sizes.get(pid, 1)
                                 for pid in filtered_updates.keys()}

            fedavg = FedAvgAggregator()
            result = fedavg.aggregate(filtered_updates, filtered_data_sizes, global_parameters)

            # Update result metadata
            result.strategy_used = AggregationStrategy.BYZANTINE_ROBUST
            result.byzantine_detected = byzantine_detected
            result.aggregation_time = time.time() - start_time

            return result
        else:
            # Fallback if all participants are detected as byzantine
            return AggregationResult(
                aggregated_parameters=global_parameters,
                participant_weights={},
                strategy_used=AggregationStrategy.BYZANTINE_ROBUST,
                convergence_metrics={},
                byzantine_detected=list(participant_updates.keys()),
                aggregation_time=time.time() - start_time
            )

    def _krum_selection(self, participant_updates: Dict[str, Dict[str, np.ndarray]]) -> Tuple[Dict, List[str]]:
        """Select non-byzantine participants using Krum algorithm"""
        participant_ids = list(participant_updates.keys())
        n = len(participant_ids)
        f = int(n * self.byzantine_ratio)  # Maximum number of byzantine participants

        if n <= 2 * f + 1:
            # Not enough participants for byzantine tolerance
            return participant_updates, []

        # Calculate pairwise distances
        distances = {}
        for i, pid1 in enumerate(participant_ids):
            distances[pid1] = {}
            for j, pid2 in enumerate(participant_ids):
                if i != j:
                    dist = self._calculate_parameter_distance(
                        participant_updates[pid1], participant_updates[pid2]
                    )
                    distances[pid1][pid2] = dist

        # Calculate Krum scores (sum of f closest neighbors)
        scores = {}
        for pid in participant_ids:
            sorted_distances = sorted(distances[pid].values())
            krum_score = sum(sorted_distances[:n - f - 1])
            scores[pid] = krum_score

        # Select participant with minimum Krum score
        selected_pid = min(scores, key=scores.get)

        # For multi-Krum, select top k participants
        k = max(1, n - 2 * f)
        sorted_participants = sorted(participant_ids, key=lambda x: scores[x])
        selected_participants = sorted_participants[:k]

        filtered_updates = {pid: participant_updates[pid] for pid in selected_participants}
        byzantine_detected = [pid for pid in participant_ids if pid not in selected_participants]

        return filtered_updates, byzantine_detected

    def _trimmed_mean_selection(self, participant_updates: Dict[str, Dict[str, np.ndarray]]) -> Tuple[Dict, List[str]]:
        """Select non-byzantine participants using trimmed mean"""
        participant_ids = list(participant_updates.keys())
        n = len(participant_ids)
        trim_ratio = self.byzantine_ratio

        # Calculate coordinate-wise median for each parameter
        aggregated = {}
        layer_names = next(iter(participant_updates.values())).keys()

        for layer_name in layer_names:
            # Collect all parameter values for this layer
            layer_params = []
            for pid in participant_ids:
                layer_params.append(participant_updates[pid][layer_name])

            # Calculate trimmed mean
            layer_params = np.array(layer_params)
            aggregated[layer_name] = self._trimmed_mean(layer_params, trim_ratio)

        # Identify participants that deviate significantly from trimmed mean
        byzantine_detected = []
        threshold = 2.0  # Deviation threshold

        for pid in participant_ids:
            total_deviation = 0.0
            total_norm = 0.0

            for layer_name in layer_names:
                deviation = np.sum((participant_updates[pid][layer_name] - aggregated[layer_name]) ** 2)
                norm = np.sum(aggregated[layer_name] ** 2)
                total_deviation += deviation
                total_norm += norm

            relative_deviation = np.sqrt(total_deviation / (total_norm + 1e-8))
            if relative_deviation > threshold:
                byzantine_detected.append(pid)

        # Return non-byzantine participants
        filtered_updates = {pid: participant_updates[pid] for pid in participant_ids
                          if pid not in byzantine_detected}

        return filtered_updates, byzantine_detected

    def _calculate_parameter_distance(self, params1: Dict[str, np.ndarray], params2: Dict[str, np.ndarray]) -> float:
        """Calculate Euclidean distance between parameter sets"""
        total_distance = 0.0
        for layer_name in params1.keys():
            if layer_name in params2:
                diff = params1[layer_name] - params2[layer_name]
                total_distance += np.sum(diff ** 2)
        return np.sqrt(total_distance)

    def _trimmed_mean(self, values: np.ndarray, trim_ratio: float) -> np.ndarray:
        """Calculate trimmed mean along the first axis"""
        n = values.shape[0]
        trim_count = int(n * trim_ratio)

        if trim_count == 0:
            return np.mean(values, axis=0)

        # Sort along first axis
        sorted_values = np.sort(values, axis=0)

        # Remove top and bottom trim_count values
        if trim_count * 2 >= n:
            # Use median if trimming would remove all values
            return np.median(values, axis=0)

        trimmed = sorted_values[trim_count:-trim_count]
        return np.mean(trimmed, axis=0)


class AdaptiveAggregator(BaseAggregator):
    """Adaptive aggregation that switches strategies based on network conditions"""

    def __init__(self):
        self.fedavg = FedAvgAggregator()
        self.byzantine_robust = ByzantineRobustAggregator()
        self.history = []

    def aggregate(self,
                  participant_updates: Dict[str, Dict[str, np.ndarray]],
                  participant_data_sizes: Dict[str, int],
                  global_parameters: Dict[str, np.ndarray]) -> AggregationResult:

        n_participants = len(participant_updates)

        # Use byzantine robust aggregation if:
        # 1. Many participants (> 10)
        # 2. High variance in recent rounds
        # 3. Network shows signs of instability

        use_byzantine_robust = False

        if n_participants >= 10:
            use_byzantine_robust = True

        # Check for high variance in recent aggregations
        if len(self.history) >= 3:
            recent_variances = [h['convergence_metrics'].get('participant_variance', 0.0)
                              for h in self.history[-3:]]
            avg_variance = np.mean(recent_variances)

            if avg_variance > 0.1:  # High variance threshold
                use_byzantine_robust = True

        # Choose aggregation strategy
        if use_byzantine_robust:
            result = self.byzantine_robust.aggregate(
                participant_updates, participant_data_sizes, global_parameters
            )
            result.strategy_used = AggregationStrategy.BYZANTINE_ROBUST
        else:
            result = self.fedavg.aggregate(
                participant_updates, participant_data_sizes, global_parameters
            )

        # Store history for adaptive decisions
        self.history.append({
            'strategy': result.strategy_used,
            'convergence_metrics': result.convergence_metrics,
            'n_participants': n_participants,
            'byzantine_detected': len(result.byzantine_detected)
        })

        # Keep only recent history
        if len(self.history) > 10:
            self.history = self.history[-10:]

        return result


class AggregatorFactory:
    """Factory for creating aggregation algorithms"""

    @staticmethod
    def create_aggregator(strategy: AggregationStrategy, **kwargs) -> BaseAggregator:
        """Create aggregator instance based on strategy"""
        if strategy == AggregationStrategy.FEDAVG:
            return FedAvgAggregator()
        elif strategy == AggregationStrategy.WEIGHTED_FEDAVG:
            return FedAvgAggregator()
        elif strategy == AggregationStrategy.BYZANTINE_ROBUST:
            return ByzantineRobustAggregator(**kwargs)
        elif strategy == AggregationStrategy.KRUM:
            return ByzantineRobustAggregator(use_krum=True, **kwargs)
        else:
            return AdaptiveAggregator()


def demonstrate_aggregation_algorithms():
    """Demonstrate different aggregation algorithms with synthetic data"""
    print("=== Aggregation Algorithms Demonstration ===\n")

    # Create synthetic parameter updates
    layer_shapes = {
        'layer1': (10, 5),
        'layer2': (5, 1),
        'bias1': (5,),
        'bias2': (1,)
    }

    # Generate honest participant updates
    honest_updates = {}
    for i in range(8):
        pid = f"honest_{i}"
        params = {}
        for layer_name, shape in layer_shapes.items():
            # Add small random noise to base parameters
            params[layer_name] = np.random.normal(0, 0.1, shape)
        honest_updates[pid] = params

    # Generate byzantine participant updates
    byzantine_updates = {}
    for i in range(2):
        pid = f"byzantine_{i}"
        params = {}
        for layer_name, shape in layer_shapes.items():
            # Large random values (byzantine behavior)
            params[layer_name] = np.random.normal(0, 10.0, shape)
        byzantine_updates[pid] = params

    # Combine all updates
    all_updates = {**honest_updates, **byzantine_updates}
    data_sizes = {pid: 100 for pid in all_updates.keys()}

    # Initialize global parameters
    global_params = {}
    for layer_name, shape in layer_shapes.items():
        global_params[layer_name] = np.zeros(shape)

    # Test different aggregation strategies
    strategies = [
        AggregationStrategy.FEDAVG,
        AggregationStrategy.BYZANTINE_ROBUST
    ]

    for strategy in strategies:
        print(f"Testing {strategy.value}:")

        aggregator = AggregatorFactory.create_aggregator(strategy)
        result = aggregator.aggregate(all_updates, data_sizes, global_params)

        print(f"  - Aggregation time: {result.aggregation_time:.3f}s")
        print(f"  - Byzantine detected: {len(result.byzantine_detected)}")
        print(f"  - Strategy used: {result.strategy_used.value}")

        if result.convergence_metrics:
            for metric, value in result.convergence_metrics.items():
                print(f"  - {metric}: {value:.4f}")

        print()


if __name__ == "__main__":
    demonstrate_aggregation_algorithms()