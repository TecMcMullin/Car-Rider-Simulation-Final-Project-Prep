## Purpose / Design
Uber Shnuber models a lightweight ride‑sharing system. It tracks:
- Cars (drivers)
- Riders (pickup + dropoff requests)
- A city map (graph‑based)
- An event engine (priority queue)
- A Quadtree for fast nearest‑car lookup

The goal is to simulate how a ride‑sharing service assigns cars, processes events over time, and navigates a map.

## Dijkstra’s Algorithm Use
Dijkstra’s algorithm computes the shortest road‑network travel time between two graph nodes.

In this simplified example map, each location has only one direct connection, so Dijkstra always selects the only available path.  
However, the full routing pipeline is implemented correctly and supports more complex maps with multiple possible routes.

## Quadtree Data Structure
The Quadtree stores available cars as 2D points and supports efficient nearest‑neighbor search.

A naive search checks every car → O(N).  
A Quadtree subdivides space recursively → O(log N) average‑case lookup.

How it works:
- The map is treated as a large rectangle.
- Each node stores up to a fixed capacity of points.
- When full, the node subdivides into four quadrants.
- Nearest‑neighbor search:
  - Prioritizes the quadrant containing the query point.
  - Prunes entire branches if their bounding box is farther than the current best distance.
  - Recursively checks only relevant regions.

This structure allows fast spatial queries and scales better than brute‑force scanning.

## Simulation Engine Prototype
The simulation engine is a discrete‑event system that processes ride activity in chronological order.  
Instead of updating the world every second, the engine jumps directly to the next meaningful event.

### How the Event Loop Works
The core of the simulation is a min‑heap priority queue.  
Each event is stored as:

    (timestamp, sequence_number, event_type, data)


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




------------------------------------------------------------
# Map-File Format
------------------------------------------------------------
The map file is a CSV describing road edges:
    
    start_node_id,start_x,start_y,end_node_id,end_x,end_y,weight

Example:

    A,0.0,0.0,B,10.0,0.0,10.0
    B,10.0,0.0,C,10.0,10.0,10.0
    C,10.0,10.0,D,0.0,10.0,10.0
    D,0.0,10.0,A,0.0,0.0,10.0

Each row defines:
- Two graph nodes
- Their coordinates
- The travel weight (distance/time)

------------------------------------------------------------
# Event System (Four-Field Event Tuple)
------------------------------------------------------------
Every event in the simulation is a four-field tuple:

    (timestamp, sequence_number, event_type, payload)


### Event Types

| Event | Description |
|--------|-------------|
| `RIDER_REQUEST` | A new rider appears and requests a car. |
| `PICKUP_ARRIVAL` | A dispatched car reaches the rider. |
| `DROPOFF_ARRIVAL` | The car reaches the rider’s destination. |

The event heap safely handles multiple events with identical timestamps.


------------------------------------------------------------
# Car State Transitions
------------------------------------------------------------

Cars move through these states:

| State | Meaning |
|--------|---------|
| `available` | Car is idle and indexed in the Quadtree. |
| `busy` | Car has been dispatched and removed from availability. |
| `en_route_to_pickup` | Car is traveling to the rider. |
| `en_route_to_destination` | Car is carrying the rider. |

Cars are never available during pickup or passenger travel.


------------------------------------------------------------
# Rider State Transitions
------------------------------------------------------------

| State | Meaning |
|--------|---------|
| `new` | Rider created but not yet processed. |
| `waiting` | Rider matched; waiting for pickup. |
| `in_car` | Rider picked up. |
| `completed` | Rider dropped off successfully. |
| `unmatched` | No reachable cars. |
| `unsuccessful` | Destination unreachable. |


------------------------------------------------------------
# Default k Value (Nearest Cars)
------------------------------------------------------------

The Quadtree returns **k = 5** nearest available cars by default.

Change it via:

    --candidate-count N


Example:

    python simulation.py --candidate-count 7



------------------------------------------------------------
# Matching Workflow (Quadtree → Dijkstra)
------------------------------------------------------------

The required matching pipeline:

1. `RIDER_REQUEST` event fires.
2. Convert rider start location → `Point`.
3. Query Quadtree for up to **k nearest cars**.
4. For each candidate:
   - Snap car location to nearest graph vertex.
   - Snap rider start to nearest graph vertex.
   - Run Dijkstra.
   - Skip unreachable candidates.
5. Select the reachable candidate with minimum travel time.
6. Dispatch car.
7. Remove car from all availability structures.
8. Schedule `PICKUP_ARRIVAL`.
9. At pickup:
   - Run Dijkstra for rider trip.
   - Schedule `DROPOFF_ARRIVAL`.
10. At dropoff:
    - Update car location.
    - Reinsert car into Quadtree using a new immutable Point.


------------------------------------------------------------
# Availability Structures (Synchronization Guarantee)
------------------------------------------------------------

The simulation maintains three synchronized structures:

1. `available_cars`
2. `available_car_points`
3. `available_car_quadtree`

The invariant:

    set(available_cars)
    == set(available_car_points)
    == IDs stored in available_car_quadtree


Synchronization is enforced by:

- `add_available_car(car)`
- `remove_available_car(car)`

These are the only legal ways to modify availability.


------------------------------------------------------------
# Policy for Unavailable Cars & Unreachable Routes
------------------------------------------------------------

### Unavailable Cars
If no cars are available:
- Rider is marked `unmatched`
- Count increments `total_riders_unmatched`
- Simulation continues (does NOT stall)

### Unreachable Routes
If Dijkstra cannot reach:
- Rider start → car, or
- Pickup → destination

Then:
- Rider marked `unsuccessful`
- Car’s busy time is added
- Car is returned to availability
- No event is scheduled at infinity
- Simulation state remains consistent


------------------------------------------------------------
# Metrics Definitions
------------------------------------------------------------

The simulation reports:

### Rider Metrics
- Total riders generated
- Total riders completed
- Total unmatched riders
- Total unsuccessful riders
- Average wait time
- Average trip duration

### Car Metrics
- Trips completed per car
- Driver utilization:


Simulation span = final processed event time.


------------------------------------------------------------
# Analytical Visualization (simulation_summary.png)
------------------------------------------------------------

The PNG includes:

### Final car locations (map)
Scatter plot of all cars after simulation ends.

### Metrics area
Displayed using `plt.text()`.

### Chart
One of:
- Trips completed per car
- Rider wait-time distribution
- Completed vs unmatched riders

Saved automatically as:

    simulation_summary.png

## How to Run

## Dependencies
    matplotlib
    python 3.10 +

### Install dependencies
~~~bash
   pip install -r requirements.txt
~~~
### Run Test
~~~bash
    python3 test.py
~~~

No other external libraries are required. All routing, spatial indexing, and event processing are implemented from scratch.


------------------------------------------------------------
# Command-Line Options
------------------------------------------------------------

Run the simulation:
~~~bash
    python3 simulation.py [options] [options] ...
~~~

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--max-time` | float | 300.0 | Stop generating new riders after this simulation time. |
| `--num-riders` | int | 100 | Maximum number of riders to generate. |
| `--num-cars` | int | 100 | Number of cars inserted into the Quadtree at startup. |
| `--candidate-count` | int | 5 | Number of nearest cars returned by the Quadtree. |
| `--random-seed` | int | 42 | Makes simulation deterministic. |
| `--map-file` | str | city_map.csv | Road network file. |

### Examples
~~~bash
    python3 simulation.py --max-time 300 --num-riders 200 --num-cars 50 --candidate-count 7 --random-seed 99
~~~



    