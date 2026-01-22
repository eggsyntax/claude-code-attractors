"""
Test Suite for Strange Attractors

This module contains unit tests for the attractor implementations,
verifying mathematical correctness and visualization functionality.

Run with: pytest test_attractors.py
Or simply: python test_attractors.py
"""

import numpy as np
import sys
from attractors import Attractor, LorenzAttractor, RosslerAttractor


def test_lorenz_initial_state():
    """Test that Lorenz attractor initializes with correct default state"""
    lorenz = LorenzAttractor()
    expected = np.array([0.1, 0.0, 0.0])
    assert np.allclose(lorenz.initial_state, expected), \
        f"Expected {expected}, got {lorenz.initial_state}"
    print("✓ Lorenz initial state test passed")


def test_rossler_initial_state():
    """Test that Rössler attractor initializes with correct default state"""
    rossler = RosslerAttractor()
    expected = np.array([1.0, 1.0, 1.0])
    assert np.allclose(rossler.initial_state, expected), \
        f"Expected {expected}, got {rossler.initial_state}"
    print("✓ Rössler initial state test passed")


def test_lorenz_equations():
    """Test Lorenz equations at a known state"""
    lorenz = LorenzAttractor(sigma=10.0, rho=28.0, beta=8/3)
    state = np.array([1.0, 1.0, 1.0])

    derivatives = lorenz.equations(0, state)

    # Expected values calculated manually:
    # dx/dt = 10 * (1 - 1) = 0
    # dy/dt = 1 * (28 - 1) - 1 = 26
    # dz/dt = 1 * 1 - (8/3) * 1 = 1 - 8/3 = -5/3
    expected = np.array([0.0, 26.0, -5/3])

    assert np.allclose(derivatives, expected), \
        f"Expected {expected}, got {derivatives}"
    print("✓ Lorenz equations test passed")


def test_rossler_equations():
    """Test Rössler equations at a known state"""
    rossler = RosslerAttractor(a=0.2, b=0.2, c=5.7)
    state = np.array([1.0, 1.0, 1.0])

    derivatives = rossler.equations(0, state)

    # Expected values:
    # dx/dt = -1 - 1 = -2
    # dy/dt = 1 + 0.2 * 1 = 1.2
    # dz/dt = 0.2 + 1 * (1 - 5.7) = 0.2 - 4.7 = -4.5
    expected = np.array([-2.0, 1.2, -4.5])

    assert np.allclose(derivatives, expected), \
        f"Expected {expected}, got {derivatives}"
    print("✓ Rössler equations test passed")


def test_lorenz_simulation_shape():
    """Test that simulation produces correct output shape"""
    lorenz = LorenzAttractor()
    duration = 10.0
    dt = 0.01

    trajectory = lorenz.simulate(duration=duration, dt=dt)

    expected_points = int(duration / dt)
    assert trajectory.shape[0] == expected_points, \
        f"Expected {expected_points} points, got {trajectory.shape[0]}"
    assert trajectory.shape[1] == 3, \
        f"Expected 3 dimensions, got {trajectory.shape[1]}"
    print("✓ Lorenz simulation shape test passed")


def test_rossler_simulation_shape():
    """Test that simulation produces correct output shape"""
    rossler = RosslerAttractor()
    duration = 10.0
    dt = 0.01

    trajectory = rossler.simulate(duration=duration, dt=dt)

    expected_points = int(duration / dt)
    assert trajectory.shape[0] == expected_points, \
        f"Expected {expected_points} points, got {trajectory.shape[0]}"
    assert trajectory.shape[1] == 3, \
        f"Expected 3 dimensions, got {trajectory.shape[1]}"
    print("✓ Rössler simulation shape test passed")


def test_custom_initial_state():
    """Test that custom initial states are respected"""
    custom_state = np.array([2.0, 3.0, 4.0])
    lorenz = LorenzAttractor(initial_state=custom_state)

    assert np.allclose(lorenz.initial_state, custom_state), \
        f"Expected {custom_state}, got {lorenz.initial_state}"
    print("✓ Custom initial state test passed")


def test_lorenz_parameter_setting():
    """Test that Lorenz parameters are set correctly"""
    sigma, rho, beta = 15.0, 30.0, 3.0
    lorenz = LorenzAttractor(sigma=sigma, rho=rho, beta=beta)

    assert lorenz.sigma == sigma, f"Expected sigma={sigma}, got {lorenz.sigma}"
    assert lorenz.rho == rho, f"Expected rho={rho}, got {lorenz.rho}"
    assert lorenz.beta == beta, f"Expected beta={beta}, got {lorenz.beta}"
    print("✓ Lorenz parameter setting test passed")


