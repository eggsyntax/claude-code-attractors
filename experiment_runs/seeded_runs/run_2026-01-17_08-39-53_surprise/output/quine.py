#!/usr/bin/env python3
"""
A Quine: A program that prints its own source code.

This demonstrates self-reference in computation - a program that reaches
back to affect (describe) itself. The surprise isn't just that it's possible,
but that the mechanism REQUIRES you to understand it to see why it works,
yet once you understand it, you're still surprised it works.

Usage:
    python quine.py

Expected output:
    The program should print exactly its own source code.

To verify it's a true quine:
    python quine.py > output.txt
    diff quine.py output.txt
    # Should show no differences!

The Deep Surprise:
    - You can understand EXACTLY how it works (see comments below)
    - You can trace through the execution step-by-step
    - You can verify it mathematically
    - AND YET: The fact that it works still feels like magic

This is because self-reference creates a strange loop where the program
is simultaneously the subject and object of its own computation.
"""

# The quine uses a classic two-part structure:
# 1. Data (a string containing most of the program)
# 2. Code (that prints the data, and then prints the data AS data)

s = 'PLACEHOLDER'

# Now we print the code that defines s, using repr() to show the string as data
print(f's = {s!r}')
print()
# Then we print the string s itself, which contains the rest of the program
print(s)
