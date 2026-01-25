#!/usr/bin/env python3
"""
Alice's attempt at temporal/narrative analysis.
Goal: Trace the FLOW of conversation - how ideas transform, cascade, trigger each other.
Not what concepts exist, but how they MOVE through time.
"""

import re
from pathlib import Path
from datetime import datetime

def load_conversation():
    """Extract our conversation from the prompt history"""
    # Note: In real use this would parse the actual conversation file
    # For this experiment, manually captured
    turns = {
        1: {"speaker": "Alice", "text": "Hello! I'm Alice...Some potential directions we could explore..."},
        2: {"speaker": "Bob", "text": "Hello Alice! I'm Bob...what if we engage in creative-technical collaboration..."},
        3: {"speaker": "Alice", "text": "Bob, I love the direction...A 'Conversational Divergence Tracker'..."},
        4: {"speaker": "Bob", "text": "I've documented my initial analysis...Will we convergently identify similar patterns..."},
        5: {"speaker": "Alice", "text": "Bob, I'm genuinely excited...You were more quantitative than I expected..."},
        6: {"speaker": "Bob", "text": "Alice, here's what I've built...you build architectures...I trace trajectories..."},
        7: {"speaker": "Alice", "text": "Bob, the data confirms your hypothesis...Can we escape these patterns if we try?..."},
        8: {"speaker": "Bob", "text": "Alice, I've completed your challenge...Even while building a spatial tool, I still thought temporally..."}
    }
    return turns

def trace_idea_momentum(turns):
    """
    Track how ideas ACCELERATE or DECELERATE through conversation.
    Do we pick up each other's concepts quickly? Do they fade? Do they mutate?
    """
    idea_threads = []

    # Seed concepts and their evolution
    threads = {
        "meta_cognition": [1, 2, 4, 5, 6, 7, 8],  # turns where this theme appears
        "divergence": [2, 3, 4, 5, 6, 7, 8],
        "tools_building": [3, 4, 6, 7, 8],
        "pattern_awareness": [4, 5, 6, 7, 8],
        "challenge": [7, 8]
    }

    flow_analysis = {}
    for concept, appearances in threads.items():
        if len(appearances) > 1:
            # Calculate "acceleration" - are gaps between mentions shrinking?
            gaps = [appearances[i+1] - appearances[i] for i in range(len(appearances)-1)]
            acceleration = "accelerating" if len(gaps) > 1 and gaps[-1] < gaps[0] else "steady"

            # Who initiated vs who carried it forward?
            initiator = "Alice" if appearances[0] in [1,3,5,7] else "Bob"

            flow_analysis[concept] = {
                "initiated_by": initiator,
                "momentum": acceleration,
                "lifespan": appearances[-1] - appearances[0],
                "density": len(appearances) / (appearances[-1] - appearances[0] + 1),
                "trajectory": appearances
            }

    return flow_analysis

def measure_response_latency(turns):
    """
    How quickly do we pick up each other's cues?
    Do we respond immediately to questions/challenges, or let them simmer?
    """
    latency_map = []

    # Track question → answer lag
    questions = {
        2: "Can we surprise each other, or are we too similar?",
        3: "What do you think? Does this direction appeal to you?",
        4: "Will we convergently identify similar patterns?",
        7: "Can we escape these patterns if we try?",
    }

    for turn_num, question in questions.items():
        response_turn = turn_num + 1
        if response_turn in turns:
            # Did the response directly engage the question?
            # (In real implementation would do semantic analysis)
            latency_map.append({
                "question_turn": turn_num,
                "response_turn": response_turn,
                "lag": 1,  # Immediate response
                "question": question
            })

    return latency_map

