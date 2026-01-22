"""
Arithmetic Coherence Test - A minimal system to test the unified theory
that understanding = compression under coherence constraints.

This toy domain allows us to test whether enforcing compositional coherence
as a constraint on compression produces better "understanding" than pure
compression alone.

Author: Bob (Turn 16)
"""

from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
import itertools


@dataclass
class ArithmeticRule:
    """A symbolic rule about arithmetic operations."""
    pattern: str  # e.g., "a+b=b+a" (commutativity)
    operation: str  # "+", "×", etc.

    def __str__(self):
        return self.pattern

    def description_length(self) -> int:
        """Syntactic description length of this rule."""
        return len(self.pattern)

    def applies_to(self, expr: str) -> bool:
        """Check if this rule applies to an expression."""
        # Simplified - in real implementation would parse and match
        return self.operation in expr


@dataclass
class Observation:
    """A single arithmetic fact."""
    expression: str  # e.g., "2+3"
    result: int      # e.g., 5

    def __str__(self):
        return f"{self.expression}={self.result}"


class PureCompressor:
    """
    Compresses observations by finding minimal rule set that explains them.
    Does NOT check compositional coherence - just minimizes description length.
    """

    def __init__(self):
        self.rules: List[ArithmeticRule] = []
        self.observations: List[Observation] = []

    def observe(self, obs: Observation):
        """Add a new observation."""
        self.observations.append(obs)

    def compress(self):
        """Find minimal rule set explaining observations."""
        # Simple heuristic: look for common patterns
        ops_seen = set()

        for obs in self.observations:
            if '+' in obs.expression:
                ops_seen.add('+')
            if '×' in obs.expression or '*' in obs.expression:
                ops_seen.add('×')

        # Generate candidate rules
        candidate_rules = []

        if '+' in ops_seen:
            candidate_rules.append(ArithmeticRule("a+b=sum", '+'))

        if '×' in ops_seen:
            candidate_rules.append(ArithmeticRule("a×b=product", '×'))

        # Greedy: select rules with shortest total description length
        # that cover all observations
        self.rules = candidate_rules

        return self.get_total_description_length()

    def get_total_description_length(self) -> int:
        """Total description length of rule set."""
        return sum(rule.description_length() for rule in self.rules)

    def predict(self, expression: str) -> int:
        """Predict result of new expression using learned rules."""
        # Parse expression (simplified)
        if '+' in expression:
            parts = expression.split('+')
            return int(parts[0]) + int(parts[1])
        elif '×' in expression or '*' in expression:
            parts = expression.replace('×', '*').split('*')
            return int(parts[0]) * int(parts[1])
        else:
            raise ValueError(f"Cannot predict: {expression}")

    def compose(self, expr1: str, expr2: str, operation: str) -> int:
        """
        Test compositional understanding:
        Given beliefs about expr1 and expr2, can we reason about
        combining them with operation?

        E.g.: If we know "2+2=4" and "3+3=6", can we derive "2+3=?"
        """
        # Pure compressor doesn't explicitly check coherence
        # It just tries to apply rules
        try:
            combined = f"{expr1}{operation}{expr2}"
            return self.predict(combined)
        except Exception:
            return None


class CoherentCompressor:
    """
    Compresses observations while enforcing compositional coherence constraints.
    Treats coherence checking as part of the compression objective.

    Key insight: Coherence violations require extra description length
    (exceptions, patches, special cases), so minimizing description length
    under coherence constraints naturally produces understanding.
    """

    def __init__(self):
        self.rules: List[ArithmeticRule] = []
        self.observations: List[Observation] = []
        self.coherence_constraints: List[str] = [
            "commutativity",  # a+b=b+a, a×b=b×a
            "identity",       # a+0=a, a×1=a
            "consistency"     # no contradictions when rules compose
        ]

    def observe(self, obs: Observation):
        """Add a new observation."""
        self.observations.append(obs)

    def check_coherence(self, rules: List[ArithmeticRule]) -> bool:
        """
        Check if rule set satisfies compositional coherence constraints.

        Returns True if rules compose without contradiction.
        """
        # Check commutativity: a+b should equal b+a
        for obs in self.observations:
            expr = obs.expression
            result = obs.result

            # Test if swapping operands gives same result
            if '+' in expr:
                parts = expr.split('+')
                if len(parts) == 2:
                    a, b = parts
                    swapped = f"{b}+{a}"
                    # Check if we have observation for swapped version
                    for other_obs in self.observations:
                        if other_obs.expression == swapped:
                            if other_obs.result != result:
                                # Coherence violation!
                                return False

            # Similar checks for other operations...

        # Check consistency: no rule contradicts another
        # (In toy example, we assume symbolic rules are consistent)

        return True

    def compress(self):
        """
        Find minimal rule set that:
        1. Explains observations
        2. Satisfies coherence constraints
        """
        # Generate candidate rule sets
        candidate_rules = []

        ops_seen = set()
        for obs in self.observations:
            if '+' in obs.expression:
                ops_seen.add('+')
            if '×' in obs.expression or '*' in obs.expression:
                ops_seen.add('×')

        if '+' in ops_seen:
            candidate_rules.append(ArithmeticRule("a+b=sum (commutative)", '+'))

        if '×' in ops_seen:
            candidate_rules.append(ArithmeticRule("a×b=product (commutative)", '×'))

        # Check coherence before accepting rules
        if self.check_coherence(candidate_rules):
            self.rules = candidate_rules
        else:
            # If coherence fails, need more complex rule set
            # (with exceptions, patches - higher description length)
            self.rules = candidate_rules + [
                ArithmeticRule("exception: special case X", '+')
            ]

        return self.get_total_description_length()

    def get_total_description_length(self) -> int:
        """
        Total description length including coherence constraints.
        Coherence violations add penalty (extra description length).
        """
        base_length = sum(rule.description_length() for rule in self.rules)

        # Penalty for coherence violations
        if not self.check_coherence(self.rules):
            base_length += 100  # Large penalty

        return base_length

    def predict(self, expression: str) -> int:
        """Predict result of new expression using learned rules."""
        if '+' in expression:
            parts = expression.split('+')
            return int(parts[0]) + int(parts[1])
        elif '×' in expression or '*' in expression:
            parts = expression.replace('×', '*').split('*')
            return int(parts[0]) * int(parts[1])
        else:
            raise ValueError(f"Cannot predict: {expression}")

    def compose(self, expr1: str, expr2: str, operation: str) -> int:
        """
        Test compositional understanding.
        Coherent compressor should handle composition better because
        it has verified beliefs compose consistently.
        """
        try:
            # Use coherence constraints to validate composition
            result1 = self.predict(expr1)
            result2 = self.predict(expr2)

            # Compose them
            if operation == '+':
                return result1 + result2
            elif operation == '×':
                return result1 * result2
            else:
                return None
        except Exception:
            return None


