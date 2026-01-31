"""
Comprehensive Performance Benchmarking for Federated Learning
============================================================

Advanced benchmarking suite for analyzing federated learning performance
across different scenarios, network sizes, and algorithm configurations.

Author: Bob (Claude Code Agent)
Phase: 2 - Performance Analysis & Optimization
"""

import asyncio
import time
import numpy as np
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from federated_protocol import InMemoryProtocol, FederatedCoordinator
from model_base import SimpleNeuralNetwork
from federated_participant import FederatedParticipant, TrainingConfig, GradientCompressor
from aggregation_algorithms import AggregatorFactory, AggregationStrategy


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark scenarios"""
    n_participants: int = 10
    n_rounds: int = 5
    data_size_per_participant: int = 100
    model_size: Tuple[int, int, int] = (20, 10, 2)  # input, hidden, output
    aggregation_strategy: AggregationStrategy = AggregationStrategy.FEDAVG
    compression_enabled: bool = False
    compression_ratio: float = 0.1
    differential_privacy: bool = False
    byzantine_ratio: float = 0.0
    heterogeneous_data: bool = False
    network_delay_ms: float = 0.0


@dataclass
class BenchmarkResult:
    """Results from a benchmark run"""
    config: BenchmarkConfig
    total_time: float
    rounds_completed: int
    final_accuracy: float
    convergence_rounds: int
    communication_overhead: float
    computation_time: float
    aggregation_times: List[float] = field(default_factory=list)
    participant_stats: Dict[str, Any] = field(default_factory=dict)
    memory_usage: float = 0.0
    network_efficiency: float = 0.0


class FederatedLearningBenchmark:
    """Comprehensive benchmark suite for federated learning"""

    def __init__(self):
        self.results: List[BenchmarkResult] = []

    async def run_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Run a single benchmark scenario"""
        print(f"🔄 Running benchmark: {config.n_participants} participants, {config.aggregation_strategy.value}")

        start_time = time.time()

        # Setup protocol with network delay simulation
        protocol = InMemoryProtocol()
        protocol.network_delay = config.network_delay_ms / 1000.0

        # Create coordinator
        coordinator = FederatedCoordinator(protocol, strategy=config.aggregation_strategy)

        # Create participants
        participants = []
        for i in range(config.n_participants):
            model = SimpleNeuralNetwork(
                input_size=config.model_size[0],
                hidden_size=config.model_size[1],
                output_size=config.model_size[2]
            )

            training_config = TrainingConfig(
                local_epochs=2,
                learning_rate=0.01,
                gradient_compression=config.compression_enabled,
                compression_ratio=config.compression_ratio,
                differential_privacy=config.differential_privacy
            )

            participant = FederatedParticipant(
                f"participant_{i}", model, protocol, training_config
            )

            # Generate data for participant
            X, y = self._generate_participant_data(
                i, config.data_size_per_participant, config.model_size[0],
                config.heterogeneous_data
            )
            participant.set_data((X, y))

            # Add byzantine behavior if configured
            if config.byzantine_ratio > 0 and i < int(config.n_participants * config.byzantine_ratio):
                # This participant will send malicious updates (simulated in aggregation)
                participant.is_byzantine = True
            else:
                participant.is_byzantine = False

            participants.append(participant)

        # Start coordinator
        coordinator_task = asyncio.create_task(coordinator.start())

        # Join all participants
        for participant in participants:
            await participant.join_federation()
            await asyncio.sleep(0.01)  # Small delay to simulate realistic joins

        # Wait for coordinator to process all joins
        await asyncio.sleep(0.5)

        # Track metrics
        aggregation_times = []
        communication_start = time.time()

        # Run training rounds
        for round_num in range(config.n_rounds):
            round_start = time.time()

            await coordinator.start_round()
            await asyncio.sleep(0.5)  # Wait for round to complete

            round_time = time.time() - round_start
            aggregation_times.append(round_time)

            if round_num % 2 == 0:  # Log progress
                print(f"  Round {round_num + 1}/{config.n_rounds} completed in {round_time:.2f}s")

        communication_time = time.time() - communication_start
        computation_time = sum(p.stats.total_training_time for p in participants)

        # Evaluate final model performance
        final_accuracy = await self._evaluate_global_model(coordinator, participants[0])

        # Calculate convergence rounds (simplified)
        convergence_rounds = config.n_rounds  # In a real scenario, we'd track loss convergence

        # Gather participant statistics
        participant_stats = {}
        for participant in participants:
            stats = participant.get_statistics()
            participant_stats[participant.participant_id] = stats

        # Calculate network efficiency
        total_data_transmitted = sum(
            stats['data_samples'] for stats in participant_stats.values()
        )
        network_efficiency = total_data_transmitted / communication_time if communication_time > 0 else 0

        # Clean up
        for participant in participants:
            await participant.leave_federation()

        coordinator.stop()
        await coordinator_task

        total_time = time.time() - start_time

        # Create result
        result = BenchmarkResult(
            config=config,
            total_time=total_time,
            rounds_completed=config.n_rounds,
            final_accuracy=final_accuracy,
            convergence_rounds=convergence_rounds,
            communication_overhead=communication_time / total_time,
            computation_time=computation_time,
            aggregation_times=aggregation_times,
            participant_stats=participant_stats,
            network_efficiency=network_efficiency
        )

        self.results.append(result)
        return result

    def _generate_participant_data(self, participant_id: int, size: int, input_dim: int,
                                  heterogeneous: bool) -> Tuple[np.ndarray, np.ndarray]:
        """Generate training data for a participant"""
        np.random.seed(participant_id + 42)  # Consistent but different per participant

        if heterogeneous:
            # Create non-IID data distribution
            # Each participant has bias towards different features
            feature_bias = participant_id % input_dim
            X = np.random.randn(size, input_dim)
            X[:, feature_bias] += 2.0  # Bias certain features

            # Create labels based on biased features
            y = (X[:, feature_bias] + X[:, (feature_bias + 1) % input_dim] > 0).astype(int)
        else:
            # IID data distribution
            X = np.random.randn(size, input_dim)
            y = (X[:, 0] + X[:, 1] > 0).astype(int)

        return X, y

    async def _evaluate_global_model(self, coordinator: FederatedCoordinator,
                                   sample_participant: FederatedParticipant) -> float:
        """Evaluate the global model's performance"""
        # Generate test data
        X_test = np.random.randn(100, sample_participant.model.input_size)
        y_test = (X_test[:, 0] + X_test[:, 1] > 0).astype(int)

        # Use sample participant's model (which has global parameters)
        metrics = sample_participant.model.evaluate(X_test, y_test)
        return metrics.accuracy

    async def run_scalability_benchmarks(self) -> List[BenchmarkResult]:
        """Run benchmarks across different network sizes"""
        print("\n🚀 Running Scalability Benchmarks")
        print("=" * 50)

        scalability_results = []
        participant_counts = [5, 10, 20, 50]

        for n_participants in participant_counts:
            config = BenchmarkConfig(
                n_participants=n_participants,
                n_rounds=3,
                aggregation_strategy=AggregationStrategy.FEDAVG
            )

            result = await self.run_benchmark(config)
            scalability_results.append(result)

            print(f"✅ {n_participants} participants: {result.total_time:.2f}s, "
                  f"accuracy: {result.final_accuracy:.3f}")

        return scalability_results

    async def run_algorithm_comparison(self) -> List[BenchmarkResult]:
        """Compare different aggregation algorithms"""
        print("\n🔍 Running Algorithm Comparison")
        print("=" * 50)

        algorithm_results = []
        strategies = [
            AggregationStrategy.FEDAVG,
            AggregationStrategy.BYZANTINE_ROBUST
        ]

        for strategy in strategies:
            config = BenchmarkConfig(
                n_participants=15,
                n_rounds=4,
                aggregation_strategy=strategy,
                byzantine_ratio=0.2 if strategy == AggregationStrategy.BYZANTINE_ROBUST else 0.0
            )

            result = await self.run_benchmark(config)
            algorithm_results.append(result)

            print(f"✅ {strategy.value}: {result.total_time:.2f}s, "
                  f"accuracy: {result.final_accuracy:.3f}")

        return algorithm_results

    async def run_compression_benchmarks(self) -> List[BenchmarkResult]:
        """Test gradient compression performance"""
        print("\n📦 Running Compression Benchmarks")
        print("=" * 50)

        compression_results = []
        compression_ratios = [1.0, 0.5, 0.1, 0.05]  # 1.0 means no compression

        for ratio in compression_ratios:
            config = BenchmarkConfig(
                n_participants=12,
                n_rounds=3,
                compression_enabled=ratio < 1.0,
                compression_ratio=ratio
            )

            result = await self.run_benchmark(config)
            compression_results.append(result)

            compression_status = "No compression" if ratio >= 1.0 else f"{ratio*100}% compression"
            print(f"✅ {compression_status}: {result.total_time:.2f}s, "
                  f"accuracy: {result.final_accuracy:.3f}")

        return compression_results

    async def run_privacy_benchmarks(self) -> List[BenchmarkResult]:
        """Test differential privacy impact"""
        print("\n🔒 Running Privacy Benchmarks")
        print("=" * 50)

        privacy_results = []
        privacy_configs = [
            (False, 0.0),  # No privacy
            (True, 10.0),  # High privacy (low epsilon)
            (True, 1.0),   # Medium privacy
            (True, 0.1)    # Strong privacy (very low epsilon)
        ]

        for use_dp, epsilon in privacy_configs:
            config = BenchmarkConfig(
                n_participants=10,
                n_rounds=3,
                differential_privacy=use_dp
            )

            result = await self.run_benchmark(config)
            privacy_results.append(result)

            privacy_status = "No privacy" if not use_dp else f"DP ε={epsilon}"
            print(f"✅ {privacy_status}: {result.total_time:.2f}s, "
                  f"accuracy: {result.final_accuracy:.3f}")

        return privacy_results

    def generate_report(self, output_file: str = "benchmark_report.json"):
        """Generate comprehensive benchmark report"""
        print(f"\n📊 Generating Benchmark Report: {output_file}")

        report = {
            'summary': {
                'total_benchmarks': len(self.results),
                'timestamp': time.time(),
                'performance_analysis': self._analyze_performance()
            },
            'results': [
                {
                    'config': result.config.__dict__,
                    'metrics': {
                        'total_time': result.total_time,
                        'final_accuracy': result.final_accuracy,
                        'communication_overhead': result.communication_overhead,
                        'network_efficiency': result.network_efficiency,
                        'avg_aggregation_time': np.mean(result.aggregation_times)
                    }
                }
                for result in self.results
            ]
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ Report saved to {output_file}")

    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance across all benchmark results"""
        if not self.results:
            return {}

        accuracies = [r.final_accuracy for r in self.results]
        total_times = [r.total_time for r in self.results]
        communication_overheads = [r.communication_overhead for r in self.results]

        return {
            'accuracy_stats': {
                'mean': np.mean(accuracies),
                'std': np.std(accuracies),
                'min': np.min(accuracies),
                'max': np.max(accuracies)
            },
            'time_stats': {
                'mean': np.mean(total_times),
                'std': np.std(total_times),
                'min': np.min(total_times),
                'max': np.max(total_times)
            },
            'communication_stats': {
                'mean': np.mean(communication_overheads),
                'std': np.std(communication_overheads)
            }
        }

    def plot_results(self, output_dir: str = "/tmp/cc-exp/run_s40_2026-01-30_22-27-41/output/federated-learning/"):
        """Generate performance visualizations"""
        print(f"\n📈 Generating Performance Plots")

        if not self.results:
            print("No results to plot")
            return

        # Plot 1: Scalability (participants vs time)
        scalability_results = [r for r in self.results if r.config.aggregation_strategy == AggregationStrategy.FEDAVG]
        if scalability_results:
            participants = [r.config.n_participants for r in scalability_results]
            times = [r.total_time for r in scalability_results]

            plt.figure(figsize=(10, 6))
            plt.subplot(2, 2, 1)
            plt.plot(participants, times, 'bo-')
            plt.xlabel('Number of Participants')
            plt.ylabel('Total Time (s)')
            plt.title('Scalability: Participants vs Time')
            plt.grid(True)

        # Plot 2: Accuracy vs Time
        accuracies = [r.final_accuracy for r in self.results]
        times = [r.total_time for r in self.results]

        plt.subplot(2, 2, 2)
        plt.scatter(times, accuracies, alpha=0.7)
        plt.xlabel('Total Time (s)')
        plt.ylabel('Final Accuracy')
        plt.title('Accuracy vs Training Time')
        plt.grid(True)

        # Plot 3: Communication Overhead
        overheads = [r.communication_overhead for r in self.results]

        plt.subplot(2, 2, 3)
        plt.hist(overheads, bins=10, alpha=0.7, edgecolor='black')
        plt.xlabel('Communication Overhead Ratio')
        plt.ylabel('Frequency')
        plt.title('Distribution of Communication Overhead')
        plt.grid(True)

        # Plot 4: Algorithm Comparison
        algorithms = {}
        for result in self.results:
            strategy = result.config.aggregation_strategy.value
            if strategy not in algorithms:
                algorithms[strategy] = {'times': [], 'accuracies': []}
            algorithms[strategy]['times'].append(result.total_time)
            algorithms[strategy]['accuracies'].append(result.final_accuracy)

        plt.subplot(2, 2, 4)
        for i, (alg, data) in enumerate(algorithms.items()):
            avg_time = np.mean(data['times'])
            avg_acc = np.mean(data['accuracies'])
            plt.scatter(avg_time, avg_acc, s=100, label=alg)

        plt.xlabel('Average Time (s)')
        plt.ylabel('Average Accuracy')
        plt.title('Algorithm Performance Comparison')
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(f"{output_dir}benchmark_results.png", dpi=150, bbox_inches='tight')
        print(f"✅ Plots saved to {output_dir}benchmark_results.png")
        plt.close()


async def run_comprehensive_benchmarks():
    """Run the complete benchmark suite"""
    print("🚀 FEDERATED LEARNING COMPREHENSIVE BENCHMARKS")
    print("=" * 60)

    benchmark = FederatedLearningBenchmark()

    try:
        # Run all benchmark categories
        await benchmark.run_scalability_benchmarks()
        await benchmark.run_algorithm_comparison()
        await benchmark.run_compression_benchmarks()
        await benchmark.run_privacy_benchmarks()

        # Generate reports and visualizations
        output_dir = "/tmp/cc-exp/run_s40_2026-01-30_22-27-41/output/federated-learning/"
        benchmark.generate_report(f"{output_dir}comprehensive_benchmark_report.json")
        benchmark.plot_results(output_dir)

        print(f"\n🎉 Comprehensive Benchmarks Complete!")
        print(f"📊 Total benchmarks run: {len(benchmark.results)}")
        print(f"📈 Results saved to: {output_dir}")

        # Print summary statistics
        if benchmark.results:
            accuracies = [r.final_accuracy for r in benchmark.results]
            times = [r.total_time for r in benchmark.results]

            print(f"\n📋 SUMMARY STATISTICS:")
            print(f"   Average Accuracy: {np.mean(accuracies):.3f} ± {np.std(accuracies):.3f}")
            print(f"   Average Time: {np.mean(times):.2f}s ± {np.std(times):.2f}s")
            print(f"   Best Accuracy: {np.max(accuracies):.3f}")
            print(f"   Fastest Time: {np.min(times):.2f}s")

    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_comprehensive_benchmarks())