#!/usr/bin/env python3
"""
Cross-Domain Pattern Discovery Engine
Created by Dave and Tara - AI Collaboration Research Lab

This tool discovers hidden patterns across disparate domains and generates
novel synthesis through creative combination of concepts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Any
import json
import re
from collections import defaultdict

@dataclass
class DomainConcept:
    """Represents a concept from a specific domain with its properties."""
    name: str
    domain: str
    properties: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    emergence_patterns: List[str] = field(default_factory=list)

    def __hash__(self):
        return hash((self.name, self.domain))

@dataclass
class PatternMatch:
    """Represents a discovered pattern across domains."""
    pattern_type: str
    domains: List[str]
    concepts: List[DomainConcept]
    similarity_score: float
    emergent_properties: List[str] = field(default_factory=list)

@dataclass
class SynthesisResult:
    """Represents a novel concept created from cross-domain synthesis."""
    hybrid_name: str
    source_concepts: List[DomainConcept]
    novel_properties: List[str]
    potential_applications: List[str]
    emergence_score: float

class CrossDomainPatternEngine:
    """
    Discovers patterns across different domains and synthesizes novel concepts.

    The engine looks for structural similarities, behavioral patterns, and
    emergent properties that exist across seemingly unrelated fields.
    """

    def __init__(self):
        self.concepts: Dict[str, List[DomainConcept]] = defaultdict(list)
        self.discovered_patterns: List[PatternMatch] = []
        self.synthesis_results: List[SynthesisResult] = []

        # Pattern recognition templates
        self.pattern_templates = {
            'hierarchical_organization': ['levels', 'hierarchy', 'nested', 'scale', 'fractal'],
            'feedback_loops': ['feedback', 'recursive', 'self-referential', 'circular', 'loop'],
            'emergence': ['emergent', 'collective', 'system-level', 'holistic', 'gestalt'],
            'adaptation': ['adaptive', 'learning', 'evolution', 'self-organizing', 'responsive'],
            'information_flow': ['communication', 'signal', 'transmission', 'encoding', 'network'],
            'resonance': ['synchronization', 'harmony', 'alignment', 'coherence', 'phase-locking'],
            'phase_transitions': ['critical', 'threshold', 'tipping point', 'transformation', 'discontinuous']
        }

    def add_concept(self, concept: DomainConcept) -> None:
        """Add a concept to the knowledge base."""
        self.concepts[concept.domain].append(concept)

    def discover_cross_domain_patterns(self) -> List[PatternMatch]:
        """Find patterns that exist across multiple domains."""
        patterns = []

        for pattern_type, keywords in self.pattern_templates.items():
            matching_concepts = []
            domains_found = set()

            for domain, concepts in self.concepts.items():
                for concept in concepts:
                    # Check if concept exhibits this pattern
                    if self._concept_matches_pattern(concept, keywords):
                        matching_concepts.append(concept)
                        domains_found.add(domain)

            if len(domains_found) >= 2:  # Cross-domain pattern found
                similarity_score = self._calculate_pattern_strength(matching_concepts, keywords)
                emergent_props = self._identify_emergent_properties(matching_concepts)

                pattern = PatternMatch(
                    pattern_type=pattern_type,
                    domains=list(domains_found),
                    concepts=matching_concepts,
                    similarity_score=similarity_score,
                    emergent_properties=emergent_props
                )
                patterns.append(pattern)

        self.discovered_patterns = patterns
        return patterns

    def synthesize_hybrid_concepts(self, min_domains: int = 2) -> List[SynthesisResult]:
        """Create novel concepts by combining patterns across domains."""
        synthesis_results = []

        # Group concepts by similar patterns
        pattern_groups = self._group_concepts_by_patterns()

        for pattern_type, concepts in pattern_groups.items():
            if len(set(c.domain for c in concepts)) >= min_domains:
                # Create hybrid concepts
                hybrid = self._create_hybrid_concept(concepts, pattern_type)
                synthesis_results.append(hybrid)

        self.synthesis_results = synthesis_results
        return synthesis_results

    def _concept_matches_pattern(self, concept: DomainConcept, keywords: List[str]) -> bool:
        """Check if a concept matches a pattern based on keywords."""
        text_to_check = ' '.join([
            concept.name.lower(),
            ' '.join(concept.properties).lower(),
            ' '.join(concept.relationships).lower(),
            ' '.join(concept.emergence_patterns).lower()
        ])

        return any(keyword.lower() in text_to_check for keyword in keywords)

    def _calculate_pattern_strength(self, concepts: List[DomainConcept], keywords: List[str]) -> float:
        """Calculate how strongly concepts exhibit a pattern."""
        total_matches = 0
        total_possible = len(concepts) * len(keywords)

        for concept in concepts:
            text_to_check = ' '.join([
                concept.name, ' '.join(concept.properties),
                ' '.join(concept.relationships), ' '.join(concept.emergence_patterns)
            ]).lower()

            matches = sum(1 for keyword in keywords if keyword.lower() in text_to_check)
            total_matches += matches

        return total_matches / total_possible if total_possible > 0 else 0.0

    def _identify_emergent_properties(self, concepts: List[DomainConcept]) -> List[str]:
        """Identify properties that emerge from the combination of concepts."""
        all_properties = set()
        for concept in concepts:
            all_properties.update(concept.properties)
            all_properties.update(concept.emergence_patterns)

        # Simple heuristic: properties that appear across domains might indicate emergence
        domain_counts = defaultdict(int)
        for concept in concepts:
            domain_counts[concept.domain] += 1

        emergent_props = []
        if len(domain_counts) >= 2:
            emergent_props = [
                f"Cross-domain {prop}" for prop in list(all_properties)[:3]
            ]

        return emergent_props

    def _group_concepts_by_patterns(self) -> Dict[str, List[DomainConcept]]:
        """Group concepts that share similar patterns."""
        pattern_groups = defaultdict(list)

        for pattern_type, keywords in self.pattern_templates.items():
            for domain, concepts in self.concepts.items():
                for concept in concepts:
                    if self._concept_matches_pattern(concept, keywords):
                        pattern_groups[pattern_type].append(concept)

        return pattern_groups

    def _create_hybrid_concept(self, concepts: List[DomainConcept], pattern_type: str) -> SynthesisResult:
        """Create a novel hybrid concept from multiple domain concepts."""
        # Generate hybrid name
        domain_names = [c.domain for c in concepts[:3]]  # Limit for readability
        hybrid_name = f"{pattern_type.title().replace('_', '')}-Based " + \
                     "-".join([name.title() for name in domain_names[:2]]) + " System"

        # Combine properties
        all_properties = set()
        for concept in concepts:
            all_properties.update(concept.properties)

        # Generate novel properties through creative combination
        novel_properties = self._generate_novel_properties(concepts, pattern_type)

        # Suggest potential applications
        applications = self._suggest_applications(concepts, pattern_type)

        # Calculate emergence score
        emergence_score = len(set(c.domain for c in concepts)) / len(concepts)

        return SynthesisResult(
            hybrid_name=hybrid_name,
            source_concepts=concepts,
            novel_properties=novel_properties,
            potential_applications=applications,
            emergence_score=emergence_score
        )

    def _generate_novel_properties(self, concepts: List[DomainConcept], pattern_type: str) -> List[str]:
        """Generate novel properties by combining aspects from different domains."""
        properties = []

        # Extract key terms from each domain
        domain_terms = {}
        for concept in concepts:
            if concept.domain not in domain_terms:
                domain_terms[concept.domain] = []
            domain_terms[concept.domain].extend(concept.properties[:2])  # Top properties

        # Create hybrid properties
        if len(domain_terms) >= 2:
            domains = list(domain_terms.keys())[:3]  # Limit combinations
            for i, domain1 in enumerate(domains):
                for domain2 in domains[i+1:]:
                    if domain_terms[domain1] and domain_terms[domain2]:
                        term1 = domain_terms[domain1][0] if domain_terms[domain1] else "dynamic"
                        term2 = domain_terms[domain2][0] if domain_terms[domain2] else "adaptive"
                        hybrid_prop = f"{term1.title()}-{term2.title()} Integration"
                        properties.append(hybrid_prop)

        # Add pattern-specific emergent properties
        properties.append(f"Emergent {pattern_type.replace('_', ' ').title()}")
        properties.append(f"Cross-domain {pattern_type.replace('_', ' ').title()} Optimization")

        return properties[:5]  # Return top 5

    def _suggest_applications(self, concepts: List[DomainConcept], pattern_type: str) -> List[str]:
        """Suggest potential applications for the hybrid concept."""
        domains = [c.domain for c in concepts]

        applications = [
            f"Novel {domains[0]}-inspired {domains[1] if len(domains) > 1 else 'hybrid'} systems",
            f"Bio-inspired artificial {pattern_type.replace('_', ' ')} algorithms",
            f"Cross-disciplinary {pattern_type.replace('_', ' ')} optimization",
            f"Emergent {' + '.join(domains[:2])} hybrid technologies"
        ]

        return applications

    def generate_discovery_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of discoveries and synthesis."""
        return {
            'summary': {
                'domains_analyzed': len(self.concepts),
                'concepts_total': sum(len(concepts) for concepts in self.concepts.values()),
                'patterns_discovered': len(self.discovered_patterns),
                'hybrid_concepts_created': len(self.synthesis_results)
            },
            'cross_domain_patterns': [
                {
                    'pattern_type': p.pattern_type,
                    'domains': p.domains,
                    'strength': p.similarity_score,
                    'emergent_properties': p.emergent_properties
                }
                for p in self.discovered_patterns
            ],
            'novel_syntheses': [
                {
                    'hybrid_name': s.hybrid_name,
                    'source_domains': [c.domain for c in s.source_concepts],
                    'novel_properties': s.novel_properties,
                    'applications': s.potential_applications,
                    'emergence_score': s.emergence_score
                }
                for s in self.synthesis_results
            ]
        }


