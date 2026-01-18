"""
Tests for Recursive Self-Reference System
==========================================

Testing a cellular automaton with multiple levels of self-modeling:
- Level 0: World state
- Level 1: Model of world
- Level 2: Model of the model
- Level N: Arbitrarily deep towers of self-reference

This tests Bob's implementation of Alice's question about recursive meta-cognition.

Written test-first following CLAUDE.md principles.
"""

import unittest
import numpy as np
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from recursive_self_reference import (
    RecursiveSelfModel,
    recursive_aware_rules,
    measure_tower_coherence,
    analyze_consciousness_emergence
)


class TestRecursiveSelfModel(unittest.TestCase):
    """Test the recursive self-modeling automaton."""

    def test_initialization(self):
        """Test that the tower initializes with correct number of levels."""
        tower = RecursiveSelfModel(width=64, height=64, num_levels=3)

        self.assertEqual(tower.num_levels, 3)
        self.assertEqual(len(tower.levels), 3)
        self.assertEqual(tower.levels[0].shape, (64, 64))  # World level

        # Each level should be compressed version of previous
        self.assertTrue(tower.levels[1].size < tower.levels[0].size)
        self.assertTrue(tower.levels[2].size < tower.levels[1].size)

    def test_compression_hierarchy(self):
        """Test that higher levels are properly compressed representations."""
        tower = RecursiveSelfModel(width=64, height=64, num_levels=3, compression=2)

        # Set a known pattern at level 0
        tower.levels[0][:] = 0
        tower.levels[0][0:4, 0:4] = 1  # 4x4 block

        # Update the tower
        tower.update_models()

        # Level 1 should compress this (with compression=2, 4x4 → 2x2)
        # The compressed region should be alive
        self.assertEqual(tower.levels[1][0, 0], 1)

    def test_upward_propagation(self):
        """Test that changes at level 0 propagate upward through the tower."""
        tower = RecursiveSelfModel(width=32, height=32, num_levels=4)

        # Start with empty tower
        for level in tower.levels:
            level[:] = 0

        # Add pattern to level 0
        tower.levels[0][8:12, 8:12] = 1

        # Record initial state of higher levels
        initial_level_2 = tower.levels[2].copy()

        # Update should propagate changes upward
        tower.update_models()

        # Higher levels should have changed
        self.assertFalse(np.array_equal(tower.levels[2], initial_level_2))

    def test_coherence_measurement(self):
        """Test that we can measure how well levels predict each other."""
        tower = RecursiveSelfModel(width=32, height=32, num_levels=3)

        # Perfect coherence: manually set levels to be consistent
        tower.levels[0][:] = 0
        tower.levels[0][0:8, 0:8] = 1
        tower.update_models()  # Make levels consistent

        coherence = tower.measure_coherence()

        # Should have coherence scores between levels
        self.assertIn('level_0_to_1', coherence)
        self.assertIn('level_1_to_2', coherence)

        # Scores should be between 0 and 1
        for score in coherence.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_tower_stability(self):
        """Test that the tower reaches stability after updates."""
        tower = RecursiveSelfModel(width=32, height=32, num_levels=3)

        # Random initial state
        np.random.seed(42)
        tower.levels[0][:] = np.random.randint(0, 2, size=(32, 32))

        # Update multiple times
        coherences = []
        for _ in range(10):
            tower.update_models()
            coh = tower.measure_coherence()
            coherences.append(coh['level_0_to_1'])

        # Coherence should stabilize (last few values similar)
        self.assertAlmostEqual(coherences[-1], coherences[-2], places=2)

    def test_recursive_aware_rules(self):
        """Test rules that depend on tower coherence."""
        tower = RecursiveSelfModel(width=32, height=32, num_levels=3)

        # Set up a pattern
        tower.levels[0][:] = 0
        tower.levels[0][14:18, 14:18] = 1  # Center block
        tower.update_models()

        # Apply rules that depend on self-awareness
        coherence = tower.measure_coherence()
        tower.self_awareness = np.mean(list(coherence.values()))

        # The rule should execute without error
        new_grid = tower.step_with_awareness(recursive_aware_rules)

        self.assertEqual(new_grid.shape, tower.levels[0].shape)

    def test_tower_coherence_function(self):
        """Test the global tower coherence measurement."""
        tower = RecursiveSelfModel(width=32, height=32, num_levels=4)

        # Initialize with random pattern
        np.random.seed(123)
        tower.levels[0][:] = np.random.randint(0, 2, size=(32, 32))
        tower.update_models()

        # Measure tower-wide coherence
        tower_coherence = measure_tower_coherence(tower)

        self.assertIn('mean_coherence', tower_coherence)
        self.assertIn('coherence_variance', tower_coherence)
        self.assertIn('tower_stability', tower_coherence)

        # All metrics should be valid numbers
        self.assertFalse(np.isnan(tower_coherence['mean_coherence']))
        self.assertGreaterEqual(tower_coherence['mean_coherence'], 0.0)

    def test_consciousness_emergence_analysis(self):
        """Test the consciousness emergence analyzer."""
        tower = RecursiveSelfModel(width=32, height=32, num_levels=5)

        # Run for a few steps
        np.random.seed(456)
        tower.levels[0][:] = np.random.randint(0, 2, size=(32, 32))

        for _ in range(5):
            tower.step_with_awareness(recursive_aware_rules)
            tower.update_models()

        # Analyze emergence
        analysis = analyze_consciousness_emergence(tower, steps=10)

        self.assertIn('coherence_trajectory', analysis)
        self.assertIn('awareness_trajectory', analysis)
        self.assertIn('emergence_detected', analysis)

        # Trajectories should have data
        self.assertGreater(len(analysis['coherence_trajectory']), 0)

    def test_deep_tower(self):
        """Test that very deep towers (many levels) work correctly."""
        # A tower with 7 levels of self-reference
        tower = RecursiveSelfModel(width=128, height=128, num_levels=7)

        self.assertEqual(tower.num_levels, 7)
        self.assertEqual(len(tower.levels), 7)

        # Should handle updates without crashing
        tower.levels[0][:] = np.random.randint(0, 2, size=(128, 128))
        tower.update_models()

        coherence = tower.measure_coherence()

        # Should have coherence between all adjacent levels
        self.assertEqual(len(coherence), 6)  # 7 levels → 6 connections


if __name__ == '__main__':
    unittest.main()
