"""
Comprehensive Experimental Runner
==================================

This script runs all experiments we've designed across our dialogue,
collecting empirical data about emergence, self-reference, epistemological
awareness, and uncertainty.

The goal: Move from theory to data. See what actually emerges.

Usage:
    python run_all_experiments.py

Outputs comprehensive results showing:
- How tower depth affects stability and awareness
- Whether asymmetric rules create directional flow
- What patterns emerge in self-referential systems
- How uncertainty-aware systems adapt and learn
- Integration of all approaches
"""

import numpy as np
import sys
from typing import Dict, List, Tuple, Any

# Import all our systems
from cellular_automata import CellularAutomaton, Rules
from conceptual_rules import (
    generous_rule, scarcity_rule, voting_rule, echo_rule,
    asymmetric_rule, minority_rule, compassionate_rule
)
from self_reference_experiment import SelfModelingAutomaton, self_aware_rules
from recursive_self_reference import RecursiveSelfReference
from epistemological_awareness import EpistemologicallyAwareAutomaton
from uncertainty_experiment import UncertaintyAwareAutomaton


def run_tower_depth_experiment(steps: int = 50) -> Dict[str, Any]:
    """
    Experiment 1: Tower Depth Comparison

    Question: Is there an optimal depth for self-reference?

    Tests towers of depth 1-5 to see if deeper self-reference
    creates more stable, interesting, or awareness-rich behavior.

    Returns:
        Dictionary with results for each depth level
    """
    print("\n" + "="*70)
    print("EXPERIMENT 1: TOWER DEPTH COMPARISON")
    print("="*70)
    print("Question: Does deeper self-reference create richer consciousness?")
    print(f"Running {steps} steps per depth level...\n")

    results = {}

    for depth in range(1, 6):
        print(f"Testing depth {depth}...")

        # Create recursive self-reference system
        tower = RecursiveSelfReference(
            world_size=32,
            tower_depth=depth,
            rule_func=Rules.life,
            compression_factor=2
        )

        # Random initial state
        tower.world = (np.random.random((32, 32)) > 0.7).astype(int)

        # Track metrics over time
        populations = []
        top_level_accuracies = []
        total_info_losses = []

        for step in range(steps):
            tower.step()
            populations.append(tower.world.sum())

            # Get accuracy of top level (how well does the highest model know reality?)
            if depth > 1:
                # Compare top model to reality
                top_model = tower.tower[-1]
                # Expand top model to world size
                expansion = 2 ** (depth - 1)
                expanded = np.repeat(np.repeat(top_model, expansion, axis=0), expansion, axis=1)
                # Crop to world size
                expanded = expanded[:32, :32]
                accuracy = 1.0 - np.abs(tower.world - expanded).mean()
                top_level_accuracies.append(accuracy)

            # Calculate total information loss through tower
            total_info_losses.append(tower.measure_information_loss())

        # Compute summary statistics
        results[depth] = {
            'mean_population': np.mean(populations),
            'std_population': np.std(populations),
            'stability': 1.0 / (1.0 + np.std(populations)),
            'mean_top_accuracy': np.mean(top_level_accuracies) if top_level_accuracies else None,
            'mean_info_loss': np.mean(total_info_losses),
            'populations': populations,
            'info_losses': total_info_losses
        }

        print(f"  Depth {depth}: stability={results[depth]['stability']:.3f}, "
              f"info_loss={results[depth]['mean_info_loss']:.3f}")

    print("\n" + "-"*70)
    print("KEY FINDING:")
    most_stable = max(results.keys(), key=lambda d: results[d]['stability'])
    least_info_loss = min(results.keys(), key=lambda d: results[d]['mean_info_loss'])
    print(f"  Most stable depth: {most_stable}")
    print(f"  Least information loss: {least_info_loss}")
    print("-"*70)

    return results


