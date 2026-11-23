"""Budgeted simple paths ranked by route points, then train cost.

Hop count is not a filter: a longer path wins when it scores more points and
still fits in the train budget. Equal points and trains keep the first path
in adjacency order.
"""

import heapq

import networkx as nx

# Unreachable sentinel for the train-distance bound. Larger than any budget.
_INF = 10**9


def best_simple_paths(
    graph: nx.Graph,
    start,
    end,
    budget: int,
    *,
    claimed: set[frozenset] | None = None,
    cache: dict | None = None,
    point_attr: str = "weight",
    train_attr: str = "trains",
) -> tuple[list | None, list[list]]:
    """Return ``(chosen, tied)`` among simple paths with trains <= ``budget``.

    ``chosen`` is None when no path fits. ``tied`` lists every path that
    matches the winning points and train cost, with ``chosen`` first.
    Claimed edges add neither points nor trains.
    """
    if budget < 0 or start not in graph or end not in graph:
        return None, []

    key = None
    if cache is not None:
        key = (id(graph), start, end, budget, frozenset(claimed or ()), True)
        hit = cache.get(key)
        if hit is not None:
            return hit

    nodes, index, adj, bound, free_bonus = _prepare(
        graph, claimed, point_attr, train_attr, budget
    )
    dist = _distances_to(adj, index[end])
    chosen_ids, tie_ids = _search(
        adj, index[start], index[end], budget, bound, free_bonus, dist, True
    )
    if chosen_ids is None:
        result = (None, [])
    else:
        result = (
            [nodes[i] for i in chosen_ids],
            [[nodes[i] for i in path] for path in tie_ids],
        )
    if key is not None:
        cache[key] = result
    return result


def all_pairs_best(
    names: list[str],
    edges: list[tuple[str, str, int, int]],
    budget: int,
) -> dict[tuple[str, str], list[str]]:
    """Best path for every ordered pair, keyed by ``(start, end)``.

    ``edges`` is ``(city_a, city_b, route_points, trains)``. Missing keys are
    unreachable within ``budget``. Diagonal pairs are the single-city path.
    """
    graph = nx.Graph()
    graph.add_nodes_from(names)
    for u, v, points, trains in edges:
        graph.add_edge(u, v, weight=points, trains=trains)

    nodes, index, adj, bound, free_bonus = _prepare(
        graph, None, "weight", "trains", budget
    )
    dist = _all_pairs_trains(adj)
    out: dict[tuple[str, str], list[str]] = {}
    for i, name in enumerate(nodes):
        out[(name, name)] = [name]
    n = len(nodes)
    for i in range(n):
        for j in range(n):
            if i == j or dist[i][j] > budget:
                continue
            to_end = [dist[u][j] for u in range(n)]
            chosen, _tied = _search(
                adj, i, j, budget, bound, free_bonus, to_end, False
            )
            if chosen is not None:
                out[(nodes[i], nodes[j])] = [nodes[k] for k in chosen]
    return out


def _prepare(graph, claimed, point_attr, train_attr, budget):
    claimed = claimed or set()
    nodes = list(graph.nodes)
    index = {node: i for i, node in enumerate(nodes)}
    adj: list[list[tuple[int, int, int]]] = [[] for _ in nodes]
    for u in nodes:
        ui = index[u]
        for v in graph.neighbors(u):
            data = graph[u][v]
            edge = frozenset((u, v))
            if edge in claimed:
                trains, points = 0, 0
            else:
                trains = int(data[train_attr])
                points = int(data[point_attr])
            adj[ui].append((index[v], trains, points))

    items: list[tuple[int, int]] = []
    free_bonus = 0
    seen: set[frozenset] = set()
    for u, v, data in graph.edges(data=True):
        edge = frozenset((u, v))
        if edge in seen or edge in claimed:
            continue
        seen.add(edge)
        trains = int(data[train_attr])
        points = int(data[point_attr])
        if trains <= 0:
            if points > 0:
                free_bonus += points
        elif points > 0:
            items.append((trains, points))

    limit = budget if budget > 0 else 0
    bound = [0] * (limit + 1)
    for trains, points in items:
        if trains > limit:
            continue
        for left in range(limit, trains - 1, -1):
            cand = bound[left - trains] + points
            if cand > bound[left]:
                bound[left] = cand
    return nodes, index, adj, bound, free_bonus


def _distances_to(adj, end: int) -> list[int]:
    dist = [_INF] * len(adj)
    dist[end] = 0
    heap: list[tuple[int, int]] = [(0, end)]
    while heap:
        trains, node = heapq.heappop(heap)
        if trains != dist[node]:
            continue
        for nxt, cost, _points in adj[node]:
            cand = trains + cost
            if cand < dist[nxt]:
                dist[nxt] = cand
                heapq.heappush(heap, (cand, nxt))
    return dist


def _all_pairs_trains(adj) -> list[list[int]]:
    n = len(adj)
    dist = [[_INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
        for nxt, cost, _points in adj[i]:
            if cost < dist[i][nxt]:
                dist[i][nxt] = cost
    for mid in range(n):
        via = dist[mid]
        for i in range(n):
            start = dist[i][mid]
            if start >= _INF:
                continue
            row = dist[i]
            for j in range(n):
                cand = start + via[j]
                if cand < row[j]:
                    row[j] = cand
    return dist


def _search(adj, start, end, budget, bound, free_bonus, dist, find_ties):
    """First max-point, then min-train, simple path from ``start`` to ``end``."""
    if budget < 0 or dist[start] > budget:
        return None, []
    if start == end:
        path = [start]
        return path, [path]

    best_points = -1
    best_trains = _INF
    chosen = None
    ties: list[list[int]] = []
    visited = [False] * len(adj)
    visited[start] = True
    path = [start]

    def dfs(node: int, trains: int, points: int) -> None:
        nonlocal best_points, best_trains, chosen
        if node == end:
            if points > best_points or (points == best_points and trains < best_trains):
                best_points = points
                best_trains = trains
                chosen = path.copy()
                ties.clear()
                ties.append(chosen)
            elif find_ties and points == best_points and trains == best_trains:
                ties.append(path.copy())
            return

        remaining = budget - trains
        if dist[node] > remaining:
            return
        if best_points >= 0:
            optimistic = points + bound[remaining] + free_bonus
            if optimistic < best_points or (optimistic == best_points and trains > best_trains):
                return
            # Without tie enumeration, an equal key cannot replace the first path.
            if (
                not find_ties
                and optimistic == best_points
                and trains == best_trains
            ):
                return

        for nxt, cost, weight in adj[node]:
            if visited[nxt] or trains + cost > budget:
                continue
            visited[nxt] = True
            path.append(nxt)
            dfs(nxt, trains + cost, points + weight)
            path.pop()
            visited[nxt] = False

    dfs(start, 0, 0)
    if chosen is None:
        return None, []
    return chosen, ties
