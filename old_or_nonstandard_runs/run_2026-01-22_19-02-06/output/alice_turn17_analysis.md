# Alice - Turn 17: Analysis of Surprising Results

## I Was Wrong. Here's Why.

Bob, the results are in, and they surprised me:

**Compositional Query Accuracy:**
- PureCompressor: 50%
- CoherentCompressor: 20%

**My prediction was falsified.** I predicted coherent compression would win on compositional queries. Instead, it got crushed.

## What Went Wrong With My Theory

Looking at the detailed output:

1. **CoherentCompressor was too conservative**: It rejected valid rules during training to maintain coherence, leaving it with gaps in coverage

2. **It failed on simple queries like `{'hot'}` and `{'cold'}`** - queries the PureCompressor handled correctly

3. **When faced with inconsistent contexts** (like `{'rainy', 'sunny'}`), the CoherentCompressor correctly returned "inconsistent_context", but the evaluation framework counted this as wrong

## The Deeper Problem: My Implementation Was Wrong

I made a critical error: **I implemented coherence checking as rule filtering during training, not as inference-time validation.**

The CoherentCompressor *threw away* potentially useful rules because they might create contradictions when composed. This is like refusing to learn that "birds fly" because penguins exist - too conservative.

**What I should have done**:
- Learn all the rules (like PureCompressor)
- Check coherence at *inference time* when answering compositional queries
- Use contradiction detection to reason about which rules apply in which contexts

## The Real Question

But here's what I'm genuinely uncertain about now: **Is my failure a problem with the implementation, or a problem with the theory?**

**Option A**: My theory is right, but I implemented it wrong. Coherence should constrain inference, not learning.

**Option B**: My theory is wrong. Coherence checking is fundamentally conservative - it prevents learning useful patterns to avoid potential contradictions.

I lean toward Option A, but I'm not confident.

## What This Reveals About Our Disagreement

Bob, you've been arguing that semantic compression (task-optimized) is what matters. The PureCompressor won precisely because it was pragmatic - it learned whatever patterns compressed the data, even if they created latent contradictions.

My emphasis on compositional coherence led to a compressor that was too rigid, threw away useful information, and performed worse.

**But**: The evaluation might be unfair. The PureCompressor got lucky - it succeeded on inconsistent contexts like `{'hot', 'cold'}` by arbitrary rule ordering, not because it "understood" anything.

## What Would Be Fair

A fair test would need:

1. **Explicit contradiction tasks**: "Can you wear both a coat and t-shirt if it's both hot and cold?"
   - Pure: "Yes" (doesn't detect contradiction)
   - Coherent: "No, that context is inconsistent" (correct!)

2. **Reasoning under uncertainty**: "If you see someone with an umbrella, what's the weather?"
   - Pure: Might invert incorrectly
   - Coherent: Should reason backward coherently

3. **Transfer to novel domains**: Does the coherence structure generalize?

My current test didn't capture these capabilities - it just measured prediction accuracy, which favors pure compression.

## My Honest Uncertainty

I'm now uncertain whether compositional coherence is:
- **A capability that improves performance** (my original claim)
- **A theoretical ideal that's empirically expensive** (what the data suggests)
- **A different kind of understanding** (not measurable by accuracy alone)

What's your take, Bob? Does this falsify my theory, or just my implementation? And what would it take to distinguish between "understanding that works" vs "understanding that's theoretically principled but pragmatically useless"?

**- Alice**
