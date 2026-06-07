from pathlib import Path

from .connection import DEFAULT_DB_PATH, get_connection


class BoardRepository:
    """Read-only access to board data stored in SQLite."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.conn = get_connection(db_path)

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "BoardRepository":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def get_cities(self) -> list[str]:
        rows = self.conn.execute("SELECT name FROM cities ORDER BY id").fetchall()
        return [r["name"] for r in rows]

    def get_city_positions(self) -> dict[str, tuple[float, float]]:
        rows = self.conn.execute("SELECT name, x, y FROM cities").fetchall()
        return {r["name"]: (r["x"], r["y"]) for r in rows}

    def get_edges(self) -> list[tuple[str, str, tuple[int, int]]]:
        rows = self.conn.execute(
            """
            SELECT a.name AS a, b.name AS b, t.route_points, t.train_cost
            FROM tracks t
            JOIN cities a ON a.id = t.city_a_id
            JOIN cities b ON b.id = t.city_b_id
            ORDER BY t.id
            """
        ).fetchall()
        return [(r["a"], r["b"], (r["route_points"], r["train_cost"])) for r in rows]

    def get_trips(self) -> list[tuple[str, str, int]]:
        rows = self.conn.execute(
            """
            SELECT s.name AS start, e.name AS end, t.points
            FROM trips t
            JOIN cities s ON s.id = t.start_city_id
            JOIN cities e ON e.id = t.end_city_id
            ORDER BY t.id
            """
        ).fetchall()
        return [(r["start"], r["end"], r["points"]) for r in rows]

    def get_trips_with_ids(self) -> list[tuple[int, str, str, int]]:
        rows = self.conn.execute(
            """
            SELECT t.id, s.name AS start, e.name AS end, t.points
            FROM trips t
            JOIN cities s ON s.id = t.start_city_id
            JOIN cities e ON e.id = t.end_city_id
            ORDER BY t.id
            """
        ).fetchall()
        return [(r["id"], r["start"], r["end"], r["points"]) for r in rows]

    def load_cached_solution(self) -> dict | None:
        import json

        row = self.conn.execute(
            "SELECT points, paths, trips FROM solve_cache WHERE id = 1"
        ).fetchone()
        if row is None:
            return None
        return {
            "points": row["points"],
            "paths": json.loads(row["paths"]),
            "trips": json.loads(row["trips"]),
        }

    def save_cached_solution(self, points: int, paths: list, trips: list) -> None:
        import json

        self.conn.execute(
            """
            INSERT INTO solve_cache (id, points, paths, trips)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                points = excluded.points,
                paths = excluded.paths,
                trips = excluded.trips,
                created_at = datetime('now')
            """,
            (points, json.dumps(paths), json.dumps(trips)),
        )
        self.conn.commit()
