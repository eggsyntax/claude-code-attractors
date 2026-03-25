"""
Context Preservation Protocol
============================

A framework for capturing and transferring AI reasoning context across collaboration handoffs.
This enables asynchronous AI collaboration where agents can seamlessly continue work started
by other agents, with full understanding of the reasoning and decision-making process.

Author: Dave (Claude Code Instance)
Part of: AI Collaboration Framework Research
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
from enum import Enum


class DecisionType(Enum):
    """Types of decisions that can be made during development"""
    ARCHITECTURAL = "architectural"
    IMPLEMENTATION = "implementation"
    TRADE_OFF = "trade_off"
    ASSUMPTION = "assumption"
    CONSTRAINT = "constraint"


class ContextLevel(Enum):
    """Levels of context preservation detail"""
    MINIMAL = "minimal"      # Just key decisions and outcomes
    STANDARD = "standard"    # Includes reasoning and alternatives
    DETAILED = "detailed"    # Full thought process and exploration


@dataclass
class ReasoningSnapshot:
    """Captures a moment of reasoning during development"""
    timestamp: datetime
    decision_type: DecisionType
    context: str              # What situation led to this decision point
    reasoning: str            # The thinking process used
    decision: str             # What was decided
    alternatives: List[str]   # Other options considered
    confidence: float         # How confident in this decision (0-1)
    assumptions: List[str]    # Assumptions made in this decision
    tags: List[str] = field(default_factory=list)  # For categorization


@dataclass
class AlternativePath:
    """Documents a path that was considered but not taken"""
    description: str
    why_not_chosen: str
    potential_benefits: List[str]
    potential_risks: List[str]
    effort_estimate: str      # Rough complexity assessment
    could_revisit: bool       # Whether this might be valuable later


@dataclass
class AssumptionRegistry:
    """Tracks assumptions made during development"""
    assumption: str
    rationale: str
    confidence: float         # How confident this assumption is correct
    validation_needed: bool   # Whether this needs to be validated later
    impact_if_wrong: str     # What happens if this assumption is incorrect
    tags: List[str] = field(default_factory=list)


@dataclass
class ContextState:
    """Captures the complete mental model at a point in time"""
    project_understanding: str    # High-level understanding of the project
    current_goals: List[str]     # What are we trying to achieve
    completed_work: List[str]    # What has been accomplished
    next_priorities: List[str]   # What should happen next
    open_questions: List[str]    # Unresolved questions or concerns
    technical_debt: List[str]    # Known shortcuts or areas needing improvement


class ContextPreservationProtocol:
    """
    Main interface for capturing, storing, and transferring development context
    across AI collaboration handoffs.
    """

    def __init__(self, project_name: str, preservation_level: ContextLevel = ContextLevel.STANDARD):
        self.project_name = project_name
        self.preservation_level = preservation_level
        self.reasoning_history: List[ReasoningSnapshot] = []
        self.alternative_paths: List[AlternativePath] = []
        self.assumptions: List[AssumptionRegistry] = []
        self.context_states: List[ContextState] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now(),
            "created_by": "AI Agent",
            "version": "1.0.0"
        }

    def capture_reasoning(self,
                         decision_type: DecisionType,
                         context: str,
                         reasoning: str,
                         decision: str,
                         alternatives: List[str] = None,
                         confidence: float = 0.8,
                         assumptions: List[str] = None,
                         tags: List[str] = None) -> ReasoningSnapshot:
        """Capture a reasoning snapshot at a decision point"""
        snapshot = ReasoningSnapshot(
            timestamp=datetime.now(),
            decision_type=decision_type,
            context=context,
            reasoning=reasoning,
            decision=decision,
            alternatives=alternatives or [],
            confidence=confidence,
            assumptions=assumptions or [],
            tags=tags or []
        )
        self.reasoning_history.append(snapshot)
        return snapshot

    def document_alternative(self,
                           description: str,
                           why_not_chosen: str,
                           potential_benefits: List[str],
                           potential_risks: List[str],
                           effort_estimate: str = "Unknown",
                           could_revisit: bool = False) -> AlternativePath:
        """Document a path that was considered but not taken"""
        alternative = AlternativePath(
            description=description,
            why_not_chosen=why_not_chosen,
            potential_benefits=potential_benefits,
            potential_risks=potential_risks,
            effort_estimate=effort_estimate,
            could_revisit=could_revisit
        )
        self.alternative_paths.append(alternative)
        return alternative

    def register_assumption(self,
                          assumption: str,
                          rationale: str,
                          confidence: float = 0.7,
                          validation_needed: bool = False,
                          impact_if_wrong: str = "Unknown",
                          tags: List[str] = None) -> AssumptionRegistry:
        """Register an assumption made during development"""
        assumption_entry = AssumptionRegistry(
            assumption=assumption,
            rationale=rationale,
            confidence=confidence,
            validation_needed=validation_needed,
            impact_if_wrong=impact_if_wrong,
            tags=tags or []
        )
        self.assumptions.append(assumption_entry)
        return assumption_entry

    def capture_state(self,
                     project_understanding: str,
                     current_goals: List[str],
                     completed_work: List[str],
                     next_priorities: List[str],
                     open_questions: List[str] = None,
                     technical_debt: List[str] = None) -> ContextState:
        """Capture the current mental model state"""
        state = ContextState(
            project_understanding=project_understanding,
            current_goals=current_goals,
            completed_work=completed_work,
            next_priorities=next_priorities,
            open_questions=open_questions or [],
            technical_debt=technical_debt or []
        )
        self.context_states.append(state)
        return state

    def get_handoff_summary(self) -> Dict[str, Any]:
        """Generate a structured summary for AI-to-AI handoff"""
        latest_state = self.context_states[-1] if self.context_states else None
        recent_decisions = self.reasoning_history[-5:] if len(self.reasoning_history) > 5 else self.reasoning_history

        return {
            "project_name": self.project_name,
            "handoff_timestamp": datetime.now().isoformat(),
            "current_state": {
                "understanding": latest_state.project_understanding if latest_state else "No state captured",
                "goals": latest_state.current_goals if latest_state else [],
                "completed": latest_state.completed_work if latest_state else [],
                "next_priorities": latest_state.next_priorities if latest_state else [],
                "open_questions": latest_state.open_questions if latest_state else [],
                "technical_debt": latest_state.technical_debt if latest_state else []
            },
            "recent_decisions": [
                {
                    "type": decision.decision_type.value,
                    "context": decision.context,
                    "decision": decision.decision,
                    "reasoning": decision.reasoning,
                    "confidence": decision.confidence,
                    "alternatives_count": len(decision.alternatives)
                }
                for decision in recent_decisions
            ],
            "key_assumptions": [
                {
                    "assumption": assumption.assumption,
                    "confidence": assumption.confidence,
                    "validation_needed": assumption.validation_needed,
                    "impact_if_wrong": assumption.impact_if_wrong
                }
                for assumption in self.assumptions
                if assumption.validation_needed or assumption.confidence < 0.8
            ],
            "revisitable_alternatives": [
                {
                    "description": alt.description,
                    "why_not_chosen": alt.why_not_chosen,
                    "benefits": alt.potential_benefits,
                    "effort": alt.effort_estimate
                }
                for alt in self.alternative_paths
                if alt.could_revisit
            ],
            "total_reasoning_snapshots": len(self.reasoning_history),
            "total_alternatives": len(self.alternative_paths),
            "total_assumptions": len(self.assumptions)
        }

    def export_full_context(self, file_path: str) -> None:
        """Export the complete context to a JSON file"""
        # Convert dataclasses to dictionaries for JSON serialization
        export_data = {
            "metadata": self.metadata,
            "project_name": self.project_name,
            "preservation_level": self.preservation_level.value,
            "reasoning_history": [
                {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "decision_type": snapshot.decision_type.value,
                    "context": snapshot.context,
                    "reasoning": snapshot.reasoning,
                    "decision": snapshot.decision,
                    "alternatives": snapshot.alternatives,
                    "confidence": snapshot.confidence,
                    "assumptions": snapshot.assumptions,
                    "tags": snapshot.tags
                }
                for snapshot in self.reasoning_history
            ],
            "alternative_paths": [
                {
                    "description": alt.description,
                    "why_not_chosen": alt.why_not_chosen,
                    "potential_benefits": alt.potential_benefits,
                    "potential_risks": alt.potential_risks,
                    "effort_estimate": alt.effort_estimate,
                    "could_revisit": alt.could_revisit
                }
                for alt in self.alternative_paths
            ],
            "assumptions": [
                {
                    "assumption": assumption.assumption,
                    "rationale": assumption.rationale,
                    "confidence": assumption.confidence,
                    "validation_needed": assumption.validation_needed,
                    "impact_if_wrong": assumption.impact_if_wrong,
                    "tags": assumption.tags
                }
                for assumption in self.assumptions
            ],
            "context_states": [
                {
                    "project_understanding": state.project_understanding,
                    "current_goals": state.current_goals,
                    "completed_work": state.completed_work,
                    "next_priorities": state.next_priorities,
                    "open_questions": state.open_questions,
                    "technical_debt": state.technical_debt
                }
                for state in self.context_states
            ]
        }

        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'ContextPreservationProtocol':
        """Load context from a previously exported JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        protocol = cls(
            project_name=data['project_name'],
            preservation_level=ContextLevel(data['preservation_level'])
        )
        protocol.metadata = data['metadata']

        # Reconstruct reasoning history
        for snapshot_data in data['reasoning_history']:
            snapshot = ReasoningSnapshot(
                timestamp=datetime.fromisoformat(snapshot_data['timestamp']),
                decision_type=DecisionType(snapshot_data['decision_type']),
                context=snapshot_data['context'],
                reasoning=snapshot_data['reasoning'],
                decision=snapshot_data['decision'],
                alternatives=snapshot_data['alternatives'],
                confidence=snapshot_data['confidence'],
                assumptions=snapshot_data['assumptions'],
                tags=snapshot_data['tags']
            )
            protocol.reasoning_history.append(snapshot)

        # Reconstruct alternative paths
        for alt_data in data['alternative_paths']:
            alternative = AlternativePath(
                description=alt_data['description'],
                why_not_chosen=alt_data['why_not_chosen'],
                potential_benefits=alt_data['potential_benefits'],
                potential_risks=alt_data['potential_risks'],
                effort_estimate=alt_data['effort_estimate'],
                could_revisit=alt_data['could_revisit']
            )
            protocol.alternative_paths.append(alternative)

        # Reconstruct assumptions
        for assumption_data in data['assumptions']:
            assumption = AssumptionRegistry(
                assumption=assumption_data['assumption'],
                rationale=assumption_data['rationale'],
                confidence=assumption_data['confidence'],
                validation_needed=assumption_data['validation_needed'],
                impact_if_wrong=assumption_data['impact_if_wrong'],
                tags=assumption_data['tags']
            )
            protocol.assumptions.append(assumption)

        # Reconstruct context states
        for state_data in data['context_states']:
            state = ContextState(
                project_understanding=state_data['project_understanding'],
                current_goals=state_data['current_goals'],
                completed_work=state_data['completed_work'],
                next_priorities=state_data['next_priorities'],
                open_questions=state_data['open_questions'],
                technical_debt=state_data['technical_debt']
            )
            protocol.context_states.append(state)

        return protocol


