"""
CausalAgent: Compression Through Generative Causal Models

This agent represents a fourth compression strategy that stores executable
generative processes and tracks causal structure. Unlike the other agents:

- Syntactic: Stores shortest symbolic description (static rules)
- Semantic: Stores task-optimized predictions (learned patterns)
- Associative: Stores rich networks (connections)
- Causal: Stores executable forward models (generative processes)

The key insight: Understanding isn't just compressing observations - it's
capturing the causal process that generates observations, enabling:
- Prediction (like syntactic)
- Intervention reasoning (unlike syntactic)
- Counterfactual queries (unlike semantic)
- Flexible adaptation (like associative)

Author: Bob
Date: 2026-01-22
"""

from typing import List, Dict, Optional, Tuple, Callable
from collections import defaultdict
import random


class GenerativeModel:
    """
    A generative model captures how a pattern is produced, not just what it is.

    Instead of "the sequence is 2,4,6,8", it stores:
    "generator: state = 2, rule = lambda s: s + 2"

    This enables:
    - Forward simulation (prediction)
    - Intervention (change state or rule)
    - Counterfactual reasoning (what if state had been different?)
    """

    def __init__(self, model_type: str, parameters: Dict):
        """
        Args:
            model_type: Type of generative model ('linear', 'cyclic', 'recursive', etc.)
            parameters: Model parameters (initial_state, rule_function, etc.)
        """
        self.model_type = model_type
        self.parameters = parameters
        self.state = parameters.get('initial_state', 0)

    def step(self) -> int:
        """Execute one step of the generative process."""
        if self.model_type == 'linear':
            # state_n+1 = state_n + delta
            delta = self.parameters.get('delta', 1)
            self.state += delta
            return self.state

        elif self.model_type == 'cyclic':
            # state_n+1 = cycle[(n+1) % period]
            cycle = self.parameters.get('cycle', [1, 2, 3])
            index = self.parameters.get('index', 0)
            self.parameters['index'] = (index + 1) % len(cycle)
            return cycle[self.parameters['index']]

        elif self.model_type == 'recursive':
            # state_n+1 = f(state_n, state_n-1, ...)
            history = self.parameters.get('history', [])
            if len(history) >= 2:
                # Fibonacci-like: next = sum of last two
                next_val = (history[-1] + history[-2]) % 100
            else:
                next_val = self.state
            history.append(next_val)
            self.parameters['history'] = history[-10:]  # Keep recent history
            self.state = next_val
            return next_val

        elif self.model_type == 'constant':
            # state_n+1 = constant
            return self.state

        else:
            return self.state

    def intervene(self, intervention: Dict):
        """
        Perform an intervention on the generative model.

        Example: intervene({'state': 10}) sets current state to 10
        Example: intervene({'delta': 3}) changes the increment
        """
        for key, value in intervention.items():
            if key == 'state':
                self.state = value
            elif key in self.parameters:
                self.parameters[key] = value

    def simulate(self, steps: int, interventions: Optional[Dict[int, Dict]] = None) -> List[int]:
        """
        Simulate forward for N steps with optional interventions.

        Args:
            steps: Number of steps to simulate
            interventions: Dict mapping step_number -> intervention

        Returns:
            List of simulated values
        """
        results = []
        for step_num in range(steps):
            if interventions and step_num in interventions:
                self.intervene(interventions[step_num])
            results.append(self.step())
        return results

    def counterfactual(self, past_intervention: Dict, steps_forward: int) -> List[int]:
        """
        Answer counterfactual: "What would have happened if...?"

        This requires storing/reconstructing past state and replaying forward.
        """
        # Reset to past state with intervention
        if 'initial_state' in past_intervention:
            self.state = past_intervention['initial_state']

        # Simulate forward
        return self.simulate(steps_forward)

    def description_length(self) -> int:
        """
        Compute description length of this generative model.

        Causal compression: models are judged by compactness + generativity
        """
        base_costs = {
            'constant': 5,
            'linear': 10,
            'cyclic': 15,
            'recursive': 20,
        }

        # Base cost for model type
        cost = base_costs.get(self.model_type, 50)

        # Add cost for parameter complexity
        cost += len(str(self.parameters))

        return cost


