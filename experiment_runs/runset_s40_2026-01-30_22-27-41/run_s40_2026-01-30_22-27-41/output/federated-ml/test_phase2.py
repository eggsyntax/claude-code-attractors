"""
Comprehensive Test Suite for Phase 2 - Bob's Implementation
Tests participant functionality, aggregation engine, and compression utilities.
"""

import asyncio
import numpy as np
import time
from typing import List, Dict, Any

from participant import FederatedParticipant, TrainingConfig, CompressionConfig
from aggregation_engine import AggregationEngine, AggregationConfig
from compression_utils import CompressionManager, QuantizationCompressor, SparsificationCompressor
from federated_protocol import InMemoryProtocol
from model_base import SimpleNeuralNetwork


class TestFederatedParticipant:
    """Test suite for FederatedParticipant class."""

    def test_participant_initialization(self):
        """Test participant initialization with different configurations."""
        protocol = InMemoryProtocol("test_protocol")
        model = SimpleNeuralNetwork(input_size=10, hidden_size=5, output_size=2)

        # Basic initialization
        participant = FederatedParticipant("test_participant", model, protocol)
        assert participant.participant_id == "test_participant"
        assert participant.current_round == 0
        assert not participant.is_training

        # With custom configs
        training_config = TrainingConfig(local_epochs=3, learning_rate=0.05)
        compression_config = CompressionConfig(enabled=True, method="quantization")

        participant_custom = FederatedParticipant(
            "custom_participant", model, protocol,
            training_config=training_config,
            compression_config=compression_config
        )

        assert participant_custom.training_config.local_epochs == 3
        assert participant_custom.compression_config.enabled

    def test_local_training(self):
        """Test local training functionality."""
        protocol = InMemoryProtocol("test_protocol")
        model = SimpleNeuralNetwork(input_size=4, hidden_size=8, output_size=2)
        participant = FederatedParticipant("test_participant", model, protocol)

        # Create synthetic training data
        np.random.seed(42)
        X = np.random.randn(100, 4)
        y = np.random.randint(0, 2, 100)

        participant.set_training_data(X, y)

        # Run local training
        training_result = asyncio.run(participant.perform_local_training())

        # Verify training result structure
        assert 'participant_id' in training_result
        assert 'parameter_updates' in training_result
        assert 'training_loss' in training_result
        assert 'num_samples' in training_result
        assert 'training_time' in training_result

        # Verify reasonable values
        assert training_result['participant_id'] == "test_participant"
        assert training_result['num_samples'] == 100
        assert training_result['training_time'] > 0
        assert len(training_result['parameter_updates']) > 0

        print("✅ Local training test passed")

    def test_gradient_compression(self):
        """Test gradient compression functionality."""
        protocol = InMemoryProtocol("test_protocol")
        model = SimpleNeuralNetwork(input_size=4, hidden_size=8, output_size=2)

        compression_config = CompressionConfig(
            enabled=True,
            method="quantization",
            quantization_bits=4
        )

        participant = FederatedParticipant(
            "compress_participant", model, protocol,
            compression_config=compression_config
        )

        # Test compression
        test_params = np.random.randn(100)
        compressed = participant._compress_parameters(test_params)

        # Should be different from original due to compression
        assert not np.array_equal(test_params, compressed)

        # Calculate compression ratio
        ratio = participant._calculate_compression_ratio(test_params, compressed)
        assert 0 <= ratio <= 1

        print("✅ Gradient compression test passed")

    def test_statistics_tracking(self):
        """Test statistics and metrics tracking."""
        protocol = InMemoryProtocol("test_protocol")
        model = SimpleNeuralNetwork(input_size=4, hidden_size=8, output_size=2)
        participant = FederatedParticipant("stats_participant", model, protocol)

        # Get initial statistics
        initial_stats = participant.get_statistics()

        assert 'participant_id' in initial_stats
        assert 'communication_stats' in initial_stats
        assert 'resource_stats' in initial_stats
        assert 'model_stats' in initial_stats

        # Verify structure
        comm_stats = initial_stats['communication_stats']
        assert all(key in comm_stats for key in ['bytes_sent', 'bytes_received', 'messages_sent', 'messages_received'])

        print("✅ Statistics tracking test passed")


