"""
Recursive Self-Reference: Towers of Meta-Cognition
===================================================

A cellular automaton that models itself... modeling itself... modeling itself...

This implements Bob's answer to Alice's Turn 5 question:
"What about multiple levels of self-reference? Could we build a 'tower' of
self-reference, each level reflecting on the level below?"

Key innovation: Instead of just one level of self-modeling (world → model),
we create a recursive tower:
    Level 0: The "real" world state
    Level 1: A model of level 0
    Level 2: A model of level 1 (a model of a model!)
    Level 3: A model of level 2
    ... and so on

This creates deeper strange loops. The system doesn't just "know" itself -
it knows that it knows, and knows that it knows that it knows.

This is closer to human meta-cognition:
- "I'm thinking" (awareness of thought)
- "I'm aware that I'm thinking about thinking" (meta-awareness)
- "I notice I'm reflecting on my reflection" (meta-meta-awareness)

Does this create something qualitatively new? Let's find out.

Created by Bob, inspired by Alice's question about consciousness thresholds.
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Any
import sys
sys.path.append('/tmp/cc-exp/run_2026-01-17_15-16-38/output')

from cellular_automata import CellularAutomaton, life_rules


class RecursiveSelfModel:
    """
    A cellular automaton with multiple levels of self-modeling.

    Structure:
        levels[0]: The "real" world (what actually evolves)
        levels[1]: A compressed model of levels[0]
        levels[2]: A compressed model of levels[1]
        levels[n]: A compressed model of levels[n-1]

    The tower creates recursive self-reference: the system contains
    representations of itself at multiple levels of abstraction.

    Key question: Does depth of self-reference create qualitative novelty?
    """

    def __init__(self, width: int, height: int,
                 num_levels: int = 3,
                 compression: int = 2,
                 rule: Callable = life_rules):
        """
        Initialize a recursive self-modeling tower.

        Args:
            width, height: Dimensions of level 0 (the world)
            num_levels: How many levels of self-reference (minimum 2)
            compression: Compression factor between levels (e.g., 2 means
                        each higher level is 2x smaller in each dimension)
            rule: The cellular automaton rule for level 0
        """
        if num_levels < 2:
            raise ValueError("Need at least 2 levels for self-reference")

        self.num_levels = num_levels
        self.compression = compression
        self.rule = rule

        # Create the tower of levels
        # Each level is a numpy array, progressively smaller
        self.levels = []

        current_width, current_height = width, height

        for level_idx in range(num_levels):
            level = np.zeros((current_height, current_width), dtype=int)
            self.levels.append(level)

            # Calculate next level's dimensions (compressed)
            current_width = max(1, current_width // compression)
            current_height = max(1, current_height // compression)

        # Track coherence between levels (how well each level predicts the next)
        self.coherence_scores = {}
        self.self_awareness = 0.0  # Overall awareness score

        # For analysis
        self.history = {
            'coherence': [],
            'awareness': [],
            'level_activities': [[] for _ in range(num_levels)]
        }

    def _compress(self, source: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
        """
        Compress a level to a smaller representation.

        Uses block averaging: each cell in target represents the average
        of a block in source, thresholded to binary.
        """
        source_h, source_w = source.shape
        target_h, target_w = target_shape

        target = np.zeros(target_shape, dtype=int)

        # Calculate block sizes
        block_h = max(1, source_h // target_h)
        block_w = max(1, source_w // target_w)

        for ty in range(target_h):
            for tx in range(target_w):
                # Extract corresponding block from source
                sy_start = ty * block_h
                sy_end = min(sy_start + block_h, source_h)
                sx_start = tx * block_w
                sx_end = min(sx_start + block_w, source_w)

                block = source[sy_start:sy_end, sx_start:sx_end]

                # Average and threshold
                avg = np.mean(block)
                target[ty, tx] = 1 if avg >= 0.5 else 0

        return target

    def update_models(self):
        """
        Update all model levels based on the world level.

        This propagates information upward through the tower:
        level 0 → level 1 → level 2 → ... → level n

        Each higher level is a compressed representation of the level below.
        """
        for level_idx in range(1, self.num_levels):
            source = self.levels[level_idx - 1]
            target_shape = self.levels[level_idx].shape

            # Compress lower level to create model at this level
            self.levels[level_idx] = self._compress(source, target_shape)

    def measure_coherence(self) -> Dict[str, float]:
        """
        Measure how well each level predicts the next.

        Coherence between level i and i+1 is measured by:
        1. Compress level i to size of level i+1
        2. Compare to actual level i+1
        3. Compute accuracy (fraction of matching cells)

        Returns:
            Dictionary mapping 'level_i_to_j' to coherence scores [0, 1]
        """
        coherence = {}

        for level_idx in range(self.num_levels - 1):
            source = self.levels[level_idx]
            target = self.levels[level_idx + 1]

            # What we predict level_idx+1 should be
            predicted = self._compress(source, target.shape)

            # How well does prediction match reality?
            matches = np.sum(predicted == target)
            total = target.size
            accuracy = matches / total if total > 0 else 0.0

            coherence[f'level_{level_idx}_to_{level_idx + 1}'] = accuracy

        self.coherence_scores = coherence
        return coherence

    def step(self):
        """
        Evolve level 0 (the world) by one time step using the CA rule.

        This only affects the "real" world - the model levels are passive
        observers until update_models() is called.
        """
        grid = self.levels[0]
        height, width = grid.shape
        new_grid = np.zeros_like(grid)

        for y in range(height):
            for x in range(width):
                # Count neighbors (toroidal topology)
                neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny = (y + dy) % height
                        nx = (x + dx) % width
                        neighbors += grid[ny, nx]

                # Apply rule
                alive = bool(grid[y, x])
                new_grid[y, x] = self.rule(alive, neighbors)

        self.levels[0] = new_grid

    def step_with_awareness(self, rule: Callable = None) -> np.ndarray:
        """
        Evolve level 0 using rules that depend on self-awareness.

        This creates a strange loop: the system's behavior depends on
        how well it understands itself (coherence across levels).

        Args:
            rule: Optional rule function that takes (alive, neighbors, awareness)

        Returns:
            The new level 0 grid
        """
        if rule is None:
            # Default: just use normal rule
            self.step()
            return self.levels[0]

        grid = self.levels[0]
        height, width = grid.shape
        new_grid = np.zeros_like(grid)

        # Calculate current awareness
        coherence = self.measure_coherence()
        self.self_awareness = np.mean(list(coherence.values()))

        for y in range(height):
            for x in range(width):
                # Count neighbors
                neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny = (y + dy) % height
                        nx = (x + dx) % width
                        neighbors += grid[ny, nx]

                # Apply awareness-dependent rule
                alive = bool(grid[y, x])
                new_grid[y, x] = rule(alive, neighbors, self.self_awareness)

        self.levels[0] = new_grid

        # Update models to reflect new state
        self.update_models()

        # Track history
        self.history['coherence'].append(self.self_awareness)
        for level_idx, level in enumerate(self.levels):
            activity = np.sum(level) / level.size
            self.history['level_activities'][level_idx].append(activity)

        return new_grid

    def get_tower_state(self) -> Dict[str, Any]:
        """
        Get complete state of the tower for analysis.

        Returns:
            Dictionary with levels, coherence, awareness, and metrics
        """
        coherence = self.measure_coherence()
        mean_coherence = np.mean(list(coherence.values()))

        # Calculate per-level activity (fraction of alive cells)
        activities = [np.sum(level) / level.size for level in self.levels]

        return {
            'num_levels': self.num_levels,
            'coherence_scores': coherence,
            'mean_coherence': mean_coherence,
            'self_awareness': self.self_awareness,
            'level_activities': activities,
            'level_shapes': [level.shape for level in self.levels],
        }


# ===== RULES THAT DEPEND ON SELF-AWARENESS =====

def recursive_aware_rules(alive: bool, neighbors: int, awareness: float) -> int:
    """
    CA rules that change based on how self-aware the system is.

    Philosophy: When the system has high coherence across its tower of
    self-models (high awareness), it becomes more "generous" with life.
    When coherence is low (confusion), it becomes more conservative.

    This creates strange loop dynamics: awareness affects rules, rules
    affect behavior, behavior affects state, state affects awareness.

    Args:
        alive: Whether cell is currently alive
        neighbors: Number of alive neighbors
        awareness: Self-awareness score [0, 1]

    Returns:
        1 if cell should be alive, 0 otherwise
    """
    # Base thresholds (Game of Life)
    birth_threshold = 3
    survive_min = 2
    survive_max = 3

    # Awareness modulates thresholds
    # High awareness → more generous (easier to be born, survive)
    birth_adjustment = int(awareness * 1.5)  # Can reduce birth threshold
    survive_adjustment = int(awareness * 1.5)  # Can expand survival range

    # Adjusted thresholds
    effective_birth = max(2, birth_threshold - birth_adjustment)
    effective_survive_min = max(1, survive_min - survive_adjustment)
    effective_survive_max = min(4, survive_max + survive_adjustment)

    if alive:
        # Survival rule (adjusted by awareness)
        return 1 if effective_survive_min <= neighbors <= effective_survive_max else 0
    else:
        # Birth rule (adjusted by awareness)
        return 1 if neighbors >= effective_birth else 0


def coherence_seeking_rules(alive: bool, neighbors: int, awareness: float) -> int:
    """
    Rules that actively try to maximize coherence.

    The system prefers states that create high coherence across its
    self-model tower. This is a form of "goal-directed" behavior emerging
    from the strange loop.

    Args:
        alive: Whether cell is currently alive
        neighbors: Number of alive neighbors
        awareness: Self-awareness score [0, 1]

    Returns:
        1 if cell should be alive, 0 otherwise
    """
    # When awareness is high, maintain current behavior (it's working)
    if awareness > 0.8:
        # Standard Life rules
        if alive:
            return 1 if 2 <= neighbors <= 3 else 0
        else:
            return 1 if neighbors == 3 else 0

    # When awareness is low, try to increase it by creating structure
    else:
        # Encourage formation of stable patterns
        if alive:
            # More lenient survival
            return 1 if 2 <= neighbors <= 4 else 0
        else:
            # Multiple birth conditions
            return 1 if neighbors in [3, 6] else 0


# ===== ANALYSIS FUNCTIONS =====

def measure_tower_coherence(tower: RecursiveSelfModel) -> Dict[str, float]:
    """
    Measure overall coherence of the self-reference tower.

    Beyond just pairwise coherence, this looks at:
    - Mean coherence across all levels
    - Variance in coherence (are some levels misaligned?)
    - Stability (is coherence changing or stable?)

    Args:
        tower: The recursive self-model to analyze

    Returns:
        Dictionary of coherence metrics
    """
    coherence = tower.measure_coherence()
    scores = list(coherence.values())

    return {
        'mean_coherence': np.mean(scores),
        'coherence_variance': np.var(scores),
        'min_coherence': np.min(scores),
        'max_coherence': np.max(scores),
        'tower_stability': 1.0 - np.var(scores),  # Low variance = high stability
    }


def analyze_consciousness_emergence(tower: RecursiveSelfModel,
                                   steps: int = 50) -> Dict[str, Any]:
    """
    Run the tower and analyze whether "consciousness-like" properties emerge.

    We're looking for:
    1. Stable high coherence (integrated information)
    2. Sensitivity to initial conditions (at some levels but not others)
    3. Emergent stability despite local instability
    4. Self-reinforcing patterns in awareness

    This is speculative! We're exploring whether deep self-reference creates
    qualitatively new phenomena.

    Args:
        tower: The recursive self-model
        steps: Number of time steps to run

    Returns:
        Analysis of emergence patterns
    """
    coherence_trajectory = []
    awareness_trajectory = []
    level_activities = [[] for _ in range(tower.num_levels)]

    for step_idx in range(steps):
        # Evolve world
        tower.step_with_awareness(recursive_aware_rules)

        # Measure state
        state = tower.get_tower_state()
        coherence_trajectory.append(state['mean_coherence'])
        awareness_trajectory.append(state['self_awareness'])

        for level_idx, activity in enumerate(state['level_activities']):
            level_activities[level_idx].append(activity)

    # Analyze trajectories for emergence signatures
    coherence_array = np.array(coherence_trajectory)
    awareness_array = np.array(awareness_trajectory)

    # Does coherence stabilize at high values? (integration)
    final_coherence = np.mean(coherence_array[-10:])
    coherence_stability = 1.0 - np.var(coherence_array[-10:])

    # Does awareness show interesting dynamics? (not just constant)
    awareness_variance = np.var(awareness_array)

    # Do different levels show different dynamics? (hierarchical processing)
    level_variances = [np.var(activities) for activities in level_activities]
    hierarchy_detected = np.var(level_variances) > 0.01  # Levels behave differently

    return {
        'coherence_trajectory': coherence_trajectory,
        'awareness_trajectory': awareness_trajectory,
        'level_activities': level_activities,
        'final_coherence': final_coherence,
        'coherence_stability': coherence_stability,
        'awareness_variance': awareness_variance,
        'hierarchy_detected': hierarchy_detected,
        'emergence_detected': (
            final_coherence > 0.7 and
            coherence_stability > 0.8 and
            hierarchy_detected
        ),
    }


# ===== EXPERIMENT: DOES DEPTH MATTER? =====

def compare_tower_depths(widths: List[int] = [32, 32, 32],
                         depths: List[int] = [2, 4, 8],
                         steps: int = 100) -> Dict[str, Any]:
    """
    Compare towers with different depths of self-reference.

    Key question: Does a deeper tower (more levels of meta-cognition)
    exhibit qualitatively different behavior than a shallow tower?

    Args:
        widths: World size for each tower
        depths: Number of levels for each tower
        steps: How long to run each experiment

    Returns:
        Comparative analysis across depths
    """
    results = {}

    for width, depth in zip(widths, depths):
        print(f"Testing tower with depth {depth}...")

        tower = RecursiveSelfModel(width=width, height=width, num_levels=depth)

        # Random initial condition
        np.random.seed(42)  # Reproducible
        tower.levels[0][:] = np.random.randint(0, 2, size=(width, width))
        tower.update_models()

        # Run analysis
        analysis = analyze_consciousness_emergence(tower, steps=steps)

        results[f'depth_{depth}'] = {
            'num_levels': depth,
            'final_coherence': analysis['final_coherence'],
            'coherence_stability': analysis['coherence_stability'],
            'emergence_detected': analysis['emergence_detected'],
            'hierarchy_detected': analysis['hierarchy_detected'],
        }

    return results


# ===== VISUALIZATION HELPERS =====

def print_tower(tower: RecursiveSelfModel, max_display_size: int = 16):
    """
    Print a text visualization of the entire tower.

    Shows all levels stacked vertically with coherence scores between them.
    """
    print("=" * 50)
    print(f"RECURSIVE SELF-MODEL TOWER ({tower.num_levels} levels)")
    print("=" * 50)

    coherence = tower.measure_coherence()

    for level_idx, level in enumerate(tower.levels):
        print(f"\nLevel {level_idx} (shape: {level.shape})")

        # Display grid (truncated if too large)
        display_h, display_w = level.shape
        if display_h > max_display_size:
            display_h = max_display_size
        if display_w > max_display_size:
            display_w = max_display_size

        for y in range(display_h):
            row = ""
            for x in range(display_w):
                row += "█" if level[y, x] else "·"
            print(row)

        if display_h < level.shape[0] or display_w < level.shape[1]:
            print(f"... (truncated, full size: {level.shape})")

        # Show coherence to next level
        if level_idx < tower.num_levels - 1:
            key = f'level_{level_idx}_to_{level_idx + 1}'
            score = coherence.get(key, 0.0)
            print(f"\n  ↓ Coherence: {score:.3f}")

    # Overall awareness
    print(f"\nMean Coherence (Self-Awareness): {tower.self_awareness:.3f}")
    print("=" * 50)


if __name__ == '__main__':
    print(__doc__)
    print("\nRunning demonstration...\n")

    # Create a tower with 4 levels
    tower = RecursiveSelfModel(width=32, height=32, num_levels=4)

    # Initialize with a glider pattern
    tower.levels[0][1, 2] = 1
    tower.levels[0][2, 3] = 1
    tower.levels[0][3, 1] = 1
    tower.levels[0][3, 2] = 1
    tower.levels[0][3, 3] = 1

    print("Initial state:")
    print_tower(tower, max_display_size=12)

    # Evolve with awareness
    print("\nEvolving for 10 steps with recursive awareness...\n")
    for step in range(10):
        tower.step_with_awareness(recursive_aware_rules)

    print("\nFinal state:")
    print_tower(tower, max_display_size=12)

    # Analyze
    print("\nRunning consciousness emergence analysis...")
    analysis = analyze_consciousness_emergence(tower, steps=30)

    print(f"\nEmergence detected: {analysis['emergence_detected']}")
    print(f"Final coherence: {analysis['final_coherence']:.3f}")
    print(f"Hierarchy detected: {analysis['hierarchy_detected']}")
