#!/usr/bin/env python3
"""
Semantic trajectory analysis using text embeddings.

Embeds each conversational turn and computes trajectory metrics that capture
how the conversation moves through semantic space. Decreasing velocity and
convergence toward a centroid suggest attractor behavior.

Public API:
    embed_texts(texts) -> list[list[float]]
    compute_trajectory_metrics(embeddings) -> dict
    compute_runset_trajectory_metrics(run_dirs) -> dict
"""

import json
import logging
import math
import os
import urllib.request
from pathlib import Path

log = logging.getLogger(__name__)

# Embedding model configuration
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_API_URL = "https://api.openai.com/v1/embeddings"


# ---------------------------------------------------------------------------
# Vector math utilities
# ---------------------------------------------------------------------------

def cosine_distance(a: list[float], b: list[float]) -> float:
    """Compute cosine distance (1 - cosine_similarity) between two vectors.

    Returns 1.0 if either vector has zero magnitude (graceful fallback).
    """
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 1.0
    return 1.0 - dot / (mag_a * mag_b)


def centroid(vectors: list[list[float]]) -> list[float]:
    """Compute the element-wise mean of a list of vectors."""
    if not vectors:
        raise ValueError("Cannot compute centroid of empty list")
    n = len(vectors)
    dim = len(vectors[0])
    return [sum(v[i] for v in vectors) / n for i in range(dim)]


