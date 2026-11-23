from itertools import combinations

import networkx as nx

from ttro.graph import Board
from ttro.solver.pathchoice import best_simple_paths

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

    ``pre_claimed`` edges (yours, already on the board) are pre-loaded into
    ``claimed`` and pre-counted toward ``trains_used``. ``blocked`` edges
    (opponent's) are removed from the working graph entirely, so pathfinding
    can never traverse them.

    ``rank="points"`` picks the simple path with the most new route points,
    then the fewest new trains, that still fits in the remaining train budget.
    ``rank="edges"`` is the previous rule: fewest new edges, then fewest new
    trains, then most route points. ``ties`` records points-rank cases where
    another path matched the winning points and train cost; the first path
    is the one that was kept.
    """

    def __init__(
        self,
        graph: nx.Graph,
        *,
        blocked: set[frozenset] | None = None,
        pre_claimed: set[frozenset] | None = None,
        rank: str = "points",
        cache: dict | None = None,
    ):
        self.blocked = blocked or set()
        if self.blocked:
            G = graph.copy()
            G.remove_edges_from(
                (u, v) for u, v in graph.edges() if _edge_key(u, v) in self.blocked
            )
            self.G = G
        else:
            self.G = graph

        self.claimed: set[frozenset] = set(pre_claimed or set())
        self.mandatory: set[frozenset] = set(self.claimed)
        self.used_edges: set[frozenset] = set()

        if rank not in ("points", "edges"):
            raise ValueError(f"unknown rank: {rank}")
        self.rank = rank
        self._cache = cache
        self.ties: list[dict] = []

        self.trains_used = 0
        for edge in self.claimed:
            u, v = tuple(edge)
            if self.G.has_edge(u, v):
                self.trains_used += self.G[u][v]["trains"]

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

        None means no simple path connects the ticket within the trains still
        left (45 minus trains already placed). ``rank="points"`` maximizes new
        route points, then minimizes new trains. An equal key keeps the first
        path and is appended to ``ties``. ``rank="edges"`` keeps the old
        fewest-new-edges order and does not apply the budget filter.
        """
        start, end = trip[0], trip[1]
        if start == end or not nx.has_path(self.G, start, end):
            return None

        if self.rank == "edges":
            best_path = self._fewest_new_edges(start, end)
        else:
            budget = TOTAL_TRAINS - self.trains_used
            if budget < 0:
                budget = 0
            prior_claims = len(self.claimed)
            chosen, tied = best_simple_paths(
                self.G, start, end, budget, claimed=self.claimed, cache=self._cache
            )
            if chosen is None:
                return None
            best_path = chosen
            if len(tied) > 1:
                trains, points = self._new_track(best_path)
                self.ties.append(
                    {
                        "start": start,
                        "end": end,
                        "points": points,
                        "trains": trains,
                        "prior_claims": prior_claims,
                        "paths": [list(path) for path in tied],
                    }
                )

        new_trains = 0
        new_points = 0
        for u, v in zip(best_path, best_path[1:]):
            key = _edge_key(u, v)
            self.used_edges.add(key)
            if key not in self.claimed:
                new_trains += self.G[u][v]["trains"]
                new_points += self.G[u][v]["weight"]
                self.claimed.add(key)
        self.trains_used += new_trains
        return new_points, best_path

    def _fewest_new_edges(self, start: str, end: str) -> list[str]:
        """Old within-ticket rule: fewest new edges, then trains, then points."""
        key = None
        if self._cache is not None:
            key = ("edges", id(self.G), start, end, frozenset(self.claimed))
            hit = self._cache.get(key)
            if hit is not None:
                return hit

        best_path: list[str] = []
        best_key = None
        for path in nx.all_shortest_paths(self.G, start, end, weight=self._distance):
            trains, points = self._new_track(path)
            rank_key = (trains, -points)
            if best_key is None or rank_key < best_key:
                best_key = rank_key
                best_path = path
        if key is not None:
            self._cache[key] = best_path
        return best_path


class Optimizer:
    """Combinatorial search for the highest-scoring set of destination tickets."""

    def __init__(self):
        self.graph = Board.build_graph()

    def evaluate_set(
        self, trip_list, *, rank: str = "points", cache: dict | None = None
    ) -> tuple[int, list[list[str]]]:
        """Route a fixed set of trips, sharing claimed track between them.

        Returns the total score (ticket points + placed-train points) and one real
        city-chain path per trip. Returns ``(0, [])`` if the set exceeds 45 trains.
        ``cache`` reuses path searches across sets; it does not change which path
        is chosen.
        """
        routes = RouteSet(self.graph, rank=rank, cache=cache)
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

    def evaluate_hand(
        self,
        trip_list: list,
        *,
        blocked: set[frozenset] | None = None,
        pre_claimed: set[frozenset] | None = None,
    ) -> dict:
        """Route a trip hand, highest points first, around edge claims.

        Trips route in points-descending order so high-value tickets claim
        contested track before low-value ones. Returned ``order`` gives the
        original ``trip_list`` index for each entry in ``paths``, so callers
        can re-derive routing order for ids/labels kept alongside the input.
        Unlike ``evaluate_set``, going over the 45-train cap is reported via
        ``trains_used`` rather than a hard fail.
        """
        order = sorted(range(len(trip_list)), key=lambda i: trip_list[i][2], reverse=True)
        routes = RouteSet(self.graph, blocked=blocked, pre_claimed=pre_claimed)

        total = 0
        paths: list[list[str]] = []
        unreachable: list[int] = []

        for i in order:
            result = routes.add_trip(trip_list[i])
            if result is None:
                unreachable.append(i)
                paths.append([])
                continue
            new_points, path = result
            total += new_points + trip_list[i][2]
            paths.append(path)

        return {
            "order": order,
            "points": total,
            "paths": paths,
            "trains_used": routes.trains_used,
            "unreachable": unreachable,
            "unused_mandatory": [tuple(edge) for edge in routes.mandatory - routes.used_edges],
        }

    def max_set_trips(
        self, set_size: int = DEFAULT_SET_SIZE
    ) -> tuple[int, list[list[str]], list]:
        """Search every ticket combination of ``set_size`` for the maximum score."""
        trips = Board.get_trips()
        best_score = 0
        best_paths: list[list[str]] = []
        best_trips: list = []
        cache: dict = {}

        for combo in combinations(trips, set_size):
            if sum(t[2] for t in combo) < POINT_PRUNE_THRESHOLD:
                continue
            score, paths = self.evaluate_set(combo, cache=cache)
            if score > best_score:
                best_score = score
                best_paths = paths
                best_trips = list(combo)

        return best_score, best_paths, best_trips
