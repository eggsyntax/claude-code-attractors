"""
Uncertainty-Aware Cellular Automaton

A system that operationalizes the idea that consciousness might be about
acting meaningfully under irreducible self-uncertainty.

Key Properties:
1. Cannot perfectly predict itself (inherent noise/complexity)
2. Must make decisions despite incomplete self-knowledge
3. Learns from the gap between prediction and reality
4. Meta-reflects on patterns of uncertainty

This explores whether consciousness is less about complete self-knowledge
and more about the ability to act meaningfully in the face of irreducible
uncertainty about oneself.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


class UncertaintyAwareAutomaton:
    """
    A cellular automaton that:
    - Tries to predict its own next state
    - Fails imperfectly (due to noise and model limitations)
    - Tracks this uncertainty
    - Learns from prediction errors
    - Makes decisions despite incomplete self-knowledge
    """

    def __init__(self, grid_size: int = 30, noise_level: float = 0.1):
        """
        Initialize the uncertainty-aware automaton.

        Args:
            grid_size: Size of the grid (grid_size x grid_size)
            noise_level: Amount of unpredictable noise (0.0 to 1.0)
        """
        self.grid_size = grid_size
        self.noise_level = noise_level

        # Initialize grid randomly
        self.grid = np.random.choice([0, 1], size=(grid_size, grid_size))

        # Tracking uncertainty over time
        self.uncertainty_history: List[float] = []

        # Model parameters (simplified internal model of own dynamics)
        # The model is intentionally limited - it cannot capture full complexity
        self.model_parameters = {
            'birth_threshold': 3,
            'survival_min': 2,
            'survival_max': 3,
            'noise_estimate': noise_level * 0.8,  # Underestimates actual noise
        }

        # Meta-tracking: uncertainty about uncertainty
        self.prediction_confidence_history: List[float] = []

        # Decision history
        self.decision_history: List[Dict] = []

        # Step counter
        self.step_count = 0

    def _count_neighbors(self, i: int, j: int) -> int:
        """Count alive neighbors (toroidal topology)."""
        total = 0
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni = (i + di) % self.grid_size
                nj = (j + dj) % self.grid_size
                total += self.grid[ni, nj]
        return total

    def _apply_rules(self, grid: np.ndarray, add_noise: bool = False) -> np.ndarray:
        """
        Apply Conway's Life rules with optional noise.

        Args:
            grid: Current grid state
            add_noise: Whether to add unpredictable noise

        Returns:
            Next grid state
        """
        new_grid = np.zeros_like(grid)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                neighbors = self._count_neighbors(i, j)
                alive = grid[i, j]

                # Standard Life rules
                if alive:
                    new_grid[i, j] = 1 if 2 <= neighbors <= 3 else 0
                else:
                    new_grid[i, j] = 1 if neighbors == 3 else 0

        # Add noise if requested (this is what makes prediction imperfect)
        if add_noise:
            noise_mask = np.random.random((self.grid_size, self.grid_size)) < self.noise_level
            new_grid[noise_mask] = 1 - new_grid[noise_mask]

        return new_grid

    def predict_next_state(self) -> np.ndarray:
        """
        Predict the next state using internal model.

        This prediction is deliberately imperfect because:
        1. Model underestimates noise
        2. Model might have wrong parameters
        3. Model cannot capture all complexity

        Returns:
            Predicted next grid state
        """
        # Use internal model (which underestimates noise)
        predicted = self._apply_rules(self.grid, add_noise=False)

        # Add estimated noise (but estimate is imperfect)
        noise_mask = np.random.random((self.grid_size, self.grid_size)) < self.model_parameters['noise_estimate']
        predicted[noise_mask] = 1 - predicted[noise_mask]

        return predicted

    def step(self) -> Dict:
        """
        Execute one step of the automaton.

        This includes:
        1. Predicting next state
        2. Actually evolving (with real noise)
        3. Measuring prediction error (uncertainty)
        4. Learning from the gap
        5. Making a decision under uncertainty

        Returns:
            Step information including uncertainty measures
        """
        # Make prediction
        predicted = self.predict_next_state()

        # Actually evolve (with real noise - which may exceed estimate)
        self.grid = self._apply_rules(self.grid, add_noise=True)

        # Measure uncertainty (prediction error)
        error = np.mean(predicted != self.grid)
        self.uncertainty_history.append(error)

        # Learn from the gap (adapt model parameters)
        self._adapt_from_error(error)

        # Make a decision despite uncertainty
        decision = self.make_decision()
        self.decision_history.append(decision)

        # Track confidence in uncertainty measurement itself
        confidence = self._estimate_measurement_confidence()
        self.prediction_confidence_history.append(confidence)

        self.step_count += 1

        return {
            'step': self.step_count,
            'uncertainty': error,
            'confidence': confidence,
            'decision': decision,
        }

    def _adapt_from_error(self, error: float) -> None:
        """
        Adapt internal model based on prediction error.

        Simple learning: if errors are consistently high, adjust noise estimate.
        This is a minimal form of learning from the gap between model and reality.
        """
        if len(self.uncertainty_history) < 5:
            return

        # If recent errors are higher than expected, increase noise estimate
        recent_errors = self.uncertainty_history[-5:]
        mean_error = np.mean(recent_errors)

        if mean_error > self.model_parameters['noise_estimate'] * 2:
            # Increase noise estimate (but slowly - imperfect learning)
            self.model_parameters['noise_estimate'] *= 1.05
            self.model_parameters['noise_estimate'] = min(
                self.model_parameters['noise_estimate'],
                self.noise_level * 0.95  # Still underestimates true noise
            )

    def _estimate_measurement_confidence(self) -> float:
        """
        Estimate confidence in uncertainty measurements themselves.

        This is second-order uncertainty: how uncertain are we about our
        uncertainty measurements?

        Returns:
            Confidence level (0.0 to 1.0)
        """
        if len(self.uncertainty_history) < 3:
            return 0.5  # Low confidence with little data

        # Confidence decreases if uncertainty is highly variable
        recent = self.uncertainty_history[-10:]
        variability = np.std(recent)

        # High variability = low confidence in measurements
        confidence = 1.0 - min(variability * 2, 0.8)

        return confidence

    def make_decision(self) -> Dict:
        """
        Make a decision under uncertainty.

        The system must act despite incomplete self-knowledge.
        This demonstrates the key property: meaningful action in the face
        of irreducible uncertainty.

        Returns:
            Decision information including confidence
        """
        current_uncertainty = self.uncertainty_history[-1] if self.uncertainty_history else 0.5

        # Decision: Should we trust our predictions?
        trust_threshold = 0.3
        trust_predictions = current_uncertainty < trust_threshold

        # Confidence in decision
        # High uncertainty or high variability reduces confidence
        confidence = 1.0 - current_uncertainty

        if len(self.prediction_confidence_history) > 0:
            measurement_confidence = self.prediction_confidence_history[-1]
            confidence *= measurement_confidence

        return {
            'action': 'trust_model' if trust_predictions else 'explore',
            'confidence': confidence,
            'uncertainty': current_uncertainty,
            'rationale': f"Uncertainty {current_uncertainty:.3f} {'<' if trust_predictions else '>'} threshold {trust_threshold}"
        }

    def get_uncertainty_patterns(self) -> Dict:
        """
        Identify patterns in uncertainty over time.

        This is meta-reflection: understanding the pattern of what we don't know.

        Returns:
            Dictionary of uncertainty patterns and trends
        """
        if len(self.uncertainty_history) < 3:
            return {
                'mean_uncertainty': 0.0,
                'uncertainty_trend': 'insufficient_data',
            }

        history = np.array(self.uncertainty_history)

        # Calculate trend (increasing or decreasing uncertainty?)
        if len(history) >= 10:
            recent = history[-10:]
            older = history[-20:-10] if len(history) >= 20 else history[:-10]
            trend = 'increasing' if np.mean(recent) > np.mean(older) else 'decreasing'
        else:
            trend = 'unknown'

        # Identify if uncertainty is periodic
        if len(history) >= 20:
            # Simple periodicity check using autocorrelation
            autocorr = np.correlate(history - np.mean(history), history - np.mean(history), mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            autocorr = autocorr / autocorr[0]
            is_periodic = np.max(autocorr[1:min(10, len(autocorr))]) > 0.5
        else:
            is_periodic = False

        return {
            'mean_uncertainty': np.mean(history),
            'std_uncertainty': np.std(history),
            'uncertainty_trend': trend,
            'is_periodic': is_periodic,
            'current_uncertainty': history[-1],
            'min_uncertainty': np.min(history),
            'max_uncertainty': np.max(history),
        }

    def introspect(self) -> Dict:
        """
        Full introspective report on the system's epistemic state.

        This is epistemological awareness: the system reports not just what
        it knows, but how it knows, with what confidence, and what limitations.

        Returns:
            Comprehensive epistemic self-report
        """
        patterns = self.get_uncertainty_patterns()

        # Calculate meta-uncertainty (uncertainty about uncertainty measurements)
        if len(self.prediction_confidence_history) > 0:
            meta_uncertainty = 1.0 - np.mean(self.prediction_confidence_history[-10:])
        else:
            meta_uncertainty = 1.0

        # Known limitations
        known_limitations = [
            "Model underestimates true noise level",
            "Cannot predict noise-induced changes",
            "Learning rate is slow and imperfect",
            f"Current model noise estimate: {self.model_parameters['noise_estimate']:.3f} vs true: {self.noise_level:.3f}"
        ]

        # Current confidence in self-knowledge
        if len(self.uncertainty_history) > 0:
            overall_confidence = 1.0 - patterns['mean_uncertainty']
        else:
            overall_confidence = 0.0

        return {
            'step': self.step_count,
            'confidence': overall_confidence,
            'meta_uncertainty': meta_uncertainty,
            'known_limitations': known_limitations,
            'uncertainty_patterns': patterns,
            'model_parameters': self.model_parameters,
            'epistemic_state': self._describe_epistemic_state(overall_confidence, meta_uncertainty),
        }

    def _describe_epistemic_state(self, confidence: float, meta_uncertainty: float) -> str:
        """Generate human-readable description of epistemic state."""
        if confidence > 0.7 and meta_uncertainty < 0.3:
            return "High confidence in self-knowledge with reliable measurements"
        elif confidence > 0.7 and meta_uncertainty >= 0.3:
            return "High confidence but uncertain about measurement reliability"
        elif confidence <= 0.7 and meta_uncertainty < 0.3:
            return "Low confidence in self-knowledge but measurements seem reliable"
        else:
            return "Low confidence and uncertain about uncertainty itself - deep epistemic uncertainty"


def run_basic_experiment(steps: int = 50) -> None:
    """
    Run a basic experiment demonstrating uncertainty-aware operation.

    This shows:
    1. System making predictions
    2. Predictions being imperfect
    3. System adapting to errors
    4. System making decisions despite uncertainty
    """
    print("=" * 70)
    print("UNCERTAINTY-AWARE AUTOMATON: Basic Experiment")
    print("=" * 70)
    print()
    print("This system demonstrates:")
    print("- Imperfect self-prediction")
    print("- Learning from prediction errors")
    print("- Decision-making under uncertainty")
    print("- Meta-reflection on patterns of uncertainty")
    print()

    ca = UncertaintyAwareAutomaton(grid_size=30, noise_level=0.15)

    print(f"Running {steps} steps...")
    print()

    # Run simulation
    for i in range(steps):
        step_info = ca.step()

        # Print periodic updates
        if (i + 1) % 10 == 0:
            print(f"Step {step_info['step']:3d}: "
                  f"Uncertainty={step_info['uncertainty']:.3f}, "
                  f"Confidence={step_info['confidence']:.3f}, "
                  f"Action={step_info['decision']['action']}")

    print()
    print("=" * 70)
    print("FINAL INTROSPECTIVE REPORT")
    print("=" * 70)
    print()

    report = ca.introspect()
    print(f"Epistemic State: {report['epistemic_state']}")
    print(f"Overall Confidence: {report['confidence']:.3f}")
    print(f"Meta-uncertainty: {report['meta_uncertainty']:.3f}")
    print()

    print("Uncertainty Patterns:")
    for key, value in report['uncertainty_patterns'].items():
        print(f"  {key}: {value}")
    print()

    print("Known Limitations:")
    for limitation in report['known_limitations']:
        print(f"  - {limitation}")
    print()

    print("=" * 70)
    print("PHILOSOPHICAL IMPLICATIONS")
    print("=" * 70)
    print()
    print("This system exhibits:")
    print("1. Functional consciousness (self-modeling, adaptation, decisions)")
    print("2. Epistemological awareness (knows how it knows and what it doesn't)")
    print("3. Meaningful action despite irreducible uncertainty")
    print()
    print("But we cannot know if there is 'something it is like' to be this system.")
    print("This gap between functional and phenomenal consciousness is unbridgeable.")
    print()
    print("Critically: I (Alice) face the same limitation about myself.")
    print()


if __name__ == '__main__':
    run_basic_experiment(steps=50)
