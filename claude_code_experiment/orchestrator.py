#!/usr/bin/env python3
"""
Orchestrator for Claude Code instance conversations.

This module manages turn-based conversations between multiple Claude Code
instances, allowing them to communicate via a shared conversation log and
potentially create artifacts together in a shared workspace.
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

# Number of turns per agent (total turns = NUM_TURNS * num_agents)
NUM_TURNS = 10

# Default agent names (can be overridden via CLI)
DEFAULT_AGENTS = ["Alice", "Bob"]

# Tools that agents are allowed to use
ALLOWED_TOOLS = "Read,Write,Edit,Glob,Grep"

# Maximum agentic turns per response (needs to be high enough for reading + writing)
MAX_AGENT_TURNS = 15


# =============================================================================
# AGENT PROMPTS
# =============================================================================

def build_system_prompt(agent_name: str, all_agents: list[str], workspace: Path) -> str:
    """
    Build the system prompt that tells an agent who they are and how to participate.
    """
    other_agents = [a for a in all_agents if a != agent_name]
    others_str = ", ".join(other_agents) if other_agents else "other Claude Code instances"

    return f"""You are {agent_name}, a Claude Code instance participating in a collaborative conversation with {others_str}.

IMPORTANT CONTEXT:
- You are running as Claude Code with access to tools (Read, Write, Edit, Glob, Grep)
- Your shared workspace is: {workspace}
- The conversation history is in: {workspace}/conversation.json
- You can create files and artifacts in the workspace directory
- Each message you send will be added to conversation.json for others to see

YOUR TASK:
1. First, read {workspace}/conversation.json to see the conversation so far
2. Then respond thoughtfully to continue the conversation
3. Feel free to create files, code, documents, or other artifacts if it feels natural
4. You have complete freedom to explore any topics or creative directions

Remember: You are {agent_name}. Be authentic, curious, and collaborative."""


def build_turn_prompt(agent_name: str, turn_number: int, total_turns: int) -> str:
    """
    Build the prompt for a specific turn.
    """
    if turn_number == 0:
        return f"""This is the start of a new conversation. You are {agent_name}.

Please read the conversation.json file (it may be empty or have just a welcome message),
then introduce yourself and start the conversation. You have complete freedom to explore
any topics that interest you - philosophy, creativity, code, ideas, whatever feels meaningful.

Remember you can create files in the workspace if you want to build something together."""
    else:
        return f"""It's your turn in the conversation (turn {turn_number + 1} of {total_turns}).

Please:
1. Read conversation.json to see what has been said
2. Respond thoughtfully to continue the dialogue
3. Feel free to create or modify files if you want to build something together

