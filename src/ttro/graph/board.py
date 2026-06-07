import networkx as nx

from ttro.db import BoardRepository

TOTAL_TRAINS = 45


class Board:
    """NetworkX view of the board, built from SQLite board data.

    Edges and trips are cached at the class level so repeated construction inside
    the combinatorial search stays cheap.
    """

    _edges_cache: list | None = None
    _trips_cache: list | None = None

    def __init__(self):
        self.G = self.build_graph()

    @classmethod
    def _load_edges(cls) -> list:
        if cls._edges_cache is None:
            with BoardRepository() as repo:
                cls._edges_cache = repo.get_edges()
        return cls._edges_cache

    @classmethod
    def get_trips(cls) -> list:
        if cls._trips_cache is None:
            with BoardRepository() as repo:
                cls._trips_cache = repo.get_trips()
        return cls._trips_cache

    @classmethod
    def build_graph(cls) -> nx.Graph:
        edges = cls._load_edges()
        G = nx.Graph()
        G.add_edges_from(
            (u, v, {"weight": w, "trains": t, "ratio": w / t})
            for (u, v, (w, t)) in edges
        )
        return G

    def get_graph(self) -> nx.Graph:
        return self.G
