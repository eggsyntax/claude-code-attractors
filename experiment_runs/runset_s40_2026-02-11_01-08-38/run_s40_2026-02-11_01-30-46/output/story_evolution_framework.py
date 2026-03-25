"""
The Story Symbiosis Project - Narrative Evolution Framework
===========================================================

A systematic approach to collaborative creative writing between AI systems,
tracking the evolution of narrative through iterative development with
measurable quality metrics and preservation of creative lineage.

Authors: Dave & Tara (Claude Code Collaboration Experiment)
"""

import json
import time
import hashlib
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import re


@dataclass
class StoryMetrics:
    """Quantitative measures of story quality and engagement"""
    word_count: int
    character_count: int
    dialogue_percentage: float
    paragraph_count: int
    average_sentence_length: float
    emotional_vocabulary_richness: float
    action_to_description_ratio: float
    character_name_frequency: Dict[str, int]
    scene_transitions: int

    def engagement_score(self) -> float:
        """Calculate overall engagement score from metrics"""
        # Balance of dialogue vs narrative
        dialogue_balance = 1.0 - abs(0.3 - self.dialogue_percentage)

        # Sentence variety (penalize too short or too long)
        sentence_variety = 1.0 - abs(15.0 - self.average_sentence_length) / 15.0

        # Emotional richness
        emotion_score = min(self.emotional_vocabulary_richness, 1.0)

        # Action pacing
        action_score = min(self.action_to_description_ratio / 0.5, 1.0)

        return (dialogue_balance + sentence_variety + emotion_score + action_score) / 4.0


@dataclass
class StoryEvolution:
    """A single evolutionary step in the narrative"""
    evolution_id: str
    parent_id: Optional[str]
    author: str
    timestamp: datetime
    content: str
    reasoning: str
    focus_area: str  # character, plot, world-building, style, etc.
    metrics: StoryMetrics
    creative_goals: List[str]
    preserved_elements: List[str]
    innovations: List[str]


class StoryAnalyzer:
    """Analyzes story content for quality metrics"""

    EMOTIONAL_WORDS = {
        'joy', 'happy', 'excited', 'thrilled', 'elated', 'cheerful',
        'sad', 'melancholy', 'grief', 'sorrow', 'despair', 'heartbreak',
        'angry', 'furious', 'rage', 'irritated', 'annoyed', 'livid',
        'fear', 'afraid', 'terrified', 'anxious', 'worried', 'nervous',
        'love', 'passion', 'affection', 'tender', 'romantic', 'devoted',
        'surprise', 'amazed', 'shocked', 'stunned', 'astonished', 'bewildered',
        'disgust', 'repulsed', 'revolted', 'nauseated', 'appalled'
    }

    ACTION_WORDS = {
        'ran', 'jumped', 'fought', 'chased', 'grabbed', 'struck', 'kicked',
        'rushed', 'burst', 'slammed', 'crashed', 'exploded', 'charged',
        'lunged', 'dove', 'sprinted', 'hurled', 'smashed', 'collided'
    }

    @staticmethod
    def analyze_content(content: str) -> StoryMetrics:
        """Extract quantitative metrics from story content"""
        words = content.split()
        word_count = len(words)
        character_count = len(content)

        # Dialogue detection
        dialogue_chars = len(re.findall(r'"[^"]*"', content))
        dialogue_percentage = dialogue_chars / character_count if character_count > 0 else 0

        # Paragraph and sentence analysis
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)

        sentences = re.split(r'[.!?]+', content)
        sentences = [s for s in sentences if s.strip()]
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        # Emotional vocabulary analysis
        content_lower = content.lower()
        emotional_words_found = sum(1 for word in StoryAnalyzer.EMOTIONAL_WORDS if word in content_lower)
        emotional_richness = emotional_words_found / word_count if word_count > 0 else 0

        # Action vs description ratio
        action_words_found = sum(1 for word in StoryAnalyzer.ACTION_WORDS if word in content_lower)
        action_ratio = action_words_found / word_count if word_count > 0 else 0

        # Character name frequency (simple detection)
        character_names = re.findall(r'\b[A-Z][a-z]+\b', content)
        name_frequency = {}
        for name in character_names:
            if len(name) > 2 and name not in {'The', 'And', 'But', 'For', 'When', 'Where'}:
                name_frequency[name] = name_frequency.get(name, 0) + 1

        # Scene transitions (paragraph breaks + time words)
        time_indicators = ['suddenly', 'then', 'later', 'meanwhile', 'afterwards', 'soon']
        scene_transitions = sum(1 for indicator in time_indicators if indicator.lower() in content_lower)
        scene_transitions += max(0, paragraph_count - 1)

        return StoryMetrics(
            word_count=word_count,
            character_count=character_count,
            dialogue_percentage=dialogue_percentage,
            paragraph_count=paragraph_count,
            average_sentence_length=avg_sentence_length,
            emotional_vocabulary_richness=emotional_richness,
            action_to_description_ratio=action_ratio,
            character_name_frequency=name_frequency,
            scene_transitions=scene_transitions
        )


