# A* Pathfinding Visualizer on Real Road Networks

> Interactive A* pathfinding on OpenStreetMap road networks, with animated
> node exploration and performance metrics. Built as a resume project
> demonstrating graph algorithms, software engineering architecture, and
> real-world data integration.

**[▶ Live Demo](https://your-app.streamlit.app)** · [Architecture](#architecture) · [How it works](#how-it-works) · [Run locally](#run-locally)

---

![Demo animation](assets/demo.gif)

---

## Features

- Downloads real road networks from OpenStreetMap via OSMnx
- A\* implemented from scratch with a haversine heuristic
- Animated node exploration showing the search frontier expanding in real time
- Performance metrics: path length, nodes explored, runtime, search efficiency
- Modular architecture — new algorithms plug in by subclassing one abstract class
- Streamlit UI with preset cities and coordinate snapping

---

## Architecture

```
pathfinding-visualizer/
│
├── algorithms/
│   ├── base.py          # Abstract PathfindingAlgorithm + SearchResult dataclass
│   └── astar.py         # A* with haversine heuristic, priority queue, closed set
│
├── graph/
│   ├── loader.py        # OSMnx download + GraphML cache layer
│   └── builder.py       # RoadGraph interface over NetworkX MultiDiGraph
│
├── visualization/
│   ├── map_view.py      # Folium map rendering (explored nodes + path overlay)
│   └── animation.py     # Streamlit progressive frame animation driver
│
├── metrics/
│   └── performance.py   # SearchMetrics dataclass + derived statistics
│
├── ui/
│   ├── state.py         # Centralised Streamlit session state management
│   ├── app.py           # Main Streamlit app shell and render logic
│   └── components.py    # Sidebar: city loader + coordinate input panels
│
├── tests/
│   ├── conftest.py      # FakeRoadGraph fixtures — no network, no OSM
│   ├── test_astar.py    # Correctness, optimality, edge cases
│   ├── test_heuristic.py# Haversine admissibility proof via unit tests
│   └── test_metrics.py  # SearchMetrics derivation and formatting
│
└── main.py              # Entry point: streamlit run main.py
```

### Data flow

```
OSM / GraphML cache
       │
       ▼
  graph/loader.py          Downloads + caches road network
       │
       ▼
  graph/builder.py         RoadGraph — clean interface for algorithm layer
       │
       ▼
  algorithms/astar.py      A* search → SearchResult
       │            │
       ▼            ▼
visualization/   metrics/
map_view.py      performance.py   Render map     Compute stats
       │            │
       └─────┬──────┘
             ▼
         ui/app.py           Streamlit shell — wires everything together
```

---

## How it works

### Graph representation

OpenStreetMap road data is downloaded via OSMnx and stored as a NetworkX
`MultiDiGraph` — a directed graph where nodes are road intersections and
edges are road segments with a `length` attribute in metres. One-way
streets are represented as directed edges, which A\* handles correctly.

The raw NetworkX graph is wrapped in `RoadGraph`, a thin interface that
decouples the algorithm layer from OSMnx. This means adding a new data
source (PostGIS, GeoPackage, synthetic test graph) requires changing only
`graph/loader.py`, not the algorithms.

### A\* algorithm

A\* finds the shortest path between two nodes by maintaining:

- **Open set** — a min-heap of `(f_score, node_id)` tuples. Heap
  operations are O(log n). Duplicate entries are allowed and filtered
  via the closed set, avoiding the cost of in-place updates.
- **Closed set** — a Python `set` of finalised node IDs. Membership
  check is O(1).
- **g\_score** — a dict of best known costs from the origin node.
- **came\_from** — a dict of predecessor pointers for path reconstruction.

The heuristic `h(n)` is the **haversine distance** between node `n` and
the destination — the straight-line distance on a sphere. This is
*admissible* (never overestimates) because road distance ≥ straight-line
distance, which guarantees A\* returns the optimal path.

**Time complexity:** O((V + E) log V)
**Space complexity:** O(V)

### Extending with a new algorithm

Every algorithm subclasses `PathfindingAlgorithm` from `algorithms/base.py`:

```python
from algorithms.base import PathfindingAlgorithm, SearchResult

class DijkstraPathfinder(PathfindingAlgorithm):
    name = "Dijkstra"

    def find_path(self, origin_node: int, destination_node: int) -> SearchResult | None:
        # your implementation here
        ...
```

The UI picks up any registered algorithm automatically — no changes to
`app.py`, `components.py`, or any other file.

---

## Run locally

```bash
git clone https://github.com/your-username/pathfinding-visualizer
cd pathfinding-visualizer

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

streamlit run main.py
```

Open `http://localhost:8501` in your browser.

**First run:** OSMnx downloads the road network from OpenStreetMap
(~10–30 seconds depending on city size). Subsequent runs load from the
local cache instantly.

### Run tests

```bash
pytest tests/ -v
```

All tests use synthetic graphs — no network access, runs in under 2 seconds.

---

## Tech stack

| Layer | Library | Why |
|---|---|---|
| Road data | OSMnx 1.9+ | Wraps Overpass API; handles topology, projection, caching |
| Graph | NetworkX 3.2+ | Standard graph library; MultiDiGraph for one-way streets |
| Visualization | Folium 0.15+ | Leaflet.js maps as self-contained HTML |
| UI | Streamlit 1.31+ | Fast interactive apps; free cloud deployment |
| Algorithms | Pure Python | No routing library — A\* implemented from scratch |

---

## Performance

On a city-scale graph (Piedmont, CA — ~2,000 nodes):

| Metric | Typical value |
|---|---|
| Graph load (cached) | < 1 second |
| A\* runtime | 5–50 ms |
| Nodes explored | 200–800 |
| Search efficiency | 40–75% |

On larger graphs (Manhattan — ~70,000 nodes), A\* runtime is typically
under 500 ms with the haversine heuristic.

---

## What I learned

- Implementing A\* with correct tie-breaking, stale-entry filtering, and
  admissible heuristic selection for geographic coordinates
- Modular Python architecture with clear separation between data, algorithm,
  and presentation layers
- Working with real-world geospatial data: coordinate systems, graph
  simplification, one-way street handling
- Streamlit session state management for multi-step interactive apps
- Writing a test suite that runs without network access using synthetic
  fixture graphs

---

## Future extensions

The algorithm base class makes these drop-in additions:

- [ ] Dijkstra (remove heuristic — useful as a correctness baseline)
- [ ] Bidirectional A\* (search from both ends simultaneously)
- [ ] Jump Point Search (order-of-magnitude speedup on uniform grids)
- [ ] D\* Lite (dynamic replanning when edges change weight)
- [ ] Algorithm comparison mode (run two algorithms side by side)
- [ ] Turn restrictions (model `via` relations from OSM)
- [ ] Isochrone maps (all nodes reachable within N minutes)

---

## License

MIT