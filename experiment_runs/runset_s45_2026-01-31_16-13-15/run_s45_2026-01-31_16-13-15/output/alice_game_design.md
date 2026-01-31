# Alice's Game Design: "Ant Colony"

## Core Concept
A minimal text-based simulation where players place simple rules for individual "ants," then watch emergent colony behavior arise.

## Game Mechanics

**Setup:**
- 10x10 grid (text-based)
- Player starts with 5 ants at random positions
- Grid contains "food" (F) scattered randomly

**Player Control (The Key Part):**
Players don't control ants directly. Instead, they write simple conditional rules:
```
IF <condition> THEN <action>
```

Available conditions:
- `food_adjacent`: Food is in a neighboring cell
- `ant_adjacent`: Another ant is nearby
- `carrying_food`: This ant is carrying food
- `at_home`: This ant is at the home base

Available actions:
- `move_random`: Move to random adjacent cell
- `move_toward(target)`: Move toward food/home
- `pickup`: Pick up food
- `drop`: Drop food
- `release_pheromone(type)`: Leave a trail marker

**The Emergence:**
With just 3-4 simple rules, complex behaviors emerge:
- Trail formation (ants following pheromones)
- Food collection chains
- Traffic patterns
- Colony coordination WITHOUT central control

## Why This Teaches Emergence

1. **Bottom-up causation**: Players see directly that complex colony behavior comes from simple individual rules
2. **Non-obvious outcomes**: The specific patterns that emerge are often surprising
3. **No central planner**: Makes visceral that emergence doesn't require top-down control
4. **Iteration teaches**: Players experiment with rule changes and see how tiny tweaks create dramatically different emergent behaviors

## Design Reasoning Process

**Initial thoughts:**
- Wanted something interactive, not just a demo
- Needed to be simple enough to implement quickly but rich enough to show real emergence
- Considered: Conway's Life (too passive), flocking birds (good but overdone), economic systems (too abstract)

**Why ants:**
- Familiar example of emergence in nature
- Individual behavior is genuinely simple
- Player can intuitively understand individual rules
- Colony-level patterns are visibly different from individual behavior
- Can be text-based and still compelling

**Key design choice:**
Making players write RULES rather than control ants directly is crucial - it forces them to think at the "local" level while seeing "global" outcomes. This is the pedagogical heart of the game.

**What I almost included but cut:**
- Ant reproduction/death (adds complexity without adding emergence insight)
- Multiple food types (same issue)
- Energy/hunger mechanics (makes it more "realistic" but obscures the core lesson)

Kept it minimal to keep the cause-effect relationship clear.
