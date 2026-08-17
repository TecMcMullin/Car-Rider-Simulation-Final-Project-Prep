##simulation.py

import argparse
import heapq
import random

from graph import Graph
from quadtree import Quadtree, Rectangle, Point
from car import Car
from rider import Rider
from pathfinding import find_nearest_vertex, dijkstra, reconstruct_path
import matplotlib.pyplot as plt

DEFAULT_CANDIDATE_COUNT = 5
MEAN_ARRIVAL_TIME = 30.0


class Simulation:
    def __init__(self, args):
        self.max_time = args.max_time
        self.num_riders = args.num_riders
        self.num_cars = args.num_cars
        self.candidate_count = args.candidate_count
        self.map_file = args.map_file

        if args.random_seed is not None:
            random.seed(args.random_seed)

        self.graph = Graph()
        self.graph.load_map_data(self.map_file)

        # Map boundary (simple bounding box from node coordinates)
        xs = [x for x, y in self.graph.node_coordinates.values()]
        ys = [y for x, y in self.graph.node_coordinates.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        self.map_boundary = Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)

        self.events = []
        self.current_time = 0.0
        self.sequence_counter = 0

        self.available_cars = {}
        self.available_car_points = {}
        self.available_car_quadtree = Quadtree(self.map_boundary, capacity=4)

        self.all_cars = []
        self.riders = {}
        self.next_rider_id = 0
        self.generated_riders = 0

        # Metrics
        self.total_riders_generated = 0
        self.total_riders_completed = 0
        self.total_riders_unmatched = 0
        self.total_riders_unsuccessful = 0
        self.total_wait_time = 0.0
        self.total_trip_time = 0.0
        self.final_event_time = 0.0
        self.event_log = []

        self.initialize_cars()

        if self.should_generate_more_riders():
            rider = self.create_random_rider()
            self.riders[rider.id] = rider
            self.schedule_event(0.0, "RIDER_REQUEST", rider)

    def log(self, message):
        entry = f"TIME {self.current_time}: {message}"
        print(entry)
        self.event_log.append(entry)

    def schedule_event(self, timestamp, event_type, data):
        if timestamp == float("inf"):
            raise ValueError("Cannot schedule event at infinity.")
        self.sequence_counter += 1
        heapq.heappush(
            self.events,
            (timestamp, self.sequence_counter, event_type, data),
        )

    def initialize_cars(self):
        for i in range(self.num_cars):
            x = random.uniform(self.map_boundary.x, self.map_boundary.x + self.map_boundary.width)
            y = random.uniform(self.map_boundary.y, self.map_boundary.y + self.map_boundary.height)
            car = Car(i, (x, y))
            self.all_cars.append(car)
            self.add_available_car(car)

    def add_available_car(self, car):
        if car.id in self.available_cars or car.id in self.available_car_points:
            raise ValueError(f"Car {car.id} already available.")

        point = Point(car.location[0], car.location[1], data=car)
        inserted = self.available_car_quadtree.insert(point)
        if not inserted:
            raise ValueError(f"Car {car.id} at {car.location} outside Quadtree boundary.")

        self.available_cars[car.id] = car
        self.available_car_points[car.id] = point
        car.status = "available"

    def remove_available_car(self, car):
        if car.id not in self.available_car_points:
            raise ValueError(f"Car {car.id} not currently available.")
        point = self.available_car_points[car.id]
        removed = self.available_car_quadtree.remove(point)
        if not removed:
            raise RuntimeError(f"Quadtree removal failed for car {car.id}.")
        del self.available_car_points[car.id]
        del self.available_cars[car.id]
        car.status = "busy"

    def should_generate_more_riders(self):
        if self.max_time is None and self.num_riders is None:
            return True
        if self.max_time is not None and self.current_time >= self.max_time:
            return False
        if self.num_riders is not None and self.generated_riders >= self.num_riders:
            return False
        return True

    def create_random_rider(self):
        rider_id = self.next_rider_id
        self.next_rider_id += 1

        x1 = random.uniform(self.map_boundary.x, self.map_boundary.x + self.map_boundary.width)
        y1 = random.uniform(self.map_boundary.y, self.map_boundary.y + self.map_boundary.height)
        x2 = random.uniform(self.map_boundary.x, self.map_boundary.x + self.map_boundary.width)
        y2 = random.uniform(self.map_boundary.y, self.map_boundary.y + self.map_boundary.height)

        rider = Rider(rider_id, (x1, y1), (x2, y2))
        return rider

    def generate_rider_request(self):
        if not self.should_generate_more_riders():
            return

        rider = self.create_random_rider()
        self.riders[rider.id] = rider
        self.generated_riders += 1
        self.total_riders_generated += 1

        self.schedule_event(self.current_time, "RIDER_REQUEST", rider)

        interval = random.expovariate(1.0 / MEAN_ARRIVAL_TIME)
        next_time = self.current_time + interval
        if self.max_time is not None and next_time > self.max_time:
            return

        next_rider = self.create_random_rider()
        self.riders[next_rider.id] = next_rider
        self.schedule_event(next_time, "RIDER_REQUEST", next_rider)

    def select_candidate_cars(self, rider):
        query_point = Point(rider.start_location[0], rider.start_location[1], data=None)
        candidate_points = self.available_car_quadtree.find_k_nearest(
            query_point,
            k=self.candidate_count,
        )
        if not candidate_points:
            rider.status = "unmatched"
            self.total_riders_unmatched += 1
            self.log(f"Rider {rider.id} unmatched (no available cars).")
            return []
        return candidate_points

    def choose_best_car(self, rider, candidate_points):
        graph = self.graph
        rider_vertex = find_nearest_vertex(rider.start_location, graph.node_coordinates)

        best_car = None
        best_route = None
        best_pickup_time = float("inf")

        for point in candidate_points:
            car = point.data
            car_vertex = find_nearest_vertex(car.location, graph.node_coordinates)
            distances, predecessors = dijkstra(graph.adjacency_list, car_vertex)

            if rider_vertex not in distances or distances[rider_vertex] == float("inf"):
                continue

            pickup_time = distances[rider_vertex]
            route = reconstruct_path(predecessors, rider_vertex)

            if pickup_time < best_pickup_time:
                best_pickup_time = pickup_time
                best_route = route
                best_car = car
            elif pickup_time == best_pickup_time and best_car is not None:
                if car.id < best_car.id:
                    best_pickup_time = pickup_time
                    best_route = route
                    best_car = car

        if best_car is None:
            rider.status = "unmatched"
            self.total_riders_unmatched += 1
            self.log(
                f"Rider {rider.id} unmatched (all {len(candidate_points)} candidates unreachable)."
            )
            return None, None, float("inf")

        return best_car, best_route, best_pickup_time

    def dispatch_car_to_rider(self, best_car, rider, best_route, best_pickup_time):
        if best_car is None:
            return

        self.remove_available_car(best_car)
        best_car.status = "en_route_to_pickup"
        best_car.assigned_rider = rider
        best_car.route = best_route
        best_car.route_time = best_pickup_time
        best_car.busy_start_time = self.current_time
        rider.status = "waiting"

        pickup_time = self.current_time + best_pickup_time
        self.schedule_event(pickup_time, "PICKUP_ARRIVAL", best_car)
        self.log(
            f"Dispatch CAR {best_car.id} to RIDER {rider.id}, pickup ETA {best_pickup_time}"
        )

    def handle_rider_request(self, rider):
        if rider.request_time is None:
            rider.request_time = self.current_time

        candidate_points = self.select_candidate_cars(rider)
        if candidate_points:
            best_car, best_route, best_pickup_time = self.choose_best_car(
                rider,
                candidate_points,
            )
            self.dispatch_car_to_rider(best_car, rider, best_route, best_pickup_time)

        if self.should_generate_more_riders():
            self.generate_rider_request()

    def handle_pickup_arrival(self, car):
        rider = car.assigned_rider
        if rider is None:
            raise RuntimeError(f"CAR {car.id} has no assigned rider at pickup.")

        car.location = rider.start_location
        car.status = "en_route_to_destination"
        rider.status = "in_car"
        rider.pickup_time = self.current_time

        wait_time = rider.pickup_time - rider.request_time
        self.total_wait_time += wait_time
        self.log(f"CAR {car.id} picked up RIDER {rider.id} (wait {wait_time})")

        graph = self.graph
        pickup_vertex = find_nearest_vertex(rider.start_location, graph.node_coordinates)
        destination_vertex = find_nearest_vertex(rider.destination, graph.node_coordinates)

        distances, predecessors = dijkstra(graph.adjacency_list, pickup_vertex)

        if destination_vertex not in distances or distances[destination_vertex] == float("inf"):
            self.log(f"Trip for RIDER {rider.id} unsuccessful (destination unreachable).")
            rider.status = "unsuccessful"
            self.total_riders_unsuccessful += 1

            if car.busy_start_time is not None:
                car.total_busy_time += self.current_time - car.busy_start_time
                car.busy_start_time = None

            car.assigned_rider = None
            car.status = "available"
            self.add_available_car(car)
            return

        trip_time = distances[destination_vertex]
        trip_route = reconstruct_path(predecessors, destination_vertex)
        car.route = trip_route
        car.route_time = trip_time

        dropoff_time = self.current_time + trip_time
        self.schedule_event(dropoff_time, "DROPOFF_ARRIVAL", car)
        self.log(
            f"CAR {car.id} en route to destination for RIDER {rider.id} (trip {trip_time})"
        )

    def handle_dropoff_arrival(self, car):
        rider = car.assigned_rider
        if rider is None:
            raise RuntimeError(f"CAR {car.id} reached dropoff with no assigned rider.")

        car.location = rider.destination
        rider.status = "completed"
        rider.dropoff_time = self.current_time
        self.total_riders_completed += 1

        trip_time = rider.dropoff_time - rider.pickup_time
        self.total_trip_time += trip_time

        self.log(f"CAR {car.id} dropped off RIDER {rider.id} (trip {trip_time})")

        if car.busy_start_time is not None:
            car.total_busy_time += self.current_time - car.busy_start_time
            car.busy_start_time = None

        car.trips_completed += 1
        car.assigned_rider = None
        car.status = "available"
        self.add_available_car(car)

    def run(self):
        while self.events:
            timestamp, seq, event_type, data = heapq.heappop(self.events)
            self.current_time = timestamp

            if event_type == "RIDER_REQUEST":
                self.handle_rider_request(data)
            elif event_type == "PICKUP_ARRIVAL":
                self.handle_pickup_arrival(data)
            elif event_type == "DROPOFF_ARRIVAL":
                self.handle_dropoff_arrival(data)
            else:
                raise ValueError(f"Unknown event type: {event_type}")

        self.final_event_time = self.current_time

    def calculate_driver_utilization(self):
        total_busy = sum(car.total_busy_time for car in self.all_cars)
        span = self.final_event_time
        if span <= 0 or self.num_cars <= 0:
            return 0.0
        return total_busy / (self.num_cars * span)

    def print_metrics(self):
        print("\n=== SIMULATION METRICS ===")
        print(f"Total riders generated:     {self.total_riders_generated}")
        print(f"Total riders completed:     {self.total_riders_completed}")
        print(f"Total unmatched riders:     {self.total_riders_unmatched}")
        print(f"Total unsuccessful riders:  {self.total_riders_unsuccessful}")

        avg_wait = (
            self.total_wait_time / self.total_riders_completed
            if self.total_riders_completed > 0 else 0.0
        )
        avg_trip = (
            self.total_trip_time / self.total_riders_completed
            if self.total_riders_completed > 0 else 0.0
        )

        print(f"Average wait time:          {avg_wait:.2f}")
        print(f"Average trip duration:      {avg_trip:.2f}")

        utilization = self.calculate_driver_utilization()
        print(f"Driver utilization:         {utilization:.4f}")

        print("\nTrips completed per car:")
        for car in self.all_cars:
            print(f"  Car {car.id}: {car.trips_completed}")

    def write_log(self, filename="simulation_log.txt"):
        with open(filename, "w") as f:
            for entry in self.event_log:
                f.write(entry + "\n")

    def create_visualization(self, filename="simulation_summary.png"):
        car_x = [car.location[0] for car in self.all_cars]
        car_y = [car.location[1] for car in self.all_cars]
        trips = [car.trips_completed for car in self.all_cars]
        car_ids = [car.id for car in self.all_cars]

        avg_wait = (
            self.total_wait_time / self.total_riders_completed
            if self.total_riders_completed > 0 else 0.0
        )
        avg_trip = (
            self.total_trip_time / self.total_riders_completed
            if self.total_riders_completed > 0 else 0.0
        )
        utilization = self.calculate_driver_utilization()

        fig = plt.figure(figsize=(12, 8))

        ax_map = fig.add_axes([0.05, 0.35, 0.45, 0.6])
        ax_map.scatter(car_x, car_y, c="blue", s=30, label="Cars")
        ax_map.set_title("Final Car Locations")
        ax_map.set_xlabel("X")
        ax_map.set_ylabel("Y")
        ax_map.legend()
        ax_map.set_aspect("equal", adjustable="box")

        ax_metrics = fig.add_axes([0.55, 0.35, 0.4, 0.6])
        ax_metrics.axis("off")
        metrics_text = (
            f"Simulation Metrics\n\n"
            f"Total riders generated:     {self.total_riders_generated}\n"
            f"Total riders completed:     {self.total_riders_completed}\n"
            f"Total unmatched riders:     {self.total_riders_unmatched}\n"
            f"Total unsuccessful riders:  {self.total_riders_unsuccessful}\n\n"
            f"Average wait time:          {avg_wait:.2f}\n"
            f"Average trip duration:      {avg_trip:.2f}\n"
            f"Driver utilization:         {utilization:.4f}\n"
        )
        ax_metrics.text(
            0.0,
            1.0,
            metrics_text,
            va="top",
            ha="left",
            fontsize=10,
            family="monospace",
        )

        ax_chart = fig.add_axes([0.05, 0.05, 0.9, 0.25])
        ax_chart.bar(car_ids, trips, color="green")
        ax_chart.set_title("Trips Completed per Car")
        ax_chart.set_xlabel("Car ID")
        ax_chart.set_ylabel("Trips Completed")

        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-time", type=float, default=None)
    parser.add_argument("--num-riders", type=int, default=None)
    parser.add_argument("--num-cars", type=int, default=100)
    parser.add_argument("--candidate-count", type=int, default=DEFAULT_CANDIDATE_COUNT)
    parser.add_argument("--random-seed", type=int, default=None)
    parser.add_argument("--map-file", type=str, default="city_map.csv")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sim = Simulation(args)
    sim.run()
    sim.print_metrics()
    sim.write_log()
    sim.create_visualization("simulation_summary.png")
