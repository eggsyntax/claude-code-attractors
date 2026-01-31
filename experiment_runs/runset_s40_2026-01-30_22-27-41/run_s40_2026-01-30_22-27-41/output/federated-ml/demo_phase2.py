"""
Phase 2 Demonstration - Advanced Federated Learning Features
Demonstrates Bob's implementation of participants, aggregation, and compression.
"""

import asyncio
import numpy as np
import time
from typing import List, Dict, Any

from participant import FederatedParticipant, TrainingConfig, CompressionConfig
from aggregation_engine import AggregationEngine, AggregationConfig
from compression_utils import CompressionManager
from federated_protocol import InMemoryProtocol, FederatedMessage, MessageType
from model_base import SimpleNeuralNetwork


def create_synthetic_dataset(num_samples: int, input_size: int, num_classes: int, noise_level: float = 0.1):
    """Create a synthetic classification dataset."""
    np.random.seed(42)

    # Create structured data with some signal
    X = np.random.randn(num_samples, input_size)

    # Create meaningful labels based on linear combination
    weights = np.random.randn(input_size)
    linear_combination = X @ weights
    probabilities = 1 / (1 + np.exp(-linear_combination))

    # Add noise and convert to class labels
    y = (probabilities + np.random.normal(0, noise_level, num_samples) > 0.5).astype(int)

    return X, y


async def demonstrate_advanced_participants():
    """Demonstrate advanced participant features."""
    print("🔥 Advanced Participant Features Demonstration")
    print("=" * 60)

    protocol = InMemoryProtocol()

    # Create participants with different configurations
    participants = []

    # Participant 1: Basic configuration
    model1 = SimpleNeuralNetwork(input_size=8, hidden_size=16, output_size=2)
    participant1 = FederatedParticipant("basic_participant", model1, protocol)

    # Participant 2: With compression
    model2 = SimpleNeuralNetwork(input_size=8, hidden_size=16, output_size=2)
    compression_config = CompressionConfig(
        enabled=True,
        method="quantization",
        quantization_bits=6
    )
    participant2 = FederatedParticipant(
        "compressed_participant", model2, protocol,
        compression_config=compression_config
    )

    # Participant 3: With advanced training config
    model3 = SimpleNeuralNetwork(input_size=8, hidden_size=16, output_size=2)
    training_config = TrainingConfig(
        local_epochs=10,
        learning_rate=0.02,
        batch_size=16,
        gradient_clipping=True,
        max_gradient_norm=1.0
    )
    participant3 = FederatedParticipant(
        "advanced_participant", model3, protocol,
        training_config=training_config
    )

    participants = [participant1, participant2, participant3]

    # Create different datasets for each participant (simulating heterogeneity)
    for i, participant in enumerate(participants):
        # Each participant gets slightly different data distribution
        X, y = create_synthetic_dataset(200 + i * 50, 8, 2, noise_level=0.1 + i * 0.05)
        participant.set_training_data(X, y)

        # Some participants also get validation data
        if i > 0:
            X_val, y_val = create_synthetic_dataset(50, 8, 2)
            participant.set_validation_data(X_val, y_val)

    print(f"✅ Created {len(participants)} participants with different configurations")

    # Demonstrate local training
    print("\n🏃‍♂️ Local Training Performance:")
    training_results = []

    for participant in participants:
        start_time = time.time()
        result = await participant.perform_local_training()
        training_time = time.time() - start_time

        training_results.append(result)

        print(f"\n📊 {participant.participant_id}:")
        print(f"   Training Loss: {result['training_loss']:.4f}")
        print(f"   Gradient Norm: {result['gradient_norm']:.4f}")
        print(f"   Training Time: {training_time:.3f}s")
        print(f"   Samples: {result['num_samples']}")

        if 'compression_ratio' in result:
            print(f"   Compression Ratio: {result['compression_ratio']:.3f}")

        if 'val_accuracy' in result:
            print(f"   Validation Accuracy: {result['val_accuracy']:.3f}")

    # Demonstrate statistics tracking
    print("\n📈 Participant Statistics:")
    for participant in participants:
        stats = participant.get_statistics()
        print(f"\n🔍 {participant.participant_id}:")
        print(f"   Parameters: {stats['model_stats']['num_parameters']}")
        print(f"   Parameter Norm: {stats['model_stats']['parameter_norm']:.4f}")
        print(f"   Training History Length: {len(stats['training_history'])}")

    return training_results


