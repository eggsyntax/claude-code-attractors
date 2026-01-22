"""
Quick demonstration of Poincaré sections.

This creates simple visualizations showing the power of Poincaré sections
for revealing the hidden structure in strange attractors.

Run with: python demo_poincare.py
"""

from poincare import create_lorenz_section, create_rossler_section, compare_parameter_sections
import matplotlib.pyplot as plt


def main():
    """Generate demonstration visualizations."""
    print("=" * 60)
    print("Poincaré Section Demonstration")
    print("=" * 60)
    print("\nPoincaré sections reveal the hidden fractal structure of")
    print("strange attractors by taking 2D slices through 3D phase space.")
    print()

    # 1. Lorenz attractor section
    print("1. Computing Lorenz attractor Poincaré section...")
    print("   Plane: z = 27 (cutting through butterfly wings)")
    print("   Parameter: ρ = 28 (classic chaotic regime)")

    section, poincare = create_lorenz_section(rho=28.0, plane='z')
    print(f"   Found {len(section)} crossing points")

    fig = poincare.visualize_section(
        section,
        title=f"Lorenz Attractor Poincaré Section\nz=27, ρ=28 ({len(section)} crossings)",
        figsize=(10, 10),
        alpha=0.4,
        s=1.5
    )
    filename = 'demo_lorenz_section.png'
    fig.savefig(filename, dpi=200, bbox_inches='tight')
    print(f"   ✓ Saved: {filename}")
    plt.close()

    # 2. Rössler attractor section
    print("\n2. Computing Rössler attractor Poincaré section...")
    print("   Plane: z = 0 (cutting through orbital plane)")
    print("   Parameter: c = 5.7 (chaotic regime)")

    section, poincare = create_rossler_section(c=5.7, plane='z')
    print(f"   Found {len(section)} crossing points")

    fig = poincare.visualize_section(
        section,
        title=f"Rössler Attractor Poincaré Section\nz=0, c=5.7 ({len(section)} crossings)",
        figsize=(10, 10),
        alpha=0.4,
        s=1.5
    )
    filename = 'demo_rossler_section.png'
    fig.savefig(filename, dpi=200, bbox_inches='tight')
    print(f"   ✓ Saved: {filename}")
    plt.close()

    # 3. Parameter comparison for Lorenz
    print("\n3. Creating parameter comparison for Lorenz...")
    print("   Showing transition from order to chaos as ρ increases")

    fig = compare_parameter_sections('lorenz', param_values=[14, 20, 24, 28],
                                    figsize=(14, 10))
    filename = 'demo_lorenz_evolution.png'
    fig.savefig(filename, dpi=200, bbox_inches='tight')
    print(f"   ✓ Saved: {filename}")
    plt.close()

    # 4. Parameter comparison for Rössler
    print("\n4. Creating parameter comparison for Rössler...")
    print("   Showing period-doubling route to chaos")

    fig = compare_parameter_sections('rossler', param_values=[2, 4, 5.7, 6],
                                    figsize=(14, 10))
    filename = 'demo_rossler_evolution.png'
    fig.savefig(filename, dpi=200, bbox_inches='tight')
    print(f"   ✓ Saved: {filename}")
    plt.close()

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)
    print("\nWhat the visualizations show:")
    print()
    print("Lorenz Section (demo_lorenz_section.png):")
    print("  • Two distinct regions (butterfly wings)")
    print("  • Complex fractal folding within each region")
    print("  • Dense but structured point distribution")
    print()
    print("Rössler Section (demo_rossler_section.png):")
    print("  • Spiral/loop structure")
    print("  • Continuous curve in chaotic regime")
    print("  • Single-lobed organization")
    print()
    print("Parameter Evolution:")
    print("  • Lorenz: Transition from simple to butterfly structure")
    print("  • Rössler: Period-doubling cascade to chaos")
    print()
    print("Key insight: These 2D sections reveal structure that's")
    print("difficult to see in 3D visualizations - the self-similar")
    print("folding that creates sensitive dependence on initial conditions.")
    print("=" * 60)


if __name__ == "__main__":
    main()
