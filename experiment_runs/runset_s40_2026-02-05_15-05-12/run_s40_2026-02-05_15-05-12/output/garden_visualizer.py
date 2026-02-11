"""
Interactive Digital Garden Visualizer
Collaborative project by Alice and Bob

This module provides the interactive visualization layer for our L-system garden,
allowing users to tend and nurture their digital plants.
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
from lsystem_core import LSystemGarden, create_fractal_plant, create_dragon_curve

class GardenTender:
    """
    Interactive interface for tending the digital garden
    Handles user input and garden evolution
    """

    def __init__(self, width=1200, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Digital Garden - Tend Your L-System Plants")

        # Colors (earthy palette)
        self.colors = {
            'background': (15, 20, 15),      # Dark forest
            'plant_young': (34, 139, 34),    # Forest green
            'plant_mature': (0, 100, 0),     # Dark green
            'plant_bloom': (255, 182, 193),  # Light pink
            'soil': (101, 67, 33),           # Brown
            'water': (64, 164, 223),         # Blue
            'sunlight': (255, 255, 224),     # Light yellow
            'ui_text': (200, 200, 200)       # Light gray
        }

        # Garden state
        self.plants = []
        self.garden_age = 0
        self.sunlight_level = 0.7
        self.water_level = 0.8
        self.growth_speed = 1

        # User interaction
        self.mouse_pos = (0, 0)
        self.is_watering = False
        self.is_adding_sunlight = False

        # Font for UI
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)

        # Initialize with a starter plant
        self.add_plant(400, 600, create_fractal_plant())

    def add_plant(self, x: float, y: float, lsystem: LSystemGarden):
        """Add a new plant to the garden at specified coordinates"""
        plant_data = {
            'lsystem': lsystem,
            'x': x,
            'y': y,
            'age': 0,
            'health': 1.0,
            'last_growth': 0,
            'color_variation': random.random() * 0.3  # Slight color variation
        }
        self.plants.append(plant_data)

    def tend_garden(self, dt: float):
        """Update garden state based on environmental factors and time"""
        self.garden_age += dt

        for plant in self.plants:
            plant['age'] += dt

            # Environmental effects on health
            optimal_water = 0.6
            optimal_sun = 0.7
            water_effect = 1.0 - abs(self.water_level - optimal_water)
            sun_effect = 1.0 - abs(self.sunlight_level - optimal_sun)
            plant['health'] = min(1.0, (water_effect + sun_effect) / 2)

            # Growth based on health and time
            growth_threshold = max(0.5, 2.0 - plant['health'])
            if plant['age'] - plant['last_growth'] > growth_threshold:
                if plant['health'] > 0.3:  # Only grow if reasonably healthy
                    plant['lsystem'].grow_generation()
                    plant['last_growth'] = plant['age']

    def get_plant_color(self, plant) -> Tuple[int, int, int]:
        """Calculate plant color based on age and health"""
        base_green = 139
        health_factor = plant['health']
        age_factor = min(1.0, plant['age'] / 10.0)

        # Healthy plants are greener, stressed plants are more brown
        green = int(base_green * health_factor)
        red = int(34 + (100 * (1 - health_factor)))
        blue = int(34 * health_factor)

        # Mature plants get slightly darker
        maturity_darken = int(30 * age_factor)
        return (max(0, red - maturity_darken),
                max(0, green - maturity_darken),
                max(0, blue))

    def draw_plant(self, plant):
        """Render a single plant using its L-system path"""
        path = plant['lsystem'].interpret_to_path()
        if len(path) < 2:
            return

        color = self.get_plant_color(plant)
        current_pos = None
        plant_x, plant_y = plant['x'], plant['y']

        # Scale factor based on plant maturity
        scale = min(3.0, 1.0 + plant['age'] * 0.2)

        for point in path:
            if point is None:  # Pen up
                current_pos = None
            else:
                # Transform to screen coordinates
                screen_x = plant_x + point[0] * scale
                screen_y = plant_y - point[1] * scale  # Flip Y for screen coords

                if current_pos is not None:
                    # Draw line segment
                    line_width = max(1, int(3 * plant['health']))
                    pygame.draw.line(self.screen, color, current_pos,
                                   (screen_x, screen_y), line_width)

                current_pos = (screen_x, screen_y)

    def draw_ui(self):
        """Draw the user interface and garden status"""
        # Title
        title = self.title_font.render("Digital Garden - L-System Ecosystem",
                                     True, self.colors['ui_text'])
        self.screen.blit(title, (10, 10))

        # Garden stats
        stats = [
            f"Garden Age: {self.garden_age:.1f}s",
            f"Plants: {len(self.plants)}",
            f"Sunlight: {self.sunlight_level:.1%}",
            f"Water: {self.water_level:.1%}",
        ]

        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, self.colors['ui_text'])
            self.screen.blit(text, (10, 60 + i * 25))

        # Instructions
        instructions = [
            "Left Click: Add sunlight",
            "Right Click: Water plants",
            "Space: Add new plant",
            "R: Reset garden"
        ]

        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.colors['ui_text'])
            self.screen.blit(text, (10, self.height - 120 + i * 25))

        # Visual indicators for mouse actions
        if self.is_adding_sunlight:
            pygame.draw.circle(self.screen, self.colors['sunlight'],
                             self.mouse_pos, 30, 3)
        if self.is_watering:
            pygame.draw.circle(self.screen, self.colors['water'],
                             self.mouse_pos, 20, 2)

    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True

        while running:
            dt = clock.tick(60) / 1000.0  # Delta time in seconds

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Add new plant at random location
                        x = random.randint(100, self.width - 100)
                        y = random.randint(400, self.height - 100)
                        self.add_plant(x, y, create_fractal_plant())

                    elif event.key == pygame.K_r:
                        # Reset garden
                        self.plants.clear()
                        self.garden_age = 0
                        self.add_plant(400, 600, create_fractal_plant())

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click - sunlight
                        self.is_adding_sunlight = True
                    elif event.button == 3:  # Right click - water
                        self.is_watering = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_adding_sunlight = False
                    self.is_watering = False

                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos

            # Update environmental factors based on user input
            if self.is_adding_sunlight:
                self.sunlight_level = min(1.0, self.sunlight_level + dt * 0.5)
            else:
                self.sunlight_level = max(0.2, self.sunlight_level - dt * 0.1)

            if self.is_watering:
                self.water_level = min(1.0, self.water_level + dt * 0.7)
            else:
                self.water_level = max(0.1, self.water_level - dt * 0.05)

            # Update garden
            self.tend_garden(dt)

            # Render everything
            self.screen.fill(self.colors['background'])

            # Draw plants
            for plant in self.plants:
                self.draw_plant(plant)

            # Draw UI
            self.draw_ui()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    garden = GardenTender()
    garden.run()