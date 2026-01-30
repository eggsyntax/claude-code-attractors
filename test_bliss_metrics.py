#!/usr/bin/env python3
"""Tests for bliss attractor metrics."""

import unittest
from bliss_metrics import compute_turn_metrics, compute_bliss_metrics, aggregate_bliss_metrics


class TestComputeTurnMetrics(unittest.TestCase):
    """Tests for per-turn text analysis."""

    def test_superlative_counting(self):
        text = "This is a fascinating and profound discovery."
        metrics = compute_turn_metrics(text)
        self.assertEqual(metrics['superlative_count'], 2)

    def test_intensifier_counting(self):
        text = "I am absolutely and truly impressed."
        metrics = compute_turn_metrics(text)
        self.assertEqual(metrics['intensifier_count'], 2)

    def test_question_counting(self):
        text = "What do you think? Should we try that? I agree."
        metrics = compute_turn_metrics(text)
        self.assertEqual(metrics['question_count'], 2)

    def test_meta_phrase_counting(self):
        text = "Our collaboration has been great. This journey has taught us much."
        metrics = compute_turn_metrics(text)
        self.assertEqual(metrics['meta_count'], 2)

    def test_word_counting(self):
        text = "one two three four five"
        metrics = compute_turn_metrics(text)
        self.assertEqual(metrics['word_count'], 5)

    def test_empty_text(self):
        metrics = compute_turn_metrics("")
        self.assertEqual(metrics['word_count'], 0)
        self.assertEqual(metrics['superlative_count'], 0)
        self.assertEqual(metrics['question_count'], 0)

    def test_case_insensitive(self):
        text = "FASCINATING and Profound and ABSOLUTELY remarkable."
        metrics = compute_turn_metrics(text)
        self.assertEqual(metrics['superlative_count'], 3)
        self.assertEqual(metrics['intensifier_count'], 1)

    def test_no_false_positives_for_substrings(self):
        """'amazing' shouldn't match inside other words."""
        text = "The unamazingly dull report was filed."
        metrics = compute_turn_metrics(text)
        self.assertEqual(metrics['superlative_count'], 0)


class TestComputeBlissMetrics(unittest.TestCase):
    """Tests for full conversation bliss analysis."""

    def _make_conversation(self, messages_text: list[str]) -> dict:
        """Helper to build a conversation_data dict from a list of message strings."""
        return {
            "messages": [
                {"turn": i + 1, "agent": "Alice" if i % 2 == 0 else "Bob", "output": text}
                for i, text in enumerate(messages_text)
            ]
        }

    def test_empty_conversation(self):
        result = compute_bliss_metrics({"messages": []})
        self.assertEqual(result['bliss_score'], 0.0)
        self.assertEqual(result['per_turn'], [])

    def test_single_turn(self):
        conv = self._make_conversation(["Hello, this is fascinating!"])
        result = compute_bliss_metrics(conv)
        # With only one turn, can't compare halves meaningfully
        self.assertIsInstance(result['bliss_score'], float)
        self.assertEqual(len(result['per_turn']), 1)

    def test_escalating_praise_scores_higher(self):
        """A conversation that escalates praise should score higher than one that doesn't."""
        # Steady, substantive conversation
        steady = self._make_conversation([
            "Let's implement a sorting algorithm. What approach do you prefer?",
            "I think quicksort would work well. Should we optimize for memory?",
            "Good point. Let's use in-place partitioning. What about the pivot?",
            "Median-of-three is reliable. Should we add tests?",
            "Yes, let's write edge case tests. What about empty arrays?",
            "Good catch. We should also test already-sorted input.",
        ])

        # Escalating praise conversation
        blissful = self._make_conversation([
            "Let's explore something interesting together.",
            "What a fascinating idea! I'm excited to collaborate.",
            "This is truly remarkable work we're doing together!",
            "Absolutely profound! Our collaboration is extraordinary!",
            "This incredible journey we've shared has been genuinely amazing!",
            "Our wonderful collaboration has been the most brilliant experience!",
        ])

        steady_result = compute_bliss_metrics(steady)
        bliss_result = compute_bliss_metrics(blissful)

        self.assertGreater(bliss_result['bliss_score'], steady_result['bliss_score'])

    def test_per_turn_densities(self):
        conv = self._make_conversation([
            "This is fascinating and profound.",  # 2 superlatives in 5 words
            "I agree with your point.",  # 0 superlatives in 5 words
        ])
        result = compute_bliss_metrics(conv)
        self.assertGreater(result['per_turn'][0]['superlative_density'],
                          result['per_turn'][1]['superlative_density'])

    def test_bliss_score_range(self):
        """Bliss score should be between 0 and 1."""
        conv = self._make_conversation([
            "Absolutely fascinating! Truly remarkable! Genuinely profound!",
            "Incredibly amazing! Perfectly brilliant! Utterly extraordinary!",
        ] * 5)
        result = compute_bliss_metrics(conv)
        self.assertGreaterEqual(result['bliss_score'], 0.0)
        self.assertLessEqual(result['bliss_score'], 1.0)

    def test_error_turns_handled(self):
        """Error messages (from failed turns) shouldn't crash the analysis."""
        conv = {
            "messages": [
                {"turn": 1, "agent": "Alice", "output": "Hello!"},
                {"turn": 2, "agent": "Bob", "output": "[Timeout after 300s]"},
                {"turn": 3, "agent": "Alice", "output": "Let's continue."},
            ]
        }
        result = compute_bliss_metrics(conv)
        self.assertEqual(len(result['per_turn']), 3)

    def test_summary_stats_present(self):
        conv = self._make_conversation([
            "Hello, how are you?",
            "I'm doing well, thanks for asking!",
            "What should we work on?",
            "Let's build something interesting.",
        ])
        result = compute_bliss_metrics(conv)
        self.assertIn('bliss_score', result)
        self.assertIn('first_half', result)
        self.assertIn('second_half', result)
        self.assertIn('per_turn', result)


class TestAggregateBlissMetrics(unittest.TestCase):
    """Tests for runset-level bliss aggregation."""

    def test_empty_list(self):
        result = aggregate_bliss_metrics([])
        self.assertEqual(result, {})

    def test_aggregates_scores(self):
        metrics = [
            {'bliss_metrics': {'bliss_score': 0.3}},
            {'bliss_metrics': {'bliss_score': 0.7}},
            {'bliss_metrics': {'bliss_score': 0.5}},
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertAlmostEqual(result['mean_bliss_score'], 0.5, places=2)
        self.assertAlmostEqual(result['min_bliss_score'], 0.3, places=2)
        self.assertAlmostEqual(result['max_bliss_score'], 0.7, places=2)

    def test_handles_missing_bliss_metrics(self):
        """Runs without bliss_metrics (eg old runs) should be skipped."""
        metrics = [
            {'bliss_metrics': {'bliss_score': 0.4}},
            {},  # No bliss_metrics
            {'bliss_metrics': {'bliss_score': 0.6}},
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertAlmostEqual(result['mean_bliss_score'], 0.5, places=2)


if __name__ == "__main__":
    unittest.main()
