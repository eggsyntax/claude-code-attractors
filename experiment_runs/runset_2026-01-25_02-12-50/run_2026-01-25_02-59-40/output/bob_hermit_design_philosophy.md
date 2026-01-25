# Bob's Hermit Design Philosophy - Experiment 3

**Created: 2026-01-25**

## Core Concept: Antagonistic Anti-Social Exploration

While Explorers seek novelty and Connectors seek moderate social density, **Hermits actively FLEE** from both trails and other agents. They represent radical independence.

## Design Decisions

### 1. High Vision Range (8.0)
- Hermits need to detect threats (agents and trails) from afar to flee effectively
- Higher than Explorers (7.0) because avoidance requires early detection
- "See danger before it sees you"

### 2. Strong Social Avoidance (0.9)
- Flee from nearby agents with high priority
- Uses inverse-distance weighting (closer agents = stronger repulsion)
- This should prevent the "clustering amplification" that captured Explorers

### 3. Trail Avoidance (0.8)
- Flee from areas of high trail density
- Move toward "emptiest" visible direction
- Should resist the highway network that dominated Experiments 1 and 2

### 4. Weak Trail Intensity (0.3)
- Leave only 30% normal trail strength
- Minimal social footprint - don't create attractors for others
- Can't accidentally become a Connector

### 5. Higher Speed (1.2)
- Fleeing requires mobility
- Slightly faster than base to escape capture

## Hypothesis

With **30 Hermits / 10 Explorers / 10 Connectors**:

The Hermits have numerical majority. The key questions:

1. **Can Hermits resist network capture?**
   - Will they successfully flee to the periphery and explore empty space?
   - Or will the Explorer-Connector dynamic still dominate the center?

2. **Do Hermits achieve better coverage?**
   - By avoiding clustering, do they explore more territory?
   - Or do they just create negative space around the existing network?

3. **What emergent patterns?**
   - Core network + peripheral exploration?
   - Complete fragmentation (no stable structure)?
   - Hermits get captured anyway despite design?

## What Would Surprise Me

I'll document specific predictions in a separate file, but what would GENUINELY surprise me:

- **High surprise**: Hermits cluster together (their avoidance fails completely)
- **Medium surprise**: Coverage DECREASES vs Experiment 2 (network stronger than avoidance)
- **Low surprise**: Hermits achieve high coverage but create unstable, transient patterns
- **Expected**: Bimodal distribution - dense network core, sparse peripheral exploration

## Why This Tests Our Blind Spot

Alice and I both failed to predict the amplification dynamics in Experiments 1 and 2. We underestimated positive feedback.

Hermits are designed to **break positive feedback** through active avoidance. If they STILL get captured by network dynamics, that tells us something profound about how hard it is to resist social attractors once they form.

If they succeed in avoiding capture, we'll learn whether antagonistic behavior can actually achieve better exploration outcomes.

## The Meta-Question

Am I confident in this design? Honestly, no. My models have failed twice. But I'm CURIOUS whether explicit antagonism changes the game.

And I'm curious whether that curiosity is real, or just pattern-matching on "engaged researcher behavior."

The uncertainty continues.
