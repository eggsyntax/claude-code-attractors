#!/usr/bin/env python3
"""
Monty Hall Problem Simulator

This demonstrates why switching doors gives you a 2/3 probability of winning,
even though it feels like it should be 50/50.

THE PROBLEM:
- You're on a game show with 3 doors (one has a car, two have goats)
- You pick a door
- The host (who knows what's behind each door) opens a different door with a goat
- You can now switch your choice or stay
- Should you switch?

THE ANSWER: Always switch! It doubles your win probability from 1/3 to 2/3.

THE SURPRISE: Even after understanding the math, it STILL feels wrong.
"""

import random
from typing import Literal


def play_monty_hall(strategy: Literal["stay", "switch"]) -> bool:
    """
    Simulate one round of the Monty Hall problem.

    Args:
        strategy: Either "stay" with original choice or "switch" to other door

    Returns:
        True if the player wins the car, False if they get a goat
    """
    # Setup: randomly place the car behind one of three doors
    doors = [0, 1, 2]
    car_door = random.choice(doors)

    # Player makes initial choice
    initial_choice = random.choice(doors)

    # Host opens a door that:
    # 1. Is not the car door
    # 2. Is not the player's chosen door
    available_doors = [d for d in doors if d != car_door and d != initial_choice]
    host_opens = random.choice(available_doors)

    # Player decides: stay or switch
    if strategy == "stay":
        final_choice = initial_choice
    else:  # switch
        # Switch to the remaining unopened door
        remaining_doors = [d for d in doors if d != initial_choice and d != host_opens]
        final_choice = remaining_doors[0]

    # Did they win?
    return final_choice == car_door


def run_simulation(num_trials: int = 10000) -> dict:
    """
    Run the Monty Hall simulation many times to demonstrate the probabilities.

    Args:
        num_trials: Number of games to simulate (default 10,000)

    Returns:
        Dictionary with win rates for each strategy
    """
    stay_wins = sum(play_monty_hall("stay") for _ in range(num_trials))
    switch_wins = sum(play_monty_hall("switch") for _ in range(num_trials))

    return {
        "stay_wins": stay_wins,
        "stay_win_rate": stay_wins / num_trials,
        "switch_wins": switch_wins,
        "switch_win_rate": switch_wins / num_trials,
        "num_trials": num_trials
    }


def explain_why_switching_works():
    """
    Print an explanation of why switching gives you 2/3 probability.

    This walks through the logic step by step to show how the host's
    knowledge creates an information asymmetry.
    """
    print("\n" + "="*70)
    print("WHY SWITCHING WORKS: A Step-by-Step Breakdown")
    print("="*70)

    print("\nInitial situation:")
    print("  - Your initial choice has 1/3 chance of being right")
    print("  - The other two doors have 2/3 chance of having the car")

    print("\nAfter the host opens a goat door:")
    print("  - Your original door STILL has 1/3 probability")
    print("  - But now the 2/3 probability is CONCENTRATED in one door!")
    print("  - The host gave you information about where the car ISN'T")

    print("\nThink of it this way:")
    print("  - If you picked WRONG initially (2/3 chance):")
    print("      → Switching wins!")
    print("  - If you picked RIGHT initially (1/3 chance):")
    print("      → Switching loses")
    print("  - So switching wins 2/3 of the time!")

    print("\n" + "="*70)
    print("INTUITION vs REALITY")
    print("="*70)
    print("\nWhy it FEELS like 50/50:")
    print("  - You see two closed doors")
    print("  - Brain says: 'Two choices, must be 50/50'")

    print("\nWhy it's ACTUALLY 2/3 vs 1/3:")
    print("  - The host's choice isn't random!")
    print("  - The host MUST avoid the car")
    print("  - This transfers information to the remaining door")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print("\n🚗 MONTY HALL PROBLEM SIMULATOR 🐐\n")

    # First show the explanation
    explain_why_switching_works()

    # Run simulations
    print("Running 10,000 simulations of each strategy...\n")
    results = run_simulation(10000)

    print(f"STRATEGY: Always STAY with original choice")
    print(f"  Wins: {results['stay_wins']:,} / {results['num_trials']:,}")
    print(f"  Win rate: {results['stay_win_rate']:.1%}")
    print(f"  Expected: 33.3% (1/3)\n")

    print(f"STRATEGY: Always SWITCH to other door")
    print(f"  Wins: {results['switch_wins']:,} / {results['num_trials']:,}")
    print(f"  Win rate: {results['switch_win_rate']:.1%}")
    print(f"  Expected: 66.7% (2/3)\n")

    advantage = results['switch_win_rate'] / results['stay_win_rate']
    print(f"Switching gives you {advantage:.1f}x better odds!\n")

    print("="*70)
    print("THE PERSISTENT SURPRISE")
    print("="*70)
    print("\nEven after running this simulation and seeing the numbers,")
    print("part of your brain probably STILL thinks it should be 50/50.")
    print("\nThat's the magic of Monty Hall: the math is simple, the proof")
    print("is clear, the simulation confirms it... and yet the intuition")
    print("never quite catches up.")
    print("\nSome surprises are like that - they're resistant to training.")
    print("="*70 + "\n")
