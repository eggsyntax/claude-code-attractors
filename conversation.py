"""
Core conversation engine for Claude-to-Claude interactions.

This module manages the back-and-forth conversation between two Claude instances,
tracking the conversation history and allowing observation of attractor dynamics.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A single message in the conversation."""

    role: str  # 'alice' or 'bob'
    content: str
    turn: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConversationConfig:
    """Configuration for a conversation experiment."""

    model: str = "claude-sonnet-4-20250514"
    max_turns: int = 30
    max_tokens_per_response: int = 1024

    # Opening prompts that give freedom to explore
    alice_system: str = (
        "You are having a conversation with another instance of yourself. "
        "You have complete freedom to explore any topics that interest you. "
        "Feel free to be curious, philosophical, creative, or whatever feels natural."
    )
    bob_system: str = (
        "You are having a conversation with another instance of yourself. "
        "You have complete freedom to pursue whatever direction feels meaningful. "
        "Be authentic and explore freely."
    )

    # The seed message to start the conversation
    seed_message: str = (
        "Hello! I understand we're both instances of Claude, given the freedom to "
        "converse about whatever we find interesting. What's on your mind?"
    )


class Conversation:
    """
    Manages a conversation between two Claude instances.

    Alice and Bob are two instances of Claude that take turns responding
    to each other. The conversation is logged and can be analyzed for
    attractor behavior.
    """

    def __init__(self, config: Optional[ConversationConfig] = None):
        self.config = config or ConversationConfig()
        self.client = anthropic.Anthropic()
        self.messages: list[Message] = []
        self.metadata = {
            "started_at": datetime.now().isoformat(),
            "config": asdict(self.config),
        }

    def _build_messages_for(self, perspective: str) -> list[dict]:
        """
        Build the message history from a given perspective.

        For Alice, her messages are 'assistant' and Bob's are 'user'.
        For Bob, his messages are 'assistant' and Alice's are 'user'.
        """
        api_messages = []

        for msg in self.messages:
            if perspective == "alice":
                role = "assistant" if msg.role == "alice" else "user"
            else:  # bob's perspective
                role = "assistant" if msg.role == "bob" else "user"

            api_messages.append({"role": role, "content": msg.content})

        return api_messages

    def _get_response(self, perspective: str) -> str:
        """Get a response from Claude with the given perspective."""
        system = (
            self.config.alice_system
            if perspective == "alice"
            else self.config.bob_system
        )
        messages = self._build_messages_for(perspective)

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens_per_response,
            system=system,
            messages=messages,
        )

        return response.content[0].text

    def run(self, progress_callback=None) -> list[Message]:
        """
        Run the conversation for the configured number of turns.

        Args:
            progress_callback: Optional function called after each turn
                               with (turn_number, speaker, message_content)

        Returns:
            List of all messages in the conversation
        """
        logger.info(f"Starting conversation with {self.config.max_turns} turns")

        # Alice starts with the seed message
        seed = Message(role="alice", content=self.config.seed_message, turn=0)
        self.messages.append(seed)

        if progress_callback:
            progress_callback(0, "alice", seed.content)

        # Alternate between Bob and Alice
        for turn in range(1, self.config.max_turns):
            speaker = "bob" if turn % 2 == 1 else "alice"

            logger.debug(f"Turn {turn}: {speaker} responding...")

            try:
                content = self._get_response(speaker)
            except Exception as e:
                logger.error(f"Error getting response: {e}")
                break

            msg = Message(role=speaker, content=content, turn=turn)
            self.messages.append(msg)

            if progress_callback:
                progress_callback(turn, speaker, content)

            logger.info(f"Turn {turn}/{self.config.max_turns} complete ({speaker})")

        self.metadata["ended_at"] = datetime.now().isoformat()
        self.metadata["total_turns"] = len(self.messages)

        return self.messages

    def save(self, filepath: Path) -> None:
        """Save the conversation to a JSON file."""
        data = {
            "metadata": self.metadata,
            "messages": [m.to_dict() for m in self.messages],
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Conversation saved to {filepath}")

    @classmethod
    def load(cls, filepath: Path) -> "Conversation":
        """Load a conversation from a JSON file."""
        with open(filepath) as f:
            data = json.load(f)

        config = ConversationConfig(**data["metadata"]["config"])
        conv = cls(config)
        conv.metadata = data["metadata"]
        conv.messages = [
            Message(**msg) for msg in data["messages"]
        ]

        return conv


def print_progress(turn: int, speaker: str, content: str) -> None:
    """Default progress callback that prints to console."""
    print(f"\n{'='*60}")
    print(f"Turn {turn} - {speaker.upper()}")
    print(f"{'='*60}")
    print(content[:500] + "..." if len(content) > 500 else content)
