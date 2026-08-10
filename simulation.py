# simulation.py

import heapq
import math
from graph import Graph

TRAVEL_SPEED_FACTOR = 1.0  # Tune as needed


class Simulation:
    def __init__(self, map_filename):
        self.cars = {}
        self.riders = {}

        self.current_time = 0

        # Min-heap event queue
        self.event_queue = []

        # Load map (still used for future milestones)
        self.city_map = Graph()
        self.city_map.load_from_file(map_filename)
        self.city_map.display()

        # Sequence counter to break ties in heap ordering
        self.sequence_counter = 0

    def schedule_event(self, timestamp, event_type, data):
        """
        Event tuple format:
        (timestamp, sequence_number, event_type, data)
        """
        self.sequence_counter += 1
        event = (timestamp, self.sequence_counter, event_type, data)
        heapq.heappush(self.event_queue, event)

    def find_closest_car_brute_force(self, rider_location):
        best_car = None
        best_dist = math.inf

        for car in self.cars.values():
            if car.status == "available":
                cx, cy = car.location
                rx, ry = rider_location
                dist = abs(cx - rx) + abs(cy - ry)

                if dist < best_dist:
                    best_dist = dist
                    best_car = car

        return best_car

    def calculate_travel_time(self, start_location, end_location):
        x1, y1 = start_location
        x2, y2 = end_location
        distance = abs(x1 - x2) + abs(y1 - y2)
        return distance * TRAVEL_SPEED_FACTOR

    def handle_rider_request(self, rider):
        car = self.find_closest_car_brute_force(rider.start_location)

        if car is None:
            print(f"TIME {self.current_time}: No available cars for rider {rider.id}")
            return
        car.assigned_rider = rider
        car.status = "en_route_to_pickup"

        pickup_duration = self.calculate_travel_time(car.location, rider.start_location)
        arrival_time = self.current_time + pickup_duration

        print(f"TIME {self.current_time}: CAR {car.id} dispatched to RIDER {rider.id}")

        self.schedule_event(arrival_time, "ARRIVAL", car)

    def handle_arrival(self, car):
        rider = car.assigned_rider

        if car.status == "en_route_to_pickup":
            print(f"TIME {self.current_time}: CAR {car.id} picked up RIDER {rider.id}")

            car.location = rider.start_location
            car.status = "en_route_to_destination"
            rider.status = "in_car"

            dropoff_duration = self.calculate_travel_time(rider.start_location, rider.destination)
            arrival_time = self.current_time + dropoff_duration

            self.schedule_event(arrival_time, "ARRIVAL", car)

        elif car.status == "en_route_to_destination":
            print(f"TIME {self.current_time}: CAR {car.id} dropped off RIDER {rider.id}")

            car.location = rider.destination
            car.status = "available"
            rider.status = "completed"

            car.assigned_rider = None


    def run(self):
        while self.event_queue:
            timestamp, seq, event_type, data = heapq.heappop(self.event_queue)

            self.current_time = timestamp

            if event_type == "RIDER_REQUEST":
                self.handle_rider_request(data)

            elif event_type == "ARRIVAL":
                self.handle_arrival(data)
