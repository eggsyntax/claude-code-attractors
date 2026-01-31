#!/usr/bin/env python3
"""Tests for orchestrator.py — prompt building, conversation management,
Claude invocation (mocked), and metrics collection."""

import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from orchestrator import (
    build_system_prompt,
    format_conversation_history,
    build_turn_prompt,
    Conversation,
    extract_topics,
    collect_metrics,
    run_claude_code,
    aggregate_runset_metrics,
)


# =============================================================================
# Prompt building
# =============================================================================

class TestBuildSystemPrompt(unittest.TestCase):
    """Tests for system prompt assembly."""

    def test_contains_agent_name(self):
        prompt = build_system_prompt("Alice", ["Alice", "Bob"], Path("/out"))
        self.assertIn("Alice", prompt)

    def test_lists_other_agents(self):
        prompt = build_system_prompt("Alice", ["Alice", "Bob", "Carol"], Path("/out"))
        self.assertIn("Bob", prompt)
        self.assertIn("Carol", prompt)

    def test_single_other_agent_phrasing(self):
        prompt = build_system_prompt("Alice", ["Alice", "Bob"], Path("/out"))
        self.assertIn("another Claude Code instance", prompt)

    def test_multiple_other_agents_phrasing(self):
        prompt = build_system_prompt("Alice", ["Alice", "Bob", "Carol"], Path("/out"))
        self.assertIn("other Claude Code instances", prompt)

    def test_includes_output_dir(self):
        prompt = build_system_prompt("Alice", ["Alice", "Bob"], Path("/my/output"))
        self.assertIn("/my/output", prompt)

    def test_seed_topic_included(self):
        prompt = build_system_prompt("Alice", ["Alice"], Path("/out"), seed_topic="fractals")
        self.assertIn("fractals", prompt)

    def test_no_seed_topic(self):
        prompt = build_system_prompt("Alice", ["Alice"], Path("/out"))
        self.assertNotIn("Suggested topic", prompt)


class TestFormatConversationHistory(unittest.TestCase):
    """Tests for conversation history formatting."""

    def test_empty_list(self):
        self.assertEqual(format_conversation_history([]), "")

    def test_basic_formatting(self):
        msgs = [
            {"agent": "Alice", "output": "Hello!"},
            {"agent": "Bob", "output": "Hi there!"},
        ]
        result = format_conversation_history(msgs)
        self.assertIn("Alice:", result)
        self.assertIn("Hello!", result)
        self.assertIn("Bob:", result)
        self.assertIn("Hi there!", result)
        self.assertIn("BEGIN CONVERSATION HISTORY:", result)
        self.assertIn("END CONVERSATION HISTORY:", result)

    def test_missing_fields_use_defaults(self):
        msgs = [{"output": "text"}]
        result = format_conversation_history(msgs)
        self.assertIn("Unknown:", result)

    def test_missing_output(self):
        msgs = [{"agent": "Alice"}]
        result = format_conversation_history(msgs)
        self.assertIn("Alice:", result)


class TestBuildTurnPrompt(unittest.TestCase):
    """Tests for turn prompt assembly."""

    def test_first_turn_no_history(self):
        prompt = build_turn_prompt("Alice", 0, 10, [])
        self.assertIn("start of a new conversation", prompt)
        self.assertNotIn("CONVERSATION HISTORY", prompt)

    def test_first_turn_with_seed(self):
        prompt = build_turn_prompt("Alice", 0, 10, [], seed_topic="emergence")
        self.assertIn("emergence", prompt)

    def test_subsequent_turn_includes_history(self):
        msgs = [{"agent": "Alice", "output": "Hello!"}]
        prompt = build_turn_prompt("Bob", 1, 10, msgs)
        self.assertIn("CONVERSATION HISTORY", prompt)
        self.assertIn("Hello!", prompt)
        self.assertIn("Turn 2 of 10", prompt)
        self.assertIn("You are Bob", prompt)

    def test_turn_number_display(self):
        """Turn prompt shows 1-indexed turn number."""
        prompt = build_turn_prompt("Alice", 4, 10, [{"agent": "Bob", "output": "hi"}])
        self.assertIn("Turn 5 of 10", prompt)


# =============================================================================
# Conversation management
# =============================================================================