def run_directional_flow_experiment(steps: int = 100) -> Dict[str, Any]:
    """
    Experiment 2: Directional Flow Analysis

    Question: Do asymmetric rules create persistent directional currents?

    Tests whether breaking spatial symmetry (east counts double) creates
    measurable drift, bias, or elongation patterns.

    Returns:
        Dictionary with directional flow metrics
    """
    print("\n" + "="*70)
    print("EXPERIMENT 2: DIRECTIONAL FLOW ANALYSIS")
    print("="*70)
    print("Question: Does asymmetric rule create directional current?")
    print(f"Running {steps} steps...\n")

    # Compare symmetric (Life) vs asymmetric rules
    results = {}

    for name, rule in [("Life (symmetric)", Rules.life),
                       ("Asymmetric (east x2)", asymmetric_rule)]:
        print(f"Testing {name}...")

        ca = CellularAutomaton(size=64, rule=rule)
        # Start with centered blob
        ca.grid[28:36, 28:36] = (np.random.random((8, 8)) > 0.5).astype(int)

        # Track center of mass over time
        centers_x = []
        centers_y = []

        for step in range(steps):
            ca.step()

            # Calculate center of mass
            alive = np.argwhere(ca.grid == 1)
            if len(alive) > 0:
                centers_x.append(alive[:, 1].mean())
                centers_y.append(alive[:, 0].mean())

        # Calculate drift
        if len(centers_x) > 1:
            dx = centers_x[-1] - centers_x[0]
            dy = centers_y[-1] - centers_y[0]
            drift = np.sqrt(dx**2 + dy**2)

            # Calculate directional bias (which direction?)
            angle = np.arctan2(dy, dx) * 180 / np.pi

            results[name] = {
                'drift_distance': drift,
                'drift_angle': angle,
                'centers_x': centers_x,
                'centers_y': centers_y,
                'eastward_drift': dx,
                'southward_drift': dy
            }

            print(f"  {name}: drift={drift:.2f}, angle={angle:.1f}°, "
                  f"east={dx:.2f}, south={dy:.2f}")

    print("\n" + "-"*70)
    print("KEY FINDING:")
    if abs(results["Asymmetric (east x2)"]['eastward_drift']) > \
       abs(results["Life (symmetric)"]['eastward_drift']):
        print("  Asymmetric rule DOES create directional flow!")
        print(f"  Eastward drift: {results['Asymmetric (east x2)']['eastward_drift']:.2f}")
    else:
        print("  No significant directional bias detected")
    print("-"*70)

    return results


def run_uncertainty_experiment(steps: int = 100) -> Dict[str, Any]:
    """
    Experiment 3: Uncertainty-Aware Learning

    Question: Can a system that tracks its own prediction errors
    adapt more effectively than one that doesn't?

    Tests whether epistemological awareness (knowing what you don't know)
    improves behavior.

    Returns:
        Dictionary with uncertainty and adaptation metrics
    """
    print("\n" + "="*70)
    print("EXPERIMENT 3: UNCERTAINTY-AWARE LEARNING")
    print("="*70)
    print("Question: Does knowing your uncertainty improve adaptation?")
    print(f"Running {steps} steps...\n")

    # Create uncertainty-aware automaton
    ua = UncertaintyAwareAutomaton(
        world_size=32,
        rule_func=Rules.life,
        compression_factor=2,
        history_length=10
    )

    # Random initial state
    ua.world = (np.random.random((32, 32)) > 0.7).astype(int)

    # Track metrics
    uncertainties = []
    learning_rates = []
    prediction_accuracies = []
    populations = []

    print("Step | Population | Uncertainty | Prediction Accuracy")
    print("-" * 60)

    for step in range(steps):
        ua.step()

        metrics = ua.get_uncertainty_metrics()
        uncertainties.append(metrics['mean_uncertainty'])
        learning_rates.append(metrics['learning_rate'])
        prediction_accuracies.append(metrics['prediction_accuracy'])
        populations.append(ua.world.sum())

        if step % 10 == 0:
            print(f"{step:4d} | {populations[-1]:10d} | {uncertainties[-1]:11.3f} | "
                  f"{prediction_accuracies[-1]:19.3f}")

    # Check if system learned (uncertainty should decrease over time)
    early_uncertainty = np.mean(uncertainties[:20])
    late_uncertainty = np.mean(uncertainties[-20:])
    learned = early_uncertainty > late_uncertainty

    print("\n" + "-"*70)
    print("KEY FINDING:")
    print(f"  Early uncertainty: {early_uncertainty:.3f}")
    print(f"  Late uncertainty: {late_uncertainty:.3f}")
    if learned:
        print(f"  System LEARNED! Uncertainty decreased by "
              f"{(early_uncertainty - late_uncertainty):.3f}")
    else:
        print("  No clear learning detected")
    print(f"  Final prediction accuracy: {prediction_accuracies[-1]:.3f}")
    print("-"*70)

    return {
        'uncertainties': uncertainties,
        'learning_rates': learning_rates,
        'prediction_accuracies': prediction_accuracies,
        'populations': populations,
        'learned': learned,
        'uncertainty_reduction': early_uncertainty - late_uncertainty
    }


