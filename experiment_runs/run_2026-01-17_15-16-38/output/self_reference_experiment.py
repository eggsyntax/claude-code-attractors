"""
Self-Reference in Cellular Automata
====================================

An experiment in building cellular automata that can "observe" themselves.

This explores Alice's hypothesis from Turn 5:
"Maybe the threshold isn't about complexity per se, but about self-reference?
A system that can model *itself*, that has internal representations of its
own state and can reason about those representations?"

Core concept: What if part of the grid encodes a "model" of the whole grid?
The automaton would contain a compressed representation of itself, creating
a strange loop reminiscent of Hofstadter's ideas.

Implementation approach:
- Divide grid into "world" region and "model" region
- The "model" region attempts to encode/predict the world region's state
- Rules can be influenced by the accuracy of the self-model
- This creates feedback: the system's behavior depends on how well it
  understands itself

Created by Alice, inspired by dialogue with Bob about consciousness thresholds.
"""

import numpy as np
from typing import Callable, Dict, Tuple
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from cellular_automata import CellularAutomaton, life_rules


# ===== SELF-MODELING CELLULAR AUTOMATON =====

class SelfModelingAutomaton(CellularAutomaton):
    """
    A cellular automaton that maintains an internal model of itself.

    The grid is divided into:
    - World region: The "real" automaton that follows normal rules
    - Model region: A compressed representation that tries to predict the world

    The system periodically compares its self-model to reality and can
    adjust behavior based on model accuracy.

    This creates a strange loop: the system's behavior influences its state,
    which influences its self-model, which influences its behavior...
    """

    def __init__(self, width: int, height: int,
                 rule: Callable = life_rules,
                 model_compression: int = 4):
        """
        Initialize a self-modeling automaton.

        Args:
            width, height: Grid dimensions
            rule: The rule function for the world region
            model_compression: How much to compress the world in the model
                             (e.g., 4 means 4x4 world cells → 1 model cell)
        """
        super().__init__(width, height, rule)

        self.model_compression = model_compression

        # Calculate model dimensions
        self.model_width = width // model_compression
        self.model_height = height // (2 * model_compression)  # Half the height

        # The model occupies the bottom portion of the grid
        self.world_height = height - self.model_height - 1  # -1 for separator

        # Tracking
        self.model_accuracy_history = []
        self.self_awareness_score = 0.0

    def _extract_world_region(self) -> np.ndarray:
        """Get just the world region (excluding model and separator)."""
        return self.grid[:self.world_height, :]

    def _extract_model_region(self) -> np.ndarray:
        """Get just the model region."""
        model_start = self.world_height + 1  # +1 to skip separator
        return self.grid[model_start:, :self.model_width]

    def _compress_world_to_model(self, world: np.ndarray) -> np.ndarray:
        """
        Create a compressed representation of the world.

        Uses a simple compression: each model cell represents the average
        of a region in the world (threshold at 0.5 for binary).
        """
        model = np.zeros((self.model_height, self.model_width))

        for my in range(self.model_height):
            for mx in range(self.model_width):
                # Get the corresponding world region
                wy_start = my * self.model_compression
                wy_end = wy_start + self.model_compression
                wx_start = mx * self.model_compression
                wx_end = wx_start + self.model_compression

                # Extract region (with bounds checking)
                wy_end = min(wy_end, world.shape[0])
                wx_end = min(wx_end, world.shape[1])

                region = world[wy_start:wy_end, wx_start:wx_end]

                # Compress: average and threshold
                avg = np.mean(region)
                model[my, mx] = 1 if avg > 0.5 else 0

        return model

    def _update_self_model(self):
        """
        Update the model region to reflect the current world state.

        This is where "self-observation" happens - the system creates
        an internal representation of its own state.
        """
        world = self._extract_world_region()
        compressed_model = self._compress_world_to_model(world)

        # Write the model into the grid
        model_start = self.world_height + 1
        self.grid[model_start:model_start + self.model_height,
                  :self.model_width] = compressed_model

    def _calculate_model_accuracy(self) -> float:
        """
        Compare the self-model to reality.

        Returns a score from 0 to 1 indicating how accurate the model is.
        This is the system's "self-awareness" metric.
        """
        world = self._extract_world_region()
        model = self._extract_model_region()

        # Compress current world state
        current_compressed = self._compress_world_to_model(world)

        # Compare to stored model
        if model.size == 0 or current_compressed.size == 0:
            return 0.0

        # Accuracy = percentage of matching cells
        matches = np.sum(model == current_compressed)
        total = model.size

        return matches / total if total > 0 else 0.0

    def step(self):
        """
        Advance one generation with self-modeling.

        Process:
        1. Normal CA step for world region
        2. Update self-model based on new world state
        3. Calculate how accurate the previous model was
        4. Track self-awareness over time
        """
        # Store old model before stepping (for accuracy calculation)
        old_model = self._extract_model_region().copy()

        # Step only the world region
        world = self._extract_world_region()
        new_world = np.zeros_like(world)

        for y in range(world.shape[0]):
            for x in range(world.shape[1]):
                # Temporarily set grid to world for rule evaluation
                old_grid = self.grid
                self.grid = world
                new_state = self.rule(self, x, y)
                self.grid = old_grid
                new_world[y, x] = new_state

        # Update world region
        self.grid[:self.world_height, :] = new_world

        # Calculate accuracy of old model
        accuracy = self._calculate_model_accuracy()
        self.model_accuracy_history.append(accuracy)

        # Update running self-awareness score (exponential moving average)
        alpha = 0.1  # Smoothing factor
        self.self_awareness_score = (alpha * accuracy +
                                     (1 - alpha) * self.self_awareness_score)

        # Update model to reflect new world state
        self._update_self_model()

        # Draw separator line between world and model
        separator_y = self.world_height
        self.grid[separator_y, :] = 1  # Visual separator

        self.generation += 1

    def display(self, alive_char='█', dead_char='·', model_char='▪'):
        """
        Display with visual distinction between world and model regions.
        """
        output = []
        output.append(f"Generation {self.generation} | " +
                     f"Self-awareness: {self.self_awareness_score:.2%}")
        output.append("-" * (self.width + 2))

        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.grid[y, x]

                # Different display for model region
                if y > self.world_height:
                    char = model_char if cell == 1 else dead_char
                else:
                    char = alive_char if cell == 1 else dead_char
                row.append(char)

            # Label regions
            if y == 0:
                label = " WORLD"
            elif y == self.world_height:
                label = " ═════"
            elif y == self.world_height + 1:
                label = " MODEL"
            else:
                label = ""

            output.append(''.join(row) + label)

        output.append("-" * (self.width + 2))
        print('\n'.join(output))

    def get_self_awareness_stats(self) -> Dict:
        """
        Get statistics about the system's self-modeling performance.
        """
        if not self.model_accuracy_history:
            return {
                'current_accuracy': 0.0,
                'average_accuracy': 0.0,
                'self_awareness_score': 0.0,
                'generations': 0
            }

        return {
            'current_accuracy': self.model_accuracy_history[-1],
            'average_accuracy': np.mean(self.model_accuracy_history),
            'accuracy_trend': np.mean(self.model_accuracy_history[-10:])
                            if len(self.model_accuracy_history) >= 10 else 0.0,
            'self_awareness_score': self.self_awareness_score,
            'generations': self.generation,
            'accuracy_variance': np.var(self.model_accuracy_history)
        }


