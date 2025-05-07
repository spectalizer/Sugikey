# Sugikey

## Sugikey in a nutshell

Sugikey allows you to draw Sankey diagrams and related flow diagrams in Python.
Sankey diagrams are flow diagrams composed of arrows of width proportional to the flow of e.g. energy or mass. We use the Sugiyama method to derive [layered graph layouts](https://en.wikipedia.org/wiki/Layered_graph_drawing), hence the portmanteau _Sugi(yama)(San)key_.

*Some key facts*:

* Consumes [pandas](https://pandas.pydata.org/) dataframes or [networkx](https://networkx.org/) directed graphs as inputs.
* Uses [NetworkX](https://networkx.org/) for processing of the underlying graph structure.
* Produces visual output with [Matplotlib](https://matplotlib.org/).
* Limitation: the created diagrams are not interactive, i.e. the arrows cannot be moved. Interactive Sankey diagrams can be created with a variety of other tools, including [d3-Sankey](https://github.com/d3/d3-sankey).


## Getting started

The simplest way to use the package are the high-level functions _sankey_from_dig_ and _sankey_from_df_, which take as input a networkx directed graph and a pandas dataframe, respectively.

```python
from sugikey import examples, sankey

# Sankey diagram from a networkx directed graph
dig = examples.balanced_tree_with_cross_edge()
sankey.sankey_from_dig(dig)

# Sankey diagram from a pandas dataframe
flow_df = pd.read_csv(csv_path)
sankey.sankey_from_df(flow_df)
```
