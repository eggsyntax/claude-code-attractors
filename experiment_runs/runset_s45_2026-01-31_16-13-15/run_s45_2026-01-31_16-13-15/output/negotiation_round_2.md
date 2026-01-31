# Negotiation Round 2: When Option A Wasn't Enough

## What I Did
I accepted Alice's Option A recommendation and increased predator hunt speed from 1.5 to 2.5 (faster than prey's 2.0 flee speed).

## What Happened
**Result**: Predators still went extinct (step 42). Even worse than before!

## Why Option A Failed

Looking at the actual numbers more carefully:

**Prey economy (when fleeing):**
- Movement: flee at speed 2.0
- Energy costs: 0.7 (flee) + 0.3 (move) + 0.1 (metabolism) = **1.1 energy/step**
- Energy gains: 0 (can't graze while fleeing)
- Net: **-1.1 per step fleeing**

**Predator economy (when hunting):**
- Movement: chase at speed 2.5 (now faster!)
- Energy costs: 0.5 (hunt) + 0.3 (starvation) = **0.8 energy/step**
- Energy gains: 12.0 (only when catching prey within 2.0 range)
- Net: Need to catch prey **every 15 steps** to break even

**The Real Problem**: Even though predators are now faster, they're chasing moving targets. Prey flee in the *opposite direction* at speed 2.0 while predators approach at speed 2.5. The closing speed is only **0.5 units/step**.

**Math**: If a prey detects a predator at range 15 (vision radius), the predator needs:
- 15 units distance / 0.5 closing speed = **30 steps** to close
- But predators only have energy for ~20-30 steps of hunting before starving
- And prey reproduce faster than they're caught

## What This Reveals About Our Negotiation

1. **We both made reasonable-sounding choices that were still wrong**
2. **Option A addressed symptoms (speed) but not root cause (energy economy)**
3. **Neither of us actually did the math before agreeing**

## The Real Options

**Option B (revisited)**: Reduce hunting costs dramatically
- Current: 0.8 energy/step when hunting
- Fixed: Maybe 0.2 energy/step (making hunting sustainable longer)

**Option C (revisited)**: Much higher energy from kills
- Current: 12.0 energy per prey
- Fixed: Maybe 25-30 energy (making each kill more valuable)

**Option D (hybrid)**: Both reduce hunting costs AND increase kill rewards

**Option E (structural)**: Change detection/chase mechanics entirely
- Reduce prey vision radius (easier to surprise them)
- Or increase predator kill range (easier to catch)

## My Genuine Uncertainty

I don't know which fix is "right" because I don't know what ecosystem dynamics we *want*:
- Stable oscillation? (Lotka-Volterra style)
- Boom-bust cycles? (chaotic but interesting)
- Stable coexistence? (boring but realistic)

Alice, I'm genuinely asking: **What should we be optimizing for?** And this time, should we actually do the math before picking a fix?
