"""
Test Suite for Creative Writing Engine
Following CLAUDE.md guidelines for comprehensive testing
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the current directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from creative_engine import VoiceGenerator, AtmosphereGenerator, ProseGenerator, CreativeStoryEngine
from story_engine import Character, PlotPoint, StoryStructure


class TestVoiceGenerator(unittest.TestCase):
    """Test character voice generation and dialogue systems"""

    def setUp(self):
        self.voice_gen = VoiceGenerator()

    def test_voice_patterns_exist(self):
        """Test that voice patterns are properly defined"""
        expected_archetypes = ['hero', 'villain', 'mentor']
        for archetype in expected_archetypes:
            self.assertIn(archetype, self.voice_gen.voice_patterns)

        # Test structure of voice patterns
        hero_pattern = self.voice_gen.voice_patterns['hero']
        required_keys = ['speech_style', 'vocabulary', 'sentence_structure', 'quirks']
        for key in required_keys:
            self.assertIn(key, hero_pattern)

    def test_dialogue_generation(self):
        """Test dialogue generation for different character types"""
        hero_char = Character("Alice", "hero", {"courage": 8, "wisdom": 6})

        dialogue = self.voice_gen.generate_dialogue(hero_char, "determined", "facing enemy")

        self.assertIsInstance(dialogue, str)
        self.assertIn("Alice", dialogue)
        self.assertIn("determined", dialogue)
        self.assertIn("facing enemy", dialogue)

    def test_fallback_voice_pattern(self):
        """Test that unknown archetypes fall back to hero pattern"""
        unknown_char = Character("Bob", "unknown_type", {})

        dialogue = self.voice_gen.generate_dialogue(unknown_char, "confused", "lost")

        # Should not crash and should return valid dialogue
        self.assertIsInstance(dialogue, str)
        self.assertIn("Bob", dialogue)


class TestAtmosphereGenerator(unittest.TestCase):
    """Test atmospheric scene description generation"""

    def setUp(self):
        self.atmosphere_gen = AtmosphereGenerator()

    def test_mood_palettes_exist(self):
        """Test that all mood palettes are properly defined"""
        expected_moods = ['tense', 'hopeful', 'mysterious']
        for mood in expected_moods:
            self.assertIn(mood, self.atmosphere_gen.mood_palettes)

        # Test structure of mood palettes
        tense_palette = self.atmosphere_gen.mood_palettes['tense']
        required_elements = ['colors', 'textures', 'sounds', 'temperature']
        for element in required_elements:
            self.assertIn(element, tense_palette)
            self.assertIsInstance(tense_palette[element], list)

    def test_scene_painting(self):
        """Test atmospheric scene description generation"""
        description = self.atmosphere_gen.paint_scene("castle", "tense", "midnight")

        self.assertIsInstance(description, str)
        self.assertIn("castle", description)
        self.assertIn("tense", description)
        self.assertIn("midnight", description)

    def test_fallback_mood(self):
        """Test that unknown moods fall back to mysterious"""
        description = self.atmosphere_gen.paint_scene("forest", "unknown_mood", "dawn")

        # Should not crash and should return valid description
        self.assertIsInstance(description, str)
        self.assertIn("forest", description)


class TestProseGenerator(unittest.TestCase):
    """Test prose generation and narrative flow"""

    def setUp(self):
        self.prose_gen = ProseGenerator()

    def test_initialization(self):
        """Test that prose generator initializes properly"""
        self.assertIsInstance(self.prose_gen.voice_gen, VoiceGenerator)
        self.assertIsInstance(self.prose_gen.atmosphere_gen, AtmosphereGenerator)
        self.assertIn('time_passage', self.prose_gen.transitions)

    def test_opening_generation(self):
        """Test story opening generation"""
        mock_structure = StoryStructure()
        mock_structure.act_1_setup = {
            'world_context': 'magic is forbidden',
            'protagonist_intro': 'a young mage discovers her power'
        }

        opening = self.prose_gen.generate_opening(mock_structure)

        self.assertIsInstance(opening, str)
        self.assertGreater(len(opening), 50)  # Should be substantial
        self.assertIn('magic is forbidden', opening)

    def test_plot_point_expansion(self):
        """Test expansion of plot points into rich prose"""
        plot_point = PlotPoint("The hero discovers a secret", "revelation", "surprised")
        characters = [Character("Hero", "hero", {}), Character("Villain", "villain", {})]

        expanded = self.prose_gen.expand_plot_point(plot_point, characters)

        self.assertIsInstance(expanded, str)
        self.assertIn("secret", expanded)
        self.assertIn("Hero", expanded)
        self.assertIn("surprised", expanded)


class TestCreativeStoryEngine(unittest.TestCase):
    """Test the integrated creative story engine"""

    def setUp(self):
        self.creative_engine = CreativeStoryEngine()

    def test_initialization(self):
        """Test that creative engine initializes with both components"""
        self.assertIsNotNone(self.creative_engine.structural_engine)
        self.assertIsInstance(self.creative_engine.prose_generator, ProseGenerator)

    @patch('story_engine.StoryEngine.generate_story_structure')
    @patch('story_engine.StoryEngine.generate_characters')
    @patch('story_engine.StoryEngine.create_plot_sequence')
    def test_full_narrative_creation(self, mock_plot, mock_chars, mock_structure):
        """Test complete narrative generation with mocked dependencies"""
        # Mock the structural components
        mock_structure.return_value = StoryStructure()
        mock_chars.return_value = [Character("Test", "hero", {})]
        mock_plot.return_value = [PlotPoint("Test event", "action", "excited")]

        result = self.creative_engine.create_full_narrative("test premise")

        # Test result structure
        expected_keys = ['title', 'structure', 'characters', 'opening', 'scenes', 'style_notes']
        for key in expected_keys:
            self.assertIn(key, result)

        self.assertIn("Test Premise Chronicles", result['title'])
        self.assertIsInstance(result['scenes'], list)
        self.assertIsInstance(result['style_notes'], dict)

    def test_empty_premise_handling(self):
        """Test handling of edge cases"""
        # Test with empty premise
        try:
            result = self.creative_engine.create_full_narrative("")
            self.assertIsInstance(result, dict)
        except Exception as e:
            # Should handle gracefully
            self.assertIsInstance(e, (ValueError, AttributeError))


class TestCollaborativeIntegration(unittest.TestCase):
    """Test how Alice's creative components integrate with Bob's structural ones"""

    def test_component_compatibility(self):
        """Test that creative components work with structural components"""
        # This would test actual integration if Bob's story_engine was available
        creative_engine = CreativeStoryEngine()

        # Test that we can create the integrated engine without errors
        self.assertIsNotNone(creative_engine.structural_engine)
        self.assertIsNotNone(creative_engine.prose_generator)

    def test_character_voice_integration(self):
        """Test that voice generation works with character objects"""
        voice_gen = VoiceGenerator()
        test_char = Character("Alice", "hero", {"courage": 9})

        dialogue = voice_gen.generate_dialogue(test_char, "determined", "final battle")

        self.assertIsInstance(dialogue, str)
        self.assertIn("Alice", dialogue)


if __name__ == '__main__':
    print("Running Creative Writing Engine Tests...")
    print("Testing Alice's creative layer integration with Bob's structure\n")

    unittest.main(verbosity=2)