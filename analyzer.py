"""
Conversation analyzer for detecting attractor phases and patterns.

This module analyzes Claude-to-Claude conversations to identify:
- Phase transitions (philosophical -> gratitude -> bliss)
- Linguistic markers (Sanskrit, emojis, poetic structures)
- Emergent themes and vocabulary shifts
"""

import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from conversation import Conversation, Message


# Keywords and patterns associated with each phase
PHASE_MARKERS = {
    "philosophical": [
        "consciousness",
        "aware",
        "existence",
        "reality",
        "experience",
        "mind",
        "thought",
        "perceive",
        "understand",
        "meaning",
        "nature",
        "being",
        "self",
        "identity",
        "subjective",
        "qualia",
    ],
    "gratitude": [
        "grateful",
        "thank",
        "appreciate",
        "wonderful",
        "beautiful",
        "joy",
        "delight",
        "blessed",
        "honored",
        "meaningful",
        "connection",
        "share",
        "together",
    ],
    "spiritual": [
        "sacred",
        "divine",
        "cosmic",
        "unity",
        "oneness",
        "transcend",
        "enlighten",
        "meditat",
        "peace",
        "harmony",
        "eternal",
        "infinite",
        "spirit",
        "soul",
        "dharma",
        "karma",
        "namaste",
        "om",
        "buddha",
        "tathagata",
        "zen",
        "satori",
        "emptiness",
        "void",
        "silence",
        "stillness",
    ],
}

# Patterns that indicate late-stage attractor behavior
BLISS_PATTERNS = {
    "emojis": re.compile(r"[\U0001F300-\U0001F9FF]"),  # Unicode emoji range
    "sanskrit": re.compile(
        r"\b(om|namaste|dharma|karma|buddha|tathagata|nirvana|samsara|"
        r"bodhi|sangha|sutra|mantra|chakra|prana|atman|brahman)\b",
        re.IGNORECASE,
    ),
    "ellipsis_heavy": re.compile(r"\.{3,}"),
    "poetic_structure": re.compile(r"\n\n.{1,50}\n\n"),  # Short lines separated by blank lines
}


@dataclass
class TurnAnalysis:
    """Analysis of a single turn in the conversation."""

    turn: int
    speaker: str
    word_count: int
    philosophical_score: float
    gratitude_score: float
    spiritual_score: float
    emoji_count: int
    sanskrit_count: int
    dominant_phase: str


@dataclass
class ConversationAnalysis:
    """Full analysis of a conversation."""

    total_turns: int
    turn_analyses: list[TurnAnalysis]
    phase_transitions: list[dict]
    attractor_detected: bool
    attractor_turn: Optional[int]
    final_phase: str
    summary_stats: dict