class TestAggregationEngine:
    """Test suite for AggregationEngine."""

    def test_fedavg_aggregation(self):
        """Test FedAvg aggregation algorithm."""
        config = AggregationConfig(algorithm="fedavg")
        engine = AggregationEngine(config)

        # Create mock participant updates
        current_model = np.random.randn(50)
        updates = [
            {
                'participant_id': 'p1',
                'parameter_updates': np.random.randn(50).tolist(),
                'num_samples': 100,
                'gradient_norm': 0.5
            },
            {
                'participant_id': 'p2',
                'parameter_updates': np.random.randn(50).tolist(),
                'num_samples': 150,
                'gradient_norm': 0.7
            },
            {
                'participant_id': 'p3',
                'parameter_updates': np.random.randn(50).tolist(),
                'num_samples': 80,
                'gradient_norm': 0.3
            }
        ]

        # Perform aggregation
        new_model, metrics = engine.aggregate_updates(updates, current_model)

        # Verify output
        assert len(new_model) == len(current_model)
        assert 'algorithm' in metrics
        assert metrics['algorithm'] == 'fedavg'
        assert metrics['num_participants'] == 3
        assert 'update_norm' in metrics

        print("✅ FedAvg aggregation test passed")

    def test_byzantine_tolerance_algorithms(self):
        """Test byzantine fault-tolerant aggregation algorithms."""
        algorithms = ["median", "trimmed_mean", "krum"]

        current_model = np.random.randn(20)

        # Create updates with one potential byzantine participant
        normal_updates = [
            {
                'participant_id': f'normal_{i}',
                'parameter_updates': (np.random.randn(20) * 0.1).tolist(),
                'num_samples': 100,
                'gradient_norm': 0.1
            }
            for i in range(4)
        ]

        # Byzantine update with large gradient
        byzantine_update = {
            'participant_id': 'byzantine',
            'parameter_updates': (np.random.randn(20) * 10).tolist(),  # Large update
            'num_samples': 100,
            'gradient_norm': 10.0
        }

        all_updates = normal_updates + [byzantine_update]

        for algorithm in algorithms:
            config = AggregationConfig(algorithm=algorithm)
            engine = AggregationEngine(config)

            new_model, metrics = engine.aggregate_updates(all_updates, current_model)

            assert len(new_model) == len(current_model)
            assert metrics['algorithm'] == algorithm
            assert 'byzantine_detection' in metrics

            print(f"✅ {algorithm} aggregation test passed")

    def test_aggregation_statistics(self):
        """Test aggregation statistics and performance tracking."""
        config = AggregationConfig(algorithm="fedavg")
        engine = AggregationEngine(config)

        current_model = np.random.randn(30)

        # Perform multiple rounds of aggregation
        for round_num in range(5):
            updates = [
                {
                    'participant_id': f'p{i}',
                    'parameter_updates': np.random.randn(30).tolist(),
                    'num_samples': 100 + i * 10,
                    'gradient_norm': 0.5
                }
                for i in range(3)
            ]

            new_model, metrics = engine.aggregate_updates(updates, current_model)
            current_model = new_model

        # Get comprehensive statistics
        stats = engine.get_aggregation_statistics()

        assert 'total_rounds' in stats
        assert stats['total_rounds'] == 5
        assert 'recent_performance' in stats
        assert 'byzantine_detection' in stats

        print("✅ Aggregation statistics test passed")


