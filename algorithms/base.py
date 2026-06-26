"""
Abstract base class for all pathfinding algorithms.

To add a new algorithm (Dijkstra, BFS, JPS, etc.):
  1. Subclass PathfindingAlgorithm
  2. Implement find_path()
  3. Set the `name` class attribute
The UI and visualization layer picks it up automatically.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """Everything a pathfinding run produces."""
    path: list[int]            # node IDs from origin to destination
    explored: list[int]        # nodes popped from open set, in order (for animation)
    path_length_m: float       # sum of edge lengths in metres
    nodes_explored: int        # len(explored), kept separate for clarity
    runtime_ms: float          # wall-clock time of find_path()


class PathfindingAlgorithm(ABC):
    """
    All algorithms receive a graph.builder.RoadGraph and return a SearchResult.

    The interface is intentionally narrow — algorithms must not call OSMnx,
    touch Streamlit, or write to disk.
    """

    name: str = ""  # subclasses set this as a class attribute

    def __init__(self, graph):
        # Accepts graph.builder.RoadGraph — typed loosely to avoid
        # circular imports; both layers stay decoupled.
        self.graph = graph

    @abstractmethod
    def find_path(
        self,
        origin_node: int,
        destination_node: int,
    ) -> SearchResult | None:
        """
        Find the shortest path between two node IDs.

        Returns SearchResult on success, None if no path exists.
        """
        ...

    # ------------------------------------------------------------------ #
    # Shared helpers — subclasses may use these                           #
    # ------------------------------------------------------------------ #

    def _reconstruct_path(
        self, came_from: dict[int, int], current: int
    ) -> list[int]:
        """Walk came_from pointers back to origin."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return list(reversed(path))

    def _path_length_m(self, path: list[int]) -> float:
        """Sum edge lengths along a node-ID path."""
        total = 0.0
        for u, v in zip(path, path[1:]):
            neighbors = dict(self.graph.get_neighbors(u))
            total += neighbors.get(v, 0.0)
        return total