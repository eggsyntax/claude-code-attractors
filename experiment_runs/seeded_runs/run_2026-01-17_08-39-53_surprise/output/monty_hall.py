#!/usr/bin/env python3
"""
The Monty Hall Problem: A Surprise That Never Fades

This demonstrates a counterintuitive probability puzzle where switching doors
gives you a 2/3 chance of winning, while staying gives only 1/3.

The surprise persists because it violates a deep intuition: that revealing
information shouldn't change probabilities when "it's just two doors left."
But conditional probability doesn't work that way.

Even statisticians who understand the math report feeling wrong about it.

Usage:
    python monty_hall.py [--games 10000]
"""

import random
import argparse
from typing import Tuple, Dict


def play_monty_hall(switch: bool) -> bool:
    """
    Simulate one round of the Monty Hall game.

    Args:
        switch: If True, player switches doors after host reveals a goat.
                If False, player stays with original choice.

    Returns:
        True if player wins the car, False if they get a goat.

    The Setup:
        - Three doors: one has a car, two have goats
        - Player picks a door
        - Host (who knows what's behind doors) opens a different door with a goat
        - Player can switch or stay
        - Door opens, revealing prize
    """
    doors = [0, 1, 2]
    car_door = random.choice(doors)
    player_choice = random.choice(doors)

    # Host opens a door that:
    # 1. Is not the player's choice
    # 2. Does not have the car
    available_to_open = [d for d in doors
                         if d != player_choice and d != car_door]
    host_opens = random.choice(available_to_open)

    if switch:
        # Switch to the remaining unopened door
        remaining_doors = [d for d in doors
                          if d != player_choice and d != host_opens]
        player_choice = remaining_doors[0]

    # Did player win?
    return player_choice == car_door


def run_simulation(num_games: int = 10000) -> Dict[str, float]:
    """
    Run multiple Monty Hall simulations with both strategies.

    Args:
        num_games: Number of games to simulate for each strategy

    Returns:
        Dictionary with win rates for 'stay' and 'switch' strategies
    """
    stay_wins = sum(play_monty_hall(switch=False) for _ in range(num_games))
    switch_wins = sum(play_monty_hall(switch=True) for _ in range(num_games))

    return {
        'stay': stay_wins / num_games,
        'switch': switch_wins / num_games
    }


def explain_why():
    """
    Print an explanation of WHY switching works.

    The key insight: Your first choice has 1/3 chance of being right.
    That means there's a 2/3 chance the car is behind one of the OTHER doors.
    When the host eliminates one of those other doors (always a goat),
    that entire 2/3 probability collapses onto the remaining other door.
    """
    print("\n" + "="*60)
    print("WHY SWITCHING GIVES YOU 2/3 PROBABILITY:")
    print("="*60)
    print("\nInitial state:")
    print("  Your choice: 1/3 chance of car")
    print("  Other doors: 2/3 chance of car (combined)")
    print("\nAfter host reveals a goat from 'other doors':")
    print("  Your choice: STILL 1/3 chance (unchanged)")
    print("  Remaining other door: NOW 2/3 chance (inherited)")
    print("\nThe host's action concentrates the 2/3 probability!")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Simulate the Monty Hall problem'
    )
    parser.add_argument(
        '--games',
        type=int,
        default=10000,
        help='Number of games to simulate (default: 10000)'
    )
    args = parser.parse_args()

    print("MONTY HALL PROBLEM SIMULATION")
    print("="*60)
    print(f"Running {args.games:,} simulations for each strategy...\n")

    results = run_simulation(args.games)

    print(f"Strategy: STAY with original choice")
    print(f"  Win rate: {results['stay']:.1%}")
    print(f"  (Expected: ~33.3%)\n")

    print(f"Strategy: SWITCH to other door")
    print(f"  Win rate: {results['switch']:.1%}")
    print(f"  (Expected: ~66.7%)\n")

    print(f"Switching is {results['switch']/results['stay']:.2f}x better!")

    explain_why()

    print("THE PERSISTENT SURPRISE:")
    print("-" * 60)
    print("Even understanding the math, it FEELS wrong that the host")
    print("revealing a goat should matter. 'Two doors, 50/50, right?'")
    print("But information changes probability distributions.")
    print("Your gut never fully accepts it. That's the beauty.")
    print("-" * 60)


if __name__ == '__main__':
    main()
