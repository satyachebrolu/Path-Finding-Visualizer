"""
Tests for the haversine heuristic in isolation.

Imports _haversine_m directly — this is the one internal function
we test directly because admissibility is a correctness guarantee,
not just a behaviour check.
"""

import math
import pytest


# We import from the agreed module path. This will fail until P1
# merges — that's fine, run these after the merge.
from algorithms.astar import _haversine_m


class _N:
    """Minimal node-like object with lat/lng."""
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng


class TestHaversine:

    def test_same_point_is_zero(self):
        n = _N(51.5, -0.1)
        assert _haversine_m(n, n) == pytest.approx(0.0)

    def test_known_distance_london_paris(self):
        # London → Paris is approximately 340 km
        london = _N(51.5074, -0.1278)
        paris  = _N(48.8566,  2.3522)
        dist = _haversine_m(london, paris)
        assert 330_000 < dist < 350_000, f"Expected ~340km, got {dist/1000:.1f}km"

    def test_symmetry(self):
        a = _N(51.50, -0.10)
        b = _N(51.51, -0.09)
        assert _haversine_m(a, b) == pytest.approx(_haversine_m(b, a))

    def test_admissibility_on_grid(self, grid_graph):
        """
        Heuristic must never exceed true road distance.

        On the 3x3 grid, every edge is 100m. For all node pairs,
        check h(n, goal) ≤ actual shortest path length.
        """
        import networkx as nx
        # Reconstruct raw graph to run nx.shortest_path_length
        # (safe to do in tests; not used in production code)
        raw_g = nx.DiGraph()
        for node_id in range(9):
            node = grid_graph.get_node(node_id)
            raw_g.add_node(node_id, lat=node.lat, lng=node.lng)
        for node_id in range(9):
            for neighbor_id, length in grid_graph.get_neighbors(node_id):
                raw_g.add_edge(node_id, neighbor_id, weight=length)

        goal = grid_graph.get_node(8)
        for node_id in range(9):
            node = grid_graph.get_node(node_id)
            h = _haversine_m(node, goal)
            try:
                true_dist = nx.shortest_path_length(
                    raw_g, node_id, 8, weight='weight'
                )
            except nx.NetworkXNoPath:
                continue
            assert h <= true_dist + 1.0, (
                f"Heuristic {h:.1f}m > true distance {true_dist:.1f}m "
                f"from node {node_id} to 8 — not admissible"
            )