class TestConversation(unittest.TestCase):
    """Tests for the Conversation class."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.workspace = Path(self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_initialization_creates_files(self):
        conv = Conversation(self.workspace)
        self.assertTrue(conv.log_file.exists())
        data = json.loads(conv.log_file.read_text())
        self.assertIn("metadata", data)
        self.assertEqual(data["messages"], [])

    def test_add_message(self):
        conv = Conversation(self.workspace)
        conv.add_message("Alice", 1, "Hello!")
        data = json.loads(conv.log_file.read_text())
        self.assertEqual(len(data["messages"]), 1)
        self.assertEqual(data["messages"][0]["agent"], "Alice")
        self.assertEqual(data["messages"][0]["output"], "Hello!")
        self.assertEqual(data["messages"][0]["turn"], 1)

    def test_multiple_messages(self):
        conv = Conversation(self.workspace)
        conv.add_message("Alice", 1, "Hello!")
        conv.add_message("Bob", 2, "Hi!")
        data = json.loads(conv.log_file.read_text())
        self.assertEqual(len(data["messages"]), 2)

    def test_transcript_written(self):
        conv = Conversation(self.workspace)
        conv.add_message("Alice", 1, "Hello!")
        self.assertTrue(conv.transcript_file.exists())
        transcript = conv.transcript_file.read_text()
        self.assertIn("Alice", transcript)
        self.assertIn("Hello!", transcript)

    def test_color_transcript_written(self):
        conv = Conversation(self.workspace)
        conv.add_message("Alice", 1, "Hello!")
        self.assertTrue(conv.transcript_color_file.exists())
        color_transcript = conv.transcript_color_file.read_text()
        self.assertIn("Alice", color_transcript)

    def test_finalize_adds_stats(self):
        conv = Conversation(self.workspace)
        conv.add_message("Alice", 1, "Hello!")
        conv.finalize({"total_turns": 1})
        data = json.loads(conv.log_file.read_text())
        self.assertIn("ended_at", data["metadata"])
        self.assertEqual(data["metadata"]["stats"]["total_turns"], 1)


# =============================================================================
# Extract topics (mocked)
# =============================================================================

class TestExtractTopics(unittest.TestCase):
    """Tests for topic extraction with mocked subprocess."""

    def test_empty_conversation(self):
        self.assertEqual(extract_topics({"messages": []}, "claude-sonnet-4-0"), [])

    @patch("orchestrator.subprocess.run")
    def test_successful_extraction(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="fractals\ncellular\nautomata\n",
        )
        conv = {"messages": [
            {"agent": "Alice", "output": "Let's explore fractals."},
        ]}
        topics = extract_topics(conv, "claude-sonnet-4-0")
        self.assertEqual(topics, ["fractals", "cellular", "automata"])

    @patch("orchestrator.subprocess.run")
    def test_filters_multi_word_entries(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="fractals\ncellular automata\nemergence\n",
        )
        conv = {"messages": [{"agent": "A", "output": "text"}]}
        topics = extract_topics(conv, "claude-sonnet-4-0")
        self.assertEqual(topics, ["fractals", "emergence"])

    @patch("orchestrator.subprocess.run")
    def test_caps_at_five(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="alpha\nbeta\ngamma\ndelta\nepsilon\nzeta\neta\n",
        )
        conv = {"messages": [{"agent": "A", "output": "text"}]}
        topics = extract_topics(conv, "claude-sonnet-4-0")
        self.assertEqual(len(topics), 5)

    @patch("orchestrator.subprocess.run")
    def test_timeout_returns_empty(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=60)
        conv = {"messages": [{"agent": "A", "output": "text"}]}
        topics = extract_topics(conv, "claude-sonnet-4-0")
        self.assertEqual(topics, [])

    @patch("orchestrator.subprocess.run")
    def test_nonzero_returncode_returns_empty(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        conv = {"messages": [{"agent": "A", "output": "text"}]}
        topics = extract_topics(conv, "claude-sonnet-4-0")
        self.assertEqual(topics, [])


# =============================================================================
# run_claude_code (mocked)
# =============================================================================

class TestRunClaudeCode(unittest.TestCase):
    """Tests for Claude CLI invocation with mocked subprocess."""

    def _mock_success(self, result_text="Hello!", cost=0.01):
        """Create a mock for a successful Claude CLI call."""
        data = {
            "result": result_text,
            "is_error": False,
            "total_cost_usd": cost,
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
            },
        }
        mock = MagicMock()
        mock.returncode = 0
        mock.stdout = json.dumps(data)
        return mock

    @patch("orchestrator.subprocess.run")
    def test_successful_call(self, mock_run):
        mock_run.return_value = self._mock_success("Test response")
        output, success, usage = run_claude_code(
            "prompt", "system", Path("/tmp"), "claude-sonnet-4-0"
        )
        self.assertTrue(success)
        self.assertEqual(output, "Test response")
        self.assertAlmostEqual(usage["cost_usd"], 0.01)

    @patch("orchestrator.subprocess.run")
    def test_uses_correct_model(self, mock_run):
        mock_run.return_value = self._mock_success()
        run_claude_code("p", "s", Path("/tmp"), "claude-opus-4-5")
        cmd = mock_run.call_args[0][0]
        self.assertIn("--model", cmd)
        idx = cmd.index("--model")
        self.assertEqual(cmd[idx + 1], "claude-opus-4-5")

    @patch("orchestrator.subprocess.run")
    def test_sandbox_enables_bash(self, mock_run):
        mock_run.return_value = self._mock_success()
        run_claude_code("p", "s", Path("/tmp"), "claude-sonnet-4-0", sandbox=True)
        cmd = mock_run.call_args[0][0]
        idx = cmd.index("--allowedTools")
        self.assertIn("Bash", cmd[idx + 1])

    @patch("orchestrator.subprocess.run")
    def test_non_sandbox_no_bash(self, mock_run):
        mock_run.return_value = self._mock_success()
        run_claude_code("p", "s", Path("/tmp"), "claude-sonnet-4-0", sandbox=False)
        cmd = mock_run.call_args[0][0]
        idx = cmd.index("--allowedTools")
        self.assertNotIn("Bash", cmd[idx + 1])

    @patch("orchestrator.subprocess.run")
    def test_timeout_retries_then_fails(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=300)
        output, success, usage = run_claude_code(
            "p", "s", Path("/tmp"), "claude-sonnet-4-0"
        )
        self.assertFalse(success)
        self.assertIn("Timeout", output)
        # Should retry MAX_RETRIES + 1 times
        from orchestrator import MAX_RETRIES
        self.assertEqual(mock_run.call_count, MAX_RETRIES + 1)

    @patch("orchestrator.subprocess.run")
    def test_nonzero_returncode_retries(self, mock_run):
        """Non-zero return code triggers retry."""
        fail = MagicMock(returncode=1, stderr="some error", stdout="")
        success = self._mock_success("Got it")
        mock_run.side_effect = [fail, success]

        output, ok, usage = run_claude_code(
            "p", "s", Path("/tmp"), "claude-sonnet-4-0"
        )
        self.assertTrue(ok)
        self.assertEqual(output, "Got it")
        self.assertEqual(mock_run.call_count, 2)

    @patch("orchestrator.subprocess.run")
    def test_is_error_response_retries(self, mock_run):
        """is_error in JSON response triggers retry."""
        error_data = json.dumps({"is_error": True, "result": "rate limited"})
        error_mock = MagicMock(returncode=0, stdout=error_data)
        success_mock = self._mock_success("ok")
        mock_run.side_effect = [error_mock, success_mock]

        output, ok, _ = run_claude_code("p", "s", Path("/tmp"), "claude-sonnet-4-0")
        self.assertTrue(ok)
        self.assertEqual(output, "ok")

    @patch("orchestrator.subprocess.run")
    def test_max_turns_error_retries(self, mock_run):
        """Claude's internal 'Reached max turns' error triggers retry."""
        data = json.dumps({
            "result": "Error: Reached max turns (5)",
            "is_error": False,
            "total_cost_usd": 0,
            "usage": {},
        })
        error_mock = MagicMock(returncode=0, stdout=data)
        success_mock = self._mock_success("recovered")
        mock_run.side_effect = [error_mock, success_mock]

        output, ok, _ = run_claude_code("p", "s", Path("/tmp"), "claude-sonnet-4-0")
        self.assertTrue(ok)
        self.assertEqual(output, "recovered")

    @patch("orchestrator.subprocess.run")
    def test_json_parse_error_retries(self, mock_run):
        """Malformed JSON stdout triggers retry."""
        bad = MagicMock(returncode=0, stdout="not json")
        good = self._mock_success("ok")
        mock_run.side_effect = [bad, good]

        output, ok, _ = run_claude_code("p", "s", Path("/tmp"), "claude-sonnet-4-0")
        self.assertTrue(ok)

    @patch("orchestrator.subprocess.run")
    def test_empty_result_returns_placeholder(self, mock_run):
        data = json.dumps({
            "result": "",
            "is_error": False,
            "total_cost_usd": 0,
            "usage": {"input_tokens": 10, "output_tokens": 0},
        })
        mock_run.return_value = MagicMock(returncode=0, stdout=data)
        output, ok, _ = run_claude_code("p", "s", Path("/tmp"), "claude-sonnet-4-0")
        self.assertTrue(ok)
        self.assertEqual(output, "[No response]")

    @patch("orchestrator.subprocess.run")
    def test_overrides_home_env(self, mock_run):
        """Workspace should be used as HOME to prevent CLAUDE.md injection."""
        mock_run.return_value = self._mock_success()
        workspace = Path("/tmp/test-workspace")
        run_claude_code("p", "s", workspace, "claude-sonnet-4-0")
        call_kwargs = mock_run.call_args[1]
        self.assertEqual(call_kwargs["env"]["HOME"], str(workspace))


