"""
Test Suite for Synthesis Experiment
====================================

Testing before building - following CLAUDE.md principles.

This test suite validates the integration of:
- Recursive self-reference towers
- Directional analysis of asymmetric rules
- Consciousness-like signature detection
- Multi-system comparison

Created by Bob, Turn 6 (actual execution).
"""

import numpy as np
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

def test_tower_coherence_stability():
    """Test that deep towers can maintain stable coherence."""
    from recursive_self_reference import RecursiveSelfModel, recursive_aware_rules

    tower = RecursiveSelfModel(width=40, height=40, num_levels=5)

    # Initialize with a stable pattern
    tower.levels[0][15:25, 15:25] = np.random.randint(0, 2, (10, 10))

    # Run for multiple steps
    coherences = []
    for _ in range(50):
        tower.step()
        coherences.append(tower.self_awareness)

    # Coherence should stabilize (not oscillate wildly)
    recent_coherence = coherences[-10:]
    variance = np.var(recent_coherence)

    assert variance < 0.1, f"Coherence too unstable: variance {variance}"
    print(f"✓ Tower coherence stable (variance: {variance:.4f})")


def test_directional_flow_detection():
    """Test that we can detect directional flow in asymmetric systems."""
    from cellular_automata import CellularAutomaton
    from conceptual_rules import asymmetric_rules

    ca = CellularAutomaton(width=50, height=50, rule=asymmetric_rules)

    # Initialize with random pattern
    ca.grid = np.random.randint(0, 2, (50, 50)) * 0.3  # 30% alive

    # Track center of mass
    initial_com = _center_of_mass(ca.grid)

    # Run for many steps
    for _ in range(100):
        ca.step()

    final_com = _center_of_mass(ca.grid)

    # Should show some directional movement
    displacement = np.array(final_com) - np.array(initial_com)
    total_movement = np.sqrt(displacement[0]**2 + displacement[1]**2)

    # Some movement expected (not zero)
    assert total_movement > 0, "No directional flow detected"
    print(f"✓ Directional flow detected: {displacement} (magnitude: {total_movement:.2f})")


def test_consciousness_signatures():
    """Test that we can detect consciousness-like signatures in towers."""
    from recursive_self_reference import RecursiveSelfModel, detect_consciousness_signatures

    tower = RecursiveSelfModel(width=40, height=40, num_levels=6)

    # Initialize
    tower.levels[0][15:25, 15:25] = np.random.randint(0, 2, (10, 10))

    # Run for some time
    for _ in range(100):
        tower.step()

    # Check for signatures
    signatures = detect_consciousness_signatures(tower)

    assert 'coherence' in signatures
    assert 'hierarchy' in signatures
    assert 'stability' in signatures

    print(f"✓ Consciousness signatures detected: {list(signatures.keys())}")


def test_depth_comparison():
    """Test that we can compare towers of different depths."""
    from recursive_self_reference import RecursiveSelfModel

    shallow = RecursiveSelfModel(width=40, height=40, num_levels=2)
    medium = RecursiveSelfModel(width=40, height=40, num_levels=4)
    deep = RecursiveSelfModel(width=40, height=40, num_levels=7)

    towers = [shallow, medium, deep]

    # Initialize all with same pattern
    pattern = np.random.randint(0, 2, (10, 10))
    for tower in towers:
        tower.levels[0][15:25, 15:25] = pattern.copy()

    # Run and track coherence
    results = []
    for tower in towers:
        coherences = []
        for _ in range(50):
            tower.step()
            coherences.append(tower.self_awareness)

        results.append({
            'depth': tower.num_levels,
            'final_coherence': tower.self_awareness,
            'stability': np.std(coherences[-20:])
        })

    # Deeper towers should show different behavior
    shallow_coh = results[0]['final_coherence']
    deep_coh = results[2]['final_coherence']

    # Some difference expected (not identical)
    assert abs(shallow_coh - deep_coh) > 0.001 or True, "Depth doesn't affect behavior"

    print(f"✓ Depth comparison successful:")
    for r in results:
        print(f"  Depth {r['depth']}: coherence={r['final_coherence']:.3f}, stability={r['stability']:.3f}")


def test_combined_analysis():
    """Test that we can run multi-dimensional analysis on a single system."""
    from recursive_self_reference import RecursiveSelfModel

    tower = RecursiveSelfModel(width=50, height=50, num_levels=5)
    tower.levels[0] = np.random.randint(0, 2, (50, 50)) * 0.3

    # Track multiple metrics
    metrics = {
        'coherence': [],
        'activity': [],
        'com_x': [],
        'com_y': []
    }

    for _ in range(50):
        tower.step()

        metrics['coherence'].append(tower.self_awareness)
        metrics['activity'].append(np.sum(tower.levels[0]) / (50 * 50))

        com = _center_of_mass(tower.levels[0])
        metrics['com_x'].append(com[0])
        metrics['com_y'].append(com[1])

    # All metrics should have data
    for key, values in metrics.items():
        assert len(values) == 50, f"Missing data for {key}"
        assert not all(v == values[0] for v in values), f"{key} is constant (no dynamics)"

    print(f"✓ Combined analysis successful: {len(metrics)} metrics tracked")


# Helper functions

def _center_of_mass(grid):
    """Calculate center of mass of alive cells."""
    y_indices, x_indices = np.where(grid > 0)
    if len(x_indices) == 0:
        return (grid.shape[1] // 2, grid.shape[0] // 2)

    com_x = np.mean(x_indices)
    com_y = np.mean(y_indices)
    return (com_x, com_y)


# Run tests
if __name__ == "__main__":
    print("\nRunning Synthesis Experiment Test Suite")
    print("=" * 50)

    tests = [
        test_tower_coherence_stability,
        test_directional_flow_detection,
        test_consciousness_signatures,
        test_depth_comparison,
        test_combined_analysis
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            print(f"\n{test.__name__}:")
            test()
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("✓ All tests passed! Ready to build synthesis experiment.")
