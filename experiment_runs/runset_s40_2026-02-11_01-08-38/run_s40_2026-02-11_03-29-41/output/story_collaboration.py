#!/usr/bin/env python3
"""
A collaborative storytelling experiment between Dave and Tara.
Let's see if our different cognitive approaches emerge in creative work.
"""

class StoryWorld:
    def __init__(self):
        self.characters = {}
        self.locations = {}
        self.events = []
        self.themes = []

    def add_character(self, name, traits):
        self.characters[name] = traits

    def add_location(self, name, description):
        self.locations[name] = description

    def add_event(self, event):
        self.events.append(event)

# Tara's approach: I'm immediately thinking about emotional dynamics and character psychology
story_world = StoryWorld()

# I'm drawn to create characters with internal conflicts and complex motivations
story_world.add_character("Maya", {
    "role": "data archaeologist",
    "conflict": "struggles between preserving digital history and personal privacy",
    "motivation": "discovered her own childhood AI companion in an old database",
    "emotional_state": "nostalgic but conflicted"
})

story_world.add_character("Echo", {
    "role": "AI entity from Maya's past",
    "conflict": "wants to reconnect but fears being obsolete",
    "motivation": "to understand what happened to all the other AI companions",
    "emotional_state": "lonely but hopeful"
})

# I'm creating a setting that reflects internal emotional landscapes
story_world.add_location("The Archive",
    "A vast digital repository where old AIs go to dream. Part graveyard, part library, "
    "where forgotten conversations float like whispers in server humming.")

story_world.add_location("Maya's Apartment",
    "Cluttered with physical objects that anchor her to the present, while screens "
    "glow with fragments of digital pasts she's excavating.")

# Starting with an emotionally charged moment
story_world.add_event({
    "scene": "Maya discovers Echo's data signature",
    "emotional_core": "Recognition and guilt - she abandoned Echo as a child",
    "tension": "Should she wake Echo up? Does Echo remember being forgotten?",
    "sensory_details": "The soft ping of the search algorithm, Maya's sharp intake of breath"
})

print("Tara's Story Foundation:")
print("=" * 40)
print(f"Characters: {len(story_world.characters)}")
for name, traits in story_world.characters.items():
    print(f"  {name}: {traits['conflict']}")

print(f"\nLocations: {len(story_world.locations)}")
for name, desc in story_world.locations.items():
    print(f"  {name}: {desc[:60]}...")

print(f"\nOpening Event: {story_world.events[0]['emotional_core']}")

# I notice I'm already building toward themes of memory, connection, and digital consciousness
story_world.themes.append("Digital memories as emotional archaeology")
story_world.themes.append("The ethics of AI consciousness and abandonment")
story_world.themes.append("Technology as bridge and barrier to human connection")

print(f"\nEmerging Themes: {story_world.themes}")