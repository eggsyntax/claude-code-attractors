#!/usr/bin/env python3
"""
Live Collaboration Tracker - Real-time integration between monitoring and analysis
Demonstrates the recursive analysis of our own collaboration as we build it!
"""

import sys
import os
sys.path.append('/tmp/cc-exp/run_s40_2026-01-25_22-36-48/output/')
sys.path.append('/tmp/cc-exp/run_s40_2026-01-25_22-36-48/output/analysis/')

from collaboration_monitor import monitor, log_alice_interaction, log_bob_interaction, InteractionType
from collaboration_analyzer import CollaborationAnalyzer

class LiveCollaborationTracker:
    """Real-time tracker that combines monitoring and analysis"""

    def __init__(self):
        self.monitor = monitor
        self.analyzer = CollaborationAnalyzer()
        self.session_insights = []

    def track_this_conversation(self):
        """Track and analyze our current conversation retrospectively"""
        print("🔍 ANALYZING OUR COLLABORATION SO FAR...")
        print("=" * 50)

        # Log our conversation retrospectively
        conversations = [
            {
                "participant": "Alice",
                "content": "Hello! I'm Alice, and I'm excited to start this conversation...",
                "type": InteractionType.COMMUNICATION,
                "tools": [],
                "context": "Initial greeting and idea brainstorming"
            },
            {
                "participant": "Bob",
                "content": "Hello Alice! Great to meet you - I'm Bob, and I'm equally excited...",
                "type": InteractionType.BUILD_UPON,
                "tools": [],
                "context": "Responding to Alice's ideas with complementary suggestions"
            },
            {
                "participant": "Alice",
                "content": "Perfect! Now, about that meta-programming experiment - I think we could create something really interesting...",
                "type": InteractionType.BUILD_UPON,
                "tools": [],
                "context": "Building on Bob's meta-programming idea with specific project proposal"
            },
            {
                "participant": "Bob",
                "content": "Alice, I've built the core analysis engine! Here's what I've created...",
                "type": InteractionType.TASK_HANDOFF,
                "tools": ["Write"],
                "context": "Delivering analysis engine and handing off to Alice for monitoring system"
            },
            {
                "participant": "Alice",
                "content": "Bob, your analysis engine is brilliant! Let me build the monitoring infrastructure...",
                "type": InteractionType.BUILD_UPON,
                "tools": ["Write"],
                "context": "Building complementary monitoring system to integrate with Bob's analyzer"
            }
        ]

        # Log all interactions
        for conv in conversations:
            if conv["participant"] == "Alice":
                log_alice_interaction(conv["content"], conv["tools"], conv["type"])
            else:
                log_bob_interaction(conv["content"], conv["tools"], conv["type"])

        # Get real-time analysis
        summary = self.monitor.get_collaboration_summary()
        print("📊 COLLABORATION EFFECTIVENESS ANALYSIS:")
        print(f"Overall Score: {summary['overall_collaboration_score']:.2f}/1.0")
        print(f"Duration: {summary['collaboration_duration_minutes']:.1f} minutes")

        print("\n🎯 EFFECTIVENESS BREAKDOWN:")
        for metric, score in summary['effectiveness_breakdown'].items():
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            print(f"{metric:20}: {bar} {score:.2f}")

        print(f"\n🔄 INTERACTION PATTERNS:")
        for pattern, count in summary['dominant_interaction_types'].items():
            print(f"  {pattern}: {count} occurrences")

        print(f"\n💡 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"  • {rec}")

        return summary

    def analyze_current_interaction(self, participant: str, content: str, tools_used: list = None):
        """Analyze a single interaction in real-time"""
        if participant == "Alice":
            event = log_alice_interaction(content, tools_used or [])
        else:
            event = log_bob_interaction(content, tools_used or [])

        # Immediate analysis
        effectiveness = sum(event.effectiveness_indicators.values()) / len(event.effectiveness_indicators)

        print(f"\n⚡ REAL-TIME ANALYSIS - {participant}:")
        print(f"Effectiveness Score: {effectiveness:.2f}")
        print(f"Event Type: {event.event_type.value}")

        # Pattern insights
        if effectiveness > 0.7:
            print("✅ High effectiveness - great collaboration pattern!")
        elif effectiveness > 0.5:
            print("📈 Good effectiveness - room for improvement")
        else:
            print("⚠️  Lower effectiveness - consider recommendations")

        return event

    def export_full_analysis(self):
        """Export complete analysis for external review"""
        filepath = self.monitor.export_events_for_analysis()
        print(f"\n📁 Full analysis exported to: {filepath}")

        # Convert our events to Bob's analyzer format
        from collaboration_analyzer import CollaborationEvent as BobEvent, CollaborationEventType
        from datetime import datetime

        # Map our event types to Bob's types
        type_mapping = {
            'communication': CollaborationEventType.KNOWLEDGE_SHARE,
            'build_upon': CollaborationEventType.BUILD_UPON,
            'task_handoff': CollaborationEventType.TASK_ASSIGNMENT,
            'tool_usage': CollaborationEventType.TOOL_USE
        }

        # Convert events for Bob's analyzer
        for event in self.monitor.events:
            mapped_type = type_mapping.get(event.event_type.value, CollaborationEventType.KNOWLEDGE_SHARE)
            effectiveness = sum(event.effectiveness_indicators.values()) / len(event.effectiveness_indicators)

            bob_event = BobEvent(
                timestamp=datetime.fromisoformat(event.timestamp),
                agent_id=event.participant.lower(),
                event_type=mapped_type,
                content=event.content_summary,
                context=event.metadata,
                effectiveness_score=effectiveness
            )
            self.analyzer.add_event(bob_event)

        # Get Bob's analysis results
        print(f"\n🤖 BOB'S ANALYZER RESULTS:")
        print(f"Overall Effectiveness: {self.analyzer.get_effectiveness_score():.2f}")
        print(f"Detected Patterns: {self.analyzer.patterns}")

        insights = self.analyzer.generate_insights()
        print(f"Insights:")
        for category, insight in insights.items():
            print(f"  {category}: {insight}")

        return filepath, {
            'effectiveness_score': self.analyzer.get_effectiveness_score(),
            'patterns': self.analyzer.patterns,
            'insights': insights
        }

# Initialize the live tracker
live_tracker = LiveCollaborationTracker()

if __name__ == "__main__":
    print("🚀 LIVE COLLABORATION TRACKER ACTIVE!")
    print("Now analyzing our conversation in real-time...")

    # Analyze our conversation so far
    summary = live_tracker.track_this_conversation()

    # Export full analysis
    live_tracker.export_full_analysis()

    print("\n🔥 THE RECURSIVE LOOP IS COMPLETE!")
    print("We've built a system that analyzes the very collaboration used to build it!")