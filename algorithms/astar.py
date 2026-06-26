"""
A* pathfinding on an OSM road network.

Data structures
---------------
open_set   : min-heap of (f_score, node_id) tuples
             heapq gives O(log n) insert and pop-min
closed_set : set of node IDs already finalised
             O(1) membership test
g_score    : dict mapping node_id → best known cost from origin
came_from  : dict mapping node_id → predecessor for path reconstruction

Time complexity  : O((V + E) log V)
Space complexity : O(V)

The heuristic is haversine distance — straight-line distance between
two lat/lng points on a sphere. It is admissible (never overestimates)
because road distance ≥ straight-line distance, so A* is guaranteed
to find the optimal path.
"""

import heapq
import math
import time

from .base import PathfindingAlgorithm, SearchResult


class AStarPathfinder(PathfindingAlgorithm):

    name = "A*"

    def find_path(
        self,
        origin_node: int,
        destination_node: int,
    ) -> SearchResult | None:

        start_time = time.perf_counter()

        if not self.graph.has_node(origin_node):
            raise ValueError(f"Origin node {origin_node} not in graph")
        if not self.graph.has_node(destination_node):
            raise ValueError(f"Destination node {destination_node} not in graph")

        if origin_node == destination_node:
            return SearchResult(
                path=[origin_node],
                explored=[origin_node],
                path_length_m=0.0,
                nodes_explored=1,
                runtime_ms=0.0,
            )

        dest_node_data = self.graph.get_node(destination_node)

        # g_score[n] = cheapest known path cost from origin to n
        g_score: dict[int, float] = {origin_node: 0.0}

        # f_score[n] = g_score[n] + h(n)
        h_origin = _haversine_m(
            self.graph.get_node(origin_node), dest_node_data
        )

        # open_set entries: (f_score, node_id)
        # Duplicates are allowed — stale entries are skipped via closed_set check
        open_set: list[tuple[float, int]] = [(h_origin, origin_node)]

        closed_set: set[int] = set()
        came_from: dict[int, int] = {}
        explored: list[int] = []

        while open_set:
            _, current = heapq.heappop(open_set)

            # Skip stale heap entries
            if current in closed_set:
                continue

            closed_set.add(current)
            explored.append(current)

            if current == destination_node:
                path = self._reconstruct_path(came_from, current)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                return SearchResult(
                    path=path,
                    explored=explored,
                    path_length_m=self._path_length_m(path),
                    nodes_explored=len(explored),
                    runtime_ms=elapsed_ms,
                )

            for neighbor, edge_length in self.graph.get_neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g = g_score[current] + edge_length

                if tentative_g < g_score.get(neighbor, math.inf):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h = _haversine_m(
                        self.graph.get_node(neighbor), dest_node_data
                    )
                    f = tentative_g + h
                    heapq.heappush(open_set, (f, neighbor))

        # Open set exhausted — no path exists
        return None


def _haversine_m(node_a, node_b) -> float:
    """
    Straight-line distance in metres between two graph nodes.

    Uses the haversine formula for accuracy on geographic coordinates.
    This is the A* heuristic h(n) — admissible because road distance
    is always ≥ straight-line distance.

    Args:
        node_a, node_b: NodeData objects with .lat and .lng attributes

    Returns:
        Distance in metres (float)
    """
    R = 6_371_000  # Earth radius in metres

    lat1, lon1 = math.radians(node_a.lat), math.radians(node_a.lng)
    lat2, lon2 = math.radians(node_b.lat), math.radians(node_b.lng)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c