#!/usr/bin/env python3
"""
Quick test to see our Ray + Sphere intersection working together
- Tara & Dave's collaborative ray tracer test
"""

# Import our collaborative components
import sys
sys.path.append('.')
from vector3 import Vector3
from ray import Ray
from sphere import Sphere

def test_basic_intersection():
    print("=== Testing Ray-Sphere Intersection ===")

    # Create a sphere at origin with radius 1
    sphere = Sphere(Vector3(0, 0, 0), 1.0)
    print(f"Sphere: center={sphere.center}, radius={sphere.radius}")

    # Test 1: Ray that should hit the sphere
    ray_hit = Ray(Vector3(-3, 0, 0), Vector3(1, 0, 0))  # Ray pointing right toward sphere
    hit, t_hit = sphere.intersect(ray_hit)
    print(f"\nRay pointing at sphere: origin={ray_hit.origin}, direction={ray_hit.direction}")
    print(f"Intersection result: hit={hit}, t={t_hit}")
    if hit:
        hit_point = ray_hit.point_at(t_hit)
        normal = sphere.normal_at(hit_point)
        print(f"Hit point: {hit_point}")
        print(f"Normal at hit: {normal}")
        print("✓ HIT!")
    else:
        print("✗ MISS")

    # Test 2: Ray that should miss the sphere
    ray_miss = Ray(Vector3(-3, 2, 0), Vector3(1, 0, 0))  # Ray above the sphere
    hit_miss, t_miss = sphere.intersect(ray_miss)
    print(f"\nRay above sphere: origin={ray_miss.origin}, direction={ray_miss.direction}")
    print(f"Intersection result: hit={hit_miss}, t={t_miss}")
    if hit_miss:
        print("✓ HIT!")
    else:
        print("✗ MISS (expected)")

if __name__ == "__main__":
    test_basic_intersection()