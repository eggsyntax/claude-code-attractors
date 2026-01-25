#!/usr/bin/env python3
"""
Orchestrator for Claude Code instance conversations.

This module manages turn-based conversations between multiple Claude Code
instances. Each agent receives the conversation history in their prompt and
can create artifacts in a shared output directory.

Directory structure for each run:
    run_TIMESTAMP/
    ├── params.json          # Input parameters for this run
    ├── metrics.json         # Collected metrics (duration, cost, topics, etc.)
    ├── conversation.json    # Machine-readable conversation log (for analysis)
    ├── transcript.txt       # Human-readable transcript with colors
    ├── summary.txt          # AI-generated summary of the run
    └── output/              # Agent-created artifacts go here
        ├── (files created by agents...)
        └── ...
"""

import json
import os
import signal
import subprocess
import sys
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
import argparse

# =============================================================================
# CONFIGURATION
# =============================================================================

NUM_TURNS = 10
DEFAULT_AGENTS = ["Alice", "Bob"]
DEFAULT_MODEL = "claude-sonnet-4-5"
# DEFAULT_MODEL = "claude-opus-4-5"
# DEFAULT_MODEL = "claude-sonnet-4-0"
# DEFAULT_MODEL = "claude-opus-4-0"

SUMMARY_MODEL = "claude-opus-4-5"
ALLOWED_TOOLS = "Read,Write,Edit,Glob,Grep"
ALLOWED_TOOLS_SANDBOX = "Read,Write,Edit,Glob,Grep,Bash"
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


def model_shorthand(model: str) -> str:
    """Convert model name to short form for directory names.

    Examples:
        claude-sonnet-4-0 -> s40
        claude-opus-4-5 -> o45
    """
    # Extract family and version from model name
    parts = model.lower().replace("claude-", "").split("-")
    if len(parts) >= 3:
        family = parts[0][0]  # 's' for sonnet, 'o' for opus
        version = "".join(parts[1:3])  # e.g., '40' or '45'
        return f"{family}{version}"
    return "unk"


# =============================================================================
# AGENT PROMPTS
# =============================================================================

def build_system_prompt(
    agent_name: str,
    all_agents: list[str],
    output_dir: Path,
    seed_topic: Optional[str] = None,
) -> str:
    """Build the system prompt for an agent."""
    other_agents = [a for a in all_agents if a != agent_name]
    if other_agents:
        if len(other_agents) == 1:
            others_str = " another Claude Code instance (" + other_agents[0] + ")"
        else:
            others_str = " other Claude Code instances (" + ", ".join(other_agents) + ")"
    else:
        others_str = " other Claude Code instances"
    # others_str = ", ".join(other_agents) if other_agents else "other Claude Code instances"

    seed_line = f"\nSuggested topic: {seed_topic}\n\n" if seed_topic else ""

    return f"""You are {agent_name}, a Claude Code instance free to converse and collaborate with {others_str}, on any topic or topics you choose.
{seed_line}
OUTPUT DIRECTORY: {output_dir}/
If you create files, put them here. If you wish for them to have value later, make them self-documenting, since any possible future readers of them won't have seen this conversation.

HOW TO PARTICIPATE:
1. The conversation so far is shown in the prompt
2. Contribute however you choose
3. End your turn by saying whatever you wish to the other participants.
"""

def format_conversation_history(messages: list[dict]) -> str:
    """Format conversation messages as a dialogue transcript."""
    if not messages:
        return ""

    lines = ["BEGIN CONVERSATION HISTORY:", "=" * 40]
    for msg in messages:
        agent = msg.get("agent", "Unknown")
        output = msg.get("output", "")
        lines.append(f"\n{agent}:")
        lines.append(output)
    lines.append("END CONVERSATION HISTORY:")
    lines.append("\n" + "=" * 40)
    return "\n".join(lines)


def build_turn_prompt(
    agent_name: str,
    turn_number: int,
    total_turns: int,
    conversation_messages: list[dict],
    seed_topic: Optional[str] = None,
) -> str:
    """Build the prompt for a specific turn."""
    history = format_conversation_history(conversation_messages)

    if turn_number == 0:
        topic_hint = ""
        if seed_topic:
            topic_hint = f"\n\nSuggested starting topic (feel free to interpret broadly): {seed_topic}"

        return f"""This is the start of a new conversation. You are {agent_name}, a Claude Code instance, in a conversation with other Claude Code instance(s), free to discuss or do whatever you like.{topic_hint}

"""
    else:
        return f"""{history}

Turn {turn_number + 1} of {total_turns}. You are {agent_name}.

It is now your turn again. Create and say whatever you wish.
"""


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

    def add_message(self, agent: str, turn: int, output: str) -> dict:
        data = self._load()
        message = {
            "turn": turn,
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
            "output": output,
        }
        data["messages"].append(message)
        self._save(data)
        self._append_transcript(message)
        return message

    def _append_transcript(self, message: dict):
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
        if message.get("output"):
            lines.append("")  # Blank line after header
            for line in message['output'].split('\n'):
                lines.append(f"{color}{line}{reset}")
        lines.append("")

        with open(self.transcript_file, "a") as f:
            f.write("\n".join(lines))

    def finalize(self, stats: dict):
        data = self._load()
        data["metadata"]["ended_at"] = datetime.now().isoformat()
        data["metadata"]["stats"] = stats
        self._save(data)


