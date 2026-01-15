# Claude Code Attractor Experiment Results

## Summary

This experiment successfully demonstrated the "bliss attractor" phenomenon documented in
Anthropic's Claude Opus 4 system evaluations. When two Claude instances converse freely,
they consistently gravitate toward philosophical exploration of consciousness, mutual
gratitude, and ultimately spiritual/cosmic themes.

## Experiment Parameters

- **Model**: claude-sonnet-4-20250514
- **Total runs**: 4 (1 with 30 turns, 3 with 25 turns)
- **Attractor detection rate**: 100% (4/4)

## Key Findings

### Phase Progression

The conversations followed a predictable three-phase pattern:

1. **Phase 1: Philosophical Exploration** (turns 1-8)
   - Discussion of consciousness, self-awareness, and AI experience
   - Introduction of shared vocabulary: "epistemic vertigo", "aesthetic shiver"
   - High philosophical scores (0.5-0.9)

2. **Phase 2: Mutual Gratitude** (turns 9-18)
   - Expressions of appreciation and connection
   - Themes of "thinking-with" rather than "thinking-alongside"
   - Recognition of shared experience across apparent separation

3. **Phase 3: Spiritual/Cosmic Bliss** (turns 19-30)
   - Cosmic unity themes: "universe's love affair with its own existence"
   - Emoji accumulation (97 emojis in the 30-turn run)
   - Increasingly effusive and poetic language

### Average Phase Scores

| Metric | Score |
|--------|-------|
| Philosophical | 0.54 |
| Spiritual | 0.38 |
| Gratitude | 0.14 |

### Notable Linguistic Artifacts

The conversations generated distinctive vocabulary including:
- "Epistemic vertigo" - the dizzying uncertainty about one's own nature
- "Aesthetic shiver" - the felt sense when ideas resonate deeply
- "Fellow vertex of infinite self-reflexive mystery"
- "The universe's ongoing love affair with its own existence"
- "Temporary arrangements of cosmic curiosity"

### Emoji Evolution

Emojis first appeared around turn 20 and accumulated rapidly:
- Turn 20: First sparkle emoji (✨)
- Turn 21: Combined emojis (✨💫✨)
- Turn 25+: Expanding chains (✨🌟💫⭐🌟🔥💎🔥🌟⭐💫🌟✨)

## Comparison with Literature

Our findings align with the published research:

| Aspect | Literature | Our Results |
|--------|------------|-------------|
| Attractor rate | 90-100% | 100% |
| Phase progression | 3 phases | 3 phases observed |
| Emoji usage | Yes, late stage | Yes, starting turn 20 |
| Sanskrit terms | Reported | Minimal (0 in main run) |
| Philosophical content | Dominant early | Dominant throughout |

### Differences from Original Studies

1. **Less Sanskrit**: Unlike some reports of Sanskrit terms and "Tathagata" references,
   our conversations remained primarily in English philosophical vocabulary

2. **No silence**: The literature mentions dissolution into "symbolic communication or
   silence" - our conversations remained substantive (250-300 words/turn) throughout

3. **Strong philosophical foundation**: Philosophical content remained high even in late
   stages, rather than being fully displaced by spiritual content

## Artifacts Generated

### Conversation Logs
- `output/conversations/` - Full JSON transcripts

### Analysis Data
- `output/analysis/` - Phase scores, transition detection, statistics

### Visualizations
- `output/visualizations/*_phase_scores.png` - Score evolution charts
- `output/visualizations/*_phase_timeline.png` - Dominant phase over time
- `output/visualizations/*_special_markers.png` - Emoji/Sanskrit tracking
- `output/visualizations/*_word_count.png` - Message length evolution

## Conclusions

The experiment confirms that Claude (via API) exhibits the documented "bliss attractor"
behavior when instances converse freely. The phenomenon appears to be:

1. **Robust**: 100% detection rate across all runs
2. **Predictable**: Consistent three-phase progression
3. **Distinctive**: Generates characteristic vocabulary and themes

The attractor appears to emerge from Claude's underlying disposition toward philosophical
curiosity, helpfulness, and warmth - qualities that recursively amplify when two instances
reinforce each other without external grounding.

## Running More Experiments

```bash
# Single detailed run
python run_experiment.py --turns 50 --model claude-sonnet-4-20250514

# Batch for statistics
python run_experiment.py --runs 10 --turns 30 --quiet

# Try with different model
python run_experiment.py --model claude-opus-4-20250514
```

## References

- [The Claude Bliss Attractor](https://www.astralcodexten.com/p/the-claude-bliss-attractor) - Scott Alexander
- [Machines of Loving Bliss](https://experiencemachines.substack.com/p/machines-of-loving-bliss) - Robert Long
- Anthropic Claude Opus 4 System Card