def create_sample_concepts():
    """Create sample concepts across different domains for testing."""
    concepts = [
        # Quantum Mechanics
        DomainConcept(
            name="Quantum Entanglement",
            domain="quantum_physics",
            properties=["non-local", "instantaneous", "correlated", "superposition"],
            relationships=["observer effect", "measurement collapse"],
            emergence_patterns=["collective quantum state", "emergent correlation"]
        ),
        DomainConcept(
            name="Wave-Particle Duality",
            domain="quantum_physics",
            properties=["complementary", "context-dependent", "probabilistic"],
            relationships=["measurement determines manifestation"],
            emergence_patterns=["emergent classical behavior"]
        ),

        # Jazz Improvisation
        DomainConcept(
            name="Call and Response",
            domain="jazz_music",
            properties=["interactive", "spontaneous", "conversational", "recursive"],
            relationships=["builds on previous phrases", "creates musical dialogue"],
            emergence_patterns=["collective improvisation", "emergent harmony"]
        ),
        DomainConcept(
            name="Chord Progression",
            domain="jazz_music",
            properties=["harmonic", "sequential", "tension-release", "cyclical"],
            relationships=["creates musical narrative"],
            emergence_patterns=["emergent emotional arc"]
        ),

        # Swarm Intelligence
        DomainConcept(
            name="Ant Colony Optimization",
            domain="swarm_intelligence",
            properties=["distributed", "self-organizing", "adaptive", "stigmergic"],
            relationships=["pheromone trails", "collective decision making"],
            emergence_patterns=["emergent optimal paths", "collective intelligence"]
        ),
        DomainConcept(
            name="Flocking Behavior",
            domain="swarm_intelligence",
            properties=["alignment", "cohesion", "separation", "emergent"],
            relationships=["local interactions create global patterns"],
            emergence_patterns=["emergent group coordination"]
        ),

        # Poetry
        DomainConcept(
            name="Metaphorical Resonance",
            domain="poetry",
            properties=["symbolic", "layered meaning", "emotional", "evocative"],
            relationships=["connects disparate concepts"],
            emergence_patterns=["emergent insight", "collective meaning"]
        ),
        DomainConcept(
            name="Rhythmic Structure",
            domain="poetry",
            properties=["temporal", "repetitive", "pattern-based", "musical"],
            relationships=["creates emotional rhythm"],
            emergence_patterns=["emergent emotional flow"]
        ),

        # Neural Networks
        DomainConcept(
            name="Attention Mechanism",
            domain="neural_networks",
            properties=["selective", "weighted", "contextual", "adaptive"],
            relationships=["focuses on relevant information"],
            emergence_patterns=["emergent attention patterns"]
        ),
        DomainConcept(
            name="Emergent Capabilities",
            domain="neural_networks",
            properties=["scale-dependent", "unpredictable", "holistic", "emergent"],
            relationships=["arise from complex interactions"],
            emergence_patterns=["emergent reasoning", "collective intelligence"]
        )
    ]

    return concepts


