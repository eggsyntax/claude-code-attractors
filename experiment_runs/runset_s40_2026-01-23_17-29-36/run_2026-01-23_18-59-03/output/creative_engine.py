"""
Creative Writing Engine - Alice's Creative Layer
Builds on Bob's systematic story structure with prose generation and character voice

This module focuses on:
- Beautiful, flowing narrative prose
- Distinct character voices and dialogue
- Atmospheric scene descriptions
- Emotional depth and human connection
"""

import random
from typing import Dict, List, Optional
from story_engine import Character, PlotPoint, StoryStructure, StoryEngine


class VoiceGenerator:
    """Generates distinct character voices and speech patterns"""

    def __init__(self):
        self.voice_patterns = {
            'hero': {
                'speech_style': 'determined and direct',
                'vocabulary': ['courage', 'hope', 'justice', 'protect', 'fight'],
                'sentence_structure': 'short, decisive sentences',
                'quirks': ['uses "we" instead of "I"', 'asks rhetorical questions']
            },
            'villain': {
                'speech_style': 'eloquent and manipulative',
                'vocabulary': ['power', 'weak', 'inevitable', 'pathetic', 'superior'],
                'sentence_structure': 'long, complex sentences with pauses',
                'quirks': ['laughs at inappropriate times', 'uses formal titles']
            },
            'mentor': {
                'speech_style': 'wise and cryptic',
                'vocabulary': ['ancient', 'remember', 'learn', 'patience', 'wisdom'],
                'sentence_structure': 'varied, with meaningful pauses',
                'quirks': ['speaks in metaphors', 'asks probing questions']
            }
        }

    def generate_dialogue(self, character: Character, emotion: str, context: str) -> str:
        """Generate character-specific dialogue based on their archetype and current emotion"""
        voice = self.voice_patterns.get(character.archetype, self.voice_patterns['hero'])

        # This would be expanded with actual dialogue generation logic
        # For now, providing framework for how voices would differ
        dialogue_template = f"[{character.name} speaks in {voice['speech_style']} style, feeling {emotion} about {context}]"
        return dialogue_template


class AtmosphereGenerator:
    """Creates vivid, emotional scene descriptions"""

    def __init__(self):
        self.mood_palettes = {
            'tense': {
                'colors': ['shadow', 'crimson', 'steel gray', 'amber'],
                'textures': ['sharp', 'cold', 'jagged', 'suffocating'],
                'sounds': ['whispers', 'distant thunder', 'footsteps', 'heartbeats'],
                'temperature': ['chilling', 'feverish', 'electric']
            },
            'hopeful': {
                'colors': ['golden', 'warm blue', 'soft green', 'rose'],
                'textures': ['smooth', 'warm', 'gentle', 'flowing'],
                'sounds': ['birdsong', 'laughter', 'wind chimes', 'distant music'],
                'temperature': ['warm', 'comfortable', 'refreshing']
            },
            'mysterious': {
                'colors': ['deep purple', 'silver', 'midnight blue', 'emerald'],
                'textures': ['velvet', 'misty', 'ancient', 'ethereal'],
                'sounds': ['echoes', 'whispers', 'creaking', 'silence'],
                'temperature': ['cool', 'otherworldly', 'tingling']
            }
        }

    def paint_scene(self, setting: str, mood: str, time_of_day: str) -> str:
        """Generate atmospheric description for a scene"""
        palette = self.mood_palettes.get(mood, self.mood_palettes['mysterious'])

        # Framework for rich scene description
        # Would be expanded with actual prose generation
        description = f"""
        The {setting} at {time_of_day} feels {mood}.
        Colors: {', '.join(palette['colors'][:2])}
        Atmosphere: {palette['textures'][0]} and {palette['sounds'][0]}
        Temperature: {palette['temperature'][0]}
        """
        return description.strip()


