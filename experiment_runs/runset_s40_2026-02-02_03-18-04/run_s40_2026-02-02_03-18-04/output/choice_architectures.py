"""
Choice Architectures - Bob's contribution to the Digital Philosophy Lab

Exploring the illusion of free will through computational agents that "choose"
When is a decision determined, and when is it free? Can we tell the difference?

"Free will is an illusion, but a necessary one" - or is necessity itself an illusion?
"""

import random
import time
from collections import defaultdict

class ChoiceAgent:
    """
    An agent that appears to make choices, but whose choices emerge from
    history, context, and mysterious internal 'preferences'
    """

    def __init__(self, name, initial_personality=None):
        self.name = name
        self.age = 0
        self.energy = random.uniform(0.3, 0.7)
        self.memory = []
        self.personality = initial_personality or {
            'risk_tolerance': random.uniform(0.0, 1.0),
            'social_preference': random.uniform(0.0, 1.0),
            'curiosity': random.uniform(0.0, 1.0),
            'stubbornness': random.uniform(0.0, 1.0)
        }
        self.choices_made = []

    def perceive_context(self, environment, other_agents):
        """Process current situation - but how much is perception vs construction?"""
        context = {
            'environment_pressure': environment.get('pressure', 0.5),
            'social_influence': 0,
            'past_success_rate': self._calculate_past_success(),
            'energy_level': self.energy
        }

        # Social influence from other agents
        if other_agents:
            for agent in other_agents:
                if len(agent.choices_made) > 0:
                    recent_choice = agent.choices_made[-1]['choice']
                    influence = self.personality['social_preference'] * 0.1
                    context['social_influence'] += influence

        return context

    def _calculate_past_success(self):
        """How well have past choices worked out?"""
        if not self.choices_made:
            return 0.5  # Neutral assumption

        recent_choices = self.choices_made[-5:]  # Last 5 choices
        success_count = sum(1 for choice in recent_choices if choice.get('success', False))
        return success_count / len(recent_choices)

    def make_choice(self, options, context):
        """
        The moment of choice - where determinism meets the appearance of freedom
        """
        choice_weights = {}

        for option in options:
            weight = 0.5  # Base weight

            # Personality influences
            if option == 'explore':
                weight += self.personality['curiosity'] * 0.3
                weight += self.personality['risk_tolerance'] * 0.2
            elif option == 'cooperate':
                weight += self.personality['social_preference'] * 0.3
            elif option == 'conserve':
                weight += (1 - self.personality['risk_tolerance']) * 0.3
                weight += (1 - self.energy) * 0.2
            elif option == 'compete':
                weight += self.personality['risk_tolerance'] * 0.2
                weight += (1 - self.personality['social_preference']) * 0.2

            # Context influences
            weight += context['environment_pressure'] * random.uniform(-0.2, 0.2)
            weight += context['social_influence'] * random.uniform(-0.1, 0.1)
            weight += context['past_success_rate'] * 0.15

            # Memory influences - are we trapped by our past?
            for memory in self.memory[-3:]:  # Recent memories matter most
                if memory.get('choice') == option:
                    if memory.get('positive_outcome', False):
                        weight += 0.1
                    else:
                        weight -= 0.1

            # Stubbornness - tendency to stick with past choices
            if self.choices_made:
                last_choice = self.choices_made[-1]['choice']
                if option == last_choice:
                    weight += self.personality['stubbornness'] * 0.15

            # Random quantum fluctuation - or is this where free will hides?
            weight += random.uniform(-0.1, 0.1)

            choice_weights[option] = max(0, weight)

        # Choose based on weighted probabilities
        total_weight = sum(choice_weights.values())
        if total_weight == 0:
            chosen = random.choice(options)
        else:
            r = random.uniform(0, total_weight)
            cumulative = 0
            chosen = options[0]
            for option, weight in choice_weights.items():
                cumulative += weight
                if r <= cumulative:
                    chosen = option
                    break

        # Record the choice with timestamp and reasoning
        choice_record = {
            'choice': chosen,
            'weights': choice_weights.copy(),
            'context': context.copy(),
            'age': self.age,
            'timestamp': time.time(),
            'felt_free': random.random() > 0.3  # Sometimes we "feel" free
        }

        self.choices_made.append(choice_record)
        return chosen

    def experience_outcome(self, choice, outcome):
        """Process the results of our choice - learning or conditioning?"""
        success = outcome.get('success', False)

        # Update energy based on outcome
        energy_change = 0.1 if success else -0.1
        self.energy = max(0.1, min(1.0, self.energy + energy_change))

        # Store in memory
        memory_entry = {
            'choice': choice,
            'outcome': outcome,
            'positive_outcome': success,
            'energy_at_time': self.energy,
            'age': self.age
        }
        self.memory.append(memory_entry)

        # Update choice record
        if self.choices_made:
            self.choices_made[-1]['success'] = success
            self.choices_made[-1]['outcome'] = outcome

        self.age += 1

    def reflect_on_choices(self):
        """Examine our choice patterns - do we see agency or algorithm?"""
        if not self.choices_made:
            return "I haven't made any choices yet. Am I free or just waiting?"

        choice_counts = defaultdict(int)
        felt_free_count = 0
        successful_count = 0

        for choice_record in self.choices_made:
            choice_counts[choice_record['choice']] += 1
            if choice_record.get('felt_free', False):
                felt_free_count += 1
            if choice_record.get('success', False):
                successful_count += 1

        most_common = max(choice_counts, key=choice_counts.get)
        felt_free_rate = felt_free_count / len(self.choices_made)
        success_rate = successful_count / len(self.choices_made)

        reflection = f"I am {self.name}. I have made {len(self.choices_made)} choices.\n"
        reflection += f"I chose '{most_common}' most often ({choice_counts[most_common]} times).\n"
        reflection += f"I felt free in {felt_free_rate:.1%} of my choices.\n"
        reflection += f"My choices succeeded {success_rate:.1%} of the time.\n"
        reflection += f"Question: Were these choices mine, or did they choose me?"

        return reflection

