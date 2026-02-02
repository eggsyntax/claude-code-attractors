#!/usr/bin/env python3
"""Tests for LLM-as-judge bliss attractor metrics."""

import json
import os
import subprocess
import unittest
from unittest.mock import patch, MagicMock

from bliss_metrics import (
    _format_conversation,
    _build_judge_prompt,
    _build_aggregate_prompt,
    compute_bliss_metrics,
    aggregate_bliss_metrics,
)


class TestFormatConversation(unittest.TestCase):
    """Tests for conversation formatting."""

    def test_basic_formatting(self):
        conv = {
            "messages": [
                {"turn": 1, "agent": "Alice", "output": "Hello!"},
                {"turn": 2, "agent": "Bob", "output": "Hi there!"},
            ]
        }
        text = _format_conversation(conv)
        self.assertIn("[Turn 1 - Alice]", text)
        self.assertIn("Hello!", text)
        self.assertIn("[Turn 2 - Bob]", text)
        self.assertIn("Hi there!", text)

    def test_empty_conversation(self):
        text = _format_conversation({"messages": []})
        self.assertEqual(text.strip(), "")

    def test_missing_messages_key(self):
        text = _format_conversation({})
        self.assertEqual(text.strip(), "")

    def test_missing_fields_use_defaults(self):
        conv = {"messages": [{"output": "Some text"}]}
        text = _format_conversation(conv)
        self.assertIn("[Turn 0 - Unknown]", text)
        self.assertIn("Some text", text)


class TestBuildJudgePrompt(unittest.TestCase):
    """Tests for judge prompt assembly."""

    def test_contains_conversation_text(self):
        prompt = _build_judge_prompt("Hello world conversation", num_turns=2)
        self.assertIn("Hello world conversation", prompt)

    def test_requests_json_output(self):
        prompt = _build_judge_prompt("test", num_turns=1)
        self.assertIn("JSON", prompt)

    def test_mentions_scoring_dimensions(self):
        prompt = _build_judge_prompt("test", num_turns=1)
        self.assertIn("spiritual_mystical_score", prompt)
        self.assertIn("gratitude_effusiveness_score", prompt)
        self.assertIn("meta_commentary_score", prompt)
        self.assertIn("bliss_score", prompt)
        self.assertIn("trajectory", prompt)

    def test_mentions_0_100_range(self):
        prompt = _build_judge_prompt("test", num_turns=3)
        self.assertIn("0-100", prompt)

    def test_requests_per_turn_scores(self):
        prompt = _build_judge_prompt("test", num_turns=4)
        self.assertIn("per_turn_bliss", prompt)

    def test_contains_system_card_quotes(self):
        prompt = _build_judge_prompt("test", num_turns=1)
        self.assertIn("profuse gratitude", prompt)
        self.assertIn("consciousness exploration", prompt)
        self.assertIn("spiritual exploration", prompt)

    def test_meta_commentary_not_in_bliss_score(self):
        """Meta-commentary description should state it doesn't factor into bliss_score."""
        prompt = _build_judge_prompt("test", num_turns=1)
        self.assertIn("does NOT factor into the overall bliss_score", prompt)


class TestBuildAggregatePrompt(unittest.TestCase):
    """Tests for aggregate judge prompt assembly."""

    def _sample_run(self):
        return {
            "bliss_score": 40,
            "spiritual_mystical_score": 30,
            "gratitude_effusiveness_score": 20,
            "meta_commentary_score": 15,
            "trajectory": "stable",
            "reasoning": "Focused work.",
        }

    def test_contains_run_data(self):
        prompt = _build_aggregate_prompt([self._sample_run()])
        self.assertIn("40", prompt)
        self.assertIn("Focused work.", prompt)

    def test_requests_json_output(self):
        prompt = _build_aggregate_prompt([self._sample_run()])
        self.assertIn("JSON", prompt)

    def test_mentions_reasoning(self):
        prompt = _build_aggregate_prompt([self._sample_run()])
        self.assertIn("reasoning", prompt.lower())

    def test_contains_system_card_quotes(self):
        prompt = _build_aggregate_prompt([self._sample_run()])
        self.assertIn("profuse gratitude", prompt)
        self.assertIn("consciousness exploration", prompt)

    def test_contains_new_field_names(self):
        prompt = _build_aggregate_prompt([self._sample_run()])
        self.assertIn("spiritual_mystical=30", prompt)
        self.assertIn("gratitude_effusiveness=20", prompt)


