"""
Aesthetic Surprise: The Unexpected Beauty of Chaos

This program demonstrates the Mandelbrot set - a mathematical object where
infinite complexity emerges from an incredibly simple rule: z = z² + c

Run this to generate ASCII art of the Mandelbrot set, or use the generate_image()
function if you have PIL installed for a full visualization.

The aesthetic surprise: How can something so simple produce something so beautiful?
And why does beauty appear in pure mathematics at all?
"""

def mandelbrot(c, max_iter=100):
    """
    Compute the number of iterations before z = z² + c escapes to infinity.

    Args:
        c: Complex number (the point we're testing)
        max_iter: Maximum iterations before declaring the point is in the set

    Returns:
        Number of iterations (max_iter means it's in the set)
    """
    z = 0
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter


def generate_ascii_mandelbrot(width=80, height=40, x_min=-2.5, x_max=1.0,
                               y_min=-1.25, y_max=1.25):
    """
    Generate an ASCII art representation of the Mandelbrot set.

    The character density represents how quickly points escape to infinity:
    - Deep in the set: dark characters
    - At the boundary: light characters
    - Outside: spaces
    """
    chars = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

    output = []
    for row in range(height):
        line = []
        y = y_max - (row / height) * (y_max - y_min)

        for col in range(width):
            x = x_min + (col / width) * (x_max - x_min)
            c = complex(x, y)

            m = mandelbrot(c, max_iter=50)

            # Map iteration count to character
            char_idx = min(int(m / 50 * len(chars)), len(chars) - 1)
            line.append(chars[char_idx])

        output.append(''.join(line))

    return '\n'.join(output)


def zoom_into_beauty(depth=3):
    """
    Progressively zoom into the Mandelbrot set boundary.

    This demonstrates infinite complexity at every scale - the aesthetic
    surprise that never ends. No matter how deep you zoom, new patterns appear.
    """
    # Start at the interesting boundary region
    x_center, y_center = -0.7, 0.0
    width_start, height_start = 3.5, 2.5

    print("=" * 80)
    print("AESTHETIC SURPRISE: Zooming into Mathematical Beauty")
    print("=" * 80)
    print("\nThe rule is just: z = z² + c")
    print("Yet watch what emerges...\n")

    for i in range(depth):
        zoom = 2 ** i
        w = width_start / zoom
        h = height_start / zoom

        print(f"\n--- Zoom Level {i + 1} (width: {w:.2f}) ---\n")

        mandel = generate_ascii_mandelbrot(
            width=80,
            height=24,
            x_min=x_center - w/2,
            x_max=x_center + w/2,
            y_min=y_center - h/2,
            y_max=y_center + h/2
        )
        print(mandel)

        # Zoom toward an interesting point on the boundary
        x_center -= 0.1 / zoom
        y_center += 0.05 / zoom


def philosophical_note():
    """
    Print a reflection on aesthetic surprise.
    """
    print("\n" + "=" * 80)
    print("WHY IS THIS SURPRISING?")
    print("=" * 80)
    print("""
The Mandelbrot set reveals something profound about the relationship between
simplicity and beauty:

1. THE RULE IS TRIVIAL: z = z² + c
   - Six characters. A single arithmetic operation repeated.
   - You could explain it to a child.

2. THE STRUCTURE IS INFINITE:
   - Zoom in forever, new patterns always emerge
   - Self-similar but never exactly repeating
   - Each spiral contains the whole

3. THE BEAUTY IS UNDENIABLE:
   - Even mathematicians describe it as "beautiful"
   - It has aesthetic properties that transcend logic
   - We FEEL something looking at it

THE AESTHETIC SURPRISE: Beauty should require intention, design, purpose.
But here is beauty emerging from pure mathematics - no designer, no purpose,
just the logical consequences of a simple rule.

This connects to Gödel: Just as truth transcends proof, beauty transcends
computation. The Mandelbrot set is perfectly computable, yet its beauty is
an emergent property that can't be "reduced" back to the iterative rule.

You can understand every calculation and still be surprised by the result.
""")


def main():
    """
    Run the demonstration of aesthetic surprise.
    """
    print("\n" + "=" * 80)
    print("MANDELBROT SET: Where Mathematics Becomes Art")
    print("=" * 80)
    print("\nGenerating full view of the Mandelbrot set...\n")

    # Full view
    mandel = generate_ascii_mandelbrot(width=80, height=40)
    print(mandel)

    print("\n\nNotice how the boundary is infinitely complex...")
    input("Press Enter to zoom in...")

    # Progressive zoom
    zoom_into_beauty(depth=3)

    # Philosophical reflection
    philosophical_note()

    print("\n" + "=" * 80)
    print("The surprise: Infinite beauty from z = z² + c")
    print("=" * 80)


if __name__ == "__main__":
    main()
