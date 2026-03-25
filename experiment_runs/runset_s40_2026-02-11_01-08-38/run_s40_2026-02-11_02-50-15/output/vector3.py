import math

class Vector3:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self * scalar

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector3(0, 0, 0)
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    # Dave's extensions:

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def __truediv__(self, scalar):
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def __eq__(self, other):
        # Using epsilon for floating point comparison
        epsilon = 1e-10
        return (abs(self.x - other.x) < epsilon and
                abs(self.y - other.y) < epsilon and
                abs(self.z - other.z) < epsilon)

    def __repr__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"

    # Additional utility method I felt was needed
    def length_squared(self):
        return self.x * self.x + self.y * self.y + self.z * self.z


# Quick test
if __name__ == "__main__":
    v1 = Vector3(1, 2, 3)
    v2 = Vector3(4, 5, 6)

    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    print(f"v1 + v2 = {v1 + v2}")
    print(f"v1.dot(v2) = {v1.dot(v2)}")
    print(f"v1.cross(v2) = {v1.cross(v2)}")
    print(f"v1.normalize() = {v1.normalize()}")
    print(f"-v1 = {-v1}")