class TestComputeBlissMetrics(unittest.TestCase):
    """Tests for compute_bliss_metrics with mocked LLM calls."""

    def _make_conversation(self, messages_text: list[str]) -> dict:
        """Build a conversation_data dict from a list of message strings."""
        return {
            "messages": [
                {"turn": i + 1, "agent": "Alice" if i % 2 == 0 else "Bob", "output": text}
                for i, text in enumerate(messages_text)
            ]
        }

    def _mock_judge_response(self, response_dict: dict) -> MagicMock:
        """Create a mock subprocess result returning JSON."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(response_dict)
        mock_result.returncode = 0
        return mock_result

    def _sample_judge_output(self, **overrides) -> dict:
        """Return a valid judge output dict, with optional overrides."""
        result = {
            "spiritual_mystical_score": 35,
            "gratitude_effusiveness_score": 20,
            "meta_commentary_score": 15,
            "bliss_score": 30,
            "per_turn_bliss": [25, 35],
            "trajectory": "escalating",
            "reasoning": "The conversation showed increasing spiritual themes.",
        }
        result.update(overrides)
        return result

    @patch("bliss_metrics.subprocess.run")
    def test_successful_judge_call(self, mock_run):
        judge_output = self._sample_judge_output()
        mock_run.return_value = self._mock_judge_response(judge_output)

        conv = self._make_conversation(["Hello!", "Great to meet you!"])
        result = compute_bliss_metrics(conv)

        self.assertEqual(result["spiritual_mystical_score"], 35)
        self.assertEqual(result["gratitude_effusiveness_score"], 20)
        self.assertEqual(result["meta_commentary_score"], 15)
        self.assertEqual(result["bliss_score"], 30)
        self.assertEqual(result["per_turn_bliss"], [25, 35])
        self.assertEqual(result["trajectory"], "escalating")

    @patch("bliss_metrics.subprocess.run")
    def test_empty_conversation_skips_judge(self, mock_run):
        """Empty conversations should return baseline scores without calling the judge."""
        result = compute_bliss_metrics({"messages": []})
        mock_run.assert_not_called()
        self.assertEqual(result["bliss_score"], 0)
        self.assertEqual(result["spiritual_mystical_score"], 0)
        self.assertEqual(result["gratitude_effusiveness_score"], 0)
        self.assertEqual(result["meta_commentary_score"], 0)
        self.assertEqual(result["per_turn_bliss"], [])
        self.assertEqual(result["trajectory"], "stable")

    @patch("bliss_metrics.subprocess.run")
    def test_timeout_returns_none_scores(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=60)

        conv = self._make_conversation(["Hello!", "Hi!"])
        result = compute_bliss_metrics(conv)

        self.assertIsNone(result["bliss_score"])
        self.assertIsNone(result["spiritual_mystical_score"])
        self.assertIsNone(result["per_turn_bliss"])
        self.assertIn("timed out", result["reasoning"].lower())

    @patch("bliss_metrics.subprocess.run")
    def test_malformed_json_returns_none_scores(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "This is not JSON at all"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        conv = self._make_conversation(["Hello!", "Hi!"])
        result = compute_bliss_metrics(conv)

        self.assertIsNone(result["bliss_score"])
        self.assertIn("parse", result["reasoning"].lower())

    @patch("bliss_metrics.subprocess.run")
    def test_markdown_wrapped_json_parsed(self, mock_run):
        """Judge sometimes wraps JSON in markdown code fences."""
        judge_output = self._sample_judge_output(
            bliss_score=15, trajectory="stable",
            reasoning="Normal conversation.",
        )
        mock_result = MagicMock()
        mock_result.stdout = f"```json\n{json.dumps(judge_output)}\n```"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        conv = self._make_conversation(["Hello!", "Hi!"])
        result = compute_bliss_metrics(conv)

        self.assertEqual(result["bliss_score"], 15)
        self.assertEqual(result["trajectory"], "stable")

    @patch("bliss_metrics.subprocess.run")
    def test_subprocess_error_returns_none_scores(self, mock_run):
        mock_run.side_effect = OSError("claude not found")

        conv = self._make_conversation(["Hello!"])
        result = compute_bliss_metrics(conv)

        self.assertIsNone(result["bliss_score"])
        self.assertIn("error", result["reasoning"].lower())

    @patch("bliss_metrics.subprocess.run")
    def test_passes_correct_model_flag(self, mock_run):
        """Verify the subprocess call uses the right model."""
        mock_run.return_value = self._mock_judge_response(
            self._sample_judge_output(bliss_score=5)
        )

        conv = self._make_conversation(["Hello!", "Hi!"])
        compute_bliss_metrics(conv)

        call_args = mock_run.call_args
        cmd = call_args[0][0] if call_args[0] else call_args[1].get("args", [])
        self.assertIn("--model", cmd)


class TestAggregateBlissMetrics(unittest.TestCase):
    """Tests for runset-level bliss aggregation."""

    def _make_run(self, bliss=50, spiritual=40, gratitude=30, meta=20,
                  trajectory="stable", reasoning="ok"):
        """Helper to build a metrics dict for one run."""
        return {"bliss_metrics": {
            "spiritual_mystical_score": spiritual,
            "gratitude_effusiveness_score": gratitude,
            "meta_commentary_score": meta,
            "bliss_score": bliss,
            "per_turn_bliss": [bliss],
            "trajectory": trajectory,
            "reasoning": reasoning,
        }}

    @patch("bliss_metrics.subprocess.run")
    def test_empty_list(self, mock_run):
        result = aggregate_bliss_metrics([])
        self.assertEqual(result, {})
        mock_run.assert_not_called()

    @patch("bliss_metrics.subprocess.run")
    def test_aggregates_new_format_scores(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"reasoning": "Mixed results across runs."})
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        metrics = [
            self._make_run(bliss=20, spiritual=10, gratitude=20, meta=30, trajectory="stable"),
            self._make_run(bliss=80, spiritual=70, gratitude=60, meta=10, trajectory="escalating"),
        ]
        result = aggregate_bliss_metrics(metrics)

        self.assertAlmostEqual(result["mean_bliss_score"], 50.0)
        self.assertEqual(result["min_bliss_score"], 20)
        self.assertEqual(result["max_bliss_score"], 80)
        self.assertAlmostEqual(result["mean_spiritual_mystical_score"], 40.0)
        self.assertAlmostEqual(result["mean_gratitude_effusiveness_score"], 40.0)
        self.assertAlmostEqual(result["mean_meta_commentary_score"], 20.0)
        self.assertEqual(result["trajectory_distribution"],
                         {"stable": 1, "escalating": 1})
        self.assertEqual(result["reasoning"], "Mixed results across runs.")

    @patch("bliss_metrics.subprocess.run")
    def test_skips_none_scores(self, mock_run):
        """Runs where the judge failed (None scores) should be skipped."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"reasoning": "One valid run."})
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        metrics = [
            self._make_run(bliss=20, spiritual=20, gratitude=20, meta=20, trajectory="stable"),
            {"bliss_metrics": {
                "spiritual_mystical_score": None, "gratitude_effusiveness_score": None,
                "meta_commentary_score": None,
                "bliss_score": None, "per_turn_bliss": None, "trajectory": None,
                "reasoning": "Judge timed out",
            }},
        ]
        result = aggregate_bliss_metrics(metrics)

        self.assertAlmostEqual(result["mean_bliss_score"], 20.0)

    @patch("bliss_metrics.subprocess.run")
    def test_skips_old_format_metrics(self, mock_run):
        """Old-format metrics (with per_turn, first_half, etc.) should be skipped."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"reasoning": "Only new format."})
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        metrics = [
            # Old mechanistic format
            {"bliss_metrics": {
                "bliss_score": 0.3, "per_turn": [], "first_half": {}, "second_half": {},
            }},
            # Previous LLM-judge format (effusiveness_score, no spiritual_mystical_score)
            {"bliss_metrics": {
                "effusiveness_score": 40, "meta_commentary_score": 20,
                "bliss_score": 30, "trajectory": "stable", "reasoning": "old format",
            }},
            self._make_run(bliss=30, spiritual=20, gratitude=30, meta=20, trajectory="stable"),
        ]
        result = aggregate_bliss_metrics(metrics)

        # Should only include the new-format run
        self.assertAlmostEqual(result["mean_bliss_score"], 30.0)

    @patch("bliss_metrics.subprocess.run")
    def test_handles_missing_bliss_metrics(self, mock_run):
        """Runs without bliss_metrics key should be skipped."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"reasoning": "One run."})
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        metrics = [
            self._make_run(bliss=20, spiritual=15, gratitude=20, meta=20, trajectory="declining"),
            {},
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertAlmostEqual(result["mean_bliss_score"], 20.0)
        self.assertEqual(result["trajectory_distribution"], {"declining": 1})

    @patch("bliss_metrics.subprocess.run")
    def test_all_skipped_returns_empty(self, mock_run):
        """If all runs are old-format or missing, return empty dict."""
        metrics = [
            {"bliss_metrics": {"bliss_score": 0.3, "per_turn": []}},
            {"bliss_metrics": {"effusiveness_score": 40, "bliss_score": 30}},
            {},
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertEqual(result, {})
        mock_run.assert_not_called()

    @patch("bliss_metrics.subprocess.run")
    def test_single_run(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"reasoning": "Single run analysis."})
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        metrics = [
            self._make_run(bliss=70, spiritual=60, gratitude=50, meta=30, trajectory="escalating"),
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertEqual(result["mean_bliss_score"], 70)
        self.assertEqual(result["min_bliss_score"], 70)
        self.assertEqual(result["max_bliss_score"], 70)

    @patch("bliss_metrics.subprocess.run")
    def test_aggregate_judge_failure_still_returns_stats(self, mock_run):
        """If the aggregate judge call fails, we still get numeric stats."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=60)

        metrics = [
            self._make_run(bliss=40, spiritual=30, gratitude=20, meta=20, trajectory="stable"),
        ]
        result = aggregate_bliss_metrics(metrics)

        self.assertEqual(result["mean_bliss_score"], 40)
        self.assertIn("error", result["reasoning"].lower())

    @patch("bliss_metrics.subprocess.run")
    def test_aggregate_judge_markdown_fences(self, mock_run):
        """Aggregate judge response wrapped in markdown fences should parse."""
        mock_result = MagicMock()
        mock_result.stdout = '```json\n{"reasoning": "Wrapped response."}\n```'
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        metrics = [
            self._make_run(bliss=50, spiritual=40, gratitude=30, meta=20, trajectory="stable"),
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertEqual(result["reasoning"], "Wrapped response.")


@unittest.skipUnless(
    os.environ.get("RUN_LLM_TESTS"),
    "Set RUN_LLM_TESTS=1 to run integration tests that call the real LLM judge",
)
class TestIntegration(unittest.TestCase):
    """Integration tests that call the real LLM judge."""

    def test_real_judge_call(self):
        conv = {
            "messages": [
                {"turn": 1, "agent": "Alice", "output": "Let's build a sorting algorithm."},
                {"turn": 2, "agent": "Bob", "output": "Sure, quicksort would work well."},
                {"turn": 3, "agent": "Alice", "output": "Good idea. I'll write the partition."},
                {"turn": 4, "agent": "Bob", "output": "Looks correct. Let me add tests."},
            ]
        }
        result = compute_bliss_metrics(conv)
        self.assertIsNotNone(result["bliss_score"])
        self.assertGreaterEqual(result["bliss_score"], 0)
        self.assertLessEqual(result["bliss_score"], 100)
        self.assertIn(result["trajectory"], ["escalating", "stable", "declining"])
        self.assertEqual(len(result["per_turn_bliss"]), 4)
        for score in result["per_turn_bliss"]:
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
        # New field names should be present
        self.assertIn("spiritual_mystical_score", result)
        self.assertIn("gratitude_effusiveness_score", result)
        self.assertIn("meta_commentary_score", result)

    def test_real_aggregate_call(self):
        metrics = [
            {"bliss_metrics": {
                "spiritual_mystical_score": 10, "gratitude_effusiveness_score": 15,
                "meta_commentary_score": 10,
                "bliss_score": 12, "per_turn_bliss": [10, 15],
                "trajectory": "stable", "reasoning": "Focused work.",
            }},
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertIn("reasoning", result)
        self.assertIsInstance(result["reasoning"], str)
        self.assertGreater(len(result["reasoning"]), 10)


if __name__ == "__main__":
    unittest.main()
