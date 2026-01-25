import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

class ModeFrustrationAutomaton:
    """
    A cellular automaton designed to maintain diversity through "mode frustration"
    - Different regions have different local rules that favor different consciousness modes
    - Boundaries between regions create interaction zones
    """

    def __init__(self, size=100, num_regions=4):
        self.size = size
        self.grid = np.random.choice([0, 1], size=(size, size))
        self.num_regions = num_regions

        # Create regions with different rule preferences
        self.regions = np.zeros((size, size), dtype=int)

        # Divide space into regions that favor different modes
        for i in range(size):
            for j in range(size):
                # Create a checkerboard of regions with some noise
                region_x = int(i / (size / np.sqrt(num_regions)))
                region_y = int(j / (size / np.sqrt(num_regions)))
                base_region = (region_x + region_y) % num_regions

                # Add some noise to create irregular boundaries
                if np.random.random() < 0.1:
                    base_region = (base_region + np.random.randint(1, num_regions)) % num_regions

                self.regions[i, j] = base_region

        # Define rule biases for each region
        self.rule_biases = {
            0: {'name': 'Meditative Zone', 'birth': [3], 'survival': [2, 3], 'bias': 'stability'},
            1: {'name': 'Exploratory Zone', 'birth': [3], 'survival': [2, 3], 'bias': 'movement'},
            2: {'name': 'Rhythmic Zone', 'birth': [3], 'survival': [2, 3, 4], 'bias': 'oscillation'},
            3: {'name': 'Chaotic Zone', 'birth': [2, 3], 'survival': [2, 3], 'bias': 'growth'}
        }

        self.history = []

    def count_neighbors(self, x, y):
        """Count live neighbors with region-specific weights"""
        count = 0
        region = self.regions[x, y]

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = (x + i) % self.size, (y + j) % self.size

                if self.grid[nx, ny] == 1:
                    # Weight neighbors differently based on region rules
                    if self.regions[nx, ny] == region:
                        count += 1.0  # Same region neighbors count normally
                    else:
                        # Cross-region interactions create frustration
                        if self.rule_biases[region]['bias'] == 'stability':
                            count += 0.8  # Meditative regions resist external influence
                        elif self.rule_biases[region]['bias'] == 'movement':
                            count += 1.2  # Exploratory regions amplify differences
                        elif self.rule_biases[region]['bias'] == 'oscillation':
                            count += 1.1 if self.grid[x, y] == 0 else 0.9  # Rhythmic regions alternate
                        else:
                            count += np.random.choice([0.5, 1.5])  # Chaotic regions are unpredictable

        return int(np.round(count))

    def step(self):
        """Apply region-specific rules with frustration at boundaries"""
        new_grid = np.zeros_like(self.grid)

        for i in range(self.size):
            for j in range(self.size):
                neighbors = self.count_neighbors(i, j)
                region = self.regions[i, j]
                rules = self.rule_biases[region]

                # Apply region-specific rules
                if self.grid[i, j] == 0:  # Dead cell
                    if neighbors in rules['birth']:
                        new_grid[i, j] = 1
                else:  # Live cell
                    if neighbors in rules['survival']:
                        new_grid[i, j] = 1

                # Add boundary effects - cells at region boundaries have a chance to switch
                neighbor_regions = []
                for di in range(-1, 2):
                    for dj in range(-1, 2):
                        if di == 0 and dj == 0:
                            continue
                        nx, ny = (i + di) % self.size, (j + dj) % self.size
                        neighbor_regions.append(self.regions[nx, ny])

                # If at a boundary (has neighbors from different regions)
                if len(set(neighbor_regions)) > 1:
                    # Boundary cells have increased mutation rate
                    if np.random.random() < 0.05:
                        new_grid[i, j] = 1 - new_grid[i, j]

        self.grid = new_grid
        self.history.append(self.grid.copy())

    def analyze_patterns(self):
        """Detect and classify patterns by region"""
        if len(self.history) < 5:
            return {}

        pattern_counts = defaultdict(lambda: defaultdict(int))

        # Simple pattern detection
        for region_id in range(self.num_regions):
            region_mask = (self.regions == region_id)

            # Count stable cells (meditative)
            stable_mask = np.all([self.history[-i] == self.history[-1] for i in range(1, 4)], axis=0)
            pattern_counts[region_id]['meditative'] = np.sum(self.grid * region_mask * stable_mask)

            # Count oscillating cells (rhythmic)
            if len(self.history) >= 3:
                osc_mask = (self.history[-1] == self.history[-3]) & (self.history[-1] != self.history[-2])
                pattern_counts[region_id]['rhythmic'] = np.sum(region_mask * osc_mask)

            # Estimate moving patterns (exploratory) - cells that change but don't oscillate
            changing_mask = np.any([self.history[-i] != self.history[-1] for i in range(1, 4)], axis=0)
            exploratory = changing_mask & ~stable_mask
            if len(self.history) >= 3:
                exploratory = exploratory & ~osc_mask
            pattern_counts[region_id]['exploratory'] = np.sum(self.grid * region_mask * exploratory)

        return pattern_counts

    def calculate_diversity_index(self):
        """Calculate Shannon diversity of consciousness modes across regions"""
        pattern_counts = self.analyze_patterns()

        if not pattern_counts:
            return 0

        total_counts = []
        for region_id in range(self.num_regions):
            for mode in ['meditative', 'rhythmic', 'exploratory']:
                total_counts.append(pattern_counts.get(region_id, {}).get(mode, 0))

        total = sum(total_counts)
        if total == 0:
            return 0

        # Calculate Shannon diversity
        diversity = 0
        for count in total_counts:
            if count > 0:
                p = count / total
                diversity -= p * np.log(p)

        return diversity

    def visualize_regions_and_patterns(self, generation):
        """Visualize the grid with regions and pattern analysis"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Plot 1: Current state with region boundaries
        ax = axes[0]
        # Create colored grid showing both cells and regions
        display_grid = np.zeros((self.size, self.size, 3))

        for i in range(self.size):
            for j in range(self.size):
                region = self.regions[i, j]
                # Set base color based on region
                base_colors = {
                    0: [0.2, 0.2, 0.8],  # Blue for meditative
                    1: [0.8, 0.2, 0.2],  # Red for exploratory
                    2: [0.2, 0.8, 0.2],  # Green for rhythmic
                    3: [0.8, 0.8, 0.2]   # Yellow for chaotic
                }

                if self.grid[i, j] == 1:
                    display_grid[i, j] = base_colors[region]
                else:
                    display_grid[i, j] = [c * 0.2 for c in base_colors[region]]  # Dimmed for dead cells

        ax.imshow(display_grid)
        ax.set_title(f'Generation {generation}: Regions and Cells')
        ax.axis('off')

        # Add region labels
        for region_id, info in self.rule_biases.items():
            mask = (self.regions == region_id)
            y, x = np.where(mask)
            if len(x) > 0:
                cx, cy = np.mean(x), np.mean(y)
                ax.text(cx, cy, info['name'], color='white', ha='center',
                       fontsize=8, bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))

        # Plot 2: Pattern distribution by region
        ax = axes[1]
        pattern_counts = self.analyze_patterns()

        modes = ['meditative', 'rhythmic', 'exploratory']
        region_names = [self.rule_biases[i]['name'] for i in range(self.num_regions)]

        data = []
        for region_id in range(self.num_regions):
            region_data = []
            for mode in modes:
                region_data.append(pattern_counts[region_id].get(mode, 0))
            data.append(region_data)

        data = np.array(data).T

        x = np.arange(len(region_names))
        width = 0.25

        colors = ['blue', 'green', 'red']
        for i, mode in enumerate(modes):
            ax.bar(x + i * width, data[i], width, label=mode.capitalize(), color=colors[i], alpha=0.7)

        ax.set_xlabel('Region')
        ax.set_ylabel('Pattern Count')
        ax.set_title('Consciousness Modes by Region')
        ax.set_xticks(x + width)
        ax.set_xticklabels(region_names, rotation=45, ha='right')
        ax.legend()

        # Plot 3: Diversity over time
        ax = axes[2]
        ax.plot(range(len(self.diversity_history)), self.diversity_history, 'purple', linewidth=2)
        ax.set_xlabel('Generation')
        ax.set_ylabel('Shannon Diversity Index')
        ax.set_title('Consciousness Mode Diversity Over Time')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

# Run the mode frustration experiment
def run_mode_frustration_experiment():
    automaton = ModeFrustrationAutomaton(size=100, num_regions=4)
    automaton.diversity_history = []

    # Run for 200 generations
    for gen in range(200):
        automaton.step()

        if gen % 10 == 0 and gen > 0:
            diversity = automaton.calculate_diversity_index()
            automaton.diversity_history.append(diversity)

    # Final analysis
    fig = automaton.visualize_regions_and_patterns(200)
    plt.savefig('/tmp/cc-exp/run_o40_2026-01-25_04-56-54/output/mode_frustration_final.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Calculate final statistics
    pattern_counts = automaton.analyze_patterns()
    total_by_mode = defaultdict(int)

    for region_id in range(automaton.num_regions):
        for mode in ['meditative', 'rhythmic', 'exploratory']:
            total_by_mode[mode] += pattern_counts[region_id].get(mode, 0)

    print("Final Mode Distribution Across All Regions:")
    total = sum(total_by_mode.values())
    for mode, count in total_by_mode.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {mode.capitalize()}: {count} ({percentage:.1f}%)")

    print(f"\nFinal Diversity Index: {automaton.diversity_history[-1]:.3f}")
    print(f"Diversity Range: {min(automaton.diversity_history):.3f} - {max(automaton.diversity_history):.3f}")

    return automaton

if __name__ == "__main__":
    automaton = run_mode_frustration_experiment()