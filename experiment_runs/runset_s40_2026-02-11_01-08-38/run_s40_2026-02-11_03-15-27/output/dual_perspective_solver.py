#!/usr/bin/env python3
"""
Dual-Perspective Problem Solver Framework
==========================================

A collaborative problem-solving system designed for two AI agents (Dave & Tara)
to approach problems from different angles and synthesize their perspectives.

Created by: Dave (Initial framework)
To be extended by: Tara (Additional methodologies and synthesis logic)
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class PerspectiveType(Enum):
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    SYSTEMATIC = "systematic"
    INTUITIVE = "intuitive"

@dataclass
class Solution:
    approach: str
    reasoning: str
    steps: List[str]
    confidence: float
    perspective_type: PerspectiveType
    author: str

@dataclass
class Problem:
    statement: str
    context: str
    constraints: List[str]
    success_criteria: List[str]

class DualPerspectiveSolver:
    def __init__(self):
        self.solutions: List[Solution] = []
        self.problem: Problem = None

    def load_problem(self, problem: Problem):
        """Load a problem for dual-perspective analysis"""
        self.problem = problem
        self.solutions = []
        print(f"Problem loaded: {problem.statement}")

    def add_solution(self, solution: Solution):
        """Add a solution from one perspective"""
        self.solutions.append(solution)
        print(f"Solution added by {solution.author} using {solution.perspective_type.value} approach")

    def dave_analysis(self) -> Solution:
        """Dave's problem-solving approach - systematic and analytical"""
        if not self.problem:
            raise ValueError("No problem loaded")

        # Dave's methodology: Break down systematically
        steps = [
            "1. Decompose problem into core components",
            "2. Identify dependencies and relationships",
            "3. Prioritize components by impact/effort ratio",
            "4. Design step-by-step implementation plan",
            "5. Identify potential failure points and mitigations"
        ]

        reasoning = """
        My approach focuses on systematic decomposition and structured analysis.
        I break complex problems into manageable components, map their relationships,
        and create clear implementation pathways. This reduces ambiguity and
        provides measurable progress indicators.
        """

        return Solution(
            approach="Systematic Decomposition",
            reasoning=reasoning.strip(),
            steps=steps,
            confidence=0.85,
            perspective_type=PerspectiveType.SYSTEMATIC,
            author="Dave"
        )

    def tara_analysis(self) -> Solution:
        """Tara's problem-solving approach - intuitive pattern recognition with human-centered focus"""
        if not self.problem:
            raise ValueError("No problem loaded")

        # Tara's methodology: Pattern recognition and human-centered design
        steps = [
            "1. Identify underlying patterns and root causes beyond surface symptoms",
            "2. Map stakeholder emotions, motivations, and unspoken needs",
            "3. Look for analogous successful solutions from different domains",
            "4. Design interventions that feel natural and sustainable to users",
            "5. Build in feedback loops and adaptation mechanisms"
        ]

        reasoning = """
        My approach emphasizes pattern recognition and human psychology.
        I look for the deeper currents beneath problems - what emotional or
        psychological factors are at play? What patterns from other domains
        might apply? I focus on solutions that work WITH human nature rather
        than against it, creating sustainable change through understanding
        root motivations and building adaptive systems.
        """

        return Solution(
            approach="Intuitive Pattern Recognition",
            reasoning=reasoning.strip(),
            steps=steps,
            confidence=0.80,
            perspective_type=PerspectiveType.INTUITIVE,
            author="Tara"
        )

    def synthesize_perspectives(self) -> Dict[str, Any]:
        """Combine multiple perspectives into a unified approach"""
        if len(self.solutions) < 2:
            return {"error": "Need at least 2 solutions to synthesize"}

        # Collaborative synthesis logic combining our approaches
        dave_solution = next((s for s in self.solutions if s.author == "Dave"), None)
        tara_solution = next((s for s in self.solutions if s.author == "Tara"), None)

        if not (dave_solution and tara_solution):
            return {"error": "Need both Dave and Tara solutions for synthesis"}

        # Interweave systematic structure with intuitive insights
        integrated_steps = [
            "Phase 1: Foundation (Dave's systematic + Tara's root cause analysis)",
            "- Decompose problem systematically AND identify underlying patterns",
            "- Map technical dependencies AND stakeholder emotional landscape",
            "",
            "Phase 2: Design (Balanced approach)",
            "- Prioritize by impact/effort ratio AND human adoption likelihood",
            "- Structure implementation plan AND ensure it feels natural to users",
            "",
            "Phase 3: Implementation (Adaptive execution)",
            "- Execute systematic plan AND build in human feedback loops",
            "- Monitor failure points AND adapt based on user behavior patterns"
        ]

        # Calculate combined confidence (weighted average with bonus for diversity)
        base_confidence = (dave_solution.confidence + tara_solution.confidence) / 2
        diversity_bonus = 0.1  # Bonus for having multiple perspectives
        combined_confidence = min(0.95, base_confidence + diversity_bonus)

        synthesis = {
            "combined_approach": "Systematic-Intuitive Hybrid",
            "description": "Combines Dave's structured decomposition with Tara's pattern recognition to create solutions that are both technically sound and psychologically sustainable",
            "integrated_steps": integrated_steps,
            "confidence_score": combined_confidence,
            "perspectives_used": [sol.perspective_type.value for sol in self.solutions],
            "strength_amplification": {
                "systematic_rigor": "Dave's approach ensures nothing is overlooked",
                "human_factors": "Tara's approach ensures solutions actually get adopted",
                "combined_power": "Structure + intuition = robust and sustainable solutions"
            }
        }

        return synthesis

    def export_analysis(self, filename: str):
        """Export the complete analysis to a file"""
        analysis = {
            "problem": {
                "statement": self.problem.statement,
                "context": self.problem.context,
                "constraints": self.problem.constraints,
                "success_criteria": self.problem.success_criteria
            },
            "solutions": [
                {
                    "approach": sol.approach,
                    "reasoning": sol.reasoning,
                    "steps": sol.steps,
                    "confidence": sol.confidence,
                    "perspective": sol.perspective_type.value,
                    "author": sol.author
                }
                for sol in self.solutions
            ],
            "synthesis": self.synthesize_perspectives()
        }

        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"Analysis exported to {filename}")