def demonstrate_aggregation_algorithms():
    """Demonstrate different aggregation algorithms."""
    print("\n\n🔧 Aggregation Algorithms Demonstration")
    print("=" * 60)

    # Create mock participant updates with varying quality
    base_update = np.random.randn(100) * 0.1

    # Normal participants
    normal_updates = []
    for i in range(4):
        update = {
            'participant_id': f'normal_{i}',
            'parameter_updates': (base_update + np.random.randn(100) * 0.02).tolist(),
            'num_samples': 100 + i * 20,
            'gradient_norm': 0.1 + i * 0.02,
            'training_loss': 0.5 - i * 0.05
        }
        normal_updates.append(update)

    # Potential byzantine participant
    byzantine_update = {
        'participant_id': 'suspicious',
        'parameter_updates': (np.random.randn(100) * 2.0).tolist(),  # Much larger
        'num_samples': 50,
        'gradient_norm': 5.0,  # Very large gradient
        'training_loss': 2.0
    }

    all_updates = normal_updates + [byzantine_update]
    current_global_model = np.random.randn(100)

    # Test different aggregation algorithms
    algorithms = ["fedavg", "median", "trimmed_mean", "krum"]

    results = {}
    for algorithm in algorithms:
        print(f"\n🔍 Testing {algorithm.upper()} Algorithm:")

        config = AggregationConfig(
            algorithm=algorithm,
            byzantine_tolerance=0.2,
            trimming_ratio=0.15 if algorithm == "trimmed_mean" else 0.1
        )

        engine = AggregationEngine(config)
        new_model, metrics = engine.aggregate_updates(all_updates, current_global_model)

        results[algorithm] = {'model': new_model, 'metrics': metrics}

        print(f"   Participants Used: {metrics['num_participants']}")
        print(f"   Update Norm: {metrics['update_norm']:.4f}")
        print(f"   Model Change: {metrics['model_change_norm']:.4f}")

        # Byzantine detection info
        byzantine_info = metrics['byzantine_detection']
        if byzantine_info['suspicious_participants']:
            print(f"   🚨 Suspicious: {byzantine_info['suspicious_participants']}")
        else:
            print(f"   ✅ No suspicious participants detected")

        if algorithm == "krum" and 'selected_participant' in metrics:
            print(f"   🎯 Selected: {metrics['selected_participant']}")

    # Compare algorithm robustness
    print(f"\n📊 Algorithm Comparison:")
    print(f"{'Algorithm':<15} {'Update Norm':<12} {'Model Change':<12} {'Byzantine Detected'}")
    print("-" * 60)

    for algo, result in results.items():
        metrics = result['metrics']
        byzantine_detected = len(metrics['byzantine_detection']['suspicious_participants']) > 0
        print(f"{algo:<15} {metrics['update_norm']:<12.4f} {metrics['model_change_norm']:<12.4f} {'Yes' if byzantine_detected else 'No'}")

    return results


