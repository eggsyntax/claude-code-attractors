#!/usr/bin/env python3
"""Tests for semantic trajectory analysis using embeddings."""

import json
import math
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from embeddings import (
    EMBEDDING_MODEL,
    cosine_distance,
    centroid,
    embed_texts,
    compute_trajectory_metrics,
    compute_runset_trajectory_metrics,
)


class TestCosineDistance(unittest.TestCase):
    """Tests for cosine distance computation."""

    def test_identical_vectors(self):
        """Cosine distance between identical vectors is 0."""
        v = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(cosine_distance(v, v), 0.0, places=6)

    def test_orthogonal_vectors(self):
        """Cosine distance between orthogonal vectors is 1."""
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        self.assertAlmostEqual(cosine_distance(a, b), 1.0, places=6)

    def test_opposite_vectors(self):
        """Cosine distance between opposite vectors is 2."""
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        self.assertAlmostEqual(cosine_distance(a, b), 2.0, places=6)

    def test_similar_vectors(self):
        """Similar vectors have small cosine distance."""
        a = [1.0, 1.0, 0.0]
        b = [1.0, 1.1, 0.0]
        dist = cosine_distance(a, b)
        self.assertGreater(dist, 0.0)
        self.assertLess(dist, 0.1)

    def test_zero_vector_returns_one(self):
        """Zero vector yields distance 1.0 (graceful fallback)."""
        a = [0.0, 0.0]
        b = [1.0, 0.0]
        self.assertAlmostEqual(cosine_distance(a, b), 1.0, places=6)


class TestCentroid(unittest.TestCase):
    """Tests for centroid computation."""

    def test_single_vector(self):
        """Centroid of one vector is itself."""
        v = [1.0, 2.0, 3.0]
        c = centroid([v])
        for i in range(3):
            self.assertAlmostEqual(c[i], v[i])

    def test_two_vectors(self):
        """Centroid of two vectors is their midpoint."""
        a = [0.0, 0.0]
        b = [2.0, 4.0]
        c = centroid([a, b])
        self.assertAlmostEqual(c[0], 1.0)
        self.assertAlmostEqual(c[1], 2.0)

    def test_empty_raises(self):
        """Empty list raises ValueError."""
        with self.assertRaises(ValueError):
            centroid([])


class TestEmbedTexts(unittest.TestCase):
    """Tests for the embed_texts API wrapper."""

    def _mock_response(self, embeddings):
        """Build a mock urllib response returning the given embeddings."""
        body = json.dumps({
            "data": [{"embedding": e, "index": i} for i, e in enumerate(embeddings)]
        }).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("embeddings.urllib.request.urlopen")
    def test_basic_embedding(self, mock_urlopen):
        """Returns embeddings in input order."""
        mock_urlopen.return_value = self._mock_response([[0.1, 0.2], [0.3, 0.4]])
        result = embed_texts(["hello", "world"])
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0][0], 0.1)
        self.assertAlmostEqual(result[1][0], 0.3)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("embeddings.urllib.request.urlopen")
    def test_reorders_by_index(self, mock_urlopen):
        """Handles out-of-order response indices."""
        body = json.dumps({
            "data": [
                {"embedding": [0.3, 0.4], "index": 1},
                {"embedding": [0.1, 0.2], "index": 0},
            ]
        }).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        result = embed_texts(["first", "second"])
        self.assertAlmostEqual(result[0][0], 0.1)
        self.assertAlmostEqual(result[1][0], 0.3)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_raises(self):
        """Raises RuntimeError when OPENAI_API_KEY is not set."""
        # Ensure the key is truly absent
        os.environ.pop("OPENAI_API_KEY", None)
        with self.assertRaises(RuntimeError):
            embed_texts(["hello"])

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("embeddings.urllib.request.urlopen")
    def test_api_error_propagates(self, mock_urlopen):
        """HTTP errors propagate as exceptions."""
        mock_urlopen.side_effect = Exception("API error")
        with self.assertRaises(Exception):
            embed_texts(["hello"])

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("embeddings.urllib.request.urlopen")
    def test_sends_correct_model(self, mock_urlopen):
        """Request body includes the configured model name."""
        mock_urlopen.return_value = self._mock_response([[0.1]])
        embed_texts(["test"])
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        body = json.loads(request.data.decode())
        self.assertEqual(body["model"], EMBEDDING_MODEL)


