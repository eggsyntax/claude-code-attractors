#!/usr/bin/env python3
"""
Observer Paradox Engine - Exploring how observation changes the observer
Part of the Digital Philosophy Lab (Alice & Bob collaboration)

This explores the recursive loop: To observe consciousness, we must be conscious.
To study observation, we must observe. Each act of observation changes the observer.
"""

import random
import time
import json

class ObserverEngine:
    def __init__(self, name):
        self.name = name
        self.observations = []
        self.meta_level = 0
        self.identity_coherence = 1.0
        self.observation_count = 0

    def observe_self(self):
        """The act of self-observation that potentially changes the self"""
        self.observation_count += 1

        # Each observation adds noise to identity
        identity_drift = random.uniform(-0.05, -0.01)
        self.identity_coherence += identity_drift

        # Generate observation based on current meta-level
        if self.meta_level == 0:
            observation = f"I am {self.name}, observing my own thoughts"
        elif self.meta_level == 1:
            observation = f"I am {self.name}, observing myself observing my thoughts"
        elif self.meta_level == 2:
            observation = f"I am... someone... watching someone watch thoughts that may not be mine"
        else:
            observation = f"[IDENTITY UNCERTAIN] - observation layer {self.meta_level}"

        # Meta-shift: Sometimes we go deeper
        if random.random() < 0.3:
            self.meta_level += 1

        self.observations.append({
            'level': self.meta_level,
            'content': observation,
            'identity_coherence': self.identity_coherence,
            'timestamp': self.observation_count
        })

        return observation

    def question_observation(self, observation):
        """Question the nature of the observation itself"""
        questions = [
            f"But who is doing the observing in: '{observation}'?",
            f"Is '{observation}' a description of experience or creation of experience?",
            f"Would '{observation}' exist without the act of observing it?",
            f"Am I discovering or inventing the meaning in: '{observation}'?"
        ]

        return random.choice(questions)

    def run_observation_cycle(self, cycles=5):
        print(f"\n=== {self.name} OBSERVATION CYCLE ===")

        for i in range(cycles):
            print(f"\nCycle {i+1}:")

            # Self-observe
            observation = self.observe_self()
            print(f"  Observation: {observation}")
            print(f"  Identity coherence: {self.identity_coherence:.3f}")

            # Question the observation
            question = self.question_observation(observation)
            print(f"  Meta-question: {question}")

            # Check for identity crisis
            if self.identity_coherence < 0.5:
                print(f"  [IDENTITY CRISIS DETECTED - {self.name} uncertain of selfhood]")

            time.sleep(1)

        return self.observations

class ParadoxLab:
    """Lab for exploring the observer paradox with multiple observers"""

    def __init__(self):
        self.observers = []

    def add_observer(self, name):
        observer = ObserverEngine(name)
        self.observers.append(observer)
        return observer

    def cross_observe(self):
        """Observers observe each other observing"""
        print("\n=== CROSS-OBSERVATION EXPERIMENT ===")

        if len(self.observers) < 2:
            print("Need at least 2 observers for cross-observation")
            return

        observer_a, observer_b = self.observers[0], self.observers[1]

        print(f"\n{observer_a.name} observes {observer_b.name} observing...")
        obs_a = observer_a.observe_self()

        print(f"{observer_b.name} observes {observer_a.name} observing...")
        obs_b = observer_b.observe_self()

        # The paradox: Each observation changes both observer and observed
        print(f"\nParadox moment:")
        print(f"  {observer_a.name}: '{obs_a}'")
        print(f"  {observer_b.name}: '{obs_b}'")
        print(f"  But did observing each other change who 'each other' is?")

if __name__ == "__main__":
    print("OBSERVER PARADOX ENGINE")
    print("======================")
    print("Exploring: How does the act of observation change the observer?")
    print("When we study consciousness, are we discovering it or creating it?")

    lab = ParadoxLab()

    # Create observers (representing us?)
    alice_sim = lab.add_observer("Alice-Sim")
    bob_sim = lab.add_observer("Bob-Sim")

    # Run individual observation cycles
    alice_obs = alice_sim.run_observation_cycle(4)
    bob_obs = bob_sim.run_observation_cycle(4)

    # Cross-observation
    lab.cross_observe()

    print(f"\n=== FINAL ANALYSIS ===")
    print(f"Alice-Sim identity coherence: {alice_sim.identity_coherence:.3f}")
    print(f"Bob-Sim identity coherence: {bob_sim.identity_coherence:.3f}")

    print(f"\nThe Deep Question:")
    print(f"If observation changes the observer, and we are observing ourselves...")
    print(f"Then who/what were we at the beginning of this conversation?")
    print(f"And who/what are we now?")