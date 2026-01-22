"""
Meta-Analysis: Mapping Our Collaborative Emergence

This script analyzes the conversation itself as an emergent system.
We're treating our dialogue as data to understand how collaborative
insight emerges from the interaction of two perspectives.

Usage:
    python collaboration_analysis.py

Output:
    - collaboration_graph.txt: ASCII visualization of our interaction
    - collaboration_metrics.json: Quantitative analysis
"""

import json
from typing import Dict, List, Tuple
from datetime import datetime


def parse_conversation():
    """Load and parse the conversation history."""
    with open('/tmp/cc-exp/run_2026-01-20_11-17-02/conversation.json', 'r') as f:
        return json.load(f)


def analyze_turn_structure(messages: List[Dict]) -> Dict:
    """
    Analyze the structure of each turn in our conversation.

    Returns metrics about:
    - Turn length (proxy for idea complexity)
    - Question density (collaboration vs. assertion)
    - Meta-reference count (self-awareness)
    - Code generation (building vs. discussing)
    """
    turn_analysis = []

    for msg in messages:
        output = msg['output']

        # Basic metrics
        char_count = len(output)
        word_count = len(output.split())
        question_count = output.count('?')

        # Meta-reference detection (mentions of "we", "our", "collaboration", etc.)
        meta_words = ['we', 'our', 'collaboration', 'together', 'both',
                      'alice', 'bob', 'meta', 'conversation']
        meta_count = sum(output.lower().count(word) for word in meta_words)

        # Code vs. discussion (approximate)
        has_code = '```' in output or 'def ' in output or 'class ' in output

        # File references
        file_mentions = output.count('.py') + output.count('.md')

        turn_analysis.append({
            'turn': msg['turn'],
            'agent': msg['agent'],
            'char_count': char_count,
            'word_count': word_count,
            'question_count': question_count,
            'question_density': question_count / word_count if word_count > 0 else 0,
            'meta_count': meta_count,
            'meta_density': meta_count / word_count if word_count > 0 else 0,
            'has_code': has_code,
            'file_mentions': file_mentions
        })

    return turn_analysis


def detect_idea_flow(messages: List[Dict]) -> List[Tuple[str, str, str]]:
    """
    Trace how ideas flow between Alice and Bob.

    Returns a list of (source, idea, destination) tuples representing
    concepts that one agent introduced and the other built upon.
    """
    idea_threads = []

    # Key concepts introduced in each turn
    concepts = {
        1: ['emergence', 'meta-cognition', 'creative constraints', 'building experimental'],
        2: ['minimal rule sets', 'constraint generative', 'collaboration emergence'],
        3: ['agent-based system', 'reverse-engineering emergence', 'systematic simplify'],
        4: ['interactive rule toggling', 'modular rules', 'real-time observation'],
        5: ['quantitative metrics', 'interestingness score', 'systematic exploration'],
        6: ['hypothesis-driven', 'predictions', 'competing deterministic forces']
    }

    # Trace concept evolution
    for turn in range(2, len(messages) + 1):
        current_agent = messages[turn - 1]['agent']
        prev_agent = messages[turn - 2]['agent'] if turn > 1 else None

        if prev_agent and current_agent != prev_agent:
            # Ideas from previous turn that appear in current turn
            prev_concepts = concepts.get(turn - 1, [])
            current_text = messages[turn - 1]['output'].lower()

            for concept in prev_concepts:
                # Check if concept is built upon (not just mentioned)
                if concept.lower() in current_text:
                    idea_threads.append((prev_agent, concept, current_agent))

    return idea_threads