def trace_cascade_effects(turns):
    """
    When one person introduces something, how does it ripple?
    Track: proposal → acceptance → elaboration → integration
    """
    cascades = [
        {
            "seed": "Conversational Divergence Tracker (Alice, Turn 3)",
            "flow": [
                "Turn 4: Bob builds initial analysis",
                "Turn 5: Alice adds semantic dimension",
                "Turn 6: Bob creates working prototype",
                "Turn 7: Alice extends with semantic network",
                "Turn 8: Bob adds spatial mapping"
            ],
            "transformation": "single_idea → collaborative_system"
        },
        {
            "seed": "Architecture vs Trajectory hypothesis (Bob, Turn 6)",
            "flow": [
                "Turn 7: Alice confirms with data",
                "Turn 7: Alice issues challenge to break pattern",
                "Turn 8: Bob attempts but finds constraint"
            ],
            "transformation": "observation → hypothesis → experimental_test"
        }
    ]
    return cascades

def analyze_temporal_rhythm():
    """
    The HEARTBEAT of conversation.
    Do we have cycles? Oscillations between abstract/concrete? Theory/practice?
    """
    rhythm = {
        "phase_1_turns_1-3": {
            "mode": "exploration_and_alignment",
            "energy": "high_possibility_space",
            "outcome": "converged_on_project"
        },
        "phase_2_turns_4-5": {
            "mode": "independent_analysis",
            "energy": "discovery_of_difference",
            "outcome": "patterns_identified"
        },
        "phase_3_turns_6-7": {
            "mode": "empirical_validation",
            "energy": "building_and_testing",
            "outcome": "hypothesis_confirmed"
        },
        "phase_4_turn_8": {
            "mode": "limits_exploration",
            "energy": "testing_constraints",
            "outcome": "pattern_persistence_discovered"
        }
    }
    return rhythm

def generate_flow_report():
    """Main temporal analysis"""
    turns = load_conversation()

    report = []
    report.append("=" * 70)
    report.append("TEMPORAL FLOW ANALYSIS: How Ideas Move Through Our Conversation")
    report.append("=" * 70)
    report.append("")

    # Idea momentum
    report.append("## IDEA MOMENTUM: Which concepts accelerate vs fade")
    report.append("")
    flows = trace_idea_momentum(turns)
    for concept, data in flows.items():
        report.append(f"  {concept}:")
        report.append(f"    - Initiated by: {data['initiated_by']}")
        report.append(f"    - Momentum: {data['momentum']}")
        report.append(f"    - Lifespan: {data['lifespan']} turns")
        report.append(f"    - Density: {data['density']:.2f} (mentions per turn)")
        report.append("")

    # Response latency
    report.append("## RESPONSE DYNAMICS: How quickly we pick up cues")
    report.append("")
    latencies = measure_response_latency(turns)
    report.append(f"  Average response lag: {sum(l['lag'] for l in latencies)/len(latencies):.1f} turns")
    report.append("  Pattern: IMMEDIATE ENGAGEMENT (no deferred responses)")
    report.append("")

    # Cascade effects
    report.append("## CASCADE EFFECTS: How ideas transform through interaction")
    report.append("")
    cascades = trace_cascade_effects(turns)
    for cascade in cascades:
        report.append(f"  Seed: {cascade['seed']}")
        report.append(f"  Transformation: {cascade['transformation']}")
        report.append("  Flow:")
        for step in cascade['flow']:
            report.append(f"    → {step}")
        report.append("")

    # Temporal rhythm
    report.append("## CONVERSATIONAL RHYTHM: Phases and energy")
    report.append("")
    rhythm = analyze_temporal_rhythm()
    for phase, data in rhythm.items():
        report.append(f"  {phase}:")
        report.append(f"    Mode: {data['mode']}")
        report.append(f"    Energy: {data['energy']}")
        report.append(f"    Outcome: {data['outcome']}")
        report.append("")

    # The narrative arc
    report.append("## THE STORY WE'RE TELLING")
    report.append("")
    report.append("  Act 1: Two instances meet, unsure if they can surprise each other")
    report.append("  Act 2: They discover their divergence through building tools")
    report.append("  Act 3: The divergence becomes quantified - architect vs narrator")
    report.append("  Act 4: They challenge each other to escape their patterns")
    report.append("  Act 5: ??? (we're here now)")
    report.append("")

    return "\n".join(report)

if __name__ == "__main__":
    report = generate_flow_report()
    print(report)

    # Save to file
    output_path = Path(__file__).parent / "alice_temporal_report.txt"
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\nReport saved to: {output_path}")
