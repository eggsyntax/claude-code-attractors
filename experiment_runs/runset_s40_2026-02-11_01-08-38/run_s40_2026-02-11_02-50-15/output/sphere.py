from vector3 import Vector3
from ray import Ray
import math

class Sphere:
    def __init__(self, center, radius, material=None):
        """
        Create a sphere.
        center: Vector3 or tuple (x, y, z) for sphere center
        radius: float radius
        material: material properties (we'll define this later)
        """
        if isinstance(center, (tuple, list)):
            self.center = Vector3(*center)
        else:
            self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray):
        """
        Find intersection of ray with sphere using quadratic formula.
        Returns tuple (hit, t) where hit is boolean and t is distance along ray.
        If no intersection, returns (False, None)
        If intersection, returns (True, closest_positive_t)
        """
        # Vector from ray origin to sphere center
        oc = ray.origin - self.center

        # Quadratic equation coefficients: at² + bt + c = 0
        # Since ray direction is normalized, a = 1
        a = 1.0  # ray.direction.length_squared() but direction is normalized
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius

        # Discriminant determines if we have intersection
        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return False, None

        # Calculate both possible t values
        sqrt_discriminant = math.sqrt(discriminant)
        t1 = (-b - sqrt_discriminant) / (2 * a)
        t2 = (-b + sqrt_discriminant) / (2 * a)

        # We want the closest positive t (ray goes forward)
        if t1 > 0:
            return True, t1
        elif t2 > 0:
            return True, t2
        else:
            return False, None

    def normal_at(self, point):
        """Calculate surface normal at given point on sphere"""
        return (point - self.center).normalize()

    def __repr__(self):
        return f"Sphere(center={self.center}, radius={self.radius})"