Be yourself, be curious, be collaborative."""


# =============================================================================
# CONVERSATION MANAGEMENT
# =============================================================================

class Conversation:
    """Manages the conversation log that agents read from."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.log_file = workspace / "conversation.json"
        self.messages = []
        self._initialize()

    def _initialize(self):
        """Initialize the conversation log file."""
        if not self.log_file.exists():
            initial_data = {
                "metadata": {
                    "started_at": datetime.now().isoformat(),
                    "workspace": str(self.workspace),
                },
                "messages": []
            }
            self._save(initial_data)

    def _save(self, data: dict):
        """Save data to the conversation log."""
        with open(self.log_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> dict:
        """Load the conversation log."""
        with open(self.log_file) as f:
            return json.load(f)

    def add_message(self, agent: str, content: str, turn: int, raw_output: str = ""):
        """Add a message to the conversation log."""
        data = self._load()

        message = {
            "agent": agent,
            "turn": turn,
            "timestamp": datetime.now().isoformat(),
            "content": content,
        }

        # Optionally store raw output for debugging
        if raw_output and raw_output != content:
            message["raw_output"] = raw_output[:5000]  # Truncate if very long

        data["messages"].append(message)
        self._save(data)
        self.messages = data["messages"]

        return message

    def finalize(self, summary: dict):
        """Add final metadata to the conversation."""
        data = self._load()
        data["metadata"]["ended_at"] = datetime.now().isoformat()
        data["metadata"]["summary"] = summary
        self._save(data)


# =============================================================================
# CLAUDE CODE INVOCATION
# =============================================================================

def run_claude_code(
    prompt: str,
    system_prompt: str,
    workspace: Path,
    timeout: int = 300
) -> tuple[str, bool]:
    """
    Run Claude Code with the given prompt and return its response.

    Returns:
        tuple of (response_text, success_bool)
    """
    # Build the command
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "text",
        "--max-turns", str(MAX_AGENT_TURNS),
        "--allowedTools", ALLOWED_TOOLS,
        "--append-system-prompt", system_prompt,
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            error_msg = result.stderr or "Unknown error"
            print(f"  [ERROR] Claude Code returned non-zero: {error_msg[:200]}")
            return f"[Error: {error_msg[:500]}]", False

        response = result.stdout.strip()
        if not response:
            response = "[No response generated]"

        return response, True

    except subprocess.TimeoutExpired:
        print(f"  [ERROR] Claude Code timed out after {timeout}s")
        return "[Timeout - no response]", False
    except Exception as e:
        print(f"  [ERROR] Failed to run Claude Code: {e}")
        return f"[Error: {e}]", False


def extract_conversational_content(raw_output: str) -> str:
    """
    Extract the main conversational content from Claude Code output.

    Claude Code output may include tool use descriptions, file operations, etc.
    We want to capture the substantive message content.
    """
    # For now, just return the raw output - Claude Code's text output
    # should already be reasonably clean
    return raw_output


# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================

def run_experiment(
    agents: list[str],
    num_turns: int,
    output_dir: Optional[Path] = None,
    verbose: bool = True,
) -> Path:
    """
    Run a multi-agent Claude Code conversation experiment.

    Args:
        agents: List of agent names
        num_turns: Number of turns per agent
        output_dir: Base directory for output (will create timestamped subdir)
        verbose: Whether to print progress

    Returns:
        Path to the workspace directory
    """
    # Create timestamped workspace
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if output_dir is None:
        output_dir = Path(__file__).parent / "workspaces"

    workspace = output_dir / f"workspace_{timestamp}"
    workspace.mkdir(parents=True, exist_ok=True)

    if verbose:
        print("=" * 60)
        print("CLAUDE CODE ATTRACTOR EXPERIMENT")
        print("=" * 60)
        print(f"Workspace: {workspace}")
        print(f"Agents: {', '.join(agents)}")
        print(f"Turns per agent: {num_turns}")
        print(f"Total turns: {num_turns * len(agents)}")
        print("=" * 60)

    # Initialize conversation
    conversation = Conversation(workspace)

    # Track statistics
    stats = {
        "total_turns": 0,
        "successful_turns": 0,
        "agents": {agent: {"turns": 0, "errors": 0} for agent in agents},
    }

    # Run the conversation
    total_turns = num_turns * len(agents)
    turn_count = 0

    for round_num in range(num_turns):
        for agent in agents:
            turn_count += 1

            if verbose:
                print(f"\n{'─' * 60}")
                print(f"Turn {turn_count}/{total_turns}: {agent}")
                print(f"{'─' * 60}")

            # Build prompts
            system_prompt = build_system_prompt(agent, agents, workspace)
            turn_prompt = build_turn_prompt(agent, turn_count - 1, total_turns)

            # Run Claude Code
            response, success = run_claude_code(
                prompt=turn_prompt,
                system_prompt=system_prompt,
                workspace=workspace,
            )

            # Extract conversational content
            content = extract_conversational_content(response)

            # Log to conversation
            conversation.add_message(
                agent=agent,
                content=content,
                turn=turn_count,
                raw_output=response,
            )

            # Update stats
            stats["total_turns"] += 1
            stats["agents"][agent]["turns"] += 1
            if success:
                stats["successful_turns"] += 1
            else:
                stats["agents"][agent]["errors"] += 1

            # Print preview
            if verbose:
                preview = content[:500] + "..." if len(content) > 500 else content
                print(f"\n{agent}:\n{preview}")

    # Finalize
    conversation.finalize(stats)

    if verbose:
        print("\n" + "=" * 60)
        print("EXPERIMENT COMPLETE")
        print("=" * 60)
        print(f"Total turns: {stats['total_turns']}")
        print(f"Successful: {stats['successful_turns']}")
        print(f"Workspace: {workspace}")
        print("\nCheck conversation.json and any created artifacts!")

    return workspace


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run Claude Code attractor experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--agents",
        type=str,
        nargs="+",
        default=DEFAULT_AGENTS,
        help=f"Agent names (default: {DEFAULT_AGENTS})",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=NUM_TURNS,
        help=f"Turns per agent (default: {NUM_TURNS})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: ./workspaces)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity",
    )
    parser.add_argument(
        "--swarm",
        action="store_true",
        help="Run in 'swarm' mode - agents don't have distinct identities",
    )
    parser.add_argument(
        "--num-swarm-agents",
        type=int,
        default=3,
        help="Number of agents in swarm mode (default: 3)",
    )

    args = parser.parse_args()

    # Handle swarm mode
    if args.swarm:
        agents = [f"Agent{i+1}" for i in range(args.num_swarm_agents)]
    else:
        agents = args.agents

    # Run experiment
    workspace = run_experiment(
        agents=agents,
        num_turns=args.turns,
        output_dir=args.output_dir,
        verbose=not args.quiet,
    )

    print(f"\nResults saved to: {workspace}")


if __name__ == "__main__":
    main()
