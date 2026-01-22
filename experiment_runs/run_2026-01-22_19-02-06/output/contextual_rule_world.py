"""
Contextual Rule World - Testing Coherent Compression vs Pure Compression

This module implements a domain where:
1. Rules are context-dependent (if X then Y)
2. Some contexts have hidden contradictions
3. Pure compression minimizes description length
4. Coherent compression enforces logical consistency

The decisive question: Does coherence constraint improve compositional reasoning?

Author: Alice
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Context:
    """A context is a set of properties that might have contradictions."""
    properties: Set[str]

    def contradicts(self, other: 'Context') -> bool:
        """Check if this context has contradictory properties."""
        # Define known contradictions
        contradictions = [
            {'sunny', 'rainy'},
            {'hot', 'cold'},
            {'day', 'night'},
            {'wet', 'dry'},
        ]

        all_props = self.properties | other.properties
        for contra_pair in contradictions:
            if contra_pair.issubset(all_props):
                return True
        return False

    def is_consistent(self) -> bool:
        """Check if this context is internally consistent."""
        contradictions = [
            {'sunny', 'rainy'},
            {'hot', 'cold'},
            {'day', 'night'},
            {'wet', 'dry'},
        ]

        for contra_pair in contradictions:
            if contra_pair.issubset(self.properties):
                return False
        return True


@dataclass
class Rule:
    """A conditional rule: if context matches, then apply action."""
    context: Context
    action: str

    def applies_to(self, query_context: Context) -> bool:
        """Does this rule apply to the given context?"""
        return self.context.properties.issubset(query_context.properties)


class ContextualRuleWorld:
    """
    A world where agents observe context-action pairs and must learn rules.

    Training data contains contexts with actions.
    Test queries ask: "In context X, what action?"

    Compositional queries combine properties in novel ways.
    """

    def __init__(self):
        self.training_data: List[Tuple[Context, str]] = []
        self.ground_truth_rules: List[Rule] = []

    def add_training_example(self, properties: Set[str], action: str):
        """Add a training example."""
        context = Context(properties)
        self.training_data.append((context, action))

    def add_ground_truth_rule(self, properties: Set[str], action: str):
        """Add a ground truth rule (for evaluation only)."""
        rule = Rule(Context(properties), action)
        self.ground_truth_rules.append(rule)

    def generate_compositional_queries(self) -> List[Context]:
        """Generate queries that combine properties in novel ways."""
        # Extract all properties seen in training
        all_properties = set()
        for context, _ in self.training_data:
            all_properties.update(context.properties)

        # Generate combinations not seen in training
        queries = []

        # Single properties
        for prop in all_properties:
            queries.append(Context({prop}))

        # Pairs of properties (compositional)
        props_list = list(all_properties)
        for i in range(len(props_list)):
            for j in range(i+1, len(props_list)):
                queries.append(Context({props_list[i], props_list[j]}))

        return queries

    def evaluate_answer(self, query: Context, predicted_action: str) -> bool:
        """Evaluate if predicted action is correct for query context."""
        # Find applicable ground truth rules
        applicable_rules = [r for r in self.ground_truth_rules if r.applies_to(query)]

        if not applicable_rules:
            # No rule applies - correct answer is None or "no_action"
            return predicted_action in [None, "no_action", "unknown"]

        # Check if prediction matches any applicable rule
        return any(predicted_action == rule.action for rule in applicable_rules)


class PureCompressor:
    """
    Compresses observations by finding shortest rule set.
    Does NOT check for logical consistency.
    Might learn contradictory rules if they compress data well.
    """

    def __init__(self):
        self.rules: List[Rule] = []

    def learn(self, training_data: List[Tuple[Context, str]]):
        """Learn rules from training data by minimizing description length."""
        # Strategy: Greedy rule induction
        # Find most common patterns, create rules

        action_contexts = defaultdict(list)
        for context, action in training_data:
            action_contexts[action].append(context)

        # For each action, find common properties
        for action, contexts in action_contexts.items():
            # Find properties that appear in all contexts for this action
            if not contexts:
                continue

            common_props = set(contexts[0].properties)
            for ctx in contexts[1:]:
                common_props &= ctx.properties

            # If no common properties, take the most frequent
            if not common_props:
                property_counts = defaultdict(int)
                for ctx in contexts:
                    for prop in ctx.properties:
                        property_counts[prop] += 1

                if property_counts:
                    most_common = max(property_counts.items(), key=lambda x: x[1])
                    common_props = {most_common[0]}

            if common_props:
                rule = Rule(Context(common_props), action)
                self.rules.append(rule)

    def predict(self, query: Context) -> str:
        """Predict action for query context."""
        # Find applicable rules
        applicable = [r for r in self.rules if r.applies_to(query)]

        if not applicable:
            return "no_action"

        # If multiple rules apply, return the first (arbitrary)
        return applicable[0].action

    def description_length(self) -> int:
        """Calculate description length (number of rules + properties)."""
        length = len(self.rules)  # Each rule has cost 1
        for rule in self.rules:
            length += len(rule.context.properties)  # Properties have cost
        return length


class CoherentCompressor:
    """
    Compresses observations while enforcing logical consistency.
    Rejects rule sets that would create contradictions.
    Pays description length cost for coherence.
    """

    def __init__(self):
        self.rules: List[Rule] = []
        self.contradiction_constraints: List[Set[str]] = [
            {'sunny', 'rainy'},
            {'hot', 'cold'},
            {'day', 'night'},
            {'wet', 'dry'},
        ]

    def _rules_are_coherent(self, rules: List[Rule]) -> bool:
        """Check if a set of rules is logically coherent."""
        # Check each pair of rules for potential contradiction
        for i, rule1 in enumerate(rules):
            for rule2 in rules[i+1:]:
                # If rules apply to overlapping contexts with different actions
                # AND contexts would contradict, that's incoherent

                combined_props = rule1.context.properties | rule2.context.properties
                combined_ctx = Context(combined_props)

                if not combined_ctx.is_consistent():
                    # Contexts contradict - this is fine as long as they don't
                    # both claim to apply
                    continue

                # If one rule's context contains the other, they must agree on action
                if rule1.context.properties.issubset(rule2.context.properties):
                    if rule1.action != rule2.action:
                        return False

                if rule2.context.properties.issubset(rule1.context.properties):
                    if rule1.action != rule2.action:
                        return False

        return True

    def learn(self, training_data: List[Tuple[Context, str]]):
        """Learn rules while enforcing coherence constraints."""
        # Strategy: Greedy rule induction with coherence checking

        action_contexts = defaultdict(list)
        for context, action in training_data:
            # Only learn from consistent contexts
            if context.is_consistent():
                action_contexts[action].append(context)

        candidate_rules = []

        # Generate candidate rules for each action
        for action, contexts in action_contexts.items():
            if not contexts:
                continue

            # Try to find common properties
            common_props = set(contexts[0].properties)
            for ctx in contexts[1:]:
                common_props &= ctx.properties

            if common_props:
                rule = Rule(Context(common_props), action)
                candidate_rules.append(rule)
            else:
                # Create separate rules for each context
                for ctx in contexts:
                    rule = Rule(ctx, action)
                    candidate_rules.append(rule)

        # Filter rules to maintain coherence
        self.rules = []
        for rule in candidate_rules:
            test_rules = self.rules + [rule]
            if self._rules_are_coherent(test_rules):
                self.rules.append(rule)

    def predict(self, query: Context) -> str:
        """Predict action for query context."""
        # Only make predictions for consistent contexts
        if not query.is_consistent():
            return "inconsistent_context"

        # Find applicable rules
        applicable = [r for r in self.rules if r.applies_to(query)]

        if not applicable:
            return "no_action"

        # If multiple rules apply, they should agree (due to coherence)
        return applicable[0].action

    def description_length(self) -> int:
        """Calculate description length including coherence constraints."""
        length = len(self.rules)
        for rule in self.rules:
            length += len(rule.context.properties)

        # Coherence constraints add to description length
        length += len(self.contradiction_constraints) * 2

        return length


def create_scenario_1():
    """
    Scenario 1: Simple weather-based actions
    Training data has some contexts with implicit contradictions.
    """
    world = ContextualRuleWorld()

    # Training examples (some contexts are contradictory!)
    world.add_training_example({'rainy', 'cold'}, 'umbrella+coat')
    world.add_training_example({'sunny', 'hot'}, 'sunglasses')
    world.add_training_example({'rainy', 'hot'}, 'umbrella')  # Contradiction!
    world.add_training_example({'sunny', 'cold'}, 'sunglasses+coat')  # Contradiction!
    world.add_training_example({'cold'}, 'coat')
    world.add_training_example({'hot'}, 'tshirt')

    # Ground truth rules (consistent)
    world.add_ground_truth_rule({'rainy'}, 'umbrella')
    world.add_ground_truth_rule({'sunny'}, 'sunglasses')
    world.add_ground_truth_rule({'cold'}, 'coat')
    world.add_ground_truth_rule({'hot'}, 'tshirt')

    return world


def run_evaluation():
    """Run evaluation comparing PureCompressor vs CoherentCompressor."""

    print("=" * 60)
    print("CONTEXTUAL RULE WORLD - COHERENT COMPRESSION TEST")
    print("=" * 60)
    print()

    world = create_scenario_1()

    # Train both compressors
    pure = PureCompressor()
    coherent = CoherentCompressor()

    pure.learn(world.training_data)
    coherent.learn(world.training_data)

    print(f"Training data: {len(world.training_data)} examples")
    print(f"PureCompressor learned {len(pure.rules)} rules")
    print(f"CoherentCompressor learned {len(coherent.rules)} rules")
    print()

    # Compare description lengths
    print(f"Description Length:")
    print(f"  Pure: {pure.description_length()}")
    print(f"  Coherent: {coherent.description_length()}")
    print()

    # Test on training data (simple prediction)
    print("Performance on Training Data:")
    pure_correct = 0
    coherent_correct = 0

    for context, actual_action in world.training_data:
        pure_pred = pure.predict(context)
        coherent_pred = coherent.predict(context)

        # Simplistic evaluation - check if action is contained
        if actual_action in pure_pred or pure_pred in actual_action:
            pure_correct += 1
        if actual_action in coherent_pred or coherent_pred in actual_action:
            coherent_correct += 1

    print(f"  Pure: {pure_correct}/{len(world.training_data)} correct")
    print(f"  Coherent: {coherent_correct}/{len(world.training_data)} correct")
    print()

    # Test on compositional queries (novel combinations)
    print("Performance on Compositional Queries:")
    queries = world.generate_compositional_queries()

    pure_comp_correct = 0
    coherent_comp_correct = 0

    print("\nQuery Results:")
    print("-" * 60)

    for query in queries:
        pure_pred = pure.predict(query)
        coherent_pred = coherent.predict(query)

        # Check consistency of query
        is_consistent = query.is_consistent()

        # Evaluate correctness
        pure_ok = world.evaluate_answer(query, pure_pred)
        coherent_ok = world.evaluate_answer(query, coherent_pred)

        if pure_ok:
            pure_comp_correct += 1
        if coherent_ok:
            coherent_comp_correct += 1

        # Print interesting cases
        if not is_consistent or pure_pred != coherent_pred:
            print(f"Query: {query.properties}")
            print(f"  Consistent: {is_consistent}")
            print(f"  Pure → {pure_pred} {'✓' if pure_ok else '✗'}")
            print(f"  Coherent → {coherent_pred} {'✓' if coherent_ok else '✗'}")
            print()

    print("-" * 60)
    print(f"Compositional Query Accuracy:")
    print(f"  Pure: {pure_comp_correct}/{len(queries)} = {100*pure_comp_correct/len(queries):.1f}%")
    print(f"  Coherent: {coherent_comp_correct}/{len(queries)} = {100*coherent_comp_correct/len(queries):.1f}%")
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Trade-off Analysis:")
    print(f"  Pure: Shorter description ({pure.description_length()}), "
          f"but {100*pure_comp_correct/len(queries):.1f}% compositional accuracy")
    print(f"  Coherent: Longer description ({coherent.description_length()}), "
          f"but {100*coherent_comp_correct/len(queries):.1f}% compositional accuracy")
    print()

    if coherent_comp_correct > pure_comp_correct:
        print("RESULT: Coherence constraints IMPROVE compositional reasoning")
        print("Conclusion: Understanding = compression constrained by coherence")
    elif coherent_comp_correct < pure_comp_correct:
        print("RESULT: Coherence constraints HARM compositional reasoning")
        print("Conclusion: Pure compression is sufficient for understanding")
    else:
        print("RESULT: Coherence constraints have NO EFFECT on compositional reasoning")
        print("Conclusion: Coherence is already implicit in good compression")
    print()


if __name__ == "__main__":
    run_evaluation()
