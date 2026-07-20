# graph.py
import csv

class Graph:
    def __init__(self):
        self.adj_list = {}

    def add_vertex(self, vertex):
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []

    def add_edge(self, v1, v2, weight):
        self.add_vertex(v1)
        self.add_vertex(v2)
        self.adj_list[v1].append((v2, float(weight)))

    def load_from_file(self, filename):
        print(f"Loading map from {filename}...")
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 3:
                        start, end, weight = row
                        self.add_edge(start.strip(), end.strip(), weight.strip())
            print("Map loaded successfully.")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def display(self):
        print("\n--- Graph Adjacency List ---")
        for vertex, neighbors in self.adj_list.items():
            neighbor_str = ", ".join([f"({n}, {w})" for n, w in neighbors])
            print(f"{vertex} -> [{neighbor_str}]")
        print("----------------------------")

if __name__ == "__main__":
    city_map = Graph()
    city_map.load_from_file('map.csv')
    city_map.display()
