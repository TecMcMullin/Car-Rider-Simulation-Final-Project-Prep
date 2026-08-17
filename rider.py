##rider.py

class Rider:
    def __init__(self, rider_id, start_location, destination):
        self.id = rider_id
        self.start_location = start_location
        self.destination = destination

        self.status = "new"
        self.request_time = None
        self.pickup_time = None
        self.dropoff_time = None
