# rider.py

class Rider:
    def __init__(self, rider_id, pickup_location, dropoff_location):
        """
        Args:
            rider_id (str): The unique identifier for the car.
            pickup_location (tuple): The starting (x, y) coordinates.
            dropoff_location (tuple): The ending (x, y) coordinates.
        """
        self.id = rider_id
        self.start_location = pickup_location
        self.destination = dropoff_location
        self.status = 'waiting'
    def __str__(self):
        print(f"--- Rider: {self.id} ---")
        print(f"  Status: {self.status}")
        print(f"  Pickup: {self.start_location}")
        print(f"  Destination: {self.destination}")
        print("--------------------")