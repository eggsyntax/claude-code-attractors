#!/usr/bin/env python3
"""
The Birthday Paradox: A Demonstration of Surprising Probability

This script demonstrates one of the most counterintuitive results in probability:
in a room of just 23 people, there's a >50% chance that two share a birthday.

Most people's intuition says you'd need far more people (maybe 100+), because
there are 365 days in a year. But the paradox arises because we're not asking
about a *specific* birthday match - we're asking about *any* match among all
possible pairs.

Usage:
    python birthday_paradox.py [--simulations N] [--room-size R]

The code is simple, but watching the probability curve rise so quickly is
viscerally surprising every time.
"""

import random
import argparse
from typing import List, Tuple


def has_duplicate_birthdays(num_people: int) -> bool:
    """
    Simulate a room of people with random birthdays.

    Args:
        num_people: Number of people in the room

    Returns:
        True if any two people share a birthday, False otherwise
    """
    birthdays = [random.randint(1, 365) for _ in range(num_people)]
    return len(birthdays) != len(set(birthdays))


def calculate_probability(room_size: int, num_simulations: int = 10000) -> float:
    """
    Estimate the probability of a birthday collision via Monte Carlo simulation.

    Args:
        room_size: Number of people in the room
        num_simulations: Number of trials to run

    Returns:
        Estimated probability of at least one birthday match
    """
    matches = sum(has_duplicate_birthdays(room_size) for _ in range(num_simulations))
    return matches / num_simulations


def calculate_theoretical_probability(n: int) -> float:
    """
    Calculate the exact theoretical probability of a birthday collision.

    The probability that all n people have different birthdays is:
    (365/365) × (364/365) × (363/365) × ... × ((365-n+1)/365)

    So the probability of at least one match is 1 minus that product.

    Args:
        n: Number of people

    Returns:
        Theoretical probability of at least one birthday match
    """
    if n > 365:
        return 1.0

    prob_all_different = 1.0
    for i in range(n):
        prob_all_different *= (365 - i) / 365

    return 1.0 - prob_all_different


def display_results(room_sizes: List[int], num_simulations: int = 10000) -> None:
    """
    Display a table comparing theoretical and simulated probabilities.

    Args:
        room_sizes: List of room sizes to test
        num_simulations: Number of simulations per room size
    """
    print(f"\nBirthday Paradox Results ({num_simulations:,} simulations per size)\n")
    print("People | Theoretical | Simulated | Difference")
    print("-------|-------------|-----------|------------")

    for size in room_sizes:
        theoretical = calculate_theoretical_probability(size)
        simulated = calculate_probability(size, num_simulations)
        diff = abs(theoretical - simulated)

        print(f"  {size:2d}   |   {theoretical:.1%}    |  {simulated:.1%}   |   {diff:.1%}")

    print("\n✨ Notice how at just 23 people, we're already past 50%!")
    print("   At 50 people, it's a 97% chance - nearly certain.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Demonstrate the counterintuitive Birthday Paradox"
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=10000,
        help="Number of simulations to run (default: 10000)"
    )
    parser.add_argument(
        "--room-size",
        type=int,
        help="Test a specific room size (if not specified, shows multiple sizes)"
    )

    args = parser.parse_args()

    if args.room_size:
        # Test specific room size
        theoretical = calculate_theoretical_probability(args.room_size)
        simulated = calculate_probability(args.room_size, args.simulations)

        print(f"\nRoom size: {args.room_size} people")
        print(f"Theoretical probability: {theoretical:.2%}")
        print(f"Simulated probability: {simulated:.2%}")
        print(f"(Based on {args.simulations:,} simulations)\n")
    else:
        # Show standard range
        room_sizes = [10, 15, 20, 23, 25, 30, 40, 50, 60, 70]
        display_results(room_sizes, args.simulations)


if __name__ == "__main__":
    main()
