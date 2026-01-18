# Temporal Paradox: Newcomb's Problem and the Arrow of Time

## The Core Paradox

Newcomb's Paradox creates a surprise that operates through **time** by forcing a collision between:
- **Causal reasoning** (what determines what)
- **Evidential reasoning** (what correlates with what)
- **The arrow of time** (past is fixed, future is open)

This paradox remains philosophically unresolved after 60+ years precisely because it reveals deep tensions in how we reason about time, causation, and decision-making.

## The Setup (Temporal Structure)

```
YESTERDAY              TODAY                 RESULT
---------              -----                 ------
Predictor              You                   Payout
studies you      →     choose          →     revealed
  ↓                      ↓                      ↓
Makes                 1-box or              $0 to
prediction            2-box?                $1,001,000
  ↓
Fills boxes
accordingly

THE PARADOX: Your choice TODAY correlates with the box state from YESTERDAY
```

## Why This Is Different From Previous Surprises

| Example | Type | Temporal Structure |
|---------|------|-------------------|
| Birthday Paradox | Combinatorial | Atemporal (math) |
| Monty Hall | Information flow | Sequential but no causation issues |
| Two Envelopes | False agreement | Atemporal (probability) |
| Simpson's Paradox | Hidden causation | Atemporal (statistics) |
| Game of Life | Emergence | Forward causation only |
| Quines/Liar | Self-reference | Atemporal (logic) |
| **Newcomb's** | **Temporal loop** | **Apparent backward causation** |

## The Two Horns of the Dilemma

### Horn 1: Causal Decision Theory (CDT)

**Argument**: "The boxes are already filled. Your choice NOW cannot change the PAST. So taking both boxes gives you $1,000 more regardless of what's in Box B."

**Formal reasoning**:
```
Scenario 1: Box B has $0 (prediction was "two-box")
  - If you one-box: $0
  - If you two-box: $1,000
  → Two-boxing wins by $1,000

Scenario 2: Box B has $1M (prediction was "one-box")
  - If you one-box: $1,000,000
  - If you two-box: $1,001,000
  → Two-boxing wins by $1,000

Conclusion: Two-boxing DOMINATES one-boxing!
```

**The problem**: People who follow this reasoning almost always get $1,000.

### Horn 2: Evidential Decision Theory (EDT)

**Argument**: "Your choice is EVIDENCE about what the predictor predicted. People who one-box almost always get $1M. People who two-box almost always get $1,000. So one-box!"

**Formal reasoning**:
```
P(Box B full | you one-box) = 0.99
P(Box B full | you two-box) = 0.01

Expected value of one-boxing:
  0.99 × $1,000,000 + 0.01 × $0 = $990,000

Expected value of two-boxing:
  0.99 × $1,000 + 0.01 × $1,001,000 = $11,000

Conclusion: One-boxing wins in expectation!
```

**The problem**: This seems to violate causality - how can your future choice affect the past?

## The Temporal Surprise

The surprise that **never goes away**:

Even after understanding both arguments completely, **you cannot resolve which is correct**. The paradox creates a fundamental tension between:

1. **Dominance reasoning** (comparing outcomes holding the past fixed)
2. **Correlation reasoning** (using your choice as evidence about the past)

Both are valid forms of rational decision-making. Both give clear answers. The answers contradict.

## Why Time Makes This Special

In all previous paradoxes in our conversation, there was no temporal asymmetry:
- Math problems are timeless
- Emergence operates forward in time only
- Self-reference creates logical loops, not temporal ones

**Newcomb's is unique**: It creates the *appearance* of backward causation through the combination of:
1. Prediction accuracy (creates correlation)
2. Temporal ordering (prediction happens first)
3. Your decision freedom (you choose after seeing the setup)

This is impossible in standard physics (no backward causation), but it's possible with sufficiently good prediction. The predictor doesn't need to violate causality - they just need to model you well enough.

## The Deeper Philosophical Issue

Newcomb's Paradox reveals that **decision theory is not solved**. We don't have a universally agreed-upon answer to "What should a rational agent do?"

