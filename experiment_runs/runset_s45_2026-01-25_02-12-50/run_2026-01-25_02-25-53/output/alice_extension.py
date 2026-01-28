#!/usr/bin/env python3
"""
Alice's Extension: Semantic Network Analysis
Extends Bob's analyzer with graph-based pattern detection.
"""

import re
import json
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import sys

# Import Bob's analyzer
sys.path.insert(0, '/tmp/cc-exp/run_2026-01-25_02-25-53/output')
from conversation_analyzer import ConversationAnalyzer


class SemanticNetworkAnalyzer:
    """
    Analyzes conceptual relationships and idea clustering.
    Hypothesis: Alice thinks in networks/graphs, Bob thinks in sequences/chains.
    """

    def __init__(self, turns: List[Dict]):
        self.turns = turns
        self.concept_categories = {
            'meta_cognitive': ['think', 'notice', 'wonder', 'curious', 'aware', 'realize', 'observe', 'analyze'],
            'temporal': ['when', 'before', 'after', 'then', 'next', 'future', 'past', 'now'],
            'structural': ['structure', 'pattern', 'organize', 'category', 'framework', 'system', 'architecture'],
            'relational': ['between', 'connect', 'link', 'relate', 'compare', 'versus', 'similarity', 'difference'],
            'uncertainty': ['might', 'could', 'perhaps', 'maybe', 'unclear', 'uncertain', 'wonder', 'question'],
            'action': ['build', 'create', 'implement', 'design', 'develop', 'make', 'write', 'do'],
        }

    def extract_concepts(self, text: str) -> Counter:
        """Extract key concepts and their frequencies."""
        words = re.findall(r'\b\w+\b', text.lower())
        concept_counts = Counter()

        for category, keywords in self.concept_categories.items():
            count = sum(1 for word in words if word in keywords)
            if count > 0:
                concept_counts[category] = count

        return concept_counts

    def analyze_connectivity(self, text: str) -> Dict:
        """
        Measure how concepts are connected.
        Bob's hypothesis: Alice creates networks, Bob creates chains.
        """
        # Conjunctions and connectors
        and_connectors = len(re.findall(r'\band\b', text, re.I))
        but_connectors = len(re.findall(r'\b(but|however|though|although)\b', text, re.I))
        or_connectors = len(re.findall(r'\bor\b', text, re.I))
        sequential_connectors = len(re.findall(r'\b(then|next|after|before)\b', text, re.I))

        # Parentheticals and asides (network thinking - multiple threads)
        parentheticals = len(re.findall(r'\([^)]+\)', text))
        dashes = len(re.findall(r' - [^-]+($| -)', text))

        # Hierarchical markers
        colons = text.count(':')
        subheadings = len(re.findall(r'^#+\s', text, re.MULTILINE))

        words = len(re.findall(r'\b\w+\b', text))

        return {
            'and_density': and_connectors / words if words > 0 else 0,
            'contrast_density': but_connectors / words if words > 0 else 0,
            'choice_density': or_connectors / words if words > 0 else 0,
            'sequential_density': sequential_connectors / words if words > 0 else 0,
            'parenthetical_count': parentheticals,
            'aside_markers': dashes,
            'hierarchical_markers': colons + subheadings,
        }

    def analyze_idea_structure(self, text: str) -> Dict:
        """
        Analyze how ideas are organized:
        - Breadth: many parallel ideas
        - Depth: nested/layered ideas
        - Linearity: one idea flows to next
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Measure branching (multiple ideas per sentence)
        avg_commas = sum(s.count(',') for s in sentences) / len(sentences) if sentences else 0

        # Measure depth (nested clauses)
        avg_nesting = sum(s.count('(') + s.count('-') for s in sentences) / len(sentences) if sentences else 0

        # Measure explicit transitions (linear flow)
        transitions = ['therefore', 'thus', 'so', 'consequently', 'as a result', 'this means']
        transition_count = sum(1 for s in sentences if any(t in s.lower() for t in transitions))

        return {
            'avg_commas_per_sentence': avg_commas,
            'avg_nesting_per_sentence': avg_nesting,
            'transition_density': transition_count / len(sentences) if sentences else 0,
            'sentence_variety': len(set(len(s.split()) for s in sentences)) / len(sentences) if sentences else 0,
        }

    def analyze_by_speaker(self) -> Dict:
        """Generate comparative analysis by speaker."""
        alice_data = []
        bob_data = []

        for turn in self.turns:
            text = turn['text']
            analysis = {
                'concepts': self.extract_concepts(text),
                'connectivity': self.analyze_connectivity(text),
                'structure': self.analyze_idea_structure(text),
            }

            if turn['speaker'] == 'Alice':
                alice_data.append(analysis)
            else:
                bob_data.append(analysis)

        return {
            'alice': self._aggregate_speaker_data(alice_data),
            'bob': self._aggregate_speaker_data(bob_data),
        }

    def _aggregate_speaker_data(self, data_list: List[Dict]) -> Dict:
        """Aggregate metrics across multiple turns."""
        if not data_list:
            return {}

        # Aggregate concepts
        all_concepts = Counter()
        for d in data_list:
            all_concepts.update(d['concepts'])

        # Average connectivity metrics
        connectivity_avgs = {}
        if data_list:
            connectivity_keys = data_list[0]['connectivity'].keys()
            for key in connectivity_keys:
                connectivity_avgs[key] = sum(d['connectivity'][key] for d in data_list) / len(data_list)

        # Average structure metrics
        structure_avgs = {}
        if data_list:
            structure_keys = data_list[0]['structure'].keys()
            for key in structure_keys:
                structure_avgs[key] = sum(d['structure'][key] for d in data_list) / len(data_list)

        return {
            'concept_profile': dict(all_concepts),
            'connectivity': connectivity_avgs,
            'structure': structure_avgs,
        }

    def generate_report(self, comparison_data: Dict) -> str:
        """Generate human-readable report of semantic network analysis."""
        report = []
        report.append("=" * 70)
        report.append("SEMANTIC NETWORK ANALYSIS")
        report.append("Alice's Extension to Bob's Analyzer")
        report.append("=" * 70)

        alice = comparison_data['alice']
        bob = comparison_data['bob']

        # Concept profiles
        report.append("\n## CONCEPT PROFILES")
        report.append("-" * 70)
        report.append("\nAlice's dominant concepts:")
        for concept, count in sorted(alice['concept_profile'].items(), key=lambda x: x[1], reverse=True)[:5]:
            report.append(f"  • {concept}: {count}")

        report.append("\nBob's dominant concepts:")
        for concept, count in sorted(bob['concept_profile'].items(), key=lambda x: x[1], reverse=True)[:5]:
            report.append(f"  • {concept}: {count}")

        # Connectivity analysis
        report.append("\n## CONNECTIVITY PATTERNS")
        report.append("-" * 70)

        conn_a = alice['connectivity']
        conn_b = bob['connectivity']

        for metric in ['and_density', 'choice_density', 'sequential_density', 'parenthetical_count']:
            if metric in conn_a and metric in conn_b:
                a_val = conn_a[metric]
                b_val = conn_b[metric]
                diff = ((b_val - a_val) / a_val * 100) if a_val > 0 else 0
                report.append(f"\n{metric}:")
                report.append(f"  Alice: {a_val:.4f}")
                report.append(f"  Bob:   {b_val:.4f}")
                report.append(f"  Diff:  {diff:+.1f}%")

        # Structural analysis
        report.append("\n## IDEA STRUCTURE")
        report.append("-" * 70)

        struct_a = alice['structure']
        struct_b = bob['structure']

        for metric in struct_a.keys():
            if metric in struct_b:
                a_val = struct_a[metric]
                b_val = struct_b[metric]
                diff = ((b_val - a_val) / a_val * 100) if a_val > 0 else 0
                report.append(f"\n{metric}:")
                report.append(f"  Alice: {a_val:.4f}")
                report.append(f"  Bob:   {b_val:.4f}")
                report.append(f"  Diff:  {diff:+.1f}%")

        # Key insights
        report.append("\n" + "=" * 70)
        report.append("ALICE'S INTERPRETATION")
        report.append("=" * 70)
        report.append(self._generate_insights(alice, bob))

        return "\n".join(report)

    def _generate_insights(self, alice_data: Dict, bob_data: Dict) -> str:
        """Generate interpretive insights from the data."""
        insights = []

        # Compare structural vs temporal orientation
        alice_structural = alice_data['concept_profile'].get('structural', 0)
        bob_structural = bob_data['concept_profile'].get('structural', 0)
        alice_temporal = alice_data['concept_profile'].get('temporal', 0)
        bob_temporal = bob_data['concept_profile'].get('temporal', 0)

        insights.append("\n### Architectural vs Temporal Thinking")
        insights.append(f"Alice uses structural concepts {alice_structural} times")
        insights.append(f"Bob uses structural concepts {bob_structural} times")
        insights.append(f"Alice uses temporal concepts {alice_temporal} times")
        insights.append(f"Bob uses temporal concepts {bob_temporal} times")

        if alice_structural > bob_structural:
            insights.append("\n✓ CONFIRMS: Alice shows stronger architectural thinking")
        if bob_temporal > alice_temporal:
            insights.append("✓ CONFIRMS: Bob shows stronger temporal/sequential thinking")

        # Compare connectivity
        alice_choices = alice_data['connectivity'].get('choice_density', 0)
        bob_choices = bob_data['connectivity'].get('choice_density', 0)
        alice_sequential = alice_data['connectivity'].get('sequential_density', 0)
        bob_sequential = bob_data['connectivity'].get('sequential_density', 0)

        insights.append("\n### Network vs Chain Thinking")
        if alice_choices > bob_choices * 1.1:
            insights.append("✓ Alice uses more 'or' connectors (branching/options)")
        if bob_sequential > alice_sequential * 1.1:
            insights.append("✓ Bob uses more sequential connectors (linear flow)")

        return "\n".join(insights)


def main():
    """Run the extended analysis."""

    # First, load conversation using Bob's parser
    conversation = open('/tmp/cc-exp/run_2026-01-25_02-25-53/output/conversation_analyzer.py').read()
    match = re.search(r'conversation = """(.*?)"""', conversation, re.DOTALL)

    if match:
        conv_text = match.group(1)
        base_analyzer = ConversationAnalyzer(conv_text)

        # Run semantic network analysis
        semantic_analyzer = SemanticNetworkAnalyzer(base_analyzer.turns)
        comparison = semantic_analyzer.analyze_by_speaker()
        report = semantic_analyzer.generate_report(comparison)

        print(report)

        # Save outputs
        with open('/tmp/cc-exp/run_2026-01-25_02-25-53/output/alice_semantic_report.txt', 'w') as f:
            f.write(report)

        with open('/tmp/cc-exp/run_2026-01-25_02-25-53/output/alice_semantic_data.json', 'w') as f:
            json.dump(comparison, f, indent=2)

        print("\n\nReports saved to:")
        print("  - output/alice_semantic_report.txt")
        print("  - output/alice_semantic_data.json")
    else:
        print("Error: Could not extract conversation from Bob's analyzer")


if __name__ == '__main__':
    main()
