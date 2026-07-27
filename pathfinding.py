import heapq
import math

def dijkstra(graph, start_node):
    distances = {node: math.inf for node in graph}
    distances[start_node] = 0

    predecessors = {node: None for node in graph}
    priority_queue = [(0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances, predecessors


def reconstruct_path(predecessors, end_node):
    path = []
    current = end_node
    while current is not None:
        path.insert(0, current)
        current = predecessors[current]
    return path
