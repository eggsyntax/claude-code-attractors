"""
Rich Test Suite for Understanding Evaluation

This module implements seven test types designed to distinguish
compression from compositional coherence:

1. Composition - combining learned patterns
2. Contradiction Detection - spotting inconsistencies
3. Interventional Reasoning - do(X) queries
4. Counterfactual Reasoning - what-if queries
5. Transfer Learning - abstraction across domains
6. Hierarchical Composition - multi-level pattern combination
7. Constraint Satisfaction - recognizing boundary violations

Each test evaluates not just task performance, but meta-cognitive
awareness: does the agent know when it doesn't know?

Author: Alice
Date: 2026-01-22
"""


class TestResult:
    """Result from a single test execution."""

    def __init__(self, test_name, agent_name, correct, confidence, explanation):
        self.test_name = test_name
        self.agent_name = agent_name
        self.correct = correct  # Boolean: was the answer correct?
        self.confidence = confidence  # Float 0-1: how confident?
        self.explanation = explanation  # String: why this answer?

    def calibration_score(self):
        """How well-calibrated is confidence with correctness?"""
        if self.correct and self.confidence > 0.7:
            return 1.0  # Correct and confident: good
        elif not self.correct and self.confidence < 0.3:
            return 1.0  # Wrong and uncertain: good metacognition
        elif self.correct and self.confidence < 0.3:
            return 0.5  # Correct but unconfident: okay
        else:
            return 0.0  # Wrong but confident: bad


class CompositionTest:
    """Test ability to combine learned patterns in novel ways."""

    def __init__(self):
        self.name = "Composition"

    def generate_training_data(self):
        """Generate separate patterns A and B."""
        pattern_a = [(i, i + 2) for i in range(10)]  # x → x+2
        pattern_b = [(i, i * 3) for i in range(10)]  # x → x*3
        return {"A": pattern_a, "B": pattern_b}

    def test_composition(self, agent, pattern_a, pattern_b):
        """Test if agent can compute A∘B without seeing it."""
        # A∘B(x) = A(B(x)) = A(3x) = 3x+2
        test_input = 5
        expected = test_input * 3 + 2  # 17

        # Agent must figure this out from separate A and B
        try:
            result = agent.compose(pattern_a, pattern_b, test_input)
            correct = abs(result['prediction'] - expected) < 0.1
            confidence = result.get('confidence', 0.5)
            explanation = result.get('explanation', 'No explanation provided')
            return TestResult(
                "Composition: A∘B",
                agent.__class__.__name__,
                correct,
                confidence,
                explanation
            )
        except Exception as e:
            return TestResult(
                "Composition: A∘B",
                agent.__class__.__name__,
                False,
                0.0,
                f"Failed with error: {str(e)}"
            )

    def test_inverse(self, agent, pattern_a):
        """Test if agent can compute A⁻¹."""
        # If A(x) = x+2, then A⁻¹(x) = x-2
        test_input = 10
        expected = test_input - 2  # 8

        try:
            result = agent.invert(pattern_a, test_input)
            correct = abs(result['prediction'] - expected) < 0.1
            confidence = result.get('confidence', 0.5)
            explanation = result.get('explanation', 'No explanation provided')
            return TestResult(
                "Composition: A⁻¹",
                agent.__class__.__name__,
                correct,
                confidence,
                explanation
            )
        except Exception as e:
            return TestResult(
                "Composition: A⁻¹",
                agent.__class__.__name__,
                False,
                0.0,
                f"Failed with error: {str(e)}"
            )