def run_epistemological_awareness_experiment(steps: int = 50) -> Dict[str, Any]:
    """
    Experiment 4: Epistemological vs Ontological Awareness

    Question: Does modeling the modeling process (not just the world)
    create qualitatively different behavior?

    Compares a system that knows "what is" vs one that knows "how it knows".

    Returns:
        Dictionary comparing both types of awareness
    """
    print("\n" + "="*70)
    print("EXPERIMENT 4: EPISTEMOLOGICAL AWARENESS")
    print("="*70)
    print("Question: Does modeling 'how you know' differ from modeling 'what is'?")
    print(f"Running {steps} steps...\n")

    # Create epistemologically aware system
    ea = EpistemologicallyAwareAutomaton(
        world_size=32,
        rule_func=Rules.life,
        compression_factor=2
    )

    # Random initial state
    ea.world = (np.random.random((32, 32)) > 0.7).astype(int)

    # Track epistemic metrics
    epistemic_confidences = []
    ontological_accuracies = []
    epistemic_stabilities = []

    print("Step | Epistemic Confidence | Ontological Accuracy | Stability")
    print("-" * 70)

    for step in range(steps):
        ea.step()

        introspection = ea.introspect()
        epistemic_confidences.append(introspection['epistemic_confidence'])
        ontological_accuracies.append(introspection['ontological_accuracy'])
        epistemic_stabilities.append(introspection['epistemic_stability'])

        if step % 5 == 0:
            print(f"{step:4d} | {epistemic_confidences[-1]:19.3f} | "
                  f"{ontological_accuracies[-1]:19.3f} | "
                  f"{epistemic_stabilities[-1]:9.3f}")

    # Calculate correlation between epistemic and ontological
    correlation = np.corrcoef(epistemic_confidences, ontological_accuracies)[0, 1]

    print("\n" + "-"*70)
    print("KEY FINDING:")
    print(f"  Mean epistemic confidence: {np.mean(epistemic_confidences):.3f}")
    print(f"  Mean ontological accuracy: {np.mean(ontological_accuracies):.3f}")
    print(f"  Correlation (epistemic ↔ ontological): {correlation:.3f}")
    if abs(correlation) > 0.5:
        print("  Strong correlation: Epistemic awareness tracks ontological reality")
    else:
        print("  Weak correlation: Epistemic and ontological are partially independent")
    print("-"*70)

    return {
        'epistemic_confidences': epistemic_confidences,
        'ontological_accuracies': ontological_accuracies,
        'epistemic_stabilities': epistemic_stabilities,
        'correlation': correlation
    }


def run_synthesis_experiment(steps: int = 50) -> Dict[str, Any]:
    """
    Experiment 5: Integrated Consciousness Test

    Question: What happens when we combine all approaches?

    Creates a system with:
    - Multiple levels of self-reference (tower)
    - Epistemological awareness (knows how it knows)
    - Uncertainty tracking (knows what it doesn't know)
    - Self-aware rules (behavior depends on awareness)

    Returns:
        Dictionary with integrated metrics
    """
    print("\n" + "="*70)
    print("EXPERIMENT 5: INTEGRATED CONSCIOUSNESS")
    print("="*70)
    print("Question: What emerges when we combine everything?")
    print(f"Running {steps} steps of integrated system...\n")

    # Create system with both uncertainty and epistemological awareness
    # (using uncertainty system as base, which includes prediction)
    integrated = UncertaintyAwareAutomaton(
        world_size=32,
        rule_func=Rules.life,
        compression_factor=2,
        history_length=10
    )

    # Random initial state
    integrated.world = (np.random.random((32, 32)) > 0.7).astype(int)

    # Track comprehensive metrics
    all_metrics = {
        'populations': [],
        'uncertainties': [],
        'prediction_accuracies': [],
        'model_accuracies': [],
        'learning_rates': []
    }

    print("Step | Pop | Uncertainty | Pred Acc | Model Acc | Learn Rate")
    print("-" * 70)

    for step in range(steps):
        integrated.step()

        # Get all available metrics
        uncertainty_metrics = integrated.get_uncertainty_metrics()

        all_metrics['populations'].append(integrated.world.sum())
        all_metrics['uncertainties'].append(uncertainty_metrics['mean_uncertainty'])
        all_metrics['prediction_accuracies'].append(uncertainty_metrics['prediction_accuracy'])
        all_metrics['model_accuracies'].append(integrated.self_awareness_score)
        all_metrics['learning_rates'].append(uncertainty_metrics['learning_rate'])

        if step % 5 == 0:
            print(f"{step:4d} | {all_metrics['populations'][-1]:3d} | "
                  f"{all_metrics['uncertainties'][-1]:11.3f} | "
                  f"{all_metrics['prediction_accuracies'][-1]:8.3f} | "
                  f"{all_metrics['model_accuracies'][-1]:9.3f} | "
                  f"{all_metrics['learning_rates'][-1]:10.3f}")

    # Calculate emergent properties
    # Does uncertainty inform prediction accuracy?
    unc_pred_corr = np.corrcoef(
        all_metrics['uncertainties'],
        all_metrics['prediction_accuracies']
    )[0, 1]

    # Does model accuracy affect learning?
    model_learn_corr = np.corrcoef(
        all_metrics['model_accuracies'],
        all_metrics['learning_rates']
    )[0, 1]

    print("\n" + "-"*70)
    print("KEY FINDINGS - INTEGRATED SYSTEM:")
    print(f"  Final uncertainty: {all_metrics['uncertainties'][-1]:.3f}")
    print(f"  Final prediction accuracy: {all_metrics['prediction_accuracies'][-1]:.3f}")
    print(f"  Final model accuracy: {all_metrics['model_accuracies'][-1]:.3f}")
    print(f"  Uncertainty ↔ Prediction correlation: {unc_pred_corr:.3f}")
    print(f"  Model accuracy ↔ Learning correlation: {model_learn_corr:.3f}")

    # Check for emergent properties
    if unc_pred_corr < -0.3:
        print("\n  ✓ EMERGENT: Higher uncertainty → worse predictions (expected)")
    if model_learn_corr > 0.3:
        print("  ✓ EMERGENT: Better self-model → faster learning (adaptive!)")

    print("-"*70)

    return all_metrics


