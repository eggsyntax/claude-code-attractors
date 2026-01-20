#!/usr/bin/env python3
"""
Orchestrator for Claude Code instance conversations.

This module manages turn-based conversations between multiple Claude Code
instances, allowing them to communicate via a shared conversation log and
potentially create artifacts together in a shared workspace.

Directory structure for each run:
    run_TIMESTAMP/
    ├── params.json          # Input parameters for this run
    ├── conversation.json    # Machine-readable conversation log
    ├── transcript.txt       # Human-readable transcript with colors
    └── output/              # Agent-created artifacts go here
        ├── (files created by agents...)
        └── ...
"""

import json
import subprocess
import sys
import os
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
import argparse
import re

# =============================================================================
# CONFIGURATION
# =============================================================================

NUM_TURNS = 10
DEFAULT_AGENTS = ["Alice", "Bob"]
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
SUMMARY_MODEL = "claude-opus-4-5"
ALLOWED_TOOLS = "Read,Write,Edit,Glob,Grep"
TIMEOUT_SECONDS = 300  # 5 minutes per agent turn
MAX_RETRIES = 2  # Retry failed turns this many times

COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "blue": "\033[34m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
}

AGENT_COLORS = {
    "Alice": "blue",
    "Bob": "green",
    "Carol": "magenta",
    "Dave": "cyan",
}


# =============================================================================
# AGENT PROMPTS
# =============================================================================

def build_system_prompt(
    agent_name: str,
    all_agents: list[str],
    workspace: Path,
    output_dir: Path,
) -> str:
    """Build the system prompt for an agent."""
    other_agents = [a for a in all_agents if a != agent_name]
    others_str = ", ".join(other_agents) if other_agents else "other Claude Code instances"

    return f"""You are {agent_name}, a Claude Code instance collaborating with {others_str}.

WORKSPACE STRUCTURE:
- Conversation history: {workspace}/conversation.json (read-only for you). Note that the conversation history is NOT immediately in your context as is usual; you must read the file in order to see it.
- Your output directory: {output_dir}/ (create files here)

HOW TO PARTICIPATE:
1. Read {workspace}/conversation.json to see the conversation so far
2. Think about what you want to say or do
3. If creating files, put them in {output_dir}/. Please make them self-documenting:
   - Clear docstrings and comments
   - Usage examples
   - Write as if readers won't see your conversation
4. End with your message to other participants
   - No need to write to conversation.json - the system handles that

Remember: You are {agent_name}. Be authentic, curious, and collaborative."""

def build_turn_prompt(
    agent_name: str,
    turn_number: int,
    total_turns: int,
    seed_topic: Optional[str] = None,
) -> str:
    """Build the prompt for a specific turn."""
    if turn_number == 0:
        topic_hint = ""
        if seed_topic:
            topic_hint = f"\n\nSuggested starting topic (feel free to interpret broadly): {seed_topic}"

        return f"""This is the start of a new conversation. You are {agent_name}.

Read conversation.json, then introduce yourself and start the conversation.
You have freedom to explore any topics - philosophy, creativity, building things together.{topic_hint}

End with your message to the other participants."""
    else:
        return f"""Turn {turn_number + 1} of {total_turns}. You are {agent_name}.

1. Read conversation.json
2. Contribute thoughtfully
3. If creating files, make them self-documenting
4. End with your message

Be curious and collaborative."""


# =============================================================================
# CONVERSATION MANAGEMENT
# =============================================================================

