from itertools import combinations

import networkx as nx

from ttro.graph import Board

DEFAULT_SET_SIZE = 10
POINT_PRUNE_THRESHOLD = 150
TOTAL_TRAINS = 45


def _edge_key(u: str, v: str) -> frozenset:
    return frozenset((u, v))


class RouteSet:
    """Routes a set of trips while sharing already-claimed track.

    Track that has already been claimed costs no extra trains or distance, so a
    later trip reuses it for free. Every route is computed on the original board,
    so paths are always real city chains (no collapsed representative nodes).
    """

    def __init__(self, graph: nx.Graph):
        self.G = graph
        self.claimed: set[frozenset] = set()
        self.trains_used = 0

    def _distance(self, u: str, v: str, data: dict) -> int:
        return 0 if _edge_key(u, v) in self.claimed else 1

    def _new_track(self, path: list[str]) -> tuple[int, int]:
        """Newly placed (trains, route_points) for a candidate path."""
        trains = points = 0
        for u, v in zip(path, path[1:]):
            if _edge_key(u, v) not in self.claimed:
                trains += self.G[u][v]["trains"]
                points += self.G[u][v]["weight"]
        return trains, points

    def add_trip(self, trip) -> tuple[int, list[str]] | None:
        """Claim the best route for a trip. Returns (new_points, path) or None.

        None means the trip is unreachable. The route minimizes newly placed track;
        among ties it spends the fewest new trains, then scores the most points.
        """
        start, end = trip[0], trip[1]
        if start == end or not nx.has_path(self.G, start, end):
            return None

        best_path: list[str] = []
        best_key = None
        for path in nx.all_shortest_paths(self.G, start, end, weight=self._distance):
            trains, points = self._new_track(path)
            key = (trains, -points)
            if best_key is None or key < best_key:
                best_key = key
                best_path = path

        new_trains = 0
        new_points = 0
        for u, v in zip(best_path, best_path[1:]):
            if _edge_key(u, v) not in self.claimed:
                new_trains += self.G[u][v]["trains"]
                new_points += self.G[u][v]["weight"]
                self.claimed.add(_edge_key(u, v))
        self.trains_used += new_trains
        return new_points, best_path


class Optimizer:
    """Combinatorial search for the highest-scoring set of destination tickets."""

    def __init__(self):
        self.graph = Board.build_graph()

    def evaluate_set(self, trip_list) -> tuple[int, list[list[str]]]:
        """Route a fixed set of trips, sharing claimed track between them.

        Returns the total score (ticket points + placed-train points) and one real
        city-chain path per trip. Returns ``(0, [])`` if the set exceeds 45 trains.
        """
        routes = RouteSet(self.graph)
        total = 0
        paths: list[list[str]] = []

        for trip in trip_list:
            result = routes.add_trip(trip)
            if result is None:
                paths.append([])
                continue
            new_points, path = result
            if routes.trains_used > TOTAL_TRAINS:
                return 0, []
            total += new_points + trip[2]
            paths.append(path)

        return total, paths

    def max_set_trips(
        self, set_size: int = DEFAULT_SET_SIZE
    ) -> tuple[int, list[list[str]], list]:
        """Search every ticket combination of ``set_size`` for the maximum score."""
        trips = Board.get_trips()
        best_score = 0
        best_paths: list[list[str]] = []
        best_trips: list = []

        for combo in combinations(trips, set_size):
            if sum(t[2] for t in combo) < POINT_PRUNE_THRESHOLD:
                continue
            score, paths = self.evaluate_set(combo)
            if score > best_score:
                best_score = score
                best_paths = paths
                best_trips = list(combo)

        return best_score, best_paths, best_trips
