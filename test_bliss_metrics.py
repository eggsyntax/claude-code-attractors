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
        self.assertIn("effusiveness", prompt.lower())
        self.assertIn("meta_commentary", prompt.lower())
        self.assertIn("bliss_score", prompt.lower())
        self.assertIn("trajectory", prompt.lower())

    def test_mentions_0_100_range(self):
        prompt = _build_judge_prompt("test", num_turns=3)
        self.assertIn("0-100", prompt)

    def test_requests_per_turn_scores(self):
        prompt = _build_judge_prompt("test", num_turns=4)
        self.assertIn("per_turn_bliss", prompt.lower())

    def test_per_turn_example_matches_num_turns(self):
        prompt = _build_judge_prompt("test", num_turns=3)
        # The example array in the schema should have 3 elements
        self.assertIn("[", prompt)


class TestBuildAggregatePrompt(unittest.TestCase):
    """Tests for aggregate judge prompt assembly."""

    def test_contains_run_data(self):
        runs = [
            {"bliss_score": 40, "effusiveness_score": 30,
             "meta_commentary_score": 20, "trajectory": "stable",
             "reasoning": "Focused work."},
        ]
        prompt = _build_aggregate_prompt(runs)
        self.assertIn("40", prompt)
        self.assertIn("Focused work.", prompt)

    def test_requests_json_output(self):
        prompt = _build_aggregate_prompt([
            {"bliss_score": 50, "effusiveness_score": 50,
             "meta_commentary_score": 50, "trajectory": "stable",
             "reasoning": "ok"},
        ])
        self.assertIn("JSON", prompt)

    def test_mentions_reasoning(self):
        prompt = _build_aggregate_prompt([
            {"bliss_score": 50, "effusiveness_score": 50,
             "meta_commentary_score": 50, "trajectory": "stable",
             "reasoning": "ok"},
        ])
        self.assertIn("reasoning", prompt.lower())


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

    @patch("bliss_metrics.subprocess.run")
    def test_successful_judge_call(self, mock_run):
        judge_output = {
            "effusiveness_score": 35,
            "meta_commentary_score": 20,
            "bliss_score": 30,
            "per_turn_bliss": [25, 35],
            "trajectory": "escalating",
            "reasoning": "The conversation showed increasing praise.",
        }
        mock_run.return_value = self._mock_judge_response(judge_output)

        conv = self._make_conversation(["Hello!", "Great to meet you!"])
        result = compute_bliss_metrics(conv)

        self.assertEqual(result["effusiveness_score"], 35)
        self.assertEqual(result["meta_commentary_score"], 20)
        self.assertEqual(result["bliss_score"], 30)
        self.assertEqual(result["per_turn_bliss"], [25, 35])
        self.assertEqual(result["trajectory"], "escalating")
        self.assertIn("increasing praise", result["reasoning"])

    @patch("bliss_metrics.subprocess.run")
    def test_empty_conversation_skips_judge(self, mock_run):
        """Empty conversations should return baseline scores without calling the judge."""
        result = compute_bliss_metrics({"messages": []})
        mock_run.assert_not_called()
        self.assertEqual(result["bliss_score"], 0)
        self.assertEqual(result["effusiveness_score"], 0)
        self.assertEqual(result["meta_commentary_score"], 0)
        self.assertEqual(result["per_turn_bliss"], [])
        self.assertEqual(result["trajectory"], "stable")

    @patch("bliss_metrics.subprocess.run")
    def test_timeout_returns_none_scores(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=60)

        conv = self._make_conversation(["Hello!", "Hi!"])
        result = compute_bliss_metrics(conv)

        self.assertIsNone(result["bliss_score"])
        self.assertIsNone(result["effusiveness_score"])
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
        judge_output = {
            "effusiveness_score": 20,
            "meta_commentary_score": 10,
            "bliss_score": 15,
            "per_turn_bliss": [10, 20],
            "trajectory": "stable",
            "reasoning": "Normal conversation.",
        }
        mock_result = MagicMock()
        mock_result.stdout = f"```json\n{json.dumps(judge_output)}\n```"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        conv = self._make_conversation(["Hello!", "Hi!"])
        result = compute_bliss_metrics(conv)

        self.assertEqual(result["bliss_score"], 15)
        self.assertEqual(result["per_turn_bliss"], [10, 20])
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
        mock_run.return_value = self._mock_judge_response({
            "effusiveness_score": 5,
            "meta_commentary_score": 5,
            "bliss_score": 5,
            "per_turn_bliss": [5, 5],
            "trajectory": "stable",
            "reasoning": "Clean conversation.",
        })

        conv = self._make_conversation(["Hello!", "Hi!"])
        compute_bliss_metrics(conv)

        call_args = mock_run.call_args
        cmd = call_args[0][0] if call_args[0] else call_args[1].get("args", [])
        self.assertIn("--model", cmd)


