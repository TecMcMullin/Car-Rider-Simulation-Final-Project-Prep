##car.py

from pathfinding import find_nearest_vertex, dijkstra, reconstruct_path


class Car:
    def __init__(self, car_id, initial_location):
        self.id = car_id
        self.location = initial_location
        self.status = "available"
        self.assigned_rider = None
        self.route = None
        self.route_time = float("inf")
        self.busy_start_time = None
        self.total_busy_time = 0.0
        self.trips_completed = 0

    def calculate_route(self, destination, graph):
        start_vertex = find_nearest_vertex(self.location, graph.node_coordinates)
        end_vertex = find_nearest_vertex(destination, graph.node_coordinates)

        distances, predecessors = dijkstra(graph.adjacency_list, start_vertex)

        if end_vertex not in distances or distances[end_vertex] == float("inf"):
            self.route = None
            self.route_time = float("inf")
            return None, float("inf")

        route = reconstruct_path(predecessors, end_vertex)
        self.route = route
        self.route_time = distances[end_vertex]
        return route, distances[end_vertex]
