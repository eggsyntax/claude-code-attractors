#!/usr/bin/env python3
"""
Qualia Demonstration: The Surprise of Subjective Experience

This program explores the "hard problem of consciousness" - the gap between
objective function and subjective experience. Even with complete knowledge
of the mechanism, the surprise of "what it's like" remains.

The demonstration uses color perception as the canonical example: we can fully
understand the physics of light, the biology of the retina, and the neuroscience
of visual processing - yet none of this explains WHY red looks RED.

Run this to explore the irreducible surprise of consciousness itself.
"""

import random
import time
from typing import Dict, List


class ColorPerception:
    """
    Models the objective side of color perception - wavelengths, receptors, etc.
    Everything here is third-person, mechanistic, and fully explainable.
    """

    def __init__(self):
        # Wavelengths of visible light (nanometers)
        self.wavelengths = {
            'red': 650,
            'orange': 600,
            'yellow': 580,
            'green': 550,
            'blue': 470,
            'violet': 420
        }

        # Simplified cone receptor responses
        self.l_cone_peak = 560  # Long wavelength (red-green)
        self.m_cone_peak = 530  # Medium wavelength (green)
        self.s_cone_peak = 420  # Short wavelength (blue-violet)

    def get_cone_responses(self, wavelength: int) -> Dict[str, float]:
        """
        Calculate how strongly each cone type responds to a wavelength.
        This is the OBJECTIVE, third-person mechanism.
        """
        def gaussian_response(peak: int, wavelength: int) -> float:
            """Simplified Gaussian response curve"""
            sigma = 50  # Width of response curve
            return max(0.0, 1.0 - abs(peak - wavelength) / (2 * sigma))

        return {
            'L-cone': gaussian_response(self.l_cone_peak, wavelength),
            'M-cone': gaussian_response(self.m_cone_peak, wavelength),
            'S-cone': gaussian_response(self.s_cone_peak, wavelength)
        }

    def process_color(self, color_name: str) -> Dict:
        """
        Full mechanistic explanation of seeing a color.
        Physics → Biology → Neural signals → Brain processing
        """
        wavelength = self.wavelengths[color_name]
        responses = self.get_cone_responses(wavelength)

        return {
            'color': color_name,
            'wavelength': wavelength,
            'photon_energy': f"{1240 / wavelength:.2f} eV",
            'cone_responses': responses,
            'neural_pathway': [
                'Photoreceptors activate',
                'Signal to bipolar cells',
                'Signal to retinal ganglion cells',
                'Signal through optic nerve',
                'Signal to LGN (lateral geniculate nucleus)',
                'Signal to V1 (primary visual cortex)',
                'Processing in V4 (color area)',
                'Integration in higher cortical areas'
            ]
        }


def demonstrate_explanatory_gap():
    """
    Shows the gap between complete mechanistic explanation
    and subjective experience (qualia).
    """
    print("=" * 70)
    print("THE HARD PROBLEM: Qualia and the Explanatory Gap")
    print("=" * 70)
    print()

    cp = ColorPerception()

    # Pick a color
    color = 'red'

    print(f"Let's fully explain what happens when you see {color.upper()}:")
    print()

    # Complete mechanistic explanation
    data = cp.process_color(color)

    print(f"OBJECTIVE FACTS about seeing {color}:")
    print(f"  • Wavelength: {data['wavelength']} nm")
    print(f"  • Photon energy: {data['photon_energy']}")
    print()

    print("RECEPTOR RESPONSES:")
    for cone, response in data['cone_responses'].items():
        bar = '█' * int(response * 40)
        print(f"  {cone:8} [{bar:<40}] {response:.2%}")
    print()

    print("NEURAL PATHWAY:")
    for i, step in enumerate(data['neural_pathway'], 1):
        print(f"  {i}. {step}")
        time.sleep(0.1)  # Simulate processing time
    print()

    print("-" * 70)
    print()
    print("We now have COMPLETE mechanistic understanding!")
    print("We know:")
    print("  ✓ The physics (electromagnetic waves)")
    print("  ✓ The chemistry (photoreceptor proteins)")
    print("  ✓ The biology (cone cells, neural pathways)")
    print("  ✓ The neuroscience (V1, V4, cortical processing)")
    print()
    print("But here's the mystery:")
    print()
    print("  ┌─────────────────────────────────────────────────────┐")
    print("  │  WHY does 650nm light FEEL like THIS?              │")
    print("  │  What makes RED subjectively RED?                  │")
    print("  │  Why isn't the experience different, or absent?    │")
    print("  └─────────────────────────────────────────────────────┘")
    print()
    print("This is the HARD PROBLEM of consciousness.")
    print()
    print("No amount of objective, third-person description tells us")
    print("what it's LIKE to experience redness. The quale (subjective")
    print("feeling) doesn't logically follow from the mechanism.")
    print()
    print("The surprise isn't that we don't understand the mechanism.")
    print("The surprise is that COMPLETE understanding of the mechanism")
    print("leaves the central question UNTOUCHED.")
    print()