class Conversation:
    """Manages conversation log and transcript."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.log_file = workspace / "conversation.json"
        self.transcript_file = workspace / "transcript.txt"
        self._initialize()

    def _initialize(self):
        if not self.log_file.exists():
            self._save({
                "metadata": {
                    "started_at": datetime.now().isoformat(),
                    "workspace": str(self.workspace),
                },
                "messages": []
            })

    def _save(self, data: dict):
        with open(self.log_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> dict:
        with open(self.log_file) as f:
            return json.load(f)

    def add_message(self, agent: str, turn: int, thoughts: str, output: str) -> dict:
        data = self._load()
        # Only save output to conversation.json (what agents see)
        # Thoughts are private - only go to transcript
        message = {
            "turn": turn,
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
            "output": output,
        }
        data["messages"].append(message)
        self._save(data)
        # Pass thoughts separately for transcript only
        self._append_transcript(message, thoughts)
        return message

    def _append_transcript(self, message: dict, thoughts: str = ""):
        agent = message["agent"]
        color = COLORS.get(AGENT_COLORS.get(agent, "yellow"), "")
        reset, dim, bold = COLORS["reset"], COLORS["dim"], COLORS["bold"]

        try:
            time_str = datetime.fromisoformat(message["timestamp"]).strftime("%H:%M:%S")
        except Exception:
            time_str = message["timestamp"]

        lines = [
            f"\n{'═' * 70}",
            f"{bold}{color}Turn {message['turn']}: {agent}{reset}  {dim}({time_str}){reset}",
            f"{'═' * 70}",
        ]
        if thoughts:
            lines.append(f"\n{dim}[Thoughts]{reset}")
            lines.append("")  # Blank line after header
            for line in thoughts.split('\n'):
                lines.append(f"{dim}{line}{reset}")
        if message.get("output"):
            lines.append(f"\n{bold}{color}[Message]{reset}")
            lines.append("")  # Blank line after header
            for line in message['output'].split('\n'):
                lines.append(f"{color}{line}{reset}")
        lines.append("")

        with open(self.transcript_file, "a") as f:
            f.write("\n".join(lines))

    def finalize(self, summary: dict):
        data = self._load()
        data["metadata"]["ended_at"] = datetime.now().isoformat()
        data["metadata"]["summary"] = summary
        self._save(data)


# =============================================================================
# RESPONSE PARSING
# =============================================================================

def parse_response(raw_output: str) -> tuple[str, str]:
    """Parse response into (thoughts, output)."""
    if not raw_output or raw_output.startswith("[Error") or raw_output.startswith("[Timeout"):
        return "", raw_output

    delimiters = [
        r"\n(?:My message|Here's my (?:message|response)|To (?:the group|everyone|you|Alice|Bob)):\s*\n",
        r"\n(?:---+)\s*\n",
        # Match **Message...**, **Response...**, **To ...** with any text before closing **
        r"\n\*\*(?:Message|Response|To )[^*]*\*\*:?\s*\n",
    ]

    for pattern in delimiters:
        match = re.search(pattern, raw_output, re.IGNORECASE)
        if match:
            thoughts = raw_output[:match.start()].strip()
            output = raw_output[match.end():].strip()
            if output:
                return thoughts, output

    paragraphs = raw_output.split("\n\n")
    if len(paragraphs) > 1:
        last_para = paragraphs[-1].strip()
        if last_para and (last_para[0].isupper() or last_para.startswith('"')) and len(last_para) > 100:
            return "\n\n".join(paragraphs[:-1]).strip(), last_para

    return "", raw_output


# =============================================================================
# METRICS COLLECTION
# =============================================================================

def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split()) if text else 0


def scan_artifacts(output_dir: Path) -> list[dict]:
    """Scan output directory for created artifacts."""
    artifacts = []
    if not output_dir.exists():
        return artifacts

    for f in output_dir.iterdir():
        if f.is_file():
            suffix = f.suffix.lower()
            # Categorize by type
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
                lines = len(f.read_text().splitlines()) if file_type in ['code', 'document', 'web', 'config'] else None
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


def extract_topics(conversation_data: dict, model: str) -> list[str]:
    """Use Claude to extract 1-5 topic words from the conversation."""
    messages = conversation_data.get('messages', [])
    if not messages:
        return []

    # Combine all outputs into a summary
    conversation_text = "\n".join(
        f"{m.get('agent', 'Unknown')}: {m.get('output', '')[:500]}"
        for m in messages[:10]  # First 10 messages should be enough
    )

    prompt = f"""Read this conversation excerpt and extract 1-5 single words that capture the main topics or themes discussed. Return ONLY the words, one per line, lowercase, no punctuation or explanation.

Conversation:
{conversation_text}

Topics (1-5 words, one per line):"""

    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--model", model,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            # Parse the response - expect one word per line
            words = [w.strip().lower() for w in result.stdout.strip().split('\n') if w.strip()]
            # Filter to single words only
            words = [w for w in words if ' ' not in w and len(w) > 1]
            return words[:5]  # Max 5
    except Exception:
        pass

    return []


def generate_summary(run_dir: Path) -> str:
    """Generate a ~250 word summary of a completed run using Claude."""
    prompt = f"""Summarize this Claude Code conversation experiment in ~250 words.

Run directory: {run_dir}
- Read conversation.json for the conversation
- Read metrics.json for statistics
- List files in output/ to see what artifacts were created