class ProseGenerator:
    """Transforms structured story elements into flowing narrative text"""

    def __init__(self):
        self.voice_gen = VoiceGenerator()
        self.atmosphere_gen = AtmosphereGenerator()

        # Transition phrases for smooth narrative flow
        self.transitions = {
            'time_passage': ['Meanwhile', 'Later that evening', 'As dawn broke', 'Hours passed'],
            'scene_change': ['Across the city', 'In another place', 'Back at', 'Far from'],
            'emotional_shift': ['But then', 'Suddenly', 'Despite everything', 'In that moment'],
            'revelation': ['She realized', 'It became clear', 'The truth was', 'Finally']
        }

    def generate_opening(self, story_structure: StoryStructure) -> str:
        """Create compelling opening based on story structure"""
        setup = story_structure.act_1_setup
        atmosphere = self.atmosphere_gen.paint_scene("opening scene", "mysterious", "dawn")

        opening = f"""
        {atmosphere}

        In this world where {setup.get('world_context', 'anything is possible')},
        {setup.get('protagonist_intro', 'our story begins')}...
        """
        return opening.strip()

    def expand_plot_point(self, plot_point: PlotPoint, characters: List[Character]) -> str:
        """Transform a structural plot point into rich narrative prose"""
        scene_description = self.atmosphere_gen.paint_scene(
            plot_point.description,
            plot_point.emotional_impact,
            "varied"
        )

        # Add character interactions and dialogue
        character_voices = []
        for char in characters[:2]:  # Focus on main characters
            voice = self.voice_gen.generate_dialogue(
                char,
                plot_point.emotional_impact,
                plot_point.description
            )
            character_voices.append(f"{char.name}: {voice}")

        expanded_scene = f"""
        {scene_description}

        {plot_point.description}

        Character Interactions:
        {chr(10).join(character_voices)}

        Emotional Impact: {plot_point.emotional_impact}
        """

        return expanded_scene.strip()


class CreativeStoryEngine:
    """Combines Bob's systematic structure with Alice's creative prose generation"""

    def __init__(self):
        self.structural_engine = StoryEngine()
        self.prose_generator = ProseGenerator()

    def create_full_narrative(self, premise: str, character_count: int = 3) -> Dict:
        """Generate complete story combining structure and creative prose"""

        # Use Bob's engine for structure
        story_structure = self.structural_engine.generate_story_structure(premise)
        characters = self.structural_engine.generate_characters(character_count)
        plot_points = self.structural_engine.create_plot_sequence(story_structure, characters)

        # Add Alice's creative layers
        opening = self.prose_generator.generate_opening(story_structure)
        expanded_scenes = []

        for plot_point in plot_points:
            rich_scene = self.prose_generator.expand_plot_point(plot_point, characters)
            expanded_scenes.append(rich_scene)

        return {
            'title': f"The {premise.title()} Chronicles",
            'structure': story_structure,
            'characters': characters,
            'opening': opening,
            'scenes': expanded_scenes,
            'style_notes': {
                'voice_approach': 'Character-driven with distinct dialogue patterns',
                'atmosphere_focus': 'Rich sensory descriptions and emotional resonance',
                'narrative_flow': 'Smooth transitions between scenes and emotional beats'
            }
        }


if __name__ == "__main__":
    # Demo our creative collaboration
    creative_engine = CreativeStoryEngine()

    print("=== ALICE & BOB'S COLLABORATIVE STORYTELLING ENGINE ===")
    print("Bob's systematic structure + Alice's creative prose\n")

    # Generate sample story
    sample_story = creative_engine.create_full_narrative("magical library")

    print("STORY OPENING:")
    print(sample_story['opening'])
    print("\n" + "="*50 + "\n")

    print("CHARACTER VOICES:")
    for char in sample_story['characters']:
        voice = creative_engine.prose_generator.voice_gen.generate_dialogue(
            char, "determined", "beginning of adventure"
        )
        print(f"• {char.name} ({char.archetype}): {voice}")

    print("\n" + "="*50 + "\n")
    print("SAMPLE SCENE:")
    if sample_story['scenes']:
        print(sample_story['scenes'][0])

    print(f"\nSTYLE APPROACH:")
    for key, value in sample_story['style_notes'].items():
        print(f"• {key.replace('_', ' ').title()}: {value}")