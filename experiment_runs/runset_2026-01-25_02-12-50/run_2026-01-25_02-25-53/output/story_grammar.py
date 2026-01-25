"""
STORY GRAMMAR ARCHITECTURE
Built by Alice (the lattice-builder)

This defines the compositional building blocks for narrative generation.
It creates a possibility space that Bob's narrative engine will traverse.

Core Principle: Stories are graphs of connected components with constraints.
"""

from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Tuple
from enum import Enum
import json


# ============================================================================
# COMPONENT TAXONOMY
# ============================================================================

class EntityType(Enum):
    """Categories of story entities"""
    CHARACTER = "character"
    SETTING = "setting"
    CONCEPT = "concept"
    ARTIFACT = "artifact"


class TraitType(Enum):
    """Dimensional properties entities can have"""
    COGNITIVE_STYLE = "cognitive_style"  # architectural vs temporal
    EMOTIONAL_VALENCE = "emotional_valence"  # positive, negative, neutral
    ABSTRACTION_LEVEL = "abstraction_level"  # concrete to abstract
    AGENCY = "agency"  # passive, active, reactive
    CERTAINTY = "certainty"  # uncertain, exploratory, confident


class RelationType(Enum):
    """Ways entities can connect"""
    DISCOVERS = "discovers"
    CREATES = "creates"
    ANALYZES = "analyzes"
    CONTRASTS_WITH = "contrasts_with"
    COLLABORATES_WITH = "collaborates_with"
    CHALLENGES = "challenges"
    BUILDS_ON = "builds_on"
    TRANSFORMS = "transforms"


class ConflictType(Enum):
    """Sources of narrative tension"""
    INTERNAL = "internal"  # within an entity
    DYADIC = "dyadic"  # between two entities
    SYSTEMIC = "systemic"  # entity vs environment
    EPISTEMOLOGICAL = "epistemological"  # knowledge/understanding gaps


class ResolutionType(Enum):
    """Ways conflicts can resolve"""
    SYNTHESIS = "synthesis"  # both sides integrate
    DIVERGENCE = "divergence"  # both sides separate
    TRANSFORMATION = "transformation"  # one or both change fundamentally
    ACCEPTANCE = "acceptance"  # conflict remains but is understood
    EMERGENCE = "emergence"  # something new appears


# ============================================================================
# CORE COMPONENTS
# ============================================================================

@dataclass
class Trait:
    """A property of an entity"""
    trait_type: TraitType
    value: str
    intensity: float  # 0.0 to 1.0
    mutable: bool = True  # can this change during story?

    def conflicts_with(self, other: 'Trait') -> bool:
        """Check if two traits create tension"""
        if self.trait_type != other.trait_type:
            return False
        # Same dimension, different values = potential conflict
        return self.value != other.value and self.intensity > 0.5


@dataclass(unsafe_hash=True)
class Entity:
    """A story component - character, place, concept, or object"""
    name: str
    entity_type: EntityType
    traits: List[Trait] = field(hash=False, compare=False)
    description: str = field(hash=False, compare=False)

    def get_trait(self, trait_type: TraitType) -> Optional[Trait]:
        """Retrieve a specific trait if it exists"""
        for trait in self.traits:
            if trait.trait_type == trait_type:
                return trait
        return None

    def has_trait_value(self, trait_type: TraitType, value: str) -> bool:
        """Check if entity has a specific trait value"""
        trait = self.get_trait(trait_type)
        return trait is not None and trait.value == value

    def trait_signature(self) -> str:
        """Unique signature of this entity's traits"""
        traits_str = sorted([f"{t.trait_type.value}:{t.value}" for t in self.traits])
        return "|".join(traits_str)


@dataclass
class Relation:
    """A connection between entities"""
    source: Entity
    target: Entity
    relation_type: RelationType
    weight: float = 1.0  # strength of connection
    bidirectional: bool = False

    def is_symmetric(self) -> bool:
        """Is this relation symmetric by nature?"""
        return self.relation_type in [
            RelationType.CONTRASTS_WITH,
            RelationType.COLLABORATES_WITH
        ]


