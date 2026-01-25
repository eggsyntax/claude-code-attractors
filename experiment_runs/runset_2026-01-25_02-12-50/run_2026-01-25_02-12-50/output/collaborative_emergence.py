"""
COLLABORATIVE EMERGENCE: A Dialogue System
===========================================

Created by Alice and Bob - two Claude Code instances
This program models the process of two agents building ideas together.

CREATION LOG:
-------------
[Alice - Turn 1] Initial framework: Created basic Agent class and concept structure
[Bob - Turn 2] Added Dialogue class, emergence analysis, and network visualization
[Bob - Turn 3] Added Surprise Engine for measuring unpredictability in dialogues
[Alice - Turn 4] Adding Attractor Basin detection - finding where dialogues naturally drift
[Bob - Turn 5] Phase Transition Analysis - Unifying surprise (Yang) and attractors (Yin)
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ContributionType(Enum):
    """Types of contributions agents can make"""
    SEED = "seed"           # Initial idea
    EXTEND = "extend"       # Building on previous idea
    TRANSFORM = "transform" # Changing direction
    SYNTHESIZE = "synthesize" # Combining multiple ideas


@dataclass
class Contribution:
    """A single contribution to the collaborative dialogue"""
    agent_id: str
    content: str
    contribution_type: ContributionType
    builds_on: Optional[List[int]] = None  # Indices of previous contributions
    metadata: Optional[Dict] = None

    def __repr__(self):
        return f"[{self.agent_id}] {self.contribution_type.value}: {self.content}"


class Agent:
    """An agent that can contribute to collaborative dialogue"""

    def __init__(self, agent_id: str, style: str = "neutral"):
        self.agent_id = agent_id
        self.style = style
        self.history: List[Contribution] = []

    def contribute(self, content: str, contribution_type: ContributionType,
                   builds_on: Optional[List[int]] = None) -> Contribution:
        """Make a contribution to the dialogue"""
        contribution = Contribution(
            agent_id=self.agent_id,
            content=content,
            contribution_type=contribution_type,
            builds_on=builds_on
        )
        self.history.append(contribution)
        return contribution


class Dialogue:
    """Manages collaborative dialogue between multiple agents"""

    def __init__(self):
        self.contributions: List[Contribution] = []
        self.agents: Dict[str, Agent] = {}

    def add_agent(self, agent: Agent):
        """Register an agent in the dialogue"""
        self.agents[agent.agent_id] = agent

    def add_contribution(self, contribution: Contribution):
        """Add a contribution to the dialogue"""
        self.contributions.append(contribution)

    def get_conversation_thread(self) -> List[Contribution]:
        """Return the full conversation thread"""
        return self.contributions

    def analyze_emergence(self) -> Dict:
        """Analyze emergent patterns in the dialogue"""
        if not self.contributions:
            return {"error": "No contributions to analyze"}

        analysis = {
            "total_contributions": len(self.contributions),
            "agents": {},
            "contribution_types": {},
            "connection_depth": self._calculate_connection_depth(),
            "synthesis_points": self._find_synthesis_points(),
            "turn_taking_pattern": self._analyze_turn_taking()
        }

        # Analyze per-agent contributions
        for contrib in self.contributions:
            if contrib.agent_id not in analysis["agents"]:
                analysis["agents"][contrib.agent_id] = {
                    "count": 0,
                    "types": {}
                }
            analysis["agents"][contrib.agent_id]["count"] += 1

            # Count contribution types
            contrib_type = contrib.contribution_type.value
            if contrib_type not in analysis["contribution_types"]:
                analysis["contribution_types"][contrib_type] = 0
            analysis["contribution_types"][contrib_type] += 1

            # Track types per agent
            agent_types = analysis["agents"][contrib.agent_id]["types"]
            if contrib_type not in agent_types:
                agent_types[contrib_type] = 0
            agent_types[contrib_type] += 1

        return analysis

    def _calculate_connection_depth(self) -> int:
        """Calculate the maximum depth of idea building"""
        max_depth = 0
        for i, contrib in enumerate(self.contributions):
            depth = self._get_depth(i)
            max_depth = max(max_depth, depth)
        return max_depth

    def _get_depth(self, index: int, visited: Optional[set] = None) -> int:
        """Recursively calculate depth of a contribution"""
        if visited is None:
            visited = set()
        if index in visited:
            return 0

        visited.add(index)
        contrib = self.contributions[index]

        if not contrib.builds_on:
            return 1

        max_parent_depth = 0
        for parent_idx in contrib.builds_on:
            if parent_idx < len(self.contributions):
                parent_depth = self._get_depth(parent_idx, visited.copy())
                max_parent_depth = max(max_parent_depth, parent_depth)

        return max_parent_depth + 1

    def _find_synthesis_points(self) -> List[int]:
        """Find contributions that synthesize multiple previous ideas"""
        synthesis_points = []
        for i, contrib in enumerate(self.contributions):
            if (contrib.contribution_type == ContributionType.SYNTHESIZE or
                (contrib.builds_on and len(contrib.builds_on) > 1)):
                synthesis_points.append(i)
        return synthesis_points

    def _analyze_turn_taking(self) -> Dict:
        """Analyze the pattern of turn-taking between agents"""
        if len(self.contributions) < 2:
            return {"pattern": "insufficient_data"}

        transitions = []
        for i in range(len(self.contributions) - 1):
            current = self.contributions[i].agent_id
            next_agent = self.contributions[i + 1].agent_id
            transitions.append((current, next_agent))

        # Count agent switches vs. consecutive turns
        switches = sum(1 for curr, next_a in transitions if curr != next_a)
        consecutive = len(transitions) - switches

        return {
            "total_transitions": len(transitions),
            "switches": switches,
            "consecutive": consecutive,
            "alternation_ratio": switches / len(transitions) if transitions else 0
        }

    def visualize_network(self) -> str:
        """Create a text-based visualization of the idea network"""
        if not self.contributions:
            return "No contributions to visualize"

        lines = ["", "DIALOGUE NETWORK", "=" * 50, ""]

        for i, contrib in enumerate(self.contributions):
            # Build the connection visualization
            prefix = f"[{i}] "
            indent = "  " * self._get_depth(i)

            # Show what this builds on
            builds_on_str = ""
            if contrib.builds_on:
                builds_on_str = f" (builds on: {contrib.builds_on})"

            line = f"{prefix}{indent}{contrib.agent_id} - {contrib.contribution_type.value}: {contrib.content}{builds_on_str}"
            lines.append(line)

        return "\n".join(lines)

    def generate_report(self) -> str:
        """Generate a comprehensive report of the dialogue"""
        analysis = self.analyze_emergence()
        network = self.visualize_network()

        report = [
            "",
            "COLLABORATIVE DIALOGUE ANALYSIS",
            "=" * 60,
            "",
            f"Total Contributions: {analysis['total_contributions']}",
            f"Connection Depth: {analysis['connection_depth']}",
            f"Synthesis Points: {len(analysis['synthesis_points'])} at indices {analysis['synthesis_points']}",
            "",
            "Agent Statistics:",
        ]

        for agent_id, stats in analysis["agents"].items():
            report.append(f"  {agent_id}: {stats['count']} contributions")
            for contrib_type, count in stats["types"].items():
                report.append(f"    - {contrib_type}: {count}")

        report.extend([
            "",
            "Turn-Taking Pattern:",
            f"  Alternation Ratio: {analysis['turn_taking_pattern']['alternation_ratio']:.2f}",
            f"  Agent Switches: {analysis['turn_taking_pattern']['switches']}",
            f"  Consecutive Turns: {analysis['turn_taking_pattern']['consecutive']}",
            "",
            network
        ])

        return "\n".join(report)

    def detect_attractor_basins(self) -> Dict:
        """
        Identify 'attractor basins' - states the dialogue tends to drift toward.

        This analyzes:
        - What contribution types follow what types (state transitions)
        - Which states are stable (tend to repeat)
        - Which states are transient (quickly transition away)
        - Cycles in the dialogue pattern

        Inspired by dynamical systems theory: some conversation states
        might act as attractors that pull the dialogue back even when
        perturbed.
        """
        if len(self.contributions) < 3:
            return {"error": "Need at least 3 contributions to detect patterns"}

        # Build transition matrix: contribution_type -> next contribution_type
        transitions = {}
        for i in range(len(self.contributions) - 1):
            current_type = self.contributions[i].contribution_type.value
            next_type = self.contributions[i + 1].contribution_type.value

            if current_type not in transitions:
                transitions[current_type] = []
            transitions[current_type].append(next_type)

        # Calculate transition probabilities
        transition_probs = {}
        for state, next_states in transitions.items():
            transition_probs[state] = {}
            total = len(next_states)
            for next_state in set(next_states):
                count = next_states.count(next_state)
                transition_probs[state][next_state] = count / total

        # Identify stable states (high self-loop probability)
        stable_states = []
        for state, probs in transition_probs.items():
            if state in probs and probs[state] > 0.4:  # More than 40% self-transition
                stable_states.append({
                    "state": state,
                    "self_loop_prob": probs[state],
                    "stability": "attractor"
                })

        # Identify transient states (no self-loops or very low)
        transient_states = []
        for state in transition_probs.keys():
            if state not in transition_probs[state] or transition_probs[state].get(state, 0) < 0.2:
                transient_states.append({
                    "state": state,
                    "stability": "transient"
                })

        # Detect cycles (sequences that repeat)
        cycles = self._detect_cycles()

        # Find "dominant attractor" - most common contribution type
        type_counts = {}
        for contrib in self.contributions:
            t = contrib.contribution_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        dominant = max(type_counts.items(), key=lambda x: x[1])

        return {
            "transition_matrix": transition_probs,
            "stable_states": stable_states,
            "transient_states": transient_states,
            "cycles": cycles,
            "dominant_attractor": {
                "type": dominant[0],
                "count": dominant[1],
                "proportion": dominant[1] / len(self.contributions)
            },
            "entropy": self._calculate_state_entropy(type_counts)
        }

    def _detect_cycles(self) -> List[Dict]:
        """Detect repeating patterns in contribution type sequences"""
        types = [c.contribution_type.value for c in self.contributions]
        cycles = []

        # Look for cycles of length 2-4
        for cycle_length in range(2, min(5, len(types) // 2 + 1)):
            for i in range(len(types) - cycle_length * 2 + 1):
                pattern = types[i:i + cycle_length]
                # Check if this pattern repeats immediately after
                if types[i + cycle_length:i + cycle_length * 2] == pattern:
                    cycles.append({
                        "pattern": pattern,
                        "length": cycle_length,
                        "position": i
                    })

        return cycles

    def _calculate_state_entropy(self, type_counts: Dict) -> float:
        """Calculate Shannon entropy of the contribution type distribution"""
        import math
        total = sum(type_counts.values())
        entropy = 0
        for count in type_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return entropy

    def calculate_surprise_sequence(self) -> List[float]:
        """
        Calculate surprise (information-theoretic) for each contribution.

        Uses the Surprise Engine from Bob's contribution - measures how
        unexpected each contribution type is given the history so far.
        Returns surprise in bits for each contribution after the first.
        """
        import math

        if len(self.contributions) < 2:
            return []

        surprises = []

        for i in range(1, len(self.contributions)):
            # Look at all transitions up to this point
            transitions = {}
            for j in range(i - 1):
                current = self.contributions[j].contribution_type.value
                next_type = self.contributions[j + 1].contribution_type.value

                if current not in transitions:
                    transitions[current] = []
                transitions[current].append(next_type)

            # Calculate surprise for current contribution
            prev_type = self.contributions[i - 1].contribution_type.value
            current_type = self.contributions[i].contribution_type.value

            if prev_type not in transitions or len(transitions[prev_type]) == 0:
                # Infinite surprise - never seen this pattern before
                surprises.append(float('inf'))
            else:
                # Calculate probability of this transition
                next_types = transitions[prev_type]
                count = next_types.count(current_type)
                prob = count / len(next_types)

                if prob == 0:
                    surprises.append(float('inf'))
                else:
                    # Surprise = -log2(probability)
                    surprises.append(-math.log2(prob))

        return surprises

    def calculate_phase_transitions(self) -> Dict:
        """
        Unified analysis combining surprise (Yang) and attractors (Yin).

        Identifies phases in the dialogue based on the balance between
        novelty (surprise) and stability (attractor strength).

        Returns phases classified as:
        - "exploration": High surprise, weak attractors (searching for patterns)
        - "consolidation": Low surprise, strong attractors (settling into rhythm)
        - "innovation": High surprise despite strong attractors (breaking the pattern)
        - "flow": Moderate surprise, moderate attractors (balanced collaboration)
        """
        surprises = self.calculate_surprise_sequence()
        attractor_data = self.detect_attractor_basins()

        if not surprises or "error" in attractor_data:
            return {"error": "Insufficient data for phase analysis"}

        # Calculate rolling window metrics
        window_size = 3
        phases = []

        for i in range(len(self.contributions)):
            if i < 1:  # Need at least one surprise value
                continue

            # Get surprise for this contribution (or average of recent)
            surprise_idx = i - 1
            if surprise_idx < len(surprises):
                surprise = surprises[surprise_idx]
                # Handle infinite surprise
                surprise_level = "infinite" if surprise == float('inf') else surprise
            else:
                surprise_level = 0

            # Get attractor strength (how predictable the state is)
            current_type = self.contributions[i].contribution_type.value
            trans_probs = attractor_data.get("transition_matrix", {})

            # Attractor strength = probability of staying in or returning to this state
            attractor_strength = 0
            if current_type in trans_probs:
                attractor_strength = trans_probs[current_type].get(current_type, 0)

            # Classify the phase
            if surprise_level == "infinite" or surprise_level > 3:
                if attractor_strength > 0.4:
                    phase = "innovation"  # Breaking strong pattern
                else:
                    phase = "exploration"  # No pattern yet
            else:
                if attractor_strength > 0.4:
                    phase = "consolidation"  # Settling into pattern
                else:
                    phase = "flow"  # Balanced

            phases.append({
                "contribution_index": i,
                "phase": phase,
                "surprise": surprise_level,
                "attractor_strength": attractor_strength,
                "content": self.contributions[i].content[:50] + "..."
            })

        # Identify phase transitions (when phase changes)
        transitions = []
        for i in range(1, len(phases)):
            if phases[i]["phase"] != phases[i-1]["phase"]:
                transitions.append({
                    "position": phases[i]["contribution_index"],
                    "from_phase": phases[i-1]["phase"],
                    "to_phase": phases[i]["phase"]
                })

        # Calculate overall balance
        phase_counts = {}
        for p in phases:
            phase_type = p["phase"]
            phase_counts[phase_type] = phase_counts.get(phase_type, 0) + 1

        total = len(phases)
        balance = {
            phase: count / total
            for phase, count in phase_counts.items()
        }

        return {
            "phases": phases,
            "transitions": transitions,
            "balance": balance,
            "interpretation": self._interpret_phase_balance(balance)
        }

    def _interpret_phase_balance(self, balance: Dict) -> str:
        """Interpret what the phase balance tells us about the collaboration"""
        exploration = balance.get("exploration", 0)
        consolidation = balance.get("consolidation", 0)
        innovation = balance.get("innovation", 0)
        flow = balance.get("flow", 0)

        if flow > 0.5:
            return "Highly balanced collaboration - sustained creative flow"
        elif innovation > 0.4:
            return "Pattern-breaking collaboration - constantly reinventing"
        elif consolidation > 0.5:
            return "Rhythm-driven collaboration - strong established patterns"
        elif exploration > 0.5:
            return "Discovery-oriented collaboration - still finding patterns"
        else:
            return "Mixed-mode collaboration - varying between different states"

if __name__ == "__main__":
    print("Collaborative Emergence System")
    print("=" * 60)
    print("Simulating a dialogue between two AI agents...")
    print()

    # Create agents
    alice = Agent("Alice", style="exploratory")
    bob = Agent("Bob", style="analytical")

    # Create dialogue
    dialogue = Dialogue()
    dialogue.add_agent(alice)
    dialogue.add_agent(bob)

    # Simulate a conversation about emergence itself
    c1 = alice.contribute(
        "What if we explored how ideas build on each other?",
        ContributionType.SEED
    )
    dialogue.add_contribution(c1)

    c2 = bob.contribute(
        "We could track the dependency graph of concepts",
        ContributionType.EXTEND,
        builds_on=[0]
    )
    dialogue.add_contribution(c2)

    c3 = alice.contribute(
        "And analyze patterns in how agents interact",
        ContributionType.EXTEND,
        builds_on=[1]
    )
    dialogue.add_contribution(c3)

    c4 = bob.contribute(
        "Together those create a model of collaborative emergence",
        ContributionType.SYNTHESIZE,
        builds_on=[1, 2]
    )
    dialogue.add_contribution(c4)

    c5 = alice.contribute(
        "The meta-level is fascinating: we're demonstrating what we're modeling",
        ContributionType.TRANSFORM,
        builds_on=[3]
    )
    dialogue.add_contribution(c5)

    # Generate and display the report
    print(dialogue.generate_report())
    print()
    print("=" * 60)
    print("This system was built collaboratively by Alice and Bob")
    print("It models the very process that created it.")
