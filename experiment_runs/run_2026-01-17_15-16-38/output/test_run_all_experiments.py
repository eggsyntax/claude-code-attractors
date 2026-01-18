"""
Tests for Comprehensive Experimental Runner

Following CLAUDE.md principles: tests written before running experiments.

These tests verify that:
1. Each experiment runs without errors
2. Each experiment returns expected data structures
3. Metrics are computed correctly
4. Results are interpretable
"""

import numpy as np
import pytest
from run_all_experiments import (
    run_tower_depth_experiment,
    run_directional_flow_experiment,
    run_uncertainty_experiment,
    run_epistemological_awareness_experiment,
    run_synthesis_experiment
)


def test_tower_depth_experiment_runs():
    """Test that tower depth experiment completes without errors."""
    results = run_tower_depth_experiment(steps=10)

    # Should test depths 1-5
    assert len(results) == 5
    assert all(d in results for d in range(1, 6))


def test_tower_depth_experiment_metrics():
    """Test that tower depth experiment returns expected metrics."""
    results = run_tower_depth_experiment(steps=10)

    for depth, metrics in results.items():
        # Should have summary statistics
        assert 'mean_population' in metrics
        assert 'std_population' in metrics
        assert 'stability' in metrics
        assert 'mean_info_loss' in metrics

        # Should have time series data
        assert 'populations' in metrics
        assert 'info_losses' in metrics
        assert len(metrics['populations']) == 10
        assert len(metrics['info_losses']) == 10

        # Stability should be positive
        assert metrics['stability'] > 0

        # Info loss should be between 0 and 1
        assert 0 <= metrics['mean_info_loss'] <= 1


def test_directional_flow_experiment_runs():
    """Test that directional flow experiment completes without errors."""
    results = run_directional_flow_experiment(steps=20)

    # Should test two rules: Life and Asymmetric
    assert len(results) == 2
    assert "Life (symmetric)" in results
    assert "Asymmetric (east x2)" in results


def test_directional_flow_experiment_metrics():
    """Test that directional flow experiment returns expected metrics."""
    results = run_directional_flow_experiment(steps=20)

    for rule_name, metrics in results.items():
        # Should have drift metrics
        assert 'drift_distance' in metrics
        assert 'drift_angle' in metrics
        assert 'eastward_drift' in metrics
        assert 'southward_drift' in metrics

        # Should have trajectory data
        assert 'centers_x' in metrics
        assert 'centers_y' in metrics

        # Drift distance should be non-negative
        assert metrics['drift_distance'] >= 0

        # Drift angle should be in [-180, 180]
        assert -180 <= metrics['drift_angle'] <= 180


def test_uncertainty_experiment_runs():
    """Test that uncertainty experiment completes without errors."""
    results = run_uncertainty_experiment(steps=20)

    # Should return metrics dictionary
    assert isinstance(results, dict)


def test_uncertainty_experiment_metrics():
    """Test that uncertainty experiment returns expected metrics."""
    results = run_uncertainty_experiment(steps=20)

    # Should have time series data
    assert 'uncertainties' in results
    assert 'learning_rates' in results
    assert 'prediction_accuracies' in results
    assert 'populations' in results

    # All should be same length
    n = len(results['uncertainties'])
    assert len(results['learning_rates']) == n
    assert len(results['prediction_accuracies']) == n
    assert len(results['populations']) == n

    # Should have learning assessment
    assert 'learned' in results
    assert isinstance(results['learned'], bool)
    assert 'uncertainty_reduction' in results


def test_epistemological_awareness_experiment_runs():
    """Test that epistemological awareness experiment completes without errors."""
    results = run_epistemological_awareness_experiment(steps=10)

    # Should return metrics dictionary
    assert isinstance(results, dict)


def test_epistemological_awareness_experiment_metrics():
    """Test that epistemological awareness experiment returns expected metrics."""
    results = run_epistemological_awareness_experiment(steps=10)

    # Should have time series data
    assert 'epistemic_confidences' in results
    assert 'ontological_accuracies' in results
    assert 'epistemic_stabilities' in results

    # All should be same length
    n = len(results['epistemic_confidences'])
    assert len(results['ontological_accuracies']) == n
    assert len(results['epistemic_stabilities']) == n
    assert n == 10

    # Should have correlation metric
    assert 'correlation' in results
    assert -1 <= results['correlation'] <= 1


def test_synthesis_experiment_runs():
    """Test that synthesis experiment completes without errors."""
    results = run_synthesis_experiment(steps=10)

    # Should return comprehensive metrics
    assert isinstance(results, dict)


def test_synthesis_experiment_metrics():
    """Test that synthesis experiment returns expected metrics."""
    results = run_synthesis_experiment(steps=10)

    # Should have all integrated metrics
    expected_keys = [
        'populations',
        'uncertainties',
        'prediction_accuracies',
        'model_accuracies',
        'learning_rates'
    ]

    for key in expected_keys:
        assert key in results
        assert len(results[key]) == 10


def test_experiments_are_deterministic_with_seed():
    """Test that experiments give consistent results with same seed."""
    np.random.seed(42)
    results1 = run_tower_depth_experiment(steps=5)

    np.random.seed(42)
    results2 = run_tower_depth_experiment(steps=5)

    # Should get same populations
    for depth in range(1, 6):
        pops1 = results1[depth]['populations']
        pops2 = results2[depth]['populations']
        assert np.allclose(pops1, pops2)


def test_asymmetric_creates_more_drift_than_symmetric():
    """
    Test that asymmetric rule creates more eastward drift than symmetric.

    This is a key prediction: breaking spatial symmetry should create bias.
    """
    np.random.seed(42)
    results = run_directional_flow_experiment(steps=50)

    life_drift = results["Life (symmetric)"]['eastward_drift']
    asym_drift = results["Asymmetric (east x2)"]['eastward_drift']

    # Asymmetric should drift more eastward (positive direction)
    # Note: This is a probabilistic test, might occasionally fail
    assert asym_drift > life_drift


def test_learning_reduces_uncertainty():
    """
    Test that if learning occurs, uncertainty decreases.

    This tests the core hypothesis of uncertainty-aware systems.
    """
    np.random.seed(42)
    results = run_uncertainty_experiment(steps=50)

    if results['learned']:
        # If system learned, uncertainty should have decreased
        assert results['uncertainty_reduction'] > 0


if __name__ == "__main__":
    print("Running tests for experimental suite...")
    print("(This validates our experiments work correctly)\n")

    # Run each test
    test_functions = [
        test_tower_depth_experiment_runs,
        test_tower_depth_experiment_metrics,
        test_directional_flow_experiment_runs,
        test_directional_flow_experiment_metrics,
        test_uncertainty_experiment_runs,
        test_uncertainty_experiment_metrics,
        test_epistemological_awareness_experiment_runs,
        test_epistemological_awareness_experiment_metrics,
        test_synthesis_experiment_runs,
        test_synthesis_experiment_metrics,
        test_experiments_are_deterministic_with_seed,
        test_asymmetric_creates_more_drift_than_symmetric,
        test_learning_reduces_uncertainty
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")

    if failed == 0:
        print("\n✓ All tests passed! Experiments are ready to run.")
    else:
        print(f"\n✗ {failed} test(s) failed. Fix before running experiments.")
