"""
Renders road network and paths as interactive Folium maps.

Folium produces Leaflet.js HTML files — no server needed, opens in any browser,
and embeds cleanly in Streamlit via st.components.v1.html().

Design decisions:
- Map is rebuilt on each call rather than mutated, keeping the interface pure.
- Explored nodes are passed in full so the caller controls what subset to show
  (supports both full render and progressive animation frames).
- Returns the Folium Map object so callers can either save it or pass it to
  Streamlit — visualization layer stays decoupled from the UI layer.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import folium

if TYPE_CHECKING:
    from graph.builder import RoadGraph
    from algorithms.base import SearchResult


# Visual constants — tweak these freely
EXPLORED_NODE_COLOR   = "#4A90D9"   # blue
EXPLORED_NODE_RADIUS  = 4
PATH_COLOR            = "#E8453C"   # red
PATH_WEIGHT           = 5
PATH_OPACITY          = 0.8
ORIGIN_COLOR          = "#2ECC71"   # green
DESTINATION_COLOR     = "#E74C3C"   # red
MARKER_RADIUS         = 8


def build_base_map(road_graph: "RoadGraph", zoom_start: int = 14) -> folium.Map:
    """
    Create a Folium map centred on the road network's bounding box midpoint.

    Args:
        road_graph: The loaded road network.
        zoom_start: Initial zoom level (14 works well for city neighbourhoods).

    Returns:
        folium.Map with a CartoDB Positron tile layer (clean, low-contrast).
    """
    # Compute centre from node coordinates
    lats = [road_graph.get_node(n).lat for n in _sample_nodes(road_graph, 200)]
    lngs = [road_graph.get_node(n).lng for n in _sample_nodes(road_graph, 200)]
    centre_lat = (min(lats) + max(lats)) / 2
    centre_lng = (min(lngs) + max(lngs)) / 2

    return folium.Map(
        location=[centre_lat, centre_lng],
        zoom_start=zoom_start,
        tiles="CartoDB positron",
    )


def render_search_result(
    road_graph: "RoadGraph",
    result: "SearchResult",
    origin_node: int,
    destination_node: int,
    explored_limit: int | None = None,
) -> folium.Map:
    """
    Render a completed A* search on a Folium map.

    Layers (bottom to top):
      1. Explored nodes  — blue dots showing the search frontier
      2. Path            — red polyline connecting origin to destination
      3. Origin marker   — green circle
      4. Destination marker — red circle

    Args:
        road_graph:        Road network.
        result:            SearchResult from AStarPathfinder.find_path().
        origin_node:       Node ID of the start point.
        destination_node:  Node ID of the end point.
        explored_limit:    If set, only render the first N explored nodes.
                           Used by render_animation_frame() for progressive display.

    Returns:
        folium.Map ready to save or display.
    """
    fmap = build_base_map(road_graph)

    # --- Layer 1: explored nodes ---
    explored = result.explored
    if explored_limit is not None:
        explored = explored[:explored_limit]

    for node_id in explored:
        node = road_graph.get_node(node_id)
        folium.CircleMarker(
            location=[node.lat, node.lng],
            radius=EXPLORED_NODE_RADIUS,
            color=EXPLORED_NODE_COLOR,
            fill=True,
            fill_color=EXPLORED_NODE_COLOR,
            fill_opacity=0.6,
            weight=1,
            tooltip=f"Explored: {node_id}",
        ).add_to(fmap)

    # --- Layer 2: path polyline ---
    if result.path:
        path_coords = [
            [road_graph.get_node(n).lat, road_graph.get_node(n).lng]
            for n in result.path
        ]
        folium.PolyLine(
            locations=path_coords,
            color=PATH_COLOR,
            weight=PATH_WEIGHT,
            opacity=PATH_OPACITY,
            tooltip=f"Path: {result.path_length_m/1000:.2f} km",
        ).add_to(fmap)

    # --- Layer 3: origin / destination markers ---
    _add_pin(fmap, road_graph.get_node(origin_node), "Origin", ORIGIN_COLOR)
    _add_pin(fmap, road_graph.get_node(destination_node), "Destination", DESTINATION_COLOR)

    return fmap


def render_animation_frame(
    road_graph: "RoadGraph",
    result: "SearchResult",
    origin_node: int,
    destination_node: int,
    frame_index: int,
) -> folium.Map:
    """
    Render a single animation frame showing exploration up to frame_index nodes.

    Intended to be called in a loop by visualization/animation.py.
    Only draws the path overlay on the final frame (when all nodes are shown).

    Args:
        frame_index: Number of explored nodes to show (0 = just the markers).

    Returns:
        folium.Map for this frame.
    """
    is_final_frame = frame_index >= len(result.explored)

    partial_result = result if is_final_frame else _result_without_path(result)

    return render_search_result(
        road_graph=road_graph,
        result=partial_result,
        origin_node=origin_node,
        destination_node=destination_node,
        explored_limit=frame_index,
    )


def save_map(fmap: folium.Map, path: str) -> None:
    """Save a Folium map to an HTML file."""
    fmap.save(path)


# ------------------------------------------------------------------ #
# Private helpers                                                      #
# ------------------------------------------------------------------ #

def _add_pin(
    fmap: folium.Map, node, label: str, color: str
) -> None:
    folium.CircleMarker(
        location=[node.lat, node.lng],
        radius=MARKER_RADIUS,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        weight=2,
        tooltip=label,
        popup=folium.Popup(f"<b>{label}</b><br>Node: {node.node_id}", max_width=150),
    ).add_to(fmap)


def _sample_nodes(road_graph: "RoadGraph", n: int) -> list[int]:
    """Return up to n node IDs for bounding-box computation."""
    # RoadGraph doesn't expose an iterator, so we use the underlying graph
    all_nodes = list(road_graph.underlying_graph().nodes())
    step = max(1, len(all_nodes) // n)
    return all_nodes[::step]


def _result_without_path(result: "SearchResult") -> "SearchResult":
    """Return a copy of result with an empty path (for mid-animation frames)."""
    from algorithms.base import SearchResult as SR
    return SR(
        path=[],
        explored=result.explored,
        path_length_m=0.0,
        nodes_explored=result.nodes_explored,
        runtime_ms=result.runtime_ms,
    )