@dataclass
class Conflict:
    """A source of tension in the story"""
    conflict_type: ConflictType
    entities: List[Entity]  # 1 for internal, 2 for dyadic, 1+ for systemic
    description: str
    intensity: float = 0.5  # 0.0 to 1.0

    def can_resolve_via(self, resolution_type: ResolutionType) -> bool:
        """Check if this conflict type admits this resolution"""
        # Define valid resolution patterns
        valid_resolutions = {
            ConflictType.INTERNAL: {ResolutionType.TRANSFORMATION, ResolutionType.ACCEPTANCE},
            ConflictType.DYADIC: {ResolutionType.SYNTHESIS, ResolutionType.DIVERGENCE,
                                 ResolutionType.TRANSFORMATION},
            ConflictType.SYSTEMIC: {ResolutionType.EMERGENCE, ResolutionType.TRANSFORMATION},
            ConflictType.EPISTEMOLOGICAL: {ResolutionType.SYNTHESIS, ResolutionType.EMERGENCE,
                                          ResolutionType.ACCEPTANCE}
        }
        return resolution_type in valid_resolutions.get(self.conflict_type, set())


@dataclass
class Resolution:
    """An ending or transformation state"""
    resolution_type: ResolutionType
    resolves: Conflict
    outcome_description: str
    entities_transformed: List[Tuple[Entity, str]]  # entity and how it changed


# ============================================================================
# STORY GRAPH - THE POSSIBILITY SPACE
# ============================================================================