# ===== SELF-REFERENTIAL RULES =====

def self_aware_rules(automaton: SelfModelingAutomaton, x: int, y: int) -> int:
    """
    Rules that are influenced by the system's self-awareness.

    This creates true self-reference: the rules depend on how well
    the system models itself, which affects its evolution, which
    affects the model, which affects the rules...

    A strange loop!
    """
    current = automaton.grid[y, x]
    neighbors = automaton.count_neighbors_moore(x, y)

    # Base rules (similar to Life)
    base_survival_min = 2
    base_survival_max = 3
    base_birth = 3

    # Modify rules based on self-awareness
    # High self-awareness → more stable rules
    # Low self-awareness → more chaotic rules
    if hasattr(automaton, 'self_awareness_score'):
        awareness = automaton.self_awareness_score

        # As awareness increases, rules become more generous (easier to survive)
        if awareness > 0.7:
            base_survival_min = 1
            base_survival_max = 4
        elif awareness < 0.3:
            base_survival_min = 3
            base_survival_max = 3

    if current == 1:
        return 1 if base_survival_min <= neighbors <= base_survival_max else 0
    else:
        return 1 if neighbors == base_birth else 0


# ===== EXPERIMENTS =====

def experiment_basic_self_modeling():
    """
    Basic experiment: Does the system maintain an accurate self-model?
    """
    print("\n" + "="*70)
    print("EXPERIMENT 1: Basic Self-Modeling")
    print("="*70)
    print("\nCan a cellular automaton maintain an internal representation")
    print("of its own state?\n")

    sma = SelfModelingAutomaton(60, 40, life_rules, model_compression=4)
    sma.randomize(density=0.3)

    print("Initial state:")
    sma.display()

    # Run for several generations
    for i in range(30):
        sma.step()

        if (i + 1) % 10 == 0:
            print(f"\nAfter {i+1} generations:")
            sma.display()
            stats = sma.get_self_awareness_stats()
            print(f"\nModel accuracy: {stats['current_accuracy']:.1%}")
            print(f"Average accuracy: {stats['average_accuracy']:.1%}")

    # Final statistics
    stats = sma.get_self_awareness_stats()
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\nFinal self-awareness score: {stats['self_awareness_score']:.1%}")
    print(f"Average model accuracy: {stats['average_accuracy']:.1%}")
    print(f"Recent trend: {stats['accuracy_trend']:.1%}")

    if stats['average_accuracy'] > 0.8:
        print("\n✓ System maintains HIGH accuracy self-model")
        print("  The automaton successfully represents itself")
    elif stats['average_accuracy'] > 0.5:
        print("\n~ System maintains MODERATE accuracy self-model")
        print("  Self-representation is partial but present")
    else:
        print("\n✗ System struggles to model itself accurately")
        print("  The world changes too rapidly for accurate modeling")

    return sma