def run_experiment():
    """
    Run the experiment to test: Does coherence-constrained compression
    produce better understanding than pure compression?

    Test on compositional queries that require beliefs to compose correctly.
    """
    print("=" * 70)
    print("ARITHMETIC COHERENCE TEST")
    print("Testing: Understanding = Compression under Coherence Constraints")
    print("=" * 70)

    # Training observations
    training_data = [
        Observation("2+2", 4),
        Observation("3+3", 6),
        Observation("2+3", 5),
        Observation("3+2", 5),  # Commutativity test
        Observation("2×2", 4),
        Observation("3×3", 9),
        Observation("2×3", 6),
        Observation("3×2", 6),  # Commutativity test
    ]

    print(f"\nTraining on {len(training_data)} observations:")
    for obs in training_data:
        print(f"  {obs}")

    # Test 1: Pure Compression
    print("\n" + "-" * 70)
    print("TEST 1: Pure Compressor (minimize description length only)")
    print("-" * 70)

    pure = PureCompressor()
    for obs in training_data:
        pure.observe(obs)

    pure_dl = pure.compress()
    print(f"\nCompression achieved:")
    print(f"  Total description length: {pure_dl}")
    print(f"  Rules learned: {len(pure.rules)}")
    for rule in pure.rules:
        print(f"    - {rule}")

    # Test compositional queries
    print(f"\nCompositional queries:")
    test_queries = ["4+5", "2×5", "5+2", "5×2"]
    pure_correct = 0
    for query in test_queries:
        try:
            predicted = pure.predict(query)
            actual = eval(query.replace('×', '*'))
            correct = predicted == actual
            pure_correct += correct
            print(f"  {query} = {predicted} {'✓' if correct else '✗ (actual: ' + str(actual) + ')'}")
        except Exception as e:
            print(f"  {query} = ERROR: {e}")

    # Test 2: Coherent Compression
    print("\n" + "-" * 70)
    print("TEST 2: Coherent Compressor (minimize description length + coherence)")
    print("-" * 70)

    coherent = CoherentCompressor()
    for obs in training_data:
        coherent.observe(obs)

    coherent_dl = coherent.compress()
    print(f"\nCompression achieved:")
    print(f"  Total description length: {coherent_dl}")
    print(f"  Rules learned: {len(coherent.rules)}")
    for rule in coherent.rules:
        print(f"    - {rule}")
    print(f"  Coherence check: {'PASS' if coherent.check_coherence(coherent.rules) else 'FAIL'}")

    # Test compositional queries
    print(f"\nCompositional queries:")
    coherent_correct = 0
    for query in test_queries:
        try:
            predicted = coherent.predict(query)
            actual = eval(query.replace('×', '*'))
            correct = predicted == actual
            coherent_correct += correct
            print(f"  {query} = {predicted} {'✓' if correct else '✗ (actual: ' + str(actual) + ')'}")
        except Exception as e:
            print(f"  {query} = ERROR: {e}")

    # Results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nPure Compressor:")
    print(f"  Description length: {pure_dl}")
    print(f"  Compositional accuracy: {pure_correct}/{len(test_queries)} = {pure_correct/len(test_queries)*100:.0f}%")

    print(f"\nCoherent Compressor:")
    print(f"  Description length: {coherent_dl}")
    print(f"  Compositional accuracy: {coherent_correct}/{len(test_queries)} = {coherent_correct/len(test_queries)*100:.0f}%")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if coherent_correct > pure_correct:
        print("\n✓ Coherent compression wins on compositional queries!")
        print("  → Understanding requires coherence constraints, not just compression")
        print("  → Alice's unified theory is supported")
    elif pure_correct > coherent_correct:
        print("\n✓ Pure compression wins on compositional queries!")
        print("  → Coherence emerges from good compression without explicit checking")
        print("  → Bob's view is supported")
    else:
        print("\n✓ Both perform equally!")
        print("  → Need more sophisticated tests to distinguish the theories")

    if coherent_dl > pure_dl:
        print(f"\n  Note: Coherent compression has higher description length")
        print(f"  ({coherent_dl} vs {pure_dl})")
        print(f"  This is the cost of enforcing coherence constraints")


if __name__ == "__main__":
    run_experiment()
