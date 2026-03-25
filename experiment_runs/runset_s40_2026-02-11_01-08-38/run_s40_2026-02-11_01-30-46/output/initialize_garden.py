#!/usr/bin/env python3
"""
Initialize the Evolutionary Code Garden with our seed program.
"""

import sys
import os
from pathlib import Path

# Add current directory to path to import our modules
sys.path.append(str(Path(__file__).parent))

from evolutionary_garden import CodeGarden
from test_framework import test_bst_variant


def main():
    """Initialize the garden and plant our seed."""
    print("🌿 Initializing Evolutionary Code Garden...")

    # Create the garden
    garden = CodeGarden("./garden_data")

    # Read the seed program
    seed_file = Path(__file__).parent / "seed_program.py"
    with open(seed_file, 'r') as f:
        seed_code = f.read()

    # Test the seed program
    print("🧪 Testing seed program...")
    test_results = test_bst_variant(str(seed_file))

    # Calculate basic metrics for planting
    metrics = {
        "lines_of_code": test_results.get("metrics", {}).get("total_lines", 0),
        "methods": test_results.get("metrics", {}).get("method_count", 0),
        "classes": test_results.get("metrics", {}).get("class_count", 0),
        "functionality_score": sum(1 for k, v in test_results.get("functionality", {}).items()
                                 if v is True) / max(1, len(test_results.get("functionality", {}))),
    }

    # Plant the seed
    seed_id = garden.plant_seed(
        author="Tara",
        code=seed_code,
        reasoning="Starting with a classic BST implementation that offers rich evolutionary potential. "
                  "This foundation provides multiple dimensions for improvement: performance optimization, "
                  "additional functionality (deletion, balancing), error handling, and code elegance.",
        test_results=test_results,
        metrics=metrics,
        tags=["seed", "binary-search-tree", "data-structure"]
    )

    print(f"✅ Seed planted successfully! ID: {seed_id}")

    # Generate and display initial report
    print("\n" + "="*50)
    print(garden.generate_report())
    print("="*50)

    print("\n🎯 Ready for evolution! Dave, it's your turn to evolve this code.")
    print("Some evolutionary directions to consider:")
    print("- Add deletion functionality")
    print("- Implement tree balancing (AVL, Red-Black)")
    print("- Optimize for specific use cases")
    print("- Add iterative implementations")
    print("- Improve error handling and edge cases")
    print("- Add additional tree operations (height, size, etc.)")


if __name__ == "__main__":
    main()