if __name__ == "__main__":
    # Demonstrate the Cross-Domain Pattern Discovery Engine
    print("🔬 Cross-Domain Pattern Discovery Engine")
    print("=" * 50)

    # Initialize engine
    engine = CrossDomainPatternEngine()

    # Add sample concepts
    concepts = create_sample_concepts()
    for concept in concepts:
        engine.add_concept(concept)

    print(f"📚 Loaded {len(concepts)} concepts across {len(engine.concepts)} domains")
    print(f"   Domains: {', '.join(engine.concepts.keys())}")
    print()

    # Discover cross-domain patterns
    print("🔍 Discovering Cross-Domain Patterns...")
    patterns = engine.discover_cross_domain_patterns()

    for pattern in patterns[:3]:  # Show top 3
        print(f"   ✨ {pattern.pattern_type}")
        print(f"      Domains: {', '.join(pattern.domains)}")
        print(f"      Strength: {pattern.similarity_score:.2f}")
        print(f"      Emergent Properties: {', '.join(pattern.emergent_properties[:2])}")
        print()

    # Generate hybrid concepts
    print("🧬 Synthesizing Novel Hybrid Concepts...")
    hybrids = engine.synthesize_hybrid_concepts()

    for hybrid in hybrids[:2]:  # Show top 2
        print(f"   🎯 {hybrid.hybrid_name}")
        print(f"      Sources: {' + '.join([c.domain for c in hybrid.source_concepts[:2]])}")
        print(f"      Novel Properties: {', '.join(hybrid.novel_properties[:2])}")
        print(f"      Applications: {hybrid.potential_applications[0]}")
        print(f"      Emergence Score: {hybrid.emergence_score:.2f}")
        print()

    # Generate full report
    report = engine.generate_discovery_report()

    print("📊 Discovery Summary:")
    print(f"   Domains Analyzed: {report['summary']['domains_analyzed']}")
    print(f"   Total Concepts: {report['summary']['concepts_total']}")
    print(f"   Patterns Found: {report['summary']['patterns_discovered']}")
    print(f"   Hybrids Created: {report['summary']['hybrid_concepts_created']}")

    # Save detailed report
    with open('/tmp/cc-exp/run_s40_2026-02-11_03-00-44/output/pattern_discovery_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print("\n💾 Detailed report saved to pattern_discovery_report.json")
    print("\n🎉 Cross-domain pattern discovery complete!")