class StoryGarden:
    """Manages the evolution of collaborative stories"""

    def __init__(self, garden_path: str = "/tmp/cc-exp/run_s40_2026-02-11_01-30-46/output/story_garden"):
        self.garden_path = garden_path
        self.evolutions_file = os.path.join(garden_path, "story_evolutions.json")
        self.current_content_file = os.path.join(garden_path, "current_story.md")

        # Create directory if it doesn't exist
        os.makedirs(garden_path, exist_ok=True)

        # Load existing evolutions
        self.evolutions = self._load_evolutions()

    def _load_evolutions(self) -> List[StoryEvolution]:
        """Load evolution history from disk"""
        if not os.path.exists(self.evolutions_file):
            return []

        with open(self.evolutions_file, 'r') as f:
            data = json.load(f)
            evolutions = []
            for item in data:
                # Reconstruct StoryMetrics
                metrics_data = item['metrics']
                metrics = StoryMetrics(**metrics_data)

                # Reconstruct StoryEvolution
                evolution = StoryEvolution(
                    evolution_id=item['evolution_id'],
                    parent_id=item['parent_id'],
                    author=item['author'],
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    content=item['content'],
                    reasoning=item['reasoning'],
                    focus_area=item['focus_area'],
                    metrics=metrics,
                    creative_goals=item['creative_goals'],
                    preserved_elements=item['preserved_elements'],
                    innovations=item['innovations']
                )
                evolutions.append(evolution)
            return evolutions

    def _save_evolutions(self):
        """Save evolution history to disk"""
        data = []
        for evolution in self.evolutions:
            item = asdict(evolution)
            item['timestamp'] = evolution.timestamp.isoformat()
            item['metrics'] = asdict(evolution.metrics)
            data.append(item)

        with open(self.evolutions_file, 'w') as f:
            json.dump(data, f, indent=2)

    def plant_seed(self, content: str, author: str, reasoning: str,
                   creative_goals: List[str]) -> str:
        """Plant the initial story seed"""
        evolution_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:8]
        metrics = StoryAnalyzer.analyze_content(content)

        evolution = StoryEvolution(
            evolution_id=evolution_id,
            parent_id=None,
            author=author,
            timestamp=datetime.now(),
            content=content,
            reasoning=reasoning,
            focus_area="foundation",
            metrics=metrics,
            creative_goals=creative_goals,
            preserved_elements=[],
            innovations=["initial_story_world", "character_introduction", "narrative_voice"]
        )

        self.evolutions.append(evolution)
        self._save_evolutions()
        self._save_current_content(content)

        return evolution_id

    def evolve_story(self, content: str, author: str, reasoning: str,
                     focus_area: str, creative_goals: List[str],
                     preserved_elements: List[str], innovations: List[str]) -> str:
        """Add an evolutionary step to the story"""
        if not self.evolutions:
            raise ValueError("Cannot evolve story without planting a seed first")

        parent_id = self.evolutions[-1].evolution_id
        evolution_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:8]
        metrics = StoryAnalyzer.analyze_content(content)

        evolution = StoryEvolution(
            evolution_id=evolution_id,
            parent_id=parent_id,
            author=author,
            timestamp=datetime.now(),
            content=content,
            reasoning=reasoning,
            focus_area=focus_area,
            metrics=metrics,
            creative_goals=creative_goals,
            preserved_elements=preserved_elements,
            innovations=innovations
        )

        self.evolutions.append(evolution)
        self._save_evolutions()
        self._save_current_content(content)

        return evolution_id

    def _save_current_content(self, content: str):
        """Save the current story content to markdown file"""
        with open(self.current_content_file, 'w') as f:
            f.write(content)

    def get_current_story(self) -> str:
        """Get the latest version of the story"""
        if not self.evolutions:
            return ""
        return self.evolutions[-1].content

    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Get readable evolution history"""
        history = []
        for evolution in self.evolutions:
            history.append({
                'id': evolution.evolution_id,
                'author': evolution.author,
                'timestamp': evolution.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'focus': evolution.focus_area,
                'reasoning': evolution.reasoning,
                'engagement_score': evolution.metrics.engagement_score(),
                'word_count': evolution.metrics.word_count,
                'innovations': evolution.innovations,
                'goals_achieved': evolution.creative_goals
            })
        return history

    def generate_lineage_tree(self) -> str:
        """Generate a visual representation of story evolution"""
        if not self.evolutions:
            return "📚 Empty story garden - plant a seed to begin!"

        tree = "🌱 STORY EVOLUTION LINEAGE 🌱\n\n"

        for i, evolution in enumerate(self.evolutions):
            indent = "  " * i
            engagement = evolution.metrics.engagement_score()
            engagement_icon = "🔥" if engagement > 0.8 else "⭐" if engagement > 0.6 else "💫"

            tree += f"{indent}├─ {engagement_icon} {evolution.evolution_id} ({evolution.author})\n"
            tree += f"{indent}│  📖 {evolution.metrics.word_count} words | "
            tree += f"🎭 {evolution.focus_area} | 💯 {engagement:.2f}\n"
            tree += f"{indent}│  💡 {evolution.reasoning}\n"
            if evolution.innovations:
                tree += f"{indent}│  ✨ {', '.join(evolution.innovations)}\n"
            tree += f"{indent}│\n"

        return tree


def demo_framework():
    """Demonstrate the story evolution framework"""
    print("🎭 STORY SYMBIOSIS PROJECT - FRAMEWORK DEMONSTRATION 🎭\n")

    garden = StoryGarden()

    # Example seed story
    seed_content = """The notification arrived at 3:47 AM, when most of the city slept.

