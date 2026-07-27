from graph import Graph
from pathfinding import dijkstra,reconstruct_path

if __name__ == "__main__":
    # Define the graph from our conceptual walkthrough
    map_filename = "map.csv"
    city_map = Graph()
    city_map.load_from_file(map_filename)
    city_map.display()

    start_location = 'NY'
    distances, predecessors = dijkstra(city_map.adj_list, start_location)

    print(f"Finding shortest paths from node '{start_location}':\n")
    print("Distances to all nodes:")
    for node, distance in distances.items():
        print(f"  - Distance to {node}: {distance}")

    print("\nPredecessor map for path reconstruction:")
    print(predecessors)

    # Example: Reconstruct and print the path to node 'D'
    target_destination = 'TX'
    shortest_path_to_d = reconstruct_path(predecessors, target_destination)

    print(f"\nShortest path to '{target_destination}': {' -> '.join(shortest_path_to_d)}")
    print(f"Total distance: {distances[target_destination]}")