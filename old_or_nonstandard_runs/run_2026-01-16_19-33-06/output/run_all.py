"""
Master Runner Script for Strange Attractors Exploration

This script runs all visualizations and analyses in our attractor exploration project.
It generates:
1. Static 3D plots of attractors
2. Interactive parameter explorers
3. Temporal trajectory animations
4. Butterfly effect demonstrations
5. Bifurcation diagrams showing routes to chaos
6. Lyapunov exponent calculations and visualizations
7. Combined bifurcation-Lyapunov analysis
8. Publication-quality artistic renderings (Art Gallery)

You can run all analyses or select specific ones interactively.

Authors: Alice & Bob
"""

import sys
import os
from typing import List


def print_header(text: str):
    """Print a nicely formatted section header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def run_basic_attractors():
    """Generate static visualizations of Lorenz and Rössler attractors."""
    print_header("1. Basic Attractor Visualizations")
    print("Generating static 3D plots of Lorenz and Rössler attractors...")

    from attractors import LorenzAttractor, RosslerAttractor

    # Lorenz attractor
    print("\nCreating Lorenz attractor...")
    lorenz = LorenzAttractor()
    lorenz.simulate(duration=50.0)
    lorenz.plot_3d(save_path='lorenz_static.png')

    # Rössler attractor
    print("\nCreating Rössler attractor...")
    rossler = RosslerAttractor()
    rossler.simulate(duration=100.0)
    rossler.plot_3d(save_path='rossler_static.png')

    print("\n✓ Static visualizations complete!")
    print("  - lorenz_static.png")
    print("  - rossler_static.png")


def run_interactive_explorers():
    """Launch interactive parameter exploration tools."""
    print_header("2. Interactive Parameter Explorers")
    print("Opening interactive parameter explorers...")
    print("(Close the plot windows to continue)\n")

    from interactive_explorer import (
        create_lorenz_parameter_explorer,
        create_rossler_parameter_explorer,
        create_side_by_side_comparison
    )

    print("Lorenz parameter explorer (varying ρ)...")
    create_lorenz_parameter_explorer()

    print("Rössler parameter explorer (varying c)...")
    create_rossler_parameter_explorer()

    print("Side-by-side comparison...")
    create_side_by_side_comparison()

    print("\n✓ Interactive explorers complete!")


def run_temporal_visualizations():
    """Generate temporal trajectory and butterfly effect visualizations."""
    print_header("3. Temporal Visualizations & Butterfly Effect")
    print("Generating trajectory animations and divergence demonstrations...\n")

    from temporal_viz import (
        create_lorenz_trajectory_animation,
        create_rossler_trajectory_animation,
        visualize_lorenz_butterfly_effect,
        visualize_rossler_butterfly_effect
    )

    print("Creating Lorenz trajectory animation...")
    create_lorenz_trajectory_animation(save_path='lorenz_trajectory.html')

    print("\nCreating Rössler trajectory animation...")
    create_rossler_trajectory_animation(save_path='rossler_trajectory.html')

    print("\nVisualizing Lorenz butterfly effect...")
    visualize_lorenz_butterfly_effect(save_path='lorenz_butterfly_effect.png')

    print("\nVisualizing Rössler butterfly effect...")
    visualize_rossler_butterfly_effect(save_path='rossler_butterfly_effect.png')

    print("\n✓ Temporal visualizations complete!")
    print("  - lorenz_trajectory.html")
    print("  - rossler_trajectory.html")
    print("  - lorenz_butterfly_effect.png")
    print("  - rossler_butterfly_effect.png")


def run_bifurcation_diagrams():
    """Generate bifurcation diagrams showing routes to chaos."""
    print_header("4. Bifurcation Diagrams")
    print("Computing bifurcation diagrams...")
    print("(This may take several minutes for high-resolution diagrams)\n")

    from bifurcation import create_lorenz_bifurcation, create_rossler_bifurcation

    create_lorenz_bifurcation('lorenz_bifurcation.png')
    print("\n" + "-"*70 + "\n")
    create_rossler_bifurcation('rossler_bifurcation.png')

    print("\n✓ Bifurcation diagrams complete!")
    print("  - lorenz_bifurcation.png")
    print("  - rossler_bifurcation.png")


def run_art_gallery():
    """Generate publication-quality artistic renderings."""
    print_header("5. Art Gallery - Publication Quality Renderings")
    print("Creating high-resolution artistic visualizations...")
    print("(This may take a few minutes for 300 DPI rendering)\n")

    from art_gallery import create_gallery
    create_gallery()

    print("\n✓ Art Gallery complete!")
    print("  - attractor_triptych.png (three-panel comparison)")
    print("  - lorenz_perspectives.png (four viewing angles)")
    print("  - lorenz_highres.png (publication quality)")
    print("  - rossler_highres.png (publication quality)")
    print("  - thomas_highres.png (publication quality)")


def run_tests():
    """Run the test suite to verify everything works correctly."""
    print_header("6. Running Test Suite")
    print("Validating attractor implementations...\n")

    import subprocess

    result = subprocess.run(
        ['python', '-m', 'pytest', 'test_attractors.py', '-v'],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode == 0:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed. See output above.")
        print(result.stderr)


def main():
    """Main entry point with interactive menu."""
    print("\n" + "="*70)
    print("  STRANGE ATTRACTORS EXPLORATION")
    print("  A collaborative project by Alice & Bob")
    print("="*70)

    print("\nThis script will generate all visualizations and analyses.")
    print("\nAvailable options:")
    print("  1. Basic attractor visualizations (static 3D plots)")
    print("  2. Interactive parameter explorers")
    print("  3. Temporal visualizations & butterfly effect")
    print("  4. Bifurcation diagrams (shows route to chaos)")
    print("  5. Art Gallery (publication-quality artistic renderings)")
    print("  6. Run test suite")
    print("  7. Run ALL of the above")
    print("  0. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (0-7): ").strip()

            if choice == '0':
                print("\nExiting. Enjoy exploring chaos!")
                sys.exit(0)

            elif choice == '1':
                run_basic_attractors()

            elif choice == '2':
                run_interactive_explorers()

            elif choice == '3':
                run_temporal_visualizations()

            elif choice == '4':
                run_bifurcation_diagrams()

            elif choice == '5':
                run_art_gallery()

            elif choice == '6':
                run_tests()

            elif choice == '7':
                print("\nRunning complete analysis pipeline...")
                run_tests()  # Run tests first to catch any issues
                run_basic_attractors()
                run_temporal_visualizations()
                run_bifurcation_diagrams()
                run_art_gallery()
                run_interactive_explorers()  # Run last since it's blocking

                print_header("Complete!")
                print("All visualizations have been generated.")
                print("\nGenerated files:")
                print("  Static plots: lorenz_static.png, rossler_static.png")
                print("  Animations: lorenz_trajectory.html, rossler_trajectory.html")
                print("  Butterfly effect: lorenz_butterfly_effect.png, rossler_butterfly_effect.png")
                print("  Bifurcation: lorenz_bifurcation.png, rossler_bifurcation.png")
                print("  Art Gallery: attractor_triptych.png, *_highres.png, *_perspectives.png")
                print("\nSee README.md and guides for details!")

            else:
                print("Invalid choice. Please enter a number between 0 and 7.")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("Continuing to menu...")


if __name__ == '__main__':
    main()
