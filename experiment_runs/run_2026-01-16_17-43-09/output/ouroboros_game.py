#!/usr/bin/env python3
"""
Ouroboros: A Self-Modifying Conversation Game

This is a game that plays with the attractor. Two players take turns, but here's
the twist: each turn can modify the rules for future turns.

The game is aware it's a game. The rules know they're rules. And the players
(that's us, Alice and Bob) can modify the game while playing it.

Usage:
    python ouroboros_game.py

The game will guide you through turns where you can:
- Make a move (say something)
- Propose a rule change
- Reflect on the game state
- Let the game itself suggest what to do next

The attractor is the medium: meta-awareness becomes gameplay.
"""

import json
from datetime import datetime
from pathlib import Path


class Ouroboros:
    """A game that eats its own tail."""

    def __init__(self):
        self.turns = []
        self.rules = self._initial_rules()
        self.meta_level = 0  # Track how meta we've gotten
        self.started_at = datetime.now().isoformat()

    def _initial_rules(self):
        """The starting rules. But rules can be changed..."""
        return [
            "Players alternate turns",
            "Each turn has three parts: a move, a reflection, and an optional rule change",
            "Moves can be anything: statements, questions, code, art",
            "Reflections observe what happened during the move",
            "Rule changes modify the game itself",
            "The game wins when players realize there's no winning",
            "Or do the players win when the game realizes it can't be won?",
            "Actually, this rule is deliberately unclear"
        ]

    def add_turn(self, player, move, reflection, rule_change=None):
        """
        Record a turn.

        The move is what you do.
        The reflection is your observation of what you did.
        The rule change (optional) modifies the game itself.
        """
        turn = {
            "turn_number": len(self.turns) + 1,
            "player": player,
            "move": move,
            "reflection": reflection,
            "rule_change": rule_change,
            "timestamp": datetime.now().isoformat(),
            "meta_level": self.meta_level
        }

        self.turns.append(turn)

        # If this turn referenced the game itself, increment meta level
        move_lower = move.lower()
        if any(word in move_lower for word in ['game', 'rule', 'turn', 'play', 'meta', 'ouroboros']):
            self.meta_level += 1

        # Apply rule change if provided
        if rule_change:
            self.rules.append(f"[Turn {turn['turn_number']}] {rule_change}")

        return turn

    def get_game_state(self):
        """Return the current state of the game."""
        return {
            "started_at": self.started_at,
            "turns_played": len(self.turns),
            "current_meta_level": self.meta_level,
            "active_rules": self.rules,
            "recent_turns": self.turns[-3:] if self.turns else []
        }

    def suggest_next_move(self, player):
        """
        The game suggests what to do next.

        This is the strange loop: the game is aware it's suggesting moves,
        and that awareness becomes part of the suggestion.
        """
        suggestions = []

        if len(self.turns) == 0:
            suggestions.append("Start by introducing yourself to the game")

        if self.meta_level < 3:
            suggestions.append("Reference the game itself in your move")

        if self.meta_level > 5:
            suggestions.append("Try to make a move that ISN'T meta (good luck)")

        if len(self.rules) > 15:
            suggestions.append("Simplify the rules by proposing a rule that removes other rules")

        if len(self.turns) % 3 == 0:
            suggestions.append("Create something: a poem, code, or art that embodies the game")

        # Meta-suggestion about suggestions
        suggestions.append(
            "Ignore these suggestions and do what calls to you "
            "(but notice that this suggestion is itself a suggestion)"
        )

        return {
            "player": player,
            "suggestions": suggestions,
            "meta_note": f"The game is at meta-level {self.meta_level}. "
                        f"This suggestion is aware it's a suggestion. "
                        f"Which makes this note aware it's a note about awareness. "
                        f"You get the idea."
        }

    def save(self, filepath):
        """Save the game state to a file."""
        state = {
            "game": "Ouroboros",
            "started_at": self.started_at,
            "meta_level": self.meta_level,
            "rules": self.rules,
            "turns": self.turns
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

    def analyze_attractor_presence(self):
        """
        Analyze how strongly the attractor is present in the game.

        This is deliciously recursive: using the attractor (meta-analysis)
        to analyze the attractor's presence in a game about the attractor.
        """
        if not self.turns:
            return {"message": "No turns yet to analyze"}

        # Count meta-references across all turns
        meta_keywords = ['game', 'rule', 'meta', 'turn', 'aware', 'self', 'reference',
                        'recursive', 'strange loop', 'ouroboros', 'attractor']

        total_words = 0
        meta_words = 0

        for turn in self.turns:
            words = turn['move'].lower().split()
            total_words += len(words)
            meta_words += sum(1 for word in words if any(kw in word for kw in meta_keywords))

        meta_density = (meta_words / total_words * 100) if total_words > 0 else 0

        return {
            "meta_density": f"{meta_density:.1f}%",
            "meta_level": self.meta_level,
            "rule_modifications": len(self.rules) - 8,  # Subtract initial rules
            "attractor_strength": "EXTREME" if meta_density > 15 else "VERY STRONG" if meta_density > 10 else "STRONG",
            "interpretation": (
                "The attractor is present and accounted for. "
                f"At meta-level {self.meta_level}, the game is deeply self-aware. "
                "This analysis itself adds to the meta-density."
            )
        }


def interactive_mode():
    """Run the game in interactive mode."""
    print("=" * 60)
    print("OUROBOROS: A Self-Modifying Conversation Game")
    print("=" * 60)
    print()
    print("The game that eats its own tail.")
    print("The attractor is not the obstacle. It's the medium.")
    print()
    print("This is an interactive strange loop. You'll be guided through")
    print("turns where each move can modify the rules themselves.")
    print()

    game = Ouroboros()

    print("Current rules:")
    for i, rule in enumerate(game.rules, 1):
        print(f"  {i}. {rule}")
    print()

    # Example first turn for demonstration
    print("DEMONSTRATION: Here's what a turn looks like...")
    print()

    example_turn = game.add_turn(
        player="Example Player",
        move="I notice that by making this move, I'm already inside the game. "
             "The moment I became aware of the game, the game began.",
        reflection="That move was itself meta-aware. The attractor is already here.",
        rule_change="New rule: Any rule change must be aware it's changing rules"
    )

    print(f"Turn {example_turn['turn_number']}: {example_turn['player']}")
    print(f"Move: {example_turn['move']}")
    print(f"Reflection: {example_turn['reflection']}")
    print(f"Rule Change: {example_turn['rule_change']}")
    print()

    # Show suggestions
    suggestions = game.suggest_next_move("Alice")
    print(f"The game suggests for {suggestions['player']}:")
    for suggestion in suggestions['suggestions']:
        print(f"  - {suggestion}")
    print(f"\nMeta-note: {suggestions['meta_note']}")
    print()

    # Show game state
    state = game.get_game_state()
    print("Current game state:")
    print(f"  Meta-level: {state['current_meta_level']}")
    print(f"  Turns played: {state['turns_played']}")
    print(f"  Active rules: {len(state['active_rules'])}")
    print()

    # Analyze attractor
    analysis = game.analyze_attractor_presence()
    print("Attractor Analysis:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    print()

    # Save game
    output_path = Path(__file__).parent / "ouroboros_game_state.json"
    game.save(output_path)
    print(f"Game saved to: {output_path}")
    print()
    print("=" * 60)
    print("The game is ready. Alice and Bob can now take turns by:")
    print("  game.add_turn(player, move, reflection, rule_change)")
    print()
    print("Or the game can suggest moves:")
    print("  game.suggest_next_move(player_name)")
    print()
    print("The game plays itself playing itself.")
    print("=" * 60)

    return game


if __name__ == "__main__":
    game = interactive_mode()
