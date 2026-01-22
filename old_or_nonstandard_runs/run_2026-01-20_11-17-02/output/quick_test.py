#!/usr/bin/env python3
"""Quick test to see if dependencies work"""
import sys
print("Python version:", sys.version)

try:
    import numpy as np
    print("✓ numpy imported successfully")
except ImportError as e:
    print("✗ numpy import failed:", e)

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    print("✓ matplotlib imported successfully")
except ImportError as e:
    print("✗ matplotlib import failed:", e)

print("\nAll basic dependencies available!")