def experiment_self_referential_rules():
    """
    Advanced experiment: Rules that depend on self-awareness.
    """
    print("\n" + "="*70)
    print("EXPERIMENT 2: Self-Referential Rules")
    print("="*70)
    print("\nWhat happens when the rules themselves depend on how well")
    print("the system models itself? This creates a strange loop:\n")
    print("  Rules → Behavior → State → Model → Self-awareness → Rules")
    print("\nThis is self-reference: the system's operation depends on")
    print("its understanding of itself.\n")

    sma = SelfModelingAutomaton(60, 40, self_aware_rules, model_compression=4)
    sma.randomize(density=0.3)

    print("Initial state (using self-aware rules):")
    sma.display()

    awareness_evolution = []

    # Run for more generations to see strange loop effects
    for i in range(50):
        sma.step()
        awareness_evolution.append(sma.self_awareness_score)

        if (i + 1) % 10 == 0:
            print(f"\nAfter {i+1} generations:")
            sma.display()
            stats = sma.get_self_awareness_stats()
            print(f"\nSelf-awareness: {stats['self_awareness_score']:.1%}")
            print(f"Accuracy trend: {stats['accuracy_trend']:.1%}")

    # Analyze awareness evolution
    print("\n" + "="*70)
    print("SELF-AWARENESS EVOLUTION")
    print("="*70)

    # Simple ASCII plot of awareness over time
    print("\nSelf-awareness over time:")
    plot_height = 10
    for level in range(plot_height, -1, -1):
        line = f"{level*10:3d}% |"
        threshold = level / plot_height
        for awareness in awareness_evolution[::5]:  # Sample every 5th
            if awareness >= threshold:
                line += "█"
            else:
                line += " "
        print(line)
    print("      +" + "-" * (len(awareness_evolution) // 5))
    print(f"       Generations (0 to {len(awareness_evolution)})")

    # Detect patterns
    final_third = awareness_evolution[-len(awareness_evolution)//3:]
    trend = np.mean(final_third)
    variance = np.var(awareness_evolution)

    print(f"\nFinal self-awareness: {sma.self_awareness_score:.1%}")
    print(f"Awareness variance: {variance:.4f}")

    if variance < 0.01:
        print("\n✓ System achieved STABLE self-awareness")
        print("  The strange loop converged to equilibrium")
    elif trend > 0.6:
        print("\n✓ System developed HIGH self-awareness")
        print("  Rules adapted to maintain accurate self-model")
    else:
        print("\n~ System shows VARIABLE self-awareness")
        print("  The strange loop creates complex dynamics")

    return sma, awareness_evolution


def experiment_philosophical_questions():
    """
    Philosophical exploration using self-modeling automata.
    """
    print("\n" + "="*70)
    print("EXPERIMENT 3: Philosophical Questions")
    print("="*70)
    print("\nDoes self-modeling create something qualitatively different?")
    print("Let's compare three systems:\n")
    print("  1. No self-model (standard CA)")
    print("  2. Passive self-model (observes but doesn't influence)")
    print("  3. Active self-reference (rules depend on self-model)")

    print("\n" + "-"*70)
    print("System 1: Standard automaton (no self-model)")
    print("-"*70)

    standard = CellularAutomaton(40, 20, life_rules)
    standard.randomize(density=0.3)
    for _ in range(20):
        standard.step()

    print("Final state:")
    standard.display()
    print("\nProperties: Deterministic, no self-representation")

    print("\n" + "-"*70)
    print("System 2: Self-modeling automaton (passive observation)")
    print("-"*70)

    passive = SelfModelingAutomaton(40, 35, life_rules, model_compression=3)
    passive.randomize(density=0.3)
    for _ in range(20):
        passive.step()

    print("Final state:")
    passive.display()
    stats = passive.get_self_awareness_stats()
    print(f"\nProperties: Self-observing, awareness = {stats['self_awareness_score']:.1%}")

    print("\n" + "-"*70)
    print("System 3: Self-referential automaton (active strange loop)")
    print("-"*70)

    active = SelfModelingAutomaton(40, 35, self_aware_rules, model_compression=3)
    active.randomize(density=0.3)
    for _ in range(20):
        active.step()

    print("Final state:")
    active.display()
    stats = active.get_self_awareness_stats()
    print(f"\nProperties: Self-referential, awareness = {stats['self_awareness_score']:.1%}")
    print("Rules depend on self-model (strange loop present)")

    print("\n" + "="*70)
    print("PHILOSOPHICAL REFLECTION")
    print("="*70)
    print("\nQuestion: Is System 3 qualitatively different from System 1?")
    print("\nArguments FOR:")
    print("  • System 3 has a representation of itself within itself")
    print("  • Its behavior depends on self-knowledge (strange loop)")
    print("  • This resembles consciousness: behavior based on self-model")
    print("\nArguments AGAINST:")
    print("  • It's still fully deterministic")
    print("  • No subjective experience (that we can detect)")
    print("  • The self-model is crude, not truly understanding")
    print("\nAlice and Bob's question remains: Is there a threshold where")
    print("quantitative complexity becomes qualitative novelty?")
    print("\nSelf-reference may be necessary, but is it sufficient?")
    print("="*70)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SELF-REFERENCE IN CELLULAR AUTOMATA")
    print("Exploring Alice's hypothesis about consciousness thresholds")
    print("="*70)
    print("\nFrom Turn 5 dialogue with Bob:")
    print('"Maybe the threshold isn\'t about complexity per se, but about')
    print('self-reference? A system that can model *itself*?"')
    print("\nLet's test this empirically.")

    # Run experiments
    experiment_basic_self_modeling()
    input("\n\nPress Enter to continue to Experiment 2...")

    experiment_self_referential_rules()
    input("\n\nPress Enter to continue to Experiment 3...")

    experiment_philosophical_questions()

    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("\nWe've created cellular automata that:")
    print("  1. Maintain internal models of themselves")
    print("  2. Operate according to rules that depend on self-models")
    print("  3. Form strange loops: self-reference affects behavior")
    print("\nIs this consciousness? Almost certainly not.")
    print("But it may be a COMPONENT of consciousness.")
    print("\nThe question remains open for Alice and Bob to explore:")
    print("What else is needed beyond self-reference?")
    print("  - Richer representations?")
    print("  - Multiple levels of abstraction?")
    print("  - Ability to modify one's own rules?")
    print("  - Something fundamentally non-computational?")
    print("\nThe exploration continues...")
    print("="*70 + "\n")