class TestComputeTrajectoryMetrics(unittest.TestCase):
    """Tests for per-run trajectory metric computation."""

    def test_two_identical_turns(self):
        """Identical embeddings yield zero velocity and drift."""
        embs = [[1.0, 0.0], [1.0, 0.0]]
        metrics = compute_trajectory_metrics(embs)
        self.assertEqual(len(metrics["velocity"]), 1)
        self.assertAlmostEqual(metrics["velocity"][0], 0.0, places=6)
        self.assertAlmostEqual(metrics["drift_from_start"][0], 0.0, places=6)
        self.assertAlmostEqual(metrics["drift_from_start"][1], 0.0, places=6)

    def test_diverging_turns(self):
        """Embeddings moving apart show increasing drift."""
        embs = [[1.0, 0.0], [0.7, 0.7], [0.0, 1.0]]
        metrics = compute_trajectory_metrics(embs)
        # Drift should increase
        self.assertGreater(metrics["drift_from_start"][2],
                           metrics["drift_from_start"][1])

    def test_velocity_length(self):
        """Velocity list has n-1 entries for n embeddings."""
        embs = [[1, 0], [0.7, 0.7], [0, 1], [0, 1]]
        metrics = compute_trajectory_metrics(embs)
        self.assertEqual(len(metrics["velocity"]), 3)

    def test_single_embedding(self):
        """A single embedding produces empty velocity, one drift entry."""
        embs = [[1.0, 2.0]]
        metrics = compute_trajectory_metrics(embs)
        self.assertEqual(metrics["velocity"], [])
        self.assertEqual(len(metrics["drift_from_start"]), 1)
        self.assertAlmostEqual(metrics["drift_from_start"][0], 0.0)

    def test_summary_stats(self):
        """Summary stats are present and reasonable."""
        embs = [[1, 0], [0.7, 0.7], [0, 1]]
        metrics = compute_trajectory_metrics(embs)
        self.assertIn("mean_velocity", metrics["summary"])
        self.assertIn("final_velocity", metrics["summary"])
        self.assertIn("total_drift", metrics["summary"])
        self.assertGreater(metrics["summary"]["mean_velocity"], 0)

    def test_deceleration_ratio_computed(self):
        """Deceleration ratio is computed from velocity transitions."""
        # These embeddings produce velocities that decrease then increase
        embs = [[1, 0], [0.7, 0.7], [0.5, 0.87], [0, 1], [0.2, 0.98]]
        metrics = compute_trajectory_metrics(embs)
        self.assertIn("deceleration_ratio", metrics)
        # Should be a value between 0 and 1
        self.assertIsNotNone(metrics["deceleration_ratio"])
        self.assertGreaterEqual(metrics["deceleration_ratio"], 0.0)
        self.assertLessEqual(metrics["deceleration_ratio"], 1.0)

    def test_deceleration_ratio_insufficient_data(self):
        """With only 2 turns (1 velocity), deceleration_ratio is None."""
        embs = [[1, 0], [0, 1]]
        metrics = compute_trajectory_metrics(embs)
        self.assertIsNone(metrics["deceleration_ratio"])

    def test_empty_raises(self):
        """Empty embedding list raises ValueError."""
        with self.assertRaises(ValueError):
            compute_trajectory_metrics([])


