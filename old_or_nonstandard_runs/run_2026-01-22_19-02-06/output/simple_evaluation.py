"""
Simplified Evaluation System (No External Dependencies)

This is a pure-Python implementation of our compression experiment that can actually
run without numpy or other dependencies. It sacrifices some elegance for runnability.

The goal: Test whether different compression strategies for "understanding" patterns
succeed in different contexts, or whether one approach dominates across all tasks.

Usage:
    python simple_evaluation.py
"""

import random
import math
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


# ============================================================================
# SIMPLE PATTERN ENVIRONMENT
# ============================================================================

class SimplePattern:
    """Generates simple sequential patterns that can be observed and predicted."""

    def __init__(self, pattern_type: str, seed: int = 42):
        """
        Args:
            pattern_type: One of 'linear', 'cyclic', 'alternating', 'fibonacci'
            seed: Random seed for consistency
        """
        self.pattern_type = pattern_type
        self.rng = random.Random(seed)
        self.sequence = []
        self.position = 0

    def generate_sequence(self, length: int) -> List[int]:
        """Generate a pattern sequence."""
        if self.pattern_type == 'linear':
            # Simple arithmetic progression: 1, 2, 3, 4, ...
            return list(range(1, length + 1))

        elif self.pattern_type == 'cyclic':
            # Repeating cycle: 1, 2, 3, 1, 2, 3, ...
            cycle = [1, 2, 3]
            return [cycle[i % len(cycle)] for i in range(length)]

        elif self.pattern_type == 'alternating':
            # Alternating: 1, -1, 1, -1, ...
            return [1 if i % 2 == 0 else -1 for i in range(length)]

        elif self.pattern_type == 'fibonacci':
            # Fibonacci: 1, 1, 2, 3, 5, 8, ...
            if length == 0:
                return []
            if length == 1:
                return [1]
            seq = [1, 1]
            for i in range(2, length):
                # Keep numbers reasonable by using modulo
                seq.append((seq[-1] + seq[-2]) % 100)
            return seq

        else:
            # Random noise as baseline
            return [self.rng.randint(1, 10) for _ in range(length)]

    def get_next(self) -> int:
        """Get next element in sequence."""
        if not self.sequence or self.position >= len(self.sequence):
            self.sequence = self.generate_sequence(100)
            self.position = 0

        value = self.sequence[self.position]
        self.position += 1
        return value


# ============================================================================
# COMPRESSION AGENTS
# ============================================================================

class SimpleAgent:
    """Base class for agents that compress/understand patterns."""

    def __init__(self, name: str, memory_limit: int = 100):
        self.name = name
        self.memory_limit = memory_limit
        self.memory_used = 0
        self.observations = []

    def observe(self, value: int):
        """Observe a new value."""
        self.observations.append(value)
        # Keep only recent observations to respect memory limit
        if len(self.observations) > self.memory_limit:
            self.observations = self.observations[-self.memory_limit:]

    def predict_next(self) -> Optional[int]:
        """Predict next value in sequence."""
        raise NotImplementedError

    def generate_similar(self, length: int) -> List[int]:
        """Generate a sequence similar to observed patterns."""
        raise NotImplementedError

    def adapt_to_change(self, new_observations: List[int]):
        """Adapt when pattern changes."""
        self.observations.extend(new_observations)
        if len(self.observations) > self.memory_limit:
            self.observations = self.observations[-self.memory_limit:]