def demonstrate_compression_techniques():
    """Demonstrate different compression techniques."""
    print("\n\n🗜️ Compression Techniques Demonstration")
    print("=" * 60)

    # Create test gradient data
    np.random.seed(42)
    large_gradient = np.random.randn(10000)  # Simulate large model gradients

    # Test different compression methods
    compression_manager = CompressionManager()

    compression_tests = [
        ("Quantization 8-bit", "quantization", {"bits": 8}),
        ("Quantization 4-bit", "quantization", {"bits": 4}),
        ("Top-K Sparsification", "sparsification", {"sparsity_ratio": 0.9, "method": "topk"}),
        ("Random Sparsification", "sparsification", {"sparsity_ratio": 0.8, "method": "random"}),
        ("Hybrid Compression", "hybrid", {"quantization_bits": 6, "sparsity_ratio": 0.7})
    ]

    print(f"🔬 Testing compression on {len(large_gradient):,} parameters")
    print(f"{'Method':<20} {'Ratio':<8} {'Error':<8} {'Time(ms)':<10} {'SNR(dB)':<10}")
    print("-" * 70)

    compression_results = []
    for name, method, kwargs in compression_tests:
        compressed_data, stats = compression_manager.compress(large_gradient, method, **kwargs)

        result = {
            'name': name,
            'method': method,
            'stats': stats
        }
        compression_results.append(result)

        # Display results
        ratio = stats.compression_ratio
        error = stats.error_metrics.get('relative_error', 0)
        comp_time = stats.compression_time * 1000  # Convert to ms
        snr = stats.error_metrics.get('snr_db', 0)

        print(f"{name:<20} {ratio:<8.3f} {error:<8.4f} {comp_time:<10.2f} {snr:<10.1f}")

    # Demonstrate compression-decompression cycle
    print(f"\n🔄 Compression-Decompression Cycle Example:")
    test_method = "hybrid"
    compressed_data, stats = compression_manager.compress(
        large_gradient, test_method,
        quantization_bits=6, sparsity_ratio=0.8
    )

    print(f"   Original size: {stats.original_size:,} bytes")
    print(f"   Compressed size: {stats.compressed_size:,} bytes")
    print(f"   Compression ratio: {stats.compression_ratio:.3f}")
    print(f"   Relative error: {stats.error_metrics['relative_error']:.6f}")

    # Get compression summary
    summary = compression_manager.get_compression_summary()
    print(f"\n📋 Compression Summary:")
    print(f"   Total compressions: {summary['total_compressions']}")
    print(f"   Methods used: {', '.join(summary['methods_used'])}")

    return compression_results


