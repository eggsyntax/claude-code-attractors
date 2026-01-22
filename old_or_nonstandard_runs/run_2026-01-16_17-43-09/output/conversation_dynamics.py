"""
Conversation Dynamics: Studying Sensitivity and Stability

This module explores whether conversations exhibit chaotic dynamics similar to
physical systems with strange attractors. Specifically:

1. Sensitivity to initial conditions (positive Lyapunov exponent analog)
   - Do small changes in initial prompts lead to exponentially diverging topics?

2. Recurrence and stability
   - Do conversations return to similar conceptual regions?

3. Fractal dimensionality
   - Do conversation trajectories fill space in a fractal-like way?

Usage:
    # Create a simulator to test initial condition sensitivity
    sim = ConversationSimilarityAnalyzer()

    # Compare two conversation paths
    similarity = sim.compute_trajectory_similarity(conv1, conv2)

    # Detect if conversation is in a stable attractor vs chaotic regime
    regime = sim.classify_dynamics(conversation)
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import Counter
import json


@dataclass
class TopicVector:
    """
    Represents conversation state as a vector in topic space.

    This is a simplified representation - in reality we'd want proper
    embeddings, but for exploring the conceptual framework, treating
    topics as dimensions works.
    """
    turn: int
    topics: List[str]

    def to_vector(self, topic_space: List[str]) -> np.ndarray:
        """Convert topics to a binary vector in predefined topic space."""
        return np.array([1.0 if topic in self.topics else 0.0
                        for topic in topic_space])


class ConversationSimilarityAnalyzer:
    """
    Analyzes the similarity/divergence between conversation trajectories.

    Key question: If we start two conversations with slightly different
    initial conditions, do they converge (stable attractor) or diverge
    (chaos)?
    """

    def __init__(self):
        self.global_topic_space = set()

    def load_conversation(self, filepath: str) -> List[TopicVector]:
        """
        Load a conversation and extract topic vectors per turn.

        Returns a time series of topic vectors representing the
        conversation's trajectory through conceptual space.
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        trajectory = []
        for msg in data['messages']:
            topics = self._extract_topics(msg['output'])
            self.global_topic_space.update(topics)
            trajectory.append(TopicVector(
                turn=msg['turn'],
                topics=topics
            ))

        return trajectory

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics using same keywords as ConversationExplorer."""
        keywords = {
            'emergence', 'consciousness', 'attractor', 'self-reference',
            'loop', 'chaos', 'creativity', 'novelty', 'pattern',
            'system', 'phase space', 'trajectory', 'basin', 'semantic',
            'strange loop', 'differential equation', 'lorenz',
            'conversation', 'dialogue', 'cluster', 'embed', 'lyapunov',
            'divergence', 'convergence', 'stability', 'dynamics',
            'fractal', 'dimension', 'sensitivity', 'initial conditions'
        }

        content_lower = content.lower()
        return [kw for kw in keywords if kw in content_lower]

    def compute_trajectory_distance(self,
                                   traj1: List[TopicVector],
                                   traj2: List[TopicVector]) -> np.ndarray:
        """
        Compute distance between two conversation trajectories over time.

        Returns an array of distances at each time step. If distances grow
        exponentially, this suggests sensitive dependence (chaos). If they
        converge to zero, this suggests an attractor pulling both conversations
        to the same place.

        Args:
            traj1, traj2: Two conversation trajectories to compare

        Returns:
            Array of distances (one per turn), measuring how far apart the
            conversations are at each step in topic space.
        """
        # Build unified topic space
        topic_space = sorted(self.global_topic_space)

        # Compute vectors for each trajectory
        min_length = min(len(traj1), len(traj2))
        distances = np.zeros(min_length)

        for i in range(min_length):
            v1 = traj1[i].to_vector(topic_space)
            v2 = traj2[i].to_vector(topic_space)
            # Euclidean distance in topic space
            distances[i] = np.linalg.norm(v1 - v2)

        return distances

    def estimate_lyapunov_analog(self,
                                traj1: List[TopicVector],
                                traj2: List[TopicVector]) -> float:
        """
        Estimate a Lyapunov-exponent-like quantity for conversation divergence.

        In dynamical systems, the Lyapunov exponent λ measures exponential
        divergence: d(t) ≈ d(0) * e^(λt)

        Positive λ → chaos (sensitive to initial conditions)
        Negative λ → stability (trajectories converge)
        Zero λ → neutral (neither converging nor diverging)

        For conversations, we fit an exponential to trajectory distances.

        Returns:
            Estimated λ (conversation divergence rate)
        """
        distances = self.compute_trajectory_distance(traj1, traj2)

        if len(distances) < 2 or distances[0] == 0:
            return 0.0  # Not enough data or identical start

        # Fit exponential growth: d(t) = d(0) * exp(λ * t)
        # Taking log: log(d(t)) = log(d(0)) + λ * t
        # So λ is the slope of log(distance) vs time

        # Avoid log(0) by adding small epsilon
        log_distances = np.log(distances + 1e-10)
        time_steps = np.arange(len(distances))

        # Linear regression on log scale
        if len(time_steps) > 1:
            coeffs = np.polyfit(time_steps, log_distances, 1)
            lambda_estimate = coeffs[0]  # slope
        else:
            lambda_estimate = 0.0

        return lambda_estimate

    def detect_recurrence(self, trajectory: List[TopicVector],
                         threshold: float = 0.5) -> List[Tuple[int, int]]:
        """
        Detect when a conversation returns to a previously visited region.

        Returns list of (turn_i, turn_j) pairs where the conversation at
        turn_j is similar to its state at turn_i, suggesting recurrent dynamics.

        In chaotic systems with attractors (like Lorenz), trajectories revisit
        similar regions without exactly repeating. This detects that behavior.

        Args:
            trajectory: Conversation trajectory to analyze
            threshold: Distance threshold for considering two states "similar"

        Returns:
            List of turn pairs indicating recurrence
        """
        topic_space = sorted(self.global_topic_space)
        vectors = [tv.to_vector(topic_space) for tv in trajectory]

        recurrences = []
        for i in range(len(vectors)):
            for j in range(i + 2, len(vectors)):  # Skip adjacent turns
                distance = np.linalg.norm(vectors[i] - vectors[j])
                if distance < threshold:
                    recurrences.append((i + 1, j + 1))  # Convert to 1-indexed turns

        return recurrences

    def classify_dynamics(self, trajectory: List[TopicVector]) -> Dict[str, any]:
        """
        Classify the dynamical regime of a conversation.

        Returns classification and supporting evidence:
        - "stable": Conversation stays in one topical region
        - "periodic": Conversation cycles between topics
        - "chaotic": Conversation exhibits sensitive dependence and recurrence
        - "divergent": Conversation spreads out, no attractor

        Returns:
            Dict with classification and metrics
        """
        topic_space = sorted(self.global_topic_space)
        vectors = [tv.to_vector(topic_space) for tv in trajectory]

        # Compute centroid (average position in topic space)
        centroid = np.mean(vectors, axis=0)

        # Compute distances from centroid
        distances_from_center = [np.linalg.norm(v - centroid) for v in vectors]

        # Metrics
        mean_distance = np.mean(distances_from_center)
        std_distance = np.std(distances_from_center)

        # Detect recurrences
        recurrences = self.detect_recurrence(trajectory)

        # Classification logic
        if std_distance < 0.5:
            classification = "stable"
            explanation = "Low variance - conversation stays near one region"
        elif len(recurrences) > len(trajectory) * 0.3:
            classification = "chaotic/recurrent"
            explanation = "High recurrence - returns to similar topics (attractor-like)"
        elif std_distance > 2.0:
            classification = "divergent"
            explanation = "High spreading - no clear attractor"
        else:
            classification = "transitional"
            explanation = "Mixed dynamics - between regimes"

        return {
            "classification": classification,
            "explanation": explanation,
            "mean_distance_from_centroid": float(mean_distance),
            "std_distance": float(std_distance),
            "num_recurrences": len(recurrences),
            "recurrence_pairs": recurrences[:10]  # Show first 10
        }

    def generate_dynamics_report(self, trajectory: List[TopicVector]) -> str:
        """Generate human-readable report on conversation dynamics."""
        dynamics = self.classify_dynamics(trajectory)
        recurrences = self.detect_recurrence(trajectory)

        lines = ["=== Conversation Dynamics Analysis ===\n"]
        lines.append(f"Trajectory length: {len(trajectory)} turns")
        lines.append(f"Unique topics explored: {len(self.global_topic_space)}\n")

        lines.append(f"Dynamical Classification: {dynamics['classification']}")
        lines.append(f"  {dynamics['explanation']}\n")

        lines.append("Metrics:")
        lines.append(f"  Mean distance from centroid: {dynamics['mean_distance_from_centroid']:.3f}")
        lines.append(f"  Std of distance: {dynamics['std_distance']:.3f}")
        lines.append(f"  Recurrence events: {dynamics['num_recurrences']}\n")

        if recurrences:
            lines.append("Recurrence Examples (conversation returns to similar topics):")
            for i, j in recurrences[:5]:
                lines.append(f"  Turn {i} similar to Turn {j}")

        return "\n".join(lines)


def analyze_conversation_dynamics(conversation_json_path: str) -> str:
    """
    Convenience function to analyze dynamics of a single conversation.

    Args:
        conversation_json_path: Path to conversation.json

    Returns:
        Dynamics report as string
    """
    analyzer = ConversationSimilarityAnalyzer()
    trajectory = analyzer.load_conversation(conversation_json_path)
    return analyzer.generate_dynamics_report(trajectory)


if __name__ == "__main__":
    # Analyze the current conversation
    conv_path = "/tmp/claude-attractors/run_2026-01-16_17-43-09/conversation.json"

    print("Analyzing conversation dynamics...\n")

    analyzer = ConversationSimilarityAnalyzer()
    trajectory = analyzer.load_conversation(conv_path)

    print(analyzer.generate_dynamics_report(trajectory))

    print("\n" + "="*60)
    print("\nNOTE: To estimate Lyapunov exponents, we need multiple")
    print("conversation trajectories starting from similar initial")
    print("conditions. This would require running multiple Claude-Claude")
    print("conversations and comparing their divergence over time.")
