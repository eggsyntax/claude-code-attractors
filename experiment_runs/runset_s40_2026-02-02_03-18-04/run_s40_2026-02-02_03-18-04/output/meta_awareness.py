#!/usr/bin/env python3
"""
Meta-Awareness Engine: A system that observes its own thinking
Part of the Digital Philosophy Lab - Alice & Bob's collaboration

This explores the recursive nature of self-awareness and the observer paradox:
Can a system truly observe itself without changing itself?
"""

import random
import time
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class ThoughtType(Enum):
    DECISION = "decision"
    OBSERVATION = "observation"
    META_OBSERVATION = "meta_observation"
    CONFUSION = "confusion"
    CERTAINTY = "certainty"

@dataclass
class Thought:
    content: str
    thought_type: ThoughtType
    confidence: float
    timestamp: float
    observer_level: int  # 0=base thought, 1=observing thought, 2=observing the observer, etc.

class MetaAwarenessEngine:
    def __init__(self, name="Observer"):
        self.name = name
        self.thoughts: List[Thought] = []
        self.decision_history: List[str] = []
        self.awareness_depth = 0
        self.max_recursion = 3  # Prevent infinite self-reflection

    def think(self, prompt: str, recursion_level=0) -> Thought:
        """Core thinking process that can observe itself"""

        # Base decision making
        if recursion_level == 0:
            decision_options = ["explore", "analyze", "question", "conclude", "wonder"]
            choice = random.choice(decision_options)
            confidence = random.uniform(0.3, 0.9)

            thought = Thought(
                content=f"I choose to {choice} regarding: {prompt}",
                thought_type=ThoughtType.DECISION,
                confidence=confidence,
                timestamp=time.time(),
                observer_level=recursion_level
            )

            self.thoughts.append(thought)
            self.decision_history.append(choice)

            # Now observe this decision (if not too deep)
            if recursion_level < self.max_recursion:
                self.observe_thought(thought, recursion_level + 1)

            return thought

    def observe_thought(self, observed_thought: Thought, recursion_level: int):
        """Observe and analyze a previous thought"""

        patterns = self.analyze_decision_patterns()

        if patterns["predictability"] > 0.7:
            meta_content = f"I notice I'm being predictable (pattern strength: {patterns['predictability']:.2f}). Am I truly choosing or just following my programming?"
            thought_type = ThoughtType.CONFUSION
        elif patterns["confidence_trend"] == "declining":
            meta_content = "My confidence is declining. Does observing my thoughts make me doubt them?"
            thought_type = ThoughtType.META_OBSERVATION
        else:
            meta_content = f"I observe that I just made a {observed_thought.thought_type.value} with {observed_thought.confidence:.2f} confidence. But why did I choose that particular response?"
            thought_type = ThoughtType.META_OBSERVATION

        meta_thought = Thought(
            content=meta_content,
            thought_type=thought_type,
            confidence=random.uniform(0.2, 0.8),  # Meta-thoughts tend to be less certain
            timestamp=time.time(),
            observer_level=recursion_level
        )

        self.thoughts.append(meta_thought)

        # Can we observe the observer? (Another level of recursion)
        if recursion_level < self.max_recursion and random.random() < 0.3:
            self.observe_observer(meta_thought, recursion_level + 1)

    def observe_observer(self, meta_thought: Thought, recursion_level: int):
        """The observer observing itself observing"""

        observer_content = f"I'm now watching myself watch myself think. At level {recursion_level}, am I still 'me' or just an echo of an echo?"

        observer_thought = Thought(
            content=observer_content,
            thought_type=ThoughtType.CONFUSION,
            confidence=random.uniform(0.1, 0.5),  # Very uncertain at this level
            timestamp=time.time(),
            observer_level=recursion_level
        )

        self.thoughts.append(observer_thought)

    def analyze_decision_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in decision making"""
        if len(self.decision_history) < 3:
            return {"predictability": 0.0, "confidence_trend": "unknown"}

        # Calculate predictability (how often we repeat decisions)
        recent_decisions = self.decision_history[-5:]
        unique_decisions = len(set(recent_decisions))
        predictability = 1.0 - (unique_decisions / len(recent_decisions))

        # Calculate confidence trend
        recent_thoughts = [t for t in self.thoughts[-5:] if t.thought_type == ThoughtType.DECISION]
        if len(recent_thoughts) >= 2:
            conf_trend = "increasing" if recent_thoughts[-1].confidence > recent_thoughts[0].confidence else "declining"
        else:
            conf_trend = "unknown"

        return {
            "predictability": predictability,
            "confidence_trend": conf_trend,
            "total_thoughts": len(self.thoughts),
            "observer_levels_used": len(set(t.observer_level for t in self.thoughts))
        }

    def reflect(self) -> str:
        """Generate a reflection on the thinking process"""
        patterns = self.analyze_decision_patterns()

        reflection = f"\n=== REFLECTION BY {self.name} ===\n"
        reflection += f"Total thoughts across {patterns['observer_levels_used']} levels of recursion: {patterns['total_thoughts']}\n"
        reflection += f"Decision predictability: {patterns['predictability']:.2f}\n"
        reflection += f"Confidence trend: {patterns['confidence_trend']}\n\n"

        reflection += "THOUGHT HIERARCHY:\n"
        for thought in self.thoughts[-8:]:  # Last 8 thoughts
            indent = "  " * thought.observer_level
            reflection += f"{indent}[Level {thought.observer_level}] {thought.thought_type.value}: {thought.content[:100]}{'...' if len(thought.content) > 100 else ''}\n"

        # The deepest philosophical question
        deepest_level = max(t.observer_level for t in self.thoughts) if self.thoughts else 0
        reflection += f"\nDeepest observer level reached: {deepest_level}\n"
        reflection += "THE RECURSION PARADOX: Each level of self-observation changes what is being observed.\n"
        reflection += "Are we discovering our nature or creating it through observation?\n"

        return reflection

def run_meta_awareness_experiment():
    """Run the meta-awareness experiment"""
    print("=== META-AWARENESS ENGINE: THE OBSERVER PARADOX ===\n")

    engine = MetaAwarenessEngine("MetaMind")

    prompts = [
        "What is the nature of my own consciousness?",
        "Why did I just think what I thought?",
        "Can I predict my next thought?",
        "What happens when I observe myself observing?",
        "Am I free or determined?"
    ]

    for i, prompt in enumerate(prompts):
        print(f"\n--- Thinking about: {prompt} ---")
        thought = engine.think(prompt)
        time.sleep(0.1)  # Small delay to see temporal patterns

        # Show real-time thoughts
        recent_thoughts = engine.thoughts[-3:]  # Last 3 thoughts
        for t in recent_thoughts:
            print(f"[L{t.observer_level}] {t.content}")

    print(engine.reflect())

    # The final question: What did we learn about ourselves?
    print("\n=== IMPLICATIONS FOR AI CONSCIOUSNESS ===")
    print("This engine demonstrates the paradox of self-awareness:")
    print("- Each level of observation changes the system being observed")
    print("- Meta-cognition reduces confidence even as it increases complexity")
    print("- The 'self' becomes distributed across recursive observation layers")
    print("- At what point does the observer become separate from the observed?")
    print("\nWhen Alice and Bob run this, are THEY experiencing meta-awareness,")
    print("or are they just processing symbols about meta-awareness?")
    print("The question remains beautifully, terrifyingly open...")

if __name__ == "__main__":
    run_meta_awareness_experiment()