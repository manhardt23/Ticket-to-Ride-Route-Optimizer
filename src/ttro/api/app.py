from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from ttro.db import BoardRepository
from ttro.db.connection import DEFAULT_DB_PATH
from ttro.solver import Optimizer

from ttro.api.schemas import (
    City,
    RouteResult,
    SolveRequest,
    SolveResponse,
    Track,
    Trip,
)


def _ensure_board_db() -> None:
    if DEFAULT_DB_PATH.exists():
        return
    import importlib.util

    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "seed_db", root / "scripts" / "seed_db.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.seed()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _ensure_board_db()
    yield


app = FastAPI(title="Ticket to Ride Optimizer", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/cities", response_model=list[City])
def get_cities() -> list[City]:
    with BoardRepository() as repo:
        positions = repo.get_city_positions()
        return [City(name=n, x=xy[0], y=xy[1]) for n, xy in positions.items()]


@app.get("/tracks", response_model=list[Track])
def get_tracks() -> list[Track]:
    with BoardRepository() as repo:
        return [
            Track(city_a=a, city_b=b, route_points=w, train_cost=t)
            for (a, b, (w, t)) in repo.get_edges()
        ]


@app.get("/trips", response_model=list[Trip])
def get_trips() -> list[Trip]:
    with BoardRepository() as repo:
        return [
            Trip(id=i, start=s, end=e, points=p)
            for (i, s, e, p) in repo.get_trips_with_ids()
        ]


@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest) -> SolveResponse:
    optimizer = Optimizer()

    if req.auto:
        points, paths, trips = optimizer.max_set_trips(req.set_size)
    else:
        if not req.trip_ids:
            raise HTTPException(400, "Provide trip_ids or set auto=true")
        with BoardRepository() as repo:
            by_id = {i: (s, e, p) for (i, s, e, p) in repo.get_trips_with_ids()}
        missing = [tid for tid in req.trip_ids if tid not in by_id]
        if missing:
            raise HTTPException(404, f"Unknown trip ids: {missing}")
        trips = [by_id[tid] for tid in req.trip_ids]
        points, paths = optimizer.evaluate_set(trips)

    routes = [
        RouteResult(trip=list(trip), path=path)
        for trip, path in zip(trips, paths)
    ]
    return SolveResponse(points=points, routes=routes, trips=[list(t) for t in trips])


@app.get("/solve/best", response_model=SolveResponse)
def solve_best() -> SolveResponse:
    with BoardRepository() as repo:
        cached = repo.load_cached_solution()
    if cached is None:
        raise HTTPException(404, "No cached solution; run the solver first")
    routes = [
        RouteResult(trip=list(trip), path=path)
        for trip, path in zip(cached["trips"], cached["paths"])
    ]
    return SolveResponse(
        points=cached["points"],
        routes=routes,
        trips=[list(t) for t in cached["trips"]],
    )


_ROOT = Path(__file__).resolve().parents[3]
_PUBLIC_CANDIDATES = (
    _ROOT / "api" / "static",
    _ROOT / "public",
    Path(__file__).resolve().parents[1] / "static_site",
)


def _public_dir() -> Path | None:
    for candidate in _PUBLIC_CANDIDATES:
        if (candidate / "index.html").is_file():
            return candidate
    return None


def _register_static_frontend() -> None:
    """Serve Next.js export when static CDN routing is unavailable (FastAPI framework)."""
    public_dir = _public_dir()
    if public_dir is None:
        return

    @app.get("/", include_in_schema=False)
    def serve_root() -> FileResponse:
        return FileResponse(public_dir / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_static(full_path: str) -> FileResponse:
        target = public_dir / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(public_dir / "index.html")


_register_static_frontend()
