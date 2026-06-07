"""One-time migration: load archived txt board data into SQLite (data/board.db).

Run once after cloning:  python scripts/seed_db.py
"""

import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ttro.db.connection import DEFAULT_DB_PATH, get_connection  # noqa: E402
from ttro.db.schema import create_schema  # noqa: E402

ARCHIVE = PROJECT_ROOT / "data" / "archive"


def load_positions() -> dict[str, tuple[float, float]]:
    spec = importlib.util.spec_from_file_location(
        "city_positions", ARCHIVE / "city_positions.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.city_positions


def read_cities() -> list[str]:
    lines = (ARCHIVE / "cities.txt").read_text().splitlines()
    return [line.strip() for line in lines if line.strip()]


def read_tracks() -> list[tuple[str, str, int, int]]:
    lines = (ARCHIVE / "tracks.txt").read_text().splitlines()
    tracks = []
    for line in lines:
        if not line.strip():
            continue
        a, b, points, trains = line.split()
        tracks.append((a, b, int(points), int(trains)))
    return tracks


def read_trips() -> list[tuple[str, str, int]]:
    lines = (ARCHIVE / "trips.txt").read_text().splitlines()
    trips = []
    for line in lines:
        if not line.strip():
            continue
        start, end, points = line.split()
        trips.append((start, end, int(points)))
    return trips


def seed(db_path: Path = DEFAULT_DB_PATH) -> None:
    cities = read_cities()
    positions = load_positions()
    tracks = read_tracks()
    trips = read_trips()

    conn = get_connection(db_path)
    create_schema(conn)

    conn.execute("DELETE FROM tracks")
    conn.execute("DELETE FROM trips")
    conn.execute("DELETE FROM cities")

    for name in cities:
        x, y = positions.get(name, (None, None))
        conn.execute(
            "INSERT INTO cities (name, x, y) VALUES (?, ?, ?)", (name, x, y)
        )

    city_id = {
        row["name"]: row["id"]
        for row in conn.execute("SELECT id, name FROM cities")
    }

    for a, b, points, trains in tracks:
        conn.execute(
            "INSERT INTO tracks (city_a_id, city_b_id, route_points, train_cost) "
            "VALUES (?, ?, ?, ?)",
            (city_id[a], city_id[b], points, trains),
        )

    for start, end, points in trips:
        conn.execute(
            "INSERT INTO trips (start_city_id, end_city_id, points) VALUES (?, ?, ?)",
            (city_id[start], city_id[end], points),
        )

    conn.commit()
    conn.close()

    print(f"Seeded {len(cities)} cities, {len(tracks)} tracks, {len(trips)} trips")
    print(f"Database: {db_path}")


if __name__ == "__main__":
    seed()
