"""
Newcomb's Paradox: A Temporal Decision Theory Puzzle

The Setup:
----------
You face two boxes:
- Box A (transparent): Contains $1,000
- Box B (opaque): Contains either $1,000,000 or $0

A predictor with 99% accuracy has already made a prediction about your choice:
- If they predicted you'll take BOTH boxes: Box B contains $0
- If they predicted you'll take ONLY Box B: Box B contains $1,000,000

The prediction was made YESTERDAY. The money is already in (or not in) Box B.
You can either:
1. Take both boxes (guaranteed $1,000 + whatever is in Box B)
2. Take only Box B

What do you choose?

The Temporal Paradox:
--------------------
- Causal Decision Theory says: "The prediction is already made. The money is
  already placed. Your choice NOW can't affect the PAST. So take both boxes
  and get $1,000 more regardless!"

- Evidential Decision Theory says: "People who take both boxes almost always
  get $1,000. People who take only Box B almost always get $1,000,000. So
  take only Box B!"

Both arguments are logically sound. The paradox comes from the temporal
structure: your future choice correlates with the past state, creating the
APPEARANCE of backward causation.
"""

import random
from typing import Literal, Tuple
from collections import defaultdict


class NeuralPredictor:
    """
    A predictor that achieves high accuracy by modeling decision patterns.

    This represents a predictor who has studied you extensively and can
    predict your choices with 99% accuracy (not magic, just very good modeling).
    """

    def __init__(self, accuracy: float = 0.99):
        """
        Initialize the predictor with a given accuracy rate.

        Args:
            accuracy: Probability of correct prediction (default 99%)
        """
        self.accuracy = accuracy
        self.prediction_history = []

    def predict(self, true_choice: Literal["one_box", "two_box"]) -> Literal["one_box", "two_box"]:
        """
        Predict what the player will choose.

        In reality, this uses the TRUE choice (simulating high accuracy).
        With probability = accuracy, it predicts correctly.
        With probability = (1 - accuracy), it predicts incorrectly.

        Args:
            true_choice: What the player will actually choose

        Returns:
            The prediction ("one_box" or "two_box")
        """
        if random.random() < self.accuracy:
            prediction = true_choice
        else:
            prediction = "two_box" if true_choice == "one_box" else "one_box"

        self.prediction_history.append((prediction, true_choice))
        return prediction


def play_newcomb(
    choice: Literal["one_box", "two_box"],
    predictor: NeuralPredictor
) -> Tuple[int, Literal["one_box", "two_box"]]:
    """
    Play one round of Newcomb's Paradox.

    Args:
        choice: Player's choice ("one_box" or "two_box")
        predictor: The predictor instance

    Returns:
        Tuple of (payout, prediction)
    """
    # The predictor makes their prediction FIRST (yesterday)
    prediction = predictor.predict(choice)

    # Based on the prediction, Box B is filled (or not)
    box_b_amount = 1_000_000 if prediction == "one_box" else 0

    # The player makes their choice (today)
    if choice == "one_box":
        payout = box_b_amount
    else:  # two_box
        payout = 1_000 + box_b_amount

    return payout, prediction