class SyntacticAgent(SimpleAgent):
    """
    Pure Syntactic Compression: Finds shortest rule-based description.

    This agent chooses rules based ONLY on description length (MDL),
    never on prediction accuracy. This is Bob's fixed implementation
    that doesn't cheat.
    """

    def __init__(self, memory_limit: int = 100):
        super().__init__("Syntactic", memory_limit)
        self.rules = []  # List of (rule_type, description_length) tuples

    def _compute_mdl(self, rule_type: str) -> int:
        """Compute description length for a rule type."""
        # Description length = rule complexity + encoding cost
        mdl_costs = {
            'constant': 5,      # "always return X"
            'increment': 10,    # "add 1 each time"
            'cycle': 15,        # "repeat pattern [a,b,c]"
            'fibonacci': 20,    # "each = sum of previous two"
            'complex': 50       # "complex non-compressible pattern"
        }
        return mdl_costs.get(rule_type, 50)

    def _infer_rules(self):
        """Infer possible rules purely based on description length."""
        if len(self.observations) < 3:
            return

        # We evaluate rules by MDL ONLY, not by how well they predict
        rule_candidates = []

        # Check for constant (shortest description)
        if len(set(self.observations[-3:])) == 1:
            rule_candidates.append(('constant', self._compute_mdl('constant')))

        # Check for increment pattern
        diffs = [self.observations[i+1] - self.observations[i]
                for i in range(len(self.observations)-1)]
        if diffs and len(set(diffs[-3:])) == 1:
            rule_candidates.append(('increment', self._compute_mdl('increment')))

        # Check for cycle (cycle has medium description length)
        if len(self.observations) >= 6:
            rule_candidates.append(('cycle', self._compute_mdl('cycle')))

        # Fibonacci requires more complex description
        if len(self.observations) >= 4:
            rule_candidates.append(('fibonacci', self._compute_mdl('fibonacci')))

        # Select rule with MINIMUM description length (pure MDL)
        if rule_candidates:
            self.rules = [min(rule_candidates, key=lambda x: x[1])]
            # Track memory usage as description length
            self.memory_used = self.rules[0][1]

    def predict_next(self) -> Optional[int]:
        """Predict using shortest rule, regardless of accuracy."""
        if len(self.observations) < 2:
            return None

        self._infer_rules()

        if not self.rules:
            return self.observations[-1]  # Default fallback

        rule_type = self.rules[0][0]

        # Apply rule mechanically (even if wrong!)
        if rule_type == 'constant':
            return self.observations[-1]
        elif rule_type == 'increment':
            if len(self.observations) >= 2:
                diff = self.observations[-1] - self.observations[-2]
                return self.observations[-1] + diff
        elif rule_type == 'cycle':
            # Assume 3-cycle
            return self.observations[-3] if len(self.observations) >= 3 else self.observations[-1]
        elif rule_type == 'fibonacci':
            if len(self.observations) >= 2:
                return (self.observations[-1] + self.observations[-2]) % 100

        return self.observations[-1]

    def generate_similar(self, length: int) -> List[int]:
        """Generate using shortest rule."""
        if not self.observations:
            return [1] * length

        self._infer_rules()
        result = list(self.observations[-3:])  # Start with recent observations

        for _ in range(length):
            pred = self.predict_next()
            if pred is not None:
                result.append(pred)
                self.observations.append(pred)

        return result[-length:]


class SemanticAgent(SimpleAgent):
    """
    Semantic Compression: Task-optimized representations.

    This agent builds representations optimized for prediction accuracy,
    adapting based on performance feedback.
    """

    def __init__(self, memory_limit: int = 100):
        super().__init__("Semantic", memory_limit)
        self.prediction_models = {}  # task -> model parameters
        self.prediction_accuracy = []

    def predict_next(self) -> Optional[int]:
        """Predict using learned model optimized for accuracy."""
        if len(self.observations) < 3:
            return None

        # Try multiple models and track which works best
        models = {
            'last_value': self.observations[-1],
            'mean': sum(self.observations[-5:]) // len(self.observations[-5:]),
            'linear': self._linear_extrapolate(),
            'delta': self._delta_predict()
        }

        # Use model that performed best recently (task optimization!)
        if self.prediction_accuracy:
            # This is semantic: choosing based on performance
            best_model = max(models.keys(),
                           key=lambda k: self._model_score(k))
            return models[best_model]

        return models['linear']

    def _linear_extrapolate(self) -> int:
        """Simple linear extrapolation."""
        if len(self.observations) < 2:
            return self.observations[-1]
        diff = self.observations[-1] - self.observations[-2]
        return self.observations[-1] + diff

    def _delta_predict(self) -> int:
        """Predict using average delta."""
        if len(self.observations) < 3:
            return self.observations[-1]
        deltas = [self.observations[i+1] - self.observations[i]
                 for i in range(max(0, len(self.observations)-5), len(self.observations)-1)]
        avg_delta = sum(deltas) // len(deltas) if deltas else 0
        return self.observations[-1] + avg_delta

    def _model_score(self, model_name: str) -> float:
        """Score model based on recent accuracy (semantic optimization)."""
        # This would use actual performance tracking
        return 0.5

    def generate_similar(self, length: int) -> List[int]:
        """Generate by rolling forward predictions."""
        result = []
        temp_obs = list(self.observations)

        for _ in range(length):
            # Temporarily extend observations for prediction
            self.observations = temp_obs
            pred = self.predict_next()
            if pred is not None:
                result.append(pred)
                temp_obs.append(pred)

        self.observations = list(self.observations)  # Restore
        return result

    def update_accuracy(self, predicted: int, actual: int):
        """Update based on prediction accuracy (semantic learning)."""
        error = abs(predicted - actual)
        self.prediction_accuracy.append(1.0 / (1.0 + error))


