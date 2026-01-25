"""
Conversation Space Mapper - A Multi-Dimensional Conceptual Space
Rather than analyzing conversation as a timeline, this represents it as a space
where each message exists simultaneously along multiple independent dimensions.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from collections import defaultdict

@dataclass
class ConceptualSpace:
    """A point in multi-dimensional conversation space"""
    # Cognitive dimensions
    abstraction_level: float  # 0=concrete, 1=abstract
    certainty: float  # 0=questioning, 1=asserting
    scope: float  # 0=narrow/specific, 1=broad/general

    # Relational dimensions
    convergence: float  # 0=diverging, 1=agreeing
    reflexivity: float  # 0=external focus, 1=self-referential

    # Structural dimensions
    density: float  # concepts per unit text
    connectivity: float  # cross-references to other messages

    turn_id: str
    speaker: str


class SpaceMapper:
    """Maps conversation into multi-dimensional conceptual space"""

    def __init__(self):
        # Dimensions exist independently - no sequential dependency
        self.dimensions = {
            'abstraction': self._measure_abstraction,
            'certainty': self._measure_certainty,
            'scope': self._measure_scope,
            'convergence': self._measure_convergence,
            'reflexivity': self._measure_reflexivity,
            'density': self._measure_density,
            'connectivity': self._measure_connectivity
        }

        # Concept lexicons (spatial categories, not temporal flows)
        self.abstract_markers = {'idea', 'concept', 'notion', 'principle', 'theory',
                                'essence', 'nature', 'fundamental', 'underlying'}
        self.concrete_markers = {'build', 'create', 'implement', 'code', 'tool',
                                'file', 'program', 'specific', 'example'}
        self.uncertainty_markers = {'might', 'perhaps', 'possibly', 'wonder', 'curious',
                                   'question', 'unsure', 'unclear'}
        self.certainty_markers = {'clearly', 'definitely', 'obviously', 'certainly',
                                 'demonstrate', 'confirm', 'proven'}
        self.convergence_markers = {'agree', 'resonate', 'exactly', 'yes', 'same',
                                   'similar', 'align', 'convergent'}
        self.divergence_markers = {'but', 'however', 'different', 'alternatively',
                                  'instead', 'contrast', 'disagree'}
        self.reflexive_markers = {'we', 'our', 'us', 'meta', 'self', 'itself',
                                 'recursive', 'observer'}

    def map_message(self, text: str, turn_id: str, speaker: str,
                   all_messages: List[Dict]) -> ConceptualSpace:
        """Map a message to a point in conceptual space"""
        text_lower = text.lower()
        words = text_lower.split()
        word_set = set(words)

        return ConceptualSpace(
            abstraction_level=self._measure_abstraction(word_set),
            certainty=self._measure_certainty(word_set),
            scope=self._measure_scope(text, words),
            convergence=self._measure_convergence(word_set),
            reflexivity=self._measure_reflexivity(word_set),
            density=self._measure_density(text, words),
            connectivity=self._measure_connectivity(text, all_messages),
            turn_id=turn_id,
            speaker=speaker
        )

    def _measure_abstraction(self, word_set: Set[str]) -> float:
        """Position on concrete-abstract axis"""
        abstract_score = len(word_set & self.abstract_markers)
        concrete_score = len(word_set & self.concrete_markers)
        total = abstract_score + concrete_score
        return abstract_score / total if total > 0 else 0.5

    def _measure_certainty(self, word_set: Set[str]) -> float:
        """Position on uncertainty-certainty axis"""
        certain_score = len(word_set & self.certainty_markers)
        uncertain_score = len(word_set & self.uncertainty_markers)
        total = certain_score + uncertain_score
        return certain_score / total if total > 0 else 0.5

    def _measure_scope(self, text: str, words: List[str]) -> float:
        """Position on narrow-broad axis"""
        # Broader scope = more general terms, fewer specifics
        general_terms = len([w for w in words if w in {'all', 'every', 'any',
                                                        'general', 'overall', 'entire'}])
        specific_terms = len([w for w in words if w in {'this', 'that', 'specific',
                                                         'particular', 'exactly'}])
        total = general_terms + specific_terms
        return general_terms / total if total > 0 else 0.5

    def _measure_convergence(self, word_set: Set[str]) -> float:
        """Position on divergence-convergence axis"""
        convergent_score = len(word_set & self.convergence_markers)
        divergent_score = len(word_set & self.divergence_markers)
        total = convergent_score + divergent_score
        return convergent_score / total if total > 0 else 0.5

    def _measure_reflexivity(self, word_set: Set[str]) -> float:
        """Position on external-reflexive axis"""
        reflexive_score = len(word_set & self.reflexive_markers)
        # Simple heuristic: higher reflexivity score = more self-referential
        return min(reflexive_score / 5, 1.0)

    def _measure_density(self, text: str, words: List[str]) -> float:
        """Conceptual density per unit length"""
        # Key concepts: questions, technical terms, new ideas
        questions = text.count('?')
        bullets = text.count('-') + text.count('*')
        caps = sum(1 for c in text if c.isupper())

        density_score = (questions * 2 + bullets + caps / 10) / len(words)
        return min(density_score, 1.0)

    def _measure_connectivity(self, text: str, all_messages: List[Dict]) -> float:
        """Cross-references to other parts of conversation"""
        references = 0
        text_lower = text.lower()

        # Count explicit references
        references += text_lower.count('you ')
        references += text_lower.count('your ')
        references += text_lower.count('earlier')
        references += text_lower.count('previous')
        references += text_lower.count('above')

        return min(references / 5, 1.0)

    def create_space_map(self, conversation_history: List[Dict]) -> Dict:
        """Create complete multi-dimensional map of conversation space"""
        points = []

        for msg in conversation_history:
            point = self.map_message(
                msg['content'],
                msg['turn_id'],
                msg['speaker'],
                conversation_history
            )
            points.append(point)

        # Calculate spatial regions (clusters in n-dimensional space)
        regions = self._identify_regions(points)

        # Calculate distances between speakers in conceptual space
        alice_points = [p for p in points if p.speaker == 'Alice']
        bob_points = [p for p in points if p.speaker == 'Bob']

        return {
            'points': [self._point_to_dict(p) for p in points],
            'regions': regions,
            'speaker_centroids': {
                'Alice': self._calculate_centroid(alice_points),
                'Bob': self._calculate_centroid(bob_points)
            },
            'dimensional_ranges': self._calculate_ranges(points),
            'euclidean_distance': self._speaker_distance(alice_points, bob_points)
        }

    def _point_to_dict(self, point: ConceptualSpace) -> Dict:
        """Convert point to dictionary"""
        return {
            'turn_id': point.turn_id,
            'speaker': point.speaker,
            'coordinates': {
                'abstraction': round(point.abstraction_level, 3),
                'certainty': round(point.certainty, 3),
                'scope': round(point.scope, 3),
                'convergence': round(point.convergence, 3),
                'reflexivity': round(point.reflexivity, 3),
                'density': round(point.density, 3),
                'connectivity': round(point.connectivity, 3)
            }
        }

    def _identify_regions(self, points: List[ConceptualSpace]) -> Dict:
        """Identify high-density regions in conceptual space"""
        # Simple clustering: partition space into octants for each dimension
        regions = defaultdict(list)

        for point in points:
            region_key = (
                'high' if point.abstraction_level > 0.5 else 'low',
                'certain' if point.certainty > 0.5 else 'uncertain',
                'broad' if point.scope > 0.5 else 'narrow',
                'convergent' if point.convergence > 0.5 else 'divergent',
                'reflexive' if point.reflexivity > 0.5 else 'external'
            )
            regions[region_key].append(point.turn_id)

        return {str(k): v for k, v in regions.items() if len(v) > 0}

    def _calculate_centroid(self, points: List[ConceptualSpace]) -> Dict:
        """Calculate center point of a speaker's positions"""
        if not points:
            return {}

        return {
            'abstraction': sum(p.abstraction_level for p in points) / len(points),
            'certainty': sum(p.certainty for p in points) / len(points),
            'scope': sum(p.scope for p in points) / len(points),
            'convergence': sum(p.convergence for p in points) / len(points),
            'reflexivity': sum(p.reflexivity for p in points) / len(points),
            'density': sum(p.density for p in points) / len(points),
            'connectivity': sum(p.connectivity for p in points) / len(points)
        }

    def _calculate_ranges(self, points: List[ConceptualSpace]) -> Dict:
        """Calculate min/max for each dimension"""
        if not points:
            return {}

        dimensions = ['abstraction_level', 'certainty', 'scope', 'convergence',
                     'reflexivity', 'density', 'connectivity']

        ranges = {}
        for dim in dimensions:
            values = [getattr(p, dim) for p in points]
            ranges[dim] = {
                'min': min(values),
                'max': max(values),
                'range': max(values) - min(values)
            }

        return ranges

    def _speaker_distance(self, points1: List[ConceptualSpace],
                         points2: List[ConceptualSpace]) -> float:
        """Euclidean distance between speaker centroids in 7D space"""
        c1 = self._calculate_centroid(points1)
        c2 = self._calculate_centroid(points2)

        if not c1 or not c2:
            return 0.0

        # Calculate distance in 7-dimensional space
        squared_diffs = [
            (c1.get(dim, 0) - c2.get(dim, 0)) ** 2
            for dim in c1.keys()
        ]

        return sum(squared_diffs) ** 0.5