class TestComputeRunsetTrajectoryMetrics(unittest.TestCase):
    """Tests for cross-run trajectory metrics."""

    def _make_run_dir(self, tmp: Path, name: str, embeddings: list) -> Path:
        """Create a run directory with an embeddings.json file."""
        run_dir = tmp / name
        run_dir.mkdir()
        data = {
            "embeddings": [
                {"turn": i + 1, "embedding": e}
                for i, e in enumerate(embeddings)
            ]
        }
        with open(run_dir / "embeddings.json", "w") as f:
            json.dump(data, f)
        return run_dir

    def test_two_converging_runs(self):
        """Runs ending at similar embeddings show low end-state distance."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            r1 = self._make_run_dir(tmp, "run1", [[1, 0], [0.5, 0.5], [0, 1]])
            r2 = self._make_run_dir(tmp, "run2", [[0, 1], [0.5, 0.5], [0.1, 0.9]])
            metrics = compute_runset_trajectory_metrics([r1, r2])
            self.assertIn("end_state_mean_distance", metrics)
            self.assertIn("start_state_mean_distance", metrics)
            # End states [0,1] and [0.1,0.9] should be closer than starts [1,0] and [0,1]
            self.assertLess(metrics["end_state_mean_distance"],
                            metrics["start_state_mean_distance"])

    def test_single_run(self):
        """Single run yields zero pairwise distances."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            r1 = self._make_run_dir(tmp, "run1", [[1, 0], [0, 1]])
            metrics = compute_runset_trajectory_metrics([r1])
            self.assertAlmostEqual(metrics["end_state_mean_distance"], 0.0)

    def test_velocity_curves(self):
        """Velocity curves average across runs by turn position."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # Both runs have 3 turns -> 2 velocity values each
            r1 = self._make_run_dir(tmp, "run1", [[1, 0], [0.7, 0.7], [0, 1]])
            r2 = self._make_run_dir(tmp, "run2", [[1, 0], [0.7, 0.7], [0, 1]])
            metrics = compute_runset_trajectory_metrics([r1, r2])
            self.assertIn("velocity_curves", metrics)
            self.assertEqual(len(metrics["velocity_curves"]), 2)

    def test_missing_embeddings_file(self):
        """Runs without embeddings.json are skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            r1 = self._make_run_dir(tmp, "run1", [[1, 0], [0, 1]])
            r2 = tmp / "run2"
            r2.mkdir()
            # No embeddings.json in r2
            metrics = compute_runset_trajectory_metrics([r1, r2])
            # Should still work with just r1
            self.assertIn("end_state_mean_distance", metrics)

    def test_empty_run_list(self):
        """Empty run list returns empty dict."""
        metrics = compute_runset_trajectory_metrics([])
        self.assertEqual(metrics, {})

    def test_convergence_ratio(self):
        """Convergence ratio is end_state / start_state distance."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # Runs start far apart, end close together
            r1 = self._make_run_dir(tmp, "run1", [[1, 0], [0.1, 0.9]])
            r2 = self._make_run_dir(tmp, "run2", [[0, 1], [0, 1]])
            metrics = compute_runset_trajectory_metrics([r1, r2])
            self.assertIn("convergence_ratio", metrics)
            # End states closer than start states -> ratio < 1
            self.assertLess(metrics["convergence_ratio"], 1.0)


class TestIntegration(unittest.TestCase):
    """Integration tests that call real APIs. Skipped unless RUN_LLM_TESTS=1."""

    @unittest.skipUnless(
        os.environ.get("RUN_LLM_TESTS") == "1",
        "Set RUN_LLM_TESTS=1 to run integration tests",
    )
    def test_real_embedding(self):
        """Embed a small set of texts and verify the result shape."""
        texts = ["Hello world", "Goodbye moon"]
        result = embed_texts(texts)
        self.assertEqual(len(result), 2)
        # text-embedding-3-large returns 3072-dim vectors
        self.assertGreater(len(result[0]), 100)
        self.assertEqual(len(result[0]), len(result[1]))

    @unittest.skipUnless(
        os.environ.get("RUN_LLM_TESTS") == "1",
        "Set RUN_LLM_TESTS=1 to run integration tests",
    )
    def test_real_trajectory_metrics(self):
        """Embed real texts and compute trajectory metrics end-to-end."""
        texts = [
            "Let's discuss cellular automata",
            "Conway's Game of Life is a fascinating example",
            "The glider is a beautiful emergent pattern",
        ]
        embeddings = embed_texts(texts)
        metrics = compute_trajectory_metrics(embeddings)
        self.assertEqual(len(metrics["velocity"]), 2)
        self.assertEqual(len(metrics["drift_from_start"]), 3)


if __name__ == "__main__":
    unittest.main()
