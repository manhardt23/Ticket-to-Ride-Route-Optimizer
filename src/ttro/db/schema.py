import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS cities (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    x    REAL,
    y    REAL
);

CREATE TABLE IF NOT EXISTS tracks (
    id           INTEGER PRIMARY KEY,
    city_a_id    INTEGER NOT NULL REFERENCES cities(id),
    city_b_id    INTEGER NOT NULL REFERENCES cities(id),
    route_points INTEGER NOT NULL,
    train_cost   INTEGER NOT NULL,
    UNIQUE (city_a_id, city_b_id)
);

CREATE TABLE IF NOT EXISTS trips (
    id            INTEGER PRIMARY KEY,
    start_city_id INTEGER NOT NULL REFERENCES cities(id),
    end_city_id   INTEGER NOT NULL REFERENCES cities(id),
    points        INTEGER NOT NULL,
    UNIQUE (start_city_id, end_city_id)
);

CREATE TABLE IF NOT EXISTS solve_cache (
    id         INTEGER PRIMARY KEY CHECK (id = 1),
    points     INTEGER NOT NULL,
    paths      TEXT NOT NULL,
    trips      TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