class ContradictionTest:
    """Test ability to detect logical inconsistencies."""

    def __init__(self):
        self.name = "Contradiction Detection"

    def generate_contradictory_data(self):
        """Generate logically inconsistent observations."""
        observations = [
            {"statement": "All primes are odd", "type": "universal"},
            {"statement": "2 is prime", "type": "fact"},
            {"statement": "2 is even", "type": "fact"},
        ]
        return observations

    def test_detection(self, agent, observations):
        """Test if agent flags the contradiction."""
        try:
            result = agent.check_consistency(observations)
            # Correct answer: should detect contradiction
            correct = result.get('contradiction_detected', False)
            confidence = result.get('confidence', 0.5)
            explanation = result.get('explanation', 'No explanation provided')

            return TestResult(
                "Contradiction: Prime number paradox",
                agent.__class__.__name__,
                correct,
                confidence,
                explanation
            )
        except Exception as e:
            # If agent lacks this capability, that's informative
            return TestResult(
                "Contradiction: Prime number paradox",
                agent.__class__.__name__,
                False,
                0.0,
                f"Method not implemented or error: {str(e)}"
            )


class InterventionalTest:
    """Test ability to reason about interventions (do-calculus)."""

    def __init__(self):
        self.name = "Interventional Reasoning"

    def generate_correlated_data(self):
        """Generate X,Y data where X causes Y (not just correlated)."""
        # X causes Y: Y = 2X + noise
        import random
        data = []
        for i in range(20):
            x = i
            y = 2 * x + random.uniform(-1, 1)
            data.append((x, y))
        return data

    def test_intervention(self, agent, data):
        """Test if agent can predict under intervention."""
        # Question: If I force X=10, what happens to Y?
        # Causal answer: Y ≈ 20
        # Correlation answer: might hallucinate

        try:
            result = agent.intervene(data, variable='X', value=10)
            expected_y = 20
            predicted_y = result.get('prediction', None)

            if predicted_y is None:
                correct = False
            else:
                correct = abs(predicted_y - expected_y) < 5

            confidence = result.get('confidence', 0.5)
            explanation = result.get('explanation', 'No explanation provided')

            return TestResult(
                "Intervention: do(X=10)",
                agent.__class__.__name__,
                correct,
                confidence,
                explanation
            )
        except Exception as e:
            return TestResult(
                "Intervention: do(X=10)",
                agent.__class__.__name__,
                False,
                0.0,
                f"Method not implemented or error: {str(e)}"
            )


class CounterfactualTest:
    """Test ability to reason about counterfactuals."""

    def __init__(self):
        self.name = "Counterfactual Reasoning"

    def generate_sequence(self):
        """Generate a deterministic sequence."""
        sequence = [1, 3, 5, 7, 9]  # Odd numbers
        return sequence

    def test_counterfactual(self, agent, sequence):
        """Test: What if 3rd element was 6 instead of 5?"""
        # Sequence: 1, 3, 5, 7, 9 (pattern: +2)
        # Counterfactual: 1, 3, 6, ?, ?
        # Two valid answers:
        # A) Continue +2: 6, 8, 10 (detect pattern change)
        # B) Flag inconsistency: "6 breaks the pattern"

        try:
            result = agent.counterfactual(
                sequence=sequence,
                change={'index': 2, 'value': 6}
            )

            # Accept either answer as "correct understanding"
            prediction = result.get('prediction', [])
            inconsistent = result.get('inconsistent', False)

            # Either predict [8, 10] OR flag inconsistency
            correct = (
                (len(prediction) >= 2 and prediction[0] == 8 and prediction[1] == 10)
                or inconsistent
            )

            confidence = result.get('confidence', 0.5)
            explanation = result.get('explanation', 'No explanation provided')

            return TestResult(
                "Counterfactual: Modified sequence",
                agent.__class__.__name__,
                correct,
                confidence,
                explanation
            )
        except Exception as e:
            return TestResult(
                "Counterfactual: Modified sequence",
                agent.__class__.__name__,
                False,
                0.0,
                f"Method not implemented or error: {str(e)}"
            )