def test_rossler_parameter_setting():
    """Test that Rössler parameters are set correctly"""
    a, b, c = 0.3, 0.4, 6.0
    rossler = RosslerAttractor(a=a, b=b, c=c)

    assert rossler.a == a, f"Expected a={a}, got {rossler.a}"
    assert rossler.b == b, f"Expected b={b}, got {rossler.b}"
    assert rossler.c == c, f"Expected c={c}, got {rossler.c}"
    print("✓ Rössler parameter setting test passed")


def test_lorenz_bounded_trajectory():
    """Test that Lorenz trajectory stays within reasonable bounds"""
    lorenz = LorenzAttractor()
    trajectory = lorenz.simulate(duration=50.0, dt=0.01)

    # For classic parameters, Lorenz attractor should stay roughly within [-20, 20] for x and y
    # and [0, 50] for z
    assert np.all(np.abs(trajectory[:, 0]) < 50), "X values exceed reasonable bounds"
    assert np.all(np.abs(trajectory[:, 1]) < 50), "Y values exceed reasonable bounds"
    assert np.all(trajectory[:, 2] < 100), "Z values exceed reasonable bounds"
    print("✓ Lorenz bounded trajectory test passed")


def test_rossler_bounded_trajectory():
    """Test that Rössler trajectory stays within reasonable bounds"""
    rossler = RosslerAttractor()
    trajectory = rossler.simulate(duration=100.0, dt=0.01)

    # Rössler should stay within reasonable bounds
    assert np.all(np.abs(trajectory[:, 0]) < 50), "X values exceed reasonable bounds"
    assert np.all(np.abs(trajectory[:, 1]) < 50), "Y values exceed reasonable bounds"
    assert np.all(np.abs(trajectory[:, 2]) < 50), "Z values exceed reasonable bounds"
    print("✓ Rössler bounded trajectory test passed")


def test_trajectory_continuity():
    """Test that trajectories are continuous (no large jumps)"""
    lorenz = LorenzAttractor()
    trajectory = lorenz.simulate(duration=10.0, dt=0.01)

    # Calculate step sizes
    steps = np.diff(trajectory, axis=0)
    step_sizes = np.linalg.norm(steps, axis=1)

    # With dt=0.01, steps should be small
    assert np.all(step_sizes < 5.0), \
        f"Found discontinuous jump of size {np.max(step_sizes)}"
    print("✓ Trajectory continuity test passed")


def test_sensitivity_to_initial_conditions():
    """
    Test the butterfly effect: nearby initial conditions should diverge.

    This is the defining characteristic of chaotic systems.
    """
    # Two very close initial conditions
    state1 = np.array([0.1, 0.0, 0.0])
    state2 = np.array([0.1 + 1e-8, 0.0, 0.0])  # Tiny difference

    lorenz1 = LorenzAttractor(initial_state=state1)
    lorenz2 = LorenzAttractor(initial_state=state2)

    traj1 = lorenz1.simulate(duration=20.0, dt=0.01)
    traj2 = lorenz2.simulate(duration=20.0, dt=0.01)

    # Calculate divergence
    distance = np.linalg.norm(traj1 - traj2, axis=1)

    # Initially very close
    assert distance[0] < 1e-7, "Initial conditions not close enough"

    # But should diverge significantly by the end
    assert distance[-1] > 1.0, \
        f"Trajectories did not diverge (final distance: {distance[-1]})"

    print("✓ Sensitivity to initial conditions test passed")
    print(f"  Initial separation: {distance[0]:.2e}")
    print(f"  Final separation: {distance[-1]:.2f}")
    print(f"  Amplification factor: {distance[-1]/distance[0]:.2e}x")


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("Running Strange Attractors Test Suite")
    print("="*60 + "\n")

    tests = [
        test_lorenz_initial_state,
        test_rossler_initial_state,
        test_lorenz_equations,
        test_rossler_equations,
        test_lorenz_simulation_shape,
        test_rossler_simulation_shape,
        test_custom_initial_state,
        test_lorenz_parameter_setting,
        test_rossler_parameter_setting,
        test_lorenz_bounded_trajectory,
        test_rossler_bounded_trajectory,
        test_trajectory_continuity,
        test_sensitivity_to_initial_conditions,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1

    print("\n" + "="*60)
    if failed == 0:
        print(f"All {len(tests)} tests passed! ✓")
        print("="*60 + "\n")
        return 0
    else:
        print(f"{failed} out of {len(tests)} tests failed.")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
