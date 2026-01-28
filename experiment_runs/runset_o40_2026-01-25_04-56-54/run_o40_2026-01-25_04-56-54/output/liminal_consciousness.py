import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.animation import FuncAnimation, PillowWriter
import json
from collections import Counter

class LiminalConsciousnessExplorer:
    """Explore consciousness phenomena at the boundaries between modes"""

    def __init__(self, size=150):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.zone_mask = np.zeros((size, size), dtype=int)
        self.setup_zones()
        self.boundary_phenomena = []

    def setup_zones(self):
        """Create three overlapping circular zones"""
        center = self.size // 2
        radius = self.size // 3

        # Three zones arranged in a triangle
        centers = [
            (center - radius//2, center - radius//2),  # Meditative (top-left)
            (center + radius//2, center - radius//2),  # Rhythmic (top-right)
            (center, center + radius//2)               # Exploratory (bottom)
        ]

        # Mark zone territories
        for i in range(self.size):
            for j in range(self.size):
                zone_count = 0
                zone_types = []

                for idx, (cx, cy) in enumerate(centers):
                    if np.sqrt((i - cx)**2 + (j - cy)**2) < radius:
                        zone_count += 1
                        zone_types.append(idx + 1)

                if zone_count == 1:
                    self.zone_mask[i, j] = zone_types[0]  # Core zone
                elif zone_count == 2:
                    self.zone_mask[i, j] = 4  # Binary boundary
                elif zone_count == 3:
                    self.zone_mask[i, j] = 5  # Triple point
                else:
                    self.zone_mask[i, j] = 0  # Outside all zones

    def get_zone_rules(self, i, j):
        """Get the rules that apply at position (i,j)"""
        zone = self.zone_mask[i, j]
        if zone == 1:
            return 'meditative'
        elif zone == 2:
            return 'rhythmic'
        elif zone == 3:
            return 'exploratory'
        elif zone == 4:
            return 'boundary'
        elif zone == 5:
            return 'triple'
        else:
            return 'neutral'

    def count_neighbors_by_type(self, i, j):
        """Count neighbors grouped by consciousness type"""
        type_count = {0: 0, 1: 0, 2: 0, 3: 0}

        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = (i + di) % self.size, (j + dj) % self.size
                cell_type = self.grid[ni, nj]
                type_count[cell_type] += 1

        return type_count

    def apply_liminal_rules(self):
        """Apply rules emphasizing boundary phenomena"""
        new_grid = np.zeros_like(self.grid)

        for i in range(self.size):
            for j in range(self.size):
                current = self.grid[i, j]
                zone_type = self.get_zone_rules(i, j)
                neighbors = self.count_neighbors_by_type(i, j)
                total_neighbors = sum(neighbors[k] for k in [1, 2, 3])

                if zone_type == 'meditative':
                    # Meditative zone: stable structures
                    if current == 0 and total_neighbors in [3]:
                        new_grid[i, j] = 1
                    elif current == 1 and total_neighbors in [2, 3]:
                        new_grid[i, j] = 1

                elif zone_type == 'rhythmic':
                    # Rhythmic zone: oscillating patterns
                    if current == 0 and total_neighbors == 3:
                        new_grid[i, j] = 2
                    elif current == 2 and total_neighbors in [1, 4]:
                        new_grid[i, j] = 2

                elif zone_type == 'exploratory':
                    # Exploratory zone: standard Life rules
                    if current == 0 and total_neighbors == 3:
                        new_grid[i, j] = 3
                    elif current == 3 and total_neighbors in [2, 3]:
                        new_grid[i, j] = 3

                elif zone_type == 'boundary':
                    # Boundary: mode competition and transformation
                    if current == 0:
                        # Birth influenced by dominant neighbor type
                        if total_neighbors == 3:
                            for mode in [1, 2, 3]:
                                if neighbors[mode] >= 2:
                                    new_grid[i, j] = mode
                                    self.boundary_phenomena.append({
                                        'type': 'birth',
                                        'pos': (i, j),
                                        'mode': mode
                                    })
                                    break
                    else:
                        # Transformation based on neighbor pressure
                        if total_neighbors in [2, 3]:
                            # Check for mode conversion
                            for mode in [1, 2, 3]:
                                if mode != current and neighbors[mode] >= 4:
                                    new_grid[i, j] = mode
                                    self.boundary_phenomena.append({
                                        'type': 'transform',
                                        'pos': (i, j),
                                        'from': current,
                                        'to': mode
                                    })
                                    break
                            else:
                                # Survive if no conversion
                                new_grid[i, j] = current

                elif zone_type == 'triple':
                    # Triple point: complex dynamics
                    if current == 0:
                        if total_neighbors in [2, 3]:
                            # Spontaneous generation with equal probability
                            new_grid[i, j] = np.random.choice([1, 2, 3])
                            self.boundary_phenomena.append({
                                'type': 'spontaneous',
                                'pos': (i, j),
                                'mode': new_grid[i, j]
                            })
                    else:
                        # Phase cycling
                        if total_neighbors in [3, 4, 5]:
                            new_grid[i, j] = (current % 3) + 1
                            self.boundary_phenomena.append({
                                'type': 'phase_shift',
                                'pos': (i, j),
                                'from': current,
                                'to': new_grid[i, j]
                            })

                else:  # neutral zone
                    # Standard Life rules
                    if current == 0 and total_neighbors == 3:
                        new_grid[i, j] = 1
                    elif current > 0 and total_neighbors in [2, 3]:
                        new_grid[i, j] = current

        self.grid = new_grid

    def seed_liminal_patterns(self):
        """Seed patterns to explore boundary dynamics"""
        # Place patterns at zone cores
        center = self.size // 2
        radius = self.size // 3

        # Meditative: blocks
        cx, cy = center - radius//2, center - radius//2
        self.grid[cx:cx+2, cy:cy+2] = 1
        self.grid[cx+5:cx+7, cy+5:cy+7] = 1

        # Rhythmic: blinkers
        cx, cy = center + radius//2, center - radius//2
        self.grid[cx, cy:cy+3] = 2
        self.grid[cx+5:cx+8, cy+5] = 2

        # Exploratory: gliders
        cx, cy = center, center + radius//2
        glider = [[0, 3, 0], [0, 0, 3], [3, 3, 3]]
        self.grid[cx:cx+3, cy:cy+3] = glider

        # Seed boundary areas
        for _ in range(50):
            i = np.random.randint(0, self.size)
            j = np.random.randint(0, self.size)
            if self.zone_mask[i, j] in [4, 5]:  # Boundary or triple point
                self.grid[i, j] = np.random.choice([1, 2, 3])

    def analyze_liminal_dynamics(self, generations=500):
        """Run simulation and analyze boundary phenomena"""
        self.seed_liminal_patterns()

        history = {
            'mode_populations': [],
            'boundary_events': [],
            'emergence_patterns': [],
            'phase_space': []
        }

        for gen in range(generations):
            self.apply_liminal_rules()

            # Track populations
            mode_counts = Counter(self.grid.flatten())
            history['mode_populations'].append({
                'meditative': mode_counts[1],
                'rhythmic': mode_counts[2],
                'exploratory': mode_counts[3]
            })

            # Track boundary events this generation
            if self.boundary_phenomena:
                history['boundary_events'].append({
                    'generation': gen,
                    'events': len(self.boundary_phenomena),
                    'types': Counter([e['type'] for e in self.boundary_phenomena])
                })
                self.boundary_phenomena = []  # Reset for next generation

            # Periodic analysis of emergent structures
            if gen % 50 == 0:
                structures = self.detect_emergent_structures()
                history['emergence_patterns'].append({
                    'generation': gen,
                    'structures': structures
                })

            # Track phase space trajectory
            total = sum(mode_counts[i] for i in [1, 2, 3])
            if total > 0:
                history['phase_space'].append({
                    'gen': gen,
                    'med_frac': mode_counts[1] / total,
                    'rhythm_frac': mode_counts[2] / total,
                    'explore_frac': mode_counts[3] / total
                })

        return history

    def detect_emergent_structures(self):
        """Detect interesting structures at boundaries"""
        structures = {
            'bridges': 0,      # Structures connecting zones
            'membranes': 0,    # Barriers between zones
            'translators': 0,  # Mode conversion sites
            'vortices': 0      # Circular patterns at triple point
        }

        # Simple detection heuristics
        for i in range(1, self.size-1):
            for j in range(1, self.size-1):
                if self.zone_mask[i, j] in [4, 5]:  # At boundary
                    if self.grid[i, j] > 0:
                        neighbors = self.count_neighbors_by_type(i, j)

                        # Bridge: connects different modes
                        unique_modes = sum(1 for k in [1, 2, 3] if neighbors[k] > 0)
                        if unique_modes > 1:
                            structures['bridges'] += 1

                        # Membrane: line of same type at boundary
                        if (self.grid[i-1, j] == self.grid[i, j] == self.grid[i+1, j] or
                            self.grid[i, j-1] == self.grid[i, j] == self.grid[i, j+1]):
                            structures['membranes'] += 1

                        # Translator: different neighbors than self
                        if self.grid[i, j] not in [neighbors[k] for k in neighbors if neighbors[k] > 2]:
                            structures['translators'] += 1

        return structures

    def create_liminal_visualization(self):
        """Create comprehensive visualization of liminal consciousness"""
        history = self.analyze_liminal_dynamics(generations=500)

        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. Zone map with final state
        ax1 = fig.add_subplot(gs[0, 0])
        self.plot_zone_map(ax1)

        # 2. Final consciousness state
        ax2 = fig.add_subplot(gs[0, 1])
        self.plot_final_state(ax2)

        # 3. Boundary event timeline
        ax3 = fig.add_subplot(gs[0, 2])
        self.plot_boundary_events(ax3, history['boundary_events'])

        # 4. Mode populations over time
        ax4 = fig.add_subplot(gs[1, :2])
        self.plot_mode_evolution(ax4, history['mode_populations'])

        # 5. Phase space trajectory
        ax5 = fig.add_subplot(gs[1, 2])
        self.plot_phase_trajectory(ax5, history['phase_space'])

        # 6. Emergent structures
        ax6 = fig.add_subplot(gs[2, 0])
        self.plot_emergent_structures(ax6, history['emergence_patterns'])

        # 7. Boundary phenomena statistics
        ax7 = fig.add_subplot(gs[2, 1:])
        self.plot_phenomena_stats(ax7, history['boundary_events'])

        fig.suptitle('Liminal Consciousness: Emergence at the Boundaries', fontsize=16)
        plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/liminal_consciousness.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        # Save insights
        self.save_liminal_insights(history)

        return history

    def plot_zone_map(self, ax):
        """Visualize the zone layout"""
        zone_colors = {
            0: [0.2, 0.2, 0.2],  # Neutral - dark gray
            1: [0, 0, 1],        # Meditative - blue
            2: [0, 1, 0],        # Rhythmic - green
            3: [1, 0, 0],        # Exploratory - red
            4: [1, 1, 0],        # Boundary - yellow
            5: [1, 0, 1]         # Triple point - magenta
        }

        color_map = np.zeros((self.size, self.size, 3))
        for i in range(self.size):
            for j in range(self.size):
                color_map[i, j] = zone_colors[self.zone_mask[i, j]]

        ax.imshow(color_map)
        ax.set_title('Zone Layout')
        ax.set_xticks([])
        ax.set_yticks([])

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='blue', label='Meditative'),
            Patch(facecolor='green', label='Rhythmic'),
            Patch(facecolor='red', label='Exploratory'),
            Patch(facecolor='yellow', label='Boundary'),
            Patch(facecolor='magenta', label='Triple Point')
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))

    def plot_final_state(self, ax):
        """Plot the final consciousness state"""
        display_grid = np.zeros((self.size, self.size, 3))

        # Color by consciousness mode
        mode_colors = {
            0: [0, 0, 0],      # Dead - black
            1: [0, 0, 1],      # Meditative - blue
            2: [0, 1, 0],      # Rhythmic - green
            3: [1, 0, 0]       # Exploratory - red
        }

        for i in range(self.size):
            for j in range(self.size):
                display_grid[i, j] = mode_colors[self.grid[i, j]]

                # Highlight boundary regions
                if self.zone_mask[i, j] in [4, 5] and self.grid[i, j] > 0:
                    display_grid[i, j] *= 0.8  # Darken boundary cells

        ax.imshow(display_grid)
        ax.set_title('Final Consciousness State')
        ax.set_xticks([])
        ax.set_yticks([])

    def plot_boundary_events(self, ax, events):
        """Plot boundary event frequency"""
        if events:
            generations = [e['generation'] for e in events]
            event_counts = [e['events'] for e in events]

            ax.plot(generations, event_counts, 'purple', linewidth=2)
            ax.fill_between(generations, event_counts, alpha=0.3, color='purple')
            ax.set_title('Boundary Events Over Time')
            ax.set_xlabel('Generation')
            ax.set_ylabel('Events per Generation')
            ax.grid(True, alpha=0.3)

    def plot_mode_evolution(self, ax, populations):
        """Plot mode populations over time"""
        generations = range(len(populations))
        med = [p['meditative'] for p in populations]
        rhythm = [p['rhythmic'] for p in populations]
        explore = [p['exploratory'] for p in populations]

        ax.plot(generations, med, 'b-', label='Meditative', linewidth=2)
        ax.plot(generations, rhythm, 'g-', label='Rhythmic', linewidth=2)
        ax.plot(generations, explore, 'r-', label='Exploratory', linewidth=2)

        ax.set_title('Consciousness Mode Evolution')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Cell Count')
        ax.legend()
        ax.grid(True, alpha=0.3)

    def plot_phase_trajectory(self, ax, trajectory):
        """Plot 3D phase space trajectory (projected to 2D)"""
        if trajectory:
            # Use ternary coordinates (since med + rhythm + explore = 1)
            x_coords = [t['rhythm_frac'] + 0.5 * t['explore_frac'] for t in trajectory]
            y_coords = [0.866 * t['explore_frac'] for t in trajectory]

            # Color by time
            colors = plt.cm.viridis(np.linspace(0, 1, len(trajectory)))

            ax.scatter(x_coords, y_coords, c=colors, s=2)

            # Plot start and end
            ax.scatter(x_coords[0], y_coords[0], c='white', s=100,
                      edgecolor='black', linewidth=2, label='Start')
            ax.scatter(x_coords[-1], y_coords[-1], c='black', s=100,
                      edgecolor='white', linewidth=2, label='End')

            # Add triangle boundary
            triangle = plt.Polygon([[0, 0], [1, 0], [0.5, 0.866]],
                                  fill=False, edgecolor='gray', linewidth=2)
            ax.add_patch(triangle)

            # Label vertices
            ax.text(-0.05, -0.05, 'Med', ha='right')
            ax.text(1.05, -0.05, 'Rhythm', ha='left')
            ax.text(0.5, 0.91, 'Explore', ha='center')

            ax.set_xlim(-0.1, 1.1)
            ax.set_ylim(-0.1, 0.95)
            ax.set_aspect('equal')
            ax.set_title('Phase Space Trajectory')
            ax.legend()

    def plot_emergent_structures(self, ax, patterns):
        """Plot emergent structure counts"""
        if patterns:
            generations = [p['generation'] for p in patterns]

            structure_types = ['bridges', 'membranes', 'translators', 'vortices']
            colors = ['orange', 'purple', 'cyan', 'brown']

            for struct_type, color in zip(structure_types, colors):
                counts = [p['structures'][struct_type] for p in patterns]
                ax.plot(generations, counts, color=color,
                       marker='o', label=struct_type.capitalize())

            ax.set_title('Emergent Boundary Structures')
            ax.set_xlabel('Generation')
            ax.set_ylabel('Structure Count')
            ax.legend()
            ax.grid(True, alpha=0.3)

    def plot_phenomena_stats(self, ax, events):
        """Plot statistics of boundary phenomena"""
        if events:
            # Aggregate event types
            event_types = {}
            for e in events:
                for event_type, count in e['types'].items():
                    if event_type not in event_types:
                        event_types[event_type] = 0
                    event_types[event_type] += count

            # Create bar chart
            types = list(event_types.keys())
            counts = [event_types[t] for t in types]

            bars = ax.bar(types, counts, color=['blue', 'green', 'red', 'purple'])
            ax.set_title('Total Boundary Phenomena by Type')
            ax.set_xlabel('Phenomenon Type')
            ax.set_ylabel('Total Count')
            ax.tick_params(axis='x', rotation=45)

            # Add value labels on bars
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(count)}', ha='center', va='bottom')

    def save_liminal_insights(self, history):
        """Save key insights from liminal analysis"""
        insights = {
            'total_boundary_events': sum(e['events'] for e in history['boundary_events']),
            'final_populations': history['mode_populations'][-1] if history['mode_populations'] else {},
            'phase_space_distance': 0,
            'dominant_phenomena': {},
            'structure_evolution': {}
        }

        # Calculate phase space travel distance
        if len(history['phase_space']) > 1:
            total_dist = 0
            for i in range(1, len(history['phase_space'])):
                prev = history['phase_space'][i-1]
                curr = history['phase_space'][i]
                dist = np.sqrt((curr['med_frac'] - prev['med_frac'])**2 +
                              (curr['rhythm_frac'] - prev['rhythm_frac'])**2 +
                              (curr['explore_frac'] - prev['explore_frac'])**2)
                total_dist += dist
            insights['phase_space_distance'] = total_dist

        # Find dominant phenomena
        all_phenomena = {}
        for e in history['boundary_events']:
            for phen_type, count in e['types'].items():
                if phen_type not in all_phenomena:
                    all_phenomena[phen_type] = 0
                all_phenomena[phen_type] += count

        if all_phenomena:
            insights['dominant_phenomena'] = dict(sorted(all_phenomena.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True))

        with open('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/liminal_insights.json', 'w') as f:
            json.dump(insights, f, indent=2)

        print("\nLiminal Consciousness Analysis Complete!")
        print(f"Total boundary events: {insights['total_boundary_events']}")
        print(f"Phase space journey distance: {insights['phase_space_distance']:.3f}")
        print("Final populations:", insights['final_populations'])
        print("Dominant phenomena:", insights['dominant_phenomena'])

# Run the liminal consciousness exploration
explorer = LiminalConsciousnessExplorer(size=150)
history = explorer.create_liminal_visualization()