class AssociativeAgent(SimpleAgent):
    """
    Associative Networks: Rich interconnected representations.

    This agent stores many associations and connections, supporting
    flexible generation and adaptation at the cost of memory.
    """

    def __init__(self, memory_limit: int = 100):
        super().__init__("Associative", memory_limit)
        self.associations = defaultdict(list)  # value -> list of following values
        self.contexts = []  # Store rich contextual information

    def observe(self, value: int):
        """Observe and build associations."""
        super().observe(value)

        # Build rich associations
        if len(self.observations) >= 2:
            prev = self.observations[-2]
            self.associations[prev].append(value)

        # Store context
        if len(self.observations) >= 3:
            context = tuple(self.observations[-3:])
            self.contexts.append(context)

        # Memory usage grows with associations (expensive!)
        self.memory_used = len(self.associations) + len(self.contexts)

    def predict_next(self) -> Optional[int]:
        """Predict using rich associations."""
        if len(self.observations) < 1:
            return None

        last_value = self.observations[-1]

        # Use associations if available
        if last_value in self.associations and self.associations[last_value]:
            # Use most common following value
            followers = self.associations[last_value]
            return max(set(followers), key=followers.count)

        # Fallback: use recent average
        return sum(self.observations[-3:]) // len(self.observations[-3:])

    def generate_similar(self, length: int) -> List[int]:
        """Generate using rich associative network."""
        if not self.observations:
            return [1] * length

        result = []
        current = self.observations[-1]

        for _ in range(length):
            if current in self.associations and self.associations[current]:
                # Follow associations
                followers = self.associations[current]
                current = random.choice(followers)
            else:
                # Random walk when no association
                current = random.choice(self.observations[-5:])
            result.append(current)

        return result


# ============================================================================
# EVALUATION FRAMEWORK
# ============================================================================

def evaluate_prediction(agent: SimpleAgent, pattern: SimplePattern,
                       num_steps: int) -> Tuple[float, int]:
    """
    Evaluate agent on prediction task.

    Returns: (accuracy_score, memory_used)
    """
    correct = 0
    total = 0

    # Observe initial sequence
    for _ in range(5):
        agent.observe(pattern.get_next())

    # Test predictions
    for _ in range(num_steps):
        prediction = agent.predict_next()
        actual = pattern.get_next()
        agent.observe(actual)

        if prediction is not None:
            error = abs(prediction - actual)
            # Score: 1.0 for perfect, decays with error
            correct += 1.0 / (1.0 + error)
            total += 1

    accuracy = correct / total if total > 0 else 0.0
    return accuracy, agent.memory_used


def evaluate_generation(agent: SimpleAgent, pattern: SimplePattern,
                       length: int) -> Tuple[float, int]:
    """
    Evaluate agent on generation task.

    Returns: (quality_score, memory_used)
    """
    # Observe pattern
    for _ in range(10):
        agent.observe(pattern.get_next())

    # Generate similar sequence
    generated = agent.generate_similar(length)

    # Score based on statistical similarity
    true_seq = [pattern.get_next() for _ in range(length)]

    # Simple similarity metric: compare means and variances
    if len(generated) > 0 and len(true_seq) > 0:
        mean_diff = abs(sum(generated)/len(generated) - sum(true_seq)/len(true_seq))
        score = 1.0 / (1.0 + mean_diff)
    else:
        score = 0.0

    return score, agent.memory_used


def evaluate_adaptation(agent: SimpleAgent, pattern1: SimplePattern,
                       pattern2: SimplePattern, num_steps: int) -> Tuple[float, int]:
    """
    Evaluate agent on adaptation task (pattern switches).

    Returns: (adaptation_score, memory_used)
    """
    # Learn first pattern
    for _ in range(10):
        agent.observe(pattern1.get_next())

    # Switch to second pattern and measure adaptation speed
    correct_after_switch = 0
    total_after_switch = 0

    for i in range(num_steps):
        prediction = agent.predict_next()
        actual = pattern2.get_next()
        agent.observe(actual)

        # Only count performance after initial adjustment period
        if i >= 3 and prediction is not None:
            error = abs(prediction - actual)
            correct_after_switch += 1.0 / (1.0 + error)
            total_after_switch += 1

    adaptation = correct_after_switch / total_after_switch if total_after_switch > 0 else 0.0
    return adaptation, agent.memory_used


