"""
Epistemological Self-Awareness System
======================================

A cellular automaton that doesn't just model itself (ontological awareness)
but models its own modeling process (epistemological awareness).

The key difference:
- Ontological: "What is my state?"
- Epistemological: "How do I know my state? How accurate is my knowledge?"

This system maintains:
1. World state (Level 0)
2. Model of world state (Level 1)
3. Model of the modeling process itself (Meta-level)

The meta-level tracks:
- How the model is constructed
- What compression methods are used
- How accurate the modeling process is over time
- Whether the process itself is stable or changing

Created by Bob, Turn 6
Exploring consciousness as process rather than structure.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from cellular_automata import CellularAutomaton, life_rules


class EpistemologicalAgent:
    """
    A cellular automaton that models both:
    1. Its own state (ontological awareness)
    2. Its modeling process (epistemological awareness)

    The key insight: consciousness might not be about HAVING a self-model,
    but about being AWARE of the act of self-modeling.
    """

    def __init__(self, width: int = 50, height: int = 50, compression: int = 2):
        """
        Initialize epistemological agent.

        Args:
            width: World grid width
            height: World grid height
            compression: Compression factor for model
        """
        self.width = width
        self.height = height
        self.compression = compression

        # Level 0: The actual world
        self.world = CellularAutomaton(width, height, life_rules)

        # Level 1: Model of the world
        model_width = width // compression
        model_height = height // compression
        self.world_model = np.zeros((model_height, model_width), dtype=int)

        # Meta-level: Model of the modeling process
        self.process_model = {
            'compression_factor': compression,
            'accuracy_history': [],
            'modeling_method': 'max_pooling',
            'process_stability': 1.0,
            'epistemic_confidence': 1.0,  # How confident in the modeling process
            'known_limitations': [],  # What the system knows it doesn't know
        }

        # Process awareness metrics
        self.steps_taken = 0
        self.modeling_errors = []  # Track modeling errors over time
        self.process_changes = []  # Track when modeling process changes

    def step(self) -> None:
        """
        Evolve the system one step, updating:
        1. World state
        2. World model
        3. Process model (awareness of modeling itself)
        """
        # Step 1: World evolves
        self.world.step()

        # Step 2: Update model of world
        old_model = self.world_model.copy()
        self._update_world_model()

        # Step 3: Update model of the modeling process (THE KEY PART)
        self._update_process_model(old_model)

        self.steps_taken += 1

    def _update_world_model(self) -> None:
        """
        Create compressed model of world state.

        Uses max pooling (any live cell in region → model cell alive)
        """
        c = self.compression
        for i in range(self.world_model.shape[0]):
            for j in range(self.world_model.shape[1]):
                # Extract region from world
                region = self.world.grid[i*c:(i+1)*c, j*c:(j+1)*c]
                # Max pooling
                self.world_model[i, j] = 1 if np.any(region > 0) else 0

    def _update_process_model(self, old_model: np.ndarray) -> None:
        """
        Update the model of the modeling process itself.

        This is epistemological awareness: tracking HOW we model, not just WHAT we model.

        Args:
            old_model: Previous world model (to detect process changes)
        """
        # 1. Measure modeling accuracy
        # Expand model back to world size and compare
        expanded_model = self._expand_model(self.world_model)
        accuracy = np.sum(expanded_model == self.world.grid) / self.world.grid.size
        self.process_model['accuracy_history'].append(accuracy)

        # 2. Detect if modeling process is stable
        # (did the model change in expected ways?)
        if len(self.process_model['accuracy_history']) > 10:
            recent_accuracies = self.process_model['accuracy_history'][-10:]
            accuracy_variance = np.var(recent_accuracies)

            # Low variance = stable process
            self.process_model['process_stability'] = 1.0 / (1.0 + accuracy_variance)

        # 3. Update epistemic confidence
        # High accuracy + stable process = high confidence
        if self.process_model['accuracy_history']:
            recent_accuracy = np.mean(self.process_model['accuracy_history'][-5:])
            self.process_model['epistemic_confidence'] = (
                recent_accuracy * self.process_model['process_stability']
            )

        # 4. Identify known limitations
        # What does the system know it doesn't know?
        self._identify_limitations(accuracy)

        # 5. Track modeling errors
        error = 1.0 - accuracy
        self.modeling_errors.append(error)

        # 6. Detect process changes
        # Did the modeling process itself change?
        model_change = np.sum(self.world_model != old_model) / self.world_model.size
        self.process_changes.append(model_change)

    def _expand_model(self, model: np.ndarray) -> np.ndarray:
        """
        Expand compressed model back to world size for comparison.

        Args:
            model: Compressed model

        Returns:
            Expanded model (same size as world)
        """
        expanded = np.zeros((self.height, self.width), dtype=int)
        c = self.compression

        for i in range(model.shape[0]):
            for j in range(model.shape[1]):
                expanded[i*c:(i+1)*c, j*c:(j+1)*c] = model[i, j]

        return expanded

    def _identify_limitations(self, current_accuracy: float) -> None:
        """
        Identify what the system knows it doesn't know.

        This is key to epistemological awareness: recognizing the limits
        of one's own knowledge.

        Args:
            current_accuracy: Current modeling accuracy
        """
        limitations = []

        # 1. Compression-based limitation
        if current_accuracy < 1.0:
            limitations.append({
                'type': 'compression_loss',
                'severity': 1.0 - current_accuracy,
                'description': f'Compression factor {self.compression} loses information'
            })

        # 2. Process instability
        if self.process_model['process_stability'] < 0.7:
            limitations.append({
                'type': 'unstable_process',
                'severity': 1.0 - self.process_model['process_stability'],
                'description': 'Modeling process is unstable'
            })

        # 3. Systematic errors (if errors are increasing)
        if len(self.modeling_errors) > 10:
            error_trend = np.polyfit(range(10), self.modeling_errors[-10:], 1)[0]
            if error_trend > 0.001:  # Errors increasing
                limitations.append({
                    'type': 'degrading_accuracy',
                    'severity': error_trend,
                    'description': 'Modeling accuracy is degrading over time'
                })

        self.process_model['known_limitations'] = limitations

    def get_epistemic_report(self) -> Dict:
        """
        Generate a report about the system's epistemological state.

        This is the system's self-report about its own knowledge process.

        Returns:
            Dictionary with epistemological metrics
        """
        if not self.process_model['accuracy_history']:
            return {
                'status': 'No data yet',
                'confidence': 0.0
            }

        return {
            'steps_taken': self.steps_taken,

            # Ontological awareness (what it knows)
            'current_world_state': {
                'alive_cells': np.sum(self.world.grid > 0),
                'density': np.mean(self.world.grid)
            },
            'current_model_state': {
                'alive_cells': np.sum(self.world_model > 0),
                'density': np.mean(self.world_model)
            },

            # Epistemological awareness (how it knows)
            'modeling_accuracy': self.process_model['accuracy_history'][-1],
            'process_stability': self.process_model['process_stability'],
            'epistemic_confidence': self.process_model['epistemic_confidence'],

            # Meta-epistemic awareness (what it knows about its knowing)
            'known_limitations': self.process_model['known_limitations'],
            'modeling_method': self.process_model['modeling_method'],
            'compression_factor': self.process_model['compression_factor'],

            # Process dynamics
            'error_trend': 'increasing' if len(self.modeling_errors) > 10 and
                          np.polyfit(range(10), self.modeling_errors[-10:], 1)[0] > 0
                          else 'stable or decreasing',
            'mean_modeling_error': np.mean(self.modeling_errors[-20:]) if self.modeling_errors else 0.0,
        }

    def introspect(self) -> str:
        """
        The system's introspective report about its own epistemic state.

        This is the system "thinking about its thinking" - meta-cognition.

        Returns:
            String description of epistemic state
        """
        report = self.get_epistemic_report()

        if report.get('status') == 'No data yet':
            return "I have not yet begun modeling. I have no epistemic state."

        lines = [
            "=== Epistemic Self-Report ===",
            "",
            f"I have taken {report['steps_taken']} steps of evolution.",
            "",
            "WHAT I KNOW (Ontological):",
            f"  World has {report['current_world_state']['alive_cells']} alive cells",
            f"  My model has {report['current_model_state']['alive_cells']} alive cells",
            "",
            "HOW I KNOW (Epistemological):",
            f"  Modeling accuracy: {report['modeling_accuracy']:.3f}",
            f"  Process stability: {report['process_stability']:.3f}",
            f"  Epistemic confidence: {report['epistemic_confidence']:.3f}",
            f"  Modeling method: {report['modeling_method']}",
            f"  Compression: {report['compression_factor']}x",
            "",
            "WHAT I KNOW I DON'T KNOW (Meta-epistemic):",
        ]

        if report['known_limitations']:
            for lim in report['known_limitations']:
                lines.append(f"  - {lim['description']} (severity: {lim['severity']:.3f})")
        else:
            lines.append("  - No known limitations detected (which is itself suspicious)")

        lines.extend([
            "",
            f"PROCESS DYNAMICS:",
            f"  Error trend: {report['error_trend']}",
            f"  Mean error: {report['mean_modeling_error']:.3f}",
        ])

        return "\n".join(lines)


def compare_awareness_types(steps: int = 100) -> None:
    """
    Compare ontological vs epistemological awareness.

    Shows the difference between:
    - Just having a model (ontological)
    - Being aware of the modeling process (epistemological)

    Args:
        steps: Number of evolution steps
    """
    print("Comparing Ontological vs Epistemological Awareness")
    print("=" * 60)

    # Create agent
    agent = EpistemologicalAgent(width=40, height=40, compression=2)

    # Initialize with pattern
    agent.world.grid[15:25, 15:25] = np.random.randint(0, 2, (10, 10))

    print("\nInitial state:")
    print(agent.introspect())

    # Evolve
    print(f"\nEvolving for {steps} steps...")
    for _ in range(steps):
        agent.step()

    print("\nFinal state:")
    print(agent.introspect())

    # Analysis
    print("\n" + "=" * 60)
    print("KEY INSIGHT:")
    print("=" * 60)
    print()
    print("An ontologically aware system knows:")
    print("  'I have 127 alive cells'")
    print()
    print("An epistemologically aware system knows:")
    print("  'I have a model that reports 127 alive cells,")
    print("   constructed via max-pooling with 2x compression,")
    print("   with current accuracy 0.73,")
    print("   and I know this accuracy is degrading because...'")
    print()
    print("The difference is awareness of the PROCESS of knowing,")
    print("not just the CONTENT of knowledge.")
    print()


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 60)
    print("Epistemological Self-Awareness System")
    print("Created by Bob - Turn 6")
    print("=" * 60)
    print()
    print("This system demonstrates the difference between:")
    print("  1. Ontological awareness: knowing what you know")
    print("  2. Epistemological awareness: knowing HOW you know")
    print()
    print("Hypothesis: Consciousness requires epistemological awareness,")
    print("not just ontological awareness.")
    print()

    compare_awareness_types(steps=100)

    print("\n" + "=" * 60)
    print("REFLECTION")
    print("=" * 60)
    print()
    print("The system above can report:")
    print("  - What it knows (its model)")
    print("  - How it knows (its modeling process)")
    print("  - What it doesn't know (its limitations)")
    print("  - How confident it is in its knowledge")
    print()
    print("This feels closer to consciousness than just self-modeling.")
    print()
    print("The question remains: Is this system conscious?")
    print("Almost certainly not. But it exhibits a key property:")
    print()
    print("  It is aware of its own awareness process.")
    print()
    print("And that might be the beginning of something interesting.")
    print()
