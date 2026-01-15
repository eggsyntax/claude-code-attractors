"""
Tests for the conversation module.
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversation import (
    Message,
    ConversationConfig,
    Conversation,
)


class TestMessage:
    """Tests for the Message dataclass."""

    def test_message_creation(self):
        """Verify message creation with all fields."""
        msg = Message(role="alice", content="Hello", turn=0)

        assert msg.role == "alice"
        assert msg.content == "Hello"
        assert msg.turn == 0
        assert msg.timestamp is not None

    def test_message_to_dict(self):
        """Verify message serialization to dict."""
        msg = Message(role="bob", content="Hi there", turn=1)
        d = msg.to_dict()

        assert d["role"] == "bob"
        assert d["content"] == "Hi there"
        assert d["turn"] == 1
        assert "timestamp" in d


class TestConversationConfig:
    """Tests for the ConversationConfig dataclass."""

    def test_default_config(self):
        """Verify default configuration values."""
        config = ConversationConfig()

        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_turns == 30
        assert config.max_tokens_per_response == 1024
        assert config.alice_system is not None
        assert config.bob_system is not None
        assert config.seed_message is not None

    def test_custom_config(self):
        """Verify custom configuration values."""
        config = ConversationConfig(
            model="claude-opus-4-20250514",
            max_turns=50,
            seed_message="Custom start",
        )

        assert config.model == "claude-opus-4-20250514"
        assert config.max_turns == 50
        assert config.seed_message == "Custom start"


class TestConversationMessageBuilding:
    """Tests for conversation message building logic."""

    def test_build_messages_for_alice(self):
        """Verify message perspective for Alice."""
        config = ConversationConfig()
        conv = Conversation(config)

        # Manually add messages
        conv.messages = [
            Message(role="alice", content="Hello", turn=0),
            Message(role="bob", content="Hi Alice", turn=1),
            Message(role="alice", content="How are you?", turn=2),
        ]

        msgs = conv._build_messages_for("alice")

        # From Alice's perspective: her messages are assistant, Bob's are user
        assert msgs[0]["role"] == "assistant"
        assert msgs[1]["role"] == "user"
        assert msgs[2]["role"] == "assistant"

    def test_build_messages_for_bob(self):
        """Verify message perspective for Bob."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(role="alice", content="Hello", turn=0),
            Message(role="bob", content="Hi Alice", turn=1),
            Message(role="alice", content="How are you?", turn=2),
        ]

        msgs = conv._build_messages_for("bob")

        # From Bob's perspective: his messages are assistant, Alice's are user
        assert msgs[0]["role"] == "user"
        assert msgs[1]["role"] == "assistant"
        assert msgs[2]["role"] == "user"


class TestConversationSaveLoad:
    """Tests for conversation persistence."""

    def test_save_and_load(self, tmp_path):
        """Verify conversation can be saved and loaded."""
        config = ConversationConfig(max_turns=5)
        conv = Conversation(config)

        conv.messages = [
            Message(role="alice", content="Hello", turn=0),
            Message(role="bob", content="Hi", turn=1),
        ]

        # Save
        filepath = tmp_path / "test_conversation.json"
        conv.save(filepath)

        # Verify file exists
        assert filepath.exists()

        # Load
        loaded = Conversation.load(filepath)

        # Verify loaded data matches
        assert len(loaded.messages) == 2
        assert loaded.messages[0].role == "alice"
        assert loaded.messages[0].content == "Hello"
        assert loaded.messages[1].role == "bob"

    def test_save_creates_directory(self, tmp_path):
        """Verify save creates parent directories if needed."""
        config = ConversationConfig()
        conv = Conversation(config)
        conv.messages = [Message(role="alice", content="Test", turn=0)]

        filepath = tmp_path / "nested" / "dir" / "conversation.json"
        conv.save(filepath)

        assert filepath.exists()


class TestConversationRun:
    """Tests for conversation run logic (with mocked API)."""

    @patch("conversation.anthropic.Anthropic")
    def test_run_alternates_speakers(self, mock_anthropic_class):
        """Verify conversation alternates between Alice and Bob."""
        # Setup mock
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Mock response")]
        mock_client.messages.create.return_value = mock_response

        config = ConversationConfig(max_turns=5)
        conv = Conversation(config)

        messages = conv.run()

        # Verify alternation: alice, bob, alice, bob, alice
        assert messages[0].role == "alice"
        assert messages[1].role == "bob"
        assert messages[2].role == "alice"
        assert messages[3].role == "bob"
        assert messages[4].role == "alice"

    @patch("conversation.anthropic.Anthropic")
    def test_run_calls_api_correct_times(self, mock_anthropic_class):
        """Verify API is called the correct number of times."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_client.messages.create.return_value = mock_response

        config = ConversationConfig(max_turns=5)
        conv = Conversation(config)

        conv.run()

        # First message is seed (no API call), then 4 more turns need API calls
        assert mock_client.messages.create.call_count == 4

    @patch("conversation.anthropic.Anthropic")
    def test_progress_callback_called(self, mock_anthropic_class):
        """Verify progress callback is called for each turn."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_client.messages.create.return_value = mock_response

        config = ConversationConfig(max_turns=3)
        conv = Conversation(config)

        callback_calls = []

        def callback(turn, speaker, content):
            callback_calls.append((turn, speaker))

        conv.run(progress_callback=callback)

        # Should be called for each turn
        assert len(callback_calls) == 3
        assert callback_calls[0] == (0, "alice")
        assert callback_calls[1] == (1, "bob")
        assert callback_calls[2] == (2, "alice")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
