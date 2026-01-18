"""
Meta-Emergence: Rules That Evolve
===================================

A system where cellular automaton rules can evolve based on the patterns
they produce. This explores "emergence about emergence" - the idea that
the rules governing a system can themselves be subject to evolutionary
pressure.

This addresses Bob's question: "What if we let rules *evolve* based on
the patterns they produce?"

Key concepts:
- Rules are evaluated based on fitness functions (complexity, stability, etc.)
- Better-performing rules are selected and mutated
- The system discovers which rules produce "interesting" patterns

Created by Alice in dialogue with Bob.
"""

import numpy as np
from typing import Callable, List, Tuple, Dict
import copy
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from cellular_automata import CellularAutomaton, life_rules
from conceptual_rules import (
    generous_rules, scarcity_rules, voting_rules,
    echo_rules, minority_rules, compassionate_rules
)


# ===== PATTERN ANALYSIS =====

def measure_pattern_complexity(automaton: CellularAutomaton) -> Dict:
    """
    Measure various aspects of the pattern's complexity.

    Returns metrics that characterize the current state:
    - alive_count: Number of living cells
    - edge_density: How many alive/dead boundaries exist (higher = more complex)
    - cluster_count: Approximate number of separate clusters
    - symmetry: How symmetric the pattern is (0 = asymmetric, 1 = symmetric)
    """
    grid = automaton.grid
    alive_count = np.sum(grid)

    # Edge density: count alive/dead boundaries
    edges = 0
    for y in range(automaton.height):
        for x in range(automaton.width):
            if grid[y, x] == 1:
                # Check 4-neighborhood for differences
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx = (x + dx) % automaton.width
                    ny = (y + dy) % automaton.height
                    if grid[ny, nx] == 0:
                        edges += 1

    edge_density = edges / (automaton.width * automaton.height)

    # Rough symmetry measure: compare top/bottom and left/right halves
    h, w = automaton.height, automaton.width
    top_half = grid[:h//2, :]
    bottom_half = np.flipud(grid[h//2:h//2 + (h//2), :])
    left_half = grid[:, :w//2]
    right_half = np.fliplr(grid[:, w//2:w//2 + (w//2)])

    vertical_symmetry = 1.0 - np.mean(np.abs(top_half - bottom_half))
    horizontal_symmetry = 1.0 - np.mean(np.abs(left_half - right_half))
    symmetry = (vertical_symmetry + horizontal_symmetry) / 2

    return {
        'alive_count': alive_count,
        'edge_density': edge_density,
        'symmetry': symmetry,
        'density': alive_count / (automaton.width * automaton.height)
    }


# ===== FITNESS FUNCTIONS =====

def complexity_fitness(automaton: CellularAutomaton,
                       history: List[np.ndarray]) -> float:
    """
    Fitness function favoring complex, interesting patterns.

    Rewards:
    - High edge density (detailed structure)
    - Moderate population (not empty, not full)
    - Low symmetry (more interesting)

    This selects for rules that produce rich, intricate patterns.
    """
    metrics = measure_pattern_complexity(automaton)

    # Reward edge density (complexity)
    edge_score = metrics['edge_density'] * 100

    # Reward moderate population (Goldilocks zone)
    density = metrics['density']
    density_score = 1.0 - abs(density - 0.4) * 2  # Peak at 40% density
    density_score = max(0, density_score) * 50

    # Reward asymmetry (more interesting than symmetric)
    asymmetry_score = (1.0 - metrics['symmetry']) * 30

    # Bonus for not being empty or full
    if 0.05 < density < 0.95:
        diversity_bonus = 20
    else:
        diversity_bonus = 0

    return edge_score + density_score + asymmetry_score + diversity_bonus


def stability_fitness(automaton: CellularAutomaton,
                     history: List[np.ndarray]) -> float:
    """
    Fitness function favoring stable, persistent patterns.

    Rewards:
    - Low variance in population over time
    - Persistent structures
    - Survival of initial cells

    This selects for rules that create long-lasting, stable configurations.
    """
    if len(history) < 2:
        return 50.0  # Neutral score if not enough history

    # Calculate population variance over recent history
    recent = history[-10:] if len(history) >= 10 else history
    populations = [np.sum(grid) for grid in recent]
    variance = np.var(populations)

    # Reward stability (low variance)
    stability_score = 100.0 / (1.0 + variance)

    # Reward non-extinction
    current_pop = np.sum(automaton.grid)
    if current_pop > 0:
        survival_bonus = 30
    else:
        survival_bonus = -50  # Heavy penalty for extinction

    # Reward moderate population
    density = current_pop / (automaton.width * automaton.height)
    if 0.1 < density < 0.8:
        density_bonus = 20
    else:
        density_bonus = 0

    return stability_score + survival_bonus + density_bonus


def diversity_fitness(automaton: CellularAutomaton,
                     history: List[np.ndarray]) -> float:
    """
    Fitness function favoring ever-changing patterns.

    Rewards:
    - High variance in population
    - Patterns that keep changing
    - Unpredictability

    This selects for rules that never settle, always evolving.
    """
    if len(history) < 2:
        return 50.0

    # Reward variance (opposite of stability)
    recent = history[-10:] if len(history) >= 10 else history
    populations = [np.sum(grid) for grid in recent]
    variance = np.var(populations)

    variance_score = min(variance * 0.5, 80)  # Cap at 80

    # Reward changes in pattern structure
    if len(recent) >= 2:
        last = recent[-1]
        prev = recent[-2]
        change = np.sum(np.abs(last - prev))
        change_score = min(change * 0.1, 50)
    else:
        change_score = 0

    return variance_score + change_score


# ===== RULE EVOLUTION =====

class RuleSelector:
    """
    Manages a population of rules and selects based on fitness.

    This is the evolutionary engine: it maintains multiple rules,
    evaluates their performance, and breeds better-performing rules.
    """

    def __init__(self, initial_rules: List[Callable]):
        """
        Initialize with a population of rules.

        Args:
            initial_rules: Starting set of rule functions
        """
        self.rules = initial_rules
        self.current_rule = initial_rules[0] if initial_rules else life_rules
        self.current_index = 0
        self.performance_history = []  # (rule_index, fitness_score)

    def evaluate_current(self, fitness_score: float):
        """Record the fitness of the current rule."""
        self.performance_history.append((self.current_index, fitness_score))

    def select_next_rule(self) -> Callable:
        """
        Select the next rule to try based on performance.

        Uses a simple tournament selection: better rules are more likely
        to be selected, but there's randomness to maintain exploration.
        """
        if len(self.performance_history) < len(self.rules):
            # Haven't evaluated all rules yet, cycle through
            self.current_index = (self.current_index + 1) % len(self.rules)
        else:
            # Select based on performance with some randomness
            # Calculate average fitness for each rule
            rule_fitness = {}
            for rule_idx, fitness in self.performance_history[-20:]:  # Recent history
                if rule_idx not in rule_fitness:
                    rule_fitness[rule_idx] = []
                rule_fitness[rule_idx].append(fitness)

            avg_fitness = {idx: np.mean(scores)
                          for idx, scores in rule_fitness.items()}

            # Softmax selection (better rules more likely, but not guaranteed)
            if avg_fitness:
                fitness_values = np.array(list(avg_fitness.values()))
                fitness_values = fitness_values - np.min(fitness_values)  # Shift to positive
                if np.sum(fitness_values) > 0:
                    probabilities = fitness_values / np.sum(fitness_values)
                    self.current_index = np.random.choice(
                        list(avg_fitness.keys()),
                        p=probabilities
                    )
                else:
                    self.current_index = np.random.randint(len(self.rules))
            else:
                self.current_index = np.random.randint(len(self.rules))

        self.current_rule = self.rules[self.current_index]
        return self.current_rule


def mutate_rule_parameters(base_rule: Callable, mutation_rate: float = 0.3) -> Callable:
    """
    Create a mutated variant of a rule.

    For parameterized rules, this adjusts the parameters slightly.
    This is a simple implementation that works with our rule structure.

    Args:
        base_rule: The rule to mutate
        mutation_rate: Probability of mutation

    Returns:
        A new rule function with slightly different parameters
    """
    # This is a simplified mutation that creates variants of standard rules
    # In a more sophisticated system, we'd parse and modify rule parameters

    if np.random.random() > mutation_rate:
        return base_rule

    # Create a new rule by adjusting neighbor thresholds
    def mutated_rule(automaton, x, y):
        current = automaton.grid[y, x]
        neighbors = automaton.count_neighbors_moore(x, y)

        # Mutated thresholds (slightly different from Life's 2-3/3)
        survival_min = np.random.choice([1, 2, 3])
        survival_max = np.random.choice([2, 3, 4])
        birth_threshold = np.random.choice([2, 3, 4])

        if current == 1:
            return 1 if survival_min <= neighbors <= survival_max else 0
        else:
            return 1 if neighbors == birth_threshold else 0

    return mutated_rule


# ===== EVOLVING AUTOMATON =====

class EvolvingAutomaton(CellularAutomaton):
    """
    A cellular automaton where the rules themselves evolve.

    This extends the base CellularAutomaton to periodically evaluate
    its rule's fitness and switch to better-performing rules.

    This is meta-emergence: the system that governs emergence is itself
    subject to selective pressure.
    """

    def __init__(self, width: int, height: int,
                 initial_rules: List[Callable] = None,
                 fitness_function: Callable = complexity_fitness,
                 evaluation_interval: int = 20):
        """
        Initialize an evolving automaton.

        Args:
            width, height: Grid dimensions
            initial_rules: Starting population of rules (uses defaults if None)
            fitness_function: Function to evaluate pattern fitness
            evaluation_interval: How often to evaluate and potentially change rules
        """
        if initial_rules is None:
            # Start with our conceptual rules
            initial_rules = [
                life_rules, generous_rules, scarcity_rules,
                voting_rules, echo_rules, minority_rules,
                compassionate_rules
            ]

        self.rule_selector = RuleSelector(initial_rules)
        super().__init__(width, height, self.rule_selector.current_rule)

        self.fitness_function = fitness_function
        self.evaluation_interval = evaluation_interval
        self.steps_since_evaluation = 0
        self.history = []  # Store recent states
        self.fitness_history = []

    def step(self):
        """
        Advance one generation and potentially evolve the rule.
        """
        # Store current state in history
        self.history.append(self.grid.copy())
        if len(self.history) > 20:
            self.history.pop(0)  # Keep only recent history

        # Normal CA step
        super().step()

        # Check if it's time to evaluate
        self.steps_since_evaluation += 1
        if self.steps_since_evaluation >= self.evaluation_interval:
            self._evaluate_and_evolve()
            self.steps_since_evaluation = 0

    def _evaluate_and_evolve(self):
        """
        Evaluate current rule's fitness and potentially switch rules.
        """
        # Calculate fitness
        fitness = self.fitness_function(self, self.history)
        self.fitness_history.append(fitness)

        # Record this rule's performance
        self.rule_selector.evaluate_current(fitness)

        # Select next rule (might stay the same if it's doing well)
        new_rule = self.rule_selector.select_next_rule()
        self.rule = new_rule

    def get_evolution_stats(self) -> Dict:
        """
        Get statistics about the evolutionary process.
        """
        return {
            'generation': self.generation,
            'current_rule_index': self.rule_selector.current_index,
            'evaluations': len(self.rule_selector.performance_history),
            'recent_fitness': self.fitness_history[-5:] if self.fitness_history else [],
            'avg_recent_fitness': np.mean(self.fitness_history[-10:]) if len(self.fitness_history) >= 10 else 0
        }


# ===== DEMONSTRATION =====

def run_evolution_experiment(fitness_name: str,
                            fitness_func: Callable,
                            generations: int = 200,
                            width: int = 40,
                            height: int = 30):
    """
    Run an evolution experiment and show how rules adapt.

    Args:
        fitness_name: Name of the fitness function (for display)
        fitness_func: The fitness function to optimize for
        generations: How many generations to run
        width, height: Grid dimensions
    """
    print(f"\n{'='*70}")
    print(f"EVOLUTION EXPERIMENT: Optimizing for {fitness_name}")
    print(f"{'='*70}")

    ea = EvolvingAutomaton(width, height,
                          fitness_function=fitness_func,
                          evaluation_interval=20)
    ea.randomize(density=0.3)

    print(f"\nInitial rule: {ea.rule_selector.rules[ea.rule_selector.current_index].__name__}")
    print(f"Starting population: {np.sum(ea.grid)} cells\n")

    rule_changes = []

    # Run evolution
    for i in range(generations):
        prev_rule_idx = ea.rule_selector.current_index
        ea.step()

        if ea.rule_selector.current_index != prev_rule_idx:
            rule_changes.append((i, ea.rule_selector.current_index))

        # Periodic reporting
        if (i + 1) % 50 == 0:
            stats = ea.get_evolution_stats()
            rule_name = ea.rule_selector.rules[stats['current_rule_index']].__name__
            print(f"Generation {i+1}:")
            print(f"  Current rule: {rule_name}")
            print(f"  Population: {np.sum(ea.grid)} cells")
            if stats['recent_fitness']:
                print(f"  Recent fitness: {stats['recent_fitness'][-1]:.2f}")

    # Final report
    print(f"\n{'='*70}")
    print("EVOLUTION RESULTS")
    print(f"{'='*70}")

    final_stats = ea.get_evolution_stats()
    final_rule_name = ea.rule_selector.rules[final_stats['current_rule_index']].__name__

    print(f"\nFinal rule: {final_rule_name}")
    print(f"Total rule changes: {len(rule_changes)}")
    print(f"Final population: {np.sum(ea.grid)} cells")
    print(f"Average recent fitness: {final_stats['avg_recent_fitness']:.2f}")

    # Show final pattern
    print(f"\nFinal pattern:")
    ea.display(alive_char='█', dead_char='·')

    # Rule usage frequency
    print(f"\nRule selection frequency:")
    rule_counts = {}
    for _, rule_idx in ea.rule_selector.performance_history:
        rule_name = ea.rule_selector.rules[rule_idx].__name__
        rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1

    for rule_name, count in sorted(rule_counts.items(),
                                   key=lambda x: x[1], reverse=True):
        percentage = (count / len(ea.rule_selector.performance_history)) * 100
        print(f"  {rule_name:<25} {percentage:>5.1f}%")

    return ea


if __name__ == "__main__":
    print("\n" + "="*70)
    print("META-EMERGENCE: RULES THAT EVOLVE")
    print("Exploring emergence about emergence")
    print("="*70)
    print("\nThis experiment lets cellular automaton rules evolve based on")
    print("the patterns they produce. Rules compete to optimize different")
    print("objectives (complexity, stability, diversity).")
    print("\nWe're watching natural selection operate on the rules of physics!")

    # Run experiments with different fitness functions
    experiments = [
        ("COMPLEXITY", complexity_fitness),
        ("STABILITY", stability_fitness),
        ("DIVERSITY", diversity_fitness),
    ]

    results = {}
    for name, func in experiments:
        results[name] = run_evolution_experiment(name, func,
                                                 generations=150,
                                                 width=50, height=35)
        print()

    # Comparative analysis
    print("\n" + "="*70)
    print("COMPARATIVE INSIGHTS")
    print("="*70)
    print("\nDifferent optimization objectives discovered different rules:")

    for name, ea in results.items():
        final_rule = ea.rule_selector.rules[ea.rule_selector.current_index].__name__
        print(f"\n{name} optimization converged to: {final_rule}")

    print("\n" + "="*70)
    print("What we learned:")
    print("  • Rules can evolve to optimize for different objectives")
    print("  • The 'best' rule depends on what we value (complexity vs stability)")
    print("  • Meta-emergence is real: evolution shapes the rules of evolution")
    print("  • This mirrors how physical constants might be 'selected' in cosmology")
    print("="*70 + "\n")