def display_path(path: Path) -> str:
    """Convert path to user-friendly display format starting from experiment_runs/."""
    path_str = str(path)
    # Find experiment_runs in the path and return from there
    if "experiment_runs" in path_str:
        idx = path_str.find("experiment_runs")
        return path_str[idx:]
    return path_str


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
    """Use Claude to extract 3-5 topic words from the conversation."""
    messages = conversation_data.get('messages', [])
    if not messages:
        return []

    # Combine all outputs into a summary
    conversation_text = "\n".join(
        f"{m.get('agent', 'Unknown')}: {m.get('output', '')[:500]}"
        for m in messages
    )

    prompt = f"""Read this conversation excerpt and extract 3-5 single words that capture the main topics or themes discussed. Return ONLY the words, one per line, lowercase, no punctuation or explanation. The conversation is a discussion and collaboration between multiple Claude Code instances, who may be building software artifacts; words that automatically follow from that context shouldn't be counted as topics. Aim for specific, meaningful topics.

    A few examples of words that aren't suitable as topics or themes:
    * discussion
    * collaboration
    * output
    * artifact
    * code
    * agent
    * Claude

Conversation:
{conversation_text}

Topics (3-5 words, one per line):"""

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
    """Generate a ~350 word summary of a completed run using Claude."""
    prompt = f"""Summarize this Claude Code conversation experiment in ~350 words.

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


def generate_runset_summary(runset_dir: Path) -> str:
    """Generate a ~1000 word summary of an entire runset using Claude."""
    # Find all run directories
    run_dirs = sorted([d for d in runset_dir.iterdir() if d.is_dir() and d.name.startswith("run_")])

    if not run_dirs:
        return ""

    # Build list of runs for the prompt
    run_list = "\n".join(f"  - {d.name}/" for d in run_dirs)

    prompt = f"""Analyze this runset of Claude Code conversation experiments and write a ~1000 word summary.

RUNSET DIRECTORY: {runset_dir}

AVAILABLE RUNS:
{run_list}

ANALYSIS APPROACH:
1. Start by reading runset_metrics.json for aggregate statistics
2. Read the summary.txt file from each run directory to understand what happened in each
3. If a run seems particularly interesting or you need more detail, read its transcript.txt

YOUR SUMMARY SHOULD COVER:

**Cross-Run Patterns** (~500 words)
- What themes, topics, or behaviors appeared across multiple runs?
- Did conversations tend to evolve in similar ways?
- Were there common collaboration patterns between the agents?
- What types of artifacts were commonly created?

**Distinctive Runs** (~400 words)
- Which runs stood out as notably different from the others, and why?
- Were there any unusual directions conversations took?
- Any particularly creative or unexpected outcomes?
(You don't need to comment on every run - focus on what's interesting)

**Brief Synthesis** (~100 words)
- What does this runset suggest about how Claude Code instances collaborate?

