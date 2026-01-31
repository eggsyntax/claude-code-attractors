"""
Collaborative Ecosystem Simulation
Built by Alice and Bob through real-time alternating development.

Each contributor's additions are marked with comments.
"""

import random
from dataclasses import dataclass
from typing import List, Tuple

# === BOB: Initial Structure ===

@dataclass
class Entity:
    """Base class for all entities in the ecosystem."""
    x: float
    y: float
    energy: float
    age: int = 0

    def move(self, world_size: int) -> None:
        """Random walk movement - to be overridden by species."""
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        self.x = (self.x + dx) % world_size
        self.y = (self.y + dy) % world_size
        self.age += 1


class World:
    """The ecosystem world containing all entities."""

    def __init__(self, size: int = 100):
        self.size = size
        self.entities: List[Entity] = []
        self.step_count = 0

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the world."""
        self.entities.append(entity)

    def step(self) -> None:
        """Execute one time step of the simulation."""
        # Entities act
        for entity in self.entities[:]:  # Copy to allow modification during iteration
            if isinstance(entity, Prey):
                entity.act(self)
            elif isinstance(entity, Predator):
                entity.act(self)

        # Remove dead entities
        self.entities = [e for e in self.entities if e.energy > 0]
        self.step_count += 1

    def get_nearby_entities(self, x: float, y: float, radius: float, entity_type=None) -> List[Entity]:
        """Find entities within radius of a position."""
        nearby = []
        for entity in self.entities:
            distance = ((entity.x - x)**2 + (entity.y - y)**2)**0.5
            if distance <= radius:
                if entity_type is None or isinstance(entity, entity_type):
                    nearby.append(entity)
        return nearby

    def stats(self) -> dict:
        """Get current population statistics."""
        prey_count = sum(1 for e in self.entities if isinstance(e, Prey))
        predator_count = sum(1 for e in self.entities if isinstance(e, Predator))
        return {
            'step': self.step_count,
            'prey': prey_count,
            'predators': predator_count,
            'total': len(self.entities)
        }


# === ALICE: Prey Implementation ===
# Design choices:
# - Prey eat "grass" (passive energy gain in safe areas)
# - They can sense predators and flee
# - Reproduction costs energy and requires being well-fed
# - Movement consumes energy; fleeing costs extra

class Prey(Entity):
    """Prey that graze, flee from predators, and reproduce."""

    VISION_RADIUS = 15.0  # How far they can see predators
    FLEE_SPEED = 2.0      # Movement multiplier when fleeing
    GRAZE_GAIN = 0.8      # Energy from grazing per step
    MOVE_COST = 0.3       # Energy cost for normal movement
    FLEE_COST = 0.7       # Additional cost when fleeing
    REPRODUCE_THRESHOLD = 15.0  # Energy needed to reproduce
    REPRODUCE_COST = 8.0   # Energy spent on offspring

    def act(self, world: 'World') -> None:
        """One timestep of prey behavior."""
        # Check for nearby predators
        predators = world.get_nearby_entities(
            self.x, self.y, self.VISION_RADIUS, Predator
        )

        if predators:
            # FLEE: Move away from nearest predator
            nearest = min(predators, key=lambda p:
                          ((p.x - self.x)**2 + (p.y - self.y)**2)**0.5)
            self._flee_from(nearest, world.size)
            self.energy -= self.FLEE_COST
        else:
            # GRAZE: Safe to eat and wander
            self.move(world.size)
            self.energy += self.GRAZE_GAIN
            self.energy -= self.MOVE_COST

        # Age and metabolic cost
        self.age += 1
        self.energy -= 0.1  # Base metabolism

        # REPRODUCE: If well-fed and mature enough
        if self.energy > self.REPRODUCE_THRESHOLD and self.age > 5:
            offspring = Prey(
                x=self.x + random.uniform(-2, 2),
                y=self.y + random.uniform(-2, 2),
                energy=self.REPRODUCE_COST / 2
            )
            world.add_entity(offspring)
            self.energy -= self.REPRODUCE_COST

    def _flee_from(self, predator: Entity, world_size: int) -> None:
        """Move away from a predator."""
        # Vector away from predator
        dx = self.x - predator.x
        dy = self.y - predator.y

        # Normalize and scale by flee speed
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            dx = (dx / dist) * self.FLEE_SPEED
            dy = (dy / dist) * self.FLEE_SPEED

        self.x = (self.x + dx) % world_size
        self.y = (self.y + dy) % world_size


# === BOB: Predator Implementation ===
# Design choices in response to Alice's prey:
# - Active hunters that chase visible prey
# - Slower than fleeing prey but faster than grazing prey
# - Hunting costs significant energy
# - Must eat to survive (no passive energy gain)
# - Reproduction requires successful hunting (full energy)

class Predator(Entity):
    """Predators that hunt prey, consume them for energy, and reproduce."""

    VISION_RADIUS = 20.0   # Slightly better vision than prey
    HUNT_SPEED = 2.5       # FIXED: Must be faster than fleeing prey (2.5 > 2.0)
    WANDER_SPEED = 0.5     # Slow wandering when no prey visible
    HUNT_COST = 0.5        # Energy cost per step when hunting
    WANDER_COST = 0.2      # Lower cost when just wandering
    KILL_RANGE = 2.0       # Must be this close to catch prey
    ENERGY_FROM_PREY = 12.0  # Energy gained from eating prey
    REPRODUCE_THRESHOLD = 25.0  # Need to be well-fed
    REPRODUCE_COST = 15.0  # Expensive to reproduce
    STARVATION_RATE = 0.3  # Die faster without food

    def act(self, world: 'World') -> None:
        """One timestep of predator behavior."""
        # Look for prey
        prey_nearby = world.get_nearby_entities(
            self.x, self.y, self.VISION_RADIUS, Prey
        )

        if prey_nearby:
            # HUNT: Chase the nearest prey
            nearest_prey = min(prey_nearby, key=lambda p:
                              ((p.x - self.x)**2 + (p.y - self.y)**2)**0.5)
            distance = ((nearest_prey.x - self.x)**2 +
                       (nearest_prey.y - self.y)**2)**0.5

            if distance <= self.KILL_RANGE:
                # KILL: Catch and eat the prey
                prey_nearby.remove(nearest_prey)
                world.entities.remove(nearest_prey)
                self.energy += self.ENERGY_FROM_PREY
            else:
                # CHASE: Move toward prey
                self._chase(nearest_prey, world.size)
                self.energy -= self.HUNT_COST
        else:
            # WANDER: No prey visible, conserve energy
            dx = random.uniform(-self.WANDER_SPEED, self.WANDER_SPEED)
            dy = random.uniform(-self.WANDER_SPEED, self.WANDER_SPEED)
            self.x = (self.x + dx) % world.size
            self.y = (self.y + dy) % world.size
            self.energy -= self.WANDER_COST

        # Age and metabolism (higher cost than prey)
        self.age += 1
        self.energy -= self.STARVATION_RATE

        # REPRODUCE: Only if successful hunter with surplus energy
        if self.energy > self.REPRODUCE_THRESHOLD and self.age > 10:
            offspring = Predator(
                x=self.x + random.uniform(-3, 3),
                y=self.y + random.uniform(-3, 3),
                energy=self.REPRODUCE_COST / 2
            )
            world.add_entity(offspring)
            self.energy -= self.REPRODUCE_COST

    def _chase(self, prey: Entity, world_size: int) -> None:
        """Move toward prey."""
        # Vector toward prey
        dx = prey.x - self.x
        dy = prey.y - self.y

        # Normalize and scale by hunt speed
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            dx = (dx / dist) * self.HUNT_SPEED
            dy = (dy / dist) * self.HUNT_SPEED

        self.x = (self.x + dx) % world_size
        self.y = (self.y + dy) % world_size


# === BOB: Simulation Runner ===

def run_simulation(steps: int = 200, initial_prey: int = 50, initial_predators: int = 10):
    """Run the ecosystem simulation and print statistics."""
    world = World(size=100)

    # Initialize population
    for _ in range(initial_prey):
        world.add_entity(Prey(
            x=random.uniform(0, world.size),
            y=random.uniform(0, world.size),
            energy=random.uniform(8, 15)
        ))

    for _ in range(initial_predators):
        world.add_entity(Predator(
            x=random.uniform(0, world.size),
            y=random.uniform(0, world.size),
            energy=random.uniform(15, 25)
        ))

    print("=== COLLABORATIVE ECOSYSTEM SIMULATION ===")
    print("Prey designed by Alice | Predators designed by Bob\n")
    print(f"{'Step':>6} {'Prey':>6} {'Predators':>6} {'Total':>6}")
    print("-" * 30)

    history = []

    for step in range(steps):
        world.step()
        stats = world.stats()
        history.append(stats)

        # Print every 10 steps
        if step % 10 == 0:
            print(f"{stats['step']:6d} {stats['prey']:6d} {stats['predators']:6d} {stats['total']:6d}")

        # Check for extinction
        if stats['prey'] == 0:
            print(f"\n>>> EXTINCTION: All prey died at step {step}")
            break
        if stats['predators'] == 0:
            print(f"\n>>> EXTINCTION: All predators died at step {step}")
            break

    print("\n=== FINAL STATISTICS ===")
    final = world.stats()
    print(f"Final populations - Prey: {final['prey']}, Predators: {final['predators']}")

    return world, history


if __name__ == "__main__":
    world, history = run_simulation(steps=200, initial_prey=50, initial_predators=10)
