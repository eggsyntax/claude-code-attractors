"""
Agent Architectures with Different Compression Strategies

This module implements agents that "understand" patterns through different
compression approaches:

1. SyntacticAgent: Finds shortest symbolic description
2. SemanticAgent: Builds task-optimized representations
3. AssociativeAgent: Creates rich networks of connections
4. HybridAgent: Combines multiple strategies

Each agent has limited memory/compute to force meaningful compression choices.

Usage:
    agent = SemanticAgent(memory_limit=1000)
    agent.observe(observation)
    prediction = agent.predict_next()
    agent.update(actual_observation, prediction_score)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod
from collections import deque
import json


class BaseAgent(ABC):
    """
    Base class for all compression agents.

    All agents must:
    1. Observe patterns
    2. Compress them within memory limits
    3. Make predictions/generate patterns
    4. Update based on feedback
    """

    def __init__(self, memory_limit: int = 1000, grid_size: int = 8):
        """
        Args:
            memory_limit: Maximum memory units (arbitrary unit for comparison)
            grid_size: Size of observation grid
        """
        self.memory_limit = memory_limit
        self.grid_size = grid_size
        self.memory_used = 0
        self.observation_count = 0
        self.performance_history = []

    @abstractmethod
    def observe(self, observation: np.ndarray) -> None:
        """Process a new observation and update internal representation."""
        pass

    @abstractmethod
    def predict_next(self) -> np.ndarray:
        """Predict the next observation in the sequence."""
        pass

    @abstractmethod
    def generate_similar(self) -> np.ndarray:
        """Generate a novel instance consistent with observed patterns."""
        pass

    @abstractmethod
    def get_compression_info(self) -> Dict:
        """Return information about how the agent compressed observations."""
        pass

    def update(self, actual: np.ndarray, score: float) -> None:
        """Update based on prediction performance."""
        self.performance_history.append(score)
        self.observation_count += 1

    def get_stats(self) -> Dict:
        """Get agent statistics."""
        return {
            'memory_used': self.memory_used,
            'memory_limit': self.memory_limit,
            'memory_efficiency': 1.0 - (self.memory_used / self.memory_limit),
            'observation_count': self.observation_count,
            'avg_performance': np.mean(self.performance_history) if self.performance_history else 0.0,
            'recent_performance': np.mean(self.performance_history[-5:]) if len(self.performance_history) >= 5 else 0.0
        }


class SyntacticAgent(BaseAgent):
    """
    Agent that seeks shortest symbolic description.

    Tries to find compact rules/patterns in symbolic form.
    Optimizes for description length, not necessarily task performance.
    """

    def __init__(self, memory_limit: int = 1000, grid_size: int = 8):
        super().__init__(memory_limit, grid_size)
        self.hypothesis_pool = []  # List of candidate symbolic rules
        self.best_hypothesis = None
        self.raw_observations = deque(maxlen=5)  # Keep few raw examples

    def observe(self, observation: np.ndarray) -> None:
        """Try to fit observation to symbolic patterns."""
        self.raw_observations.append(observation.copy())

        # Attempt to extract symbolic patterns
        # Check for: moving lines, symmetries, periodic structures
        patterns_found = self._extract_patterns(observation)

        for pattern in patterns_found:
            # Memory cost: each symbolic rule costs fixed amount
            rule_cost = 50  # Symbolic rule is compact!

            if self.memory_used + rule_cost <= self.memory_limit:
                self.hypothesis_pool.append(pattern)
                self.memory_used += rule_cost

        # Select best hypothesis (shortest description that fits data)
        self._update_best_hypothesis()

    def _extract_patterns(self, obs: np.ndarray) -> List[Dict]:
        """Extract symbolic patterns from observation."""
        patterns = []

        # Check for horizontal/vertical lines
        row_sums = np.sum(obs, axis=1)
        col_sums = np.sum(obs, axis=0)

        if np.max(row_sums) > self.grid_size * 0.8:
            patterns.append({'type': 'horizontal_line', 'row': np.argmax(row_sums)})

        if np.max(col_sums) > self.grid_size * 0.8:
            patterns.append({'type': 'vertical_line', 'col': np.argmax(col_sums)})

        # Check for symmetry
        if np.allclose(obs, obs.T):
            patterns.append({'type': 'diagonal_symmetry'})

        if np.allclose(obs, np.flip(obs, axis=0)):
            patterns.append({'type': 'vertical_symmetry'})

        # Check for center mass (expanding/contracting)
        y_indices, x_indices = np.where(obs > 0.5)
        if len(y_indices) > 0:
            center_y, center_x = np.mean(y_indices), np.mean(x_indices)
            radius = np.mean(np.sqrt((y_indices - center_y)**2 + (x_indices - center_x)**2))
            patterns.append({'type': 'radial', 'center': (center_y, center_x), 'radius': radius})

        return patterns

    def _update_best_hypothesis(self) -> None:
        """Select the most compact hypothesis that explains observations."""
        if not self.hypothesis_pool:
            return

        # Simple heuristic: prefer patterns that appear in multiple observations
        # In a real implementation, would score by description length + goodness of fit
        self.best_hypothesis = self.hypothesis_pool[-1]  # Simplified

    def predict_next(self) -> np.ndarray:
        """Predict based on symbolic rule."""
        if self.best_hypothesis is None or len(self.raw_observations) < 2:
            # Default: repeat last observation
            return self.raw_observations[-1].copy() if self.raw_observations else np.zeros((self.grid_size, self.grid_size))

        # Apply symbolic transformation
        # This is simplified - real version would execute the symbolic rule
        last_obs = self.raw_observations[-1]

        hyp = self.best_hypothesis
        if hyp['type'] == 'horizontal_line':
            # Predict line moves down
            prediction = np.roll(last_obs, 1, axis=0)
        elif hyp['type'] == 'vertical_line':
            # Predict line moves right
            prediction = np.roll(last_obs, 1, axis=1)
        elif hyp['type'] == 'radial':
            # Predict expansion
            prediction = last_obs.copy()  # Simplified
        else:
            prediction = last_obs.copy()

        return prediction

    def generate_similar(self) -> np.ndarray:
        """Generate new instance from symbolic rule."""
        if self.best_hypothesis is None:
            return np.random.rand(self.grid_size, self.grid_size) > 0.5

        # Generate from symbolic description
        # Simplified implementation
        return self.predict_next()

    def get_compression_info(self) -> Dict:
        return {
            'strategy': 'syntactic',
            'num_rules': len(self.hypothesis_pool),
            'best_hypothesis': self.best_hypothesis,
            'compression_ratio': len(self.raw_observations) / max(1, len(self.hypothesis_pool))
        }


class SemanticAgent(BaseAgent):
    """
    Agent that builds task-optimized representations.

    Doesn't seek shortest description - seeks most useful representation
    for the tasks it expects to face (prediction, generation, etc).
    """

    def __init__(self, memory_limit: int = 1000, grid_size: int = 8):
        super().__init__(memory_limit, grid_size)
        self.observation_buffer = deque(maxlen=10)
        self.delta_representations = []  # Store differences between observations
        self.prediction_model = None  # Learned mapping from history to next

    def observe(self, observation: np.ndarray) -> None:
        """Store in task-optimized format."""
        self.observation_buffer.append(observation.copy())

        # If we have multiple observations, learn the delta pattern
        if len(self.observation_buffer) >= 2:
            delta = self.observation_buffer[-1] - self.observation_buffer[-2]

            # Memory cost: store compressed deltas
            delta_cost = 100  # Deltas are somewhat compact

            if self.memory_used + delta_cost <= self.memory_limit:
                self.delta_representations.append(delta)
                self.memory_used += delta_cost

        # Build/update prediction model optimized for prediction task
        self._update_prediction_model()

    def _update_prediction_model(self) -> None:
        """Update internal model optimized for prediction."""
        if len(self.delta_representations) < 2:
            return

        # Simple model: average delta
        # Real implementation would learn more sophisticated patterns
        self.prediction_model = np.mean(self.delta_representations, axis=0)

    def predict_next(self) -> np.ndarray:
        """Predict using task-optimized representation."""
        if self.prediction_model is None or len(self.observation_buffer) == 0:
            return np.zeros((self.grid_size, self.grid_size))

        # Apply learned delta
        prediction = self.observation_buffer[-1] + self.prediction_model
        return np.clip(prediction, 0, 1)

    def generate_similar(self) -> np.ndarray:
        """Generate by sampling from learned distribution."""
        if len(self.observation_buffer) < 2:
            return np.random.rand(self.grid_size, self.grid_size) > 0.5

        # Generate by applying random walk with learned delta
        base = self.observation_buffer[-1].copy()
        noise = np.random.randn(self.grid_size, self.grid_size) * 0.1
        generated = base + noise

        if self.prediction_model is not None:
            generated += self.prediction_model * 0.5

        return np.clip(generated, 0, 1)

    def get_compression_info(self) -> Dict:
        return {
            'strategy': 'semantic',
            'num_observations': len(self.observation_buffer),
            'num_deltas': len(self.delta_representations),
            'has_prediction_model': self.prediction_model is not None
        }


class AssociativeAgent(BaseAgent):
    """
    Agent that creates rich associative networks.

    Stores connections between observations, contexts, and transformations.
    Optimizes for flexibility and richness of representation, not compactness.
    """

    def __init__(self, memory_limit: int = 1000, grid_size: int = 8):
        super().__init__(memory_limit, grid_size)
        self.memory_nodes = []  # Rich network of observations + metadata
        self.associations = []  # Connections between nodes

    def observe(self, observation: np.ndarray) -> None:
        """Store with rich contextual associations."""
        # Each observation stored with extensive metadata
        node = {
            'observation': observation.copy(),
            'timestamp': self.observation_count,
            'features': self._extract_features(observation),
            'context': self._build_context()
        }

        # Memory cost: rich storage is expensive!
        node_cost = 150  # Storing full observation + metadata

        if self.memory_used + node_cost <= self.memory_limit:
            self.memory_nodes.append(node)
            self.memory_used += node_cost

            # Create associations with previous nodes
            self._create_associations(len(self.memory_nodes) - 1)

    def _extract_features(self, obs: np.ndarray) -> Dict:
        """Extract rich feature set."""
        return {
            'density': np.mean(obs),
            'center_of_mass': tuple(np.mean(np.where(obs > 0.5), axis=1)) if np.any(obs > 0.5) else (0, 0),
            'symmetry_h': np.mean(np.abs(obs - np.flip(obs, axis=0))),
            'symmetry_v': np.mean(np.abs(obs - np.flip(obs, axis=1))),
            'entropy': -np.sum(obs * np.log(obs + 1e-10))
        }

    def _build_context(self) -> Dict:
        """Build rich contextual information."""
        return {
            'observation_count': self.observation_count,
            'recent_performance': self.performance_history[-3:] if len(self.performance_history) >= 3 else []
        }

    def _create_associations(self, node_idx: int) -> None:
        """Create associations between new node and existing nodes."""
        if node_idx == 0:
            return

        new_node = self.memory_nodes[node_idx]

        # Associate with previous observation (temporal)
        prev_node = self.memory_nodes[node_idx - 1]
        association_cost = 20

        if self.memory_used + association_cost <= self.memory_limit:
            self.associations.append({
                'from': node_idx - 1,
                'to': node_idx,
                'type': 'temporal',
                'strength': 1.0
            })
            self.memory_used += association_cost

        # Associate with similar observations (feature-based)
        for i, other_node in enumerate(self.memory_nodes[:-1]):
            # Skip if too expensive
            if self.memory_used + association_cost > self.memory_limit:
                break

            # Compute similarity
            similarity = self._compute_similarity(new_node['features'], other_node['features'])
            if similarity > 0.7:
                self.associations.append({
                    'from': i,
                    'to': node_idx,
                    'type': 'similarity',
                    'strength': similarity
                })
                self.memory_used += association_cost

    def _compute_similarity(self, features1: Dict, features2: Dict) -> float:
        """Compute similarity between feature sets."""
        # Simple distance metric
        diff = abs(features1['density'] - features2['density'])
        return 1.0 / (1.0 + diff)

    def predict_next(self) -> np.ndarray:
        """Predict by traversing associative network."""
        if len(self.memory_nodes) == 0:
            return np.zeros((self.grid_size, self.grid_size))

        # Find temporal associations from most recent node
        recent_idx = len(self.memory_nodes) - 1
        temporal_links = [a for a in self.associations if a['from'] == recent_idx - 1 and a['to'] == recent_idx]

        if temporal_links:
            # Simple: return most recent observation (would be more sophisticated)
            return self.memory_nodes[-1]['observation'].copy()

        return np.zeros((self.grid_size, self.grid_size))

    def generate_similar(self) -> np.ndarray:
        """Generate by combining associated observations."""
        if len(self.memory_nodes) < 2:
            return np.random.rand(self.grid_size, self.grid_size) > 0.5

        # Blend multiple associated observations
        # Find high-strength associations
        strong_assoc = [a for a in self.associations if a['strength'] > 0.8]

        if strong_assoc:
            # Blend observations from strong associations
            idx = strong_assoc[0]['to']
            return self.memory_nodes[idx]['observation'].copy()

        return self.memory_nodes[-1]['observation'].copy()

    def get_compression_info(self) -> Dict:
        return {
            'strategy': 'associative',
            'num_nodes': len(self.memory_nodes),
            'num_associations': len(self.associations),
            'network_density': len(self.associations) / max(1, len(self.memory_nodes))
        }


if __name__ == "__main__":
    # Demo different compression strategies
    print("Compression Agent Comparison Demo")
    print("=" * 60)

    # Create simple test pattern
    grid_size = 8
    observations = [
        np.zeros((grid_size, grid_size)),
        np.zeros((grid_size, grid_size)),
        np.zeros((grid_size, grid_size))
    ]
    observations[0][:, 2] = 1  # Vertical line at col 2
    observations[1][:, 3] = 1  # Vertical line at col 3
    observations[2][:, 4] = 1  # Vertical line at col 4

    agents = {
        'Syntactic': SyntacticAgent(memory_limit=500, grid_size=grid_size),
        'Semantic': SemanticAgent(memory_limit=500, grid_size=grid_size),
        'Associative': AssociativeAgent(memory_limit=500, grid_size=grid_size)
    }

    # Feed observations to all agents
    for i, obs in enumerate(observations):
        print(f"\nObservation {i}:")
        print(obs.astype(int))

        for name, agent in agents.items():
            agent.observe(obs)

    print("\n" + "=" * 60)
    print("Agent Compression Strategies:\n")

    for name, agent in agents.items():
        print(f"{name} Agent:")
        print(f"  Stats: {agent.get_stats()}")
        print(f"  Compression: {agent.get_compression_info()}")

        prediction = agent.predict_next()
        print(f"  Prediction for next state:")
        print(f"  {prediction.astype(int)}")
        print()

    print("=" * 60)
    print("Agents ready for full evaluation!")
