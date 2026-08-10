# car.py

class Car:
    def __init__(self, car_id, initial_location):

        self.id = car_id
        self.location = initial_location
        self.status = 'available'
        self.destination = None
        self.route = None
        self.route_time = None
        self.assigned_rider = None

    def __str__(self):
        print(f"--- Car ID: {self.id} ---")
        print(f"  Status: {self.status}")
        print(f"  Location: {self.location}")
        print(f"  Destination: {self.destination}")
        print(f"  Route: {self.route}")
        print(f"  Route Time: {self.route_time}")
        print(f"  Assigned Rider: {self.assigned_rider.id if self.assigned_rider else None}")
        print("--------------------")
