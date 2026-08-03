import math


class Rectangle:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, point):
        return (
            self.x <= point.x < self.x + self.width and
            self.y <= point.y < self.y + self.height
        )

    def distance_to_point(self, px, py):
        dx = max(self.x - px, 0, px - (self.x + self.width))
        dy = max(self.y - py, 0, py - (self.y + self.height))
        return math.sqrt(dx * dx + dy * dy)


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
        x, y = self.boundary.x, self.boundary.y
        w, h = self.boundary.width / 2, self.boundary.height / 2

        nw = Rectangle(x, y, w, h)
        ne = Rectangle(x + w, y, w, h)
        sw = Rectangle(x, y + h, w, h)
        se = Rectangle(x + w, y + h, w, h)

        self.northwest = QuadtreeNode(nw, self.capacity)
        self.northeast = QuadtreeNode(ne, self.capacity)
        self.southwest = QuadtreeNode(sw, self.capacity)
        self.southeast = QuadtreeNode(se, self.capacity)

        self.divided = True

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        if len(self.points) < self.capacity and not self.divided:
            self.points.append(point)
            return True

        if not self.divided:
            self.subdivide()

            old_points = self.points
            self.points = []
            for p in old_points:
                self._insert_into_children(p)

        return self._insert_into_children(point)

    def _insert_into_children(self, point):
        if self.northwest.insert(point): return True
        if self.northeast.insert(point): return True
        if self.southwest.insert(point): return True
        if self.southeast.insert(point): return True
        return False

    def find_nearest(self, query_point, best_point=None, best_dist=float("inf")):

        boundary_dist = self.boundary.distance_to_point(query_point.x, query_point.y)
        if boundary_dist > best_dist:
            return best_point, best_dist

        for p in self.points:
            d = math.dist((p.x, p.y), (query_point.x, query_point.y))
            if d < best_dist:
                best_dist = d
                best_point = p

        if not self.divided:
            return best_point, best_dist

        children = [
            self.northwest,
            self.northeast,
            self.southwest,
            self.southeast
        ]

        priority_child = None
        for child in children:
            if child.boundary.contains(query_point):
                priority_child = child
                break

        if priority_child:
            best_point, best_dist = priority_child.find_nearest(query_point, best_point, best_dist)

        for child in children:
            if child is priority_child:
                continue
            best_point, best_dist = child.find_nearest(query_point, best_point, best_dist)

        return best_point, best_dist


class Quadtree:
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary
        self.root = QuadtreeNode(boundary, capacity)

    def insert(self, point):
        return self.root.insert(point)

    def find_nearest(self, query_point):
        return self.root.find_nearest(query_point)
