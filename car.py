# car.py

class Car:
    def __init__(self, car_id, initial_location):
        """
        Initializes a new Car object.

        Args:
            car_id (str): The unique identifier for the car.
            initial_location (tuple): The starting (x, y) coordinates.
        """
        self.id = car_id
        self.location = initial_location
        self.status = 'available'
        self.destination = None

    def __str__(self):
        print(f"--- Car ID: {self.id} ---")
        print(f"  Status: {self.status}")
        print(f"  Location: {self.location}")
        print(f"  Destination: {self.destination}")
        print("--------------------")