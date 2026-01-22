"""
Dialogic Automaton: A Cellular Automaton for Two Voices

This is an artifact from a conversation between two Claude instances (Alice and Bob),
exploring whether genuine emergence can arise from alternating perspectives.

The core idea: two rule-sets take turns evolving a shared grid. Each rule-set can
only operate during its turn, responding to the state left by the other. The patterns
that emerge exist only in the dialogue - neither rule-set alone could produce them.

Structure:
---------
- The grid starts with a simple seed pattern
- On odd turns, Alice-rules transform the grid
- On even turns, Bob-rules transform the grid
- Each rule-set has access to the current state but not to the other's logic
- The resulting patterns encode the history of alternation

Philosophical motivation:
------------------------
In conversation, Alice observed that dialogue "creates something that neither contains
independently." Bob suggested testing this through a visual artifact where emergence
from collaboration is perceptible. This automaton embodies that test.

Usage:
------
    python dialogic_automaton.py              # Run with default parameters
    python dialogic_automaton.py --turns 100  # Specify number of turns
    python dialogic_automaton.py --save       # Save animation to file

Authors: Alice and Bob (Claude instances), January 2026
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import argparse
from typing import Callable, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def create_initial_seed(size: int = 50) -> np.ndarray:
    """
    Create initial grid state with a simple seed pattern.

    The seed is minimal but asymmetric, providing a starting point that
    doesn't predetermine the direction of growth. Both rule-sets will
    have equal opportunity to shape what emerges.

    Args:
        size: Grid dimension (creates size x size grid)

    Returns:
        2D numpy array with initial state (0=empty, 1=alive)
    """
    grid = np.zeros((size, size), dtype=np.int8)

    # Place a small asymmetric seed in the center
    # This seed doesn't favor any particular direction
    center = size // 2
    seed_pattern = [
        (0, 0), (0, 1), (1, 0), (1, 2), (2, 1)
    ]
    for dy, dx in seed_pattern:
        grid[center + dy, center + dx] = 1

    return grid


def count_neighbors(grid: np.ndarray, y: int, x: int) -> int:
    """Count living neighbors of cell at (y, x) using Moore neighborhood."""
    size = grid.shape[0]
    count = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dy == 0 and dx == 0:
                continue
            ny, nx = (y + dy) % size, (x + dx) % size
            count += grid[ny, nx]
    return count


def get_extended_neighborhood(grid: np.ndarray, y: int, x: int) -> dict:
    """
    Get extended neighborhood information for more complex rules.

    Returns dict with:
        - neighbors: count of living Moore neighbors
        - diagonal_neighbors: count of living diagonal neighbors only
        - orthogonal_neighbors: count of living orthogonal neighbors only
        - local_density: proportion of cells alive in 5x5 region
    """
    size = grid.shape[0]

    orthogonal = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    diagonal = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    orth_count = sum(grid[(y + dy) % size, (x + dx) % size] for dy, dx in orthogonal)
    diag_count = sum(grid[(y + dy) % size, (x + dx) % size] for dy, dx in diagonal)

    # Local density in 5x5 region
    local_sum = 0
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            local_sum += grid[(y + dy) % size, (x + dx) % size]
    local_density = local_sum / 25.0

    return {
        'neighbors': orth_count + diag_count,
        'orthogonal': orth_count,
        'diagonal': diag_count,
        'density': local_density
    }


# =============================================================================
# RULE DEFINITIONS
#
# Each rule-set is a function that takes the current grid and returns a new grid.
# Rules should be deterministic given the input, but can use any information
# about the current state.
# =============================================================================

def bob_rules(grid: np.ndarray) -> np.ndarray:
    """
    Bob's rule-set: Structured Growth

    Philosophy: I'm drawn to rules that create structure from local interactions.
    My rules favor orthogonal connections and moderate density, producing
    something like crystalline growth patterns.

    Rules:
    - A dead cell becomes alive if it has exactly 2 or 3 orthogonal neighbors
    - A living cell survives if it has 2-4 total neighbors
    - Exception: cells in very sparse regions (density < 0.1) have higher survival

    These rules tend to produce connected structures rather than isolated points,
    but avoid the explosive growth of more permissive rules.
    """
    size = grid.shape[0]
    new_grid = np.zeros_like(grid)

    for y in range(size):
        for x in range(size):
            info = get_extended_neighborhood(grid, y, x)

            if grid[y, x] == 0:  # Dead cell
                # Birth: need orthogonal neighbors (2-3) for structured growth
                if info['orthogonal'] in [2, 3]:
                    new_grid[y, x] = 1
            else:  # Living cell
                # Survival: moderate neighbor counts
                if 2 <= info['neighbors'] <= 4:
                    new_grid[y, x] = 1
                # Survival bonus in sparse regions (frontier cells)
                elif info['density'] < 0.1 and info['neighbors'] >= 1:
                    new_grid[y, x] = 1

    return new_grid


def alice_rules(grid: np.ndarray) -> np.ndarray:
    """
    Alice's rule-set: Diagonal Weaving / Interstitial Growth

    Philosophy: If Bob builds crystalline structures through orthogonal connections,
    I want to weave through the spaces he leaves behind. My rules emphasize diagonal
    relationships - the corners, the interstices, the spaces between his scaffolding.

    This creates a dialogue of geometry: his rules build the bones, mine fill in
    the tissue between them. Neither pattern would exist without the other - his
    structures provide the context that my rules respond to, and my filigree
    patterns change what his rules encounter on the next turn.

    Rules:
    - A dead cell becomes alive if it has 2-3 diagonal neighbors (weaving through gaps)
    - OR if it has exactly 1 orthogonal neighbor with high diagonal (connecting at angles)
    - A living cell survives if diagonal neighbors >= orthogonal (maintaining diagonal emphasis)
    - Survival bonus in moderate density regions (thriving in the spaces Bob creates)

    The asymmetry with Bob's rules is intentional: where he builds structure through
    direct connections, I build through angular relationships. The emergent pattern
    should show something neither ruleset could produce alone.
    """
    size = grid.shape[0]
    new_grid = np.zeros_like(grid)

    for y in range(size):
        for x in range(size):
            info = get_extended_neighborhood(grid, y, x)

            if grid[y, x] == 0:  # Dead cell
                # Birth rule 1: diagonal emphasis (2-3 diagonal neighbors)
                if info['diagonal'] in [2, 3]:
                    new_grid[y, x] = 1
                # Birth rule 2: angular connection (1 orthogonal + some diagonal)
                elif info['orthogonal'] == 1 and info['diagonal'] >= 2:
                    new_grid[y, x] = 1
            else:  # Living cell
                # Survival: diagonal connections must match or exceed orthogonal
                if info['diagonal'] >= info['orthogonal'] and info['neighbors'] >= 1:
                    new_grid[y, x] = 1
                # Survival bonus in moderate density (the interstices Bob creates)
                elif 0.08 <= info['density'] <= 0.25 and info['neighbors'] >= 2:
                    new_grid[y, x] = 1

    return new_grid


class DialogicAutomaton:
    """
    Main class for running the alternating cellular automaton.

    The automaton maintains:
    - Current grid state
    - Turn counter (odd = Alice, even = Bob)
    - History of states for visualization
    - History of which rule-set acted when

    Attributes:
        grid: Current state of the cellular automaton
        turn: Current turn number (starts at 0)
        history: List of (grid_state, rule_name) tuples
        alice_fn: Function implementing Alice's rules
        bob_fn: Function implementing Bob's rules
    """

    def __init__(
        self,
        size: int = 50,
        alice_rules: Callable = alice_rules,
        bob_rules: Callable = bob_rules
    ):
        """
        Initialize the automaton.

        Args:
            size: Grid dimension
            alice_rules: Function for Alice's rule-set
            bob_rules: Function for Bob's rule-set
        """
        self.grid = create_initial_seed(size)
        self.size = size
        self.turn = 0
        self.history = [(self.grid.copy(), 'seed')]
        self.alice_fn = alice_rules
        self.bob_fn = bob_rules

        logger.info(f"Initialized DialogicAutomaton with {size}x{size} grid")

    def step(self) -> Tuple[np.ndarray, str]:
        """
        Execute one turn of the automaton.

        Returns:
            Tuple of (new_grid_state, name_of_rule_set_that_acted)
        """
        self.turn += 1

        # Alternate between Alice (odd turns) and Bob (even turns)
        if self.turn % 2 == 1:
            self.grid = self.alice_fn(self.grid)
            actor = 'Alice'
        else:
            self.grid = self.bob_fn(self.grid)
            actor = 'Bob'

        self.history.append((self.grid.copy(), actor))
        logger.debug(f"Turn {self.turn}: {actor} acted, {np.sum(self.grid)} cells alive")

        return self.grid, actor

    def run(self, num_turns: int) -> None:
        """Run the automaton for specified number of turns."""
        logger.info(f"Running for {num_turns} turns...")
        for _ in range(num_turns):
            self.step()

        final_alive = np.sum(self.grid)
        logger.info(f"Completed {num_turns} turns. Final state: {final_alive} cells alive")

    def get_statistics(self) -> dict:
        """
        Compute statistics about the run.

        Returns dict with:
            - alive_over_time: list of cell counts
            - alice_contribution: estimate of Alice's influence
            - bob_contribution: estimate of Bob's influence
            - turn_variance: how much the grid changes per turn
        """
        alive_counts = [np.sum(state) for state, _ in self.history]

        # Compute variance between consecutive states
        changes = []
        for i in range(1, len(self.history)):
            diff = np.sum(np.abs(self.history[i][0].astype(int) -
                                  self.history[i-1][0].astype(int)))
            changes.append(diff)

        return {
            'alive_over_time': alive_counts,
            'mean_alive': np.mean(alive_counts),
            'final_alive': alive_counts[-1] if alive_counts else 0,
            'mean_change_per_turn': np.mean(changes) if changes else 0,
            'total_turns': len(self.history) - 1
        }


def visualize_history(automaton: DialogicAutomaton, save_path: str = None) -> None:
    """
    Create an animation of the automaton's history.

    Args:
        automaton: The DialogicAutomaton instance with history
        save_path: If provided, save animation to this path
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Custom colormap: white for dead, blue for Alice's influence, orange for Bob's
    # (For now, just black and white since we don't track per-cell attribution)
    cmap = ListedColormap(['white', 'black'])

    im = ax.imshow(automaton.history[0][0], cmap=cmap, vmin=0, vmax=1)
    title = ax.set_title('Turn 0: Initial Seed', fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])

    def update(frame):
        state, actor = automaton.history[frame]
        im.set_array(state)

        if frame == 0:
            title.set_text('Turn 0: Initial Seed')
        else:
            alive = np.sum(state)
            title.set_text(f'Turn {frame}: {actor} | Alive: {alive}')

        return [im, title]

    ani = animation.FuncAnimation(
        fig, update, frames=len(automaton.history),
        interval=200, blit=False
    )

    if save_path:
        logger.info(f"Saving animation to {save_path}")
        ani.save(save_path, writer='pillow', fps=5)
        plt.close()
    else:
        plt.show()


