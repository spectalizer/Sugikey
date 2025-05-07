# Sugikey


## Description
This package aims at providing a reasonably simple and flexible way to draw Sankey diagrams and related flow diagrams in Python.
Sankey diagrams are flow diagrams composed of arrows of width proportional to the flow of e.g. energy or mass. We use the Sugiyama method to derive [layered graph layouts](https://en.wikipedia.org/wiki/Layered_graph_drawing), hence the portmanteau _Sugi(yama)(San)key_.

Some key facts:
* Consumes [pandas](https://pandas.pydata.org/) dataframes or [networkx](https://networkx.org/) directed graphs as inputs.
* Uses [NetworkX](https://networkx.org/) for processing of the underlying graph structure.
* Produces visual output with [Matplotlib](https://matplotlib.org/).
* Limitation: the created diagrams are not interactive, i.e. the arrows cannot be moved. Interactive Sankey diagrams can be created with a variety of other tools, including [d3-Sankey](https://github.com/d3/d3-sankey).

Have a look at the [documentation](https://spectalizer.github.io/Sugikey/) for more information.

## Visuals
![image info](docs/imgs/balanced_with_cross_edge.svg)

## Installation
The simplest way to use Sugikey is to install the [pypi package](https://pypi.org/project/sugikey/): `pip install sugikey`.

You can also use the Python code from the repository, provided you have installed the required packages. We use [Poetry](https://python-poetry.org/) for dependency management.

You will need Python >= 3.10, as well as [NetworkX](https://networkx.org/), [pandas](https://pandas.pydata.org/), [Matplotlib](https://matplotlib.org/) and [PuLP](https://coin-or.github.io/pulp/) for layout methods using mathematical optimization.
The dependencies are managed with [Poetry](https://python-poetry.org/), which you can use to install the package (see _poetry.lock_ and _pyproject.toml_).

## Usage
The simplest way to use the package are the high-level functions _sankey_from_dig_ and _sankey_from_df_, which take as input a networkx directed graph and a pandas dataframe, respectively.

```python
import pandas as pd
from sugikey import sankey

# Sankey diagram from a pandas dataframe
flow_df = pd.read_csv(csv_path)
sankey.sankey_from_df(flow_df)
```

```python
from sugikey import sankey

# Sankey diagram from a networkx directed graph
dig = examples.balanced_tree_with_cross_edge()
sankey.sankey_from_dig(dig)
```

Have a look at the [documentation](https://spectalizer.github.io/Sugikey/) for more information.

## More on Sankey diagrams

* [Why Sankey diagrams are so great for understanding energy data](https://medium.com/@spectalizer/why-sankey-diagrams-are-so-great-for-understanding-energy-data-b14649d40890)

* [Sankey diagrams now have the package they deserve](https://medium.com/@spectalizer/sankey-diagrams-now-have-the-new-python-package-they-deserved-68754a0830d3)

## Support

Write an issue if there is an issue.


## Authors and acknowledgment
Zlatan B.


## Project status
This is a personal project without any guarantee.
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