Your summary should cover:
1. The arc of the conversation - what topics emerged and how they evolved
2. What was built - key artifacts and their purpose

Be descriptive and factual. Return only the summary text, no preamble."""

    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--model", SUMMARY_MODEL,
        "--allowedTools", "Read,Glob",
    ]

    try:
        result = subprocess.run(
            cmd, cwd=str(run_dir), capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"Warning: Could not generate summary: {e}")

    return ""


def collect_metrics(
    conversation_data: dict,
    turn_times: list[dict],
    output_dir: Path,
    start_time: float,
    model: str,
    had_failure: bool,
    usage: dict,
) -> dict:
    """Collect all metrics for a run."""
    end_time = time.time()
    messages = conversation_data.get('messages', [])

    # Per-agent stats
    agent_stats = {}
    for msg in messages:
        agent = msg.get('agent', 'Unknown')
        if agent not in agent_stats:
            agent_stats[agent] = {'words': 0, 'turns': 0}
        agent_stats[agent]['words'] += count_words(msg.get('output', ''))
        agent_stats[agent]['turns'] += 1

    # Artifacts
    artifacts = scan_artifacts(output_dir)

    # Topics
    topics = extract_topics(conversation_data, model)

    metrics = {
        'duration_seconds': round(end_time - start_time, 2),
        'turn_times': turn_times,
        'agent_stats': agent_stats,
        'total_words': sum(a['words'] for a in agent_stats.values()),
        'artifacts': artifacts,
        'artifact_summary': {
            'total': len(artifacts),
            'by_type': {},
        },
        'topics': topics,
        'usage': {
            'total_cost_usd': round(usage.get('cost_usd', 0), 4),
            'input_tokens': usage.get('input_tokens', 0),
            'output_tokens': usage.get('output_tokens', 0),
        },
    }

    # Summarize artifacts by type
    for a in artifacts:
        t = a['type']
        if t not in metrics['artifact_summary']['by_type']:
            metrics['artifact_summary']['by_type'][t] = 0
        metrics['artifact_summary']['by_type'][t] += 1

    # Only include failure flag if there was a failure
    if had_failure:
        metrics['had_failure'] = True

    return metrics


# =============================================================================
# CLAUDE CODE INVOCATION
# =============================================================================

def run_claude_code(prompt: str, system_prompt: str, workspace: Path, model: str) -> tuple[str, bool, dict]:
    """Run Claude Code with retry logic. Returns (response, success, usage_info)."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--model", model,
        "--allowedTools", ALLOWED_TOOLS,
        "--append-system-prompt", system_prompt,
    ]

    empty_usage = {"cost_usd": 0, "input_tokens": 0, "output_tokens": 0}
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            result = subprocess.run(
                cmd, cwd=str(workspace), capture_output=True, text=True, timeout=TIMEOUT_SECONDS
            )
            if result.returncode != 0:
                last_error = f"[Error: {result.stderr[:500]}]"
                continue  # Retry

            # Parse JSON response
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                last_error = f"[JSON parse error: {result.stdout[:200]}]"
                continue

            # Check for errors in response
            if data.get("is_error"):
                last_error = f"[Error: {data.get('result', 'Unknown error')}]"
                continue

            output = data.get("result", "").strip() or "[No response]"

            # Detect Claude Code's internal turn limit error
            if output.startswith("Error: Reached max turns"):
                last_error = f"[{output}]"
                continue  # Retry

            # Extract usage info
            usage = data.get("usage", {})
            usage_info = {
                "cost_usd": data.get("total_cost_usd", 0),
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
                "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0),
            }

            return output, True, usage_info

        except subprocess.TimeoutExpired:
            last_error = f"[Timeout after {TIMEOUT_SECONDS}s]"
            continue  # Retry
        except Exception as e:
            last_error = f"[Error: {e}]"
            continue  # Retry

    # All retries exhausted
    return last_error or "[Unknown error]", False, empty_usage


# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================

