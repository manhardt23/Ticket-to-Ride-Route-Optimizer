from fastapi import FastAPI, HTTPException

from ttro.db import BoardRepository
from ttro.solver import Optimizer

from .schemas import (
    City,
    RouteResult,
    SolveRequest,
    SolveResponse,
    Track,
    Trip,
)

app = FastAPI(title="Ticket to Ride Optimizer", version="0.2.0")


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
