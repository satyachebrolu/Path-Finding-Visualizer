# scripts/smoke_test_phase3.py
import sys
sys.path.insert(0, ".")

from graph.loader import load_graph, get_nearest_node
from graph.builder import RoadGraph
from algorithms.astar import AStarPathfinder
from visualization.map_view import render_search_result, save_map
from metrics.performance import metrics_from_result
import webbrowser

graph = RoadGraph(load_graph("Piedmont, California, USA"))
origin = get_nearest_node(graph.underlying_graph(), 37.8244, -122.2282)
dest   = get_nearest_node(graph.underlying_graph(), 37.8219, -122.2235)

result = AStarPathfinder(graph).find_path(origin, dest)

metrics = metrics_from_result(result, "A*", origin, dest)
print(metrics.summary_line())

fmap = render_search_result(graph, result, origin, dest)
save_map(fmap, "data/phase3_result.html")
print("Map saved → data/phase3_result.html")
webbrowser.open("data/phase3_result.html")