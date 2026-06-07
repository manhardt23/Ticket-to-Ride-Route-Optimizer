# Ticket to Ride — Backend Refactor Plan

Phased refactor of the route optimizer. Each phase is self-contained so work can
resume after a context reset.

## Target layout

```
ticket-to-ride-optimal-trips/
├── PLAN.md
├── pyproject.toml
├── main.py                 # thin CLI entry
├── data/
│   ├── board.db            # SQLite runtime source of truth (generated)
│   └── archive/            # original seed txt files
├── scripts/
│   └── seed_db.py          # one-time migration from txt -> SQLite
└── src/ttro/
    ├── db/                 # schema, connection, repository
    ├── graph/             # NetworkX board + collapse
    ├── solver/             # numpy matrices, pathfinder, optimizer
    ├── viz/                # matplotlib rendering
    └── api/                # FastAPI app + schemas
```

## Phases

- [x] Phase 1 — Foundation: `.gitignore`, `pyproject.toml`, `PLAN.md`, package skeleton.
- [x] Phase 2 — SQLite: schema, seed script, repository. Txt archived under `data/archive/`.
- [x] Phase 3 — Bug fixes: capture paths before collapse; fix `path_finder_max`
  scoring; normalize `check_in_graph` return type.
- [x] Phase 4 — numpy solver: all-pairs `BoardMatrices` (Floyd-Warshall) for fast
  single-trip routing and combination pruning.
- [x] Phase 5 — API: FastAPI with `/health`, `/cities`, `/trips`, `/tracks`,
  `/solve`, `/solve/best`.
- [x] Phase 6 — Visualization: feed corrected pre-collapse paths to matplotlib.

## Run

```bash
pip install -e .
python scripts/seed_db.py     # build data/board.db from data/archive txt
python main.py                # solve + visualize
uvicorn ttro.api.app:app --reload   # serve API for the future frontend
```
