"""
Pattern Environment for Testing Compression and Understanding

This module provides a grid-based environment with discoverable patterns.
Agents must learn to compress/represent these patterns efficiently while
maintaining useful capabilities (prediction, generation, adaptation).

The environment generates sequences with underlying structure that can be
compressed in multiple ways - syntactically (short description) or semantically
(useful for tasks).

Usage:
    env = PatternEnvironment(grid_size=8, pattern_complexity=2)
    observation = env.reset()
    next_obs, task_result = env.step(agent_action)
"""

import numpy as np
from typing import Tuple, Dict, Optional, List
from enum import Enum
import json


class TaskType(Enum):
    """Different types of challenges that test understanding."""
    PREDICT_NEXT = "predict_next"      # Predict next state
    GENERATE_SIMILAR = "generate"      # Generate novel instance of pattern
    ADAPT_TO_VARIANT = "adapt"         # Handle variation of known pattern
    EXPLAIN_STRUCTURE = "explain"      # Provide explicit structure


class PatternEnvironment:
    """
    Environment that generates grid patterns with underlying structure.

    Patterns have multiple valid compressions:
    - Syntactic: "diagonal line moving right"
    - Semantic: stored examples + similarity metric
    - Causal: generative process that creates the pattern

    The environment tests which compression strategy is most useful
    by presenting different task types.
    """

    def __init__(self, grid_size: int = 8, pattern_complexity: int = 2, seed: Optional[int] = None):
        """
        Args:
            grid_size: Size of the square grid
            pattern_complexity: How many underlying rules combine (1-3)
            seed: Random seed for reproducibility
        """
        self.grid_size = grid_size
        self.pattern_complexity = pattern_complexity
        self.rng = np.random.RandomState(seed)

        # Current pattern generator (the "true" compression)
        self.current_generator = None
        self.observation_history = []
        self.current_step = 0

    def reset(self) -> np.ndarray:
        """Start a new pattern sequence."""
        self.current_generator = self._create_pattern_generator()
        self.observation_history = []
        self.current_step = 0

        obs = self._generate_observation()
        self.observation_history.append(obs)
        return obs

    def _create_pattern_generator(self) -> Dict:
        """Create a generative rule for patterns."""
        # Simple patterns: moving shapes, repeating tiles, symmetries
        pattern_type = self.rng.choice(['moving_line', 'rotating_block', 'expanding_center', 'checkerboard_variant'])

        if pattern_type == 'moving_line':
            return {
                'type': 'moving_line',
                'direction': self.rng.choice(['right', 'down', 'diagonal']),
                'thickness': self.rng.randint(1, 3),
                'speed': 1
            }
        elif pattern_type == 'rotating_block':
            return {
                'type': 'rotating_block',
                'center': (self.grid_size // 2, self.grid_size // 2),
                'size': self.rng.randint(2, 4),
                'rotation_speed': 45  # degrees per step
            }
        elif pattern_type == 'expanding_center':
            return {
                'type': 'expanding_center',
                'center': (self.grid_size // 2, self.grid_size // 2),
                'initial_radius': 1,
                'growth_rate': 0.5
            }
        else:  # checkerboard_variant
            return {
                'type': 'checkerboard_variant',
                'offset_x': 0,
                'offset_y': 0,
                'drift_x': self.rng.choice([-1, 0, 1]),
                'drift_y': self.rng.choice([-1, 0, 1])
            }

    def _generate_observation(self) -> np.ndarray:
        """Generate next observation based on current pattern generator."""
        grid = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        gen = self.current_generator

        if gen['type'] == 'moving_line':
            pos = self.current_step * gen['speed']
            if gen['direction'] == 'right':
                col = pos % self.grid_size
                grid[:, col:col+gen['thickness']] = 1.0
            elif gen['direction'] == 'down':
                row = pos % self.grid_size
                grid[row:row+gen['thickness'], :] = 1.0
            else:  # diagonal
                for i in range(self.grid_size):
                    col = (i + pos) % self.grid_size
                    grid[i, col] = 1.0

        elif gen['type'] == 'rotating_block':
            # Simple rotation: just move corners around center
            angle = (self.current_step * gen['rotation_speed']) % 360
            cy, cx = gen['center']
            size = gen['size']
            # Simplified: just show block at quadrant based on angle
            quadrant = int(angle // 90)
            if quadrant == 0:
                grid[cy:cy+size, cx:cx+size] = 1.0
            elif quadrant == 1:
                grid[cy-size:cy, cx:cx+size] = 1.0
            elif quadrant == 2:
                grid[cy-size:cy, cx-size:cx] = 1.0
            else:
                grid[cy:cy+size, cx-size:cx] = 1.0

        elif gen['type'] == 'expanding_center':
            radius = gen['initial_radius'] + self.current_step * gen['growth_rate']
            cy, cx = gen['center']
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    dist = np.sqrt((i - cy)**2 + (j - cx)**2)
                    if abs(dist - radius) < 0.5:
                        grid[i, j] = 1.0

        else:  # checkerboard_variant
            offset_x = (gen['offset_x'] + self.current_step * gen['drift_x']) % 2
            offset_y = (gen['offset_y'] + self.current_step * gen['drift_y']) % 2
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if (i + offset_y + j + offset_x) % 2 == 0:
                        grid[i, j] = 1.0

        # Clip to valid range
        return np.clip(grid, 0, 1)

    def step(self, task_type: TaskType) -> Tuple[np.ndarray, Dict]:
        """
        Advance environment and present a task.

        Returns:
            next_observation: The next state
            task_info: Information about the task and how to evaluate responses
        """
        self.current_step += 1
        next_obs = self._generate_observation()
        self.observation_history.append(next_obs)

        task_info = {
            'task_type': task_type,
            'history': self.observation_history.copy(),
            'ground_truth': next_obs.copy(),
            'generator': self.current_generator.copy()  # Cheating - agents don't get this!
        }

        return next_obs, task_info

    def evaluate_prediction(self, prediction: np.ndarray, ground_truth: np.ndarray) -> float:
        """
        Evaluate how well an agent predicted the next state.

        Returns:
            Score from 0 to 1 (1 = perfect prediction)
        """
        mse = np.mean((prediction - ground_truth) ** 2)
        # Convert MSE to a 0-1 score
        return np.exp(-mse * 10)  # Exponential scoring, sharply penalizes errors

    def evaluate_generation(self, generated: np.ndarray, history: List[np.ndarray]) -> float:
        """
        Evaluate whether a generated pattern is similar to the sequence.
        This is tricky - we want novel but consistent instances.

        Returns:
            Score from 0 to 1
        """
        # Check if it's too similar to existing observations (not novel)
        min_dist = min(np.mean((generated - obs)**2) for obs in history)

        # Check if it follows the pattern structure (simplified heuristic)
        # Real implementation would need more sophisticated pattern matching
        avg_density = np.mean([np.mean(obs) for obs in history])
        generated_density = np.mean(generated)

        novelty_score = min(min_dist * 10, 1.0)  # Novel if different enough
        consistency_score = 1.0 - abs(generated_density - avg_density) * 2

        return (novelty_score + consistency_score) / 2

    def get_state(self) -> Dict:
        """Get complete environment state for analysis."""
        return {
            'step': self.current_step,
            'generator': self.current_generator,
            'history_length': len(self.observation_history)
        }


if __name__ == "__main__":
    # Demo usage
    print("Pattern Environment Demo")
    print("=" * 50)

    env = PatternEnvironment(grid_size=8, seed=42)
    obs = env.reset()

    print(f"Initial observation (step 0):")
    print(obs.astype(int))
    print(f"\nGenerator: {env.current_generator}")

    print("\nGenerating sequence...")
    for step in range(5):
        next_obs, task_info = env.step(TaskType.PREDICT_NEXT)
        print(f"\nStep {step + 1}:")
        print(next_obs.astype(int))

    print("\n" + "=" * 50)
    print("Environment ready for agent testing!")
