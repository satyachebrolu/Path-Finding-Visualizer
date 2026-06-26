"""
Behavioural tests for AStarPathfinder.

These test what the algorithm does, not how it does it.
All use synthetic graphs from conftest.py — no OSM, no network.
"""

import pytest
from algorithms.astar import AStarPathfinder
from algorithms.base import SearchResult


class TestAStarCorrectness:

    def test_direct_path_found(self, direct_graph):
        result = AStarPathfinder(direct_graph).find_path(0, 1)
        assert result is not None
        assert result.path == [0, 1]

    def test_same_origin_and_destination(self, direct_graph):
        result = AStarPathfinder(direct_graph).find_path(0, 0)
        assert result is not None
        assert result.path == [0]
        assert result.path_length_m == pytest.approx(0.0)

    def test_no_path_returns_none(self, disconnected_graph):
        result = AStarPathfinder(disconnected_graph).find_path(0, 3)
        assert result is None

    def test_one_way_forward_path_exists(self, one_way_graph):
        result = AStarPathfinder(one_way_graph).find_path(0, 2)
        assert result is not None
        assert result.path == [0, 1, 2]

    def test_one_way_reverse_returns_none(self, one_way_graph):
        result = AStarPathfinder(one_way_graph).find_path(2, 0)
        assert result is None

    def test_grid_optimal_path_length(self, grid_graph):
        """Shortest path 0→8 on the 3x3 grid must be exactly 400m."""
        result = AStarPathfinder(grid_graph).find_path(0, 8)
        assert result is not None
        assert result.path_length_m == pytest.approx(400.0, abs=0.01)

    def test_grid_path_is_valid_sequence(self, grid_graph):
        """Every consecutive pair in the path must be a real edge."""
        result = AStarPathfinder(grid_graph).find_path(0, 8)
        assert result is not None
        neighbor_map = {
            node: {n for n, _ in grid_graph.get_neighbors(node)}
            for node in range(9)
        }
        for u, v in zip(result.path, result.path[1:]):
            assert v in neighbor_map[u], f"Edge {u}→{v} does not exist"

    def test_grid_path_starts_and_ends_correctly(self, grid_graph):
        result = AStarPathfinder(grid_graph).find_path(0, 8)
        assert result is not None
        assert result.path[0] == 0
        assert result.path[-1] == 8


class TestAStarSearchResult:

    def test_returns_search_result_type(self, direct_graph):
        result = AStarPathfinder(direct_graph).find_path(0, 1)
        assert isinstance(result, SearchResult)

    def test_explored_nodes_non_empty(self, grid_graph):
        result = AStarPathfinder(grid_graph).find_path(0, 8)
        assert result is not None
        assert len(result.explored) > 0

    def test_destination_in_explored(self, grid_graph):
        """Destination must be the last node explored (popped from heap)."""
        result = AStarPathfinder(grid_graph).find_path(0, 8)
        assert result is not None
        assert result.explored[-1] == 8

    def test_nodes_explored_count_matches_list(self, grid_graph):
        result = AStarPathfinder(grid_graph).find_path(0, 8)
        assert result is not None
        assert result.nodes_explored == len(result.explored)

    def test_runtime_ms_is_positive(self, direct_graph):
        result = AStarPathfinder(direct_graph).find_path(0, 1)
        assert result is not None
        assert result.runtime_ms >= 0.0

    def test_path_length_matches_edges(self, direct_graph):
        """On the direct graph, path length must equal the single edge (100m)."""
        result = AStarPathfinder(direct_graph).find_path(0, 1)
        assert result is not None
        assert result.path_length_m == pytest.approx(100.0)

    def test_astar_explores_fewer_nodes_than_grid_total(self, grid_graph):
        """
        A* with an admissible heuristic should not need to explore all 9 nodes
        to find 0→8. This is a sanity check on heuristic effectiveness.
        """
        result = AStarPathfinder(grid_graph).find_path(0, 8)
        assert result is not None
        assert result.nodes_explored < 9, (
            f"A* explored all {result.nodes_explored} nodes — heuristic may not be working"
        )


class TestAStarEdgeCases:

    def test_invalid_origin_raises(self, direct_graph):
        with pytest.raises(ValueError, match="Origin node"):
            AStarPathfinder(direct_graph).find_path(999, 1)

    def test_invalid_destination_raises(self, direct_graph):
        with pytest.raises(ValueError, match="Destination node"):
            AStarPathfinder(direct_graph).find_path(0, 999)