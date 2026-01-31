#!/usr/bin/env python3
"""
Shared utility functions for the Claude Code attractor experiments.

Pure helper functions with no dependency on experiment-specific logic,
subprocess calls, or LLM invocations.
"""

from pathlib import Path


def model_shorthand(model: str) -> str:
    """Convert a Claude model name to a short form for directory names.

    Examples:
        claude-sonnet-4-0 -> s40
        claude-opus-4-5   -> o45
    """
    parts = model.lower().replace("claude-", "").split("-")
    if len(parts) >= 3:
        family = parts[0][0]  # 's' for sonnet, 'o' for opus, etc.
        version = "".join(parts[1:3])  # e.g., '40' or '45'
        return f"{family}{version}"
    return "unk"


def count_words(text: str) -> int:
    """Count whitespace-delimited words in text. Returns 0 for empty strings."""
    return len(text.split()) if text else 0


def display_path(path: Path) -> str:
    """Format a path for display, trimming to start from experiment_runs/.

    If the path contains 'experiment_runs', returns from that point onward.
    Otherwise returns the full path as a string.
    """
    path_str = str(path)
    if "experiment_runs" in path_str:
        idx = path_str.find("experiment_runs")
        return path_str[idx:]
    return path_str


def scan_artifacts(output_dir: Path) -> list[dict]:
    """Scan a directory for created artifacts and categorize them.

    Returns a list of dicts, each with:
        name, type, extension, size_bytes, lines (None for binary types)

    File types: code, document, web, config, image, other.
    """
    artifacts = []
    if not output_dir.exists():
        return artifacts

    for f in output_dir.iterdir():
        if f.is_file():
            suffix = f.suffix.lower()
            if suffix in ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs']:
                file_type = 'code'
            elif suffix in ['.md', '.txt', '.rst']:
                file_type = 'document'
            elif suffix in ['.html', '.css']:
                file_type = 'web'
            elif suffix in ['.json', '.yaml', '.yml', '.toml']:
                file_type = 'config'
            elif suffix in ['.png', '.jpg', '.svg', '.gif']:
                file_type = 'image'
            else:
                file_type = 'other'

            try:
                size = f.stat().st_size
                lines = (
                    len(f.read_text().splitlines())
                    if file_type in ['code', 'document', 'web', 'config']
                    else None
                )
            except Exception:
                size = 0
                lines = None

            artifacts.append({
                'name': f.name,
                'type': file_type,
                'extension': suffix,
                'size_bytes': size,
                'lines': lines,
            })

    return artifacts
