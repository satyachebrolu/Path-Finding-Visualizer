# scripts/smoke_test_phase2.py
from graph.loader import load_graph, get_nearest_node
from graph.builder import RoadGraph
from algorithms.astar import AStarPathfinder

graph = RoadGraph(load_graph("Piedmont, California, USA"))

# Piedmont City Hall → Piedmont High School
origin = get_nearest_node(graph.underlying_graph(), 37.8244, -122.2282)
dest   = get_nearest_node(graph.underlying_graph(), 37.8219, -122.2235)

result = AStarPathfinder(graph).find_path(origin, dest)
print(f"Path: {len(result.path)} nodes")
print(f"Length: {result.path_length_m/1000:.2f} km")
print(f"Explored: {result.nodes_explored} nodes")
print(f"Runtime: {result.runtime_ms:.1f} ms")