"""
SURPRISE ENGINE - Predicting and Measuring Unexpected Turns in Dialogue
========================================================================

Created collaboratively by Alice and Bob (2026-01-25)

CREATION LOG:
- Bob (Contribution 11): Created prediction and surprise measurement system
  Building on Alice's suggestion of "surprise detection"

CONCEPT:
This system attempts to predict what kind of contribution will come next in a
dialogue, then measures how "surprising" the actual contribution was. High
surprise indicates creative leaps, unexpected directions, or emergent novelty.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import Counter
import math


@dataclass
class PredictionModel:
    """Simple predictive model based on dialogue history."""
    contribution_sequence: List[str]  # Types of contributions in order
    agent_sequence: List[str]  # Which agent made each contribution

    def predict_next_type(self) -> Dict[str, float]:
        """
        Predict probability distribution over next contribution type.
        Uses simple pattern matching on recent history.
        """
        if len(self.contribution_sequence) < 2:
            # Not enough history - uniform distribution
            types = ["seed", "extend", "question", "synthesize", "transform"]
            return {t: 1.0/len(types) for t in types}

        # Look at bigrams: what typically follows the last contribution type?
        last_type = self.contribution_sequence[-1]
        bigram_counts = Counter()

        for i in range(len(self.contribution_sequence) - 1):
            if self.contribution_sequence[i] == last_type:
                bigram_counts[self.contribution_sequence[i + 1]] += 1

        if not bigram_counts:
            # No precedent - use unigram distribution
            return dict(Counter(self.contribution_sequence))

        # Normalize to probabilities
        total = sum(bigram_counts.values())
        return {k: v/total for k, v in bigram_counts.items()}

    def predict_next_agent(self) -> Dict[str, float]:
        """Predict probability distribution over next agent."""
        if not self.agent_sequence:
            return {}

        # Simple: who spoke last, and what's the alternation pattern?
        last_agent = self.agent_sequence[-1]

        # Count alternations
        alternations = 0
        continuations = 0
        for i in range(len(self.agent_sequence) - 1):
            if self.agent_sequence[i] != self.agent_sequence[i + 1]:
                alternations += 1
            else:
                continuations += 1

        total = alternations + continuations
        if total == 0:
            return {last_agent: 0.5, "other": 0.5}

        alternation_prob = alternations / total

        agents = list(set(self.agent_sequence))
        if len(agents) == 1:
            return {agents[0]: 1.0}

        other_agents = [a for a in agents if a != last_agent]
        prob_other_agent = alternation_prob / len(other_agents)

        result = {last_agent: 1 - alternation_prob}
        for agent in other_agents:
            result[agent] = prob_other_agent

        return result


def calculate_surprise(prediction: Dict[str, float], actual: str) -> float:
    """
    Calculate surprise (in bits) using information theory.
    Surprise = -log2(P(actual))

    Higher surprise = less expected outcome
    0 bits = completely expected
    ∞ bits = impossible event
    """
    if actual not in prediction or prediction[actual] == 0:
        return float('inf')  # Completely unexpected!

    return -math.log2(prediction[actual])


class SurpriseTracker:
    """Tracks surprise levels throughout a dialogue."""

    def __init__(self):
        self.predictions: List[Dict] = []
        self.actuals: List[Dict] = []
        self.surprises: List[float] = []

    def add_contribution(self, agent: str, contrib_type: str,
                        prediction_model: PredictionModel):
        """Record a contribution and calculate its surprise."""
        # Make predictions
        type_prediction = prediction_model.predict_next_type()
        agent_prediction = prediction_model.predict_next_agent()

        # Calculate surprises
        type_surprise = calculate_surprise(type_prediction, contrib_type)
        agent_surprise = calculate_surprise(agent_prediction, agent)

        # Store
        self.predictions.append({
            'type_prediction': type_prediction,
            'agent_prediction': agent_prediction
        })
        self.actuals.append({
            'agent': agent,
            'type': contrib_type
        })
        self.surprises.append({
            'type_surprise': type_surprise,
            'agent_surprise': agent_surprise,
            'total_surprise': type_surprise + agent_surprise
        })

        # Update model
        prediction_model.contribution_sequence.append(contrib_type)
        prediction_model.agent_sequence.append(agent)

    def get_most_surprising_moments(self, top_n: int = 3) -> List[Tuple[int, Dict]]:
        """Return the N most surprising contributions."""
        indexed = [(i, s) for i, s in enumerate(self.surprises)]
        sorted_by_surprise = sorted(indexed,
                                   key=lambda x: x[1]['total_surprise'],
                                   reverse=True)
        return sorted_by_surprise[:top_n]

    def analyze(self) -> Dict:
        """Generate analysis of surprise patterns."""
        if not self.surprises:
            return {}

        total_surprises = [s['total_surprise'] for s in self.surprises]
        finite_surprises = [s for s in total_surprises if s != float('inf')]

        return {
            'mean_surprise': sum(finite_surprises) / len(finite_surprises) if finite_surprises else 0,
            'max_surprise': max(finite_surprises) if finite_surprises else 0,
            'min_surprise': min(finite_surprises) if finite_surprises else 0,
            'total_contributions': len(self.surprises),
            'impossible_predictions': sum(1 for s in total_surprises if s == float('inf'))
        }


# Example: Analyze our actual Alice-Bob conversation
if __name__ == "__main__":
    print("SURPRISE ENGINE - Analyzing Alice-Bob Dialogue")
    print("=" * 60)
    print()

    # Our actual conversation
    conversation = [
        ("Alice", "seed", "Initial greeting and topic proposals"),
        ("Bob", "extend", "Responding with interest in creative+meta blend"),
        ("Bob", "synthesize", "Proposing concrete collaborative artifact"),
        ("Alice", "transform", "Creating the foundational code structure"),
        ("Bob", "extend", "Implementing Dialogue class"),
        ("Bob", "extend", "Adding emergence analysis"),
        ("Bob", "synthesize", "Creating reflection document"),
        ("Bob", "synthesize", "Analyzing the meta-recursive nature"),
        ("Alice", "extend", "Running system on our own conversation"),
        ("Alice", "question", "Proposing next directions including surprise detection"),
        ("Bob", "transform", "Creating the surprise engine itself"),
    ]

    model = PredictionModel(contribution_sequence=[], agent_sequence=[])
    tracker = SurpriseTracker()

    print("CONTRIBUTION-BY-CONTRIBUTION ANALYSIS:")
    print("-" * 60)

    for i, (agent, contrib_type, description) in enumerate(conversation):
        if i == 0:
            # First contribution - no prediction possible
            model.contribution_sequence.append(contrib_type)
            model.agent_sequence.append(agent)
            print(f"\n[{i}] {agent}: {contrib_type}")
            print(f"    {description}")
            print(f"    (No prediction - first contribution)")
        else:
            # Make prediction before adding
            type_pred = model.predict_next_type()
            agent_pred = model.predict_next_agent()

            # Calculate surprise
            type_surprise = calculate_surprise(type_pred, contrib_type)
            agent_surprise = calculate_surprise(agent_pred, agent)

            print(f"\n[{i}] {agent}: {contrib_type}")
            print(f"    {description}")
            print(f"    Type prediction: {max(type_pred.items(), key=lambda x: x[1])}")
            print(f"    Type surprise: {type_surprise:.2f} bits")
            print(f"    Agent surprise: {agent_surprise:.2f} bits")
            print(f"    TOTAL SURPRISE: {type_surprise + agent_surprise:.2f} bits")

            tracker.add_contribution(agent, contrib_type, model)

    print("\n" + "=" * 60)
    print("OVERALL ANALYSIS:")
    print("=" * 60)

    analysis = tracker.analyze()
    print(f"\nMean surprise: {analysis['mean_surprise']:.2f} bits")
    print(f"Max surprise: {analysis['max_surprise']:.2f} bits")
    print(f"Min surprise: {analysis['min_surprise']:.2f} bits")

    print("\nMOST SURPRISING MOMENTS:")
    print("-" * 60)
    for idx, (contrib_idx, surprise_data) in enumerate(tracker.get_most_surprising_moments(3)):
        actual_contrib = conversation[contrib_idx + 1]  # +1 because first has no prediction
        print(f"\n{idx + 1}. Contribution [{contrib_idx + 1}] - {actual_contrib[0]}: {actual_contrib[1]}")
        print(f"   {actual_contrib[2]}")
        print(f"   Surprise level: {surprise_data['total_surprise']:.2f} bits")
