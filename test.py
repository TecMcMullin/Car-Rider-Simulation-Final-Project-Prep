# test.py

from graph import Graph
from car import Car


def main():

    city_map = Graph()
    city_map.load_from_file("map.csv")

    car = Car("CAR-1", "NY")

    destination = "TX"

    car.calculate_route(destination, city_map.adj_list)
    car.__str__()

    city_map.display()

if __name__ == "__main__":
    main()