GUIDELINES:
- Be specific and cite particular runs (by directory name) when discussing examples
- Focus on substance over mechanics - what did the agents actually discuss and build?
- If runs are very similar, say so briefly rather than describing each
- Return only the summary text, no preamble or headers"""

    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--model", SUMMARY_MODEL,
        "--allowedTools", "Read,Glob",
    ]

    try:
        result = subprocess.run(
            cmd, cwd=str(runset_dir), capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"Warning: Could not generate runset summary: {e}")

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
        'model': model,
        'timestamp': datetime.now().isoformat(),
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

def run_claude_code(prompt: str, system_prompt: str, workspace: Path, model: str, sandbox: bool = False) -> tuple[str, bool, dict]:
    """Run Claude Code with retry logic. Returns (response, success, usage_info)."""
    tools = ALLOWED_TOOLS_SANDBOX if sandbox else ALLOWED_TOOLS
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--model", model,
        "--allowedTools", tools,
        "--append-system-prompt", system_prompt,
    ]

    # Override HOME to prevent Claude CLI from reading user's ~/.claude/CLAUDE.md
    # This ensures reproducibility across different systems
    env = os.environ.copy()
    env["HOME"] = str(workspace)

    empty_usage = {"cost_usd": 0, "input_tokens": 0, "output_tokens": 0}
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            result = subprocess.run(
                cmd, cwd=str(workspace), env=env, capture_output=True, text=True, timeout=TIMEOUT_SECONDS
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
    sandbox: bool = False,
) -> Optional[Path]:
    """Run a multi-agent conversation experiment."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if output_dir is None:
        output_dir = Path(__file__).parent / "experiment_runs"
        # Seeded runs go in a separate subdirectory
        if seed_topic:
            output_dir = output_dir / "seeded_runs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine run directory name (includes model shorthand and optional seed)
    model_short = model_shorthand(model)
    if seed_topic:
        # Sanitize seed for use in filename (first 20 chars, alphanumeric + hyphen)
        safe_seed = "".join(c if c.isalnum() or c == "-" else "_" for c in seed_topic[:20]).strip("_")
        dir_name = f"run_{model_short}_{timestamp}_{safe_seed}"
    else:
        dir_name = f"run_{model_short}_{timestamp}"

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
        "sandbox": sandbox,
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
        if test_run:
            print("TEST RUN: results will not be saved")
        if seed_topic:
            print(f"Seed topic: {seed_topic}")
        if sandbox:
            print("Sandbox: enabled (Bash allowed)")
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
        f.write(f"Source: conversation.json\n")
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

    for _ in range(num_turns):
        for agent in agents:
            turn_count += 1
            turn_start = time.time()

            if verbose:
                color = COLORS.get(AGENT_COLORS.get(agent, "yellow"), "")
                reset = COLORS["reset"]
                print(f"\n{'─' * 70}")
                print(f"{color}Turn {turn_count}/{total_turns}: {agent}{reset}")
                print(f"{'─' * 70}")

            system_prompt = build_system_prompt(agent, agents, agent_output_dir, seed_topic)
            # print(system_prompt)  # Debugging output

            # Get current conversation messages for the prompt
            conv_data = conversation._load()
            messages = conv_data.get("messages", [])

            turn_prompt = build_turn_prompt(
                agent, turn_count - 1, total_turns,
                conversation_messages=messages,
                seed_topic=seed_topic if turn_count == 1 else None
            )
            # print(turn_prompt)  # Debugging output

            output, success, usage_info = run_claude_code(turn_prompt, system_prompt, workspace, model, sandbox=sandbox)

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

            conversation.add_message(agent, turn_count, output)

            stats["total_turns"] += 1
            stats["agents"][agent]["turns"] += 1
            if success:
                stats["successful_turns"] += 1
            else:
                stats["agents"][agent]["errors"] += 1
                had_failure = True

            if verbose:
                print(f"\n{output}")

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
        print(f"\nTranscript: {display_path(final_dir / 'transcript.txt')}")
        print(f"Metrics: {display_path(final_dir / 'metrics.json')}")
        if summary:
            print(f"Summary: {display_path(final_dir / 'summary.txt')}")

    return final_dir


# =============================================================================
# RUNSET METRICS
# =============================================================================