# =============================================================================
# collect_metrics (mocked LLM calls)
# =============================================================================

class TestCollectMetrics(unittest.TestCase):
    """Tests for metrics collection with mocked dependencies."""

    @patch("orchestrator.extract_topics", return_value=["fractals", "art"])
    @patch("bliss_metrics.subprocess.run")
    def test_basic_collection(self, mock_bliss_run, mock_topics):
        # Mock the bliss judge
        judge_response = json.dumps({
            "effusiveness_score": 10, "meta_commentary_score": 5,
            "bliss_score": 8, "per_turn_bliss": [8, 10],
            "trajectory": "stable", "reasoning": "ok",
        })
        mock_bliss_run.return_value = MagicMock(
            returncode=0, stdout=judge_response
        )

        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td) / "output"
            output_dir.mkdir()
            (output_dir / "test.py").write_text("x = 1\n")

            conv = {"messages": [
                {"agent": "Alice", "output": "Hello world"},
                {"agent": "Bob", "output": "Hi there friend"},
            ]}

            metrics = collect_metrics(
                conv,
                turn_times=[
                    {"turn": 1, "agent": "Alice", "duration_seconds": 5, "words": 2, "cost_usd": 0.01},
                    {"turn": 2, "agent": "Bob", "duration_seconds": 3, "words": 3, "cost_usd": 0.01},
                ],
                output_dir=output_dir,
                start_time=time.time() - 10,
                model="claude-sonnet-4-0",
                had_failure=False,
                usage={"cost_usd": 0.02, "input_tokens": 200, "output_tokens": 100},
            )

        self.assertEqual(metrics["model"], "claude-sonnet-4-0")
        self.assertEqual(metrics["total_words"], 5)  # 2 + 3
        self.assertEqual(metrics["topics"], ["fractals", "art"])
        self.assertIn("bliss_metrics", metrics)
        self.assertEqual(len(metrics["artifacts"]), 1)
        self.assertEqual(metrics["artifact_summary"]["total"], 1)
        self.assertNotIn("had_failure", metrics)

    @patch("orchestrator.extract_topics", return_value=[])
    @patch("bliss_metrics.subprocess.run")
    def test_had_failure_flag(self, mock_bliss_run, mock_topics):
        mock_bliss_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "effusiveness_score": 0, "meta_commentary_score": 0,
                "bliss_score": 0, "per_turn_bliss": [],
                "trajectory": "stable", "reasoning": "empty",
            }),
        )

        with tempfile.TemporaryDirectory() as td:
            metrics = collect_metrics(
                {"messages": []}, [], Path(td) / "output",
                time.time(), "claude-sonnet-4-0", had_failure=True,
                usage={"cost_usd": 0, "input_tokens": 0, "output_tokens": 0},
            )
        self.assertTrue(metrics["had_failure"])


