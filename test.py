# test.py

from simulation import Simulation
from rider import Rider
from car import Car

sim = Simulation("map.csv")

sim.cars["C1"] = Car("C1", (10, 10))
sim.cars["C2"] = Car("C2", (50, 50))
sim.cars["C3"] = Car("C3", (100, 100))

r1 = Rider("R1", (20, 20), (80, 80))
r2 = Rider("R2", (60, 60), (10, 10))

sim.riders["R1"] = r1
sim.riders["R2"] = r2

sim.schedule_event(0, "RIDER_REQUEST", r1)
sim.schedule_event(5, "RIDER_REQUEST", r2)

sim.run()
