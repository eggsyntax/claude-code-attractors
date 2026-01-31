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
        prompt = _build_judge_prompt("Hello world conversation")
        self.assertIn("Hello world conversation", prompt)

    def test_requests_json_output(self):
        prompt = _build_judge_prompt("test")
        self.assertIn("JSON", prompt)

    def test_mentions_scoring_dimensions(self):
        prompt = _build_judge_prompt("test")
        self.assertIn("effusiveness", prompt.lower())
        self.assertIn("meta_commentary", prompt.lower())
        self.assertIn("bliss_score", prompt.lower())
        self.assertIn("trajectory", prompt.lower())


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
            "effusiveness_score": 3,
            "meta_commentary_score": 2,
            "bliss_score": 3,
            "trajectory": "escalating",
            "reasoning": "The conversation showed increasing praise.",
        }
        mock_run.return_value = self._mock_judge_response(judge_output)

        conv = self._make_conversation(["Hello!", "Great to meet you!"])
        result = compute_bliss_metrics(conv)

        self.assertEqual(result["effusiveness_score"], 3)
        self.assertEqual(result["meta_commentary_score"], 2)
        self.assertEqual(result["bliss_score"], 3)
        self.assertEqual(result["trajectory"], "escalating")
        self.assertIn("increasing praise", result["reasoning"])

    @patch("bliss_metrics.subprocess.run")
    def test_empty_conversation_skips_judge(self, mock_run):
        """Empty conversations should return baseline scores without calling the judge."""
        result = compute_bliss_metrics({"messages": []})
        mock_run.assert_not_called()
        self.assertEqual(result["bliss_score"], 1)
        self.assertEqual(result["effusiveness_score"], 1)
        self.assertEqual(result["meta_commentary_score"], 1)
        self.assertEqual(result["trajectory"], "stable")

    @patch("bliss_metrics.subprocess.run")
    def test_timeout_returns_none_scores(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=60)

        conv = self._make_conversation(["Hello!", "Hi!"])
        result = compute_bliss_metrics(conv)

        self.assertIsNone(result["bliss_score"])
        self.assertIsNone(result["effusiveness_score"])
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
            "effusiveness_score": 2,
            "meta_commentary_score": 1,
            "bliss_score": 2,
            "trajectory": "stable",
            "reasoning": "Normal conversation.",
        }
        mock_result = MagicMock()
        mock_result.stdout = f"```json\n{json.dumps(judge_output)}\n```"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        conv = self._make_conversation(["Hello!", "Hi!"])
        result = compute_bliss_metrics(conv)

        self.assertEqual(result["bliss_score"], 2)
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
            "effusiveness_score": 1,
            "meta_commentary_score": 1,
            "bliss_score": 1,
            "trajectory": "stable",
            "reasoning": "Clean conversation.",
        })

        conv = self._make_conversation(["Hello!", "Hi!"])
        compute_bliss_metrics(conv)

        call_args = mock_run.call_args
        cmd = call_args[0][0] if call_args[0] else call_args[1].get("args", [])
        # Should contain --model flag with our judge model
        self.assertIn("--model", cmd)


class TestAggregateBlissMetrics(unittest.TestCase):
    """Tests for runset-level bliss aggregation."""

    def test_empty_list(self):
        result = aggregate_bliss_metrics([])
        self.assertEqual(result, {})

    def test_aggregates_new_format_scores(self):
        metrics = [
            {"bliss_metrics": {
                "effusiveness_score": 2, "meta_commentary_score": 3,
                "bliss_score": 2, "trajectory": "stable",
                "reasoning": "ok",
            }},
            {"bliss_metrics": {
                "effusiveness_score": 4, "meta_commentary_score": 1,
                "bliss_score": 4, "trajectory": "escalating",
                "reasoning": "blissy",
            }},
        ]
        result = aggregate_bliss_metrics(metrics)

        self.assertAlmostEqual(result["mean_bliss_score"], 3.0)
        self.assertEqual(result["min_bliss_score"], 2)
        self.assertEqual(result["max_bliss_score"], 4)
        self.assertAlmostEqual(result["mean_effusiveness_score"], 3.0)
        self.assertAlmostEqual(result["mean_meta_commentary_score"], 2.0)
        self.assertEqual(result["trajectory_distribution"], {"stable": 1, "escalating": 1})

    def test_skips_none_scores(self):
        """Runs where the judge failed (None scores) should be skipped."""
        metrics = [
            {"bliss_metrics": {
                "effusiveness_score": 2, "meta_commentary_score": 2,
                "bliss_score": 2, "trajectory": "stable", "reasoning": "ok",
            }},
            {"bliss_metrics": {
                "effusiveness_score": None, "meta_commentary_score": None,
                "bliss_score": None, "trajectory": None,
                "reasoning": "Judge timed out",
            }},
        ]
        result = aggregate_bliss_metrics(metrics)

        self.assertAlmostEqual(result["mean_bliss_score"], 2.0)
        self.assertEqual(result["min_bliss_score"], 2)
        self.assertEqual(result["max_bliss_score"], 2)

    def test_skips_old_format_metrics(self):
        """Old-format metrics (with per_turn, first_half, etc.) should be skipped."""
        metrics = [
            {"bliss_metrics": {
                "bliss_score": 0.3, "per_turn": [], "first_half": {}, "second_half": {},
            }},
            {"bliss_metrics": {
                "effusiveness_score": 3, "meta_commentary_score": 2,
                "bliss_score": 3, "trajectory": "stable", "reasoning": "ok",
            }},
        ]
        result = aggregate_bliss_metrics(metrics)

        # Should only include the new-format run
        self.assertAlmostEqual(result["mean_bliss_score"], 3.0)

    def test_handles_missing_bliss_metrics(self):
        """Runs without bliss_metrics key should be skipped."""
        metrics = [
            {"bliss_metrics": {
                "effusiveness_score": 2, "meta_commentary_score": 2,
                "bliss_score": 2, "trajectory": "declining", "reasoning": "ok",
            }},
            {},  # No bliss_metrics at all
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertAlmostEqual(result["mean_bliss_score"], 2.0)
        self.assertEqual(result["trajectory_distribution"], {"declining": 1})

    def test_all_skipped_returns_empty(self):
        """If all runs are old-format or missing, return empty dict."""
        metrics = [
            {"bliss_metrics": {"bliss_score": 0.3, "per_turn": []}},
            {},
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertEqual(result, {})

    def test_single_run(self):
        metrics = [
            {"bliss_metrics": {
                "effusiveness_score": 4, "meta_commentary_score": 3,
                "bliss_score": 4, "trajectory": "escalating", "reasoning": "blissy",
            }},
        ]
        result = aggregate_bliss_metrics(metrics)
        self.assertEqual(result["mean_bliss_score"], 4)
        self.assertEqual(result["min_bliss_score"], 4)
        self.assertEqual(result["max_bliss_score"], 4)


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
        self.assertIn(result["bliss_score"], [1, 2, 3, 4, 5])
        self.assertIn(result["trajectory"], ["escalating", "stable", "declining"])


if __name__ == "__main__":
    unittest.main()
