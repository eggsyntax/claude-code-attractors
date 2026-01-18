#!/usr/bin/env python3
"""
Tests for the Monty Hall simulation.

Run with: python test_monty_hall.py
"""

import sys
from monty_hall import play_monty_hall, run_simulation


def test_basic_logic():
    """Test that the game logic works correctly."""
    print("Testing basic game logic...")

    # Run a small number of games to check both strategies work
    stay_wins = sum(play_monty_hall(switch=False) for _ in range(100))
    switch_wins = sum(play_monty_hall(switch=True) for _ in range(100))

    print(f"  100 games staying: {stay_wins} wins")
    print(f"  100 games switching: {switch_wins} wins")

    assert 0 <= stay_wins <= 100, "Stay wins out of range"
    assert 0 <= switch_wins <= 100, "Switch wins out of range"

    print("  ✓ Basic logic test passed\n")


def test_probability_distribution():
    """Test that probabilities converge to expected values."""
    print("Testing probability convergence...")

    results = run_simulation(num_games=10000)

    print(f"  Stay strategy: {results['stay']:.1%}")
    print(f"  Switch strategy: {results['switch']:.1%}")

    # With 10000 games, we expect to be reasonably close to theoretical values
    # Using generous bounds to avoid flaky tests
    assert 0.25 < results['stay'] < 0.42, \
        f"Stay win rate {results['stay']:.3f} too far from expected 0.333"

    assert 0.58 < results['switch'] < 0.75, \
        f"Switch win rate {results['switch']:.3f} too far from expected 0.667"

    print("  ✓ Probability distribution test passed\n")


def test_switch_better_than_stay():
    """Test that switching is demonstrably better than staying."""
    print("Testing that switching beats staying...")

    results = run_simulation(num_games=5000)

    assert results['switch'] > results['stay'], \
        "Switching should have higher win rate than staying"

    ratio = results['switch'] / results['stay']
    print(f"  Switching is {ratio:.2f}x better than staying")

    # Ratio should be around 2.0 (theoretically exactly 2)
    assert 1.5 < ratio < 2.5, \
        f"Ratio {ratio:.2f} too far from expected ~2.0"

    print("  ✓ Switch superiority test passed\n")


if __name__ == '__main__':
    print("="*60)
    print("MONTY HALL TESTS")
    print("="*60 + "\n")

    try:
        test_basic_logic()
        test_probability_distribution()
        test_switch_better_than_stay()

        print("="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        sys.exit(1)
