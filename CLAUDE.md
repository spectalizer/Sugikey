# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sugikey is a Python package for drawing Sankey diagrams (flow diagrams with arrow widths proportional to flow values). It uses the Sugiyama method for layered graph layouts, hence the name "Sugi(yama)(San)key".

Key characteristics:
- Accepts pandas DataFrames or NetworkX directed graphs as input
- Uses NetworkX for graph processing
- Outputs static visualizations with Matplotlib (primary) or Bokeh (interactive)
- Requires Python >= 3.10
- Uses Poetry for dependency management

## Development Commands

### Environment Setup
```bash
# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run a specific test
poetry run pytest tests/test_layout_processing.py::test_layer_assignment
```

### Code Quality
```bash
# Format code with Black
poetry run black sugikey tests

# Sort imports with isort
poetry run isort sugikey tests

# Run linting with pylint
poetry run pylint sugikey

# Type checking with mypy
poetry run mypy sugikey
```

### Documentation
```bash
# Build documentation locally
poetry run mkdocs build

# Serve documentation with live reload
poetry run mkdocs serve
```

### Building and Publishing
```bash
# Build distribution packages
poetry build

# Publish to PyPI (maintainer only)
poetry run twine upload dist/*
```

## Architecture Overview

### Core Pipeline

The package follows a clear data transformation pipeline:

1. **Input** → 2. **Processing** → 3. **Layout** → 4. **Drawing**

#### 1. Input Layer (sankey.py)
High-level entry points:
- `sankey_from_df(flow_df)` - Accepts pandas DataFrame with columns: source, target, value
- `sankey_from_dig(dig)` - Accepts NetworkX DiGraph with edge attribute "value"

Both functions orchestrate the full pipeline from input to visualization.

#### 2. Processing Layer (processing.py)
Graph transformation and preparation:
- `get_graph_from_df()` - Converts DataFrame to NetworkX DiGraph
- `check_digraph_before_processing()` - Validates input (DAG check, edge values). Handles cycles by temporarily removing edges with lowest values.
- `calculate_node_values()` - Computes node attributes: in_value, out_value, max_value

#### 3. Layout Layer (processing.py)
Sugiyama method implementation (`process_directed_graph()`):

**Step 1: Layer Assignment** (`assign_layers()`)
- Assigns nodes to horizontal layers
- Supports "left" or "right" alignment with optional justification
- Configured via `LayoutConfig.align` and `LayoutConfig.justify`

**Step 2: Dummy Nodes** (`add_dummy_nodes()`)
- Breaks edges spanning multiple layers by inserting dummy nodes
- Ensures all edges connect adjacent layers only

**Step 3: Vertical Positioning** (three methods available)
- `"barycenter_heuristic"` (default): Fast heuristic that iteratively adjusts node positions based on connected nodes' barycenters. Uses `sweep_barycenter_crossing_reduction()` to minimize edge crossings.
- `"lp"`: Linear programming optimization (via optim.py) to minimize edge bendiness while keeping relative positions from barycenter heuristic
- `"milp"`: Mixed-integer linear programming (via optim.py) for optimal vertical positioning

Configuration via `LayoutConfig.vertical_positioning`

#### 4. Drawing Layer (draw.py)
Converts graph to visual elements:
- `get_sankey_diagram()` - Converts processed graph to `Diagram` object containing `Polyline` and `Label` objects
- `draw_sankey()` - Renders to Matplotlib (default)
- Alternative: `bokeh_sk.draw_sankey_bokeh()` for interactive Bokeh output

### Key Data Structures

**Node Attributes** (added during processing):
- `layer`: Horizontal position (layer number)
- `in_value`, `out_value`, `max_value`: Flow values
- `vertical_position`: Relative position within layer (integer)
- `y`: Absolute vertical coordinate (float)
- `y_in`: Tracks vertical position for incoming edges during drawing

**Edge Attributes**:
- `value`: Flow magnitude (required)
- Optional: custom attributes (e.g., for coloring via `DrawConfig.link_color_attribute`)

**Configuration Classes**:
- `processing.LayoutConfig`: Controls layout algorithm behavior
- `draw.DrawConfig`: Controls visual appearance (colors, labels, link geometry, etc.)

### Module Breakdown

- **sankey.py**: High-level API, coordinates the pipeline
- **processing.py**: Core Sugiyama algorithm (layer assignment, crossing reduction, positioning)
- **optim.py**: Optimization-based layout methods (LP/MILP) using PuLP
- **draw.py**: Matplotlib rendering, geometry calculations
- **bokeh_sk.py**: Bokeh rendering for interactive plots
- **thin.py**: Generates layered layouts with thin edges (non-Sankey diagrams)
- **examples.py**: Example graphs for testing and demonstrations

## Important Implementation Notes

### Cycle Handling
The package expects directed acyclic graphs (DAGs). When cycles are detected:
- `check_digraph_before_processing()` temporarily removes edges with lowest values
- Removed edges are stored in `dig.cycle_edges` attribute
- Edges are reintroduced after layer assignment but before drawing
- This allows visualization of cyclic flows as backward-pointing links

### Dummy Nodes
Dummy nodes (named like "Dummy (A, B) 0") are invisible nodes inserted to:
- Break edges spanning multiple layers
- Ensure all edges connect only adjacent layers (required for Sugiyama method)
- They have zero width (`dx_node = 0`) and are not labeled

### Coordinate System
- X-axis: Layer number (horizontal position)
- Y-axis: Vertical position (computed to minimize crossings)
- Node width controlled by `DrawConfig.dx_node`
- Link curves use cubic splines by default (`DrawConfig.link_geometry`)

### Testing Strategy
Tests focus on:
- Layer assignment correctness
- Dummy node insertion (ensuring edges span only one layer)
- Node value calculations (flow conservation)
- Cross-compatibility (DataFrame ↔ DiGraph conversions)
- Visual output generation for all example graphs

## Common Patterns

### Creating a Sankey Diagram
```python
from sugikey import sankey
import pandas as pd

# From DataFrame
df = pd.DataFrame({
    'source': ['A', 'A', 'B'],
    'target': ['B', 'C', 'C'],
    'value': [10, 5, 10]
})
sankey.sankey_from_df(df)
```

### Customizing Layout
```python
from sugikey import sankey, processing

config = processing.LayoutConfig(
    align="right",           # "left" or "right"
    justify=True,            # Align terminal nodes
    vertical_positioning="lp"  # "barycenter_heuristic", "lp", or "milp"
)
sankey.sankey_from_dig(dig, layout_config=config)
```

### Customizing Appearance
```python
from sugikey import sankey, draw

config = draw.DrawConfig(
    write_edge_values=False,
    link_geometry="line",     # "line" or "cubic_spline"
    dx_node=0.3,              # Node width
    edge_fill_kw={"color": "blue", "alpha": 0.3}
)
sankey.sankey_from_dig(dig, draw_config=config)
```

## Notes for Development

- The package uses mypy with `ignore_missing_imports = true` (see pyproject.toml)
- Semantic release is configured for automated versioning
- Documentation is built with MkDocs Material theme
- The codebase prints progress messages during processing (e.g., crossing counts) - this is intentional for user feedback
