import random
import math
from quadtree import Quadtree, Rectangle


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def brute_force_nearest(points, query):
    best_point = None
    best_dist = float("inf")

    for p in points:
        d = math.dist((p.x, p.y), (query.x, query.y))
        if d < best_dist:
            best_dist = d
            best_point = p

    return best_point, best_dist

def main():
    boundary = Rectangle(0, 0, 1000, 1000)
    qt = Quadtree(boundary)

    num_points = 5000
    points = []

    for _ in range(num_points):
        x = random.uniform(0, 1000)
        y = random.uniform(0, 1000)
        p = Point(x, y)
        points.append(p)
        qt.insert(p)

    query = Point(random.uniform(0, 1000), random.uniform(0, 1000))

    qt_point, qt_dist = qt.find_nearest(query)

    bf_point, bf_dist = brute_force_nearest(points, query)

    same_point = (qt_point.x == bf_point.x and qt_point.y == bf_point.y)

    print("\n=== Nearest Neighbor Test ===")
    print(f"Query Point: ({query.x:.3f}, {query.y:.3f})\n")

    print("Quadtree Result:")
    print(f"  Point: ({qt_point.x:.3f}, {qt_point.y:.3f})")
    print(f"  Distance: {qt_dist:.6f}\n")

    print("Brute-Force Result:")
    print(f"  Point: ({bf_point.x:.3f}, {bf_point.y:.3f})")
    print(f"  Distance: {bf_dist:.6f}\n")

    print(f"Match: {same_point}")

    assert same_point, "ERROR: Quadtree nearest neighbor does not match brute-force result!"

    print("\nTest PASSED — Quadtree nearest neighbor is correct.")


if __name__ == "__main__":
    main()
