import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from ttro.db import BoardRepository  # noqa: E402
from ttro.graph import Board  # noqa: E402
from ttro.solver import Optimizer  # noqa: E402
from ttro.viz import Visualize  # noqa: E402


def main(visualize: bool = True) -> None:
    start = time.time()

    with BoardRepository() as repo:
        cached = repo.load_cached_solution()

        if cached is not None:
            print("Loading saved results...\n")
            points, paths, trips = cached["points"], cached["paths"], cached["trips"]
        else:
            print("Running expensive calculation, please wait...\n")
            points, paths, trips = Optimizer().max_set_trips()
            repo.save_cached_solution(points, paths, trips)

    print(f"Total Points Scored: {points}\n")

    print("Paths Taken:")
    count = 1
    for path in paths:
        if path:
            print(f"  {count}. " + " -> ".join(path))
            count += 1
    print()

    print("Trip Cards Used:")
    for start_city, end_city, score in trips:
        print(f"  - {start_city} -> {end_city} ({score} points)")
    print()

    print(f"Elapsed Time: {time.time() - start:.2f} seconds")

    if visualize:
        with BoardRepository() as repo:
            positions = repo.get_city_positions()
        Visualize(Board.build_graph(), positions).vis(highlight_paths=paths)


if __name__ == "__main__":
    main(visualize="--no-viz" not in sys.argv)
