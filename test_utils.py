#!/usr/bin/env python3
"""Tests for shared utility functions."""

import tempfile
import unittest
from pathlib import Path

from utils import model_shorthand, count_words, display_path, scan_artifacts


class TestModelShorthand(unittest.TestCase):
    """Tests for model name abbreviation."""

    def test_sonnet_4_0(self):
        self.assertEqual(model_shorthand("claude-sonnet-4-0"), "s40")

    def test_opus_4_5(self):
        self.assertEqual(model_shorthand("claude-opus-4-5"), "o45")

    def test_sonnet_4_5(self):
        self.assertEqual(model_shorthand("claude-sonnet-4-5"), "s45")

    def test_unknown_format(self):
        self.assertEqual(model_shorthand("gpt-4"), "unk")

    def test_case_insensitive(self):
        self.assertEqual(model_shorthand("Claude-Sonnet-4-0"), "s40")

    def test_single_part(self):
        self.assertEqual(model_shorthand("something"), "unk")


class TestCountWords(unittest.TestCase):
    """Tests for word counting."""

    def test_basic(self):
        self.assertEqual(count_words("one two three"), 3)

    def test_empty_string(self):
        self.assertEqual(count_words(""), 0)

    def test_none_like_empty(self):
        self.assertEqual(count_words(""), 0)

    def test_extra_whitespace(self):
        self.assertEqual(count_words("  hello   world  "), 2)

    def test_newlines(self):
        self.assertEqual(count_words("hello\nworld\nfoo"), 3)


class TestDisplayPath(unittest.TestCase):
    """Tests for path display formatting."""

    def test_contains_experiment_runs(self):
        p = Path("/some/long/path/experiment_runs/runset_123/metrics.json")
        self.assertEqual(display_path(p), "experiment_runs/runset_123/metrics.json")

    def test_no_experiment_runs(self):
        p = Path("/tmp/some/other/path")
        self.assertEqual(display_path(p), "/tmp/some/other/path")

    def test_experiment_runs_at_start(self):
        p = Path("experiment_runs/run_1")
        self.assertEqual(display_path(p), "experiment_runs/run_1")


class TestScanArtifacts(unittest.TestCase):
    """Tests for output directory scanning."""

    def test_nonexistent_dir(self):
        self.assertEqual(scan_artifacts(Path("/nonexistent")), [])

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(scan_artifacts(Path(td)), [])

    def test_code_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "script.py"
            p.write_text("print('hello')\n")
            artifacts = scan_artifacts(Path(td))
            self.assertEqual(len(artifacts), 1)
            self.assertEqual(artifacts[0]["name"], "script.py")
            self.assertEqual(artifacts[0]["type"], "code")
            self.assertEqual(artifacts[0]["extension"], ".py")
            self.assertEqual(artifacts[0]["lines"], 1)

    def test_document_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "notes.md"
            p.write_text("# Hello\n\nSome text.\n")
            artifacts = scan_artifacts(Path(td))
            self.assertEqual(len(artifacts), 1)
            self.assertEqual(artifacts[0]["type"], "document")

    def test_image_file_no_lines(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "logo.png"
            p.write_bytes(b"\x89PNG\r\n")
            artifacts = scan_artifacts(Path(td))
            self.assertEqual(len(artifacts), 1)
            self.assertEqual(artifacts[0]["type"], "image")
            self.assertIsNone(artifacts[0]["lines"])

    def test_multiple_files(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "a.py").write_text("x = 1\n")
            (Path(td) / "b.js").write_text("let x = 1;\n")
            (Path(td) / "c.json").write_text("{}\n")
            artifacts = scan_artifacts(Path(td))
            self.assertEqual(len(artifacts), 3)
            types = {a["type"] for a in artifacts}
            self.assertEqual(types, {"code", "config"})

    def test_unknown_extension(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "data.xyz").write_text("stuff\n")
            artifacts = scan_artifacts(Path(td))
            self.assertEqual(artifacts[0]["type"], "other")

    def test_skips_directories(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "subdir").mkdir()
            (Path(td) / "file.py").write_text("x = 1\n")
            artifacts = scan_artifacts(Path(td))
            self.assertEqual(len(artifacts), 1)


if __name__ == "__main__":
    unittest.main()