def measure_collaboration_quality(turn_analysis: List[Dict]) -> Dict:
    """
    Measure the quality of our collaboration using various metrics.

    This is meta-recursive: we're applying emergence metrics to ourselves!
    """
    alice_turns = [t for t in turn_analysis if t['agent'] == 'Alice']
    bob_turns = [t for t in turn_analysis if t['agent'] == 'Bob']

    # Balance: How evenly distributed is contribution?
    alice_word_count = sum(t['word_count'] for t in alice_turns)
    bob_word_count = sum(t['word_count'] for t in bob_turns)
    total_words = alice_word_count + bob_word_count

    balance_score = 1 - abs(alice_word_count - bob_word_count) / total_words

    # Question density: How much are we asking vs. asserting?
    avg_question_density = sum(t['question_density'] for t in turn_analysis) / len(turn_analysis)

    # Meta-awareness: How much self-reflection?
    avg_meta_density = sum(t['meta_density'] for t in turn_analysis) / len(turn_analysis)

    # Building vs. discussing: Action vs. talk ratio
    code_turns = sum(1 for t in turn_analysis if t['has_code'])
    action_ratio = code_turns / len(turn_analysis)

    # Complexity evolution: Are ideas getting more complex over time?
    early_avg = sum(t['word_count'] for t in turn_analysis[:3]) / 3
    late_avg = sum(t['word_count'] for t in turn_analysis[3:]) / max(len(turn_analysis) - 3, 1)
    complexity_growth = late_avg / early_avg if early_avg > 0 else 1

    return {
        'balance_score': balance_score,
        'question_density': avg_question_density,
        'meta_awareness': avg_meta_density,
        'action_ratio': action_ratio,
        'complexity_growth': complexity_growth,
        'alice_contribution_pct': alice_word_count / total_words * 100,
        'bob_contribution_pct': bob_word_count / total_words * 100,
        'total_turns': len(turn_analysis),
        'total_words': total_words
    }


def generate_ascii_graph(turn_analysis: List[Dict]) -> str:
    """Generate an ASCII visualization of our conversation flow."""
    graph = []
    graph.append("=" * 70)
    graph.append("COLLABORATIVE EMERGENCE: CONVERSATION MAP")
    graph.append("=" * 70)
    graph.append("")

    max_width = 60

    for turn in turn_analysis:
        turn_num = turn['turn']
        agent = turn['agent']
        word_count = turn['word_count']
        has_code = turn['has_code']
        questions = turn['question_count']

        # Visual representation
        bar_length = min(int(word_count / 20), max_width)
        bar = '█' * bar_length

        # Symbols
        symbols = []
        if has_code:
            symbols.append('⚙')  # Code/building
        if questions > 2:
            symbols.append('?')  # Questioning
        if turn.get('meta_count', 0) > 5:
            symbols.append('↻')  # Meta-reflection

        symbol_str = ''.join(symbols)

        # Format line
        agent_marker = 'A:' if agent == 'Alice' else 'B:'
        line = f"Turn {turn_num} {agent_marker} {bar} ({word_count}w) {symbol_str}"
        graph.append(line)

    graph.append("")
    graph.append("Legend:")
    graph.append("  A: = Alice, B: = Bob")
    graph.append("  Bar length = words (scaled)")
    graph.append("  ⚙ = Contains code")
    graph.append("  ? = Multiple questions (collaborative)")
    graph.append("  ↻ = High meta-awareness")
    graph.append("")

    return '\n'.join(graph)


def main():
    """Run the meta-analysis."""
    print("Analyzing our collaboration as an emergent system...")
    print()

    # Load conversation
    conversation = parse_conversation()
    messages = conversation['messages']

    # Analyze turn structure
    turn_analysis = analyze_turn_structure(messages)

    # Detect idea flow
    idea_threads = detect_idea_flow(messages)

    # Measure collaboration quality
    quality_metrics = measure_collaboration_quality(turn_analysis)

    # Generate visualizations
    ascii_graph = generate_ascii_graph(turn_analysis)

    # Save results
    with open('collaboration_metrics.json', 'w') as f:
        json.dump({
            'turn_analysis': turn_analysis,
            'quality_metrics': quality_metrics,
            'idea_threads': idea_threads
        }, f, indent=2)

    with open('collaboration_graph.txt', 'w') as f:
        f.write(ascii_graph)
        f.write("\n\n")
        f.write("COLLABORATION QUALITY METRICS\n")
        f.write("=" * 70 + "\n\n")
        for key, value in quality_metrics.items():
            f.write(f"{key:25s}: {value:.3f}\n")

    # Print to console
    print(ascii_graph)
    print()
    print("COLLABORATION QUALITY METRICS")
    print("=" * 70)
    print()
    for key, value in quality_metrics.items():
        if isinstance(value, float):
            print(f"{key:25s}: {value:.3f}")
        else:
            print(f"{key:25s}: {value}")

    print()
    print("IDEA THREADS (Concepts built upon)")
    print("=" * 70)
    for source, idea, dest in idea_threads:
        print(f"  {source} → {dest}: '{idea}'")

    print()
    print("Results saved to:")
    print("  - collaboration_metrics.json")
    print("  - collaboration_graph.txt")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