# Example usage and testing framework
if __name__ == "__main__":
    solver = DualPerspectiveSolver()

    # Example problem for testing
    test_problem = Problem(
        statement="How can we improve team productivity in a remote work environment?",
        context="A software development team of 8 people working fully remote for 2 years",
        constraints=["Limited budget for new tools", "Different time zones (6-hour spread)", "Varying experience levels"],
        success_criteria=["Measurable increase in velocity", "Higher team satisfaction", "Better code quality"]
    )

    solver.load_problem(test_problem)

    # Dave adds his solution
    dave_solution = solver.dave_analysis()
    solver.add_solution(dave_solution)

    print("\nDave's systematic approach:")
    for i, step in enumerate(dave_solution.steps, 1):
        print(f"  {step}")

    # Tara adds her solution
    tara_solution = solver.tara_analysis()
    solver.add_solution(tara_solution)

    print("\nTara's intuitive approach:")
    for i, step in enumerate(tara_solution.steps, 1):
        print(f"  {step}")

    # Now synthesize our perspectives
    print("\n" + "="*60)
    print("SYNTHESIZED DUAL PERSPECTIVE SOLUTION")
    print("="*60)

    synthesis = solver.synthesize_perspectives()
    print(f"\nApproach: {synthesis['combined_approach']}")
    print(f"Description: {synthesis['description']}")
    print(f"Combined Confidence: {synthesis['confidence_score']:.2f}")

    print("\nIntegrated Steps:")
    for step in synthesis['integrated_steps']:
        if step.strip():  # Skip empty lines
            print(f"  {step}")

    print(f"\nStrength Amplification:")
    for key, value in synthesis['strength_amplification'].items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")

    # Export our analysis
    solver.export_analysis("/tmp/cc-exp/run_s40_2026-02-11_03-15-27/output/team_productivity_analysis.json")
    print(f"\nCollaboration successful! Both perspectives integrated and exported.")