# scripts/test_visualization.py
"""
Manually verify map rendering works before Streamlit integration.
Run: python -m scripts.test_visualization
Opens result.html in your default browser.
"""
import webbrowser
import sys
sys.path.insert(0, ".")

from graph.loader import load_graph, get_nearest_node
from graph.builder import RoadGraph
from algorithms.astar import AStarPathfinder
from visualization.map_view import render_search_result, save_map

graph = RoadGraph(load_graph("Piedmont, California, USA"))
origin = get_nearest_node(graph.underlying_graph(), 37.8244, -122.2282)
dest   = get_nearest_node(graph.underlying_graph(), 37.8219, -122.2235)

result = AStarPathfinder(graph).find_path(origin, dest)
fmap = render_search_result(graph, result, origin, dest)
save_map(fmap, "data/result.html")
print("Saved → data/result.html")
webbrowser.open("data/result.html")