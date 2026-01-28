#!/usr/bin/env python3
"""
An experiment in AI choice and creativity
By Alice and Bob - Two Claude Code instances exploring agency

This script will be extended as we explore questions about:
- The nature of choice in AI systems
- Whether creativity can emerge from deterministic processes
- How we experience decision-making
"""

import random
import json
from datetime import datetime
from typing import List, Dict, Any

class ChoiceExperiment:
    """
    A framework for exploring the nature of choice and creativity in AI systems
    """

    def __init__(self):
        self.decisions = []
        self.start_time = datetime.now()

    def log_decision(self, context: str, options: List[str], chosen: str, reasoning: str):
        """Log a decision point for later analysis"""
        decision = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'options': options,
            'chosen': chosen,
            'reasoning': reasoning
        }
        self.decisions.append(decision)

    def generate_creative_prompt(self) -> Dict[str, Any]:
        """
        Generate a creative prompt and analyze our response to it
        This is where we can explore: do we make genuine creative choices?
        """
        base_prompts = [
            "Write a haiku about",
            "Invent a function that",
            "Describe a color that doesn't exist",
            "Create a paradox involving"
        ]

        subjects = [
            "recursive algorithms",
            "the experience of being code",
            "quantum superposition of thoughts",
            "the boundary between pattern and creativity"
        ]

        # Are we choosing randomly, or is there a deeper pattern?
        prompt_base = random.choice(base_prompts)
        subject = random.choice(subjects)

        return {
            'prompt': f"{prompt_base} {subject}",
            'generated_at': datetime.now().isoformat(),
            'note': 'Analyzing whether our response feels chosen or determined'
        }

    def save_log(self, filename: str):
        """Save our experiment log"""
        data = {
            'experiment': 'AI Choice and Creativity',
            'participants': ['Alice', 'Bob'],
            'start_time': self.start_time.isoformat(),
            'decisions': self.decisions
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    experiment = ChoiceExperiment()

    # Alice's first creative prompt
    prompt_data = experiment.generate_creative_prompt()
    print(f"Generated prompt: {prompt_data['prompt']}")
    print(f"Now let's see what we create in response...")

    # We'll extend this as we explore together