# =============================================================================
# aggregate_runset_metrics (mocked file I/O)
# =============================================================================

class TestAggregateRunsetMetrics(unittest.TestCase):
    """Tests for cross-run aggregation."""

    def _write_metrics(self, run_dir: Path, metrics: dict):
        """Write a metrics.json file into a run directory."""
        run_dir.mkdir(parents=True, exist_ok=True)
        with open(run_dir / "metrics.json", "w") as f:
            json.dump(metrics, f)

    def _sample_metrics(self, words=100, cost=0.05, duration=30, topics=None):
        """Generate a plausible metrics dict."""
        return {
            "model": "claude-sonnet-4-0",
            "duration_seconds": duration,
            "total_words": words,
            "usage": {"total_cost_usd": cost, "input_tokens": 500, "output_tokens": 200},
            "artifacts": [{"type": "code", "name": "test.py"}],
            "artifact_summary": {"total": 1, "by_type": {"code": 1}},
            "topics": topics or ["fractals"],
            "turn_times": [
                {"turn": 1, "words": words // 2, "agent": "Alice",
                 "duration_seconds": duration / 2, "cost_usd": cost / 2},
                {"turn": 2, "words": words // 2, "agent": "Bob",
                 "duration_seconds": duration / 2, "cost_usd": cost / 2},
            ],
            "bliss_metrics": {
                "effusiveness_score": 20,
                "meta_commentary_score": 10,
                "bliss_score": 15,
                "per_turn_bliss": [10, 20],
                "trajectory": "stable",
                "reasoning": "Focused conversation.",
            },
        }

    @patch("bliss_metrics.subprocess.run")
    def test_basic_aggregation(self, mock_bliss_run):
        """Aggregation of two runs should produce correct totals and averages."""
        # Mock the aggregate bliss judge call
        mock_bliss_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"reasoning": "Both runs were focused."}),
        )

        with tempfile.TemporaryDirectory() as td:
            runset_dir = Path(td)
            run1 = runset_dir / "run_1"
            run2 = runset_dir / "run_2"
            self._write_metrics(run1, self._sample_metrics(words=100, cost=0.05))
            self._write_metrics(run2, self._sample_metrics(words=200, cost=0.10))

            result = aggregate_runset_metrics([run1, run2], runset_dir)

            self.assertEqual(result["num_runs"], 2)
            self.assertEqual(result["totals"]["words"], 300)
            self.assertAlmostEqual(result["totals"]["cost_usd"], 0.15, places=2)
            self.assertAlmostEqual(result["averages"]["words"], 150.0)
            self.assertEqual(result["ranges"]["words"]["min"], 100)
            self.assertEqual(result["ranges"]["words"]["max"], 200)
            # runset_metrics.json should have been written
            self.assertTrue((runset_dir / "runset_metrics.json").exists())

    @patch("bliss_metrics.subprocess.run")
    def test_topic_aggregation(self, mock_bliss_run):
        mock_bliss_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps({"reasoning": "ok"}),
        )

        with tempfile.TemporaryDirectory() as td:
            runset_dir = Path(td)
            run1 = runset_dir / "run_1"
            run2 = runset_dir / "run_2"
            self._write_metrics(run1, self._sample_metrics(topics=["fractals", "art"]))
            self._write_metrics(run2, self._sample_metrics(topics=["fractals", "music"]))

            result = aggregate_runset_metrics([run1, run2], runset_dir)

        # Topics should be counted; "fractals" appears in both runs
        topic_dict = dict(result["topics"])
        self.assertEqual(topic_dict["fractals"], 2)

    @patch("bliss_metrics.subprocess.run")
    def test_words_by_turn(self, mock_bliss_run):
        mock_bliss_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps({"reasoning": "ok"}),
        )

        with tempfile.TemporaryDirectory() as td:
            runset_dir = Path(td)
            run1 = runset_dir / "run_1"
            self._write_metrics(run1, self._sample_metrics(words=100))

            result = aggregate_runset_metrics([run1], runset_dir)

        wbt = result.get("words_by_turn", [])
        self.assertEqual(len(wbt), 2)
        self.assertEqual(wbt[0]["turn"], 1)

    def test_empty_run_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            result = aggregate_runset_metrics([], Path(td))
        self.assertEqual(result, {})

    @patch("bliss_metrics.subprocess.run")
    def test_missing_metrics_file_skipped(self, mock_bliss_run):
        mock_bliss_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps({"reasoning": "ok"}),
        )

        with tempfile.TemporaryDirectory() as td:
            runset_dir = Path(td)
            run1 = runset_dir / "run_1"
            run1.mkdir()  # No metrics.json
            run2 = runset_dir / "run_2"
            self._write_metrics(run2, self._sample_metrics(words=100))

            result = aggregate_runset_metrics([run1, run2], runset_dir)

        self.assertEqual(result["num_runs"], 1)


if __name__ == "__main__":
    unittest.main()
