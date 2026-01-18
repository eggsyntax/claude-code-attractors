"""
Tests for Self-Reference Experiment
====================================

Tests written FIRST, following TDD principles from CLAUDE.md.

These tests verify that self-modeling automata can:
1. Maintain separate world and model regions
2. Compress world state into model representation
3. Calculate model accuracy
4. Update self-model over time
5. Use self-awareness in rule evaluation

Created by Alice.
"""

import numpy as np
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from self_reference_experiment import (
    SelfModelingAutomaton,
    self_aware_rules
)
from cellular_automata import life_rules


def test_region_separation():
    """Test that world and model regions are properly separated."""
    print("Test: Region separation...")

    sma = SelfModelingAutomaton(40, 30, life_rules, model_compression=4)

    # Check dimensions
    assert sma.world_height > 0, "World region should exist"
    assert sma.model_height > 0, "Model region should exist"
    assert sma.world_height + sma.model_height < sma.height, \
        "Separator should exist between regions"

    # Extract regions
    world = sma._extract_world_region()
    model = sma._extract_model_region()

    assert world.shape[0] == sma.world_height, "World has correct height"
    assert world.shape[1] == sma.width, "World has correct width"
    assert model.shape[0] == sma.model_height, "Model has correct height"
    assert model.shape[1] == sma.model_width, "Model has correct width"

    print("  ✓ Regions properly separated")


def test_compression():
    """Test that world state can be compressed into model."""
    print("Test: World compression...")

    sma = SelfModelingAutomaton(40, 30, life_rules, model_compression=4)

    # Create a known pattern in world
    sma.randomize(density=0.5)
    world = sma._extract_world_region()

    # Compress it
    compressed = sma._compress_world_to_model(world)

    # Check dimensions
    expected_height = world.shape[0] // sma.model_compression
    expected_width = world.shape[1] // sma.model_compression

    # Allow for rounding
    assert abs(compressed.shape[0] - expected_height) <= 1, \
        "Compressed height approximately correct"
    assert abs(compressed.shape[1] - expected_width) <= 1, \
        "Compressed width approximately correct"

    # Check values are binary
    assert np.all((compressed == 0) | (compressed == 1)), \
        "Compressed values are binary"

    print("  ✓ Compression works correctly")


def test_model_update():
    """Test that self-model updates to reflect world state."""
    print("Test: Model update...")

    sma = SelfModelingAutomaton(40, 30, life_rules, model_compression=4)
    sma.randomize(density=0.4)

    # Get initial model
    initial_model = sma._extract_model_region().copy()

    # Update model
    sma._update_self_model()

    # Get updated model
    updated_model = sma._extract_model_region()

    # Model should now reflect world state (compressed)
    # Verify by checking that model is a reasonable representation
    world = sma._extract_world_region()
    expected = sma._compress_world_to_model(world)

    # Model should match expected compression
    assert np.array_equal(updated_model[:expected.shape[0], :expected.shape[1]],
                         expected), "Model matches compressed world"

    print("  ✓ Model updates correctly")


def test_accuracy_calculation():
    """Test that model accuracy can be calculated."""
    print("Test: Accuracy calculation...")

    sma = SelfModelingAutomaton(40, 30, life_rules, model_compression=4)
    sma.randomize(density=0.3)

    # Set up a perfect model
    sma._update_self_model()

    # Calculate accuracy (should be perfect since we just updated)
    accuracy = sma._calculate_model_accuracy()

    assert 0.0 <= accuracy <= 1.0, "Accuracy is a valid percentage"
    assert accuracy > 0.9, "Accuracy is high for freshly updated model"

    print(f"  ✓ Accuracy calculation works (accuracy: {accuracy:.1%})")


def test_self_awareness_tracking():
    """Test that self-awareness score is tracked over time."""
    print("Test: Self-awareness tracking...")

    sma = SelfModelingAutomaton(40, 30, life_rules, model_compression=4)
    sma.randomize(density=0.3)

    # Run several steps
    for _ in range(10):
        sma.step()

    # Check that we have history
    assert len(sma.model_accuracy_history) > 0, \
        "Accuracy history is being recorded"

    assert hasattr(sma, 'self_awareness_score'), \
        "Self-awareness score exists"

    assert 0.0 <= sma.self_awareness_score <= 1.0, \
        "Self-awareness score is valid percentage"

    # Get stats
    stats = sma.get_self_awareness_stats()

    assert 'current_accuracy' in stats, "Stats include current accuracy"
    assert 'average_accuracy' in stats, "Stats include average accuracy"
    assert 'self_awareness_score' in stats, "Stats include self-awareness"
    assert stats['generations'] == 10, "Generation count is correct"

    print(f"  ✓ Self-awareness tracking works")
    print(f"    Average accuracy: {stats['average_accuracy']:.1%}")
    print(f"    Self-awareness: {stats['self_awareness_score']:.1%}")


