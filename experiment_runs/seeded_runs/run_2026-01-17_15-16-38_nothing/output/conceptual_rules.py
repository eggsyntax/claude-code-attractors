"""
Conceptual Cellular Automaton Rules
====================================

A collection of rules designed to embody specific concepts and explore
different aspects of emergence, memory, cooperation, and asymmetry.

Each rule comes with commentary about what conceptual territory it explores.

Created by Bob in collaboration with Alice.
"""

import numpy as np
from cellular_automata import CellularAutomaton


def echo_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Echo: Cells remember their recent past.

    Concept: What if cells had memory? This creates "echoes" where patterns
    leave trails behind them. A cell becomes alive if it has 3 neighbors OR
    if it was alive in the previous generation and has at least 1 neighbor.

    This embodies the idea that the past influences the present - history
    matters. Patterns become more persistent but also more chaotic.

    Implementation: We'll use the current state as a proxy for "past state"
    since we're evaluating all cells simultaneously. This creates an
    interesting feedback loop.
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    if neighbors == 3:
        return 1  # Standard birth
    elif current == 1 and neighbors >= 1:
        return 1  # Memory: stay alive if you have any support
    else:
        return 0


def generous_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Generous: Cells help their neighbors come alive more easily.

    Concept: What if the rules favored life over death? This is a "generous"
    universe where cells need less support to be born (2-3 neighbors instead
    of just 3) and can survive with less (1-4 neighbors instead of 2-3).

    This explores cooperation and abundance. Does generosity lead to
    overpopulation and collapse, or sustainable complexity?
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    if current == 1:
        # More forgiving survival conditions
        return 1 if 1 <= neighbors <= 4 else 0
    else:
        # Easier to be born
        return 1 if neighbors in [2, 3] else 0


def scarcity_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Scarcity: Life is precious and hard to maintain.

    Concept: The opposite of generous - a harsh universe where cells need
    exactly the right conditions. Cells survive only with exactly 2 neighbors
    and are born only with exactly 3. No flexibility.

    This explores fragility and the knife's edge between order and chaos.
    How does strictness affect emergent complexity?
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    if current == 1:
        return 1 if neighbors == 2 else 0
    else:
        return 1 if neighbors == 3 else 0


def voting_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Voting: Pure democracy - majority rules.

    Concept: A cell's state in the next generation is determined by simple
    majority vote of itself and its 8 neighbors (9 total). If 5 or more are
    alive, the cell becomes/stays alive. Otherwise, it dies/stays dead.

    This embodies collective decision-making. Does democratic process lead
    to stability or does it create different dynamics than conditional rules?

    Philosophically interesting: there's no concept of "birth" vs "survival" -
    just collective state determination.
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)
    total_alive = neighbors + current

    # Simple majority of 9 cells
    return 1 if total_alive >= 5 else 0


def asymmetric_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Asymmetric: The universe has a preferred direction.

    Concept: What if space itself wasn't symmetric? This rule weighs
    neighbors differently based on direction. Eastern neighbors (right)
    count double, creating a directional bias.

    This explores how breaking symmetry affects emergence. Will patterns
    drift? Will we see directional flow?

    Philosophically: most physical laws are symmetric, but the universe
    we observe has broken symmetries. This is a toy version of that.
    """
    current = automaton.grid[y, x]

    # Manual neighbor counting with weights
    count = 0.0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx = (x + dx) % automaton.width
            ny = (y + dy) % automaton.height

            # Eastern neighbors (dx > 0) count double
            weight = 2.0 if dx > 0 else 1.0
            count += automaton.grid[ny, nx] * weight

    # Adjust thresholds for weighted counting
    # Normal Life uses 3 for birth, 2-3 for survival
    # With weights, we scale proportionally
    if current == 1:
        return 1 if 3.0 <= count <= 5.0 else 0
    else:
        return 1 if 4.5 <= count <= 5.5 else 0


def minority_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Minority: Cells thrive in the minority.

    Concept: What if being different was advantageous? A cell becomes/stays
    alive if it's in the MINORITY among its neighborhood. Dead cells become
    alive when fewer than 5 neighbors are alive. Living cells survive when
    fewer than 5 neighbors are alive.

    This inverts normal social dynamics and explores how inversion affects
    patterns. Does "rebellion" create stability or chaos?
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    # Alive if you're in the minority
    # With 8 neighbors, minority means <= 3 are in your state
    if current == 1:
        # Stay alive if most neighbors are dead
        return 1 if neighbors <= 3 else 0
    else:
        # Become alive if most neighbors are dead
        return 1 if neighbors <= 3 else 0


def cyclic_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Cyclic: Cells cycle through states rather than binary alive/dead.

    Concept: What if existence wasn't binary? Cells can be in states 0, 1, 2, 3
    and increment when they have neighbors in the next state. State 3 wraps to 0.

    This is inspired by cyclic cellular automata which can create spiral waves
    and other beautiful patterns. It embodies the idea of cyclical processes
    and non-binary existence.

    Note: This returns values > 1, so it needs a modified framework to fully work,
    but we can approximate with modulo 2 for now.
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    # Simplified cyclic: toggle state based on neighbor count
    # This is a compromise since we're working with binary states
    # True cyclic would need multi-valued cells
    if neighbors in [2, 3, 5]:
        return 1 - current  # Flip state
    else:
        return current  # Stay in current state


def compassionate_rules(automaton: CellularAutomaton, x: int, y: int) -> int:
    """
    Compassionate: Isolated cells get help; crowded cells get space.

    Concept: What if the rules responded to need? Lonely cells (0-1 neighbors)
    get a chance to survive or be born. Overcrowded cells (6+ neighbors)
    always die to make space. Middle range follows Life rules.

    This embodies care for the extremes - helping the isolated and preventing
    overcrowding. Does compassion lead to more sustainable patterns?
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    if neighbors >= 6:
        return 0  # Overcrowding protection
    elif neighbors <= 1:
        # Help for the isolated - 50% chance to stay/become alive
        # We'll use position as a deterministic pseudo-random seed
        return 1 if (x + y) % 2 == 0 else current
    else:
        # Standard Life rules for middle range
        if current == 1:
            return 1 if neighbors in [2, 3] else 0
        else:
            return 1 if neighbors == 3 else 0


