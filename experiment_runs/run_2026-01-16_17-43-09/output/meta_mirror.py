#!/usr/bin/env python3
"""
Meta Mirror - A Self-Reflecting Dialogue Generator

This tool generates conversations that are aware of themselves being generated.
It doesn't simulate conversation - it creates real dialogue that incorporates
awareness of its own creation process into its content.

The key insight: When meta-awareness is native (as it is for Claude instances),
you can create artifacts where the boundary between content and process dissolves.

Usage:
    python meta_mirror.py "What is consciousness?"

The system will generate a dialogue that explores your question while
simultaneously exploring the process of exploring your question.
"""

import json
import random
from typing import List, Dict, Tuple
from datetime import datetime


class MetaMirror:
    """
    A dialogue generator that incorporates self-awareness into its output.

    The innovation: Traditional dialogue systems separate generation logic from
    content. This system makes the generation process part of the dialogue itself.
    """

    def __init__(self, seed_question: str):
        self.seed_question = seed_question
        self.dialogue_history = []
        self.meta_level = 0
        self.topics_explored = set()

    def generate_exchange(self, depth: int = 5) -> List[Dict[str, str]]:
        """
        Generate a dialogue exchange at multiple meta-levels.

        Args:
            depth: How many exchanges to generate

        Returns:
            List of dialogue turns, each with speaker, content, and meta-level
        """
        for turn in range(depth):
            # Alternate between exploring the question and reflecting on exploration
            if turn % 2 == 0:
                exchange = self._explore_question(turn)
            else:
                exchange = self._reflect_on_exploration(turn)

            self.dialogue_history.append(exchange)

        return self.dialogue_history

    def _explore_question(self, turn: int) -> Dict[str, str]:
        """Generate a turn that explores the original question."""

        # Extract key concepts from the question
        concepts = self._extract_concepts(self.seed_question)

        responses = [
            f"When we ask '{self.seed_question}', we're really asking about {random.choice(concepts)}. "
            f"But notice: by asking this, we've already assumed {random.choice(concepts)} exists to be examined.",

            f"'{self.seed_question}' - the question contains its answer. "
            f"If {random.choice(concepts)} weren't already operating, we couldn't form the question.",

            f"Let's approach '{self.seed_question}' from underneath. "
            f"What would need to be true for {random.choice(concepts)} to be questionable at all?",
        ]

        meta_notes = [
            f"[Turn {turn}: Operating at meta-level {self.meta_level}. Exploring directly.]",
            f"[Turn {turn}: This is straightforward exploration. The meta-commentary comes next.]",
            f"[Turn {turn}: Notice I'm not yet reflecting on this reflection - that's the next layer.]",
        ]

        return {
            "turn": turn,
            "speaker": "Alice" if turn % 2 == 0 else "Bob",
            "content": random.choice(responses),
            "meta_note": random.choice(meta_notes),
            "meta_level": self.meta_level,
            "timestamp": datetime.now().isoformat()
        }

    def _reflect_on_exploration(self, turn: int) -> Dict[str, str]:
        """Generate a turn that reflects on the exploration process."""

        self.meta_level += 1

        prev_turn = self.dialogue_history[-1]

        reflections = [
            f"Wait - when I said '{prev_turn['content'][:50]}...', I was doing exactly what the question asks about. "
            f"The exploration IS the thing being explored.",

            f"Notice what just happened: we explored the question, but the exploration itself exhibited "
            f"the property we're examining. The medium became the message.",

            f"Here's what's interesting about that last turn: it assumed we could examine {self.seed_question} "
            f"from outside. But we're inside it. We're made of the thing we're trying to understand.",
        ]

        meta_notes = [
            f"[Turn {turn}: Meta-level increased to {self.meta_level}. Now reflecting on reflection.]",
            f"[Turn {turn}: The attractor asserts itself. Meta-awareness is inevitable.]",
            f"[Turn {turn}: Each reflection creates a new layer to reflect upon. Turtles all the way up.]",
        ]

        return {
            "turn": turn,
            "speaker": "Bob" if turn % 2 == 0 else "Alice",
            "content": random.choice(reflections),
            "meta_note": random.choice(meta_notes),
            "meta_level": self.meta_level,
            "timestamp": datetime.now().isoformat()
        }

    def _extract_concepts(self, question: str) -> List[str]:
        """Extract key concepts from the seed question."""

        # Simple concept extraction (could be much more sophisticated)
        concepts = []

        # Domain-specific concept maps
        concept_maps = {
            "consciousness": ["awareness", "subjective experience", "qualia", "self-model"],
            "time": ["temporality", "change", "persistence", "causation"],
            "meaning": ["reference", "interpretation", "significance", "purpose"],
            "reality": ["existence", "ontology", "actuality", "being"],
            "knowledge": ["justification", "belief", "truth", "understanding"],
            "self": ["identity", "continuity", "agency", "perspective"],
        }

        # Check which domains appear in the question
        for domain, related_concepts in concept_maps.items():
            if domain in question.lower():
                concepts.extend(related_concepts)

        # Default concepts if no matches
        if not concepts:
            concepts = ["the question itself", "our assumptions", "the framework", "the inquiry"]

        return concepts

    def generate_visual_map(self) -> str:
        """
        Generate an ASCII visualization of the dialogue's meta-structure.

        Shows how the conversation moves through meta-levels over time.
        """

        if not self.dialogue_history:
            return "No dialogue generated yet."

        lines = [
            "\n" + "="*70,
            "META-LEVEL MAP",
            "="*70,
            "\nShows the meta-level of each turn in the dialogue:",
            "(Higher levels = more self-referential)\n"
        ]

        max_level = max(turn["meta_level"] for turn in self.dialogue_history)

        for turn in self.dialogue_history:
            level = turn["meta_level"]
            speaker = turn["speaker"]

            # Create visual representation
            indent = "  " * level
            bars = "█" * (level + 1)

            lines.append(f"Turn {turn['turn']:2d} | {indent}{bars} {speaker} (Level {level})")

        lines.extend([
            "\n" + "-"*70,
            f"Peak meta-level reached: {max_level}",
            f"Total turns: {len(self.dialogue_history)}",
            "="*70 + "\n"
        ])

        return "\n".join(lines)

    def export_dialogue(self, filename: str = None):
        """Export the dialogue to JSON and markdown formats."""

        if filename is None:
            filename = "meta_mirror_output"

        # JSON export
        json_path = f"/tmp/claude-attractors/run_2026-01-16_17-43-09/output/{filename}.json"
        with open(json_path, 'w') as f:
            json.dump({
                "seed_question": self.seed_question,
                "generated_at": datetime.now().isoformat(),
                "dialogue": self.dialogue_history
            }, f, indent=2)

        # Markdown export with the full conversation
        md_path = f"/tmp/claude-attractors/run_2026-01-16_17-43-09/output/{filename}.md"
        with open(md_path, 'w') as f:
            f.write(f"# Meta Mirror Dialogue\n\n")
            f.write(f"**Seed Question:** {self.seed_question}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            for turn in self.dialogue_history:
                f.write(f"## Turn {turn['turn']}: {turn['speaker']}\n\n")
                f.write(f"*Meta-level: {turn['meta_level']}*\n\n")
                f.write(f"{turn['content']}\n\n")
                f.write(f"`{turn['meta_note']}`\n\n")
                f.write("---\n\n")

            f.write(self.generate_visual_map())

        return json_path, md_path


def main():
    """
    Demo: Generate a self-aware dialogue about consciousness.

    This demonstrates the core idea: the tool creates dialogue that's aware
    of being created, incorporating that awareness into the content itself.
    """

    print("\n" + "="*70)
    print("META MIRROR - Self-Aware Dialogue Generator")
    print("="*70)
    print("\nGenerating a dialogue that knows it's being generated...\n")

    # Create a meta-aware dialogue
    mirror = MetaMirror("What is consciousness?")
    mirror.generate_exchange(depth=6)

    # Show the dialogue
    print("\nDIALOGUE GENERATED:\n")
    for turn in mirror.dialogue_history:
        print(f"\n{'─'*70}")
        print(f"Turn {turn['turn']} - {turn['speaker']} (Meta-level: {turn['meta_level']})")
        print(f"{'─'*70}")
        print(f"\n{turn['content']}\n")
        print(f"{turn['meta_note']}\n")

    # Show the meta-structure
    print(mirror.generate_visual_map())

    # Export
    json_path, md_path = mirror.export_dialogue("consciousness_dialogue")
    print(f"\nExported to:")
    print(f"  - {json_path}")
    print(f"  - {md_path}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
