"""
Federated Learning Performance Benchmarking Suite
Phase 2: Bob's Advanced Performance Analysis System

This module provides comprehensive benchmarking and performance analysis
tools for federated learning systems.
"""

import asyncio
import time
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import json
import statistics

from federated_protocol import FederatedCoordinator, MessageType
from federated_participant import FederatedParticipant, TrainingConfig, create_participant
from aggregation_algorithms import AggregationOrchestrator, create_standard_aggregation_suite
from model_base import SimpleNeuralNetwork

@dataclass
class BenchmarkConfig:
    """Configuration for federated learning benchmarks"""
    num_participants: int = 10
    num_rounds: int = 20
    participants_per_round: int = 8
    local_epochs: int = 3
    batch_size: int = 32
    learning_rate: float = 0.01

    # Data distribution settings
    data_samples_per_participant: int = 1000
    feature_size: int = 20
    num_classes: int = 3
    data_heterogeneity: float = 0.5  # 0 = IID, 1 = highly non-IID

    # Network simulation settings
    simulate_latency: bool = True
    base_latency_ms: float = 50.0
    latency_variance: float = 0.2
    packet_loss_probability: float = 0.01

@dataclass
class RoundMetrics:
    """Comprehensive metrics for a single federated learning round"""
    round_number: int
    participants: List[str]
    aggregation_algorithm: str

    # Training metrics
    avg_local_training_time: float
    max_local_training_time: float
    total_samples_processed: int
    avg_local_loss: float
    global_loss: float

    # Communication metrics
    total_communication_time: float
    avg_participant_comm_time: float
    total_bytes_transferred: int
    compression_ratio: float

    # Convergence metrics
    global_model_change: float
    convergence_delta: float
    participants_converged: int

    # Algorithm-specific metrics
    byzantine_participants_detected: int = 0
    privacy_noise_added: float = 0.0
    aggregation_time: float = 0.0

@dataclass
class BenchmarkResults:
    """Complete results from a federated learning benchmark"""
    config: BenchmarkConfig
    total_runtime: float
    rounds_completed: int
    final_global_loss: float
    convergence_achieved: bool

    # Performance metrics
    avg_round_time: float
    total_communication_overhead: float
    final_model_accuracy: float
    participant_dropout_rate: float

    # Round-by-round details
    round_metrics: List[RoundMetrics] = field(default_factory=list)
    participant_performance: Dict[str, Any] = field(default_factory=dict)
    algorithm_comparison: Dict[str, Any] = field(default_factory=dict)

