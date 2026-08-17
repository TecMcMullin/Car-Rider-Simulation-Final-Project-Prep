##pathfinding.py

import heapq


def find_nearest_vertex(point, node_coordinates):
    if not node_coordinates:
        raise ValueError("No graph vertices loaded (node_coordinates is empty).")

    px, py = point
    best_node = None
    best_dist_sq = float("inf")

    for node_id, (nx, ny) in node_coordinates.items():
        dist_sq = (nx - px) ** 2 + (ny - py) ** 2
        if dist_sq < best_dist_sq:
            best_dist_sq = dist_sq
            best_node = node_id

    return best_node


def dijkstra(adjacency_list, start):
    distances = {start: 0.0}
    predecessors = {}
    heap = [(0.0, start)]

    while heap:
        dist, node = heapq.heappop(heap)
        if dist > distances.get(node, float("inf")):
            continue

        for neighbor, weight in adjacency_list.get(node, []):
            nd = dist + weight
            if nd < distances.get(neighbor, float("inf")):
                distances[neighbor] = nd
                predecessors[neighbor] = node
                heapq.heappush(heap, (nd, neighbor))

    return distances, predecessors


def reconstruct_path(predecessors, end):
    path = []
    current = end
    while current in predecessors:
        path.append(current)
        current = predecessors[current]
    path.append(current)
    path.reverse()
    return path
