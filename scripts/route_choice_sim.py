"""Compare points-then-trains routing with the old fewest-new-edges rule.

Scores every size-10 ticket set the combinatorial search already keeps
(sum of ticket points >= 150). Writes scripts/route_choice_report.md.

Usage:
    python scripts/route_choice_sim.py
    python scripts/route_choice_sim.py --sample 2000
"""

import argparse
import random
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ttro.db.connection import DEFAULT_DB_PATH  # noqa: E402
from ttro.graph import Board  # noqa: E402
from ttro.solver.optimizer import (  # noqa: E402
    DEFAULT_SET_SIZE,
    POINT_PRUNE_THRESHOLD,
    TOTAL_TRAINS,
    RouteSet,
)
from ttro.solver.pathchoice import best_simple_paths  # noqa: E402

REPORT_PATH = Path(__file__).resolve().parent / "route_choice_report.md"


def _edge_key(u: str, v: str) -> frozenset:
    return frozenset((u, v))


def _edge_label(edge: frozenset) -> str:
    a, b = sorted(edge)
    return f"{a} — {b}"


def _score_set(graph, combo, rank: str, cache: dict) -> tuple[int, RouteSet]:
    """Same loop as Optimizer.evaluate_set, plus the RouteSet that routed it."""
    routes = RouteSet(graph, rank=rank, cache=cache)
    total = 0
    for trip in combo:
        result = routes.add_trip(trip)
        if result is None:
            continue
        new_points, _path = result
        if routes.trains_used > TOTAL_TRAINS:
            return 0, routes
        total += new_points + trip[2]
    return total, routes


def _route_rows(graph, combo, rank: str, cache: dict):
    """Per-ticket path plus the claims and budget in force before that ticket."""
    routes = RouteSet(graph, rank=rank, cache=cache)
    total = 0
    rows = []
    for trip in combo:
        before = frozenset(routes.claimed)
        budget = TOTAL_TRAINS - routes.trains_used
        if budget < 0:
            budget = 0
        result = routes.add_trip(trip)
        if result is None:
            rows.append((trip, [], before, budget))
            continue
        new_points, path = result
        rows.append((trip, path, before, budget))
        if routes.trains_used > TOTAL_TRAINS:
            return 0, rows
        total += new_points + trip[2]
    return total, rows


def _tie_sig(tie: dict) -> tuple:
    return (
        tie["start"],
        tie["end"],
        tie["points"],
        tie["trains"],
        tie["prior_claims"],
        tuple(tuple(path) for path in tie["paths"]),
    )


def _passing_combos(trips, sample: int, seed: int):
    passing = [
        combo
        for combo in combinations(trips, DEFAULT_SET_SIZE)
        if sum(trip[2] for trip in combo) >= POINT_PRUNE_THRESHOLD
    ]
    total = len(passing)
    if sample and sample < total:
        rng = random.Random(seed)
        passing = rng.sample(passing, sample)
    return passing, total


def _band(scores: list[int], best: int, near: int) -> tuple[int, list[int]]:
    """Sets at the best score, widened until 20 sets or ``near`` points."""
    band = 0
    kept = [i for i, score in enumerate(scores) if score >= best]
    while band < near and len(kept) < 20:
        band += 1
        kept = [i for i, score in enumerate(scores) if score >= best - band]
    return band, kept


