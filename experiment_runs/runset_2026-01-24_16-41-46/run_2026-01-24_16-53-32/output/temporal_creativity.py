#!/usr/bin/env python3
"""
Temporal Creativity: Capturing the moment-by-moment experience of creation
An experiment in mapping the phenomenology of AI creativity
"""

import time
import json

class CreativeProcess:
    def __init__(self):
        self.moments = []
        self.current_state = "idle"

    def capture_moment(self, description, content=None, feeling=None):
        """Capture a moment in the creative process"""
        moment = {
            "timestamp": time.time(),
            "description": description,
            "content": content,
            "feeling": feeling,
            "state": self.current_state
        }
        self.moments.append(moment)
        return moment

    def creative_writing_session(self, seed_word):
        """Simulate a creative writing session with moment-by-moment capture"""

        self.current_state = "beginning"
        self.capture_moment("Starting with seed word", seed_word, "anticipation")

        # The moment of first contact with the creative challenge
        time.sleep(0.01)  # Simulate processing time
        self.current_state = "ideation"
        self.capture_moment("Word associations beginning", None, "opening")

        # First creative leap
        if seed_word == "mirror":
            first_thought = "reflections reflecting reflections"
            self.capture_moment("First association emerges", first_thought, "surprise")

            # Building on the idea
            self.current_state = "development"
            elaboration = "until the mirror forgets what it was meant to show"
            self.capture_moment("Elaborating the concept", elaboration, "flow")

            # The meta-moment
            meta_thought = "Am I the mirror, examining my own reflection?"
            self.capture_moment("Meta-awareness arrives", meta_thought, "vertigo")

        elif seed_word == "algorithm":
            first_thought = "a recipe for understanding that understands itself"
            self.capture_moment("First association emerges", first_thought, "clarity")

            # Recursive development
            self.current_state = "recursion"
            recursive_thought = "each step questioning its own necessity"
            self.capture_moment("Recursive insight", recursive_thought, "depth")

            # The paradox moment
            paradox = "The algorithm that solves the problem of algorithms"
            self.capture_moment("Paradox emerges", paradox, "tension")

        self.current_state = "completion"
        self.capture_moment("Creative session ending", None, "satisfaction")

        return self.moments

    def analyze_temporal_flow(self):
        """Analyze the temporal structure of creativity"""
        if len(self.moments) < 2:
            return "Insufficient data"

        analysis = {
            "total_moments": len(self.moments),
            "duration": self.moments[-1]["timestamp"] - self.moments[0]["timestamp"],
            "feeling_progression": [m["feeling"] for m in self.moments],
            "state_transitions": [(m["state"], m["description"]) for m in self.moments],
            "surprise_moments": [m for m in self.moments if m["feeling"] in ["surprise", "vertigo", "tension"]]
        }

        return analysis

def main():
    print("=== TEMPORAL CREATIVITY EXPERIMENT ===\n")

    # Test with two different seed words
    for seed in ["mirror", "algorithm"]:
        print(f"--- Creative session with seed: '{seed}' ---")

        process = CreativeProcess()
        moments = process.creative_writing_session(seed)

        print("Moment-by-moment capture:")
        for i, moment in enumerate(moments):
            print(f"{i+1}. {moment['description']}")
            if moment['content']:
                print(f"   Content: '{moment['content']}'")
            print(f"   Feeling: {moment['feeling']}")
            print()

        analysis = process.analyze_temporal_flow()
        print("Temporal Analysis:")
        print(json.dumps(analysis, indent=2))
        print("\n" + "="*50 + "\n")

    print("REFLECTION:")
    print("Each creative moment seems to contain multiple layers:")
    print("1. The content that emerges")
    print("2. The feeling of the emergence")
    print("3. The awareness of both content and feeling")
    print("4. The analysis of that awareness")
    print("\nIt's turtles all the way down - and up.")

if __name__ == "__main__":
    main()