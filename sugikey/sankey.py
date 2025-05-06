"""High-level functions for Sankey diagrams in one or few lines of code"""

from typing import Optional

import matplotlib
import networkx as nx
import pandas as pd

from . import processing
from . import draw


def sankey_from_dig(
    dig: nx.DiGraph,
    layout_config: Optional[processing.LayoutConfig] = None,
    ax: Optional[matplotlib.axes.Axes] = None,
    draw_config: Optional[draw.DrawConfig] = None,
):
    """Plot Sankey diagram from directed graph

    Args:
        dig: a directed graph with edge attribute "value"
        layout_config: layout configuration
        ax: matplotlib axes
        draw_config: drawing configuration
    """

    processing.check_digraph_before_processing(dig)
    processing.calculate_node_values(dig)
    processing.process_directed_graph(dig, layout_config)
    draw.draw_sankey(dig, ax, draw_config)


def sankey_from_df(
    flow_df: pd.DataFrame,
    layout_config: Optional[processing.LayoutConfig] = None,
    ax: Optional[matplotlib.axes.Axes] = None,
    draw_config: Optional[draw.DrawConfig] = None,
):
    """Plot Sankey diagram from dataframe

    Args:
        flow_df: a dataframe with columns "source", "target" and "value", one row per flow
        layout_config: layout configuration
        ax: matplotlib axes
        draw_config: drawing configuration
    """

    dig = processing.get_graph_from_df(flow_df)
    processing.check_digraph_before_processing(dig)
    processing.calculate_node_values(dig)
    processing.process_directed_graph(dig, layout_config)
    draw.draw_sankey(dig, ax, draw_config)