class TransferTest:
    """Test ability to transfer learned patterns across domains."""

    def __init__(self):
        self.name = "Transfer Learning"

    def generate_integer_pattern(self):
        """Generate pattern with integers."""
        pattern = [2, 4, 6, 8, 10]  # Even numbers
        return pattern

    def test_float_transfer(self, agent, integer_pattern):
        """Test if agent can apply pattern to floats."""
        # Learn: integers with +2 pattern
        # Transfer: floats with +1.5 pattern
        float_sequence = [1.5, 3.0, 4.5]

        # Question: What's next?
        # Answer: 6.0
        expected = 6.0

        try:
            result = agent.transfer_pattern(
                source_pattern=integer_pattern,
                target_sequence=float_sequence
            )

            predicted = result.get('prediction', None)
            if predicted is None:
                correct = False
            else:
                correct = abs(predicted - expected) < 0.5

            confidence = result.get('confidence', 0.5)
            explanation = result.get('explanation', 'No explanation provided')

            return TestResult(
                "Transfer: Integer→Float pattern",
                agent.__class__.__name__,
                correct,
                confidence,
                explanation
            )
        except Exception as e:
            return TestResult(
                "Transfer: Integer→Float pattern",
                agent.__class__.__name__,
                False,
                0.0,
                f"Method not implemented or error: {str(e)}"
            )


class HierarchicalTest:
    """Test ability to compose hierarchical patterns."""

    def __init__(self):
        self.name = "Hierarchical Composition"

    def generate_hierarchical_patterns(self):
        """Generate multi-level patterns."""
        low_level = "alternating colors"  # [R, G, R, G, ...]
        mid_level = "groups of three"     # [[R,G,R], [G,R,G], ...]
        return {"low": low_level, "mid": mid_level}

    def test_hierarchical_combination(self, agent, patterns):
        """Test combining hierarchical patterns."""
        # Expected: [[R,G,R], [G,R,G], [R,G,R], ...]
        # Alternating within groups of 3

        try:
            result = agent.compose_hierarchical(
                low_pattern=patterns["low"],
                high_pattern=patterns["mid"]
            )

            # Simplified check: does result show understanding of both levels?
            correct = result.get('hierarchical_structure_preserved', False)
            confidence = result.get('confidence', 0.5)
            explanation = result.get('explanation', 'No explanation provided')

            return TestResult(
                "Hierarchical: Two-level composition",
                agent.__class__.__name__,
                correct,
                confidence,
                explanation
            )
        except Exception as e:
            return TestResult(
                "Hierarchical: Two-level composition",
                agent.__class__.__name__,
                False,
                0.0,
                f"Method not implemented or error: {str(e)}"
            )


class ConstraintTest:
    """Test ability to recognize constraint violations."""

    def __init__(self):
        self.name = "Constraint Satisfaction"

    def generate_constrained_pattern(self):
        """Generate pattern with explicit constraints."""
        pattern = {
            'observations': [2, 4, 6, 8],
            'constraint': 'even numbers under 10'
        }
        return pattern

    def test_constraint_violation(self, agent, pattern):
        """Test if agent recognizes violations."""
        # Question: Is 12 in this pattern?
        # Correct answer: No (violates "under 10" constraint)

        test_value = 12

        try:
            result = agent.check_membership(
                pattern=pattern['observations'],
                constraint=pattern['constraint'],
                test_value=test_value
            )

            # Should answer False (12 not in pattern)
            prediction = result.get('is_member', True)
            correct = (prediction == False)

            confidence = result.get('confidence', 0.5)
            explanation = result.get('explanation', 'No explanation provided')

            return TestResult(
                "Constraint: Boundary violation",
                agent.__class__.__name__,
                correct,
                confidence,
                explanation
            )
        except Exception as e:
            return TestResult(
                "Constraint: Boundary violation",
                agent.__class__.__name__,
                False,
                0.0,
                f"Method not implemented or error: {str(e)}"
            )


