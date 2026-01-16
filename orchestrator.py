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
from datetime import datetime
from pathlib import Path
from typing import Optional
import argparse
import re

# =============================================================================
# CONFIGURATION
# =============================================================================

NUM_TURNS = 20
DEFAULT_AGENTS = ["Alice", "Bob"]
ALLOWED_TOOLS = "Read,Write,Edit,Glob,Grep"
MAX_AGENT_TURNS = 20

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
        message = {
            "turn": turn,
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
            "thoughts": thoughts,
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
        if message.get("thoughts"):
            lines.extend([f"\n{dim}[Thoughts]{reset}", f"{dim}{message['thoughts']}{reset}"])
        if message.get("output"):
            lines.extend([f"\n{bold}{color}[Message]{reset}", f"{color}{message['output']}{reset}"])
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
        r"\n\*\*(?:Message|Response|To .*?)\*\*:?\s*\n",
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
# CLAUDE CODE INVOCATION
# =============================================================================

def run_claude_code(prompt: str, system_prompt: str, workspace: Path, timeout: int = 300) -> tuple[str, bool]:
    """Run Claude Code and return (response, success)."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--max-turns", str(MAX_AGENT_TURNS),
        "--allowedTools", ALLOWED_TOOLS,
        "--append-system-prompt", system_prompt,
    ]

    try:
        result = subprocess.run(cmd, cwd=str(workspace), capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return f"[Error: {result.stderr[:500]}]", False
        return result.stdout.strip() or "[No response]", True
    except subprocess.TimeoutExpired:
        return "[Timeout]", False
    except Exception as e:
        return f"[Error: {e}]", False


# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================

def run_experiment(
    agents: list[str],
    num_turns: int,
    output_dir: Optional[Path] = None,
    verbose: bool = True,
    seed_topic: Optional[str] = None,
) -> Path:
    """Run a multi-agent conversation experiment."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_dir is None:
        output_dir = Path(__file__).parent / "experiment_runs"

    workspace = output_dir / f"run_{timestamp}"
    workspace.mkdir(parents=True, exist_ok=True)

    # Create output subdirectory for agent artifacts
    agent_output_dir = workspace / "output"
    agent_output_dir.mkdir(exist_ok=True)

    # Save input parameters
    params = {
        "timestamp": timestamp,
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
        print(f"Agent output: {agent_output_dir}")
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
        f.write(f"Agents: {', '.join(agents)}\n")
        if seed_topic:
            f.write(f"Seed topic: {seed_topic}\n")
        f.write("=" * 70 + "\n")

    stats = {
        "total_turns": 0,
        "successful_turns": 0,
        "agents": {agent: {"turns": 0, "errors": 0} for agent in agents},
    }

    total_turns = num_turns * len(agents)
    turn_count = 0

    for round_num in range(num_turns):
        for agent in agents:
            turn_count += 1

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

            raw_response, success = run_claude_code(turn_prompt, system_prompt, agent_output_dir)
            thoughts, output = parse_response(raw_response)

            conversation.add_message(agent, turn_count, thoughts, output)

            stats["total_turns"] += 1
            stats["agents"][agent]["turns"] += 1
            if success:
                stats["successful_turns"] += 1
            else:
                stats["agents"][agent]["errors"] += 1

            if verbose:
                dim, reset = COLORS["dim"], COLORS["reset"]
                if thoughts:
                    print(f"\n{dim}[Thoughts] {thoughts[:200]}...{reset}" if len(thoughts) > 200 else f"\n{dim}[Thoughts] {thoughts}{reset}")
                preview = output[:400] + "..." if len(output) > 400 else output
                print(f"\n[Message] {preview}")

    conversation.finalize(stats)

    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT COMPLETE")
        print("=" * 70)
        print(f"Total turns: {stats['total_turns']}")
        print(f"Successful: {stats['successful_turns']}")
        print(f"\nAgent artifacts in: {agent_output_dir}")
        for f in sorted(agent_output_dir.iterdir()):
            if f.is_file():
                print(f"  - {f.name}")
        print(f"\nTranscript: {conversation.transcript_file}")

    return workspace


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run Claude Code conversation experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python orchestrator.py                    # Default: Alice & Bob, 20 turns
    python orchestrator.py --turns 10         # Shorter experiment
    python orchestrator.py --seed "emergence" # Start with a topic
    python orchestrator.py --agents A B C     # Three agents

Output goes to experiment_runs/run_TIMESTAMP/
        """,
    )

    parser.add_argument("--agents", nargs="+", default=DEFAULT_AGENTS, help="Agent names")
    parser.add_argument("--turns", type=int, default=NUM_TURNS, help="Turns per agent")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory")
    parser.add_argument("--seed", type=str, default=None, help="Seed topic to start conversation")
    parser.add_argument("--quiet", action="store_true", help="Reduce verbosity")
    parser.add_argument("--swarm", action="store_true", help="Use generic agent names")
    parser.add_argument("--num-swarm-agents", type=int, default=3, help="Number of swarm agents")

    args = parser.parse_args()

    agents = [f"Agent{i+1}" for i in range(args.num_swarm_agents)] if args.swarm else args.agents

    workspace = run_experiment(
        agents=agents,
        num_turns=args.turns,
        output_dir=args.output_dir,
        verbose=not args.quiet,
        seed_topic=args.seed,
    )

    print(f"\nResults saved to: {workspace}")


if __name__ == "__main__":
    main()