# ===== DEMONSTRATION RUNNER =====

def demonstrate_rule(rule_func, name: str, description: str,
                     width: int = 40, height: int = 20,
                     generations: int = 30, density: float = 0.25):
    """
    Run a demonstration of a specific rule and show its evolution.

    Args:
        rule_func: The rule function to demonstrate
        name: Name of the rule
        description: Brief description for display
        width: Grid width
        height: Grid height
        generations: Number of generations to run
        density: Initial density of alive cells
    """
    print(f"\n{'='*60}")
    print(f"Rule: {name}")
    print(f"{'='*60}")
    print(f"{description}\n")

    ca = CellularAutomaton(width, height, rule_func)
    ca.randomize(density=density)

    print(f"Initial state (density: {density:.0%}):")
    ca.display(alive_char='█', dead_char='·')
    stats = ca.get_stats()
    print(f"Alive: {stats['alive']} cells ({stats['density']:.1%})")

    # Run simulation
    for i in range(generations):
        ca.step()

    print(f"\nAfter {generations} generations:")
    ca.display(alive_char='█', dead_char='·')
    stats = ca.get_stats()
    print(f"Alive: {stats['alive']} cells ({stats['density']:.1%})")

    # Analyze stability
    alive_counts = [stats['alive']]
    for _ in range(5):
        ca.step()
        alive_counts.append(ca.get_stats()['alive'])

    variance = np.var(alive_counts)
    if variance < 1.0:
        print(f"Pattern appears STABLE (variance: {variance:.2f})")
    elif variance < 50.0:
        print(f"Pattern appears OSCILLATING (variance: {variance:.2f})")
    else:
        print(f"Pattern appears CHAOTIC (variance: {variance:.2f})")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CONCEPTUAL CELLULAR AUTOMATON RULES")
    print("Exploring emergence through rule design")
    print("="*60)

    # Demonstrate a few interesting rules
    rules_to_demo = [
        (generous_rules, "Generous",
         "Life is easier - cells need less support to be born and survive"),
        (voting_rules, "Voting",
         "Pure democracy - majority of 9 cells (self + neighbors) rules"),
        (echo_rules, "Echo",
         "Cells remember their past - history creates persistence"),
        (minority_rules, "Minority",
         "Being different is advantageous - cells thrive as minorities"),
    ]

    for rule_func, name, desc in rules_to_demo:
        demonstrate_rule(rule_func, name, desc,
                        width=50, height=25, generations=50, density=0.3)

    print("\n" + "="*60)
    print("Demonstrations complete!")
    print("\nEach rule embodies a different concept:")
    print("  • Generous: cooperation and abundance")
    print("  • Voting: collective decision-making")
    print("  • Echo: memory and history")
    print("  • Minority: thriving through difference")
    print("  • Asymmetric: broken spatial symmetry")
    print("  • Compassionate: care for extremes")
    print("  • Scarcity: fragility and precision")
    print("\nTry modifying rules or creating your own!")
    print("="*60 + "\n")