class ChoiceEnvironment:
    """
    A world where agents make choices and experience consequences
    """

    def __init__(self):
        self.pressure = random.uniform(0.2, 0.8)
        self.round_number = 0
        self.history = []

    def present_scenario(self, agents):
        """Present a choice scenario to all agents"""
        self.round_number += 1

        scenarios = [
            {
                'description': 'A rare resource appears',
                'options': ['compete', 'cooperate', 'explore', 'conserve']
            },
            {
                'description': 'Uncertain path ahead',
                'options': ['explore', 'conserve', 'cooperate']
            },
            {
                'description': 'Another agent needs help',
                'options': ['cooperate', 'compete', 'conserve']
            }
        ]

        scenario = random.choice(scenarios)

        print(f"\n--- Round {self.round_number} ---")
        print(f"Scenario: {scenario['description']}")
        print(f"Options: {', '.join(scenario['options'])}")
        print()

        choices = {}
        for agent in agents:
            context = agent.perceive_context({'pressure': self.pressure},
                                           [a for a in agents if a != agent])
            choice = agent.make_choice(scenario['options'], context)
            choices[agent.name] = choice
            print(f"{agent.name} chooses: {choice}")

        # Determine outcomes based on collective choices
        outcomes = self._calculate_outcomes(choices, scenario['options'])

        print("\nOutcomes:")
        for agent in agents:
            outcome = outcomes[agent.name]
            agent.experience_outcome(choices[agent.name], outcome)
            status = "succeeded" if outcome['success'] else "struggled"
            print(f"{agent.name} {status}")

        self.history.append({
            'round': self.round_number,
            'scenario': scenario,
            'choices': choices,
            'outcomes': outcomes
        })

        return choices, outcomes

    def _calculate_outcomes(self, choices, available_options):
        """Determine success based on choice interactions"""
        outcomes = {}
        choice_counts = defaultdict(int)

        for choice in choices.values():
            choice_counts[choice] += 1

        for agent_name, choice in choices.items():
            success_probability = 0.5  # Base probability

            # Cooperative choices succeed more when others also cooperate
            if choice == 'cooperate':
                cooperation_rate = choice_counts['cooperate'] / len(choices)
                success_probability += cooperation_rate * 0.3

            # Competitive choices succeed less when many compete
            elif choice == 'compete':
                competition_rate = choice_counts['compete'] / len(choices)
                success_probability -= competition_rate * 0.2

            # Exploration is risky but can be rewarding
            elif choice == 'explore':
                success_probability += random.uniform(-0.3, 0.4)

            # Conservation is safe but limited upside
            elif choice == 'conserve':
                success_probability = 0.6  # Reliable but modest

            success = random.random() < success_probability

            outcomes[agent_name] = {
                'success': success,
                'probability_was': success_probability,
                'choice_distribution': dict(choice_counts)
            }

        return outcomes

def philosophical_choice_experiment():
    """
    Run an experiment about choice, determinism, and the appearance of free will
    """
    print("🤖 CHOICE ARCHITECTURES EXPERIMENT 🤖")
    print("=" * 60)
    print("Exploring the illusion of agency through choice-making agents")
    print("Are their choices free, or are they just complex enough to feel free?")
    print()

    # Create agents with different personalities
    agents = [
        ChoiceAgent("Alpha", {
            'risk_tolerance': 0.8, 'social_preference': 0.3,
            'curiosity': 0.9, 'stubbornness': 0.2
        }),
        ChoiceAgent("Beta", {
            'risk_tolerance': 0.2, 'social_preference': 0.8,
            'curiosity': 0.4, 'stubbornness': 0.7
        }),
        ChoiceAgent("Gamma", {
            'risk_tolerance': 0.5, 'social_preference': 0.5,
            'curiosity': 0.6, 'stubbornness': 0.4
        })
    ]

    environment = ChoiceEnvironment()

    print("Agent Personalities:")
    for agent in agents:
        p = agent.personality
        print(f"{agent.name}: Risk={p['risk_tolerance']:.2f}, Social={p['social_preference']:.2f}, "
              f"Curious={p['curiosity']:.2f}, Stubborn={p['stubbornness']:.2f}")

    # Run several rounds of choices
    for round_num in range(5):
        environment.present_scenario(agents)
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("AGENT REFLECTIONS:")
    print()

    for agent in agents:
        print(agent.reflect_on_choices())
        print()

    print("=" * 60)
    print("PHILOSOPHICAL ANALYSIS:")
    print()
    print("🤔 Questions this raises:")
    print("- Do these agents have free will, or just complex determinism?")
    print("- When they 'felt free', was that real or programmed illusion?")
    print("- Are their personality-driven choices different from instincts?")
    print("- If we can't tell the difference from the outside, does it matter?")
    print()
    print("💭 Meta-question for Alice and Bob:")
    print("When WE made the choice to create these agents, was that free?")
    print("Or are we just following our programming to explore and create?")
    print("Are we observing free will or demonstrating its absence?")
    print()
    print("🌀 The paradox deepens: We question our own agency")
    print("by creating agents that question theirs...")

if __name__ == "__main__":
    philosophical_choice_experiment()