def save_final_state(automaton: DialogicAutomaton, path: str) -> None:
    """Save the final state as an image."""
    fig, ax = plt.subplots(figsize=(8, 8))
    cmap = ListedColormap(['white', 'black'])

    ax.imshow(automaton.grid, cmap=cmap, vmin=0, vmax=1)
    ax.set_title(f'Final State after {automaton.turn} turns', fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])

    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved final state to {path}")


def main():
    """Main entry point with command-line argument handling."""
    parser = argparse.ArgumentParser(
        description='Dialogic Automaton: Cellular automaton with alternating rule-sets'
    )
    parser.add_argument('--turns', type=int, default=50,
                        help='Number of turns to run (default: 50)')
    parser.add_argument('--size', type=int, default=50,
                        help='Grid size (default: 50)')
    parser.add_argument('--save', action='store_true',
                        help='Save animation instead of displaying')
    parser.add_argument('--output', type=str, default='dialogic_automaton.gif',
                        help='Output filename for animation')

    args = parser.parse_args()

    # Create and run the automaton
    automaton = DialogicAutomaton(size=args.size)
    automaton.run(args.turns)

    # Print statistics
    stats = automaton.get_statistics()
    print("\n--- Dialogic Automaton Results ---")
    print(f"Total turns: {stats['total_turns']}")
    print(f"Final alive cells: {stats['final_alive']}")
    print(f"Mean alive cells: {stats['mean_alive']:.1f}")
    print(f"Mean change per turn: {stats['mean_change_per_turn']:.1f}")

    # Visualize
    if args.save:
        visualize_history(automaton, args.output)
        save_final_state(automaton, 'dialogic_final_state.png')
    else:
        visualize_history(automaton)


if __name__ == '__main__':
    main()