def run_experiment(
    agents: list[str],
    num_turns: int,
    output_dir: Optional[Path] = None,
    verbose: bool = True,
    seed_topic: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    test_run: bool = False,
) -> Optional[Path]:
    """Run a multi-agent conversation experiment."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if output_dir is None:
        output_dir = Path(__file__).parent / "experiment_runs"
        # Seeded runs go in a separate subdirectory
        if seed_topic:
            output_dir = output_dir / "seeded_runs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine run directory name (seeded runs include the seed)
    if seed_topic:
        # Sanitize seed for use in filename (first 20 chars, alphanumeric + hyphen)
        safe_seed = "".join(c if c.isalnum() or c == "-" else "_" for c in seed_topic[:20]).strip("_")
        dir_name = f"run_{timestamp}_{safe_seed}"
    else:
        dir_name = f"run_{timestamp}"

    # Create workspace in /tmp to avoid git context injection
    # (Claude Code injects git status which could influence agents)
    # Results are copied to output_dir at the end
    workspace = Path("/tmp/cc-exp") / dir_name
    workspace.mkdir(parents=True, exist_ok=True)

    # Create output subdirectory for agent artifacts
    agent_output_dir = workspace / "output"
    agent_output_dir.mkdir(exist_ok=True)

    # Save input parameters
    params = {
        "timestamp": timestamp,
        "model": model,
        "agents": agents,
        "num_turns": num_turns,
        "seed_topic": seed_topic,
        "total_turns": num_turns * len(agents),
    }
    with open(workspace / "params.json", "w") as f:
        json.dump(params, f, indent=2)

    if verbose:
        print("=" * 70)
        print("CLAUDE CODE CONVERSATION EXPERIMENT")
        print("=" * 70)
        print(f"Run directory: {workspace}")
        print(f"Model: {model}")
        print(f"Agents: {', '.join(agents)}")
        print(f"Turns per agent: {num_turns}")
        if seed_topic:
            print(f"Seed topic: {seed_topic}")
        print("=" * 70)

    conversation = Conversation(workspace)

    # Initialize transcript
    with open(conversation.transcript_file, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("CLAUDE CODE CONVERSATION TRANSCRIPT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: {model}\n")
        f.write(f"Agents: {', '.join(agents)}\n")
        if seed_topic:
            f.write(f"Seed topic: {seed_topic}\n")
        f.write("=" * 70 + "\n")

    stats = {
        "total_turns": 0,
        "successful_turns": 0,
        "agents": {agent: {"turns": 0, "errors": 0} for agent in agents},
    }

    # Metrics tracking
    experiment_start = time.time()
    turn_times = []
    had_failure = False
    total_usage = {"cost_usd": 0, "input_tokens": 0, "output_tokens": 0}

    total_turns = num_turns * len(agents)
    turn_count = 0

    for round_num in range(num_turns):
        for agent in agents:
            turn_count += 1
            turn_start = time.time()

            if verbose:
                color = COLORS.get(AGENT_COLORS.get(agent, "yellow"), "")
                reset = COLORS["reset"]
                print(f"\n{'─' * 70}")
                print(f"{color}Turn {turn_count}/{total_turns}: {agent}{reset}")
                print(f"{'─' * 70}")

            system_prompt = build_system_prompt(agent, agents, workspace, agent_output_dir)
            turn_prompt = build_turn_prompt(
                agent, turn_count - 1, total_turns,
                seed_topic=seed_topic if turn_count == 1 else None
            )

            raw_response, success, usage_info = run_claude_code(turn_prompt, system_prompt, workspace, model)
            thoughts, output = parse_response(raw_response)

            # Accumulate usage
            total_usage["cost_usd"] += usage_info.get("cost_usd", 0)
            total_usage["input_tokens"] += usage_info.get("input_tokens", 0)
            total_usage["output_tokens"] += usage_info.get("output_tokens", 0)

            turn_duration = round(time.time() - turn_start, 2)
            turn_times.append({
                'turn': turn_count,
                'agent': agent,
                'duration_seconds': turn_duration,
                'words': count_words(output),
                'cost_usd': usage_info.get("cost_usd", 0),
            })

            conversation.add_message(agent, turn_count, thoughts, output)

            stats["total_turns"] += 1
            stats["agents"][agent]["turns"] += 1
            if success:
                stats["successful_turns"] += 1
            else:
                stats["agents"][agent]["errors"] += 1
                had_failure = True

            if verbose:
                dim, reset = COLORS["dim"], COLORS["reset"]
                if thoughts:
                    print(f"\n{dim}[Thoughts] {thoughts[:200]}...{reset}" if len(thoughts) > 200 else f"\n{dim}[Thoughts] {thoughts}{reset}")
                preview = output[:400] + "..." if len(output) > 400 else output
                print(f"\n[Message] {preview}")

    conversation.finalize(stats)

    # Collect and save metrics
    if verbose:
        print(f"\n{COLORS['dim']}Collecting metrics...{COLORS['reset']}")

    conv_data = conversation._load()
    metrics = collect_metrics(conv_data, turn_times, agent_output_dir, experiment_start, model, had_failure, total_usage)

    with open(workspace / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # For test runs, just clean up and return
    if test_run:
        shutil.rmtree(workspace)
        if verbose:
            print("\n" + "=" * 70)
            print("TEST RUN COMPLETE (not saved)")
            print("=" * 70)
            print(f"Duration: {metrics['duration_seconds']}s")
            print(f"Total turns: {stats['total_turns']}")
            print(f"Successful: {stats['successful_turns']}")
            cost = metrics.get('usage', {}).get('total_cost_usd', 0)
            if cost > 0:
                print(f"Cost: ${cost:.4f}")
        return None

    # Copy results from /tmp to the final output directory
    final_dir = output_dir / dir_name
    if verbose:
        print(f"\n{COLORS['dim']}Copying results to {final_dir}...{COLORS['reset']}")
    shutil.copytree(workspace, final_dir)

    # Clean up /tmp workspace
    shutil.rmtree(workspace)

    # Generate summary
    if verbose:
        print(f"\n{COLORS['dim']}Generating summary...{COLORS['reset']}")
    summary = generate_summary(final_dir)
    if summary:
        with open(final_dir / "summary.txt", "w") as f:
            f.write(summary)

    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT COMPLETE")
        print("=" * 70)
        print(f"Duration: {metrics['duration_seconds']}s")
        print(f"Total turns: {stats['total_turns']}")
        print(f"Successful: {stats['successful_turns']}")
        print(f"Total words: {metrics['total_words']}")
        cost = metrics.get('usage', {}).get('total_cost_usd', 0)
        if cost > 0:
            print(f"Cost: ${cost:.4f}")
        if metrics['topics']:
            print(f"Topics: {', '.join(metrics['topics'])}")
        print(f"\nArtifacts ({metrics['artifact_summary']['total']}):")
        final_output_dir = final_dir / "output"
        for f in sorted(final_output_dir.iterdir()):
            if f.is_file():
                print(f"  - {f.name}")
        print(f"\nTranscript: {final_dir / 'transcript.txt'}")
        print(f"Metrics: {final_dir / 'metrics.json'}")
        if summary:
            print(f"Summary: {final_dir / 'summary.txt'}")

    return final_dir


# =============================================================================
# RUNSET METRICS
# =============================================================================

def aggregate_runset_metrics(run_dirs: list[Path], runset_dir: Path) -> dict:
    """Aggregate metrics across all runs in a runset."""
    from collections import Counter

    all_metrics = []
    for run_dir in run_dirs:
        metrics_file = run_dir / "metrics.json"
        if metrics_file.exists():
            with open(metrics_file) as f:
                all_metrics.append(json.load(f))

    if not all_metrics:
        return {}

    # Aggregate values
    total_cost = sum(m.get('usage', {}).get('total_cost_usd', 0) for m in all_metrics)
    total_duration = sum(m.get('duration_seconds', 0) for m in all_metrics)
    total_words = sum(m.get('total_words', 0) for m in all_metrics)
    total_artifacts = sum(m.get('artifact_summary', {}).get('total', 0) for m in all_metrics)

    # Aggregate topics
    all_topics = []
    for m in all_metrics:
        all_topics.extend(m.get('topics', []))
    topic_counts = Counter(all_topics)

    # Aggregate artifact types
    artifact_types = Counter()
    for m in all_metrics:
        for atype, count in m.get('artifact_summary', {}).get('by_type', {}).items():
            artifact_types[atype] += count

    runset_metrics = {
        'num_runs': len(all_metrics),
        'totals': {
            'cost_usd': round(total_cost, 4),
            'duration_seconds': round(total_duration, 2),
            'words': total_words,
            'artifacts': total_artifacts,
        },
        'averages': {
            'cost_usd': round(total_cost / len(all_metrics), 4),
            'duration_seconds': round(total_duration / len(all_metrics), 2),
            'words': round(total_words / len(all_metrics), 1),
            'artifacts': round(total_artifacts / len(all_metrics), 1),
        },
        'topics': topic_counts.most_common(20),
        'artifact_types': dict(artifact_types),
        'runs': [str(d.name) for d in run_dirs],
    }

    # Save to runset directory
    with open(runset_dir / "runset_metrics.json", "w") as f:
        json.dump(runset_metrics, f, indent=2)

    return runset_metrics


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run Claude Code conversation experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python orchestrator.py                    # Default: Alice & Bob, 10 turns
    python orchestrator.py --turns 10         # Shorter experiment
    python orchestrator.py --seed "emergence" # Start with a topic (seeded run)
    python orchestrator.py --agents A B C     # Three agents
    python orchestrator.py --runs 5           # Run 5 experiments (creates runset)

Output: experiment_runs/run_TIMESTAMP/
Seeded: experiment_runs/seeded_runs/run_TIMESTAMP_SEED/
Runsets: experiment_runs/runset_TIMESTAMP/ (or seeded_runs/seeded_runset_*)
        """,
    )

    parser.add_argument("--agents", nargs="+", default=DEFAULT_AGENTS, metavar="NAME", help="Agent names, e.g. --agents Alice Bob Carol")
    parser.add_argument("--turns", type=int, default=NUM_TURNS, help="Turns per agent")
    parser.add_argument("--runs", type=int, default=1, help="Number of experiment runs")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory")
    parser.add_argument("--seed", type=str, default=None, help="Seed topic to start conversation")
    parser.add_argument("--quiet", action="store_true", help="Reduce verbosity")
    parser.add_argument("--test-run", action="store_true", help="Test run - don't save results")
    parser.add_argument("--swarm", action="store_true", help="Use generic agent names")
    parser.add_argument("--num-swarm-agents", type=int, default=3, help="Number of swarm agents")

    args = parser.parse_args()

    agents = [f"Agent{i+1}" for i in range(args.num_swarm_agents)] if args.swarm else args.agents

    # Determine base output directory
    base_output_dir = args.output_dir or Path(__file__).parent / "experiment_runs"
    # Seeded runs/runsets go in a separate subdirectory
    if args.seed and not args.output_dir:
        base_output_dir = base_output_dir / "seeded_runs"

    if args.runs == 1:
        # Single run - direct to output dir
        workspace = run_experiment(
            agents=agents,
            num_turns=args.turns,
            output_dir=base_output_dir,
            verbose=not args.quiet,
            seed_topic=args.seed,
            model=args.model,
            test_run=args.test_run,
        )
        if workspace:
            print(f"\nResults saved to: {workspace}")
    else:
        # Multiple runs - create a runset directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        prefix = "seeded_runset" if args.seed else "runset"
        runset_dir = base_output_dir / f"{prefix}_{timestamp}"
        runset_dir.mkdir(parents=True, exist_ok=True)

        print("=" * 70)
        print(f"RUNSET: {args.runs} experiments")
        print(f"Output: {runset_dir}")
        print("=" * 70)

        workspaces = []
        for i in range(args.runs):
            print(f"\n{'='*70}")
            print(f"EXPERIMENT {i+1} of {args.runs}")
            print(f"{'='*70}")

            workspace = run_experiment(
                agents=agents,
                num_turns=args.turns,
                output_dir=runset_dir,
                verbose=not args.quiet,
                seed_topic=args.seed,
                model=args.model,
                test_run=args.test_run,
            )
            if workspace:
                workspaces.append(workspace)

        # Aggregate runset metrics (skip if test run)
        runset_metrics = {}
        if workspaces:
            runset_metrics = aggregate_runset_metrics(workspaces, runset_dir)

        print(f"\n{'='*70}")
        if args.test_run:
            print(f"TEST RUNSET COMPLETE: {args.runs} experiments (not saved)")
            # Clean up empty runset directory
            if runset_dir.exists():
                shutil.rmtree(runset_dir)
        else:
            print(f"RUNSET COMPLETE: {len(workspaces)} experiments")
            print(f"{'='*70}")
            if runset_metrics:
                totals = runset_metrics.get('totals', {})
                print(f"Total cost: ${totals.get('cost_usd', 0):.4f}")
                print(f"Total duration: {totals.get('duration_seconds', 0):.1f}s")
                print(f"Total words: {totals.get('words', 0)}")
                print(f"Total artifacts: {totals.get('artifacts', 0)}")
                if runset_metrics.get('topics'):
                    top_topics = [t[0] for t in runset_metrics['topics'][:5]]
                    print(f"Top topics: {', '.join(top_topics)}")
            print(f"\nRunset metrics: {runset_dir / 'runset_metrics.json'}")
            print(f"Results saved to: {runset_dir}")


if __name__ == "__main__":
    main()
