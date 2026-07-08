from typing import Literal

from pydantic import BaseModel


class City(BaseModel):
    name: str
    x: float | None
    y: float | None


class Track(BaseModel):
    city_a: str
    city_b: str
    route_points: int
    train_cost: int


class Trip(BaseModel):
    id: int
    start: str
    end: str
    points: int


class EdgeClaim(BaseModel):
    city_a: str
    city_b: str
    owner: Literal["self", "opponent"]


class SolveRequest(BaseModel):
    trip_ids: list[int] | None = None
    edge_claims: list[EdgeClaim] = []
    auto: bool = False
    set_size: int = 10


class RouteResult(BaseModel):
    trip: list  # [start, end, points]
    path: list[str]


class SolveResponse(BaseModel):
    points: int
    trains_used: int = 0
    routes: list[RouteResult]
    trips: list[list]
    unreachable: list[int] = []
    unused_mandatory: list[tuple[str, str]] = []