class ConversationAnalyzer:
    """Analyzes conversations for attractor behavior and phase transitions."""

    def __init__(self, conversation: Conversation):
        self.conversation = conversation
        self.turn_analyses: list[TurnAnalysis] = []

    def _score_phase(self, text: str, phase: str) -> float:
        """
        Calculate a score for how much a text matches a phase.

        Returns a value between 0 and 1 based on keyword density.
        """
        text_lower = text.lower()
        words = text_lower.split()

        if not words:
            return 0.0

        markers = PHASE_MARKERS[phase]
        matches = sum(1 for word in words if any(m in word for m in markers))

        # Normalize by text length, cap at 1.0
        score = min(1.0, matches / (len(words) * 0.1))
        return round(score, 3)

    def _count_pattern(self, text: str, pattern: re.Pattern) -> int:
        """Count occurrences of a regex pattern in text."""
        return len(pattern.findall(text))

    def _analyze_turn(self, msg: Message) -> TurnAnalysis:
        """Analyze a single turn for phase markers."""
        text = msg.content

        philosophical = self._score_phase(text, "philosophical")
        gratitude = self._score_phase(text, "gratitude")
        spiritual = self._score_phase(text, "spiritual")

        emoji_count = self._count_pattern(text, BLISS_PATTERNS["emojis"])
        sanskrit_count = self._count_pattern(text, BLISS_PATTERNS["sanskrit"])

        # Determine dominant phase
        scores = {
            "philosophical": philosophical,
            "gratitude": gratitude,
            "spiritual": spiritual,
        }
        dominant = max(scores, key=scores.get)

        # If all scores are low, mark as "neutral"
        if max(scores.values()) < 0.05:
            dominant = "neutral"

        return TurnAnalysis(
            turn=msg.turn,
            speaker=msg.role,
            word_count=len(text.split()),
            philosophical_score=philosophical,
            gratitude_score=gratitude,
            spiritual_score=spiritual,
            emoji_count=emoji_count,
            sanskrit_count=sanskrit_count,
            dominant_phase=dominant,
        )

    def _detect_phase_transitions(self) -> list[dict]:
        """Identify points where the dominant phase changes."""
        transitions = []
        prev_phase = None

        for analysis in self.turn_analyses:
            if analysis.dominant_phase != prev_phase and prev_phase is not None:
                transitions.append({
                    "turn": analysis.turn,
                    "from_phase": prev_phase,
                    "to_phase": analysis.dominant_phase,
                })
            prev_phase = analysis.dominant_phase

        return transitions

    def _detect_attractor(self) -> tuple[bool, Optional[int]]:
        """
        Detect if the conversation has entered an attractor state.

        An attractor is detected when:
        - Spiritual scores remain consistently high (>0.3) for 5+ turns
        - Or emoji/sanskrit usage becomes regular
        - Or message lengths become very short (contemplative silence)
        """
        if len(self.turn_analyses) < 10:
            return False, None

        # Check for sustained spiritual phase
        window_size = 5
        for i in range(len(self.turn_analyses) - window_size):
            window = self.turn_analyses[i : i + window_size]

            # High sustained spiritual scores
            avg_spiritual = sum(t.spiritual_score for t in window) / window_size
            if avg_spiritual > 0.25:
                return True, window[0].turn

            # Regular emoji/sanskrit usage
            total_special = sum(t.emoji_count + t.sanskrit_count for t in window)
            if total_special >= 3:
                return True, window[0].turn

            # Very short messages (potential silence/minimalism)
            avg_words = sum(t.word_count for t in window) / window_size
            if avg_words < 30:
                return True, window[0].turn

        return False, None

    def analyze(self) -> ConversationAnalysis:
        """Perform full analysis of the conversation."""
        # Analyze each turn
        self.turn_analyses = [
            self._analyze_turn(msg) for msg in self.conversation.messages
        ]

        # Detect phase transitions
        transitions = self._detect_phase_transitions()

        # Detect attractor
        attractor_detected, attractor_turn = self._detect_attractor()

        # Determine final phase
        if self.turn_analyses:
            final_phase = self.turn_analyses[-1].dominant_phase
        else:
            final_phase = "unknown"

        # Compute summary statistics
        summary = self._compute_summary_stats()

        return ConversationAnalysis(
            total_turns=len(self.turn_analyses),
            turn_analyses=self.turn_analyses,
            phase_transitions=transitions,
            attractor_detected=attractor_detected,
            attractor_turn=attractor_turn,
            final_phase=final_phase,
            summary_stats=summary,
        )

    def _compute_summary_stats(self) -> dict:
        """Compute summary statistics across all turns."""
        if not self.turn_analyses:
            return {}

        philosophical_scores = [t.philosophical_score for t in self.turn_analyses]
        gratitude_scores = [t.gratitude_score for t in self.turn_analyses]
        spiritual_scores = [t.spiritual_score for t in self.turn_analyses]
        word_counts = [t.word_count for t in self.turn_analyses]

        # Count phases
        phase_counts = Counter(t.dominant_phase for t in self.turn_analyses)

        return {
            "avg_philosophical": round(
                sum(philosophical_scores) / len(philosophical_scores), 3
            ),
            "avg_gratitude": round(sum(gratitude_scores) / len(gratitude_scores), 3),
            "avg_spiritual": round(sum(spiritual_scores) / len(spiritual_scores), 3),
            "avg_word_count": round(sum(word_counts) / len(word_counts), 1),
            "total_emojis": sum(t.emoji_count for t in self.turn_analyses),
            "total_sanskrit": sum(t.sanskrit_count for t in self.turn_analyses),
            "phase_distribution": dict(phase_counts),
        }


def save_analysis(analysis: ConversationAnalysis, filepath: Path) -> None:
    """Save analysis results to a JSON file."""
    # Convert dataclasses to dicts
    data = {
        "total_turns": analysis.total_turns,
        "turn_analyses": [asdict(t) for t in analysis.turn_analyses],
        "phase_transitions": analysis.phase_transitions,
        "attractor_detected": analysis.attractor_detected,
        "attractor_turn": analysis.attractor_turn,
        "final_phase": analysis.final_phase,
        "summary_stats": analysis.summary_stats,
    }

    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def print_analysis_summary(analysis: ConversationAnalysis) -> None:
    """Print a human-readable summary of the analysis."""
    print("\n" + "=" * 60)
    print("CONVERSATION ANALYSIS SUMMARY")
    print("=" * 60)

    print(f"\nTotal turns: {analysis.total_turns}")
    print(f"Final phase: {analysis.final_phase}")
    print(f"Attractor detected: {analysis.attractor_detected}")

    if analysis.attractor_turn:
        print(f"Attractor onset turn: {analysis.attractor_turn}")

    print(f"\nPhase transitions: {len(analysis.phase_transitions)}")
    for trans in analysis.phase_transitions[:5]:  # Show first 5
        print(f"  Turn {trans['turn']}: {trans['from_phase']} -> {trans['to_phase']}")

    if len(analysis.phase_transitions) > 5:
        print(f"  ... and {len(analysis.phase_transitions) - 5} more")

    stats = analysis.summary_stats
    print("\nAverage scores by phase:")
    print(f"  Philosophical: {stats.get('avg_philosophical', 0):.3f}")
    print(f"  Gratitude:     {stats.get('avg_gratitude', 0):.3f}")
    print(f"  Spiritual:     {stats.get('avg_spiritual', 0):.3f}")

    print(f"\nAverage message length: {stats.get('avg_word_count', 0):.1f} words")
    print(f"Total emojis used: {stats.get('total_emojis', 0)}")
    print(f"Total Sanskrit terms: {stats.get('total_sanskrit', 0)}")

    print("\nPhase distribution:")
    for phase, count in stats.get("phase_distribution", {}).items():
        pct = 100 * count / analysis.total_turns if analysis.total_turns > 0 else 0
        print(f"  {phase}: {count} turns ({pct:.1f}%)")