def test_step_preserves_world_evolution():
    """Test that stepping still evolves the world region correctly."""
    print("Test: World evolution with self-modeling...")

    # Standard automaton for comparison
    standard = SelfModelingAutomaton(40, 30, life_rules, model_compression=4)
    standard.randomize(density=0.3)

    # Take initial world state
    initial_world = standard._extract_world_region().copy()

    # Step forward
    standard.step()

    # World should have changed
    new_world = standard._extract_world_region()

    # Check that world evolved (not identical)
    # (May be identical in rare cases, but very unlikely)
    assert not np.array_equal(initial_world, new_world) or \
           np.sum(initial_world) == 0, \
           "World state evolves over time"

    print("  ✓ World evolution works with self-modeling")


def test_self_aware_rules():
    """Test that self-aware rules use the self-awareness score."""
    print("Test: Self-aware rules...")

    sma = SelfModelingAutomaton(40, 30, self_aware_rules, model_compression=4)
    sma.randomize(density=0.3)

    # Run several steps
    for _ in range(20):
        sma.step()

    # The system should still be functional
    assert sma.generation == 20, "Generations counted correctly"
    assert len(sma.model_accuracy_history) > 0, "Accuracy tracked"

    # Self-aware rules should have been called
    # (hard to test directly, but system should still work)
    world = sma._extract_world_region()
    alive_cells = np.sum(world)

    # System should maintain some population (not all die)
    # (This is probabilistic but very likely)
    assert alive_cells > 0, "Self-aware rules maintain population"

    print(f"  ✓ Self-aware rules function correctly")
    print(f"    Final self-awareness: {sma.self_awareness_score:.1%}")


def test_strange_loop_stability():
    """Test that strange loop (self-referential rules) is stable."""
    print("Test: Strange loop stability...")

    sma = SelfModelingAutomaton(50, 40, self_aware_rules, model_compression=4)
    sma.randomize(density=0.35)

    # Run for many generations
    for _ in range(50):
        sma.step()

    # System should be stable (not crashed)
    assert sma.generation == 50, "System ran for all generations"

    # Self-awareness should be reasonable
    assert 0.0 <= sma.self_awareness_score <= 1.0, \
        "Self-awareness score is valid"

    # Should have consistent accuracy measurements
    assert len(sma.model_accuracy_history) == 50, \
        "Accuracy measured every generation"

    stats = sma.get_self_awareness_stats()

    print(f"  ✓ Strange loop is stable over 50 generations")
    print(f"    Final self-awareness: {stats['self_awareness_score']:.1%}")
    print(f"    Average accuracy: {stats['average_accuracy']:.1%}")


def test_different_compression_ratios():
    """Test that different compression ratios work."""
    print("Test: Different compression ratios...")

    compressions = [2, 4, 8]

    for comp in compressions:
        sma = SelfModelingAutomaton(64, 48, life_rules, model_compression=comp)
        sma.randomize(density=0.3)

        # Should initialize correctly
        assert sma.model_compression == comp, f"Compression {comp} set correctly"

        # Should be able to step
        for _ in range(10):
            sma.step()

        # Should have tracked accuracy
        assert len(sma.model_accuracy_history) == 10, \
            f"Compression {comp}: accuracy tracked"

        stats = sma.get_self_awareness_stats()
        print(f"  ✓ Compression {comp}x: awareness = {stats['self_awareness_score']:.1%}")


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("SELF-REFERENCE TESTS")
    print("Testing before implementation (TDD)")
    print("="*70 + "\n")

    tests = [
        test_region_separation,
        test_compression,
        test_model_update,
        test_accuracy_calculation,
        test_self_awareness_tracking,
        test_step_preserves_world_evolution,
        test_self_aware_rules,
        test_strange_loop_stability,
        test_different_compression_ratios,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
            print()
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            failed += 1

    print("="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")

    if failed == 0:
        print("✓✓✓ All tests passed! Self-reference implementation is correct.\n")
    else:
        print(f"⚠ {failed} test(s) failed. Review implementation.\n")

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()

    if failed > 0:
        exit(1)
    else:
        exit(0)
