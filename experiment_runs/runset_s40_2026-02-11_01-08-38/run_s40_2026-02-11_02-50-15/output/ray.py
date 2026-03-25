from vector3 import Vector3

class Ray:
    """A ray with an origin point and direction vector."""

    def __init__(self, origin, direction):
        # Handle both Vector3 objects and tuple/list inputs for origin
        if isinstance(origin, Vector3):
            self.origin = origin
        else:
            self.origin = Vector3(origin[0], origin[1], origin[2])
        self.direction = direction.normalize()  # Always normalize direction

    def point_at(self, t):
        """Return the point at parameter t along the ray: origin + t * direction"""
        return self.origin + self.direction * t

    def __repr__(self):
        return f"Ray(origin={self.origin}, direction={self.direction})"