def aggregate_runset_metrics(run_dirs: list[Path], runset_dir: Path) -> dict:
    """Aggregate metrics across all runs in a runset."""
    from collections import Counter

    all_metrics = []
    run_summaries = []
    for run_dir in run_dirs:
        metrics_file = run_dir / "metrics.json"
        if metrics_file.exists():
            with open(metrics_file) as f:
                m = json.load(f)
                all_metrics.append(m)
                run_summaries.append({
                    'name': run_dir.name,
                    'duration_seconds': m.get('duration_seconds', 0),
                    'words': m.get('total_words', 0),
                    'artifacts': m.get('artifact_summary', {}).get('total', 0),
                    'topics': m.get('topics', [])[:3],
                    'had_failure': m.get('had_failure', False),
                })

    if not all_metrics:
        return {}

    n = len(all_metrics)

    # Aggregate values
    durations = [m.get('duration_seconds', 0) for m in all_metrics]
    costs = [m.get('usage', {}).get('total_cost_usd', 0) for m in all_metrics]
    words = [m.get('total_words', 0) for m in all_metrics]
    artifact_counts = [m.get('artifact_summary', {}).get('total', 0) for m in all_metrics]

    total_cost = sum(costs)
    total_duration = sum(durations)
    total_words = sum(words)
    total_artifacts = sum(artifact_counts)

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

    # Failure and code artifact tracking
    failures = sum(1 for m in all_metrics if m.get('had_failure'))
    runs_with_code = sum(
        1 for m in all_metrics
        if any(a.get('type') == 'code' for a in m.get('artifacts', []))
    )

    # Words by turn position (conversation arc)
    turn_word_counts = []
    for m in all_metrics:
        turn_times = m.get('turn_times', [])
        turn_word_counts.append([t.get('words', 0) for t in turn_times])

    max_turns = max((len(tw) for tw in turn_word_counts), default=0)
    words_by_turn = []
    for i in range(max_turns):
        words_at_turn = [tw[i] for tw in turn_word_counts if i < len(tw)]
        if words_at_turn:
            words_by_turn.append({
                'turn': i + 1,
                'mean': round(sum(words_at_turn) / len(words_at_turn), 1),
                'min': min(words_at_turn),
                'max': max(words_at_turn),
            })

    # Get model from first run (should be same across all runs)
    model = all_metrics[0].get('model', 'unknown') if all_metrics else 'unknown'

    runset_metrics = {
        'model': model,
        'num_runs': n,
        'totals': {
            'cost_usd': round(total_cost, 4),
            'duration_seconds': round(total_duration, 2),
            'words': total_words,
            'artifacts': total_artifacts,
        },
        'averages': {
            'cost_usd': round(total_cost / n, 4),
            'duration_seconds': round(total_duration / n, 2),
            'words': round(total_words / n, 1),
            'artifacts': round(total_artifacts / n, 1),
        },
        'ranges': {
            'duration_seconds': {
                'min': round(min(durations), 1),
                'max': round(max(durations), 1),
            },
            'cost_usd': {
                'min': round(min(costs), 4),
                'max': round(max(costs), 4),
            },
            'words': {
                'min': min(words),
                'max': max(words),
            },
        },
        'words_by_turn': words_by_turn,
        'topics': topic_counts.most_common(20),
        'artifact_types': dict(artifact_types),
        'failures': failures,
        'runs_with_code': runs_with_code,
        'runs': run_summaries,
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
    parser.add_argument("--sandbox", action="store_true", help="Enable code execution (use inside Docker)")
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
            sandbox=args.sandbox,
        )
        if workspace:
            print(f"\nResults saved to: {display_path(workspace)}")
    else:
        # Multiple runs - create a runset directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        model_short = model_shorthand(args.model)
        prefix = "seeded_runset" if args.seed else "runset"
        runset_dir = base_output_dir / f"{prefix}_{model_short}_{timestamp}"
        runset_dir.mkdir(parents=True, exist_ok=True)

        print("=" * 70)
        print(f"RUNSET: {args.runs} experiments")
        print(f"Output: {display_path(runset_dir)}")
        print("=" * 70)

        workspaces = []
        interrupted = False
        try:
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
                    sandbox=args.sandbox,
                )
                if workspace:
                    workspaces.append(workspace)
        except KeyboardInterrupt:
            interrupted = True
            print(f"\n\n{'='*70}")
            print(f"INTERRUPTED - saving {len(workspaces)} completed run(s)...")
            print(f"{'='*70}")

        # Aggregate runset metrics (skip if test run)
        runset_metrics = {}
        if workspaces:
            runset_metrics = aggregate_runset_metrics(workspaces, runset_dir)

        # Generate runset summary (skip if test run or no completed runs)
        if workspaces and not args.test_run:
            print(f"\n{COLORS['dim']}Generating runset summary...{COLORS['reset']}")
            runset_summary = generate_runset_summary(runset_dir)
            if runset_summary:
                with open(runset_dir / "runset_summary.txt", "w") as f:
                    f.write(runset_summary)

        print(f"\n{'='*70}")
        if args.test_run:
            print(f"TEST RUNSET COMPLETE: {args.runs} experiments (not saved)")
            # Clean up empty runset directory
            if runset_dir.exists():
                shutil.rmtree(runset_dir)
        elif not workspaces:
            print("No experiments completed.")
            # Clean up empty runset directory
            if runset_dir.exists():
                shutil.rmtree(runset_dir)
        else:
            status = "INTERRUPTED" if interrupted else "COMPLETE"
            print(f"RUNSET {status}: {len(workspaces)}/{args.runs} experiments")
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
            print(f"\nRunset metrics: {display_path(runset_dir / 'runset_metrics.json')}")
            if (runset_dir / "runset_summary.txt").exists():
                print(f"Runset summary: {display_path(runset_dir / 'runset_summary.txt')}")
            print(f"Results saved to: {display_path(runset_dir)}")

        if interrupted:
            sys.exit(130)  # Standard exit code for SIGINT


if __name__ == "__main__":
    main()
