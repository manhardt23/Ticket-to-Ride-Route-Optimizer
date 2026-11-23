import numpy as np

from ttro.db import BoardRepository
from ttro.graph.board import TOTAL_TRAINS
from ttro.solver.pathchoice import all_pairs_best


class BoardMatrices:
    """All-pairs view of the board for fast, static routing.

    Builds numpy adjacency matrices for train cost and route points, then picks,
    for every city pair, the simple path with the most route points that still
    fits in ``TOTAL_TRAINS``. Equal points keep the path with fewer trains; a
    further tie keeps the first path. Used for instant single-trip routing (API
    and pruning); the combinatorial search lives in ``Optimizer``.
    """

    def __init__(self, cities: list[str], edges: list, trips: list):
        self.names = list(cities)
        self.index = {name: i for i, name in enumerate(self.names)}
        n = len(self.names)

        self.train_cost = np.full((n, n), np.inf)
        self.route_points = np.zeros((n, n), dtype=np.int64)
        np.fill_diagonal(self.train_cost, 0.0)
        # Keep insertion order so a points/trains tie picks the same first path
        # the NetworkX board graph would.
        self._edge_list: list[tuple[str, str, int, int]] = []

        for u, v, (w, t) in edges:
            i, j = self.index[u], self.index[v]
            self.train_cost[i, j] = self.train_cost[j, i] = t
            self.route_points[i, j] = self.route_points[j, i] = w
            self._edge_list.append((u, v, int(w), int(t)))

        self.trip_points = np.array([p for (_, _, p) in trips], dtype=np.int64)

        self._floyd_warshall(n)

    @classmethod
    def from_repository(cls, repo: BoardRepository | None = None) -> "BoardMatrices":
        owned = repo is None
        repo = repo or BoardRepository()
        try:
            return cls(repo.get_cities(), repo.get_edges(), repo.get_trips())
        finally:
            if owned:
                repo.close()

    def _floyd_warshall(self, n: int) -> None:
        """Fill best paths: higher route points, then lower train cost.

        A candidate replaces the stored path when its points are higher, or the
        points match and its train cost is lower. Equal points and trains keep
        the earlier path. Candidates are simple paths of at most ``TOTAL_TRAINS``
        trains, so a longer route can win and a path past the rack cannot.
        """
        paths = all_pairs_best(self.names, self._edge_list, TOTAL_TRAINS)

        self.best_points = np.zeros((n, n), dtype=np.int64)
        self.best_trains = np.full((n, n), np.inf)
        self.hops = np.full((n, n), np.inf)
        self._next = np.full((n, n), -1, dtype=np.int64)
        # Full paths, not next-hop suffixes: a higher-point route need not
        # contain the higher-point route between its intermediate cities.
        self._paths: list[list[list[str] | None]] = [
            [None] * n for _ in range(n)
        ]
        np.fill_diagonal(self.best_trains, 0.0)
        np.fill_diagonal(self.hops, 0.0)

        for i, start in enumerate(self.names):
            for j, end in enumerate(self.names):
                path = paths.get((start, end))
                if path is None:
                    continue
                self._paths[i][j] = path
                if len(path) >= 2:
                    self._next[i, j] = self.index[path[1]]
                self.hops[i, j] = len(path) - 1
                self.best_points[i, j] = self.path_route_points(path)
                self.best_trains[i, j] = self.path_train_cost(path)

    def shortest_path(self, start: str, end: str) -> list[str] | None:
        """Highest-point path within 45 trains, then fewest trains, or None."""
        if start not in self.index or end not in self.index:
            return None
        path = self._paths[self.index[start]][self.index[end]]
        if path is None:
            return None
        return list(path)

    def path_route_points(self, path: list[str]) -> int:
        total = 0
        for a, b in zip(path, path[1:]):
            total += int(self.route_points[self.index[a], self.index[b]])
        return total

    def path_train_cost(self, path: list[str]) -> int:
        total = 0
        for a, b in zip(path, path[1:]):
            total += int(self.train_cost[self.index[a], self.index[b]])
        return total