def _write_report(path: Path, text: str) -> None:
    path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="Score this many pruned sets instead of every one (0 = all)",
    )
    parser.add_argument(
        "--near",
        type=int,
        default=10,
        help="Widen the top band by at most this many points when the best score is rare",
    )
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    if not DEFAULT_DB_PATH.exists():
        sys.path.insert(0, str(ROOT / "scripts"))
        from seed_db import seed

        seed()

    graph = Board.build_graph()
    trips = Board.get_trips()
    route_points = {
        _edge_key(u, v): data["weight"] for u, v, data in graph.edges(data=True)
    }

    print("Listing pruned ticket sets...", flush=True)
    t0 = time.perf_counter()
    combos, pruned_total = _passing_combos(trips, args.sample, args.seed)
    print(
        f"{len(combos)} sets to score ({pruned_total} pass the point prune) "
        f"in {time.perf_counter() - t0:.1f}s",
        flush=True,
    )

    points_cache: dict = {}
    scores: list[int] = []
    ties: dict[tuple, dict] = {}
    t1 = time.perf_counter()
    for index, combo in enumerate(combos, start=1):
        score, routes = _score_set(graph, combo, "points", points_cache)
        scores.append(score)
        for tie in routes.ties:
            ties.setdefault(_tie_sig(tie), tie)
        if index % 20000 == 0:
            print(f"  scored {index}/{len(combos)}", flush=True)
    elapsed = time.perf_counter() - t1
    best = max(scores) if scores else 0
    band, kept = _band(scores, best, args.near)
    print(
        f"Scored {len(scores)} sets in {elapsed:.1f}s. "
        f"Best {best}. Keeping {len(kept)} sets within {band} points.",
        flush=True,
    )

    edges_cache: dict = {}
    times_used: Counter = Counter()
    extra_tickets: Counter = Counter()
    used_in_changed_path: Counter = Counter()
    sets_with_a_change = 0
    old_best_among_kept = 0
    old_sets_under_cap = 0
    old_best_completed = (0, 0)

    for nth, combo_index in enumerate(kept, start=1):
        combo = combos[combo_index]
        new_score, new_rows = _route_rows(graph, combo, "points", points_cache)
        if new_score != scores[combo_index]:
            raise RuntimeError(
                f"rescore {new_score} != first pass {scores[combo_index]}"
            )
        old_score, old_rows = _route_rows(graph, combo, "edges", edges_cache)
        if old_score > old_best_among_kept:
            old_best_among_kept = old_score
            old_best_completed = (
                sum(1 for _trip, path, _before, _budget in new_rows if path),
                sum(1 for _trip, path, _before, _budget in old_rows if path),
            )
        if old_score > 0:
            old_sets_under_cap += 1
        old_paths = {(_trip[0], _trip[1]): path for _trip, path, _before, _budget in old_rows}

        placed: set[frozenset] = set()
        set_changed = False
        for trip, path, before, budget in new_rows:
            if not path:
                continue
            old_path = old_paths.get((trip[0], trip[1]), [])
            path_changed = path != old_path
            if path_changed:
                set_changed = True
            for u, v in zip(path, path[1:]):
                edge = _edge_key(u, v)
                placed.add(edge)
                if path_changed:
                    used_in_changed_path[edge] += 1
                if edge not in before:
                    continue
                claimed = set(before)
                claimed.discard(edge)
                alt, _tied = best_simple_paths(
                    graph,
                    trip[0],
                    trip[1],
                    budget,
                    claimed=claimed,
                    cache=points_cache,
                )
                if alt is None:
                    extra_tickets[edge] += 1
        for edge in placed:
            times_used[edge] += 1
        if set_changed:
            sets_with_a_change += 1
        if nth % 500 == 0:
            print(f"  detailed {nth}/{len(kept)}", flush=True)

    # An edge's path changed when any kept set used it on a ticket whose
    # points-rank path differs from the edges-rank path.
    changed_edges = set(used_in_changed_path)

    histogram = Counter(scores)
    top_buckets = sorted(histogram.items(), reverse=True)[:8]
    open_ties = [tie for tie in ties.values() if tie["prior_claims"] == 0]
    later_ties = [tie for tie in ties.values() if tie["prior_claims"] != 0]
    solo_ties = []
    for trip in trips:
        alone = RouteSet(graph)
        alone.add_trip(trip)
        solo_ties.extend(alone.ties)

    lines = [
        "# Route choice on high-point ticket sets",
        "",
        "Within one ticket the router now keeps the simple path with the most",
        "new route points, then the fewest new trains, that still fits in",
        f"{TOTAL_TRAINS} minus trains already placed. The old rule kept the",
        "fewest new edges, then the fewest trains, then the most points.",
        "Ticket sets are the ones the combinatorial search already considers:",
        f"size {DEFAULT_SET_SIZE}, sum of ticket points >= {POINT_PRUNE_THRESHOLD}.",
        "Trips inside a set are routed in trip-list order, the same order",
        "`evaluate_set` uses. Hands from `evaluate_hand` are still sorted",
        "by ticket points, highest first.",
        "",
        f"Scored **{len(scores)}** of **{pruned_total}** pruned sets"
        + (
            f" (random sample, seed {args.seed})."
            if args.sample and args.sample < pruned_total
            else "."
        ),
        f"Best score under the new key: **{best}**.",
        f"Kept **{len(kept)}** sets with score >= {best - band}"
        + (f" (best, or within {band} points)." if band else " (the best score)."),
        f"Among those, the best score under the old key was **{old_best_among_kept}**"
        f" ({old_sets_under_cap} of {len(kept)} stayed within 45 trains).",
        "The old key still uses the hard fail in `evaluate_set`: the set scores 0",
        "once placed trains pass 45. Path changed compares the route each key",
        "chose for a ticket, including tickets routed before that fail.",
        (
            f"The set that stayed under the cap scored {old_best_among_kept} "
            f"with the old key ({old_best_completed[1]} tickets reached) and "
            f"{best} with the new key ({old_best_completed[0]} tickets reached)."
            if old_sets_under_cap
            else "No kept set stayed within 45 trains under the old key."
        ),
        f"The new key changed at least one ticket path in **{sets_with_a_change}**"
        f" of {len(kept)} kept sets.",
        "",
        "Route points below are the track's own value. A kept set adds that",
        "value once when the edge is placed, even if later tickets reuse it.",
        "Extra tickets counts, across the kept sets, later tickets that use",
        "the edge and have no budget-feasible path if that edge is no longer",
        "free. Path changed is yes when any kept set uses the edge on a",
        "ticket whose path differs from the old key.",
        "",
        "Top score counts:",
        "",
    ]
    for score, count in top_buckets:
        lines.append(f"- {score}: {count} sets")
    lines.extend(["", "## Ties after points and trains", ""])
    if not solo_ties:
        lines.append("No ticket had two paths with the same points and the same trains.")
    else:
        seen_in_sets = {(tie["start"], tie["end"]) for tie in open_ties}
        lines.append(
            f"{len(solo_ties)} tickets still tie on an empty board: same route "
            "points and same trains, so the first path is kept."
        )
        lines.append("")
        for tie in solo_ties:
            in_sets = (tie["start"], tie["end"]) in seen_in_sets
            lines.append(
                f"- **{tie['start']} — {tie['end']}**: "
                f"{tie['points']} route points, {tie['trains']} trains, "
                f"{len(tie['paths'])} paths"
                + ("" if in_sets else " (never first in a size-10 set)")
            )
            for path in tie["paths"]:
                lines.append(f"  - {' -> '.join(path)}")
        if later_ties:
            lines.append("")
            lines.append(
                f"{len(later_ties)} more tie(s) showed up only after some track "
                "was already claimed. Same points, same trains, first path kept."
            )
            for tie in sorted(later_ties, key=lambda item: (item["start"], item["end"]))[:12]:
                lines.append(
                    f"- **{tie['start']} — {tie['end']}** "
                    f"({tie['prior_claims']} edges already claimed): "
                    f"{tie['points']} points, {tie['trains']} trains, "
                    f"{len(tie['paths'])} paths"
                )
            if len(later_ties) > 12:
                lines.append(f"- … {len(later_ties) - 12} more claimed-board ties")
        elif open_ties:
            lines.append("")
            lines.append(
                "No size-10 set tied again after some track was already claimed."
            )

    lines.extend(
        [
            "",
            "## Edges in the kept sets",
            "",
            "| Edge | Times used | Route points | Extra tickets | Path changed |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    ranked = sorted(
        times_used,
        key=lambda edge: (
            -times_used[edge],
            -route_points[edge],
            -extra_tickets[edge],
            _edge_label(edge),
        ),
    )
    if not ranked:
        lines.append("| — | 0 | 0 | 0 | no |")
    for edge in ranked:
        lines.append(
            "| {label} | {times} | {points} | {extra} | {changed} |".format(
                label=_edge_label(edge),
                times=times_used[edge],
                points=route_points[edge],
                extra=extra_tickets[edge],
                changed="yes" if edge in changed_edges else "no",
            )
        )
    lines.append("")
    _write_report(REPORT_PATH, "\n".join(lines))
    print(f"Wrote {REPORT_PATH}", flush=True)


if __name__ == "__main__":
    main()