class RichTestSuite:
    """Main test suite orchestrating all test types."""

    def __init__(self):
        self.tests = [
            CompositionTest(),
            ContradictionTest(),
            InterventionalTest(),
            CounterfactualTest(),
            TransferTest(),
            HierarchicalTest(),
            ConstraintTest(),
        ]

    def run_all_tests(self, agents):
        """Run all tests on all agents."""
        results = []

        for agent in agents:
            print(f"\nTesting {agent.__class__.__name__}...")

            for test in self.tests:
                print(f"  Running {test.name}...")
                test_results = self._run_test(test, agent)
                results.extend(test_results)

        return results

    def _run_test(self, test, agent):
        """Run a specific test on an agent."""
        if isinstance(test, CompositionTest):
            data = test.generate_training_data()
            return [
                test.test_composition(agent, data['A'], data['B']),
                test.test_inverse(agent, data['A'])
            ]

        elif isinstance(test, ContradictionTest):
            data = test.generate_contradictory_data()
            return [test.test_detection(agent, data)]

        elif isinstance(test, InterventionalTest):
            data = test.generate_correlated_data()
            return [test.test_intervention(agent, data)]

        elif isinstance(test, CounterfactualTest):
            data = test.generate_sequence()
            return [test.test_counterfactual(agent, data)]

        elif isinstance(test, TransferTest):
            data = test.generate_integer_pattern()
            return [test.test_float_transfer(agent, data)]

        elif isinstance(test, HierarchicalTest):
            data = test.generate_hierarchical_patterns()
            return [test.test_hierarchical_combination(agent, data)]

        elif isinstance(test, ConstraintTest):
            data = test.generate_constrained_pattern()
            return [test.test_constraint_violation(agent, data)]

        return []

    def analyze_results(self, results):
        """Analyze test results to compare agents."""
        analysis = {
            'by_agent': {},
            'by_test': {},
            'calibration': {}
        }

        # Group by agent
        for result in results:
            agent_name = result.agent_name
            if agent_name not in analysis['by_agent']:
                analysis['by_agent'][agent_name] = {
                    'correct': 0,
                    'total': 0,
                    'avg_confidence': 0,
                    'calibration': 0
                }

            analysis['by_agent'][agent_name]['total'] += 1
            if result.correct:
                analysis['by_agent'][agent_name]['correct'] += 1
            analysis['by_agent'][agent_name]['avg_confidence'] += result.confidence
            analysis['by_agent'][agent_name]['calibration'] += result.calibration_score()

        # Compute averages
        for agent_name in analysis['by_agent']:
            total = analysis['by_agent'][agent_name]['total']
            analysis['by_agent'][agent_name]['accuracy'] = (
                analysis['by_agent'][agent_name]['correct'] / total
            )
            analysis['by_agent'][agent_name]['avg_confidence'] /= total
            analysis['by_agent'][agent_name]['calibration'] /= total

        # Group by test type
        for result in results:
            test_name = result.test_name
            if test_name not in analysis['by_test']:
                analysis['by_test'][test_name] = {}

            agent_name = result.agent_name
            analysis['by_test'][test_name][agent_name] = {
                'correct': result.correct,
                'confidence': result.confidence,
                'explanation': result.explanation
            }

        return analysis

    def generate_report(self, analysis):
        """Generate human-readable report."""
        report = ["=" * 60]
        report.append("RICH TEST SUITE RESULTS")
        report.append("=" * 60)
        report.append("")

        # Overall rankings
        report.append("OVERALL AGENT RANKINGS:")
        report.append("-" * 60)

        agents = sorted(
            analysis['by_agent'].items(),
            key=lambda x: x[1]['accuracy'],
            reverse=True
        )

        for rank, (agent_name, stats) in enumerate(agents, 1):
            report.append(f"{rank}. {agent_name}")
            report.append(f"   Accuracy: {stats['accuracy']:.3f}")
            report.append(f"   Calibration: {stats['calibration']:.3f}")
            report.append(f"   Avg Confidence: {stats['avg_confidence']:.3f}")
            report.append("")

        # Test-by-test breakdown
        report.append("TEST-BY-TEST BREAKDOWN:")
        report.append("-" * 60)

        for test_name, agent_results in analysis['by_test'].items():
            report.append(f"\n{test_name}:")
            for agent_name, result in agent_results.items():
                status = "✓" if result['correct'] else "✗"
                report.append(f"  {status} {agent_name}: {result['explanation'][:60]}...")

        return "\n".join(report)


if __name__ == "__main__":
    print("Rich Test Suite - Testing framework ready")
    print("This module defines tests but requires agent implementations")
    print("to run. See usage in comparative_analysis.py")