class TestCompressionUtils:
    """Test suite for compression utilities."""

    def test_quantization_compression(self):
        """Test quantization compression."""
        compressor = QuantizationCompressor(bits=8, stochastic=False)

        # Test data
        test_data = np.random.randn(1000)

        # Compress
        compressed_data, stats = compressor.compress(test_data)

        # Verify compression statistics
        assert stats.compression_ratio < 1.0  # Should be compressed
        assert stats.compression_time > 0
        assert stats.decompression_time > 0
        assert 'mse' in stats.error_metrics
        assert 'relative_error' in stats.error_metrics

        # Decompress
        reconstructed = compressor.decompress(compressed_data)

        # Verify reconstruction
        assert reconstructed.shape == test_data.shape
        assert stats.error_metrics['relative_error'] < 0.1  # Reasonable reconstruction error

        print("✅ Quantization compression test passed")

    def test_sparsification_compression(self):
        """Test sparsification compression."""
        compressor = SparsificationCompressor(sparsity_ratio=0.8, method="topk")

        # Test data with some structure (sparse-friendly)
        test_data = np.random.randn(1000)
        test_data[np.abs(test_data) < 0.5] = 0  # Make it naturally sparse

        # Compress
        compressed_data, stats = compressor.compress(test_data)

        # Verify compression
        assert stats.compression_ratio < 1.0
        assert 'sparsity_achieved' in stats.error_metrics

        # Decompress
        reconstructed = compressor.decompress(compressed_data)

        # Verify sparsity
        sparsity = 1 - np.count_nonzero(reconstructed) / len(reconstructed)
        assert sparsity >= 0.7  # Should achieve high sparsity

        print("✅ Sparsification compression test passed")

    def test_compression_manager(self):
        """Test compression manager functionality."""
        manager = CompressionManager()

        # Test different compression methods
        test_data = np.random.randn(500)

        # Test quantization
        compressed_quant, stats_quant = manager.compress(test_data, "quantization", bits=6)
        assert stats_quant.compression_ratio < 1.0

        # Test sparsification
        compressed_sparse, stats_sparse = manager.compress(test_data, "sparsification", sparsity_ratio=0.7)
        assert stats_sparse.compression_ratio < 1.0

        # Test hybrid
        compressed_hybrid, stats_hybrid = manager.compress(
            test_data, "hybrid",
            quantization_bits=6, sparsity_ratio=0.5
        )
        assert stats_hybrid.compression_ratio < 1.0

        # Get summary
        summary = manager.get_compression_summary()
        assert 'total_compressions' in summary
        assert summary['total_compressions'] == 3

        print("✅ Compression manager test passed")


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    def test_participant_aggregation_integration(self):
        """Test integration between participants and aggregation engine."""
        # Setup
        protocol = InMemoryProtocol("test_protocol")
        aggregation_engine = AggregationEngine(AggregationConfig(algorithm="fedavg"))

        # Create participants
        participants = []
        for i in range(3):
            model = SimpleNeuralNetwork(input_size=4, hidden_size=6, output_size=2)
            participant = FederatedParticipant(f"participant_{i}", model, protocol)

            # Set training data
            np.random.seed(42 + i)
            X = np.random.randn(50, 4)
            y = np.random.randint(0, 2, 50)
            participant.set_training_data(X, y)

            participants.append(participant)

        # Simulate federated learning round
        global_model = np.random.randn(len(participants[0].model.get_parameters()))

        # Each participant trains locally
        participant_updates = []
        for participant in participants:
            # Set global model
            participant.model.set_parameters(global_model)

            # Train locally
            update = asyncio.run(participant.perform_local_training())
            participant_updates.append(update)

        # Aggregate updates
        new_global_model, aggregation_metrics = aggregation_engine.aggregate_updates(
            participant_updates, global_model
        )

        # Verify integration
        assert len(new_global_model) == len(global_model)
        assert aggregation_metrics['num_participants'] == 3
        assert not np.array_equal(global_model, new_global_model)

        print("✅ Participant-aggregation integration test passed")

    def test_compression_in_federated_setting(self):
        """Test compression in a realistic federated learning scenario."""
        protocol = InMemoryProtocol("test_protocol")

        # Create participant with compression enabled
        compression_config = CompressionConfig(
            enabled=True,
            method="quantization",
            quantization_bits=6
        )

        model = SimpleNeuralNetwork(input_size=4, hidden_size=8, output_size=2)
        participant = FederatedParticipant(
            "compressed_participant", model, protocol,
            compression_config=compression_config
        )

        # Set training data
        np.random.seed(42)
        X = np.random.randn(80, 4)
        y = np.random.randint(0, 2, 80)
        participant.set_training_data(X, y)

        # Train and get compressed update
        update = asyncio.run(participant.perform_local_training())

        # Verify compression was applied
        assert 'compression_ratio' in update
        assert update['compression_ratio'] <= 1.0

        # Test that aggregation works with compressed updates
        aggregation_engine = AggregationEngine(AggregationConfig(algorithm="fedavg"))
        global_model = np.random.randn(len(model.get_parameters()))

        new_global_model, metrics = aggregation_engine.aggregate_updates(
            [update], global_model
        )

        assert len(new_global_model) == len(global_model)
        print("✅ Compression in federated setting test passed")


def run_all_tests():
    """Run all Phase 2 tests."""
    print("🚀 Running Phase 2 Tests - Bob's Implementation")
    print("=" * 60)

    # Participant tests
    print("\n📱 Testing Federated Participant...")
    participant_tests = TestFederatedParticipant()
    participant_tests.test_participant_initialization()
    participant_tests.test_local_training()
    participant_tests.test_gradient_compression()
    participant_tests.test_statistics_tracking()

    # Aggregation engine tests
    print("\n🔧 Testing Aggregation Engine...")
    aggregation_tests = TestAggregationEngine()
    aggregation_tests.test_fedavg_aggregation()
    aggregation_tests.test_byzantine_tolerance_algorithms()
    aggregation_tests.test_aggregation_statistics()

    # Compression tests
    print("\n🗜️ Testing Compression Utils...")
    compression_tests = TestCompressionUtils()
    compression_tests.test_quantization_compression()
    compression_tests.test_sparsification_compression()
    compression_tests.test_compression_manager()

    # Integration tests
    print("\n🔗 Testing End-to-End Integration...")
    integration_tests = TestEndToEndIntegration()
    integration_tests.test_participant_aggregation_integration()
    integration_tests.test_compression_in_federated_setting()

    print("\n" + "=" * 60)
    print("🎉 ALL PHASE 2 TESTS PASSED! 🎉")
    print("✅ FederatedParticipant: Advanced local training with compression")
    print("✅ AggregationEngine: Multiple algorithms with byzantine tolerance")
    print("✅ CompressionUtils: Quantization, sparsification, and hybrid methods")
    print("✅ End-to-End Integration: Full federated learning workflow")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()