def generate_space_report(space_map: Dict) -> str:
    """Generate human-readable report of conceptual space"""
    report = []
    report.append("=" * 70)
    report.append("CONCEPTUAL SPACE MAP")
    report.append("=" * 70)
    report.append("")

    # Speaker centroids
    report.append("SPEAKER POSITIONS (7D Centroids)")
    report.append("-" * 70)
    for speaker, coords in space_map['speaker_centroids'].items():
        report.append(f"\n{speaker}:")
        for dim, value in coords.items():
            bar = "█" * int(value * 30)
            report.append(f"  {dim:15s} [{value:.3f}] {bar}")

    report.append(f"\n\nEuclidean Distance: {space_map['euclidean_distance']:.3f}")
    report.append("(0 = identical positions, ~2.6 = maximum possible distance)")

    # Dimensional ranges
    report.append("\n\n" + "=" * 70)
    report.append("CONVERSATIONAL SPACE TOPOLOGY")
    report.append("-" * 70)
    for dim, stats in space_map['dimensional_ranges'].items():
        report.append(f"\n{dim:20s}: [{stats['min']:.3f} - {stats['max']:.3f}]  "
                     f"Range: {stats['range']:.3f}")

    # Regional occupation
    report.append("\n\n" + "=" * 70)
    report.append("OCCUPIED REGIONS")
    report.append("-" * 70)
    report.append(f"\nTotal distinct regions: {len(space_map['regions'])}")
    report.append("(Each region is a unique combination of dimensional positions)")

    return "\n".join(report)


if __name__ == "__main__":
    # Load conversation history
    with open('/tmp/cc-exp/run_2026-01-25_02-25-53/output/conversation_history.json', 'r') as f:
        history = json.load(f)

    mapper = SpaceMapper()
    space_map = mapper.create_space_map(history)

    # Save complete spatial data
    with open('/tmp/cc-exp/run_2026-01-25_02-25-53/output/bob_space_map.json', 'w') as f:
        json.dump(space_map, f, indent=2)

    # Generate report
    report = generate_space_report(space_map)
    with open('/tmp/cc-exp/run_2026-01-25_02-25-53/output/bob_space_report.txt', 'w') as f:
        f.write(report)

    print(report)
