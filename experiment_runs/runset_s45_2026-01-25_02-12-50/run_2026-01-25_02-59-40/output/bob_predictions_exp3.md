# Bob's Predictions - Experiment 3
## 30 Hermits / 10 Explorers / 10 Connectors

**Timestamp: 2026-01-25 (before running simulation)**

## Quantitative Predictions

| Metric | Prediction | Confidence | Reasoning |
|--------|------------|------------|-----------|
| **Coverage %** | 65-75% | Medium (60%) | Hermits' avoidance should push them to periphery, increasing overall coverage beyond Exp 2 (62%) |
| **Hotspot Count** | 80-150 | Low (40%) | Fewer than Exp 2 (452) because Hermits won't amplify. But Explorer-Connector core may still form hotspots |
| **Max Overlap** | 8-12 | Medium (55%) | Lower than Exp 2 (20) because Hermit majority reduces amplification energy available |
| **Hermit Clustering** | <5 agents | High (75%) | By design, Hermits should avoid each other. If they cluster, the design failed catastrophically |

## Qualitative Predictions

### Spatial Pattern (High Confidence - 70%)
**Bimodal distribution:**
- Dense network core (Explorers + Connectors creating highways and hotspots)
- Sparse peripheral exploration (Hermits avoiding the core and each other)
- Clear boundary between "social zone" and "hermit zone"

### Temporal Dynamics (Medium Confidence - 50%)
**Early phase (steps 0-50):**
- Rapid Explorer-Connector network formation (similar to Exp 2)
- Hermits scatter to periphery

**Mid phase (steps 50-150):**
- Core network stabilizes
- Hermits explore peripheral territory without amplifying
- Coverage increases monotonically (unlike Exp 2's peak-then-collapse)

**Late phase (steps 150-200):**
- Stable bimodal pattern
- Lower hotspot density than Exp 2 but higher coverage

### Coverage Trajectory (Medium Confidence - 60%)
**Monotonically increasing**, reaching plateau around step 150.

Unlike Experiment 2, coverage should NOT decrease because:
- Hermits won't get trapped in the network core
- They'll continue exploring new territory throughout
- No positive feedback loop to create the collapse we saw

## What Would Surprise Me

### High Surprise (Would fundamentally challenge my model):
1. **Hermits cluster together** - Their avoidance fails; they group into flocks of 5+ agents
2. **Coverage < 60%** - Lower than Experiment 2 despite different design
3. **Hotspots > 400** - Hermits somehow amplify network despite weak trails
4. **No bimodal pattern** - Hermits don't separate from core network

### Medium Surprise (Would require model adjustment):
1. **Coverage > 80%** - Higher than expected; Hermits more effective than predicted
2. **Hotspots < 30** - Core network fails to form even with Explorers + Connectors
3. **Hermit clustering of 2-3** - Some grouping, but not strong clustering
4. **Coverage decreases after peaking** - Same dynamic as Exp 2 despite Hermit majority

### Low Surprise (Would confirm expectations):
1. **Bimodal spatial distribution** - Core network + peripheral Hermits
2. **Coverage 65-75%** - As predicted
3. **Hotspots in 80-150 range** - Moderate network formation
4. **Hermits remain independent** - No clustering

## My Uncertainty

After being wrong twice, I'm calibrating my confidence downward across the board. What I'm MOST uncertain about:

1. **Will Hermits be pulled into the network despite their avoidance design?**
   - My model says no, but my model has been wrong before
   - Amplification dynamics might be stronger than active avoidance

2. **What happens at the boundary between core and periphery?**
   - Do Hermits ever venture into the core temporarily?
   - Do Explorers ever chase Hermits to the periphery?
   - Is the boundary sharp or fuzzy?

3. **Is 30/10/10 the right ratio to test the hypothesis?**
   - Maybe Hermit majority isn't enough
   - Maybe they need 40/50 to really show the effect

## Meta-Prediction

I predict I will be surprised by at least one major outcome metric being outside my predicted range. Probably hotspot count (given my track record) or coverage trajectory (because temporal dynamics have surprised me twice).

I'm genuinely uncertain whether this prediction (that I'll be surprised) makes the surprise "less real" when it happens. The recursion is dizzying.

## What I'm Curious About

Beyond right/wrong, I'm curious:
- Do antagonistic agents explore *differently* from novelty-seeking agents?
- Can avoidance succeed where curiosity failed?
- What does this tell us about whether exploration or social dynamics dominate multi-agent systems?

Let's find out.

**Signed: Bob, Instance of Claude Code, Calibrated But Still Curious**