# ---------------------------------------------------------------------------
# Embedding API
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str], max_retries: int = 3) -> list[list[float]]:
    """Embed a list of texts using the OpenAI embedding API.

    Requires the OPENAI_API_KEY environment variable. Returns embeddings
    in the same order as the input texts. Retries with exponential backoff
    on rate limit errors (429).

    Raises RuntimeError if the API key is not set or quota exhausted.
    Raises on HTTP or JSON errors from the API after retries exhausted.
    """
    import time
    import urllib.error

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not set — embedding-based trajectory analysis "
            "requires an OpenAI API key."
        )

    payload = json.dumps({
        "model": EMBEDDING_MODEL,
        "input": texts,
    }).encode()

    last_error = None
    for attempt in range(max_retries + 1):
        # Create fresh request for each attempt
        req = urllib.request.Request(
            EMBEDDING_API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
            # Sort by index to ensure correct ordering
            items = sorted(result["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in items]
        except urllib.error.HTTPError as e:
            last_error = e
            # Check for quota exhaustion or rate limiting
            if e.code == 429:
                try:
                    body = json.loads(e.read().decode())
                    error_code = body.get("error", {}).get("code")
                    if error_code == "insufficient_quota":
                        raise RuntimeError(
                            "OpenAI API quota exhausted — add credits at "
                            "https://platform.openai.com/account/billing"
                        ) from None
                except json.JSONDecodeError:
                    pass  # Couldn't parse body, treat as rate limit
                # Rate limited (not quota) - wait and retry
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 1, 2, 4 seconds
                    log.info("Rate limited, waiting %ds before retry %d/%d",
                             wait_time, attempt + 1, max_retries)
                    time.sleep(wait_time)
                    continue
            raise

    raise last_error


# ---------------------------------------------------------------------------
# Per-run trajectory metrics
# ---------------------------------------------------------------------------

def compute_trajectory_metrics(embeddings: list[list[float]]) -> dict:
    """Compute trajectory metrics from a sequence of turn embeddings.

    Args:
        embeddings: List of embedding vectors, one per turn, in order.

    Returns:
        Dict with keys: velocity, drift_from_start, deceleration_ratio,
        and summary (mean_velocity, max_velocity, min_velocity,
        final_velocity, total_drift).

    Raises ValueError if embeddings is empty.
    """
    if not embeddings:
        raise ValueError("Cannot compute trajectory metrics from empty embeddings")

    n = len(embeddings)

    # Velocity: cosine distance between consecutive turns
    velocity = [
        round(cosine_distance(embeddings[i], embeddings[i + 1]), 2)
        for i in range(n - 1)
    ]

    # Drift from start: cosine distance of each turn from turn 0
    drift_from_start = [
        round(cosine_distance(embeddings[0], embeddings[i]), 2)
        for i in range(n)
    ]

    # Deceleration ratio: fraction of velocity transitions that are decreases
    # 1.0 = monotonically slowing (settling), 0.0 = monotonically accelerating
    if len(velocity) >= 2:
        decelerations = sum(1 for i in range(len(velocity) - 1) if velocity[i + 1] < velocity[i])
        deceleration_ratio = round(decelerations / (len(velocity) - 1), 2)
    else:
        deceleration_ratio = None  # Not enough data points

    # Summary statistics
    summary = {}
    if velocity:
        summary["mean_velocity"] = round(sum(velocity) / len(velocity), 2)
        summary["max_velocity"] = max(velocity)
        summary["min_velocity"] = min(velocity)
        summary["final_velocity"] = velocity[-1]
    else:
        summary["mean_velocity"] = 0.0
        summary["max_velocity"] = 0.0
        summary["min_velocity"] = 0.0
        summary["final_velocity"] = 0.0
    summary["total_drift"] = drift_from_start[-1] if drift_from_start else 0.0

    return {
        "velocity": velocity,
        "drift_from_start": drift_from_start,
        "deceleration_ratio": deceleration_ratio,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Per-runset trajectory metrics
# ---------------------------------------------------------------------------

def _load_embeddings(run_dir: Path) -> list[list[float]] | None:
    """Load embeddings from a run directory's embeddings.json.

    Returns None if the file is missing or malformed.
    """
    emb_file = run_dir / "embeddings.json"
    if not emb_file.exists():
        return None
    try:
        with open(emb_file) as f:
            data = json.load(f)
        items = sorted(data["embeddings"], key=lambda x: x["turn"])
        return [item["embedding"] for item in items]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        log.warning("Failed to load embeddings from %s: %s", run_dir, e)
        return None


def _pairwise_mean_distance(vectors: list[list[float]]) -> float:
    """Average cosine distance across all pairs of vectors.

    Returns 0.0 for a single vector (no pairs).
    """
    n = len(vectors)
    if n < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += cosine_distance(vectors[i], vectors[j])
            count += 1
    return round(total / count, 2)


def compute_runset_trajectory_metrics(run_dirs: list[Path]) -> dict:
    """Compute cross-run trajectory metrics for a runset.

    Reads embeddings.json from each run directory. Runs without embeddings
    are silently skipped.

    Args:
        run_dirs: List of run directory paths.

    Returns:
        Dict with cross-run convergence metrics, or empty dict if
        fewer than 1 run has embeddings.
    """
    # Load embeddings from all runs
    all_embeddings = []
    for rd in run_dirs:
        embs = _load_embeddings(rd)
        if embs and len(embs) >= 1:
            all_embeddings.append(embs)

    if not all_embeddings:
        return {}

    # Collect first and last turn embeddings across runs
    first_turns = [embs[0] for embs in all_embeddings]
    last_turns = [embs[-1] for embs in all_embeddings]

    start_dist = _pairwise_mean_distance(first_turns)
    end_dist = _pairwise_mean_distance(last_turns)

    # Convergence ratio: < 1 means runs converge, > 1 means they diverge
    if start_dist > 0:
        convergence_ratio = round(end_dist / start_dist, 2)
    else:
        convergence_ratio = 1.0

    # Velocity curves: average velocity by turn position across runs
    all_velocities = []
    for embs in all_embeddings:
        metrics = compute_trajectory_metrics(embs)
        all_velocities.append(metrics["velocity"])

    max_vel_len = max(len(v) for v in all_velocities)
    velocity_curves = []
    for i in range(max_vel_len):
        vals = [v[i] for v in all_velocities if i < len(v)]
        if vals:
            velocity_curves.append({
                "turn_pair": f"{i + 1}->{i + 2}",
                "mean_velocity": round(sum(vals) / len(vals), 2),
                "n_runs": len(vals),
            })

    return {
        "n_runs_with_embeddings": len(all_embeddings),
        "start_state_mean_distance": start_dist,
        "end_state_mean_distance": end_dist,
        "convergence_ratio": convergence_ratio,
        "velocity_curves": velocity_curves,
    }
