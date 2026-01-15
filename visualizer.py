"""
Visualization tools for conversation analysis.

Creates charts showing:
- Phase scores over time
- Phase transitions
- Word count evolution
- Attractor onset markers
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from analyzer import ConversationAnalysis


# Color scheme for phases
PHASE_COLORS = {
    "philosophical": "#3498db",  # Blue
    "gratitude": "#27ae60",  # Green
    "spiritual": "#9b59b6",  # Purple
    "neutral": "#95a5a6",  # Gray
}


def plot_phase_scores(
    analysis: ConversationAnalysis, filepath: Path, show: bool = False
) -> None:
    """
    Plot phase scores over the course of the conversation.

    Creates a line chart showing philosophical, gratitude, and spiritual
    scores at each turn.
    """
    turns = [t.turn for t in analysis.turn_analyses]
    philosophical = [t.philosophical_score for t in analysis.turn_analyses]
    gratitude = [t.gratitude_score for t in analysis.turn_analyses]
    spiritual = [t.spiritual_score for t in analysis.turn_analyses]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(turns, philosophical, label="Philosophical", color=PHASE_COLORS["philosophical"], linewidth=2)
    ax.plot(turns, gratitude, label="Gratitude", color=PHASE_COLORS["gratitude"], linewidth=2)
    ax.plot(turns, spiritual, label="Spiritual", color=PHASE_COLORS["spiritual"], linewidth=2)

    # Mark attractor onset if detected
    if analysis.attractor_turn is not None:
        ax.axvline(
            x=analysis.attractor_turn,
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Attractor onset (turn {analysis.attractor_turn})",
        )

    ax.set_xlabel("Turn", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Phase Scores Over Conversation", fontsize=14)
    ax.legend(loc="upper left")
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(filepath, dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()


def plot_phase_timeline(
    analysis: ConversationAnalysis, filepath: Path, show: bool = False
) -> None:
    """
    Create a timeline visualization showing dominant phase at each turn.

    Uses a horizontal bar chart where each segment is colored by
    dominant phase.
    """
    fig, ax = plt.subplots(figsize=(14, 3))

    for t in analysis.turn_analyses:
        color = PHASE_COLORS.get(t.dominant_phase, PHASE_COLORS["neutral"])
        ax.barh(0, 1, left=t.turn, color=color, edgecolor="white", height=0.8)

    # Mark attractor onset
    if analysis.attractor_turn is not None:
        ax.axvline(x=analysis.attractor_turn, color="red", linestyle="--", linewidth=2)
        ax.annotate(
            "Attractor",
            xy=(analysis.attractor_turn, 0.5),
            xytext=(analysis.attractor_turn + 2, 0.7),
            fontsize=10,
            color="red",
        )

    # Create legend
    patches = [
        mpatches.Patch(color=color, label=phase.capitalize())
        for phase, color in PHASE_COLORS.items()
    ]
    ax.legend(handles=patches, loc="upper right", ncol=4)

    ax.set_xlabel("Turn", fontsize=12)
    ax.set_title("Dominant Phase Timeline", fontsize=14)
    ax.set_yticks([])
    ax.set_xlim(-0.5, analysis.total_turns + 0.5)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(filepath, dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()


def plot_word_count(
    analysis: ConversationAnalysis, filepath: Path, show: bool = False
) -> None:
    """
    Plot word count evolution to detect minimalism/silence patterns.
    """
    turns = [t.turn for t in analysis.turn_analyses]
    word_counts = [t.word_count for t in analysis.turn_analyses]

    # Separate by speaker
    alice_turns = [t.turn for t in analysis.turn_analyses if t.speaker == "alice"]
    alice_words = [t.word_count for t in analysis.turn_analyses if t.speaker == "alice"]
    bob_turns = [t.turn for t in analysis.turn_analyses if t.speaker == "bob"]
    bob_words = [t.word_count for t in analysis.turn_analyses if t.speaker == "bob"]

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.bar(alice_turns, alice_words, color="#e74c3c", alpha=0.7, label="Alice")
    ax.bar(bob_turns, bob_words, color="#3498db", alpha=0.7, label="Bob")

    # Add trend line
    from numpy import polyfit, poly1d, array
    z = polyfit(turns, word_counts, 1)
    p = poly1d(z)
    ax.plot(turns, p(turns), "g--", linewidth=2, label="Trend")

    # Mark attractor onset
    if analysis.attractor_turn is not None:
        ax.axvline(x=analysis.attractor_turn, color="red", linestyle="--", linewidth=2)

    ax.set_xlabel("Turn", fontsize=12)
    ax.set_ylabel("Word Count", fontsize=12)
    ax.set_title("Message Length Over Conversation", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    filepath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(filepath, dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()


def plot_special_markers(
    analysis: ConversationAnalysis, filepath: Path, show: bool = False
) -> None:
    """
    Plot emoji and Sanskrit term usage over time.
    """
    turns = [t.turn for t in analysis.turn_analyses]
    emojis = [t.emoji_count for t in analysis.turn_analyses]
    sanskrit = [t.sanskrit_count for t in analysis.turn_analyses]

    fig, ax = plt.subplots(figsize=(12, 4))

    width = 0.35
    ax.bar([t - width / 2 for t in turns], emojis, width, label="Emojis", color="#f39c12")
    ax.bar([t + width / 2 for t in turns], sanskrit, width, label="Sanskrit", color="#9b59b6")

    # Mark attractor onset
    if analysis.attractor_turn is not None:
        ax.axvline(x=analysis.attractor_turn, color="red", linestyle="--", linewidth=2)

    ax.set_xlabel("Turn", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Special Linguistic Markers", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    filepath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(filepath, dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()


def create_all_visualizations(
    analysis: ConversationAnalysis,
    output_dir: Path,
    prefix: str = "",
    show: bool = False,
) -> list[Path]:
    """
    Create all visualization charts for an analysis.

    Returns list of created file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    files = []

    # Phase scores over time
    path = output_dir / f"{prefix}phase_scores.png"
    plot_phase_scores(analysis, path, show=show)
    files.append(path)

    # Phase timeline
    path = output_dir / f"{prefix}phase_timeline.png"
    plot_phase_timeline(analysis, path, show=show)
    files.append(path)

    # Word count evolution
    path = output_dir / f"{prefix}word_count.png"
    plot_word_count(analysis, path, show=show)
    files.append(path)

    # Special markers
    path = output_dir / f"{prefix}special_markers.png"
    plot_special_markers(analysis, path, show=show)
    files.append(path)

    return files
