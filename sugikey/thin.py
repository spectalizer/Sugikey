"""Layered graph layouts with thin edges, as a byproduct of the Sugiyama method"""

from typing import Any, Dict, Optional, Tuple

import networkx as nx

from . import processing


def get_layered_graph_layout(
    dig: nx.DiGraph, layout_config: Optional[processing.LayoutConfig] = None
) -> Dict[Any, Tuple[float, float]]:
    """Get layered graph layout for a directed graph"""
    dig = dig.copy()
    for edge in dig.edges:
        dig.edges[edge]["value"] = 1

    processing.check_digraph_before_processing(dig)
    processing.process_directed_graph(dig, layout_config=layout_config)

    pos = {node: (dig.nodes[node]["layer"], dig.nodes[node]["y"]) for node in dig.nodes}
    return pos
