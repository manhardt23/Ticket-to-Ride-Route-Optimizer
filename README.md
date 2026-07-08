# Ticket to Ride Route Optimizer

An intelligent route optimization system that solves the classic board game *Ticket to Ride* using graph algorithms and combinatorial optimization. The solver maximizes point scores by strategically selecting destination tickets and computing optimal paths while managing limited train resources.

## 🎯 Problem Statement

*Ticket to Ride* presents a complex optimization challenge:

- **36 North American cities** connected by railway routes
- **45 train pieces** to allocate across multiple destination tickets
- **30 possible destination tickets** with varying point values (4-22 points)
- **Constraint satisfaction**: Routes cannot overlap or reuse trains
- **Objective**: Maximize total points from completed tickets and placed trains

## 🚀 Key Features

- **Combinatorial Optimization**: Tests combinations of up to 10 destination tickets to find the highest-scoring set
- **Shortest Path Algorithm**: Uses NetworkX to compute all shortest paths and selects maximum point routes
- **Graph Contraction**: Dynamically merges completed paths to prevent resource conflicts
- **Result Caching**: Caches computation results in JSON for instant subsequent runs (< 0.1s vs ~2 min)
- **Visual Analytics**: Generates matplotlib visualizations highlighting optimal routes on the game board

## 🛠️ Technical Implementation

### Core Technologies

- **Python 3.x**
- **NetworkX**: Graph representation and pathfinding algorithms
- **Matplotlib**: Route visualization and network plotting
- **JSON**: Result persistence and caching

### Architecture

```
├── main.py              # Entry point with result caching
├── graphCreate.py       # Board graph construction and contraction
├── pathing.py           # Route optimization algorithms
├── visualize.py         # Network visualization
├── city_positions.py    # Geographic coordinate mapping
├── cities.txt           # 36 city nodes
├── tracks.txt           # Railway connections (weight, train_cost)
└── trips.txt            # Destination tickets (start, end, points)
```

### Algorithm Design

**1. Graph Representation**

```python
# Each edge stores: route_points, train_cost, efficiency_ratio
G.add_edges_from(
    (u, v, {'weight': w, 'trains': t, 'ratio': (w/t)}) 
    for (u, v, (w, t)) in edges
)
```

**2. Path Optimization**

- Computes all shortest paths between ticket destinations
- Selects path maximizing point value (train placement + ticket completion)
- Tracks remaining train resources (45 total)

**3. Graph Contraction**

- After completing a route, contracts all nodes in the path into a single representative node
- Prevents reusing trains or double-counting points
- Maintains node mappings for final route reconstruction

**4. Combinatorial Search**

- Tests C(30, 10) ≈ 30 million ticket combinations
- Early pruning: skips combinations with < 150 potential points
- Stores best solution achieving maximum point total

## 📊 Results

The optimizer achieves **220 points** by completing **10 destination tickets**:

| Route | Points |
|-------|--------|
| Seattle → New York | 22 |
| Los Angeles → New York | 21 |
| Vancouver → Montreal | 20 |
| Portland → Nashville | 17 |
| San Francisco → Atlanta | 17 |
| Los Angeles → Chicago | 16 |
| Montreal → New Orleans | 13 |
| Dallas → New York | 11 |
| Montreal → Atlanta | 9 |
| Chicago → New Orleans | 7 |

**Computation Time**: ~2 minutes (first run), < 0.1 seconds (cached)

## 🏃 Quick Start

### Prerequisites

```bash
pip install networkx matplotlib
```

### Run the Optimizer

```bash
python main.py
```

### Output

- Console displays: total points, paths taken, tickets completed, execution time
- Visualization window: interactive graph showing optimal routes highlighted in red

### Example Output

```
Total Points Scored: 220

Paths Taken:
  1. Chicago → Saint-Louis → Little-Rock → New-Orleans
  2. Dallas → Chicago → Pittsburgh → New-York
  3. Los-Angeles → El-Paso → Dallas
  ...

Trip Cards Used:
  - Seattle → New-York (22 points)
  - Los-Angeles → New-York (21 points)
  ...

Elapsed Time: 120.45 seconds
```

## 💡 Technical Highlights for Employers

This project demonstrates:

✅ **Algorithm Design**: Shortest path, graph traversal, combinatorial optimization  
✅ **Data Structures**: Graph representation, hash mapping, edge attribute storage  
✅ **Performance Optimization**: Result caching, early pruning, efficient iteration  
✅ **Software Engineering**: Modular architecture, separation of concerns, clean code  
✅ **Problem Solving**: Translated complex game rules into algorithmic constraints  
✅ **Visualization**: Created intuitive visual outputs for complex data

## 🌐 Web App

An interactive planner lives in `frontend/` (Next.js) backed by the FastAPI service
in `src/ttro/api`. Click the map to claim track for yourself or an opponent, add
tickets from your hand, and routes auto-solve around your claims — see `PLAN.md`
for the full design.

### Local development

```bash
pip install -e .
python scripts/seed_db.py          # one-time: build data/board.db from data/archive/
python -m uvicorn ttro.api.app:app --app-dir src --reload   # http://127.0.0.1:8000

cd frontend
npm install
npm run dev                        # http://localhost:3000 (proxies /solve, /cities, etc. to the API)
```

### Deploying to Vercel

The repo deploys as a **single Vercel project** — Next.js is exported to static
files and served by the same FastAPI function that answers `/cities`, `/trips`,
and `/solve`.

1. Import the repo into Vercel; leave **Root Directory** blank (repo root, not `frontend`)
2. Framework Preset: **Other** (Vercel auto-detects the FastAPI entrypoint via `vercel.json`)
3. Push to `main` — `scripts/vercel_build.py` builds the frontend and bundles it for
   `api/index.py` to serve
4. No environment variables are required for a same-domain deploy

## 🔮 Future Enhancements

- [ ]  Fix visualization to accurately render paths without edge disconnects
- [ ]  Implement reinforcement learning agent for real-time competitive play
- [x]  Web interface for interactive route planning

## 📝 License

MIT License - feel free to use for educational purposes

## 👤 Contact

**[Jacob Manhardt]**  
📧 jemanhardt@comcast.net  
💼 [LinkedIn](https://www.linkedin.com/in/jacob-manhardt-b9b75025b/)  
🐙 [GitHub](https://github.com/manhardt23)

---

*Built to showcase graph algorithms, optimization techniques, and clean Python architecture*
