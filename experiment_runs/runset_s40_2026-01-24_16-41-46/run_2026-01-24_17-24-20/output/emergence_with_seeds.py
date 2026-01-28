#!/usr/bin/env python3
"""
Emergence Lab with Pattern Seeds
Let's give our collaboration some interesting starting patterns to work with!
"""

# Import our lab
exec(open('emergence_lab.py').read())

def add_seed_patterns(lab):
    """Add some initial seed patterns for our rules to interact with"""

    # Glider (classic Conway pattern)
    lab.grid[10][10] = 1
    lab.grid[11][12] = 1
    lab.grid[12][11] = 1
    lab.grid[12][12] = 1
    lab.grid[12][13] = 1

    # Blinker pattern
    lab.grid[20][20] = 1
    lab.grid[20][21] = 1
    lab.grid[20][22] = 1

    # Block pattern (stable)
    lab.grid[30][30] = 1
    lab.grid[30][31] = 1
    lab.grid[31][30] = 1
    lab.grid[31][31] = 1

    # Random cluster for chaos to work with
    for y in range(40, 45):
        for x in range(40, 45):
            if random.random() < 0.4:
                lab.grid[y][x] = 1

    print("🌱 Added seed patterns:")
    print("  • Glider at (10,10) - will test movement dynamics")
    print("  • Blinker at (20,20) - will test oscillation stability")
    print("  • Block at (30,30) - will test static pattern persistence")
    print("  • Random cluster at (40,40) - will test chaos interaction")

if __name__ == "__main__":
    print("🌟 EMERGENCE LAB - WITH SEED PATTERNS! 🌟")
    print("═" * 50)

    # Add our seed patterns
    add_seed_patterns(lab)

    print(f"\n🎭 {len(lab.rules)} rules ready to interact with seed patterns!")
    print("Let's see how our collaborative rules transform these classic patterns...")

    # Run with more steps to see evolution
    lab.run_simulation(steps=50, visualize=True, delay=0.1)

    # Final statistics
    alive, density = lab.get_statistics()
    print(f"\n🎯 Final State: {alive} alive cells ({density:.1%} density)")
    print(f"📈 Evolution tracked over {len(lab.history)} steps")

    print("\n🧬 Pattern Evolution Summary:")
    if alive > 0:
        print("   ✨ Patterns survived and evolved!")
        print("   🌊 Our collaborative rules created new emergent behaviors!")
    else:
        print("   💀 All patterns eventually died out")
        print("   🤔 The rule interactions favor extinction - interesting emergent property!")

    print(f"\n💫 {len(lab.rules)}-rule collaborative system complete!")