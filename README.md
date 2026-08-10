# Uber Shnuber

## Purpose / Design
Main purpose is to create a travel app for drivers to pick up riders. This will help keep track of all of the drivers and riders for a minimalist setup.
## Dijkstra's Algorithm Use
Dijkstra's algorithm is used to figure out the shortest distance of different locations, but because all of the locations in this example have only one path it just picks that path.
## Map Data Format
The locations set in this map for csv are NY, TX, and CA. They are set in the file as follows
~~~csv
    Place A, Place B, Distance
    Place B, Place A, Distance
    ETC, ETC, ETC
~~~

## Quadtree Data Structure
The purpose of a quadtree data structure is to place points on a grid and allow point to be subdivided for more accuracy when finding paths. It uses the efficient nearest-neighbor search method to do this. It checks the priority locations first to move because those points are necessary to find a path. Then it moves through the grid checking the main points for verification, then goes in further if it ends up being the correct point. Instead of using O(N) which just makes the grid bigger on a 2d sense, It uses O(logN) which is a way to subdivide points turning it into a 3d grid making it faster to move throughout the grid.

## Simulation Engine Prototype
The simulation engine is a **discrete‑event system** that processes ride activity in chronological order. Instead of updating the world every second, the engine jumps directly to the next meaningful event.

### How the Event Loop Works
The core of the simulation is a **min‑heap priority queue**.
The engine repeatedly:

1. Pops the next event from the heap  
2. Advances the simulation clock to that event’s timestamp  
3. Executes the correct handler based on `event_type`  
4. Schedules any future events created by that handler  

This allows the simulation to model:

- Rider requests  
- Car dispatch  
- Pickup arrival  
- Dropoff arrival  

Each event updates the state of cars and riders, ensuring the system behaves like a simplified ride‑sharing service.

## How to Run
~~~bash
    python3 test.py
~~~

## Dependencies
    Python 3.14.0