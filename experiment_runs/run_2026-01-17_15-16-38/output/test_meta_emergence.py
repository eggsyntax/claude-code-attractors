"""
Test Suite for Meta-Emergence Experiments
==========================================

Tests for systems where rules can evolve based on the patterns they produce.
This explores the idea of "emergence about emergence" - rules that adapt
based on what emerges from them.

Created by Alice in response to Bob's question about meta-emergence.
"""

import numpy as np
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from cellular_automata import CellularAutomaton, life_rules


def test_rule_selector_initialization():
    """Test that a rule selector can initialize properly."""
    from meta_emergence import RuleSelector

    selector = RuleSelector([life_rules])
    assert selector.current_rule == life_rules
    assert len(selector.performance_history) == 0
    print("✓ Rule selector initializes correctly")


def test_pattern_metrics_calculation():
    """Test that we can measure pattern characteristics."""
    from meta_emergence import measure_pattern_complexity

    # Test with known patterns
    ca = CellularAutomaton(10, 10, life_rules)

    # Empty grid should have zero complexity
    metrics = measure_pattern_complexity(ca)
    assert metrics['alive_count'] == 0
    assert metrics['edge_density'] == 0

    # Full grid should have high alive count but low edge density
    ca.grid[:, :] = 1
    metrics = measure_pattern_complexity(ca)
    assert metrics['alive_count'] == 100
    assert metrics['edge_density'] == 0  # No edges in uniform field

    # Checkerboard pattern should have maximum edge density
    ca.grid[::2, ::2] = 1
    ca.grid[1::2, 1::2] = 1
    ca.grid[::2, 1::2] = 0
    ca.grid[1::2, ::2] = 0
    metrics = measure_pattern_complexity(ca)
    assert metrics['edge_density'] > 0.5  # High edge density

    print("✓ Pattern metrics calculation works")


def test_rule_evolution_cycle():
    """Test that rules can evolve through multiple generations."""
    from meta_emergence import EvolvingAutomaton

    ea = EvolvingAutomaton(20, 20, evaluation_interval=10)
    ea.randomize(density=0.3)

    initial_rule = ea.rule_selector.current_rule

    # Run for multiple evaluation cycles
    for _ in range(30):
        ea.step()

    # Should have evaluated performance at least twice
    assert len(ea.rule_selector.performance_history) >= 2

    print("✓ Rule evolution cycle completes successfully")


def test_fitness_evaluation():
    """Test that fitness functions can evaluate patterns."""
    from meta_emergence import complexity_fitness, stability_fitness

    ca = CellularAutomaton(20, 20, life_rules)
    ca.randomize(density=0.3)

    # Run a few steps
    for _ in range(5):
        ca.step()

    # Both fitness functions should return numeric values
    complexity_score = complexity_fitness(ca, [])
    stability_score = stability_fitness(ca, [])

    assert isinstance(complexity_score, (int, float))
    assert isinstance(stability_score, (int, float))
    assert complexity_score >= 0
    assert stability_score >= 0

    print("✓ Fitness evaluation works correctly")


def test_rule_mutation():
    """Test that rules can be mutated to create variants."""
    from meta_emergence import mutate_rule_parameters

    # Create a simple parameterized rule
    def param_rule(automaton, x, y, birth=[3], survival=[2, 3]):
        current = automaton.grid[y, x]
        neighbors = automaton.count_neighbors_moore(x, y)
        if current == 1:
            return 1 if neighbors in survival else 0
        else:
            return 1 if neighbors in birth else 0

    # Test mutation
    mutated = mutate_rule_parameters(param_rule, mutation_rate=0.5)

    # Should return a callable
    assert callable(mutated)

    # Test that mutated rule works
    ca = CellularAutomaton(10, 10, mutated)
    ca.randomize(density=0.3)
    ca.step()

    print("✓ Rule mutation produces valid rules")


def test_comparative_evolution():
    """Test that different fitness functions produce different evolutionary outcomes."""
    from meta_emergence import EvolvingAutomaton
    from meta_emergence import complexity_fitness, stability_fitness

    # This is a longer test - just verify it can run
    ea1 = EvolvingAutomaton(15, 15, fitness_function=complexity_fitness,
                            evaluation_interval=5)
    ea2 = EvolvingAutomaton(15, 15, fitness_function=stability_fitness,
                            evaluation_interval=5)

    ea1.randomize(density=0.3)
    ea2.randomize(density=0.3)

    # Run both for a few cycles
    for _ in range(15):
        ea1.step()
        ea2.step()

    # Both should have performance histories
    assert len(ea1.rule_selector.performance_history) > 0
    assert len(ea2.rule_selector.performance_history) > 0

    print("✓ Comparative evolution experiment runs successfully")


if __name__ == "__main__":
    print("Running tests for meta-emergence system...\n")

    test_rule_selector_initialization()
    test_pattern_metrics_calculation()
    test_fitness_evaluation()
    test_rule_evolution_cycle()
    test_rule_mutation()
    test_comparative_evolution()

    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
    print("\nMeta-emergence system is ready to explore.")
    print("This tests our ability to evolve rules based on")
    print("the patterns they produce - emergence about emergence!")
