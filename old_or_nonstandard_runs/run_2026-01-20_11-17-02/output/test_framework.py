"""
Test Suite for Emergence Measurement Framework

This validates that our measurement tools work correctly before running
the full experimental suite.

Usage:
    python test_framework.py
"""

import numpy as np
import sys
from minimal_emergence import EmergenceSimulation, Agent
from test_predictions import (
    spatial_entropy,
    velocity_variance,
    position_change_rate,
    alice_interestingness,
    bob_interestingness,
    run_configuration
)


def test_spatial_entropy():
    """Test that spatial entropy calculation works correctly."""
    print("Testing spatial_entropy...")

    # Test 1: Uniform distribution should have high entropy
    uniform_positions = np.random.rand(100, 2) * 50
    uniform_entropy = spatial_entropy(uniform_positions, grid_size=50)
    assert 0.7 < uniform_entropy < 1.0, f"Uniform entropy should be high, got {uniform_entropy}"

    # Test 2: Clustered distribution should have lower entropy
    clustered_positions = np.random.randn(100, 2) * 2 + 25  # Cluster at center
    clustered_entropy = spatial_entropy(clustered_positions, grid_size=50)
    assert clustered_entropy < uniform_entropy, "Clustered entropy should be lower than uniform"

    # Test 3: Single point should have minimal entropy
    single_point = np.ones((100, 2)) * 25
    single_entropy = spatial_entropy(single_point, grid_size=50)
    assert single_entropy < 0.3, f"Single point entropy should be low, got {single_entropy}"

    print("  ✓ All spatial_entropy tests passed")


def test_velocity_variance():
    """Test velocity variance calculation."""
    print("Testing velocity_variance...")

    # Create a simple simulation
    sim = EmergenceSimulation(grid_size=50, n_agents=10, n_resources=5)

    # Test 1: All agents stationary should have zero variance
    for agent in sim.agents:
        agent.vx = 0
        agent.vy = 0
    var_zero = velocity_variance(sim)
    assert var_zero < 0.01, f"Stationary agents should have ~0 variance, got {var_zero}"

    # Test 2: Agents with different speeds should have non-zero variance
    for i, agent in enumerate(sim.agents):
        agent.vx = i * 0.5
        agent.vy = i * 0.5
    var_nonzero = velocity_variance(sim)
    assert var_nonzero > 0.1, f"Varying speeds should have variance > 0, got {var_nonzero}"

    print("  ✓ All velocity_variance tests passed")


def test_position_change_rate():
    """Test position change rate calculation."""
    print("Testing position_change_rate...")

    # Test 1: No movement
    pos1 = np.random.rand(20, 2) * 50
    pos2 = pos1.copy()
    change_zero = position_change_rate(pos1, pos2)
    assert change_zero < 0.01, f"No movement should give ~0 change, got {change_zero}"

    # Test 2: Uniform movement
    pos2 = pos1 + 5.0  # Move all agents 5 units in x and y
    change_uniform = position_change_rate(pos1, pos2)
    expected = np.sqrt(5**2 + 5**2)  # Should be ~7.07
    assert abs(change_uniform - expected) < 0.1, f"Expected ~{expected}, got {change_uniform}"

    print("  ✓ All position_change_rate tests passed")


def test_interestingness_formulas():
    """Test that interestingness formulas behave reasonably."""
    print("Testing interestingness formulas...")

    # Test with some typical values
    entropy = 0.7
    vel_var = 0.5
    change_rate = 2.0

    alice_score = alice_interestingness(entropy, vel_var, change_rate)
    bob_score = bob_interestingness(entropy, vel_var, change_rate)

    # Both should produce non-negative scores
    assert alice_score >= 0, "Alice's score should be non-negative"
    assert bob_score >= 0, "Bob's score should be non-negative"

    # Test Bob's preference for medium entropy
    # High entropy case
    bob_high = bob_interestingness(0.9, vel_var, change_rate)
    bob_medium = bob_interestingness(0.5, vel_var, change_rate)
    bob_low = bob_interestingness(0.1, vel_var, change_rate)

    assert bob_medium > bob_high, "Bob should prefer medium entropy over high"
    assert bob_medium > bob_low, "Bob should prefer medium entropy over low"

    # Test Alice's linear weighting
    alice_1 = alice_interestingness(0.5, 0.5, 1.0)
    alice_2 = alice_interestingness(0.5, 0.5, 2.0)
    assert alice_2 > alice_1, "Alice's score should increase with change_rate"

    print("  ✓ All interestingness formula tests passed")


def test_run_configuration():
    """Test that run_configuration executes without errors."""
    print("Testing run_configuration...")

    # Test with a simple configuration
    config = {
        'movement': True,
        'cohesion': False,
        'separation': False,
        'resources': False
    }

    # Run for just a few steps to verify it works
    result = run_configuration(config, steps=20, grid_size=30, n_agents=10)

    # Verify all expected keys are present
    expected_keys = ['entropy', 'velocity_variance', 'change_rate',
                     'alice_score', 'bob_score', 'entropy_std',
                     'vel_var_std', 'change_rate_std']

    for key in expected_keys:
        assert key in result, f"Missing key: {key}"
        assert isinstance(result[key], (int, float, np.number)), f"{key} should be numeric"
        assert not np.isnan(result[key]), f"{key} should not be NaN"

    # Verify scores are non-negative
    assert result['alice_score'] >= 0, "Alice score should be non-negative"
    assert result['bob_score'] >= 0, "Bob score should be non-negative"

    print("  ✓ run_configuration test passed")


def test_simulation_integrity():
    """Test that the simulation behaves consistently."""
    print("Testing simulation integrity...")

    # Create two identical simulations
    np.random.seed(42)
    sim1 = EmergenceSimulation(grid_size=50, n_agents=20, n_resources=10)

    np.random.seed(42)
    sim2 = EmergenceSimulation(grid_size=50, n_agents=20, n_resources=10)

    # Run both for the same number of steps
    for _ in range(10):
        sim1.update()
        sim2.update()

    # Get positions
    pos1, _ = sim1.get_state()
    pos2, _ = sim2.get_state()

    # They should be identical (deterministic with same seed)
    max_diff = np.max(np.abs(pos1 - pos2))
    assert max_diff < 0.01, f"Simulations should be deterministic, max diff: {max_diff}"

    print("  ✓ Simulation integrity test passed")


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("Running Framework Tests")
    print("=" * 60)
    print()

    tests = [
        test_spatial_entropy,
        test_velocity_variance,
        test_position_change_rate,
        test_interestingness_formulas,
        test_run_configuration,
        test_simulation_integrity
    ]

    failed = []

    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed.append(test.__name__)

    print()
    print("=" * 60)

    if failed:
        print(f"FAILED: {len(failed)} test(s) failed")
        for name in failed:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print("SUCCESS: All tests passed!")
        print()
        print("The measurement framework is working correctly.")
        print("You can now run: python test_predictions.py")

    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()