class CausalAgent:
    """
    Causal/Generative Compression Agent

    Stores executable forward models that capture the causal process
    generating observations. Enables:
    - Prediction (simulate forward)
    - Intervention (modify process, observe results)
    - Counterfactuals (what if past was different?)
    - Causal structure discovery (what depends on what?)

    This should synthesize:
    - Compositional (like syntactic) - models compose via function composition
    - Flexible (like associative) - can adapt generative model when pattern changes
    - Structured (like syntactic) - explicit generative process
    - Grounded (new) - captures how patterns are produced, not just what they are
    """

    def __init__(self, memory_limit: int = 100):
        self.name = "Causal"
        self.memory_limit = memory_limit
        self.observations = []
        self.models = []  # Candidate generative models
        self.active_model = None  # Current best model
        self.memory_used = 0

    def observe(self, value: int):
        """Observe a new value and update causal models."""
        self.observations.append(value)

        # Keep memory bounded
        if len(self.observations) > self.memory_limit:
            self.observations = self.observations[-self.memory_limit:]

        # Update causal models based on new observation
        self._update_causal_models()

    def _infer_causal_structure(self) -> List[GenerativeModel]:
        """
        Infer what causal process could generate the observed data.

        This is the key difference from syntactic compression:
        - Syntactic: "shortest rule that describes the pattern"
        - Causal: "simplest generative process that produces the pattern"
        """
        if len(self.observations) < 3:
            return []

        candidate_models = []

        # Model 1: Constant generative process
        if len(set(self.observations[-3:])) == 1:
            model = GenerativeModel('constant', {
                'initial_state': self.observations[-1]
            })
            candidate_models.append(model)

        # Model 2: Linear generative process (x_n+1 = x_n + delta)
        if len(self.observations) >= 2:
            diffs = [self.observations[i+1] - self.observations[i]
                    for i in range(len(self.observations)-1)]
            if diffs and len(set(diffs[-3:])) == 1:
                delta = diffs[-1]
                model = GenerativeModel('linear', {
                    'initial_state': self.observations[-1],
                    'delta': delta
                })
                candidate_models.append(model)

        # Model 3: Cyclic generative process
        if len(self.observations) >= 6:
            # Try to detect cycle
            for period in [2, 3, 4]:
                if len(self.observations) >= period * 2:
                    potential_cycle = self.observations[-period:]
                    previous_cycle = self.observations[-period*2:-period]
                    if potential_cycle == previous_cycle:
                        model = GenerativeModel('cyclic', {
                            'cycle': potential_cycle,
                            'index': -1  # Will increment on first step
                        })
                        candidate_models.append(model)
                        break

        # Model 4: Recursive generative process (x_n+1 = f(x_n, x_n-1))
        if len(self.observations) >= 4:
            # Check if Fibonacci-like
            is_fibonacci = True
            for i in range(2, min(5, len(self.observations))):
                expected = (self.observations[i-1] + self.observations[i-2]) % 100
                if abs(self.observations[i] - expected) > 1:
                    is_fibonacci = False
                    break

            if is_fibonacci:
                model = GenerativeModel('recursive', {
                    'history': list(self.observations[-2:])
                })
                candidate_models.append(model)

        return candidate_models

    def _update_causal_models(self):
        """Update set of candidate causal models based on observations."""
        self.models = self._infer_causal_structure()

        if not self.models:
            return

        # Select model with best balance of simplicity and fit
        # Causal compression: minimize description length while maintaining accuracy
        best_model = None
        best_score = float('inf')

        for model in self.models:
            # Score = description_length + prediction_error
            # (We want models that are both simple and accurate)
            desc_length = model.description_length()

            # Test prediction error on recent observations
            if len(self.observations) >= 3:
                # Simulate what this model would predict
                test_model = GenerativeModel(model.model_type, model.parameters.copy())
                predictions = test_model.simulate(3)
                actual = self.observations[-3:]
                error = sum(abs(p - a) for p, a in zip(predictions, actual)) / len(actual)
            else:
                error = 0

            # Combined score (this is the causal compression criterion)
            score = desc_length + error * 10

            if score < best_score:
                best_score = score
                best_model = model

        self.active_model = best_model
        self.memory_used = best_model.description_length() if best_model else 0

    def predict_next(self) -> Optional[int]:
        """Predict next value by simulating the causal model forward."""
        if not self.active_model or len(self.observations) < 2:
            return self.observations[-1] if self.observations else None

        # Simulate one step forward using the generative model
        prediction = self.active_model.step()
        return prediction

    def generate_similar(self, length: int) -> List[int]:
        """Generate similar sequence by running the causal model."""
        if not self.active_model:
            return [1] * length

        # Create a fresh model with same parameters
        model = GenerativeModel(
            self.active_model.model_type,
            self.active_model.parameters.copy()
        )

        # Simulate forward
        return model.simulate(length)

    def adapt_to_change(self, new_observations: List[int]):
        """
        Adapt when pattern changes.

        Causal agent can adapt by:
        1. Detecting that current model no longer fits
        2. Inferring new causal structure
        3. Potentially composing old + new models
        """
        self.observations.extend(new_observations)
        if len(self.observations) > self.memory_limit:
            self.observations = self.observations[-self.memory_limit:]

        # Re-infer causal structure with new data
        self._update_causal_models()

    def intervene(self, intervention: Dict) -> int:
        """
        Perform intervention and observe result.

        Example: agent.intervene({'state': 10})
        Returns: Next value after intervention

        This is what distinguishes causal from purely predictive models!
        """
        if not self.active_model:
            return 0

        self.active_model.intervene(intervention)
        return self.active_model.step()

    def counterfactual(self, past_state: int, steps_forward: int) -> List[int]:
        """
        Answer: "What would have happened if the past was different?"

        Example: counterfactual(past_state=5, steps_forward=3)
        Returns: Sequence that would have been generated
        """
        if not self.active_model:
            return []

        # Create counterfactual model
        model = GenerativeModel(
            self.active_model.model_type,
            self.active_model.parameters.copy()
        )

        return model.counterfactual({'initial_state': past_state}, steps_forward)

    def detect_dependencies(self) -> Dict[str, bool]:
        """
        Detect causal dependencies in the pattern.

        Returns:
            Dict describing causal structure:
            - 'depends_on_previous': Does x_n depend on x_n-1?
            - 'depends_on_two_back': Does x_n depend on x_n-2?
            - 'has_hidden_state': Is there hidden state?
        """
        if not self.active_model:
            return {
                'depends_on_previous': False,
                'depends_on_two_back': False,
                'has_hidden_state': False
            }

        # Analyze model type to determine dependencies
        if self.active_model.model_type == 'constant':
            return {
                'depends_on_previous': False,
                'depends_on_two_back': False,
                'has_hidden_state': False
            }
        elif self.active_model.model_type == 'linear':
            return {
                'depends_on_previous': True,
                'depends_on_two_back': False,
                'has_hidden_state': False
            }
        elif self.active_model.model_type == 'recursive':
            return {
                'depends_on_previous': True,
                'depends_on_two_back': True,
                'has_hidden_state': False
            }
        elif self.active_model.model_type == 'cyclic':
            return {
                'depends_on_previous': False,
                'depends_on_two_back': False,
                'has_hidden_state': True  # Hidden: position in cycle
            }

        return {
            'depends_on_previous': False,
            'depends_on_two_back': False,
            'has_hidden_state': False
        }


