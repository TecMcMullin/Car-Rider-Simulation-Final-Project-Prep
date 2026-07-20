# simulation.py

from graph import Graph

class Simulation:
    def __init__(self, map_filename):
        # Existing structures
        self.cars = {}
        self.riders = {}

        # Load the map
        self.city_map = Graph()
        self.city_map.load_from_file(map_filename)
        self.city_map.display()
