# test.py

from graph import Graph
from car import Car


def main():

    city_map = Graph()
    city_map.load_from_file("map.csv")

    car = Car("CAR-1", "NY")

    destination = "TX"

    route, total_time = car.calculate_route(destination, city_map.adj_list)

    print("\n=== Test Results ===")
    print(f"Car ID: {car.id}")
    print(f"Start: {car.location}")
    print(f"Destination: {destination}")
    print(f"Route: {car.route}")
    print(f"Total Distance: {car.route_time}")
    print("====================\n")

    city_map.display()

if __name__ == "__main__":
    main()