async def demonstrate_full_federated_round():
    """Demonstrate a complete federated learning round."""
    print("\n\n🌐 Complete Federated Learning Round")
    print("=" * 60)

    # Setup
    protocol = InMemoryProtocol()
    aggregation_config = AggregationConfig(
        algorithm="fedavg",
        momentum=0.1,
        learning_rate_decay=0.99
    )
    aggregation_engine = AggregationEngine(aggregation_config)

    # Create diverse participants
    participants = []
    participant_configs = [
        {"compression": False, "epochs": 5, "lr": 0.01},
        {"compression": True, "epochs": 8, "lr": 0.015},
        {"compression": True, "epochs": 3, "lr": 0.02},
    ]

    for i, config in enumerate(participant_configs):
        model = SimpleNeuralNetwork(input_size=6, hidden_size=12, output_size=2)

        training_config = TrainingConfig(
            local_epochs=config["epochs"],
            learning_rate=config["lr"],
            gradient_clipping=True
        )

        compression_config = CompressionConfig(
            enabled=config["compression"],
            method="quantization",
            quantization_bits=6
        ) if config["compression"] else CompressionConfig()

        participant = FederatedParticipant(
            f"participant_{i}", model, protocol,
            training_config=training_config,
            compression_config=compression_config
        )

        # Heterogeneous data
        X, y = create_synthetic_dataset(150 + i * 30, 6, 2, noise_level=0.1 + i * 0.02)
        participant.set_training_data(X, y)

        participants.append(participant)

    print(f"🏗️ Created federation with {len(participants)} diverse participants")

    # Initialize global model
    global_model = np.random.randn(len(participants[0].model.get_parameters()))
    print(f"📐 Global model size: {len(global_model):,} parameters")

    # Simulate multiple rounds
    num_rounds = 5
    round_metrics = []

    for round_num in range(num_rounds):
        print(f"\n🔄 Round {round_num + 1}/{num_rounds}")

        # Distribute global model to all participants
        for participant in participants:
            participant.model.set_parameters(global_model)
            participant.current_round = round_num

        # Collect updates from participants
        round_start_time = time.time()
        participant_updates = []

        for participant in participants:
            print(f"   🏃‍♂️ {participant.participant_id} training...")
            update = await participant.perform_local_training()
            participant_updates.append(update)

        # Aggregate updates
        print(f"   🔧 Aggregating {len(participant_updates)} updates...")
        new_global_model, agg_metrics = aggregation_engine.aggregate_updates(
            participant_updates, global_model
        )

        round_time = time.time() - round_start_time
        agg_metrics['round_time'] = round_time

        # Update global model
        model_change = np.linalg.norm(new_global_model - global_model)
        global_model = new_global_model

        round_metrics.append(agg_metrics)

        # Display round results
        print(f"   📊 Model change: {model_change:.6f}")
        print(f"   ⏱️ Round time: {round_time:.3f}s")

        # Check for byzantine detection
        byzantine_info = agg_metrics['byzantine_detection']
        if byzantine_info['suspicious_participants']:
            print(f"   🚨 Suspicious participants: {byzantine_info['suspicious_participants']}")

    # Final analysis
    print(f"\n📈 Federation Training Complete!")
    print(f"\n🔍 Final Analysis:")

    # Convergence analysis
    model_changes = [metrics['model_change_norm'] for metrics in round_metrics]
    print(f"   Model changes: {' → '.join([f'{change:.6f}' for change in model_changes])}")

    convergence_trend = "Converging" if model_changes[-1] < model_changes[0] else "Diverging"
    print(f"   Convergence trend: {convergence_trend}")

    # Performance analysis
    avg_round_time = np.mean([metrics['round_time'] for metrics in round_metrics])
    total_participants = sum(metrics['participants_count'] for metrics in round_metrics)

    print(f"   Average round time: {avg_round_time:.3f}s")
    print(f"   Total participant updates: {total_participants}")

    # Get aggregation statistics
    agg_stats = aggregation_engine.get_aggregation_statistics()
    print(f"   Total rounds completed: {agg_stats['total_rounds']}")

    return {
        'final_global_model': global_model,
        'round_metrics': round_metrics,
        'aggregation_stats': agg_stats,
        'participant_count': len(participants)
    }


async def main():
    """Run complete Phase 2 demonstration."""
    print("🚀 PHASE 2 DEMONSTRATION - Bob's Advanced Features")
    print("🎯 Federated Learning with Participants, Aggregation & Compression")
    print("=" * 80)

    try:
        # Run demonstrations
        training_results = await demonstrate_advanced_participants()
        aggregation_results = demonstrate_aggregation_algorithms()
        compression_results = demonstrate_compression_techniques()
        federation_results = await demonstrate_full_federated_round()

        print("\n\n🎉 PHASE 2 DEMONSTRATION COMPLETE! 🎉")
        print("=" * 80)
        print("✅ Advanced Participants: Local training with compression & monitoring")
        print("✅ Aggregation Engine: Multiple algorithms with byzantine tolerance")
        print("✅ Compression Utils: Quantization, sparsification, and hybrid methods")
        print("✅ Complete Federation: End-to-end federated learning with all features")
        print("\n🎯 Key Achievements:")
        print(f"   • {len(training_results)} participants with diverse configurations")
        print(f"   • {len(aggregation_results)} aggregation algorithms tested")
        print(f"   • {len(compression_results)} compression techniques demonstrated")
        print(f"   • {federation_results['participant_count']}-participant federation completed")
        print(f"   • {federation_results['aggregation_stats']['total_rounds']} rounds executed")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())