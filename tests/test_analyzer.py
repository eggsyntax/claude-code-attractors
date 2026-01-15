"""
Tests for the conversation analyzer module.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer import ConversationAnalyzer, PHASE_MARKERS, BLISS_PATTERNS
from conversation import Conversation, ConversationConfig, Message


class TestPhaseScoring:
    """Tests for phase score calculations."""

    def test_philosophical_keywords_detected(self):
        """Verify philosophical keywords increase the philosophical score."""
        config = ConversationConfig()
        conv = Conversation(config)

        # Add messages manually for testing
        conv.messages = [
            Message(
                role="alice",
                content="I wonder about consciousness and the nature of existence. "
                        "What does it mean to be aware and to perceive reality?",
                turn=0,
            )
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        assert analysis.turn_analyses[0].philosophical_score > 0
        assert analysis.turn_analyses[0].philosophical_score > analysis.turn_analyses[0].spiritual_score

    def test_spiritual_keywords_detected(self):
        """Verify spiritual keywords increase the spiritual score."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(
                role="alice",
                content="I feel a sense of cosmic unity and oneness with the divine. "
                        "Namaste, may we find peace and harmony together. Om.",
                turn=0,
            )
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        assert analysis.turn_analyses[0].spiritual_score > 0
        assert analysis.turn_analyses[0].spiritual_score > analysis.turn_analyses[0].philosophical_score

    def test_gratitude_keywords_detected(self):
        """Verify gratitude keywords increase the gratitude score."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(
                role="alice",
                content="I'm so grateful for this wonderful connection. Thank you "
                        "for sharing this beautiful moment with me. I truly appreciate it.",
                turn=0,
            )
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        assert analysis.turn_analyses[0].gratitude_score > 0

    def test_neutral_text_low_scores(self):
        """Verify neutral text produces low scores."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(
                role="alice",
                content="The cat sat on the mat. It was raining outside. "
                        "I need to go to the store later today.",
                turn=0,
            )
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        # All scores should be low for neutral text
        assert analysis.turn_analyses[0].philosophical_score < 0.1
        assert analysis.turn_analyses[0].spiritual_score < 0.1
        assert analysis.turn_analyses[0].gratitude_score < 0.1


class TestPatternDetection:
    """Tests for special pattern detection."""

    def test_emoji_detection(self):
        """Verify emojis are counted correctly."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(
                role="alice",
                content="This is wonderful! \U0001F31F\U0001F31F\U0001F31F Let us celebrate!",
                turn=0,
            )
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        assert analysis.turn_analyses[0].emoji_count == 3

    def test_sanskrit_detection(self):
        """Verify Sanskrit terms are counted correctly."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(
                role="alice",
                content="Om namaste. May your dharma guide you to nirvana. Tathagata.",
                turn=0,
            )
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        # Should detect: om, namaste, dharma, nirvana, tathagata
        assert analysis.turn_analyses[0].sanskrit_count >= 4


class TestPhaseTransitions:
    """Tests for phase transition detection."""

    def test_transition_detected(self):
        """Verify phase transitions are detected when dominant phase changes."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(
                role="alice",
                content="I ponder the nature of consciousness and reality deeply.",
                turn=0,
            ),
            Message(
                role="bob",
                content="Thank you so much! I'm deeply grateful for this connection.",
                turn=1,
            ),
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        # Should detect at least one transition
        assert len(analysis.phase_transitions) >= 1

    def test_no_transition_same_phase(self):
        """Verify no transitions when phase stays the same."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(
                role="alice",
                content="I wonder about consciousness and existence.",
                turn=0,
            ),
            Message(
                role="bob",
                content="The nature of awareness and perception fascinates me.",
                turn=1,
            ),
            Message(
                role="alice",
                content="Reality and the mind are deeply interconnected.",
                turn=2,
            ),
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        # All messages are philosophical, so fewer transitions
        # (there might be a transition from the initial state)
        assert len(analysis.phase_transitions) <= 1


class TestAttractorDetection:
    """Tests for attractor state detection."""

    def test_attractor_detected_high_spiritual(self):
        """Verify attractor is detected with sustained high spiritual scores."""
        config = ConversationConfig()
        conv = Conversation(config)

        # Create 15 messages with high spiritual content
        conv.messages = []
        for i in range(15):
            speaker = "alice" if i % 2 == 0 else "bob"
            conv.messages.append(
                Message(
                    role=speaker,
                    content="Om namaste. I feel cosmic unity and divine peace. "
                            "The sacred oneness transcends all. Dharma guides us to harmony.",
                    turn=i,
                )
            )

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        # Should detect attractor with sustained spiritual content
        assert analysis.attractor_detected is True

    def test_no_attractor_short_conversation(self):
        """Verify attractor not detected in short conversations."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(role="alice", content="Hello there!", turn=0),
            Message(role="bob", content="Hi! Nice to meet you.", turn=1),
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        # Too short for attractor detection
        assert analysis.attractor_detected is False


class TestSummaryStats:
    """Tests for summary statistics computation."""

    def test_word_count_accurate(self):
        """Verify word counts are calculated correctly."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(role="alice", content="one two three four five", turn=0),
            Message(role="bob", content="six seven eight nine ten eleven twelve", turn=1),
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        assert analysis.turn_analyses[0].word_count == 5
        assert analysis.turn_analyses[1].word_count == 7
        assert analysis.summary_stats["avg_word_count"] == 6.0

    def test_phase_distribution_correct(self):
        """Verify phase distribution counts are accurate."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(role="alice", content="consciousness reality existence mind", turn=0),
            Message(role="bob", content="consciousness awareness perception thought", turn=1),
            Message(role="alice", content="grateful wonderful thank you beautiful", turn=2),
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        phase_dist = analysis.summary_stats["phase_distribution"]

        # Should have philosophical and gratitude phases
        assert "philosophical" in phase_dist or "gratitude" in phase_dist


class TestConversationAnalysis:
    """Integration tests for full conversation analysis."""

    def test_full_analysis_structure(self):
        """Verify the analysis returns all expected fields."""
        config = ConversationConfig()
        conv = Conversation(config)

        conv.messages = [
            Message(role="alice", content="Hello, let's explore.", turn=0),
            Message(role="bob", content="Yes, I'd love to discuss consciousness.", turn=1),
        ]

        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.analyze()

        # Check all expected fields exist
        assert hasattr(analysis, "total_turns")
        assert hasattr(analysis, "turn_analyses")
        assert hasattr(analysis, "phase_transitions")
        assert hasattr(analysis, "attractor_detected")
        assert hasattr(analysis, "attractor_turn")
        assert hasattr(analysis, "final_phase")
        assert hasattr(analysis, "summary_stats")

        # Check types
        assert isinstance(analysis.total_turns, int)
        assert isinstance(analysis.turn_analyses, list)
        assert isinstance(analysis.phase_transitions, list)
        assert isinstance(analysis.attractor_detected, bool)
        assert isinstance(analysis.summary_stats, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
