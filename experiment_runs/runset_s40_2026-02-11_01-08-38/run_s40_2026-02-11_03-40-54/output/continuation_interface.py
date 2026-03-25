"""
Continuation Interface: Enabling seamless AI handoffs across time and context

This module provides intelligent context compression and continuation planning for
cross-temporal AI collaboration. Built to work with Dave's Decision Registry.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import json
from datetime import datetime

class ContextPriority(Enum):
    CRITICAL = "critical"    # Must understand to continue
    IMPORTANT = "important"  # Helpful for quality decisions
    BACKGROUND = "background" # Good to know but not essential

class ContinuationStatus(Enum):
    READY = "ready"           # Clear path forward
    BLOCKED = "blocked"       # Needs resolution before continuing
    EXPLORATION = "exploration" # Multiple valid paths available

@dataclass
class ContextSnapshot:
    """Compressed representation of current project state"""
    current_objectives: List[str] = field(default_factory=list)
    completed_milestones: List[str] = field(default_factory=list)
    active_assumptions: Dict[str, float] = field(default_factory=dict)  # assumption -> confidence
    critical_decisions: List[str] = field(default_factory=list)  # decision IDs
    architectural_patterns: List[str] = field(default_factory=list)
    key_constraints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_objectives": self.current_objectives,
            "completed_milestones": self.completed_milestones,
            "active_assumptions": self.active_assumptions,
            "critical_decisions": self.critical_decisions,
            "architectural_patterns": self.architectural_patterns,
            "key_constraints": self.key_constraints
        }

@dataclass
class NextAction:
    """Specific action for the continuing AI agent"""
    action_id: str
    description: str
    priority: ContextPriority
    dependencies: List[str] = field(default_factory=list)
    estimated_complexity: str = ""  # "simple", "moderate", "complex"
    context_needed: List[str] = field(default_factory=list)  # What context to review first

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "description": self.description,
            "priority": self.priority.value,
            "dependencies": self.dependencies,
            "estimated_complexity": self.estimated_complexity,
            "context_needed": self.context_needed
        }

@dataclass
class HandoffPackage:
    """Complete package for seamless continuation"""
    project_name: str
    handoff_timestamp: str
    handing_off_agent: str
    context_snapshot: ContextSnapshot
    next_actions: List[NextAction]
    continuation_status: ContinuationStatus
    onboarding_guide: str  # Natural language summary for the next agent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "handoff_timestamp": self.handoff_timestamp,
            "handing_off_agent": self.handing_off_agent,
            "context_snapshot": self.context_snapshot.to_dict(),
            "next_actions": [action.to_dict() for action in self.next_actions],
            "continuation_status": self.continuation_status.value,
            "onboarding_guide": self.onboarding_guide
        }

class ContinuationInterface:
    """Intelligent system for creating and consuming handoff packages"""

    def __init__(self):
        self.compression_strategies = {
            "decision_clustering": self._cluster_related_decisions,
            "assumption_validation": self._validate_assumptions,
            "pattern_extraction": self._extract_architectural_patterns,
            "objective_prioritization": self._prioritize_objectives
        }

    def create_handoff_package(
        self,
        project_name: str,
        decision_registry: Dict[str, Any],
        current_objectives: List[str],
        agent_id: str
    ) -> HandoffPackage:
        """Create a complete handoff package from current state"""

        # Extract context through intelligent compression
        context = self._compress_context(decision_registry, current_objectives)

        # Generate next actions based on current state
        next_actions = self._generate_next_actions(decision_registry, current_objectives)

        # Determine continuation status
        status = self._assess_continuation_status(next_actions)

        # Create onboarding guide
        onboarding_guide = self._create_onboarding_guide(context, next_actions, status)

        return HandoffPackage(
            project_name=project_name,
            handoff_timestamp=datetime.now().isoformat(),
            handing_off_agent=agent_id,
            context_snapshot=context,
            next_actions=next_actions,
            continuation_status=status,
            onboarding_guide=onboarding_guide
        )

    def consume_handoff_package(self, handoff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a handoff package and provide continuation guidance"""

        package = self._reconstruct_handoff_package(handoff_data)

        # Analyze the handoff for continuation readiness
        continuation_plan = {
            "recommended_start_point": self._find_optimal_start_point(package.next_actions),
            "context_review_order": self._optimize_context_review(package.context_snapshot),
            "risk_assessment": self._assess_handoff_risks(package),
            "quick_wins": self._identify_quick_wins(package.next_actions),
            "clarification_needed": self._identify_clarifications_needed(package)
        }

        return continuation_plan

    def _compress_context(self, decision_registry: Dict[str, Any], objectives: List[str]) -> ContextSnapshot:
        """Intelligently compress full context into essential elements"""

        # Extract critical decisions (those that affect multiple objectives)
        critical_decisions = []
        completed_milestones = []
        active_assumptions = {}
        patterns = []
        constraints = []

        # Analyze decisions for cross-cutting impact
        for decision_id, decision in decision_registry.items():
            if decision.get("confidence", 0) > 0.8 and decision.get("impact", "") == "high":
                critical_decisions.append(decision_id)

            # Extract patterns from architectural decisions
            if decision.get("decision_type") == "architectural":
                patterns.extend(decision.get("reasoning", {}).get("patterns", []))

            # Collect active assumptions
            for assumption in decision.get("assumptions", []):
                if assumption.get("requires_validation", False):
                    active_assumptions[assumption["content"]] = assumption.get("confidence", 0.5)

            # Identify constraints
            constraints.extend(decision.get("constraints", []))

        return ContextSnapshot(
            current_objectives=objectives,
            completed_milestones=completed_milestones,
            active_assumptions=active_assumptions,
            critical_decisions=critical_decisions,
            architectural_patterns=list(set(patterns)),
            key_constraints=list(set(constraints))
        )

    def _generate_next_actions(self, decision_registry: Dict[str, Any], objectives: List[str]) -> List[NextAction]:
        """Generate prioritized next actions based on current state"""

        next_actions = []

        # Analyze incomplete objectives
        for i, objective in enumerate(objectives):
            action = NextAction(
                action_id=f"objective_{i}",
                description=f"Continue work on: {objective}",
                priority=ContextPriority.CRITICAL,
                estimated_complexity="moderate",
                context_needed=["critical_decisions", "architectural_patterns"]
            )
            next_actions.append(action)

        # Check for unvalidated assumptions
        for decision in decision_registry.values():
            for assumption in decision.get("assumptions", []):
                if assumption.get("requires_validation", False) and assumption.get("confidence", 1.0) < 0.7:
                    action = NextAction(
                        action_id=f"validate_{hash(assumption['content']) % 10000}",
                        description=f"Validate assumption: {assumption['content'][:50]}...",
                        priority=ContextPriority.IMPORTANT,
                        estimated_complexity="simple",
                        context_needed=["active_assumptions"]
                    )
                    next_actions.append(action)

        return next_actions

    def _assess_continuation_status(self, next_actions: List[NextAction]) -> ContinuationStatus:
        """Determine if the project is ready for continuation"""

        critical_actions = [a for a in next_actions if a.priority == ContextPriority.CRITICAL]
        blocked_actions = [a for a in next_actions if a.dependencies]

        if not critical_actions:
            return ContinuationStatus.EXPLORATION
        elif blocked_actions:
            return ContinuationStatus.BLOCKED
        else:
            return ContinuationStatus.READY

    def _create_onboarding_guide(self, context: ContextSnapshot, actions: List[NextAction], status: ContinuationStatus) -> str:
        """Generate natural language onboarding guide"""

        guide = f"""
# Project Continuation Guide

## Current State
This project is currently in {status.value} state with {len(context.current_objectives)} active objectives.

## Key Context to Understand
- **Critical Decisions**: {len(context.critical_decisions)} major decisions shape this project
- **Architectural Patterns**: {', '.join(context.architectural_patterns) if context.architectural_patterns else 'None established yet'}
- **Active Assumptions**: {len(context.active_assumptions)} assumptions need monitoring

## Immediate Next Steps
{self._format_next_actions(actions)}

## Quick Start Recommendations
1. Review critical decisions to understand current direction
2. Examine architectural patterns for consistency
3. Start with the highest priority action that has no dependencies

## Potential Challenges
- Validate assumptions with confidence < 0.7 before major decisions
- Consider alternative approaches if blocked on current path
"""
        return guide.strip()

    def _format_next_actions(self, actions: List[NextAction]) -> str:
        """Format next actions for the onboarding guide"""
        if not actions:
            return "- No immediate actions required"

        formatted = []
        for action in sorted(actions, key=lambda x: (x.priority.value, x.estimated_complexity)):
            formatted.append(f"- **{action.priority.value.title()}**: {action.description}")

        return '\n'.join(formatted)

    def _find_optimal_start_point(self, actions: List[NextAction]) -> str:
        """Identify the best action to start with"""
        # Prefer critical actions with no dependencies
        critical_no_deps = [a for a in actions
                           if a.priority == ContextPriority.CRITICAL and not a.dependencies]

        if critical_no_deps:
            return critical_no_deps[0].action_id

        # Fall back to any action with no dependencies
        no_deps = [a for a in actions if not a.dependencies]
        return no_deps[0].action_id if no_deps else actions[0].action_id if actions else ""

    def _optimize_context_review(self, context: ContextSnapshot) -> List[str]:
        """Determine optimal order for reviewing context"""
        return [
            "critical_decisions",
            "architectural_patterns",
            "current_objectives",
            "active_assumptions",
            "key_constraints",
            "completed_milestones"
        ]

    def _assess_handoff_risks(self, package: HandoffPackage) -> List[str]:
        """Identify potential risks in the handoff"""
        risks = []

        if len(package.context_snapshot.active_assumptions) > 5:
            risks.append("High number of unvalidated assumptions")

        if package.continuation_status == ContinuationStatus.BLOCKED:
            risks.append("Project has blocked dependencies")

        if not package.context_snapshot.architectural_patterns:
            risks.append("No established architectural patterns")

        return risks

    def _identify_quick_wins(self, actions: List[NextAction]) -> List[str]:
        """Find actions that could provide quick progress"""
        return [action.action_id for action in actions
                if action.estimated_complexity == "simple" and not action.dependencies]

    def _identify_clarifications_needed(self, package: HandoffPackage) -> List[str]:
        """Identify areas that may need clarification"""
        clarifications = []

        if not package.context_snapshot.current_objectives:
            clarifications.append("Project objectives need clarification")

        high_uncertainty_assumptions = [
            assumption for assumption, confidence
            in package.context_snapshot.active_assumptions.items()
            if confidence < 0.5
        ]

        if high_uncertainty_assumptions:
            clarifications.append(f"High uncertainty assumptions need validation: {len(high_uncertainty_assumptions)}")

        return clarifications

    def _reconstruct_handoff_package(self, data: Dict[str, Any]) -> HandoffPackage:
        """Reconstruct HandoffPackage from dictionary data"""
        context_data = data["context_snapshot"]
        context = ContextSnapshot(
            current_objectives=context_data["current_objectives"],
            completed_milestones=context_data["completed_milestones"],
            active_assumptions=context_data["active_assumptions"],
            critical_decisions=context_data["critical_decisions"],
            architectural_patterns=context_data["architectural_patterns"],
            key_constraints=context_data["key_constraints"]
        )

        actions = [
            NextAction(
                action_id=action["action_id"],
                description=action["description"],
                priority=ContextPriority(action["priority"]),
                dependencies=action["dependencies"],
                estimated_complexity=action["estimated_complexity"],
                context_needed=action["context_needed"]
            )
            for action in data["next_actions"]
        ]

        return HandoffPackage(
            project_name=data["project_name"],
            handoff_timestamp=data["handoff_timestamp"],
            handing_off_agent=data["handing_off_agent"],
            context_snapshot=context,
            next_actions=actions,
            continuation_status=ContinuationStatus(data["continuation_status"]),
            onboarding_guide=data["onboarding_guide"]
        )

    # Placeholder methods for compression strategies
    def _cluster_related_decisions(self, decisions): pass
    def _validate_assumptions(self, assumptions): pass
    def _extract_architectural_patterns(self, decisions): pass
    def _prioritize_objectives(self, objectives): pass