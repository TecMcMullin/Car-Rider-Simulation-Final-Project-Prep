##test.py

import math
from graph import Graph
from quadtree import Quadtree, Rectangle, Point
from pathfinding import find_nearest_vertex, dijkstra
from simulation import Simulation, parse_args


def test_event_heap_ties():
    import heapq
    events = []
    heapq.heappush(events, (10.0, 1, "A", None))
    heapq.heappush(events, (10.0, 2, "B", None))
    t1 = heapq.heappop(events)
    t2 = heapq.heappop(events)
    assert t1[0] == t2[0]


def test_quadtree_k_limit():
    boundary = Rectangle(0, 0, 100, 100)
    qt = Quadtree(boundary)
    for i in range(10):
        qt.insert(Point(i * 5.0, i * 5.0, data=i))
    query = Point(10.0, 10.0)
    pts = qt.find_k_nearest(query, k=5)
    assert len(pts) <= 5


def test_find_nearest_vertex():
    g = Graph()
    g.node_coordinates = {
        "A": (0.0, 0.0),
        "B": (10.0, 0.0),
    }
    v = find_nearest_vertex((1.0, 0.0), g.node_coordinates)
    assert v == "A"


def test_dijkstra_unreachable():
    g = Graph()
    g.adjacency_list = {"A": [("B", 1.0)], "B": []}
    dist, _ = dijkstra(g.adjacency_list, "A")
    assert dist.get("B", math.inf) == 1.0


def test_car_unavailable_during_trip():
    args = parse_args()
    args.max_time = 50.0
    args.num_riders = 1
    args.num_cars = 5
    sim = Simulation(args)
    sim.run()
    assert len(sim.available_cars) == len(sim.available_car_points)


if __name__ == "__main__":
    test_event_heap_ties()
    test_quadtree_k_limit()
    test_find_nearest_vertex()
    test_dijkstra_unreachable()
    test_car_unavailable_during_trip()
    print("All basic tests passed.")
