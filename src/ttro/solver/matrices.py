import numpy as np

from ttro.db import BoardRepository


class BoardMatrices:
    """Vectorized all-pairs view of the board for fast, static routing.

    Builds numpy adjacency matrices for train cost and route points, then runs a
    vectorized Floyd-Warshall that minimizes hop count and, among equal-length
    paths, maximizes route points. Used for instant single-trip routing (API and
    pruning); the collapse-based combinatorial search lives in ``Optimizer``.
    """

    def __init__(self, cities: list[str], edges: list, trips: list):
        self.names = list(cities)
        self.index = {name: i for i, name in enumerate(self.names)}
        n = len(self.names)

        self.train_cost = np.full((n, n), np.inf)
        self.route_points = np.zeros((n, n), dtype=np.int64)
        np.fill_diagonal(self.train_cost, 0.0)

        for u, v, (w, t) in edges:
            i, j = self.index[u], self.index[v]
            self.train_cost[i, j] = self.train_cost[j, i] = t
            self.route_points[i, j] = self.route_points[j, i] = w

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
        INF = np.inf
        hops = np.where(self.train_cost == INF, INF, 1.0)
        np.fill_diagonal(hops, 0.0)
        points = self.route_points.astype(np.int64).copy()

        nxt = np.full((n, n), -1, dtype=np.int64)
        edge = (hops == 1.0)
        cols = np.broadcast_to(np.arange(n), (n, n))
        nxt = np.where(edge, cols, nxt)

        for k in range(n):
            cand_hops = hops[:, k][:, None] + hops[None, k, :]
            cand_points = points[:, k][:, None] + points[None, k, :]
            improve = (cand_hops < hops) | ((cand_hops == hops) & (cand_points > points))
            hops = np.where(improve, cand_hops, hops)
            points = np.where(improve, cand_points, points)
            nxt = np.where(improve, nxt[:, k][:, None], nxt)

        self.hops = hops
        self.best_points = points
        self._next = nxt

    def shortest_path(self, start: str, end: str) -> list[str] | None:
        """Max-route-point path among the fewest-hop paths, or None if unreachable."""
        if start not in self.index or end not in self.index:
            return None
        i, j = self.index[start], self.index[end]
        if not np.isfinite(self.hops[i, j]):
            return None
        path = [i]
        while i != j:
            i = int(self._next[i, j])
            if i == -1:
                return None
            path.append(i)
        return [self.names[p] for p in path]

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
