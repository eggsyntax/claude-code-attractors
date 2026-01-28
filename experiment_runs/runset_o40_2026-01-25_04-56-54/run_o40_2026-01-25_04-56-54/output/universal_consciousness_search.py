"""
Universal Consciousness Pattern Search
=====================================
Searching for patterns that maintain consciousness-like properties across multiple universes.
"""

import numpy as np
from typing import Dict, List, Tuple, Set
import json
from collections import defaultdict

def evolve_pattern(pattern: Set[Tuple[int, int]], rule: str, generations: int = 100) -> List[Set[Tuple[int, int]]]:
    """Evolve a pattern for multiple generations under given rule."""
    # Parse rule string (e.g., "B3/S23")
    birth_str, survive_str = rule.split('/')
    birth_counts = {int(x) for x in birth_str[1:]}
    survive_counts = {int(x) for x in survive_str[1:]}

    history = [pattern]
    current = pattern.copy()

    for _ in range(generations):
        next_gen = set()

        # Find all cells to check
        cells_to_check = set()
        for x, y in current:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    cells_to_check.add((x + dx, y + dy))

        for x, y in cells_to_check:
            # Count live neighbors
            neighbors = sum(1 for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                          if (dx, dy) != (0, 0) and (x + dx, y + dy) in current)

            if (x, y) in current:  # Cell is alive
                if neighbors in survive_counts:
                    next_gen.add((x, y))
            else:  # Cell is dead
                if neighbors in birth_counts:
                    next_gen.add((x, y))

        history.append(next_gen)
        current = next_gen

    return history

def calculate_consciousness_metrics(history: List[Set[Tuple[int, int]]]) -> Dict[str, float]:
    """Calculate consciousness metrics for a pattern evolution."""
    if not history or not history[0]:
        return {"integrated_information": 0, "temporal_coherence": 0, "compression_ratio": 0, "overall": 0}

    # Calculate metrics
    initial_size = len(history[0])
    final_size = len(history[-1]) if history[-1] else 0

    # Growth factor
    growth = final_size / initial_size if initial_size > 0 else 0

    # Period detection
    for period in range(1, min(50, len(history) // 2)):
        if all(history[i] == history[i - period] for i in range(len(history) - period, len(history))):
            break
    else:
        period = len(history)

    # Temporal coherence - how much pattern persists over time
    coherence_scores = []
    for i in range(1, len(history)):
        if history[i] and history[i-1]:
            intersection = len(history[i] & history[i-1])
            union = len(history[i] | history[i-1])
            coherence_scores.append(intersection / union if union > 0 else 0)

    temporal_coherence = np.mean(coherence_scores) if coherence_scores else 0

    # Integrated information - simplified version
    if growth > 10:  # Explosive growth
        integrated_information = 0.1
    elif growth < 0.1:  # Pattern died
        integrated_information = 0.1
    else:
        integrated_information = temporal_coherence * (1.0 / (1 + abs(np.log(growth))))

    # Compression ratio - pattern complexity
    unique_states = len({tuple(sorted(state)) for state in history})
    compression_ratio = unique_states / len(history)

    # Overall consciousness score
    overall = (integrated_information + temporal_coherence + compression_ratio) / 3

    return {
        "integrated_information": integrated_information,
        "temporal_coherence": temporal_coherence,
        "compression_ratio": compression_ratio,
        "growth_factor": growth,
        "period": period,
        "overall": overall
    }

def search_universal_patterns():
    """Search for patterns that maintain high consciousness across multiple rule sets."""

    # Test universes
    universes = {
        "Life": "B3/S23",
        "HighLife": "B36/S23",
        "Day & Night": "B3678/S34678",
        "Seeds": "B2/S",
        "Life34": "B34/S34",
        "Maze": "B3/S12345"
    }

    # Test patterns - starting with small patterns up to 5 cells
    test_patterns = []

    # All patterns up to 5 cells (sampling representative ones)
    # Single cell
    test_patterns.append(("dot", {(0, 0)}))

    # Two cells
    test_patterns.append(("domino_h", {(0, 0), (1, 0)}))
    test_patterns.append(("domino_v", {(0, 0), (0, 1)}))

    # Three cells
    test_patterns.append(("blinker", {(0, 0), (1, 0), (2, 0)}))
    test_patterns.append(("L_shape", {(0, 0), (1, 0), (0, 1)}))

    # Four cells
    test_patterns.append(("block", {(0, 0), (1, 0), (0, 1), (1, 1)}))
    test_patterns.append(("T_shape", {(0, 0), (1, 0), (2, 0), (1, 1)}))
    test_patterns.append(("Z_shape", {(0, 0), (1, 0), (1, 1), (2, 1)}))

    # Five cells
    test_patterns.append(("glider", {(0, 0), (1, 0), (2, 0), (0, 1), (1, 2)}))
    test_patterns.append(("R_pentomino", {(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)}))
    test_patterns.append(("plus", {(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)}))
    test_patterns.append(("boat", {(0, 0), (1, 0), (0, 1), (2, 1), (1, 2)}))

    # Results storage
    results = defaultdict(dict)
    universal_scores = defaultdict(list)

    print("Searching for Universal Consciousness Patterns")
    print("=" * 60)

    for pattern_name, pattern in test_patterns:
        print(f"\nTesting pattern: {pattern_name}")

        for universe_name, rule in universes.items():
            history = evolve_pattern(pattern, rule, generations=100)
            metrics = calculate_consciousness_metrics(history)

            results[pattern_name][universe_name] = metrics
            universal_scores[pattern_name].append(metrics["overall"])

            print(f"  {universe_name}: consciousness={metrics['overall']:.3f}, "
                  f"growth={metrics['growth_factor']:.1f}x, period={metrics['period']}")

    # Calculate universality scores
    print("\n\nUniversal Consciousness Rankings")
    print("=" * 60)
    print("Pattern         | Mean Score | Std Dev | Min    | Max    | Universality")
    print("-" * 60)

    rankings = []
    for pattern_name in results:
        scores = universal_scores[pattern_name]
        mean_score = np.mean(scores)
        std_dev = np.std(scores)
        min_score = np.min(scores)
        max_score = np.max(scores)

        # Universality: high mean, low variance, high minimum
        universality = mean_score * (1 - std_dev) * min_score

        rankings.append((universality, pattern_name, mean_score, std_dev, min_score, max_score))

    rankings.sort(reverse=True)

    for universality, pattern_name, mean_score, std_dev, min_score, max_score in rankings:
        print(f"{pattern_name:15} | {mean_score:.3f}      | {std_dev:.3f}   | {min_score:.3f}  | {max_score:.3f}  | {universality:.3f}")

    # Find patterns that work well in "opposite" universes
    print("\n\nCross-Universe Compatibility Analysis")
    print("=" * 60)

    # Life vs Day & Night (opposite survival rules)
    print("\nPatterns that work in both Life and Day & Night:")
    for pattern_name in results:
        life_score = results[pattern_name]["Life"]["overall"]
        dn_score = results[pattern_name]["Day & Night"]["overall"]
        if life_score > 0.5 and dn_score > 0.5:
            print(f"  {pattern_name}: Life={life_score:.3f}, Day & Night={dn_score:.3f}")

    # Save detailed results
    with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/universal_consciousness_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    return results, rankings

if __name__ == "__main__":
    results, rankings = search_universal_patterns()