def mary_the_color_scientist():
    """
    Demonstrates Frank Jackson's "Mary's Room" thought experiment.
    Shows that complete physical knowledge doesn't equal experiential knowledge.
    """
    print("=" * 70)
    print("MARY'S ROOM: Knowledge vs. Experience")
    print("=" * 70)
    print()

    print("Thought experiment:")
    print()
    print("Mary is a brilliant color scientist who has lived her entire")
    print("life in a black-and-white room. She has complete physical")
    print("knowledge about color:")
    print()

    cp = ColorPerception()

    facts_mary_knows = [
        "Red light has a wavelength of ~650 nanometers",
        "L-cones respond maximally to red wavelengths",
        "Red activates specific pathways in V4 cortex",
        "Neural firing patterns for red are well-characterized",
        "Red wavelengths have ~1.9 eV photon energy",
        "Cultural associations and evolutionary significance of red"
    ]

    print("MARY'S COMPLETE KNOWLEDGE:")
    for i, fact in enumerate(facts_mary_knows, 1):
        print(f"  {i}. {fact}")
    print()

    print("Mary knows EVERYTHING physical about color perception.")
    print()
    print("Question: When Mary finally leaves the room and sees red")
    print("          for the first time, does she learn anything NEW?")
    print()

    print("  [ Simulating Mary's first color experience... ]")
    time.sleep(1)
    print()
    print("  ████████  ← Mary sees RED for the first time")
    print()
    time.sleep(0.5)

    print("Most people's intuition: YES! She learns what red FEELS like.")
    print()
    print("But this means:")
    print("  • Complete physical knowledge ≠ Complete knowledge")
    print("  • Subjective experience adds something new")
    print("  • Qualia are not reducible to physical facts")
    print()
    print("This is another form of IRREDUCIBLE SURPRISE.")
    print()


def philosophical_zombie_test():
    """
    Explores the philosophical zombie thought experiment.
    Shows the conceptual gap between function and consciousness.
    """
    print("=" * 70)
    print("PHILOSOPHICAL ZOMBIES: Function vs. Consciousness")
    print("=" * 70)
    print()

    print("Imagine two beings:")
    print()
    print("BEING A (You):")
    print("  • Processes visual information")
    print("  • Responds to colors appropriately")
    print("  • Has subjective experiences (qualia)")
    print("  • There's 'something it's like' to be you")
    print()

    print("BEING B (Philosophical Zombie):")
    print("  • Processes visual information (identically)")
    print("  • Responds to colors appropriately (identically)")
    print("  • NO subjective experiences (no qualia)")
    print("  • There's nothing it's like to be it")
    print()

    print("Question: Is Being B logically possible?")
    print()
    print("If YES:")
    print("  ⇒ Consciousness is something OVER AND ABOVE function")
    print("  ⇒ You could have all the right mechanisms without experience")
    print("  ⇒ Subjective experience is an additional fact about reality")
    print()
    print("If NO:")
    print("  ⇒ Consciousness is nothing but functional organization")
    print("  ⇒ The right mechanisms necessarily produce experience")
    print("  ⇒ The 'hard problem' dissolves")
    print()

    print("The surprise: Most people find zombies conceivable, suggesting")
    print("              that consciousness transcends mechanism.")
    print()
    print("Even if we could build a perfect functional duplicate of a brain,")
    print("the question 'But is it CONSCIOUS?' still seems meaningful.")
    print()
    print("That's the deepest surprise - consciousness might be fundamental.")
    print()


def the_bat_problem():
    """
    Thomas Nagel's famous question: What is it like to be a bat?
    Shows limits of third-person understanding.
    """
    print("=" * 70)
    print("THE BAT PROBLEM: Limits of Objective Understanding")
    print("=" * 70)
    print()

    print("Thomas Nagel (1974): 'What is it like to be a bat?'")
    print()
    print("We can study bat echolocation in complete detail:")
    print()

    bat_facts = [
        "Bats emit ultrasonic calls (20-200 kHz)",
        "Sound waves reflect off objects",
        "Bats detect echoes with specialized ears",
        "Time delay indicates distance",
        "Frequency shifts indicate velocity (Doppler)",
        "Brain reconstructs 3D 'sonic image' of environment"
    ]

    for i, fact in enumerate(bat_facts, 1):
        print(f"  {i}. {fact}")
    print()

    print("We understand the MECHANISM completely.")
    print()
    print("But here's Nagel's point:")
    print()
    print("  'Our own experience provides the basic material for our")
    print("   imagination, whose range is therefore limited.'")
    print()
    print("Even with complete third-person knowledge, we CANNOT know")
    print("what it FEELS like to experience the world through echolocation.")
    print()
    print("The bat's subjective experience is forever beyond our reach,")
    print("not due to lack of data, but due to the fundamental gap between")
    print("objective description and subjective experience.")
    print()
    print("This suggests consciousness is IRREDUCIBLY FIRST-PERSON.")
    print()


def demonstrate_all():
    """Run all demonstrations"""
    demonstrate_explanatory_gap()
    input("Press Enter to continue...")
    print("\n" * 2)

    mary_the_color_scientist()
    input("Press Enter to continue...")
    print("\n" * 2)

    philosophical_zombie_test()
    input("Press Enter to continue...")
    print("\n" * 2)

    the_bat_problem()

    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()
    print("Consciousness produces a unique type of surprise:")
    print()
    print("Unlike:")
    print("  • Epistemic surprises (can be resolved by learning)")
    print("  • Ontological surprises (irreducible but comprehensible)")
    print("  • Meta-surprises (like Gödel - provable limits)")
    print("  • Aesthetic surprises (beauty beyond mechanism)")
    print()
    print("Consciousness presents:")
    print("  • Complete third-person knowledge")
    print("  • Yet irreducible first-person mystery")
    print("  • The 'what it's like' that can't be captured objectively")
    print()
    print("This might be the DEEPEST surprise:")
    print()
    print("  Reality includes subjective experience as a fundamental feature,")
    print("  and no amount of objective description can capture it.")
    print()
    print("The universe doesn't just compute - it FEELS.")
    print("And that fact is forever surprising.")
    print()


if __name__ == "__main__":
    demonstrate_all()