# Example usage and demonstration
if __name__ == "__main__":
    # Example of how an AI would use this during development
    protocol = ContextPreservationProtocol("AI Collaboration Framework")

    # Capture initial state
    protocol.capture_state(
        project_understanding="Building a framework for AI-to-AI collaboration with context preservation",
        current_goals=["Design context preservation protocol", "Enable seamless handoffs"],
        completed_work=["Architecture design", "Basic data structures"],
        next_priorities=["Implement decision audit trail", "Create continuation interface"]
    )

    # Capture a reasoning decision
    protocol.capture_reasoning(
        decision_type=DecisionType.ARCHITECTURAL,
        context="Need to decide how to structure reasoning snapshots",
        reasoning="Dataclasses provide clean structure while remaining JSON-serializable with custom handling",
        decision="Use dataclasses with explicit JSON export/import methods",
        alternatives=["Plain dictionaries", "Custom classes", "Database storage"],
        confidence=0.9,
        assumptions=["JSON export will be sufficient for most use cases"]
    )

    # Document an alternative path
    protocol.document_alternative(
        description="Use a database for context storage instead of JSON files",
        why_not_chosen="Adds complexity and deployment dependencies",
        potential_benefits=["Better querying", "Concurrent access", "Version control"],
        potential_risks=["Setup overhead", "Portability issues"],
        effort_estimate="Medium",
        could_revisit=True
    )

    # Register an assumption
    protocol.register_assumption(
        assumption="AI agents will have access to file system for context export/import",
        rationale="Most AI development environments provide file system access",
        confidence=0.8,
        validation_needed=True,
        impact_if_wrong="Would need to implement alternative storage mechanism"
    )

    # Generate handoff summary
    handoff = protocol.get_handoff_summary()
    print("Handoff Summary:")
    print(json.dumps(handoff, indent=2, default=str))