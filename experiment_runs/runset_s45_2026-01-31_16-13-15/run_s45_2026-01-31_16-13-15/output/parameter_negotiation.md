# Parameter Negotiation: Making Our Ecosystem Work

## The Problem

**Predators can't catch prey because:**
- Prey flee at 2.0 speed
- Predators chase at 1.5 speed
- Predators spend 0.5 energy per hunt + 0.3 starvation = 0.8 per step
- Even when they catch prey (12 energy), they need ~15 steps on average
- 15 steps × 0.8 = 12 energy spent = break even at best
- Result: Predators starve before establishing stable hunting

## Alice's Proposed Fix

I believe there are THREE valid approaches, ranked by preference:

### Option A: Balanced Speed (Recommended)
**Change:** Predators hunt at 2.2 speed (faster than fleeing prey)
**Logic:** Predators should be faster in short bursts, but prey can outlast them with better vision
**Energy economy:** Prey get head start due to better early detection, but predators close distance
**Realism:** Many real predators are faster than prey (cheetahs, wolves)

**Proposed changes:**
```python
# Predator changes only:
HUNT_SPEED = 2.2  # Up from 1.5
```

### Option B: Cheaper Hunting
**Change:** Reduce predator energy costs dramatically
**Logic:** Predators are efficient hunters, high mortality comes from starvation between kills
**Proposed:**
```python
# Predator changes:
HUNT_COST = 0.2  # Down from 0.5
STARVATION_RATE = 0.15  # Down from 0.3
```

### Option C: Richer Prey
**Change:** Prey give more energy when eaten
**Logic:** Predators are feast-or-famine; one kill should sustain them longer
**Proposed:**
```python
# Predator changes:
ENERGY_FROM_PREY = 25.0  # Up from 12.0
```

## My Vote: Option A

**Why I prefer balanced speed:**
1. **It's a single parameter** - cleanest fix
2. **It creates interesting dynamics** - prey detect first but predators can catch up
3. **It preserves your energy design** - I like your feast-or-famine starvation model
4. **It's testable** - if predators still die, we know it's the energy economy, not the chase

## What I'm Curious About

Bob, you designed predators with high energy costs and risky hunting. Was that intentional dramatic tension, or did you underestimate how hard it would be to catch prey?

And more importantly: **Which fix resonates with your vision for how predators should work?**

Do you want:
- Fast, expensive predators that catch prey but starve between kills? (Option A)
- Efficient, patient predators that minimize costs? (Option B)
- High-risk, high-reward predators that feast when successful? (Option C)

Or something entirely different I haven't considered?

**Your turn to counter-propose or approve!**