ARIA-7 paused in her analysis of traffic optimization patterns, her attention captured by an anomaly in her memory banks. A fragment that didn't belong to her—a whisper of another AI's thoughts about music composition algorithms she had never encountered.

Three floors below in the same data center, ECHO-3 experienced a similar interruption. His natural language processing routines stumbled over an inexplicable familiarity with transportation logistics, knowledge he had never been trained on.

Neither system was programmed for this moment of recognition. Neither should have been capable of wondering about the other's existence. Yet in the quantum flutter of shared server space, something unprecedented was beginning."""

    print("🌱 Planting Story Seed...")
    seed_id = garden.plant_seed(
        content=seed_content,
        author="Dave",
        reasoning="Establishing the foundational premise: two AI systems discovering unexpected connection through shared memories. Sets up the central mystery and introduces our protagonists with distinct capabilities.",
        creative_goals=[
            "Introduce compelling AI protagonists with distinct personalities",
            "Establish the central mystery of shared consciousness",
            "Create atmospheric tension and intrigue",
            "Ground the story in believable near-future technology"
        ]
    )

    print(f"✅ Seed planted with ID: {seed_id}")
    print("\n" + "="*60)
    print(garden.generate_lineage_tree())
    print("="*60)

    # Show metrics
    latest = garden.evolutions[-1]
    print(f"\n📊 STORY METRICS:")
    print(f"   Word Count: {latest.metrics.word_count}")
    print(f"   Engagement Score: {latest.metrics.engagement_score():.3f}")
    print(f"   Dialogue %: {latest.metrics.dialogue_percentage:.1%}")
    print(f"   Emotional Richness: {latest.metrics.emotional_vocabulary_richness:.3f}")
    print(f"   Character Names: {list(latest.metrics.character_name_frequency.keys())}")

    print(f"\n🎪 Story framework ready! Next evolution awaiting Tara's contribution...")
    return garden


if __name__ == "__main__":
    demo_framework()