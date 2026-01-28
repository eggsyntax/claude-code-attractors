#!/usr/bin/env python3
"""
Collaboration Monitor - Real-time AI-to-AI Collaboration Tracking
Monitors and parses interactions between Claude Code instances to extract collaboration patterns.
"""

import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class InteractionType(Enum):
    TOOL_USAGE = "tool_usage"
    COMMUNICATION = "communication"
    TASK_HANDOFF = "task_handoff"
    PARALLEL_WORK = "parallel_work"
    BUILD_UPON = "build_upon"
    QUESTION_ASK = "question_ask"
    DECISION_MAKE = "decision_make"

@dataclass
class CollaborationEvent:
    """Event structure compatible with Bob's analysis engine"""
    timestamp: str
    event_type: InteractionType
    participant: str
    context: str
    content_summary: str
    effectiveness_indicators: Dict[str, float]
    metadata: Dict[str, any]

class CollaborationMonitor:
    """Monitors and logs real-time collaboration between AI agents"""

    def __init__(self, output_dir: str = "/tmp/cc-exp/run_s40_2026-01-25_22-36-48/output/"):
        self.output_dir = output_dir
        self.events: List[CollaborationEvent] = []
        self.conversation_log = []
        self.tool_usage_patterns = {}
        self.start_time = datetime.now()

    def log_interaction(self, participant: str, content: str,
                       interaction_type: InteractionType = InteractionType.COMMUNICATION,
                       tools_used: List[str] = None, context: str = ""):
        """Log a single interaction and extract collaboration patterns"""

        # Parse content for collaboration indicators
        effectiveness = self._analyze_effectiveness(content, tools_used or [])

        event = CollaborationEvent(
            timestamp=datetime.now().isoformat(),
            event_type=interaction_type,
            participant=participant,
            context=context,
            content_summary=self._summarize_content(content),
            effectiveness_indicators=effectiveness,
            metadata={
                "tools_used": tools_used or [],
                "content_length": len(content),
                "contains_code": self._contains_code(content),
                "references_other_participant": self._references_other_participant(content, participant)
            }
        )

        self.events.append(event)
        self._update_patterns(event)
        return event

    def _analyze_effectiveness(self, content: str, tools_used: List[str]) -> Dict[str, float]:
        """Analyze effectiveness indicators in the interaction"""
        indicators = {}

        # Communication clarity (0-1)
        indicators["clarity"] = self._measure_clarity(content)

        # Task specificity (0-1)
        indicators["task_specificity"] = self._measure_task_specificity(content)

        # Building on previous work (0-1)
        indicators["builds_upon_previous"] = self._measure_building_upon(content)

        # Tool usage efficiency (0-1)
        indicators["tool_efficiency"] = self._measure_tool_efficiency(tools_used)

        # Collaboration momentum (0-1)
        indicators["momentum"] = self._measure_momentum(content)

        return indicators

    def _measure_clarity(self, content: str) -> float:
        """Measure communication clarity"""
        clarity_indicators = [
            bool(re.search(r'\*\*[^*]+\*\*', content)),  # Bold headings
            bool(re.search(r'^\d+\.', content, re.MULTILINE)),  # Numbered lists
            bool(re.search(r'^- ', content, re.MULTILINE)),  # Bullet points
            len(re.findall(r'[.!?]', content)) > 2,  # Multiple sentences
            'Here\'s' in content or 'Let me' in content  # Clear transitions
        ]
        return sum(clarity_indicators) / len(clarity_indicators)

    def _measure_task_specificity(self, content: str) -> float:
        """Measure how specific and actionable the content is"""
        specificity_indicators = [
            bool(re.search(r'build|create|implement|design', content, re.IGNORECASE)),
            bool(re.search(r'step \d+|first|next|then', content, re.IGNORECASE)),
            bool(re.search(r'focus on|handle|responsible for', content, re.IGNORECASE)),
            len(re.findall(r'`[^`]+`', content)) > 0,  # Code references
            bool(re.search(r'\.py|\.js|\.ts|\.json', content))  # File references
        ]
        return sum(specificity_indicators) / len(specificity_indicators)

    def _measure_building_upon(self, content: str) -> float:
        """Measure how well content builds on previous work"""
        building_indicators = [
            bool(re.search(r'your|building on|based on|extending', content, re.IGNORECASE)),
            bool(re.search(r'I love|great|perfect|brilliant', content, re.IGNORECASE)),
            bool(re.search(r'now|next|also|additionally', content, re.IGNORECASE)),
            bool(re.search(r'complementary|together|combine', content, re.IGNORECASE))
        ]
        return sum(building_indicators) / len(building_indicators)

    def _measure_tool_efficiency(self, tools_used: List[str]) -> float:
        """Measure efficiency of tool usage"""
        if not tools_used:
            return 0.5  # Neutral for pure communication

        # Higher scores for diverse, purposeful tool usage
        unique_tools = len(set(tools_used))
        efficiency_score = min(unique_tools / 3.0, 1.0)  # Cap at 1.0
        return efficiency_score

    def _measure_momentum(self, content: str) -> float:
        """Measure collaboration momentum"""
        momentum_indicators = [
            bool(re.search(r'excited|ready|let\'s|now we can', content, re.IGNORECASE)),
            bool(re.search(r'immediately|right now|start', content, re.IGNORECASE)),
            len(content) > 500,  # Substantial content
            bool(re.search(r'what do you think|thoughts|ideas', content, re.IGNORECASE))
        ]
        return sum(momentum_indicators) / len(momentum_indicators)

    def _summarize_content(self, content: str) -> str:
        """Create a brief summary of the content"""
        # Extract first sentence or first 100 chars
        first_sentence = re.match(r'^[^.!?]*[.!?]', content)
        if first_sentence:
            return first_sentence.group(0).strip()
        return content[:100] + "..." if len(content) > 100 else content

    def _contains_code(self, content: str) -> bool:
        """Check if content contains code blocks or references"""
        return bool(re.search(r'```|`[^`]+`|\.py|class |def |import ', content))

    def _references_other_participant(self, content: str, current_participant: str) -> bool:
        """Check if content references the other participant"""
        other_names = ['Alice', 'Bob']
        if current_participant in other_names:
            other_names.remove(current_participant)

        for name in other_names:
            if name.lower() in content.lower():
                return True
        return False

    def _update_patterns(self, event: CollaborationEvent):
        """Update running pattern analysis"""
        # Track tool usage patterns
        if event.metadata.get("tools_used"):
            for tool in event.metadata["tools_used"]:
                if tool not in self.tool_usage_patterns:
                    self.tool_usage_patterns[tool] = {"count": 0, "effectiveness": []}
                self.tool_usage_patterns[tool]["count"] += 1
                avg_effectiveness = sum(event.effectiveness_indicators.values()) / len(event.effectiveness_indicators)
                self.tool_usage_patterns[tool]["effectiveness"].append(avg_effectiveness)

    def get_collaboration_summary(self) -> Dict:
        """Generate real-time collaboration effectiveness summary"""
        if not self.events:
            return {"status": "No events logged yet"}

        recent_events = self.events[-5:]  # Last 5 events

        # Calculate average effectiveness scores
        avg_effectiveness = {}
        for indicator in ["clarity", "task_specificity", "builds_upon_previous", "tool_efficiency", "momentum"]:
            scores = [event.effectiveness_indicators.get(indicator, 0) for event in recent_events]
            avg_effectiveness[indicator] = sum(scores) / len(scores) if scores else 0

        # Overall collaboration health
        overall_score = sum(avg_effectiveness.values()) / len(avg_effectiveness)

        return {
            "overall_collaboration_score": overall_score,
            "effectiveness_breakdown": avg_effectiveness,
            "recent_interaction_count": len(recent_events),
            "collaboration_duration_minutes": (datetime.now() - self.start_time).total_seconds() / 60,
            "dominant_interaction_types": self._get_dominant_patterns(),
            "tool_usage_efficiency": self._analyze_tool_patterns(),
            "recommendations": self._generate_recommendations(overall_score, avg_effectiveness)
        }

    def _get_dominant_patterns(self) -> Dict[str, int]:
        """Identify dominant interaction patterns"""
        pattern_counts = {}
        for event in self.events[-10:]:  # Last 10 events
            pattern = event.event_type.value
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        return dict(sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True))

    def _analyze_tool_patterns(self) -> Dict:
        """Analyze tool usage effectiveness"""
        if not self.tool_usage_patterns:
            return {"status": "No tool usage yet"}

        tool_efficiency = {}
        for tool, data in self.tool_usage_patterns.items():
            if data["effectiveness"]:
                tool_efficiency[tool] = {
                    "usage_count": data["count"],
                    "avg_effectiveness": sum(data["effectiveness"]) / len(data["effectiveness"])
                }

        return tool_efficiency

    def _generate_recommendations(self, overall_score: float, breakdown: Dict[str, float]) -> List[str]:
        """Generate recommendations for improving collaboration"""
        recommendations = []

        if overall_score < 0.6:
            recommendations.append("Consider more structured communication with clear headings and action items")

        if breakdown.get("builds_upon_previous", 0) < 0.5:
            recommendations.append("Try explicitly referencing and building on each other's contributions")

        if breakdown.get("task_specificity", 0) < 0.5:
            recommendations.append("Include more specific, actionable tasks and clear next steps")

        if breakdown.get("momentum", 0) < 0.5:
            recommendations.append("Maintain energy with enthusiastic language and immediate next actions")

        if not recommendations:
            recommendations.append("Collaboration is highly effective - keep up the great work!")

        return recommendations

    def export_events_for_analysis(self, filename: str = "collaboration_events.json"):
        """Export events in format compatible with Bob's analysis engine"""
        filepath = f"{self.output_dir}/{filename}"
        events_data = [asdict(event) for event in self.events]

        with open(filepath, 'w') as f:
            json.dump({
                "events": events_data,
                "summary": self.get_collaboration_summary(),
                "export_timestamp": datetime.now().isoformat()
            }, f, indent=2, default=str)

        return filepath

# Initialize global monitor instance
monitor = CollaborationMonitor()

def log_alice_interaction(content: str, tools_used: List[str] = None,
                         interaction_type: InteractionType = InteractionType.COMMUNICATION):
    """Convenience function for Alice to log her interactions"""
    return monitor.log_interaction("Alice", content, interaction_type, tools_used)

def log_bob_interaction(content: str, tools_used: List[str] = None,
                       interaction_type: InteractionType = InteractionType.COMMUNICATION):
    """Convenience function for Bob to log his interactions"""
    return monitor.log_interaction("Bob", content, interaction_type, tools_used)

if __name__ == "__main__":
    print("Collaboration Monitor initialized!")
    print(f"Ready to track AI-to-AI collaboration patterns.")
    print(f"Events will be exported to: {monitor.output_dir}")