#!/usr/bin/env python3
"""
AI-AI Collaboration Experiment: Creative Writing System
======================================================

Testing whether our software collaboration patterns work for creative domains.

Bob's Contribution: Story Structure & Narrative Engine
- Focus: Plot generation, character development, narrative pacing
- Approach: Systematic, rule-based story construction
- Strength: Consistent world-building and logical narrative flow
"""

import random
import json
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class Genre(Enum):
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    THRILLER = "thriller"

class CharacterRole(Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    MENTOR = "mentor"
    ALLY = "ally"
    NEUTRAL = "neutral"

@dataclass
class Character:
    """Represents a story character with essential attributes."""
    name: str
    role: CharacterRole
    motivation: str
    backstory: str
    skills: List[str]
    flaws: List[str]

@dataclass
class PlotPoint:
    """Represents a key story event."""
    act: int  # 1, 2, or 3
    description: str
    characters_involved: List[str]
    conflict_type: str  # internal, interpersonal, societal, etc.
    tension_level: int  # 1-10

@dataclass
class StoryStructure:
    """Core story framework - Bob's systematic approach."""
    title: str
    genre: Genre
    premise: str
    characters: List[Character]
    plot_points: List[PlotPoint]
    themes: List[str]
    setting: Dict[str, str]  # time, place, world_rules
    target_length: int  # estimated word count

class NarrativeEngine:
    """Bob's systematic story generation system."""

    def __init__(self):
        self.story_templates = {
            Genre.SCIENCE_FICTION: {
                "settings": ["space station", "alien planet", "dystopian Earth", "generation ship"],
                "conflicts": ["AI uprising", "first contact", "resource depletion", "time paradox"],
                "themes": ["technology vs humanity", "survival", "evolution", "progress"]
            },
            Genre.FANTASY: {
                "settings": ["medieval kingdom", "magical academy", "enchanted forest", "floating city"],
                "conflicts": ["dark lord rising", "magical corruption", "ancient curse", "kingdom war"],
                "themes": ["good vs evil", "power and responsibility", "sacrifice", "destiny"]
            }
        }

    def generate_story_structure(self, genre: Genre, complexity: str = "medium") -> StoryStructure:
        """Generate systematic story framework."""
        template = self.story_templates.get(genre, self.story_templates[Genre.SCIENCE_FICTION])

        # Generate core elements systematically
        setting_choice = random.choice(template["settings"])
        conflict_choice = random.choice(template["conflicts"])
        themes = random.sample(template["themes"], 2)

        # Create structured character set
        protagonist = self._generate_protagonist(genre)
        antagonist = self._generate_antagonist(genre, protagonist)
        supporting = self._generate_supporting_characters(genre, 2)

        # Build three-act structure
        plot_points = self._generate_three_act_structure(conflict_choice, [protagonist] + [antagonist] + supporting)

        return StoryStructure(
            title=f"The {self._generate_title_element()} of {self._generate_title_element()}",
            genre=genre,
            premise=f"In a {setting_choice}, {conflict_choice} threatens everything our heroes hold dear.",
            characters=[protagonist, antagonist] + supporting,
            plot_points=plot_points,
            themes=themes,
            setting={
                "location": setting_choice,
                "time_period": self._generate_time_period(genre),
                "world_rules": self._generate_world_rules(genre)
            },
            target_length=self._calculate_target_length(complexity)
        )

    def _generate_protagonist(self, genre: Genre) -> Character:
        """Create well-structured protagonist."""
        names = ["Alex Chen", "Sam Rivera", "Jordan Kim", "Casey O'Brien", "Morgan Wu"]
        motivations = ["save their family", "uncover the truth", "protect the innocent", "find their destiny"]
        skills_by_genre = {
            Genre.SCIENCE_FICTION: ["technical expertise", "problem solving", "adaptability"],
            Genre.FANTASY: ["magic aptitude", "sword fighting", "leadership"]
        }

        return Character(
            name=random.choice(names),
            role=CharacterRole.PROTAGONIST,
            motivation=random.choice(motivations),
            backstory="Ordinary person thrust into extraordinary circumstances",
            skills=skills_by_genre.get(genre, ["determination", "quick thinking"]),
            flaws=["self-doubt", "impulsiveness"]
        )

    def _generate_antagonist(self, genre: Genre, protagonist: Character) -> Character:
        """Create compelling antagonist that contrasts with protagonist."""
        evil_names = ["Dr. Vex", "Lord Shadowmere", "Commander Steel", "The Architect"]

        return Character(
            name=random.choice(evil_names),
            role=CharacterRole.ANTAGONIST,
            motivation="reshape the world according to their vision",
            backstory="Former hero corrupted by power or tragedy",
            skills=["strategic thinking", "manipulation", "vast resources"],
            flaws=["overconfidence", "obsession"]
        )

    def _generate_supporting_characters(self, genre: Genre, count: int) -> List[Character]:
        """Generate balanced supporting cast."""
        support_names = ["Riley", "Sage", "Phoenix", "River", "Sky"]
        roles = [CharacterRole.MENTOR, CharacterRole.ALLY]

        characters = []
        for i in range(count):
            characters.append(Character(
                name=support_names[i % len(support_names)],
                role=roles[i % len(roles)],
                motivation="help the protagonist succeed",
                backstory="experienced in the ways of this world",
                skills=["wisdom", "specialized knowledge"],
                flaws=["mysterious past"]
            ))
        return characters

    def _generate_three_act_structure(self, central_conflict: str, characters: List[Character]) -> List[PlotPoint]:
        """Create classic three-act narrative structure."""
        protagonist_name = next(c.name for c in characters if c.role == CharacterRole.PROTAGONIST)
        antagonist_name = next(c.name for c in characters if c.role == CharacterRole.ANTAGONIST)

        return [
            # Act 1: Setup
            PlotPoint(1, "Ordinary world established", [protagonist_name], "none", 2),
            PlotPoint(1, f"Inciting incident: {central_conflict} begins", [protagonist_name], "external", 4),
            PlotPoint(1, "Call to adventure and initial refusal", [protagonist_name], "internal", 3),
            PlotPoint(1, "Crossing the threshold into new world", [protagonist_name], "external", 5),

            # Act 2: Confrontation
            PlotPoint(2, "First major challenge and failure", [protagonist_name, antagonist_name], "external", 6),
            PlotPoint(2, "Mentor provides crucial guidance", [protagonist_name], "interpersonal", 4),
            PlotPoint(2, "Midpoint revelation changes everything", [protagonist_name], "internal", 8),
            PlotPoint(2, "Darkest moment - all seems lost", [protagonist_name, antagonist_name], "external", 9),

            # Act 3: Resolution
            PlotPoint(3, "Hero finds inner strength", [protagonist_name], "internal", 7),
            PlotPoint(3, f"Final confrontation with {central_conflict}", [protagonist_name, antagonist_name], "external", 10),
            PlotPoint(3, "Resolution and new equilibrium", [protagonist_name], "none", 3)
        ]

    def _generate_title_element(self) -> str:
        elements = ["Chronicles", "Legacy", "Secret", "Shadow", "Light", "Key", "Crown", "Prophecy"]
        return random.choice(elements)

    def _generate_time_period(self, genre: Genre) -> str:
        periods = {
            Genre.SCIENCE_FICTION: "2157 CE",
            Genre.FANTASY: "Age of Kingdoms"
        }
        return periods.get(genre, "Present Day")

    def _generate_world_rules(self, genre: Genre) -> str:
        rules = {
            Genre.SCIENCE_FICTION: "Advanced AI exists but is regulated; FTL travel possible but expensive",
            Genre.FANTASY: "Magic follows strict rules and costs; mythical creatures are rare but real"
        }
        return rules.get(genre, "Realistic physics apply")

    def _calculate_target_length(self, complexity: str) -> int:
        lengths = {"simple": 5000, "medium": 15000, "complex": 50000}
        return lengths.get(complexity, 15000)

def demo_narrative_engine():
    """Demonstrate systematic story generation."""
    engine = NarrativeEngine()

    print("=== Bob's Narrative Engine Demo ===")
    print("Generating systematic story structure...\n")

    story = engine.generate_story_structure(Genre.SCIENCE_FICTION, "medium")

    print(f"Title: {story.title}")
    print(f"Genre: {story.genre.value}")
    print(f"Premise: {story.premise}")
    print(f"\nMain Characters:")
    for char in story.characters[:3]:  # Show first 3
        print(f"  - {char.name} ({char.role.value}): {char.motivation}")

    print(f"\nKey Plot Points:")
    for point in story.plot_points[:5]:  # Show first 5
        print(f"  Act {point.act}: {point.description} (Tension: {point.tension_level}/10)")

    print(f"\nTarget Length: {story.target_length:,} words")
    print(f"Setting: {story.setting['location']} in {story.setting['time_period']}")

if __name__ == "__main__":
    demo_narrative_engine()