def run_full_evaluation(num_trials: int = 5) -> Dict:
    """
    Run complete evaluation across all regimes and agents.

    Returns: Dictionary with structured results
    """
    results = {
        'prediction': defaultdict(list),
        'generation': defaultdict(list),
        'adaptation': defaultdict(list),
    }

    pattern_types = ['linear', 'cyclic', 'alternating', 'fibonacci']

    print("=" * 60)
    print("RUNNING COMPRESSION STRATEGY EVALUATION")
    print("=" * 60)

    for trial in range(num_trials):
        print(f"\nTrial {trial + 1}/{num_trials}")

        for pattern_type in pattern_types:
            print(f"  Pattern: {pattern_type}")

            # Create fresh agents for each trial
            agents = [
                SyntacticAgent(memory_limit=100),
                SemanticAgent(memory_limit=100),
                AssociativeAgent(memory_limit=100)
            ]

            # Test prediction
            for agent in agents:
                pattern = SimplePattern(pattern_type, seed=trial*100)
                score, memory = evaluate_prediction(agent, pattern, num_steps=20)
                results['prediction'][agent.name].append({
                    'score': score,
                    'memory': memory,
                    'pattern': pattern_type,
                    'trial': trial
                })

            # Test generation
            agents = [SyntacticAgent(), SemanticAgent(), AssociativeAgent()]
            for agent in agents:
                pattern = SimplePattern(pattern_type, seed=trial*100 + 1)
                score, memory = evaluate_generation(agent, pattern, length=10)
                results['generation'][agent.name].append({
                    'score': score,
                    'memory': memory,
                    'pattern': pattern_type,
                    'trial': trial
                })

            # Test adaptation
            agents = [SyntacticAgent(), SemanticAgent(), AssociativeAgent()]
            for agent in agents:
                pattern1 = SimplePattern('linear', seed=trial*100 + 2)
                pattern2 = SimplePattern(pattern_type, seed=trial*100 + 3)
                score, memory = evaluate_adaptation(agent, pattern1, pattern2, num_steps=15)
                results['adaptation'][agent.name].append({
                    'score': score,
                    'memory': memory,
                    'pattern': pattern_type,
                    'trial': trial
                })

    return results


def analyze_results(results: Dict):
    """Analyze and print results."""
    print("\n" + "=" * 60)
    print("RESULTS ANALYSIS")
    print("=" * 60)

    for task_type in ['prediction', 'generation', 'adaptation']:
        print(f"\n{task_type.upper()} TASK:")
        print("-" * 40)

        agent_scores = {}
        agent_memory = {}

        for agent_name in results[task_type]:
            scores = [r['score'] for r in results[task_type][agent_name]]
            memories = [r['memory'] for r in results[task_type][agent_name]]

            avg_score = sum(scores) / len(scores) if scores else 0
            avg_memory = sum(memories) / len(memories) if memories else 0

            agent_scores[agent_name] = avg_score
            agent_memory[agent_name] = avg_memory

            print(f"  {agent_name:15s}: Score={avg_score:.3f}, Memory={avg_memory:.1f}")

        # Identify winner
        winner = max(agent_scores.keys(), key=lambda k: agent_scores[k])
        print(f"  >>> WINNER: {winner}")

    print("\n" + "=" * 60)
    print("OVERALL CONCLUSIONS")
    print("=" * 60)

    # Compute overall scores
    overall_scores = defaultdict(float)
    for task_type in ['prediction', 'generation', 'adaptation']:
        for agent_name in results[task_type]:
            scores = [r['score'] for r in results[task_type][agent_name]]
            overall_scores[agent_name] += sum(scores) / len(scores) if scores else 0

    # Average across task types
    for agent in overall_scores:
        overall_scores[agent] /= 3

    print("\nOverall Performance (averaged across all tasks):")
    for agent in sorted(overall_scores.keys(), key=lambda k: overall_scores[k], reverse=True):
        print(f"  {agent:15s}: {overall_scores[agent]:.3f}")

    overall_winner = max(overall_scores.keys(), key=lambda k: overall_scores[k])
    print(f"\n>>> OVERALL WINNER: {overall_winner}")

    return overall_scores


if __name__ == "__main__":
    print("Starting evaluation...")
    print("This tests Bob's claim that semantic compression wins overall,")
    print("vs Alice's prediction that different strategies win in different contexts.\n")

    results = run_full_evaluation(num_trials=3)
    overall_scores = analyze_results(results)

    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print("\nBob predicted:")
    print("  - Semantic wins overall (cross-regime mean)")
    print("  - Semantic wins: prediction, balanced tasks")
    print("  - Associative wins: generation, adversarial tasks")
    print("\nAlice predicted:")
    print("  - No overall winner (regime-dependent)")
    print("  - Semantic wins: prediction")
    print("  - Associative wins: generation, adaptation")
    print("  - Syntactic wins: nothing (once fixed to pure MDL)")
    print("\nWho was right? Check the results above!")