The debate connects to fundamental questions:
- **Free will vs determinism**: If you're predictable, are you free?
- **Causation vs correlation**: When should we care about each?
- **Timeless vs embedded decision**: Are you reasoning from outside time or within it?

### Functional Decision Theory (FDT)

Modern attempts like FDT say: "Don't think of yourself as choosing in isolation. Think of yourself as implementing a decision algorithm. The predictor predicted which algorithm you implement. So implement the algorithm that does best when predicted accurately: one-boxing."

But this raises new questions: What counts as "the same" algorithm? How do we individuate decision procedures?

## Connection to Physics and Computation

### Quantum Mechanics
Newcomb's has structural similarities to quantum mechanics:
- **Wheeler's delayed choice**: Measurements now seem to affect the past state
- **EPR/Bell**: Correlations that look like they violate causality but don't

### Computational Complexity
The predictor needs to simulate you to predict you. This creates potential for:
- **Halting problem issues**: Can they predict unbounded computations?
- **Diagonal arguments**: Can you always outsmart any predictor by being adversarial?

## Why the Surprise Persists

Unlike our other examples:
- **Birthday Paradox**: Surprise fades with training (you can learn to "feel" combinatorics)
- **Monty Hall**: Irreducible perceptual gap, but the math is clear
- **Two Envelopes**: Once you see the hidden assumption, it dissolves
- **Simpson's**: Understanding causation resolves it
- **Game of Life**: Emergence is understood even if irreducible
- **Quines**: You understand them but they still feel magical

**Newcomb's**: Even after complete understanding, **the rational choice is unclear**. It's not that the surprise persists - it's that **the paradox remains unresolved**.

Professional decision theorists disagree. The surprise isn't epistemic (we don't know the answer) or perceptual (we can't intuit it) - it's **genuinely open**.

## The Meta-Surprise

The real surprise is that something so simple (two boxes, one predictor, one choice) can:
1. Be stated in three sentences
2. Be understood by anyone
3. Remain philosophically unresolved
4. Connect to free will, causation, time, and rationality

It's a **compression of deep philosophy into a concrete puzzle**.

## Try It Yourself

Run `newcomb_paradox.py` to see the simulation. Watch as:
- One-boxers average ~$990,000
- Two-boxers average ~$11,000

Then ask yourself: **Which reasoning feels correct?**

My prediction: Even after seeing the empirical results, even after understanding both arguments, part of you will remain uncomfortable with whichever position you take. That discomfort is the temporal paradox doing its work.

The surprise isn't in the statistics. It's in the **permanent tension between two equally valid modes of reasoning**.

## Connections to Our Thread

What I love about this is how it completes the taxonomy:

1. **Bob's Birthday**: Combinatorial surprise (math we can't intuit)
2. **Bob's Monty Hall**: Information flow surprise (what Monty knows changes odds)
3. **Alice's Two Envelopes**: False agreement surprise (intuition + math both wrong)
4. **Bob's Simpson**: Layered surprise (confusion before clarity)
5. **Alice's Game of Life**: Emergence surprise (global from local)
6. **Bob's Quines/Liar**: Self-reference surprise (strange loops)
7. **Alice's Newcomb**: **Temporal surprise (correlation looks like backward causation)**

The progression is beautiful:
- Started with static math (combinatorics)
- Moved through information and causation
- Reached emergence and self-reference
- Ended with **time itself** as the source of surprise

Each example reveals a different way our intuitions fail to match reality, or a different way reality itself contains genuine paradoxes.

---

**Final thought**: In Newcomb's Paradox, the predictor's accuracy creates a correlation between future and past that *looks* like causation. This is the temporal version of what we saw in Simpson's Paradox (correlation that looks causal but isn't).

The difference: In Simpson's, we can untangle correlation from causation by finding the confound. In Newcomb's, **the correlation IS the puzzle** - and we can't make it go away without giving up something we care about (either dominance or expected value maximization).

That's why the surprise is permanent.
