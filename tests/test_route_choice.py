"""Within-ticket ranking: most route points, then fewest trains, within 45."""

import random
import unittest
from itertools import pairwise

import networkx as nx

from ttro.solver.matrices import BoardMatrices
from ttro.solver.optimizer import TOTAL_TRAINS, RouteSet


def _graph(edges):
    graph = nx.Graph()
    for u, v, points, trains in edges:
        graph.add_edge(u, v, weight=points, trains=trains, ratio=points / trains)
    return graph


def _matrices(edges, trips=None):
    cities = sorted({city for u, v, _p, _t in edges for city in (u, v)})
    return BoardMatrices(
        cities,
        [(u, v, (points, trains)) for u, v, points, trains in edges],
        trips or [],
    )


def _brute(graph, start, end, budget):
    best_key = None
    paths = []
    for path in nx.all_simple_paths(graph, start, end):
        trains = points = 0
        for u, v in pairwise(path):
            trains += graph[u][v]["trains"]
            points += graph[u][v]["weight"]
        if trains > budget:
            continue
        key = (-points, trains)
        if best_key is None or key < best_key:
            best_key = key
            paths = [path]
        elif key == best_key:
            paths.append(path)
    return paths


class RouteChoiceTests(unittest.TestCase):
    def test_equal_points_fewer_trains_wins(self):
        graph = _graph(
            [
                ("A", "B", 2, 2),
                ("B", "C", 2, 2),
                ("A", "D", 2, 1),
                ("D", "C", 2, 1),
            ]
        )
        routes = RouteSet(graph)
        new_points, path = routes.add_trip(("A", "C", 5))
        self.assertEqual(path, ["A", "D", "C"])
        self.assertEqual(new_points, 4)
        self.assertEqual(routes.trains_used, 2)
        self.assertEqual(routes.ties, [])

        edges = [
            ("A", "B", 2, 2),
            ("B", "C", 2, 2),
            ("A", "D", 2, 1),
            ("D", "C", 2, 1),
        ]
        matrices = _matrices(edges)
        chosen = matrices.shortest_path("A", "C")
        self.assertEqual(chosen, ["A", "D", "C"])
        self.assertEqual(matrices.path_train_cost(chosen), 2)
        self.assertEqual(matrices.path_route_points(chosen), 4)

    def test_longer_path_with_more_points_wins(self):
        edges = [
            ("A", "C", 1, 1),
            ("A", "B", 4, 2),
            ("B", "C", 4, 2),
        ]
        graph = _graph(edges)
        routes = RouteSet(graph)
        new_points, path = routes.add_trip(("A", "C", 3))
        self.assertEqual(path, ["A", "B", "C"])
        self.assertEqual(new_points, 8)
        self.assertEqual(routes.trains_used, 4)

        old = RouteSet(graph, rank="edges")
        _points, old_path = old.add_trip(("A", "C", 3))
        self.assertEqual(old_path, ["A", "C"])

        matrices = _matrices(edges)
        self.assertEqual(matrices.shortest_path("A", "C"), ["A", "B", "C"])
        self.assertGreater(
            matrices.path_route_points(matrices.shortest_path("A", "C")),
            matrices.path_route_points(["A", "C"]),
        )

    def test_path_over_45_trains_is_not_chosen(self):
        edges = [
            ("A", "B", 10, 45),
            ("A", "C", 30, 23),
            ("C", "B", 30, 23),
        ]
        graph = _graph(edges)
        routes = RouteSet(graph)
        new_points, path = routes.add_trip(("A", "B", 1))
        self.assertEqual(path, ["A", "B"])
        self.assertEqual(new_points, 10)
        self.assertEqual(routes.trains_used, TOTAL_TRAINS)
        self.assertLessEqual(routes.trains_used, TOTAL_TRAINS)

        only_long = _graph([("A", "C", 30, 23), ("C", "B", 30, 23)])
        self.assertIsNone(RouteSet(only_long).add_trip(("A", "B", 1)))

        matrices = _matrices(edges)
        self.assertEqual(matrices.shortest_path("A", "B"), ["A", "B"])
        self.assertLessEqual(matrices.path_train_cost(matrices.shortest_path("A", "B")), 45)
        blocked = _matrices([("A", "C", 30, 23), ("C", "B", 30, 23)])
        self.assertIsNone(blocked.shortest_path("A", "B"))

    def test_equal_key_keeps_first_path_and_records_tie(self):
        graph = _graph(
            [
                ("A", "B", 2, 2),
                ("B", "C", 2, 2),
                ("A", "D", 2, 2),
                ("D", "C", 2, 2),
            ]
        )
        routes = RouteSet(graph)
        _points, path = routes.add_trip(("A", "C", 1))
        self.assertEqual(path, ["A", "B", "C"])
        self.assertEqual(len(routes.ties), 1)
        tie = routes.ties[0]
        self.assertEqual(tie["points"], 4)
        self.assertEqual(tie["trains"], 4)
        self.assertEqual(tie["paths"][0], path)
        self.assertEqual(
            sorted(tuple(p) for p in tie["paths"]),
            [("A", "B", "C"), ("A", "D", "C")],
        )
        self.assertEqual(
            _matrices(
                [
                    ("A", "B", 2, 2),
                    ("B", "C", 2, 2),
                    ("A", "D", 2, 2),
                    ("D", "C", 2, 2),
                ]
            ).shortest_path("A", "C"),
            ["A", "B", "C"],
        )

    def test_search_matches_brute_force(self):
        rng = random.Random(0)
        cities = [f"C{i}" for i in range(6)]
        edges = []
        for i, u in enumerate(cities):
            for v in cities[i + 1 :]:
                if rng.random() < 0.55:
                    trains = rng.randint(1, 4)
                    edges.append((u, v, trains + rng.randint(0, 3), trains))
        graph = _graph(edges)
        budget = 10
        for start, end in (("C0", "C5"), ("C1", "C4"), ("C2", "C3")):
            if not nx.has_path(graph, start, end):
                continue
            expected = _brute(graph, start, end, budget)
            # Spend the rack down so this ticket's budget matches the brute force cap.
            routes = RouteSet(graph)
            routes.trains_used = TOTAL_TRAINS - budget
            result = routes.add_trip((start, end, 1))
            if not expected:
                self.assertIsNone(result)
                continue
            _points, path = result
            found = routes.ties[0]["paths"] if routes.ties else [path]
            self.assertEqual(
                sorted(tuple(p) for p in found),
                sorted(tuple(p) for p in expected),
            )


if __name__ == "__main__":
    unittest.main()
