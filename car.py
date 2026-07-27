# car.py

from pathfinding import dijkstra, reconstruct_path

class Car:
    def __init__(self, car_id, initial_location):
        self.id = car_id
        self.location = initial_location
        self.status = 'available'
        self.destination = None
        self.route = None
        self.route_time = None

    def __str__(self):
        print(f"--- Car ID: {self.id} ---")
        print(f"  Status: {self.status}")
        print(f"  Location: {self.location}")
        print(f"  Destination: {self.destination}")
        print(f"  Route: {self.route}")
        print(f"  Route Time: {self.route_time}")
        print("--------------------")

    def calculate_route(self, destination, graph):
        
        self.destination = destination

        # Run Dijkstra using the external module
        distances, predecessors = dijkstra(graph, self.location)

        # Build the route
        path = reconstruct_path(predecessors, destination)

        # Store results
        self.route = path
        self.route_time = distances[destination]

        return path, distances[destination]