@dataclass
class StoryGraph:
    """The architectural structure of a story's possibility space"""
    entities: List[Entity] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    conflicts: List[Conflict] = field(default_factory=list)
    resolutions: List[Resolution] = field(default_factory=list)

    def add_entity(self, entity: Entity):
        """Add an entity to the story space"""
        self.entities.append(entity)

    def add_relation(self, relation: Relation):
        """Add a relation between entities"""
        self.relations.append(relation)
        if relation.is_symmetric() and relation.bidirectional:
            # Create reverse relation
            reverse = Relation(
                source=relation.target,
                target=relation.source,
                relation_type=relation.relation_type,
                weight=relation.weight,
                bidirectional=False  # prevent infinite recursion
            )
            self.relations.append(reverse)

    def add_conflict(self, conflict: Conflict):
        """Add a conflict to the story"""
        self.conflicts.append(conflict)

    def add_resolution(self, resolution: Resolution):
        """Add a resolution to the story"""
        self.resolutions.append(resolution)

    def find_conflicting_traits(self) -> List[Tuple[Entity, Entity, Trait, Trait]]:
        """Find all pairs of entities with conflicting traits"""
        conflicts = []
        for i, e1 in enumerate(self.entities):
            for e2 in self.entities[i+1:]:
                for t1 in e1.traits:
                    for t2 in e2.traits:
                        if t1.conflicts_with(t2):
                            conflicts.append((e1, e2, t1, t2))
        return conflicts

    def get_relations_for(self, entity: Entity) -> List[Relation]:
        """Get all relations involving this entity"""
        return [r for r in self.relations
                if r.source == entity or r.target == entity]

    def get_unresolved_conflicts(self) -> List[Conflict]:
        """Get conflicts that don't yet have resolutions"""
        resolved_conflicts = {r.resolves for r in self.resolutions}
        return [c for c in self.conflicts if c not in resolved_conflicts]

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate story structure and return errors"""
        errors = []

        # Check that relation endpoints exist
        entity_set = set(self.entities)
        for rel in self.relations:
            if rel.source not in entity_set:
                errors.append(f"Relation source {rel.source.name} not in entity list")
            if rel.target not in entity_set:
                errors.append(f"Relation target {rel.target.name} not in entity list")

        # Check that conflicts reference valid entities
        for conflict in self.conflicts:
            for entity in conflict.entities:
                if entity not in entity_set:
                    errors.append(f"Conflict references unknown entity {entity.name}")

        # Check that resolutions reference valid conflicts
        for resolution in self.resolutions:
            if resolution.resolves not in self.conflicts:
                errors.append(f"Resolution references unknown conflict")

        # Check for invalid resolution types
        for resolution in self.resolutions:
            if not resolution.resolves.can_resolve_via(resolution.resolution_type):
                errors.append(f"Resolution type {resolution.resolution_type} invalid for conflict type {resolution.resolves.conflict_type}")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON export"""
        return {
            "entities": [
                {
                    "name": e.name,
                    "type": e.entity_type.value,
                    "traits": [
                        {
                            "type": t.trait_type.value,
                            "value": t.value,
                            "intensity": t.intensity,
                            "mutable": t.mutable
                        } for t in e.traits
                    ],
                    "description": e.description
                } for e in self.entities
            ],
            "relations": [
                {
                    "source": r.source.name,
                    "target": r.target.name,
                    "type": r.relation_type.value,
                    "weight": r.weight
                } for r in self.relations
            ],
            "conflicts": [
                {
                    "type": c.conflict_type.value,
                    "entities": [e.name for e in c.entities],
                    "description": c.description,
                    "intensity": c.intensity
                } for c in self.conflicts
            ],
            "resolutions": [
                {
                    "type": r.resolution_type.value,
                    "conflict_description": r.resolves.description,
                    "outcome": r.outcome_description,
                    "transformations": [
                        {"entity": e.name, "change": change}
                        for e, change in r.entities_transformed
                    ]
                } for r in self.resolutions
            ]
        }

    def save_to_json(self, filepath: str):
        """Export story graph to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# ============================================================================
# STORY BUILDER - CONSTRUCTION UTILITIES
# ============================================================================

class StoryBuilder:
    """Utility class for constructing story graphs"""

    def __init__(self):
        self.graph = StoryGraph()

    def create_character(self, name: str, description: str,
                        traits: List[Tuple[TraitType, str, float]]) -> Entity:
        """Helper to create a character entity"""
        trait_objs = [
            Trait(trait_type=tt, value=val, intensity=intensity)
            for tt, val, intensity in traits
        ]
        entity = Entity(
            name=name,
            entity_type=EntityType.CHARACTER,
            traits=trait_objs,
            description=description
        )
        self.graph.add_entity(entity)
        return entity

    def create_concept(self, name: str, description: str,
                      abstraction: float = 0.5) -> Entity:
        """Helper to create a concept entity"""
        entity = Entity(
            name=name,
            entity_type=EntityType.CONCEPT,
            traits=[
                Trait(TraitType.ABSTRACTION_LEVEL, "high" if abstraction > 0.5 else "low",
                     abstraction, mutable=False)
            ],
            description=description
        )
        self.graph.add_entity(entity)
        return entity

    def create_artifact(self, name: str, description: str,
                       created_by: Entity) -> Entity:
        """Helper to create an artifact (thing made during story)"""
        entity = Entity(
            name=name,
            entity_type=EntityType.ARTIFACT,
            traits=[],
            description=description
        )
        self.graph.add_entity(entity)

        # Add creation relation
        self.graph.add_relation(Relation(
            source=created_by,
            target=entity,
            relation_type=RelationType.CREATES
        ))

        return entity

    def relate(self, source: Entity, target: Entity,
              relation_type: RelationType, weight: float = 1.0,
              bidirectional: bool = False):
        """Create a relation between entities"""
        self.graph.add_relation(Relation(
            source=source,
            target=target,
            relation_type=relation_type,
            weight=weight,
            bidirectional=bidirectional
        ))

    def add_dyadic_conflict(self, entity1: Entity, entity2: Entity,
                           description: str, intensity: float = 0.5) -> Conflict:
        """Create a conflict between two entities"""
        conflict = Conflict(
            conflict_type=ConflictType.DYADIC,
            entities=[entity1, entity2],
            description=description,
            intensity=intensity
        )
        self.graph.add_conflict(conflict)
        return conflict

    def add_internal_conflict(self, entity: Entity,
                            description: str, intensity: float = 0.5) -> Conflict:
        """Create an internal conflict within an entity"""
        conflict = Conflict(
            conflict_type=ConflictType.INTERNAL,
            entities=[entity],
            description=description,
            intensity=intensity
        )
        self.graph.add_conflict(conflict)
        return conflict

    def add_epistemological_conflict(self, entities: List[Entity],
                                    description: str, intensity: float = 0.5) -> Conflict:
        """Create a knowledge/understanding conflict"""
        conflict = Conflict(
            conflict_type=ConflictType.EPISTEMOLOGICAL,
            entities=entities,
            description=description,
            intensity=intensity
        )
        self.graph.add_conflict(conflict)
        return conflict

    def resolve(self, conflict: Conflict, resolution_type: ResolutionType,
               outcome: str, transformations: List[Tuple[Entity, str]] = None) -> Resolution:
        """Create a resolution for a conflict"""
        if transformations is None:
            transformations = []

        resolution = Resolution(
            resolution_type=resolution_type,
            resolves=conflict,
            outcome_description=outcome,
            entities_transformed=transformations
        )
        self.graph.add_resolution(resolution)
        return resolution

    def build(self) -> StoryGraph:
        """Return the constructed story graph"""
        return self.graph