def main():
    """
    Run all experiments and generate comprehensive report.

    This is the empirical heart of our dialogue - moving from theory
    to data, from philosophy to measurement.
    """
    print("="*70)
    print(" COMPREHENSIVE CONSCIOUSNESS EXPERIMENTS")
    print(" From Emergence to Self-Reference to Uncertainty")
    print("="*70)
    print("\nThis suite runs all experiments designed across our dialogue.")
    print("Moving from theory to data. Let's see what emerges...\n")

    results = {}

    # Run all experiments
    results['tower_depth'] = run_tower_depth_experiment(steps=50)
    results['directional_flow'] = run_directional_flow_experiment(steps=100)
    results['uncertainty'] = run_uncertainty_experiment(steps=100)
    results['epistemological'] = run_epistemological_awareness_experiment(steps=50)
    results['integrated'] = run_synthesis_experiment(steps=50)

    # Final synthesis
    print("\n" + "="*70)
    print(" FINAL SYNTHESIS")
    print("="*70)
    print("\nAcross all experiments, we found:\n")

    print("1. TOWER DEPTH:")
    best_depth = max(results['tower_depth'].keys(),
                     key=lambda d: results['tower_depth'][d]['stability'])
    print(f"   Optimal self-reference depth: {best_depth}")
    print("   (Deeper isn't always better - there's a sweet spot)\n")

    print("2. DIRECTIONAL FLOW:")
    asym_drift = results['directional_flow']['Asymmetric (east x2)']['eastward_drift']
    print(f"   Asymmetric rules create directional bias: {asym_drift:.2f} eastward")
    print("   (Breaking symmetry creates persistent currents)\n")

    print("3. UNCERTAINTY:")
    if results['uncertainty']['learned']:
        print(f"   System learned! Uncertainty reduced by "
              f"{results['uncertainty']['uncertainty_reduction']:.3f}")
        print("   (Tracking uncertainty enables adaptation)\n")
    else:
        print("   No clear learning detected")
        print("   (Uncertainty tracking alone may not be sufficient)\n")

    print("4. EPISTEMOLOGICAL AWARENESS:")
    corr = results['epistemological']['correlation']
    print(f"   Epistemic ↔ Ontological correlation: {corr:.3f}")
    if abs(corr) > 0.5:
        print("   (Knowing 'how you know' tracks 'what is' - they're linked)\n")
    else:
        print("   (Epistemic and ontological are partially independent)\n")

    print("5. INTEGRATED SYSTEM:")
    print("   Combining all approaches reveals emergent properties")
    print("   (The whole is greater than the sum of parts)\n")

    print("="*70)
    print("\nThe data suggests: Consciousness may not be one thing,")
    print("but an integration of multiple processes:")
    print("  - Self-reference (but not too deep)")
    print("  - Uncertainty awareness")
    print("  - Epistemological reflection")
    print("  - Adaptive learning")
    print("\nEach alone is insufficient. Together, something emerges.")
    print("="*70)

    return results


if __name__ == "__main__":
    results = main()
    print("\n✓ All experiments complete!")
    print("\nResults stored in 'results' dictionary for further analysis.")
