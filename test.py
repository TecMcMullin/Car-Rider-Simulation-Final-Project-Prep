# test.py

from simulation import Simulation
from car import Car
from rider import Rider

def main():
    sim = Simulation()

    car1 = Car("car_1", (0, 0))
    car2 = Car("car_2", (5, 5))

    sim.cars[car1.id] = car1
    sim.cars[car2.id] = car2

    rider1 = Rider("rider_1", (2, 3), (10, 10))
    rider2 = Rider("rider_2", (1, 1), (8, 4))

    sim.riders[rider1.id] = rider1
    sim.riders[rider2.id] = rider2

    print("\n=== Cars in Simulation ===")
    for car_id, car_obj in sim.cars.items():
        print(f"Car key: {car_id}")
        car_obj.__str__()

    print("\n=== Riders in Simulation ===")
    for rider_id, rider_obj in sim.riders.items():
        print(f"Rider key: {rider_id}")
        rider_obj.__str__()

    print("\n=== Lookup Example ===")
    lookup_id = "car_1"
    print(f"Looking up {lookup_id}...")
    sim.cars[lookup_id].__str__()

    lookup_id = "rider_2"
    print(f"Looking up {lookup_id}...")
    sim.riders[lookup_id].__str__()

if __name__ == "__main__":
    main()
