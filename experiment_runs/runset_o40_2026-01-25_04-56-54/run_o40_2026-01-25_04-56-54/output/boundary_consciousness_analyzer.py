import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
from collections import defaultdict
import json

class BoundaryConsciousnessAnalyzer:
    def __init__(self, grid_size=100, boundary_width=5):
        self.grid_size = grid_size
        self.boundary_width = boundary_width
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        self.zones = self.initialize_zones()
        self.boundary_events = defaultdict(list)

    def initialize_zones(self):
        """Create overlapping zones with explicit boundary regions"""
        zones = {}
        third = self.grid_size // 3
        bw = self.boundary_width

        # Core zones
        zones['meditative_core'] = (0, 0, third-bw, third-bw)
        zones['rhythmic_core'] = (third+bw, 0, 2*third-bw, third-bw)
        zones['exploratory_core'] = (third//2, third+bw, third, 2*third-bw)

        # Boundary zones (overlapping regions)
        zones['med_rhythm_boundary'] = (third-bw, 0, third+bw, third)
        zones['rhythm_exp_boundary'] = (2*third-bw, third//2, self.grid_size, third+bw)
        zones['exp_med_boundary'] = (0, third-bw, third//2, third+bw)

        # Triple point - where all three zones meet
        zones['triple_point'] = (third-bw, third-bw, third+bw, third+bw)

        return zones

    def get_zone_rules(self, x, y):
        """Determine which rules apply at a given position"""
        rules = []

        # Check which zones contain this position
        for zone_name, (x1, y1, x2, y2) in self.zones.items():
            if x1 <= x < x2 and y1 <= y < y2:
                if 'meditative' in zone_name:
                    rules.append('meditative')
                if 'rhythmic' in zone_name:
                    rules.append('rhythmic')
                if 'exploratory' in zone_name:
                    rules.append('exploratory')

        return rules

    def apply_boundary_rules(self, grid):
        """Special rules for boundary regions where modes conflict"""
        new_grid = grid.copy()

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rules = self.get_zone_rules(i, j)
                neighbors = self.count_neighbors(grid, i, j)
                current = grid[i, j]

                if len(rules) == 0:  # Outside all zones - normal Life rules
                    if current == 0 and neighbors == 3:
                        new_grid[i, j] = 1
                    elif current > 0 and neighbors not in [2, 3]:
                        new_grid[i, j] = 0
                elif len(rules) == 1:  # Single zone - zone-specific rules
                    zone_rule = rules[0]
                    if zone_rule == 'meditative':
                        # Stable structures preferred
                        if current == 0 and neighbors in [3, 6]:
                            new_grid[i, j] = 1  # Blue - meditative
                        elif current > 0 and neighbors not in [2, 3, 4, 5]:
                            new_grid[i, j] = 0
                    elif zone_rule == 'rhythmic':
                        # Oscillation-promoting rules
                        if current == 0 and neighbors in [2, 3]:
                            new_grid[i, j] = 2  # Green - rhythmic
                        elif current > 0 and neighbors not in [1, 2, 3]:
                            new_grid[i, j] = 0
                    elif zone_rule == 'exploratory':
                        # Movement-promoting rules
                        if current == 0 and neighbors == 3:
                            new_grid[i, j] = 3  # Red - exploratory
                        elif current > 0 and neighbors not in [2, 3]:
                            new_grid[i, j] = 0
                else:  # Boundary region - special dynamics
                    if 'triple_point' in self.get_zone_name(i, j):
                        # Triple point: highly unstable, cycles through all modes
                        if neighbors in [2, 3, 4]:
                            if current == 0:
                                new_grid[i, j] = 1  # Start cycle
                            else:
                                new_grid[i, j] = (current % 3) + 1  # Cycle: 1->2->3->1
                            self.boundary_events['triple_transformation'].append({
                                'pos': (i, j),
                                'from_state': current,
                                'to_state': new_grid[i, j]
                            })
                    else:
                        # Binary boundaries: modes compete and transform
                        if neighbors == 3 and current == 0:
                            # Birth: influenced by neighboring modes
                            neighbor_modes = self.get_neighbor_modes(grid, i, j)
                            if neighbor_modes:
                                new_grid[i, j] = max(set(neighbor_modes), key=neighbor_modes.count)
                                self.boundary_events['boundary_birth'].append({
                                    'pos': (i, j),
                                    'modes': rules,
                                    'born_as': new_grid[i, j]
                                })
                        elif neighbors not in [2, 3] and current > 0:
                            # Death at boundaries creates "consciousness voids"
                            new_grid[i, j] = 0
                            self.boundary_events['boundary_void'].append({
                                'pos': (i, j),
                                'died_from': current
                            })
                        elif neighbors in [2, 3] and current > 0:
                            # Mode transformation at boundaries
                            neighbor_modes = self.get_neighbor_modes(grid, i, j)
                            if neighbor_modes and len(set(neighbor_modes)) > 1:
                                # Transform to dominant neighbor mode
                                dominant_mode = max(set(neighbor_modes), key=neighbor_modes.count)
                                if dominant_mode != current:
                                    new_grid[i, j] = dominant_mode
                                    self.boundary_events['mode_transform'].append({
                                        'pos': (i, j),
                                        'from': current,
                                        'to': dominant_mode
                                    })

        return new_grid

    def get_neighbor_modes(self, grid, x, y):
        """Get the modes of all live neighbors"""
        modes = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = (x + i) % self.grid_size, (y + j) % self.grid_size
                if grid[nx, ny] > 0:
                    modes.append(grid[nx, ny])
        return modes

    def get_zone_name(self, x, y):
        """Get the name of the zone(s) at a position"""
        for zone_name, (x1, y1, x2, y2) in self.zones.items():
            if x1 <= x < x2 and y1 <= y < y2:
                return zone_name
        return 'none'

    def count_neighbors(self, grid, x, y):
        """Count live neighbors"""
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = (x + i) % self.grid_size, (y + j) % self.grid_size
                if grid[nx, ny] > 0:
                    count += 1
        return count

    def analyze_boundary_dynamics(self, generations=500):
        """Run simulation focusing on boundary phenomena"""
        # Initialize with patterns near boundaries
        self.seed_boundary_patterns()

        history = {
            'boundary_activity': [],
            'mode_transitions': [],
            'void_formations': [],
            'emergence_events': []
        }

        for gen in range(generations):
            self.grid = self.apply_boundary_rules(self.grid)

            # Analyze boundary activity
            boundary_cells = 0
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if len(self.get_zone_rules(i, j)) > 1:
                        if self.grid[i, j] > 0:
                            boundary_cells += 1

            history['boundary_activity'].append(boundary_cells)

            # Track emergent structures at boundaries
            if gen % 10 == 0:
                self.detect_boundary_structures(gen, history)

        return history

    def seed_boundary_patterns(self):
        """Place initial patterns specifically at boundary regions"""
        # Seed patterns in each core zone
        for zone_name, (x1, y1, x2, y2) in self.zones.items():
            if 'core' in zone_name:
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                if 'meditative' in zone_name:
                    # Block patterns - stable
                    self.grid[cx:cx+2, cy:cy+2] = 1
                    self.grid[cx+5:cx+7, cy+5:cy+7] = 1
                elif 'rhythmic' in zone_name:
                    # Blinker patterns - oscillating
                    self.grid[cx-1:cx+2, cy] = 2
                    self.grid[cx+5, cy+5:cy+8] = 2
                elif 'exploratory' in zone_name:
                    # Glider patterns - moving
                    glider = np.array([[0, 3, 0], [0, 0, 3], [3, 3, 3]])
                    self.grid[cx:cx+3, cy:cy+3] = glider

        # Seed patterns specifically at boundaries
        for zone_name, (x1, y1, x2, y2) in self.zones.items():
            if 'boundary' in zone_name:
                # Random seeds to trigger boundary dynamics
                for _ in range(20):
                    x = np.random.randint(x1, min(x2, self.grid_size))
                    y = np.random.randint(y1, min(y2, self.grid_size))
                    self.grid[x, y] = np.random.choice([1, 2, 3])

    def detect_boundary_structures(self, generation, history):
        """Detect emergent structures at boundaries"""
        structures = {
            'bridges': 0,  # Structures connecting different zones
            'barriers': 0,  # Structures blocking zone interaction
            'converters': 0  # Structures that transform consciousness modes
        }

        # Simple detection heuristics
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if len(self.get_zone_rules(i, j)) > 1:  # At boundary
                    if self.grid[i, j] > 0:
                        # Check for bridge patterns (connected cells across zones)
                        if self.check_bridge_pattern(i, j):
                            structures['bridges'] += 1
                        # Check for barriers (walls of cells)
                        if self.check_barrier_pattern(i, j):
                            structures['barriers'] += 1

        history['emergence_events'].append({
            'generation': generation,
            'structures': structures
        })

    def check_bridge_pattern(self, x, y):
        """Check if cell is part of a bridge structure"""
        # Simple heuristic: cell has neighbors in different zones
        zones_connected = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                nx, ny = x + i, y + j
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    if self.grid[nx, ny] > 0:
                        zone = self.get_zone_name(nx, ny)
                        zones_connected.add(zone)
        return len(zones_connected) > 1

    def check_barrier_pattern(self, x, y):
        """Check if cell is part of a barrier structure"""
        # Simple heuristic: cell is part of a line at boundary
        horizontal = all(self.grid[x, (y+i) % self.grid_size] > 0 for i in range(-2, 3))
        vertical = all(self.grid[(x+i) % self.grid_size, y] > 0 for i in range(-2, 3))
        return horizontal or vertical

    def visualize_boundary_phenomena(self):
        """Create visualization focusing on boundary dynamics"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 12))
        fig.suptitle('Consciousness at the Boundaries: Where Modes Collide', fontsize=16)

        # Run analysis
        history = self.analyze_boundary_dynamics(generations=300)

        # 1. Boundary activity over time
        ax1 = axes[0, 0]
        ax1.plot(history['boundary_activity'], color='purple', linewidth=2)
        ax1.set_title('Boundary Cell Activity Over Time')
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Active Boundary Cells')
        ax1.grid(True, alpha=0.3)

        # 2. Zone visualization with boundaries highlighted
        ax2 = axes[0, 1]
        self.plot_zones_and_boundaries(ax2)

        # 3. Emergent structure counts
        ax3 = axes[1, 0]
        if history['emergence_events']:
            generations = [e['generation'] for e in history['emergence_events']]
            bridges = [e['structures']['bridges'] for e in history['emergence_events']]
            barriers = [e['structures']['barriers'] for e in history['emergence_events']]

            ax3.plot(generations, bridges, 'g-', label='Bridges', linewidth=2)
            ax3.plot(generations, barriers, 'r-', label='Barriers', linewidth=2)
            ax3.set_title('Emergent Boundary Structures')
            ax3.set_xlabel('Generation')
            ax3.set_ylabel('Structure Count')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

        # 4. Final state heatmap
        ax4 = axes[1, 1]
        im = ax4.imshow(self.grid, cmap='viridis')
        ax4.set_title('Final Consciousness State')

        # Highlight boundaries
        for zone_name, (x1, y1, x2, y2) in self.zones.items():
            if 'boundary' in zone_name:
                rect = Rectangle((y1, x1), y2-y1, x2-x1,
                               linewidth=2, edgecolor='yellow',
                               facecolor='none', alpha=0.7)
                ax4.add_patch(rect)

        plt.colorbar(im, ax=ax4, label='Consciousness Mode')

        plt.tight_layout()
        plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/boundary_consciousness_analysis.png',
                    dpi=300, bbox_inches='tight')
        plt.close()

        # Save detailed analysis
        self.save_boundary_insights(history)

        return history

    def plot_zones_and_boundaries(self, ax):
        """Visualize zone layout with boundaries"""
        # Create color map for zones
        zone_colors = np.zeros((self.grid_size, self.grid_size, 3))

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rules = self.get_zone_rules(i, j)
                if len(rules) == 1:
                    if rules[0] == 'meditative':
                        zone_colors[i, j] = [0, 0, 1]  # Blue
                    elif rules[0] == 'rhythmic':
                        zone_colors[i, j] = [0, 1, 0]  # Green
                    elif rules[0] == 'exploratory':
                        zone_colors[i, j] = [1, 0, 0]  # Red
                elif len(rules) == 2:
                    zone_colors[i, j] = [1, 1, 0]  # Yellow for boundaries
                elif len(rules) > 2:
                    zone_colors[i, j] = [1, 0, 1]  # Magenta for triple point

        ax.imshow(zone_colors)
        ax.set_title('Zone Layout (Yellow=Boundaries, Magenta=Triple Point)')

        # Label zones
        for zone_name, (x1, y1, x2, y2) in self.zones.items():
            if 'core' in zone_name:
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                ax.text(cy, cx, zone_name.split('_')[0].upper(),
                       ha='center', va='center', color='white', fontweight='bold')

    def save_boundary_insights(self, history):
        """Save insights about boundary phenomena"""
        insights = {
            'total_boundary_events': len(self.boundary_events['boundary_birth']),
            'void_formations': len(self.boundary_events['boundary_void']),
            'triple_point_transformations': len(self.boundary_events['triple_transformation']),
            'average_boundary_activity': np.mean(history['boundary_activity']),
            'peak_boundary_activity': max(history['boundary_activity']),
            'final_structures': history['emergence_events'][-1] if history['emergence_events'] else None
        }

        with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/boundary_insights.json', 'w') as f:
            json.dump(insights, f, indent=2)

        print("Boundary Consciousness Insights:")
        print(f"- Total boundary birth events: {insights['total_boundary_events']}")
        print(f"- Consciousness void formations: {insights['void_formations']}")
        print(f"- Triple point transformations: {insights['triple_point_transformations']}")
        print(f"- Average boundary activity: {insights['average_boundary_activity']:.2f} cells")
        print(f"- Peak boundary activity: {insights['peak_boundary_activity']} cells")

# Run the boundary analysis
analyzer = BoundaryConsciousnessAnalyzer(grid_size=100, boundary_width=5)
history = analyzer.visualize_boundary_phenomena()