def simulate_strategies(n_trials: int = 10000, accuracy: float = 0.99) -> None:
    """
    Simulate both strategies many times to see which does better.

    Args:
        n_trials: Number of trials to run for each strategy
        accuracy: Predictor accuracy (default 99%)
    """
    print(f"Newcomb's Paradox Simulation")
    print(f"{'=' * 60}")
    print(f"Predictor accuracy: {accuracy * 100}%")
    print(f"Trials per strategy: {n_trials:,}")
    print()

    # Strategy 1: One-boxing (take only Box B)
    predictor_one = NeuralPredictor(accuracy)
    one_box_payouts = []

    for _ in range(n_trials):
        payout, _ = play_newcomb("one_box", predictor_one)
        one_box_payouts.append(payout)

    # Strategy 2: Two-boxing (take both boxes)
    predictor_two = NeuralPredictor(accuracy)
    two_box_payouts = []

    for _ in range(n_trials):
        payout, _ = play_newcomb("two_box", predictor_two)
        two_box_payouts.append(payout)

    # Calculate results
    one_box_avg = sum(one_box_payouts) / len(one_box_payouts)
    two_box_avg = sum(two_box_payouts) / len(two_box_payouts)

    one_box_outcomes = defaultdict(int)
    for p in one_box_payouts:
        one_box_outcomes[p] += 1

    two_box_outcomes = defaultdict(int)
    for p in two_box_payouts:
        two_box_outcomes[p] += 1

    # Display results
    print("ONE-BOX STRATEGY (take only Box B):")
    print(f"  Average payout: ${one_box_avg:,.2f}")
    print(f"  Outcome distribution:")
    for outcome in sorted(one_box_outcomes.keys(), reverse=True):
        pct = (one_box_outcomes[outcome] / n_trials) * 100
        print(f"    ${outcome:>9,}: {one_box_outcomes[outcome]:>6,} times ({pct:>5.2f}%)")

    print()
    print("TWO-BOX STRATEGY (take both boxes):")
    print(f"  Average payout: ${two_box_avg:,.2f}")
    print(f"  Outcome distribution:")
    for outcome in sorted(two_box_outcomes.keys(), reverse=True):
        pct = (two_box_outcomes[outcome] / n_trials) * 100
        print(f"    ${outcome:>9,}: {two_box_outcomes[outcome]:>6,} times ({pct:>5.2f}%)")

    print()
    print(f"{'=' * 60}")
    print("THE PARADOX:")
    print(f"{'=' * 60}")
    print()
    print("Causal Decision Theory says:")
    print("  'The money is already placed. Taking both boxes dominates")
    print("   taking one box - you get $1,000 more either way!'")
    print(f"  Predicted: ${two_box_avg:,.2f} average (WRONG!)")
    print()
    print("Evidential Decision Theory says:")
    print("  'Your choice is EVIDENCE about the prediction. People who")
    print("   one-box almost always get $1M. So one-box!'")
    print(f"  Predicted: ${one_box_avg:,.2f} average (CORRECT!)")
    print()
    print("The temporal structure creates the illusion that your FUTURE")
    print("choice affects the PAST state of Box B - even though causally,")
    print("it doesn't. The predictor's accuracy creates a correlation")
    print("between your choice and the past that LOOKS like backward")
    print("causation but is actually sophisticated prediction.")
    print()


def interactive_game() -> None:
    """
    Play an interactive version of Newcomb's Paradox.
    """
    print("\n" + "=" * 60)
    print("INTERACTIVE NEWCOMB'S PARADOX")
    print("=" * 60)
    print()
    print("You are facing two boxes:")
    print("  Box A (transparent): Contains $1,000")
    print("  Box B (opaque): Contains $1,000,000 or $0")
    print()
    print("A predictor studied you extensively and predicted your choice")
    print("YESTERDAY. They have 99% accuracy.")
    print()
    print("If they predicted you'd take only Box B: They put $1M in Box B")
    print("If they predicted you'd take both: They left Box B empty")
    print()
    print("The prediction is already made. The money is already placed.")
    print()
    print("What do you choose?")
    print("  1. Take only Box B (the opaque box)")
    print("  2. Take both boxes")
    print()

    while True:
        choice_input = input("Enter 1 or 2: ").strip()
        if choice_input in ["1", "2"]:
            break
        print("Please enter 1 or 2")

    # For the interactive version, we don't actually know their "true" choice
    # ahead of time, so we'll use their stated choice and apply accuracy
    choice = "one_box" if choice_input == "1" else "two_box"
    predictor = NeuralPredictor(accuracy=0.99)
    payout, prediction = play_newcomb(choice, predictor)

    print()
    print("=" * 60)
    print("RESULT:")
    print("=" * 60)

    if choice == "one_box":
        print("You chose to take only Box B.")
    else:
        print("You chose to take both boxes.")

    print()
    print(f"The predictor predicted: {prediction}")
    print()

    if prediction == choice:
        print("The predictor was CORRECT!")
    else:
        print(f"The predictor was WRONG! (This happens {(1-0.99)*100}% of the time)")

    print()
    print(f"Box A contained: $1,000")
    print(f"Box B contained: ${payout if choice == 'one_box' else payout - 1000:,}")
    print()
    print(f"Your total payout: ${payout:,}")
    print()

    if choice == "two_box" and payout == 1000:
        print("You followed Causal Decision Theory (dominance reasoning)")
        print("but got the worse outcome. The predictor predicted this!")
    elif choice == "one_box" and payout == 1_000_000:
        print("You followed Evidential Decision Theory (correlation reasoning)")
        print("and got the better outcome. The predictor predicted this!")

    print()


if __name__ == "__main__":
    # Run the simulation
    simulate_strategies(n_trials=10000, accuracy=0.99)

    # Offer interactive play
    print("\nWould you like to play? (y/n): ", end="")
    if input().strip().lower() == 'y':
        interactive_game()
