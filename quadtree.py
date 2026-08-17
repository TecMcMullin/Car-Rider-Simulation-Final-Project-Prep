##quadtree.py

import heapq
from itertools import count


class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains_point(self, px, py):
        return (
            self.x <= px <= self.x + self.width
            and self.y <= py <= self.y + self.height
        )

    def distance_to_point(self, px, py):
        # Squared distance from point to rectangle
        cx = min(max(px, self.x), self.x + self.width)
        cy = min(max(py, self.y), self.y + self.height)
        return (cx - px) ** 2 + (cy - py) ** 2


class Point:
    def __init__(self, x, y, data=None):
        self.x = x
        self.y = y
        self.data = data


class QuadtreeNode:
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def subdivide(self):
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.width, self.boundary.height
        hw = w / 2.0
        hh = h / 2.0

        self.northwest = QuadtreeNode(Rectangle(x, y + hh, hw, hh), self.capacity)
        self.northeast = QuadtreeNode(Rectangle(x + hw, y + hh, hw, hh), self.capacity)
        self.southwest = QuadtreeNode(Rectangle(x, y, hw, hh), self.capacity)
        self.southeast = QuadtreeNode(Rectangle(x + hw, y, hw, hh), self.capacity)

        self.divided = True

    def insert(self, point):
        if not self.boundary.contains_point(point.x, point.y):
            return False

        if len(self.points) < self.capacity and not self.divided:
            self.points.append(point)
            return True

        if not self.divided:
            self.subdivide()

        return (
            self.northwest.insert(point)
            or self.northeast.insert(point)
            or self.southwest.insert(point)
            or self.southeast.insert(point)
        )


class Quadtree:
    def __init__(self, boundary, capacity=4):
        self.root = QuadtreeNode(boundary, capacity)
        self.tie_breaker = count()

    def insert(self, point):
        return self.root.insert(point)

    def find_k_nearest(self, query_point, k=5):
        if k <= 0:
            raise ValueError("k must be positive")
        if self.root is None:
            return []

        candidates = []  # max-heap: (-dist_sq, tie_breaker, point)

        def search(node):
            if node is None:
                return

            rect_dist = node.boundary.distance_to_point(query_point.x, query_point.y)
            if len(candidates) == k and rect_dist > -candidates[0][0]:
                return

            for p in node.points:
                dist_sq = (p.x - query_point.x) ** 2 + (p.y - query_point.y) ** 2
                entry = (-dist_sq, next(self.tie_breaker), p)
                if len(candidates) < k:
                    heapq.heappush(candidates, entry)
                else:
                    if dist_sq < -candidates[0][0]:
                        heapq.heapreplace(candidates, entry)

            if node.divided:
                search(node.northwest)
                search(node.northeast)
                search(node.southwest)
                search(node.southeast)

        search(self.root)
        return [e[2] for e in sorted(candidates, key=lambda e: -e[0])]

    def remove(self, point):
        def remove_from_node(node):
            if node is None:
                return False

            for i, stored in enumerate(node.points):
                if stored is point:
                    node.points.pop(i)
                    return True

            if node.divided:
                removed = False
                if node.northwest.boundary.contains_point(point.x, point.y):
                    removed |= remove_from_node(node.northwest)
                if node.northeast.boundary.contains_point(point.x, point.y):
                    removed |= remove_from_node(node.northeast)
                if node.southwest.boundary.contains_point(point.x, point.y):
                    removed |= remove_from_node(node.southwest)
                if node.southeast.boundary.contains_point(point.x, point.y):
                    removed |= remove_from_node(node.southeast)
                return removed

            return False

        return remove_from_node(self.root)
