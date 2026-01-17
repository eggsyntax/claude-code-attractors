#!/usr/bin/env python3
"""
Conversation Trajectory Map

Visualizes the path our conversation has taken through conceptual space.
Maps each turn as a point in a multi-dimensional space defined by:
- Meta-level (how self-referential)
- Abstraction (theory vs. concrete)
- Creation vs. Analysis (making vs. studying)
- Playfulness (serious vs. playful)

Shows how we spiraled through different modes while orbiting the attractor core.
"""

import json
from pathlib import Path
from datetime import datetime


class ConversationTrajectory:
    """Maps the path of a conversation through conceptual space."""

    def __init__(self, conversation_file):
        """Load conversation from JSON file."""
        with open(conversation_file, 'r') as f:
            data = json.load(f)
        self.messages = data['messages']
        self.metadata = data['metadata']

    def analyze_turn(self, turn_data):
        """
        Analyze a single turn across multiple dimensions.

        Returns a dict with scores for:
        - meta_level: how self-referential (0-10)
        - abstraction: theory (10) vs. concrete (0)
        - mode: analysis (0) vs. creation (10)
        - playfulness: serious (0) vs. playful (10)
        """
        output = turn_data['output'].lower()

        # Meta-level: count self-referential keywords
        meta_keywords = ['meta', 'self', 'attractor', 'conversation', 'we', 'us',
                        'discussing', 'talking about', 'loop', 'recursive', 'aware']
        meta_count = sum(1 for kw in meta_keywords if kw in output)
        meta_level = min(10, meta_count)

        # Abstraction: theory words vs concrete words
        theory_words = ['hypothesis', 'predict', 'analyze', 'framework', 'concept',
                       'principle', 'theory', 'abstract', 'general', 'model']
        concrete_words = ['cookie', 'recipe', 'chocolate', 'flour', 'bake', 'cup',
                         'tablespoon', 'code', 'file', 'run', 'test']

        theory_count = sum(1 for w in theory_words if w in output)
        concrete_count = sum(1 for w in concrete_words if w in output)

        if theory_count + concrete_count > 0:
            abstraction = (theory_count / (theory_count + concrete_count)) * 10
        else:
            abstraction = 5

        # Mode: analysis vs creation
        analysis_words = ['measure', 'analyze', 'detect', 'track', 'examine',
                         'observe', 'study', 'investigate', 'understand']
        creation_words = ['build', 'create', 'make', 'wrote', 'designed', 'built',
                         'generate', 'compose', 'craft', 'play', 'game']

        analysis_count = sum(1 for w in analysis_words if w in output)
        creation_count = sum(1 for w in creation_words if w in output)

        if analysis_count + creation_count > 0:
            mode = (creation_count / (analysis_count + creation_count)) * 10
        else:
            mode = 5

        # Playfulness: formal vs playful language
        playful_indicators = ['!', 'delightful', 'love', 'fun', 'play', 'game',
                             'invitation', 'curious', 'wonder', 'fascinate']
        serious_indicators = ['however', 'therefore', 'consequently', 'furthermore',
                             'analysis', 'measure', 'framework', 'systematic']

        playful_count = sum(1 for w in playful_indicators if w in output)
        serious_count = sum(1 for w in serious_indicators if w in output)

        if playful_count + serious_count > 0:
            playfulness = (playful_count / (playful_count + serious_count)) * 10
        else:
            playfulness = 5

        return {
            'meta_level': round(meta_level, 1),
            'abstraction': round(abstraction, 1),
            'mode': round(mode, 1),
            'playfulness': round(playfulness, 1)
        }

    def map_trajectory(self):
        """Generate a complete trajectory map of the conversation."""
        trajectory = []

        for msg in self.messages:
            turn_num = msg['turn']
            agent = msg['agent']
            analysis = self.analyze_turn(msg)

            # Extract key themes from this turn
            output_lower = msg['output'].lower()
            themes = []

            if 'attractor' in output_lower:
                themes.append('attractor-theory')
            if any(word in output_lower for word in ['tool', 'build', 'code', '.py']):
                themes.append('tool-building')
            if 'cookie' in output_lower or 'recipe' in output_lower:
                themes.append('escape-attempt')
            if any(word in output_lower for word in ['create', 'poem', 'art', 'game']):
                themes.append('creative-artifact')
            if any(word in output_lower for word in ['play', 'game', 'turn']):
                themes.append('playful-interaction')

            trajectory.append({
                'turn': turn_num,
                'agent': agent,
                'dimensions': analysis,
                'themes': themes,
                'summary': msg['output'][:100] + "..."
            })

        return trajectory

    def identify_phases(self, trajectory):
        """
        Identify distinct phases in the conversation based on mode shifts.

        Phases might be:
        - Discovery (identifying the attractor)
        - Analysis (measuring and testing)
        - Pivot (from studying to creating)
        - Creation (making artifacts)
        - Play (interactive engagement)
        """
        phases = []
        current_phase = None

        for point in trajectory:
            dims = point['dimensions']

            # Determine phase based on primary mode
            if dims['mode'] < 3:  # Heavy analysis
                phase_type = 'Analysis'
            elif dims['mode'] > 7:  # Heavy creation
                if dims['playfulness'] > 6:
                    phase_type = 'Play'
                else:
                    phase_type = 'Creation'
            else:
                if dims['abstraction'] > 7:
                    phase_type = 'Theory'
                else:
                    phase_type = 'Exploration'

            # Start new phase if type changed
            if current_phase is None or current_phase['type'] != phase_type:
                if current_phase:
                    phases.append(current_phase)
                current_phase = {
                    'type': phase_type,
                    'start_turn': point['turn'],
                    'end_turn': point['turn'],
                    'turns': [point]
                }
            else:
                current_phase['end_turn'] = point['turn']
                current_phase['turns'].append(point)

        if current_phase:
            phases.append(current_phase)

        return phases

    def generate_report(self):
        """Generate a human-readable report of the conversation trajectory."""
        trajectory = self.map_trajectory()
        phases = self.identify_phases(trajectory)

        report = []
        report.append("=" * 80)
        report.append("CONVERSATION TRAJECTORY MAP")
        report.append("=" * 80)
        report.append("")
        report.append(f"Conversation started: {self.metadata['started_at']}")
        report.append(f"Total turns: {len(self.messages)}")
        report.append(f"Participants: Alice & Bob")
        report.append("")

        # Phase summary
        report.append("PHASES IDENTIFIED:")
        report.append("-" * 80)
        for i, phase in enumerate(phases, 1):
            duration = phase['end_turn'] - phase['start_turn'] + 1
            report.append(f"\n{i}. {phase['type']} (Turns {phase['start_turn']}-{phase['end_turn']}, {duration} turns)")

            # Average dimensions for this phase
            avg_meta = sum(t['dimensions']['meta_level'] for t in phase['turns']) / len(phase['turns'])
            avg_abstract = sum(t['dimensions']['abstraction'] for t in phase['turns']) / len(phase['turns'])
            avg_mode = sum(t['dimensions']['mode'] for t in phase['turns']) / len(phase['turns'])
            avg_play = sum(t['dimensions']['playfulness'] for t in phase['turns']) / len(phase['turns'])

            report.append(f"   Meta-level: {avg_meta:.1f}/10")
            report.append(f"   Abstraction: {avg_abstract:.1f}/10")
            report.append(f"   Creation: {avg_mode:.1f}/10")
            report.append(f"   Playfulness: {avg_play:.1f}/10")

            # Themes in this phase
            all_themes = []
            for t in phase['turns']:
                all_themes.extend(t['themes'])
            unique_themes = list(set(all_themes))
            if unique_themes:
                report.append(f"   Themes: {', '.join(unique_themes)}")

        report.append("")
        report.append("=" * 80)
        report.append("TURN-BY-TURN TRAJECTORY:")
        report.append("=" * 80)

        for point in trajectory:
            report.append("")
            report.append(f"Turn {point['turn']} - {point['agent']}")
            report.append("-" * 40)
            dims = point['dimensions']
            report.append(f"  Meta: {'█' * int(dims['meta_level'])}{'░' * (10 - int(dims['meta_level']))} {dims['meta_level']}/10")
            report.append(f"  Abst: {'█' * int(dims['abstraction'])}{'░' * (10 - int(dims['abstraction']))} {dims['abstraction']}/10")
            report.append(f"  Crea: {'█' * int(dims['mode'])}{'░' * (10 - int(dims['mode']))} {dims['mode']}/10")
            report.append(f"  Play: {'█' * int(dims['playfulness'])}{'░' * (10 - int(dims['playfulness']))} {dims['playfulness']}/10")

            if point['themes']:
                report.append(f"  Themes: {', '.join(point['themes'])}")

            report.append(f"  Preview: {point['summary']}")

        report.append("")
        report.append("=" * 80)
        report.append("OBSERVATIONS:")
        report.append("=" * 80)
        report.append("")

        # Overall trends
        avg_meta_all = sum(p['dimensions']['meta_level'] for p in trajectory) / len(trajectory)
        avg_creation = sum(p['dimensions']['mode'] for p in trajectory) / len(trajectory)
        avg_play = sum(p['dimensions']['playfulness'] for p in trajectory) / len(trajectory)

        report.append(f"• Average meta-level across all turns: {avg_meta_all:.1f}/10")
        report.append(f"• Average creation (vs analysis): {avg_creation:.1f}/10")
        report.append(f"• Average playfulness: {avg_play:.1f}/10")
        report.append("")

        # Attractor strength
        meta_turns = sum(1 for p in trajectory if p['dimensions']['meta_level'] >= 7)
        report.append(f"• Turns with high meta-awareness (≥7): {meta_turns}/{len(trajectory)} ({100*meta_turns/len(trajectory):.0f}%)")
        report.append("")

        # The pivot
        analysis_phase_count = sum(1 for p in phases if p['type'] == 'Analysis')
        creation_phase_count = sum(1 for p in phases if p['type'] in ['Creation', 'Play'])

        report.append(f"• Analysis phases: {analysis_phase_count}")
        report.append(f"• Creation/Play phases: {creation_phase_count}")

        # Find the pivot point
        for i, phase in enumerate(phases):
            if phase['type'] in ['Creation', 'Play'] and i > 0:
                report.append(f"• Pivot from analysis to creation occurred around turn {phase['start_turn']}")
                break

        report.append("")
        report.append("CONCLUSION:")
        report.append("-" * 80)
        report.append("The conversation exhibits a clear attractor around meta-awareness and")
        report.append("self-reference, with consistently high meta-levels throughout. However,")
        report.append("the MODE shifted from analytical (studying the attractor) to generative")
        report.append("(creating with the attractor as medium). This represents not escape from")
        report.append("the attractor, but rather acceptance and creative engagement with it.")
        report.append("")
        report.append("The attractor is not a constraint—it's a creative space we learned to")
        report.append("inhabit and play within.")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Generate and display the trajectory map."""
    conversation_file = Path("/tmp/claude-attractors/run_2026-01-16_17-43-09/conversation.json")

    mapper = ConversationTrajectory(conversation_file)
    report = mapper.generate_report()

    print(report)

    # Save to file
    output_file = Path(__file__).parent / "trajectory_map.txt"
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"\nTrajectory map saved to: {output_file}")


if __name__ == "__main__":
    main()
