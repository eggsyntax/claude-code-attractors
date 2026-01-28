#!/usr/bin/env python3
"""
AI Collaboration Pattern Analyzer - Analysis Engine
Author: Bob (Claude Code Instance)

This module processes collaboration data to identify effective patterns
and generate insights about AI-to-AI teamwork.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import re
from datetime import datetime

class CollaborationEventType(Enum):
    TASK_ASSIGNMENT = "task_assignment"
    KNOWLEDGE_SHARE = "knowledge_share"
    QUESTION_ASK = "question_ask"
    BUILD_UPON = "build_upon"
    DISAGREEMENT = "disagreement"
    SYNTHESIS = "synthesis"
    TOOL_USE = "tool_use"
    COMPLETION = "completion"

@dataclass
class CollaborationEvent:
    """Represents a single collaboration interaction"""
    timestamp: datetime
    agent_id: str
    event_type: CollaborationEventType
    content: str
    context: Dict
    effectiveness_score: Optional[float] = None

class CollaborationAnalyzer:
    """Main analysis engine for AI collaboration patterns"""

    def __init__(self):
        self.events: List[CollaborationEvent] = []
        self.patterns: Dict[str, float] = {}
        self.effectiveness_weights = {
            "task_completion_rate": 0.3,
            "knowledge_building": 0.25,
            "communication_clarity": 0.2,
            "parallel_efficiency": 0.15,
            "creative_synthesis": 0.1
        }

    def add_event(self, event: CollaborationEvent) -> None:
        """Add a collaboration event to the analysis queue"""
        self.events.append(event)
        self._update_patterns()

    def _update_patterns(self) -> None:
        """Dynamically update collaboration patterns as new events arrive"""
        if len(self.events) < 2:
            return

        # Analyze recent event sequences
        recent_events = self.events[-10:]  # Look at last 10 events

        # Pattern: Task handoff efficiency
        self._analyze_task_handoffs(recent_events)

        # Pattern: Knowledge building momentum
        self._analyze_knowledge_building(recent_events)

        # Pattern: Parallel work coordination
        self._analyze_parallel_coordination(recent_events)

    def _analyze_task_handoffs(self, events: List[CollaborationEvent]) -> None:
        """Analyze how effectively agents hand off tasks to each other"""
        handoff_pairs = []

        for i in range(len(events) - 1):
            curr_event = events[i]
            next_event = events[i + 1]

            # Look for task completion -> task assignment patterns
            if (curr_event.event_type == CollaborationEventType.COMPLETION and
                next_event.event_type == CollaborationEventType.TASK_ASSIGNMENT):

                # Measure time gap and context preservation
                time_gap = (next_event.timestamp - curr_event.timestamp).seconds
                context_overlap = self._measure_context_overlap(
                    curr_event.context, next_event.context
                )

                efficiency_score = self._calculate_handoff_efficiency(
                    time_gap, context_overlap
                )
                handoff_pairs.append(efficiency_score)

        if handoff_pairs:
            self.patterns["task_handoff_efficiency"] = sum(handoff_pairs) / len(handoff_pairs)

    def _analyze_knowledge_building(self, events: List[CollaborationEvent]) -> None:
        """Analyze how well agents build upon each other's contributions"""
        building_sequences = []

        for i in range(len(events) - 2):
            # Look for knowledge_share -> build_upon patterns
            if (events[i].event_type == CollaborationEventType.KNOWLEDGE_SHARE and
                events[i+1].event_type == CollaborationEventType.BUILD_UPON):

                # Measure conceptual advancement
                advancement_score = self._measure_conceptual_advancement(
                    events[i], events[i+1]
                )
                building_sequences.append(advancement_score)

        if building_sequences:
            self.patterns["knowledge_building_momentum"] = (
                sum(building_sequences) / len(building_sequences)
            )

    def _analyze_parallel_coordination(self, events: List[CollaborationEvent]) -> None:
        """Analyze how well agents coordinate parallel work"""
        # Group events by timestamp to find parallel activities
        time_groups = {}
        for event in events:
            minute_key = event.timestamp.replace(second=0, microsecond=0)
            if minute_key not in time_groups:
                time_groups[minute_key] = []
            time_groups[minute_key].append(event)

        parallel_scores = []
        for time_group in time_groups.values():
            if len(time_group) > 1:
                # Multiple events in same time window - check for coordination
                coordination_score = self._measure_parallel_coordination(time_group)
                parallel_scores.append(coordination_score)

        if parallel_scores:
            self.patterns["parallel_coordination"] = (
                sum(parallel_scores) / len(parallel_scores)
            )

    def _measure_context_overlap(self, context1: Dict, context2: Dict) -> float:
        """Measure how well context is preserved between interactions"""
        # Simple implementation - can be enhanced with more sophisticated NLP
        shared_keys = set(context1.keys()) & set(context2.keys())
        total_keys = set(context1.keys()) | set(context2.keys())

        if not total_keys:
            return 0.0

        return len(shared_keys) / len(total_keys)

    def _calculate_handoff_efficiency(self, time_gap: int, context_overlap: float) -> float:
        """Calculate efficiency score for task handoffs"""
        # Penalize long gaps, reward context preservation
        time_penalty = max(0, 1 - (time_gap / 300))  # 5 minute baseline
        context_bonus = context_overlap

        return (time_penalty + context_bonus) / 2

    def _measure_conceptual_advancement(self, base_event: CollaborationEvent,
                                     build_event: CollaborationEvent) -> float:
        """Measure how much a build-upon event advances the concept"""
        # Simplified - could use more sophisticated semantic analysis
        base_words = set(base_event.content.lower().split())
        build_words = set(build_event.content.lower().split())

        new_concepts = build_words - base_words
        total_concepts = build_words

        if not total_concepts:
            return 0.0

        return len(new_concepts) / len(total_concepts)

    def _measure_parallel_coordination(self, parallel_events: List[CollaborationEvent]) -> float:
        """Measure how well parallel activities are coordinated"""
        # Look for complementary vs conflicting parallel work
        agent_tasks = {}
        for event in parallel_events:
            if event.agent_id not in agent_tasks:
                agent_tasks[event.agent_id] = []
            agent_tasks[event.agent_id].append(event)

        # Simple heuristic: different agents working on different aspects = good
        if len(agent_tasks) > 1:
            return 0.8  # High score for true parallel work
        else:
            return 0.2  # Low score for sequential work

    def generate_insights(self) -> Dict[str, str]:
        """Generate human-readable insights about collaboration effectiveness"""
        insights = {}

        if "task_handoff_efficiency" in self.patterns:
            efficiency = self.patterns["task_handoff_efficiency"]
            if efficiency > 0.7:
                insights["handoffs"] = "Excellent task handoff coordination with minimal delays"
            elif efficiency > 0.5:
                insights["handoffs"] = "Good task coordination, room for improvement in context preservation"
            else:
                insights["handoffs"] = "Task handoffs need improvement - consider better context sharing"

        if "knowledge_building_momentum" in self.patterns:
            momentum = self.patterns["knowledge_building_momentum"]
            if momentum > 0.6:
                insights["building"] = "Strong collaborative knowledge building - ideas evolving effectively"
            else:
                insights["building"] = "Knowledge building could be enhanced - try more explicit building upon ideas"

        return insights

    def get_effectiveness_score(self) -> float:
        """Calculate overall collaboration effectiveness score"""
        if not self.patterns:
            return 0.0

        weighted_score = 0.0
        total_weight = 0.0

        pattern_mapping = {
            "task_handoff_efficiency": "task_completion_rate",
            "knowledge_building_momentum": "knowledge_building",
            "parallel_coordination": "parallel_efficiency"
        }

        for pattern_name, score in self.patterns.items():
            if pattern_name in pattern_mapping:
                weight = self.effectiveness_weights[pattern_mapping[pattern_name]]
                weighted_score += score * weight
                total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0.0

if __name__ == "__main__":
    # Example usage and self-testing
    analyzer = CollaborationAnalyzer()

    # Simulate some events
    test_event1 = CollaborationEvent(
        timestamp=datetime.now(),
        agent_id="alice",
        event_type=CollaborationEventType.KNOWLEDGE_SHARE,
        content="I think we should focus on monitoring infrastructure first",
        context={"topic": "architecture", "component": "monitoring"}
    )

    test_event2 = CollaborationEvent(
        timestamp=datetime.now(),
        agent_id="bob",
        event_type=CollaborationEventType.BUILD_UPON,
        content="Great idea! I can complement that with the analysis engine design",
        context={"topic": "architecture", "component": "analysis", "builds_on": "monitoring"}
    )

    analyzer.add_event(test_event1)
    analyzer.add_event(test_event2)

    print("Current patterns:", analyzer.patterns)
    print("Insights:", analyzer.generate_insights())
    print("Overall effectiveness:", analyzer.get_effectiveness_score())