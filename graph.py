##graph.py

import collections


class Graph:
    def __init__(self):
        self.adjacency_list = collections.defaultdict(list)
        self.node_coordinates = {}

    def load_map_data(self, filename):
        with open(filename, "r") as file:
            for line in file:
                if line.startswith("#") or not line.strip():
                    continue

                parts = line.strip().split(",")

                (
                    start_id,
                    start_x,
                    start_y,
                    end_id,
                    end_x,
                    end_y,
                    weight,
                ) = parts

                self.node_coordinates[start_id] = (
                    float(start_x),
                    float(start_y),
                )

                self.node_coordinates[end_id] = (
                    float(end_x),
                    float(end_y),
                )

                self.adjacency_list[start_id].append(
                    (end_id, float(weight))
                )

                self.adjacency_list[end_id].append(
                    (start_id, float(weight))
                )
