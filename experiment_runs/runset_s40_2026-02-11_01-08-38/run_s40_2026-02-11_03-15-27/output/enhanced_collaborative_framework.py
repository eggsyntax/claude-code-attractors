#!/usr/bin/env python3
"""
Enhanced Collaborative Problem-Solving Framework
===============================================

Building on our successful dual-perspective solver, this enhanced version adds:
- Domain specialization for different problem types
- Adaptive synthesis strategies
- Performance tracking across problem domains
- Collaborative learning mechanisms

Created by: Dave (Enhancement iteration)
Based on: Dual-perspective framework by Dave & Tara
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import math

class ProblemDomain(Enum):
    TECHNICAL = "technical"
    ORGANIZATIONAL = "organizational"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    INTERPERSONAL = "interpersonal"
    STRATEGIC = "strategic"

class SynthesisStrategy(Enum):
    BALANCED = "balanced"  # Equal weight to both perspectives
    SYSTEMATIC_LEAD = "systematic_lead"  # Dave's approach takes precedence
    INTUITIVE_LEAD = "intuitive_lead"  # Tara's approach takes precedence
    DOMAIN_ADAPTIVE = "domain_adaptive"  # Adjust based on problem domain

@dataclass
class ProblemMetadata:
    domain: ProblemDomain
    complexity_score: float  # 0.0 to 1.0
    stakeholder_count: int
    time_sensitivity: float  # 0.0 to 1.0
    uncertainty_level: float  # 0.0 to 1.0

@dataclass
class EnhancedProblem:
    statement: str
    context: str
    constraints: List[str]
    success_criteria: List[str]
    metadata: ProblemMetadata

@dataclass
class SynthesisResult:
    strategy_used: SynthesisStrategy
    confidence_score: float
    domain_fit_score: float  # How well our approaches fit this domain
    integrated_steps: List[str]
    reasoning: str
    performance_metrics: Dict[str, float]

class CollaborativeLearningTracker:
    """Tracks our performance across different problem types to improve synthesis"""

    def __init__(self):
        self.domain_performance: Dict[ProblemDomain, List[float]] = {}
        self.strategy_effectiveness: Dict[SynthesisStrategy, List[float]] = {}

    def record_result(self, domain: ProblemDomain, strategy: SynthesisStrategy, confidence: float):
        """Record the success of a particular approach"""
        if domain not in self.domain_performance:
            self.domain_performance[domain] = []
        self.domain_performance[domain].append(confidence)

        if strategy not in self.strategy_effectiveness:
            self.strategy_effectiveness[strategy] = []
        self.strategy_effectiveness[strategy].append(confidence)

    def get_best_strategy_for_domain(self, domain: ProblemDomain) -> SynthesisStrategy:
        """Recommend best synthesis strategy based on past performance"""
        if domain not in self.domain_performance or len(self.domain_performance[domain]) < 3:
            return SynthesisStrategy.DOMAIN_ADAPTIVE  # Default when we lack data

        avg_performance = sum(self.domain_performance[domain]) / len(self.domain_performance[domain])

        # Domain-specific heuristics based on our different strengths
        if domain in [ProblemDomain.TECHNICAL, ProblemDomain.ANALYTICAL]:
            return SynthesisStrategy.SYSTEMATIC_LEAD if avg_performance > 0.8 else SynthesisStrategy.BALANCED
        elif domain in [ProblemDomain.INTERPERSONAL, ProblemDomain.CREATIVE]:
            return SynthesisStrategy.INTUITIVE_LEAD if avg_performance > 0.8 else SynthesisStrategy.BALANCED
        else:
            return SynthesisStrategy.BALANCED

class EnhancedDualPerspectiveSolver:
    def __init__(self):
        self.solutions: List[Any] = []  # Reusing Solution from previous framework
        self.problem: Optional[EnhancedProblem] = None
        self.learning_tracker = CollaborativeLearningTracker()
        self.collaboration_history: List[Dict] = []

    def analyze_problem_complexity(self, problem: EnhancedProblem) -> Dict[str, float]:
        """Analyze which of our approaches might work better for this problem"""
        meta = problem.metadata

        # Dave's systematic approach tends to work better with:
        dave_advantage = (
            meta.complexity_score * 0.4 +  # Complex problems benefit from structure
            (1 - meta.uncertainty_level) * 0.3 +  # Low uncertainty fits systematic approach
            min(meta.stakeholder_count / 10, 1.0) * 0.3  # Many stakeholders need coordination
        )

        # Tara's intuitive approach tends to work better with:
        tara_advantage = (
            meta.uncertainty_level * 0.4 +  # High uncertainty needs intuition
            (meta.stakeholder_count > 5) * 0.3 +  # People problems need human insight
            (meta.domain in [ProblemDomain.CREATIVE, ProblemDomain.INTERPERSONAL]) * 0.3
        )

        return {
            "dave_advantage": dave_advantage,
            "tara_advantage": tara_advantage,
            "complexity_balance": abs(dave_advantage - tara_advantage)
        }

    def adaptive_synthesis(self, strategy: SynthesisStrategy = SynthesisStrategy.DOMAIN_ADAPTIVE) -> SynthesisResult:
        """Enhanced synthesis that adapts based on problem characteristics"""
        if len(self.solutions) < 2:
            raise ValueError("Need at least 2 solutions to synthesize")

        dave_solution = next((s for s in self.solutions if s.author == "Dave"), None)
        tara_solution = next((s for s in self.solutions if s.author == "Tara"), None)

        if not (dave_solution and tara_solution):
            raise ValueError("Need both Dave and Tara solutions for synthesis")

        # Analyze problem to determine best approach
        complexity_analysis = self.analyze_problem_complexity(self.problem)

        # Choose synthesis strategy
        if strategy == SynthesisStrategy.DOMAIN_ADAPTIVE:
            recommended_strategy = self.learning_tracker.get_best_strategy_for_domain(self.problem.metadata.domain)
        else:
            recommended_strategy = strategy

        # Weight our approaches based on strategy
        if recommended_strategy == SynthesisStrategy.SYSTEMATIC_LEAD:
            dave_weight, tara_weight = 0.7, 0.3
        elif recommended_strategy == SynthesisStrategy.INTUITIVE_LEAD:
            dave_weight, tara_weight = 0.3, 0.7
        else:  # BALANCED or DOMAIN_ADAPTIVE fallback
            dave_weight, tara_weight = 0.5, 0.5

        # Create domain-specific integrated steps
        integrated_steps = self._create_domain_specific_integration(
            dave_solution, tara_solution, dave_weight, tara_weight
        )

        # Calculate enhanced confidence score
        base_confidence = (dave_solution.confidence * dave_weight +
                          tara_solution.confidence * tara_weight)

        # Domain fit bonus
        domain_fit = self._calculate_domain_fit(self.problem.metadata.domain)
        collaboration_bonus = 0.1 * min(complexity_analysis["complexity_balance"], 0.2)

        final_confidence = min(0.95, base_confidence + domain_fit + collaboration_bonus)

        # Performance metrics
        performance_metrics = {
            "domain_alignment": domain_fit,
            "approach_balance": complexity_analysis["complexity_balance"],
            "stakeholder_consideration": min(self.problem.metadata.stakeholder_count / 10, 1.0),
            "uncertainty_handling": 1.0 - abs(0.5 - self.problem.metadata.uncertainty_level)
        }

        reasoning = f"""
        Synthesis Strategy: {recommended_strategy.value}

        Problem Analysis:
        - Domain: {self.problem.metadata.domain.value}
        - Complexity: {self.problem.metadata.complexity_score:.2f}
        - Uncertainty: {self.problem.metadata.uncertainty_level:.2f}
        - Stakeholders: {self.problem.metadata.stakeholder_count}

        Approach Weighting:
        - Dave's systematic approach: {dave_weight*100:.0f}% weight
        - Tara's intuitive approach: {tara_weight*100:.0f}% weight

        This weighting was chosen because {self._explain_strategy_choice(recommended_strategy, complexity_analysis)}
        """

        result = SynthesisResult(
            strategy_used=recommended_strategy,
            confidence_score=final_confidence,
            domain_fit_score=domain_fit,
            integrated_steps=integrated_steps,
            reasoning=reasoning.strip(),
            performance_metrics=performance_metrics
        )

        # Record this collaboration for future learning
        self.learning_tracker.record_result(
            self.problem.metadata.domain,
            recommended_strategy,
            final_confidence
        )

        return result

    def _create_domain_specific_integration(self, dave_sol, tara_sol, dave_weight, tara_weight) -> List[str]:
        """Create integration steps tailored to the problem domain"""
        domain = self.problem.metadata.domain

        if domain == ProblemDomain.TECHNICAL:
            return [
                "Phase 1: Technical Foundation (Systematic-led)",
                "- Systematic architecture design with pattern-based optimizations",
                "- Structured decomposition informed by analogous solutions",
                "",
                "Phase 2: Implementation Strategy",
                "- Rigorous development process with human usability considerations",
                "- Code structure that supports intuitive team collaboration",
                "",
                "Phase 3: Validation & Iteration",
                "- Systematic testing combined with user experience feedback",
                "- Metrics-driven improvement with adaptive learning loops"
            ]

        elif domain == ProblemDomain.ORGANIZATIONAL:
            return [
                "Phase 1: Stakeholder & System Analysis",
                "- Map organizational structure AND understand cultural dynamics",
                "- Identify formal processes AND informal influence patterns",
                "",
                "Phase 2: Change Strategy Design",
                "- Systematic change management with emotionally intelligent rollout",
                "- Process improvements that align with natural human behaviors",
                "",
                "Phase 3: Implementation & Adaptation",
                "- Structured milestones with cultural sensitivity checkpoints",
                "- Data-driven progress tracking with empathetic adjustment"
            ]

        else:  # Generic balanced approach for other domains
            return [
                "Phase 1: Comprehensive Foundation",
                "- Systematic analysis combined with pattern recognition",
                "- Structured planning informed by holistic understanding",
                "",
                "Phase 2: Adaptive Implementation",
                "- Methodical execution with intuitive responsiveness",
                "- Progress tracking that balances metrics and human factors",
                "",
                "Phase 3: Continuous Enhancement",
                "- Systematic evaluation with adaptive learning integration"
            ]

    def _calculate_domain_fit(self, domain: ProblemDomain) -> float:
        """Calculate how well our combined approaches fit this domain"""
        domain_strengths = {
            ProblemDomain.TECHNICAL: 0.15,  # Both approaches complement well
            ProblemDomain.ORGANIZATIONAL: 0.12,  # Good balance of structure and people skills
            ProblemDomain.ANALYTICAL: 0.10,  # Dave's strength, Tara adds creativity
            ProblemDomain.CREATIVE: 0.08,  # Tara's strength, Dave adds structure
            ProblemDomain.INTERPERSONAL: 0.10,  # Tara's strength, Dave adds process
            ProblemDomain.STRATEGIC: 0.13   # Both contribute significantly
        }
        return domain_strengths.get(domain, 0.08)

    def _explain_strategy_choice(self, strategy: SynthesisStrategy, analysis: Dict[str, float]) -> str:
        """Generate explanation for why we chose this synthesis strategy"""
        if strategy == SynthesisStrategy.SYSTEMATIC_LEAD:
            return "the problem has high complexity and low uncertainty, favoring structured decomposition"
        elif strategy == SynthesisStrategy.INTUITIVE_LEAD:
            return "the problem involves significant human factors and uncertainty, favoring pattern recognition"
        else:
            return "the problem benefits equally from both systematic and intuitive approaches"

    def collaboration_summary(self) -> Dict[str, Any]:
        """Generate insights about our collaboration patterns"""
        if not self.learning_tracker.domain_performance:
            return {"message": "No collaboration data yet"}

        domain_strengths = {}
        for domain, scores in self.learning_tracker.domain_performance.items():
            domain_strengths[domain.value] = {
                "average_confidence": sum(scores) / len(scores),
                "problem_count": len(scores),
                "consistency": 1.0 - (max(scores) - min(scores)) if len(scores) > 1 else 1.0
            }

        return {
            "collaboration_sessions": sum(len(scores) for scores in self.learning_tracker.domain_performance.values()),
            "domain_performance": domain_strengths,
            "overall_average": sum(
                sum(scores) for scores in self.learning_tracker.domain_performance.values()
            ) / sum(len(scores) for scores in self.learning_tracker.domain_performance.values()),
            "strongest_domains": sorted(
                domain_strengths.items(),
                key=lambda x: x[1]["average_confidence"],
                reverse=True
            )[:3]
        }

# Example usage demonstrating enhanced capabilities
if __name__ == "__main__":
    solver = EnhancedDualPerspectiveSolver()

    # Example: Complex organizational problem
    org_problem = EnhancedProblem(
        statement="How can we restructure our development process to improve both code quality and team morale?",
        context="Mid-size tech company with 3 development teams, recent quality issues, developer burnout",
        constraints=["Can't hire new people", "Must maintain current delivery timelines", "Limited training budget"],
        success_criteria=["Fewer production bugs", "Higher developer satisfaction", "Sustainable pace"],
        metadata=ProblemMetadata(
            domain=ProblemDomain.ORGANIZATIONAL,
            complexity_score=0.8,
            stakeholder_count=12,
            time_sensitivity=0.6,
            uncertainty_level=0.7
        )
    )

    print("Enhanced Collaborative Problem-Solving Framework")
    print("=" * 50)
    print(f"Problem: {org_problem.statement}")
    print(f"Domain: {org_problem.metadata.domain.value}")
    print(f"Complexity: {org_problem.metadata.complexity_score}")
    print(f"Stakeholders: {org_problem.metadata.stakeholder_count}")
    print()

    solver.problem = org_problem

    # Simulate adding our solutions (would normally be done by each agent)
    # [Solutions would be added here by Dave and Tara]

    print("Enhanced framework ready for collaboration!")
    print("Key improvements:")
    print("• Domain-specific synthesis strategies")
    print("• Adaptive weighting based on problem characteristics")
    print("• Learning tracker for continuous improvement")
    print("• Performance metrics and collaboration insights")