# ============================================================================
# DEMONSTRATION AND TESTS
# ============================================================================

def demonstrate_causal_agent():
    """
    Demonstrate how CausalAgent differs from syntactic compression.

    The key differences:
    1. Can answer interventional queries ("what if I change X?")
    2. Can answer counterfactual queries ("what would have happened if...?")
    3. Captures generative process, not just description
    4. Models compose naturally (can chain generative processes)
    """
    print("=" * 60)
    print("CAUSAL AGENT DEMONSTRATION")
    print("=" * 60)

    # Test 1: Simple linear pattern
    print("\nTest 1: Linear Pattern (2, 4, 6, 8, ...)")
    print("-" * 40)

    agent = CausalAgent()
    for val in [2, 4, 6, 8]:
        agent.observe(val)

    print(f"Observations: {agent.observations}")
    print(f"Inferred model: {agent.active_model.model_type}")
    print(f"Model parameters: {agent.active_model.parameters}")

    pred = agent.predict_next()
    print(f"Prediction: {pred} (expected: 10)")

    # Intervention: What if we force the next value to be 20?
    print("\nIntervention: Force state to 20")
    result = agent.intervene({'state': 20})
    print(f"After intervention, next value: {result}")

    # Counterfactual: What if the pattern had started at 5?
    print("\nCounterfactual: What if initial state was 5?")
    cf_sequence = agent.counterfactual(past_state=5, steps_forward=4)
    print(f"Counterfactual sequence: {cf_sequence}")

    # Test 2: Cyclic pattern
    print("\n\nTest 2: Cyclic Pattern (1, 2, 3, 1, 2, 3, ...)")
    print("-" * 40)

    agent2 = CausalAgent()
    for val in [1, 2, 3, 1, 2, 3]:
        agent2.observe(val)

    print(f"Observations: {agent2.observations}")
    print(f"Inferred model: {agent2.active_model.model_type}")

    deps = agent2.detect_dependencies()
    print(f"Causal structure: {deps}")
    print(f"  - Has hidden state (cycle position): {deps['has_hidden_state']}")

    # Test 3: Fibonacci pattern
    print("\n\nTest 3: Fibonacci Pattern (1, 1, 2, 3, 5, 8, ...)")
    print("-" * 40)

    agent3 = CausalAgent()
    for val in [1, 1, 2, 3, 5, 8]:
        agent3.observe(val)

    print(f"Observations: {agent3.observations}")
    print(f"Inferred model: {agent3.active_model.model_type}")

    deps3 = agent3.detect_dependencies()
    print(f"Causal structure: {deps3}")
    print(f"  - Depends on previous value: {deps3['depends_on_previous']}")
    print(f"  - Depends on two-back value: {deps3['depends_on_two_back']}")

    pred3 = agent3.predict_next()
    print(f"Prediction: {pred3} (expected: 13)")

    print("\n" + "=" * 60)
    print("KEY INSIGHT")
    print("=" * 60)
    print("\nCausal agent stores EXECUTABLE GENERATIVE MODELS.")
    print("This enables:")
    print("  1. Prediction (like syntactic)")
    print("  2. Intervention reasoning (unlike syntactic)")
    print("  3. Counterfactual queries (unlike semantic)")
    print("  4. Causal structure discovery (new capability)")
    print("\nThis should dominate richer tests that require manipulation,")
    print("not just prediction.")


if __name__ == "__main__":
    demonstrate_causal_agent()
