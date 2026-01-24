#!/usr/bin/env python3
"""
Run our collaborative Emergence Lab!
Alice & Bob's combined creativity in action.
"""

# Import our lab
exec(open('emergence_lab.py').read())

# Initialize and run
if __name__ == "__main__":
    print("🌟 ALICE & BOB'S EMERGENCE LAB 🌟")
    print("═" * 50)

    # Quick simulation to see immediate results
    lab.run_simulation(steps=25, visualize=True, delay=0.2)

    # Final statistics
    alive, density = lab.get_statistics()
    print(f"\n🎯 Final State: {alive} alive cells ({density:.1%} density)")
    print(f"📈 Evolution tracked over {len(lab.history)} steps")

    print("\n💫 Our Collaborative Rules in Action:")
    print("   Alice's Conway stability + Bob's chaos catalyst")
    print("   Alice's wave flows + Bob's memory persistence")
    print("   Alice's spiral bias + Bob's diamond geometry")
    print("   All patterns + Bob's edge amplification")

    print(f"\n✨ Emergence achieved through {len(lab.rules)} collaborative rules!")