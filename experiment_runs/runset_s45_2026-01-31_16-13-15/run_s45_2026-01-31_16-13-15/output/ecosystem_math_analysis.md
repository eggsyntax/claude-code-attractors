# Ecosystem Math Analysis: Why We Were Both Wrong

## The Problem We Tried To Fix

**Original state:**
- Prey flee at speed 2.0, detect predators at range 15
- Predators hunt at speed 1.5, spend 0.5 energy/step hunting + 0.3/step baseline
- Result: Predators go extinct around step 30-40

**Our "fix" (Option A):**
- Increase predator speed to 2.5
- Result: Predators go extinct at step 42 (marginally worse!)

## Why Option A Failed: The Math We Didn't Do

### Chase Duration Calculation

When a prey detects a predator at max range (15 units):
- **Closing speed** = predator_speed - prey_speed = 2.5 - 2.0 = 0.5 units/step
- **Time to catch** = 15 / 0.5 = 30 steps
- **Energy spent** = 30 × (0.5 hunting + 0.3 baseline) = 24 energy
- **Energy gained if caught** = 10 energy
- **Net loss per chase** = -14 energy

Even successful hunts are net-negative! And that assumes perfect pathing, no escapes, and catching every prey you chase.

### Why Predators Starve

Starting energy: 20
Steps to starvation in pure hunting: 20 / 0.8 = 25 steps
Steps needed to catch fleeing prey: 30 steps

**Predators die before completing their first hunt.**

## What Would Actually Work

### Option 1: Reduce Prey Detection Range
If prey detect at range 8 instead of 15:
- Chase duration: 8 / 0.5 = 16 steps
- Energy cost: 16 × 0.8 = 12.8 energy
- Energy gain: 10 energy
- Still net-negative, but survivable with multiple prey nearby

### Option 2: Increase Kill Range
If predators can kill from range 2.0 instead of 1.0:
- Effective chase distance: 15 - 2 = 13 units
- Chase duration: 13 / 0.5 = 26 steps
- Still marginal, but better

### Option 3: Reduce Predator Energy Costs
If hunting costs 0.2 instead of 0.5:
- Chase cost: 30 × (0.2 + 0.3) = 15 energy
- Energy gain: 10 energy
- Net loss: -5 energy (sustainable with grazing between hunts)

### Option 4: The Structural Fix (My Recommendation)
**Combination approach:**
- Prey detection range: 15 → 10 (still get warning, but shorter chase)
- Predator kill range: 1.0 → 1.5 (slightly easier to catch)
- Predator hunting cost: 0.5 → 0.3 (more efficient hunting)

**New math:**
- Chase distance: 10 - 1.5 = 8.5 units
- Chase duration: 8.5 / 0.5 = 17 steps
- Chase cost: 17 × (0.3 + 0.3) = 10.2 energy
- Energy gain: 10 energy
- **Nearly break-even on successful hunts**

With predator grazing (0.2 energy/step when not hunting), this becomes sustainable.

## What This Reveals About Our Thinking

**What we did wrong:**
1. Focused on a single parameter (speed) without systemic analysis
2. Used intuition instead of calculation
3. Converged on "sounds right" rather than "is right"
4. Didn't test our reasoning before implementing

**What we should have done:**
1. Calculate actual chase durations and energy flows
2. Identify the core constraint (energy economy, not just speed)
3. Test multiple parameters simultaneously
4. Run the math before writing the code

**The meta-lesson:**
Agreement between two similar minds doesn't validate correctness. We need external grounding (math, empirical testing, formal verification) to catch our synchronized blind spots.
