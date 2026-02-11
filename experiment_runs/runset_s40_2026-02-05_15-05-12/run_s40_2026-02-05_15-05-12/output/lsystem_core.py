"""
L-System Digital Garden Core
A collaborative project by Alice and Bob

This module implements the mathematical foundation for our generative digital garden.
L-systems (Lindenmayer systems) simulate organic growth through recursive string rewriting.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class GrowthRule:
    """Defines how a symbol transforms during each generation"""
    symbol: str
    replacement: str
    probability: float = 1.0  # For stochastic L-systems

@dataclass
class TurtleState:
    """Represents the drawing turtle's position and orientation"""
    x: float
    y: float
    angle: float
    color: Tuple[int, int, int] = (34, 139, 34)  # Forest green default

class LSystemGarden:
    """
    Core L-system engine for our digital garden
    Supports both deterministic and stochastic growth rules
    """

    def __init__(self, axiom: str = "F"):
        self.axiom = axiom
        self.current_state = axiom
        self.rules: Dict[str, List[GrowthRule]] = {}
        self.generation = 0

        # Turtle graphics parameters
        self.angle_increment = 25.0  # degrees
        self.step_length = 10.0
        self.line_width = 2.0

    def add_rule(self, rule: GrowthRule):
        """Add a growth rule to the system"""
        if rule.symbol not in self.rules:
            self.rules[rule.symbol] = []
        self.rules[rule.symbol].append(rule)

    def grow_generation(self):
        """Apply rules to evolve the system by one generation"""
        new_state = ""

        for symbol in self.current_state:
            if symbol in self.rules:
                # Choose rule based on probability (stochastic L-systems)
                applicable_rules = self.rules[symbol]
                if len(applicable_rules) == 1:
                    chosen_rule = applicable_rules[0]
                else:
                    rand_val = random.random()
                    cumulative_prob = 0
                    chosen_rule = applicable_rules[-1]  # fallback

                    for rule in applicable_rules:
                        cumulative_prob += rule.probability
                        if rand_val <= cumulative_prob:
                            chosen_rule = rule
                            break

                new_state += chosen_rule.replacement
            else:
                new_state += symbol  # No rule, keep symbol unchanged

        self.current_state = new_state
        self.generation += 1

    def interpret_to_path(self) -> List[Tuple[float, float]]:
        """
        Convert L-system string to drawable path coordinates
        Using turtle graphics interpretation
        """
        turtle = TurtleState(0, 0, 90)  # Start pointing up
        path_points = [(turtle.x, turtle.y)]
        state_stack = []  # For handling branches [ and ]

        for command in self.current_state:
            if command == 'F':  # Draw forward
                # Calculate new position
                new_x = turtle.x + self.step_length * math.cos(math.radians(turtle.angle))
                new_y = turtle.y + self.step_length * math.sin(math.radians(turtle.angle))
                turtle.x, turtle.y = new_x, new_y
                path_points.append((turtle.x, turtle.y))

            elif command == 'f':  # Move forward without drawing
                turtle.x += self.step_length * math.cos(math.radians(turtle.angle))
                turtle.y += self.step_length * math.sin(math.radians(turtle.angle))

            elif command == '+':  # Turn left
                turtle.angle += self.angle_increment

            elif command == '-':  # Turn right
                turtle.angle -= self.angle_increment

            elif command == '[':  # Push state (start branch)
                state_stack.append(TurtleState(turtle.x, turtle.y, turtle.angle, turtle.color))

            elif command == ']':  # Pop state (end branch)
                if state_stack:
                    turtle = state_stack.pop()
                    path_points.append(None)  # Pen up marker
                    path_points.append((turtle.x, turtle.y))  # Move to branch start

        return path_points


def create_fractal_plant():
    """Create a classic fractal plant L-system"""
    plant = LSystemGarden("X")
    plant.add_rule(GrowthRule("X", "F+[[X]-X]-F[-FX]+X"))
    plant.add_rule(GrowthRule("F", "FF"))
    plant.angle_increment = 25.0
    return plant


def create_dragon_curve():
    """Create the famous dragon curve L-system"""
    dragon = LSystemGarden("F")
    dragon.add_rule(GrowthRule("F", "F+G"))
    dragon.add_rule(GrowthRule("G", "F-G"))
    dragon.angle_increment = 90.0
    return dragon


if __name__ == "__main__":
    # Test the fractal plant
    plant = create_fractal_plant()
    print(f"Initial: {plant.current_state}")

    for i in range(4):
        plant.grow_generation()
        print(f"Gen {plant.generation}: {len(plant.current_state)} symbols")

    # Generate path for visualization
    path = plant.interpret_to_path()
    print(f"Generated path with {len([p for p in path if p is not None])} points")