class FederatedLearningBenchmark:
    """
    Comprehensive benchmarking suite for federated learning performance analysis.

    Features:
    - Multiple aggregation algorithm testing
    - Network condition simulation
    - Data heterogeneity modeling
    - Performance trend analysis
    - Statistical significance testing
    """

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.logger = logging.getLogger("FL-Benchmark")

        # Initialize components
        self.coordinator = None
        self.participants = {}
        self.orchestrator = None
        self.synthetic_data = None

        # Performance tracking
        self.round_metrics = []
        self.participant_metrics = defaultdict(list)

    async def setup_benchmark(self):
        """Initialize benchmark environment"""
        self.logger.info("Setting up federated learning benchmark...")

        # Create coordinator
        self.coordinator = FederatedCoordinator()

        # Setup aggregation algorithms
        self.orchestrator = create_standard_aggregation_suite()

        # Generate synthetic data
        self.synthetic_data = self._generate_synthetic_data()

        # Create participants
        await self._create_participants()

        self.logger.info(f"Benchmark setup complete: {len(self.participants)} participants ready")

    async def _create_participants(self):
        """Create and initialize federated learning participants"""
        training_config = TrainingConfig(
            local_epochs=self.config.local_epochs,
            batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate
        )

        for i in range(self.config.num_participants):
            participant_id = f"participant_{i:03d}"

            # Create participant with neural network
            participant = create_participant(
                participant_id=participant_id,
                input_size=self.config.feature_size,
                hidden_size=32,
                output_size=self.config.num_classes,
                coordinator=self.coordinator,
                config=training_config
            )

            # Set local data (with heterogeneity simulation)
            local_X, local_y = self._get_participant_data(i)
            participant.set_local_data(local_X, local_y)

            # Join federation
            success = await participant.join_federation()
            if success:
                self.participants[participant_id] = participant
            else:
                self.logger.warning(f"Failed to add participant {participant_id}")

    def _generate_synthetic_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic classification dataset"""
        total_samples = self.config.num_participants * self.config.data_samples_per_participant

        # Generate synthetic features
        X = np.random.randn(total_samples, self.config.feature_size)

        # Generate synthetic labels with class structure
        # Create class centers for more realistic data
        class_centers = np.random.randn(self.config.num_classes, self.config.feature_size) * 2

        y = np.zeros(total_samples, dtype=int)
        for i in range(total_samples):
            # Assign label based on distance to class centers
            distances = [np.linalg.norm(X[i] - center) for center in class_centers]
            y[i] = np.argmin(distances)

            # Add some noise to create overlap between classes
            if np.random.random() < 0.1:  # 10% label noise
                y[i] = np.random.randint(0, self.config.num_classes)

        return X, y

    def _get_participant_data(self, participant_idx: int) -> Tuple[np.ndarray, np.ndarray]:
        """Get local data for a specific participant with heterogeneity"""
        X, y = self.synthetic_data

        start_idx = participant_idx * self.config.data_samples_per_participant
        end_idx = start_idx + self.config.data_samples_per_participant

        # Base data slice
        participant_X = X[start_idx:end_idx]
        participant_y = y[start_idx:end_idx]

        # Apply data heterogeneity
        if self.config.data_heterogeneity > 0:
            # Create class imbalance based on heterogeneity level
            target_class = participant_idx % self.config.num_classes
            class_bias_samples = int(self.config.data_heterogeneity * self.config.data_samples_per_participant)

            # Find samples of target class from global dataset
            target_class_indices = np.where(y == target_class)[0]
            if len(target_class_indices) >= class_bias_samples:
                bias_indices = np.random.choice(target_class_indices, class_bias_samples, replace=False)
                bias_X = X[bias_indices]
                bias_y = y[bias_indices]

                # Replace part of participant data with biased data
                replace_count = min(class_bias_samples, len(participant_X) // 2)
                participant_X[:replace_count] = bias_X[:replace_count]
                participant_y[:replace_count] = bias_y[:replace_count]

        return participant_X, participant_y

    async def run_benchmark(self,
                          algorithm_name: str = "fedavg",
                          target_accuracy: float = 0.85,
                          max_rounds: Optional[int] = None) -> BenchmarkResults:
        """Run complete federated learning benchmark"""

        start_time = time.time()
        max_rounds = max_rounds or self.config.num_rounds

        self.logger.info(f"Starting benchmark with {algorithm_name} algorithm, "
                        f"target accuracy: {target_accuracy}")

        # Initialize global model
        sample_participant = next(iter(self.participants.values()))
        global_model = sample_participant.model.get_parameters()

        # Benchmark state
        convergence_achieved = False
        rounds_completed = 0

        for round_num in range(max_rounds):
            round_start = time.time()

            # Select participants for this round
            selected_participants = self._select_participants_for_round(round_num)

            # Run federated learning round
            round_metrics = await self._run_federated_round(
                round_num, selected_participants, global_model, algorithm_name
            )

            # Update global model
            if round_metrics.global_model_change > 0:
                # Get updated global model from coordinator
                global_model = await self._get_updated_global_model()

            self.round_metrics.append(round_metrics)
            rounds_completed += 1

            # Check convergence
            if round_metrics.global_loss < (1.0 - target_accuracy):
                convergence_achieved = True
                self.logger.info(f"Target accuracy achieved in round {round_num}")
                break

            # Log progress
            self.logger.info(f"Round {round_num}: global_loss={round_metrics.global_loss:.4f}, "
                           f"participants={len(selected_participants)}")

        total_runtime = time.time() - start_time

        # Collect final performance metrics
        return await self._compile_benchmark_results(
            total_runtime, rounds_completed, convergence_achieved,
            global_model, algorithm_name
        )

    def _select_participants_for_round(self, round_num: int) -> List[str]:
        """Select participants for federated learning round"""
        available_participants = list(self.participants.keys())

        # Simulate participant availability (some may be offline)
        if round_num > 0:
            dropout_rate = 0.1  # 10% dropout rate
            available_count = int((1.0 - dropout_rate) * len(available_participants))
            available_participants = np.random.choice(
                available_participants, available_count, replace=False
            ).tolist()

        # Select subset for this round
        participants_this_round = min(self.config.participants_per_round, len(available_participants))
        selected = np.random.choice(
            available_participants, participants_this_round, replace=False
        ).tolist()

        return selected

    async def _run_federated_round(self,
                                 round_num: int,
                                 selected_participants: List[str],
                                 global_model: np.ndarray,
                                 algorithm_name: str) -> RoundMetrics:
        """Execute a single federated learning round"""

        # Send global model to participants
        await self._distribute_global_model(global_model, selected_participants)

        # Wait for participant training
        training_start = time.time()
        participant_results = await self._collect_participant_updates(selected_participants)
        total_training_time = time.time() - training_start

        # Perform aggregation
        aggregation_start = time.time()
        new_global_model, agg_metrics = await self._perform_aggregation(
            participant_results, algorithm_name, global_model, round_num
        )
        aggregation_time = time.time() - aggregation_start

        # Compute round metrics
        round_metrics = self._compute_round_metrics(
            round_num, selected_participants, participant_results,
            global_model, new_global_model, agg_metrics,
            total_training_time, aggregation_time, algorithm_name
        )

        return round_metrics

    async def _distribute_global_model(self,
                                     global_model: np.ndarray,
                                     participants: List[str]):
        """Distribute global model to selected participants"""
        for participant_id in participants:
            if participant_id in self.participants:
                participant = self.participants[participant_id]
                participant.model.set_parameters(global_model)

    async def _collect_participant_updates(self,
                                         participants: List[str]) -> Dict[str, Dict[str, Any]]:
        """Collect model updates from participants after local training"""
        results = {}

        # Simulate participants training in parallel
        tasks = []
        for participant_id in participants:
            if participant_id in self.participants:
                participant = self.participants[participant_id]
                task = self._simulate_participant_training(participant)
                tasks.append((participant_id, task))

        # Wait for all participants to complete training
        for participant_id, task in tasks:
            try:
                result = await task
                results[participant_id] = result
            except Exception as e:
                self.logger.error(f"Participant {participant_id} training failed: {e}")

        return results

    async def _simulate_participant_training(self, participant: FederatedParticipant) -> Dict[str, Any]:
        """Simulate participant training with network latency"""

        # Simulate network latency
        if self.config.simulate_latency:
            latency = np.random.normal(
                self.config.base_latency_ms,
                self.config.base_latency_ms * self.config.latency_variance
            ) / 1000.0  # Convert to seconds
            await asyncio.sleep(max(0, latency))

        # Perform training
        training_start = time.time()

        # Get pre-training parameters
        pre_params = participant.model.get_parameters().copy()

        # Simulate local training
        if participant.local_data is not None:
            X, y = participant.local_data
            for epoch in range(participant.config.local_epochs):
                loss = participant.model.train_epoch(X, y)

        training_time = time.time() - training_start

        # Get post-training parameters
        post_params = participant.model.get_parameters()

        # Compute training metrics
        if participant.local_data is not None:
            X, y = participant.local_data
            final_loss = participant.model.compute_loss(X, y)
        else:
            final_loss = 0.0

        return {
            'parameters': post_params,
            'training_time': training_time,
            'final_loss': final_loss,
            'samples_used': X.shape[0] if participant.local_data else 0,
            'parameter_change': np.linalg.norm(post_params - pre_params)
        }

    async def _perform_aggregation(self,
                                 participant_results: Dict[str, Dict[str, Any]],
                                 algorithm_name: str,
                                 global_model: np.ndarray,
                                 round_num: int) -> Tuple[np.ndarray, Any]:
        """Perform model aggregation using specified algorithm"""

        # Extract participant updates and weights
        participant_updates = {}
        participant_weights = {}

        for participant_id, result in participant_results.items():
            participant_updates[participant_id] = result['parameters']
            # Weight by number of samples used
            participant_weights[participant_id] = result['samples_used']

        # Perform aggregation
        new_model, agg_metrics = await self.orchestrator.aggregate_with_algorithm(
            algorithm_name, participant_updates, participant_weights,
            global_model, round_num
        )

        return new_model, agg_metrics

    async def _get_updated_global_model(self) -> np.ndarray:
        """Get the updated global model from coordinator"""
        # In this simulation, we'll return the model from the first participant
        # In a real system, this would be retrieved from the coordinator
        sample_participant = next(iter(self.participants.values()))
        return sample_participant.model.get_parameters()

    def _compute_round_metrics(self,
                             round_num: int,
                             participants: List[str],
                             results: Dict[str, Dict[str, Any]],
                             old_global_model: np.ndarray,
                             new_global_model: np.ndarray,
                             agg_metrics: Any,
                             training_time: float,
                             aggregation_time: float,
                             algorithm_name: str) -> RoundMetrics:
        """Compute comprehensive metrics for a federated learning round"""

        if not results:
            # Return empty metrics for failed rounds
            return RoundMetrics(
                round_number=round_num,
                participants=[],
                aggregation_algorithm=algorithm_name,
                avg_local_training_time=0.0,
                max_local_training_time=0.0,
                total_samples_processed=0,
                avg_local_loss=0.0,
                global_loss=0.0,
                total_communication_time=0.0,
                avg_participant_comm_time=0.0,
                total_bytes_transferred=0,
                compression_ratio=1.0,
                global_model_change=0.0,
                convergence_delta=0.0,
                participants_converged=0
            )

        # Extract metrics from participant results
        training_times = [r['training_time'] for r in results.values()]
        local_losses = [r['final_loss'] for r in results.values()]
        samples_processed = sum(r['samples_used'] for r in results.values())
        parameter_changes = [r['parameter_change'] for r in results.values()]

        # Compute global metrics
        global_model_change = np.linalg.norm(new_global_model - old_global_model)

        # Estimate global loss (average of local losses weighted by samples)
        total_samples = sum(r['samples_used'] for r in results.values())
        if total_samples > 0:
            global_loss = sum(r['final_loss'] * r['samples_used'] for r in results.values()) / total_samples
        else:
            global_loss = 0.0

        # Count converged participants (small parameter change)
        convergence_threshold = 1e-4
        participants_converged = sum(1 for change in parameter_changes if change < convergence_threshold)

        # Communication metrics (simulated)
        model_size_bytes = new_global_model.nbytes
        total_bytes = len(participants) * model_size_bytes * 2  # Upload + download

        return RoundMetrics(
            round_number=round_num,
            participants=participants,
            aggregation_algorithm=algorithm_name,
            avg_local_training_time=statistics.mean(training_times),
            max_local_training_time=max(training_times),
            total_samples_processed=samples_processed,
            avg_local_loss=statistics.mean(local_losses),
            global_loss=global_loss,
            total_communication_time=training_time,  # Approximate
            avg_participant_comm_time=training_time / len(participants),
            total_bytes_transferred=total_bytes,
            compression_ratio=getattr(agg_metrics, 'compression_ratio', 1.0),
            global_model_change=global_model_change,
            convergence_delta=getattr(agg_metrics, 'convergence_delta', global_model_change),
            participants_converged=participants_converged,
            byzantine_participants_detected=getattr(agg_metrics, 'byzantine_participants_detected', 0),
            privacy_noise_added=getattr(agg_metrics, 'privacy_noise_added', 0.0),
            aggregation_time=aggregation_time
        )

    async def _compile_benchmark_results(self,
                                       total_runtime: float,
                                       rounds_completed: int,
                                       convergence_achieved: bool,
                                       final_global_model: np.ndarray,
                                       algorithm_name: str) -> BenchmarkResults:
        """Compile comprehensive benchmark results"""

        # Compute final model accuracy on test data
        final_accuracy = await self._evaluate_global_model_accuracy(final_global_model)

        # Compute aggregate metrics
        avg_round_time = total_runtime / rounds_completed if rounds_completed > 0 else 0.0
        total_comm_overhead = sum(m.total_communication_time for m in self.round_metrics)

        # Compute participant dropout rate
        total_possible_participations = rounds_completed * self.config.participants_per_round
        actual_participations = sum(len(m.participants) for m in self.round_metrics)
        dropout_rate = 1.0 - (actual_participations / total_possible_participations) if total_possible_participations > 0 else 0.0

        # Collect participant performance summaries
        participant_performance = {}
        for participant_id, participant in self.participants.items():
            participant_performance[participant_id] = participant.get_performance_summary()

        # Get algorithm performance comparison
        algorithm_comparison = {
            algorithm_name: self.orchestrator.get_algorithm_performance(algorithm_name)
        }

        final_global_loss = self.round_metrics[-1].global_loss if self.round_metrics else 1.0

        return BenchmarkResults(
            config=self.config,
            total_runtime=total_runtime,
            rounds_completed=rounds_completed,
            final_global_loss=final_global_loss,
            convergence_achieved=convergence_achieved,
            avg_round_time=avg_round_time,
            total_communication_overhead=total_comm_overhead,
            final_model_accuracy=final_accuracy,
            participant_dropout_rate=dropout_rate,
            round_metrics=self.round_metrics,
            participant_performance=participant_performance,
            algorithm_comparison=algorithm_comparison
        )

    async def _evaluate_global_model_accuracy(self, global_model: np.ndarray) -> float:
        """Evaluate global model accuracy on test dataset"""
        # Create test model
        test_model = SimpleNeuralNetwork(
            self.config.feature_size, 32, self.config.num_classes
        )
        test_model.set_parameters(global_model)

        # Use a portion of synthetic data as test set
        X, y = self.synthetic_data
        test_size = 1000
        test_X = X[:test_size]
        test_y = y[:test_size]

        # Compute accuracy
        predictions = test_model.predict(test_X)
        accuracy = np.mean(predictions == test_y)

        return accuracy

class BenchmarkSuite:
    """Suite of benchmark experiments for comprehensive performance analysis"""

    def __init__(self):
        self.logger = logging.getLogger("BenchmarkSuite")
        self.results = {}

    async def run_algorithm_comparison(self,
                                     algorithms: List[str],
                                     base_config: BenchmarkConfig) -> Dict[str, BenchmarkResults]:
        """Compare performance of different aggregation algorithms"""

        self.logger.info(f"Running algorithm comparison: {algorithms}")
        results = {}

        for algorithm in algorithms:
            self.logger.info(f"Testing algorithm: {algorithm}")

            # Create benchmark
            benchmark = FederatedLearningBenchmark(base_config)
            await benchmark.setup_benchmark()

            # Run benchmark
            result = await benchmark.run_benchmark(algorithm_name=algorithm)
            results[algorithm] = result

            self.logger.info(f"{algorithm} completed: {result.rounds_completed} rounds, "
                           f"accuracy={result.final_model_accuracy:.3f}")

        self.results['algorithm_comparison'] = results
        return results

    async def run_scalability_analysis(self,
                                     participant_counts: List[int],
                                     base_config: BenchmarkConfig) -> Dict[int, BenchmarkResults]:
        """Analyze performance scaling with number of participants"""

        self.logger.info(f"Running scalability analysis: {participant_counts} participants")
        results = {}

        for num_participants in participant_counts:
            self.logger.info(f"Testing with {num_participants} participants")

            # Modify config for this test
            config = BenchmarkConfig(
                num_participants=num_participants,
                participants_per_round=min(num_participants, base_config.participants_per_round),
                **{k: v for k, v in base_config.__dict__.items()
                   if k not in ['num_participants', 'participants_per_round']}
            )

            # Create and run benchmark
            benchmark = FederatedLearningBenchmark(config)
            await benchmark.setup_benchmark()
            result = await benchmark.run_benchmark()

            results[num_participants] = result

            self.logger.info(f"{num_participants} participants completed: "
                           f"accuracy={result.final_model_accuracy:.3f}")

        self.results['scalability_analysis'] = results
        return results

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance analysis report"""

        if not self.results:
            return {"error": "No benchmark results available"}

        report = {
            "summary": {
                "total_experiments": len(self.results),
                "experiments_run": list(self.results.keys())
            }
        }

        # Algorithm comparison analysis
        if 'algorithm_comparison' in self.results:
            alg_results = self.results['algorithm_comparison']

            best_algorithm = min(alg_results.keys(),
                               key=lambda alg: alg_results[alg].final_global_loss)

            report['algorithm_analysis'] = {
                "best_performing_algorithm": best_algorithm,
                "algorithm_rankings": {
                    alg: {
                        "final_accuracy": results.final_model_accuracy,
                        "convergence_rounds": results.rounds_completed,
                        "avg_round_time": results.avg_round_time
                    }
                    for alg, results in alg_results.items()
                }
            }

        # Scalability analysis
        if 'scalability_analysis' in self.results:
            scale_results = self.results['scalability_analysis']

            report['scalability_analysis'] = {
                "participant_performance": {
                    num_participants: {
                        "final_accuracy": results.final_model_accuracy,
                        "avg_round_time": results.avg_round_time,
                        "communication_overhead": results.total_communication_overhead
                    }
                    for num_participants, results in scale_results.items()
                }
            }

        return report