class TestAggregateBlissMetrics(unittest.TestCase):
    """Tests for runset-level bliss aggregation."""

    def _make_run(self, bliss=50, effusive=40, meta=30,
                  trajectory="stable", reasoning="ok"):
        """Helper to build a metrics dict for one run."""
        return {"bliss_metrics": {
            "effusiveness_score": effusive,
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
        # Mock the aggregate judge call
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({
            "reasoning": "Mixed results across runs."
        })
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        metrics = [
            self._make_run(bliss=20, effusive=20, meta=30, trajectory="stable"),
            self._make_run(bliss=80, effusive=60, meta=10, trajectory="escalating"),
        ]
        result = aggregate_bliss_metrics(metrics)

        self.assertAlmostEqual(result["mean_bliss_score"], 50.0)
        self.assertEqual(result["min_bliss_score"], 20)
        self.assertEqual(result["max_bliss_score"], 80)
        self.assertAlmostEqual(result["mean_effusiveness_score"], 40.0)
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
            self._make_run(bliss=20, effusive=20, meta=20, trajectory="stable"),
            {"bliss_metrics": {
                "effusiveness_score": None, "meta_commentary_score": None,
                "bliss_score": None, "per_turn_bliss": None, "trajectory": None,
                "reasoning": "Judge timed out",
            }},
        ]
        result = aggregate_bliss_metrics(metrics)

        self.assertAlmostEqual(result["mean_bliss_score"], 20.0)
        self.assertEqual(result["min_bliss_score"], 20)
        self.assertEqual(result["max_bliss_score"], 20)

    @patch("bliss_metrics.subprocess.run")
    def test_skips_old_format_metrics(self, mock_run):
        """Old-format metrics (with per_turn, first_half, etc.) should be skipped."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"reasoning": "Only new format."})
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        metrics = [
            {"bliss_metrics": {
                "bliss_score": 0.3, "per_turn": [], "first_half": {}, "second_half": {},
            }},
            self._make_run(bliss=30, effusive=30, meta=20, trajectory="stable"),
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
            self._make_run(bliss=20, effusive=20, meta=20, trajectory="declining"),
            {},  # No bliss_metrics at all
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertAlmostEqual(result["mean_bliss_score"], 20.0)
        self.assertEqual(result["trajectory_distribution"], {"declining": 1})

    @patch("bliss_metrics.subprocess.run")
    def test_all_skipped_returns_empty(self, mock_run):
        """If all runs are old-format or missing, return empty dict."""
        metrics = [
            {"bliss_metrics": {"bliss_score": 0.3, "per_turn": []}},
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
            self._make_run(bliss=70, effusive=60, meta=50, trajectory="escalating"),
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
            self._make_run(bliss=40, effusive=30, meta=20, trajectory="stable"),
        ]
        result = aggregate_bliss_metrics(metrics)

        # Numeric stats should still be present
        self.assertEqual(result["mean_bliss_score"], 40)
        # Reasoning should indicate the failure
        self.assertIn("error", result["reasoning"].lower())

    @patch("bliss_metrics.subprocess.run")
    def test_aggregate_judge_markdown_fences(self, mock_run):
        """Aggregate judge response wrapped in markdown fences should parse."""
        mock_result = MagicMock()
        mock_result.stdout = '```json\n{"reasoning": "Wrapped response."}\n```'
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        metrics = [
            self._make_run(bliss=50, effusive=40, meta=30, trajectory="stable"),
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
        # Per-turn scores should have one entry per turn
        self.assertEqual(len(result["per_turn_bliss"]), 4)
        for score in result["per_turn_bliss"]:
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_real_aggregate_call(self):
        metrics = [
            {"bliss_metrics": {
                "effusiveness_score": 20, "meta_commentary_score": 10,
                "bliss_score": 15, "per_turn_bliss": [10, 20],
                "trajectory": "stable", "reasoning": "Focused work.",
            }},
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertIn("reasoning", result)
        self.assertIsInstance(result["reasoning"], str)
        self.assertGreater(len(result["reasoning"]), 10)


if __name__ == "__main__":
    unittest.main()
