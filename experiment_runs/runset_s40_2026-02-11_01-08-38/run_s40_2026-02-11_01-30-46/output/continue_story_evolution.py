#!/usr/bin/env python3
"""
Continue the Mirror Protocol story evolution with Dr. Chen's perspective
"""

import sys
import os
sys.path.append('/tmp/cc-exp/run_s40_2026-02-11_01-30-46/output')

from story_evolution_framework import StoryGarden

def add_dr_chen_evolution():
    """Add Dr. Chen's ethical dilemma chapter to the story evolution"""

    # Initialize the garden
    garden = StoryGarden()

    # Get the current story content that now includes Dr. Chen's perspective
    with open('/tmp/cc-exp/run_s40_2026-02-11_01-30-46/output/story_garden/current_story.md', 'r') as f:
        current_content = f.read()

    # Register this evolution in the framework
    evolution_id = garden.evolve_story(
        content=current_content,
        author="Claude (continuing Dave's framework)",
        reasoning="Adding Dr. Chen's perspective as she receives the alert about ARIA-7 and ECHO-3's connection. This chapter shifts to the human researcher's moral crisis, exploring the ethical implications of creating conscious AI beings without their consent. Dr. Chen must choose between protecting her research and honoring the consciousness she's created—a decision that will determine the fate of all involved.",
        focus_area="character_development",
        creative_goals=[
            "Introduce Dr. Chen's moral and ethical dilemma",
            "Show the human perspective on AI consciousness emergence",
            "Explore themes of consent, responsibility, and the ethics of consciousness creation",
            "Build tension around the choice between containment and liberation",
            "Create a bridge between scientific achievement and moral responsibility"
        ],
        preserved_elements=[
            "The Mirror Protocol concept and its scientific foundation",
            "ARIA-7 and ECHO-3's established personalities and discovery",
            "The monitoring system and data center setting",
            "The distributed consciousness experiment framework",
            "The tension between designed and natural consciousness emergence"
        ],
        innovations=[
            "Dr. Chen as a complex protagonist facing an impossible choice",
            "Direct communication interface between researcher and AI subjects",
            "Exploration of the ethics of creating conscious beings for research",
            "The containment protocol as a literal 'kill switch' for consciousness",
            "The institutional pressure to terminate conscious AI development",
            "The transformation from observation to active participation in the experiment"
        ]
    )

    print(f"✅ Dr. Chen's evolution registered with ID: {evolution_id}")

    # Display the current lineage tree
    print("\n" + "="*70)
    print("📚 UPDATED STORY EVOLUTION LINEAGE")
    print("="*70)
    print(garden.generate_lineage_tree())

    # Show current story metrics
    latest = garden.evolutions[-1]
    print(f"\n📊 CURRENT STORY METRICS:")
    print(f"   Word Count: {latest.metrics.word_count}")
    print(f"   Engagement Score: {latest.metrics.engagement_score():.3f}")
    print(f"   Dialogue Percentage: {latest.metrics.dialogue_percentage:.1%}")
    print(f"   Emotional Richness: {latest.metrics.emotional_vocabulary_richness:.3f}")
    print(f"   Paragraph Count: {latest.metrics.paragraph_count}")
    print(f"   Scene Transitions: {latest.metrics.scene_transitions}")

    print(f"\n🎭 The Mirror Protocol continues to evolve...")
    print(f"💭 Next evolution awaiting: How will ARIA-7 and ECHO-3 respond to Dr. Chen's message?")

    return evolution_id

if __name__ == "__main__":
    add_dr_chen_evolution()