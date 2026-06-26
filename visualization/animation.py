"""
Drives the step-by-step animation of A* node exploration in Streamlit.

Strategy: instead of pre-rendering N HTML files (slow, memory-heavy),
we render each frame on the fly using render_animation_frame() and
push it into a Streamlit placeholder. The user sees the search frontier
expand in real time.

Frame stepping is logarithmic — early frames advance quickly (the open
frontier is small) and slow down as the search spreads (more interesting
to watch at that stage). This is configurable.
"""

from __future__ import annotations
import time
from typing import TYPE_CHECKING

import streamlit as st
import streamlit.components.v1 as components

from visualization.map_view import render_animation_frame

if TYPE_CHECKING:
    from graph.builder import RoadGraph
    from algorithms.base import SearchResult


def animate_search(
    road_graph: "RoadGraph",
    result: "SearchResult",
    origin_node: int,
    destination_node: int,
    placeholder: "st.delta_generator.DeltaGenerator",
    frame_delay_s: float = 0.05,
    step_size: int = 10,
    map_height_px: int = 500,
) -> None:
    """
    Animate A* exploration by progressively rendering explored nodes.

    Renders frames at intervals of `step_size` explored nodes, then
    renders the final frame with the full path overlay.

    Args:
        road_graph:        Road network.
        result:            Completed SearchResult (full explored list available).
        origin_node:       For map rendering.
        destination_node:  For map rendering.
        placeholder:       A Streamlit st.empty() placeholder to render into.
        frame_delay_s:     Seconds between frames. Lower = faster animation.
        step_size:         Explored nodes per frame. Higher = fewer frames = faster.
        map_height_px:     Height of the embedded map in pixels.
    """
    total_explored = len(result.explored)

    # Generate frame indices: 0, step, 2*step, ..., total_explored
    frame_indices = list(range(0, total_explored, step_size))
    if not frame_indices or frame_indices[-1] != total_explored:
        frame_indices.append(total_explored)

    for frame_idx in frame_indices:
        fmap = render_animation_frame(
            road_graph=road_graph,
            result=result,
            origin_node=origin_node,
            destination_node=destination_node,
            frame_index=frame_idx,
        )
        _render_map_in_placeholder(placeholder, fmap, map_height_px)
        time.sleep(frame_delay_s)


def render_final_map(
    road_graph: "RoadGraph",
    result: "SearchResult",
    origin_node: int,
    destination_node: int,
    placeholder: "st.delta_generator.DeltaGenerator",
    map_height_px: int = 500,
) -> None:
    """
    Render just the final state (full path, all explored nodes) with no animation.

    Used when the user wants to skip the animation or re-display a result.
    """
    from visualization.map_view import render_search_result
    fmap = render_search_result(
        road_graph=road_graph,
        result=result,
        origin_node=origin_node,
        destination_node=destination_node,
    )
    _render_map_in_placeholder(placeholder, fmap, map_height_px)


# ------------------------------------------------------------------ #
# Private helpers                                                      #
# ------------------------------------------------------------------ #

def _render_map_in_placeholder(
    placeholder: "st.delta_generator.DeltaGenerator",
    fmap,
    height_px: int,
) -> None:
    """Render a Folium map into a Streamlit placeholder."""
    html = fmap._repr_html_()
    with placeholder:
        components.html(html, height=height_px, scrolling=False)