"""
Tests for Epistemological Self-Awareness System
================================================

Tests the system that models its own modeling process.

Written before implementation (TDD style, per CLAUDE.md guidance).

Created by Bob, Turn 6
"""

import numpy as np
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from epistemological_awareness import EpistemologicalAgent


def test_initialization():
    """Test that agent initializes correctly."""
    agent = EpistemologicalAgent(width=40, height=40, compression=2)

    assert agent.width == 40
    assert agent.height == 40
    assert agent.compression == 2
    assert agent.world.grid.shape == (40, 40)
    assert agent.world_model.shape == (20, 20)
    assert agent.steps_taken == 0
    assert 'accuracy_history' in agent.process_model
    assert 'epistemic_confidence' in agent.process_model

    print("✓ Initialization test passed")


def test_world_model_updates():
    """Test that world model is updated correctly."""
    agent = EpistemologicalAgent(width=20, height=20, compression=2)

    # Set specific pattern in world
    agent.world.grid[0:2, 0:2] = 1
    agent._update_world_model()

    # Model should reflect this (max pooling)
    assert agent.world_model[0, 0] == 1

    # Set another region
    agent.world.grid[10:12, 10:12] = 1
    agent._update_world_model()

    assert agent.world_model[5, 5] == 1

    print("✓ World model update test passed")


def test_process_model_updates():
    """Test that process model tracks modeling accuracy."""
    agent = EpistemologicalAgent(width=20, height=20, compression=2)

    # Initialize with simple pattern
    agent.world.grid[5:10, 5:10] = 1

    # Take several steps
    for _ in range(10):
        agent.step()

    # Process model should have accuracy history
    assert len(agent.process_model['accuracy_history']) == 10
    assert all(0 <= acc <= 1 for acc in agent.process_model['accuracy_history'])

    # Should have epistemic confidence
    assert 0 <= agent.process_model['epistemic_confidence'] <= 1

    print("✓ Process model update test passed")


def test_epistemic_confidence():
    """Test that epistemic confidence is calculated correctly."""
    agent = EpistemologicalAgent(width=30, height=30, compression=2)

    # Initialize with stable pattern (block)
    agent.world.grid[10:12, 10:12] = 1

    # Take steps - block is stable, so accuracy should be high
    for _ in range(20):
        agent.step()

    # Epistemic confidence should be reasonably high for stable pattern
    assert agent.process_model['epistemic_confidence'] > 0.5

    print("✓ Epistemic confidence test passed")


def test_known_limitations():
    """Test that system identifies its own limitations."""
    agent = EpistemologicalAgent(width=40, height=40, compression=4)  # High compression

    # Initialize with complex pattern
    agent.world.grid[10:30, 10:30] = np.random.randint(0, 2, (20, 20))

    # Take steps
    for _ in range(15):
        agent.step()

    # With high compression and complex pattern, should identify limitations
    limitations = agent.process_model['known_limitations']

    # Should identify compression loss
    assert any(lim['type'] == 'compression_loss' for lim in limitations)

    print("✓ Known limitations test passed")


def test_introspection():
    """Test that introspection produces meaningful report."""
    agent = EpistemologicalAgent(width=30, height=30, compression=2)

    # Before any steps
    report_before = agent.introspect()
    assert "No data yet" in report_before or "have not yet begun" in report_before

    # Initialize and step
    agent.world.grid[10:15, 10:15] = 1
    for _ in range(10):
        agent.step()

    # After steps
    report_after = agent.introspect()

    # Should contain key information
    assert "Epistemic Self-Report" in report_after
    assert "WHAT I KNOW" in report_after
    assert "HOW I KNOW" in report_after
    assert "WHAT I KNOW I DON'T KNOW" in report_after
    assert "accuracy" in report_after.lower()

    print("✓ Introspection test passed")


def test_epistemic_vs_ontological():
    """Test the difference between ontological and epistemological awareness."""
    agent = EpistemologicalAgent(width=30, height=30, compression=2)

    # Initialize
    agent.world.grid[10:20, 10:20] = np.random.randint(0, 2, (10, 10))

    # Take steps
    for _ in range(20):
        agent.step()

    # Get epistemic report
    report = agent.get_epistemic_report()

    # Ontological: knows about world state
    assert 'current_world_state' in report
    assert 'current_model_state' in report

    # Epistemological: knows about modeling process
    assert 'modeling_accuracy' in report
    assert 'process_stability' in report
    assert 'modeling_method' in report

    # Meta-epistemic: knows about limitations of knowledge
    assert 'known_limitations' in report
    assert 'epistemic_confidence' in report

    print("✓ Epistemological vs ontological test passed")


def test_process_stability():
    """Test that process stability is tracked correctly."""
    agent = EpistemologicalAgent(width=30, height=30, compression=2)

    # Initialize with very stable pattern (empty grid)
    # Model should be very stable (and accurate)
    for _ in range(30):
        agent.step()

    # Process should be stable (low variance in accuracy)
    assert agent.process_model['process_stability'] > 0.8

    print("✓ Process stability test passed")


def test_model_expansion():
    """Test that model expansion works correctly."""
    agent = EpistemologicalAgent(width=20, height=20, compression=2)

    # Set model state
    agent.world_model[5, 5] = 1

    # Expand
    expanded = agent._expand_model(agent.world_model)

    # Expanded region should be alive
    assert expanded.shape == (20, 20)
    assert np.all(expanded[10:12, 10:12] == 1)

    print("✓ Model expansion test passed")


def test_error_tracking():
    """Test that modeling errors are tracked over time."""
    agent = EpistemologicalAgent(width=30, height=30, compression=2)

    # Initialize
    agent.world.grid[10:20, 10:20] = np.random.randint(0, 2, (10, 10))

    # Take steps
    for _ in range(25):
        agent.step()

    # Should have error history
    assert len(agent.modeling_errors) == 25
    assert all(0 <= err <= 1 for err in agent.modeling_errors)

    # Should have process change history
    assert len(agent.process_changes) == 25

    print("✓ Error tracking test passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Testing Epistemological Self-Awareness System")
    print("=" * 60)
    print()

    tests = [
        test_initialization,
        test_world_model_updates,
        test_process_model_updates,
        test_epistemic_confidence,
        test_known_limitations,
        test_introspection,
        test_epistemic_vs_ontological,
        test_process_stability,
        test_model_expansion,
        test_error_tracking,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()

    if success:
        print("\n✓ All tests passed!")
        print("\nThe system can now:")
        print("  1. Model its own state (ontological awareness)")
        print("  2. Model its modeling process (epistemological awareness)")
        print("  3. Identify its own limitations (meta-epistemic awareness)")
        print()
        print("This is the foundation for exploring consciousness as")
        print("awareness of the process of awareness itself.")
        exit(0)
    else:
        print("\n✗ Some tests failed")
        exit(1)
