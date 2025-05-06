"""Processing directed graphs"""

import itertools
from dataclasses import dataclass
from typing import Optional

import networkx as nx
import numpy as np
import pandas as pd

from . import draw, optim


@dataclass
class LayoutConfig:
    """Configuration for graph layout creation

    Attributes:
        verbose
        align: for layer assignment, one of "left" and "right"
        justify: for layer assignment
        vertical_positioning: one of "barycenter_heuristic", "lp", "milp"
    """

    verbose: bool = False
    align: str = "right"
    justify: bool = True
    vertical_positioning: str = "barycenter_heuristic"
    barycenter_heuristic_n_sweep_min: int = 2
    barycenter_heuristic_n_sweep_max: int = 6


def get_graph_from_df(flow_df: pd.DataFrame) -> nx.DiGraph:
    """Get directed graph from dataframe containing flow data

    Args:
        flow_df: a dataframe with columns "source", "target" and "value", one row per flow

    Returns:
        a networkx digraph
    """
    dig = nx.DiGraph()
    node_names = list(set(flow_df["source"]).union(set(flow_df["target"])))
    dig.add_nodes_from(node_names)
    dig.add_edges_from(
        zip(
            flow_df["source"],
            flow_df["target"],
            [{"value": val} for val in flow_df["value"]],
        )
    )
    other_columns = set(flow_df.columns) - set(["source", "target", "value"])

    for col_name in other_columns:
        for src, target, col_val in zip(
            flow_df["source"], flow_df["target"], flow_df[col_name]
        ):
            dig.edges[(src, target)][col_name] = col_val

    calculate_node_values(dig)

    return dig


def get_df_from_graph(dig: nx.DiGraph) -> pd.DataFrame:
    """Return a dataframe from a directed graph

    Args:
        dig: a directed graph with edge attribute "value"

    Returns:
        a dataframe with columns "source", "target" and "value", one row per flow
    """
    edge_dict = {
        str(edge): {
            "source": edge[0],
            "target": edge[1],
            "value": dig.edges[edge]["value"],
        }
        for edge in dig.edges
    }
    flow_df = pd.DataFrame(edge_dict).transpose()
    return flow_df


def check_digraph_before_processing(dig: nx.DiGraph):
    """Check that a directed graph is fit for processing and drawing

    Args:
        dig: a directed graph with edge attribute "value"

    Raises:
        ValueError: if the directed graph is not a directed acyclic graph,
            or if edges do not have a "value" attribute
    """
    if not isinstance(dig, nx.DiGraph):
        raise ValueError(f"Should be a directed graph, but is {type(dig)}")
    if not nx.is_directed_acyclic_graph(dig):
        dig.cycle_edges = {}
        simple_cycles = list(nx.simple_cycles(dig))
        print("Simple cycles:", simple_cycles)
        while len(simple_cycles) > 0:
            cycle = simple_cycles[0]
            if len(cycle) == 1:
                cycle_edges = [(cycle[0], cycle[0])]
            else:
                cycle_edges = [
                    (cycle[i_edge], cycle[(i_edge + 1) % len(cycle)])
                    for i_edge in range(len(cycle))
                ]
            # removing the edge with the lowest value
            edge = min(cycle_edges, key=lambda edge: dig.edges[edge]["value"])
            print(f"Temporarily opening cycle {cycle} by removing edge {edge}")
            dig.cycle_edges[edge] = dig.edges[edge]
            dig.remove_edge(*edge)
            simple_cycles = list(nx.simple_cycles(dig))

        # raise ValueError(
        #    f"Should be a directed acyclic graph, but there seem to be cycles: {simple_cycles}"
        # )
    for edge in dig.edges:
        if "value" not in dig.edges[edge]:
            raise ValueError(f"No 'value' attribute for {edge}")
    print("Check directed graph before processing: seems OK")


def calculate_node_values(dig: nx.DiGraph, max_imbalance=0.05):
    """Calculate "node values" by summing edge values

    Args:
        dig: a directed graph where edges have a "value" attribute, modified in place
        max_imbalance: value above which a node is considered imbalanced and a warning is printed

    Returns:
        None. The directed graph is modified in place.
            Nodes get attributes "in_value", "out_value" and "max_value".
    """
    for node in dig.nodes:
        dig.nodes[node]["in_value"] = 0
        dig.nodes[node]["out_value"] = 0

    for n_src, n_targ, edge_data in dig.edges.data():
        edge_val = edge_data["value"]
        dig.nodes[n_targ]["in_value"] += edge_val
        dig.nodes[n_src]["out_value"] += edge_val

    for node in dig.nodes:
        in_value = dig.nodes[node]["in_value"]
        out_value = dig.nodes[node]["out_value"]
        max_value = max(in_value, out_value)
        dig.nodes[node]["max_value"] = max_value
        imbalance = abs(in_value - out_value) / (max_value + 1e-6)
        if in_value * out_value > 0 and imbalance > max_imbalance:
            print(
                f"Imbalanced node {node}: inflow {in_value:.2f} / outflow {out_value:.2f}"
            )


def assign_layers(dig: nx.DiGraph, method: Optional[LayoutConfig] = None):
    """Assign nodes to layers by length of longest directed path from each node

    This is done recursively.
    Align right: Leaves are in layer 0, parents of leaves are in layer -1 etc.
    Align left: Nodes with no parent are in layer 0, their children are in layer 1 etc.
    Align right justify:

    Args:
        dig: a networkx digraph

    Returns:
        None: the digraph is enriched with the "layer" attribute in place
    """

    if method is None:
        method = LayoutConfig()

    if method.align == "right":

        def get_nodes_to_remove(dig_copy):
            return [node for node in dig_copy if dig_copy.out_degree(node) == 0]

        layer_increment = -1
    elif method.align == "left":

        def get_nodes_to_remove(dig_copy):
            return [node for node in dig_copy if dig_copy.in_degree(node) == 0]

        layer_increment = 1
    dig_copy = dig.copy()

    layer = 0
    while dig_copy.number_of_nodes() > 0:
        nodes_to_remove = get_nodes_to_remove(dig_copy)

        if method.verbose:
            print(f"{nodes_to_remove} added to layer {layer} and removed")
        for node in nodes_to_remove:
            dig.nodes[node]["layer"] = layer
        for node in nodes_to_remove:
            dig_copy.remove_node(node)
        layer += layer_increment

    if method.justify and method.align == "right":
        for node in dig.nodes:
            if dig.in_degree(node) == 0:
                dig.nodes[node]["layer"] = layer

    if method.justify and method.align == "left":
        for node in dig.nodes:
            if dig.out_degree(node) == 0:
                dig.nodes[node]["layer"] = layer


def get_layers(dig) -> list:
    """Get layers of directed graph

    Args:
        dig: a directed graph

    Returns:
        A list of strings
    """
    layer_set = set(dig.nodes[node]["layer"] for node in dig.nodes)
    return sorted(list(layer_set))


def get_layer_nodes(dig: nx.DiGraph, lay: str, key_name: Optional[str] = None):
    """Get nodes of layer

    Args:
        dig: a directed graph
        lay: a string, name of layer
        key_name: an optional string to sort the nodes

    Returns:
        a list of strings, names of nodes
    """
    if key_name is None:

        def key_fun(node):
            return str(node)

    else:

        def key_fun(nod):
            return dig.nodes[nod][key_name]

    layer_nodes = sorted(
        [node for node in dig.nodes if dig.nodes[node]["layer"] == lay],
        key=key_fun,
    )
    return layer_nodes


def add_dummy_nodes(dig, verbose=False):
    """Add dummy node(s) for edges bridging more 2 or more layers

    Args:
        dig: a directed graph

    Returns:
        None
    """
    edges_to_break = []
    for edge in dig.edges:
        v_par, v_chi = edge
        lay_diff = dig.nodes[v_chi]["layer"] - dig.nodes[v_par]["layer"]
        if lay_diff > 1:
            edges_to_break.append(edge)

    if verbose and len(edges_to_break) > 0:
        print(f"We need a dummy node for {edges_to_break}")

    for edge in edges_to_break:
        v_par, v_chi = edge
        edge_val = dig.edges[edge]["value"]
        edge_dict = dig.edges[edge]
        lay_diff = dig.nodes[v_chi]["layer"] - dig.nodes[v_par]["layer"]
        if lay_diff < 0:
            direction_sign = -1
        else:
            direction_sign = 1
        for i_dum in range(abs(lay_diff) - 1):
            dummy_name = f"Dummy {edge} {i_dum}"
            dummy_layer = dig.nodes[v_par]["layer"] + direction_sign * (i_dum + 1)
            dig.add_node(
                dummy_name,
                layer=dummy_layer,
                in_value=edge_val,
                out_value=edge_val,
                max_value=edge_val,
            )

            if verbose:
                print(f"Adding {dummy_name}")
            if i_dum == 0:
                prev_node = edge[0]
            else:
                prev_node = f"Dummy {edge} {i_dum-1}"
            dig.add_edge(prev_node, dummy_name, **edge_dict)
            if i_dum == abs(lay_diff) - 2:
                dig.add_edge(dummy_name, edge[1], **edge_dict)
        dig.remove_edge(v_par, v_chi)


def initialize_relative_vertical_position(dig, key_name=None, verbose=False):
    """Assign/initialize relative vertical position (integer) within each layer in the simplest possible way

    Args:
        dig
        key_name: None or a string on which to sort nodes of each layer

    Returns:
        None
    """

    layers = get_layers(dig)
    if verbose:
        print(layers)

    layer_node_dict = {
        lay: get_layer_nodes(dig, lay, key_name=key_name) for lay in layers
    }
    if verbose:
        print(layer_node_dict)

    for n in dig.nodes:
        node_layer = dig.nodes[n]["layer"]
        dig.nodes[n]["vertical_position"] = layer_node_dict[node_layer].index(n)

    return layers, layer_node_dict


def edges_cross(dig: nx.DiGraph, edge_a: tuple, edge_b: tuple, verbose: bool = False):
    """Determine if two edges cross"""
    z_a = (
        dig.nodes[edge_a[0]]["vertical_position"],
        dig.nodes[edge_a[1]]["vertical_position"],
    )
    z_b = (
        dig.nodes[edge_b[0]]["vertical_position"],
        dig.nodes[edge_b[1]]["vertical_position"],
    )
    vert_pos_diff_from = (
        dig.nodes[edge_b[0]]["vertical_position"]
        - dig.nodes[edge_a[0]]["vertical_position"]
    )
    vert_pos_diff_to = (
        dig.nodes[edge_b[1]]["vertical_position"]
        - dig.nodes[edge_a[1]]["vertical_position"]
    )
    cross = (vert_pos_diff_from * vert_pos_diff_to) < 0
    if cross and verbose:
        print(f"edge_a: {edge_a} {z_a}. edge_b: {edge_b} {z_b}")
        print(f"Vertical position difference on first layer: {vert_pos_diff_from}")
        print(f"Vertical position difference on second layer: {vert_pos_diff_to}")
    return cross


def count_crossing_edges(dig: nx.DiGraph, verbose=False) -> int:
    """Count the number of crossing edge pairs in a directed graph"""
    n_crossing = 0
    layers = get_layers(dig)
    for prev_lay, next_lay in zip(layers[:-1], layers[1:]):
        # print(f'Layer {prev_lay}')
        layer_nodes = get_layer_nodes(dig, prev_lay, key_name="vertical_position")
        next_layer_nodes = get_layer_nodes(dig, next_lay, key_name="vertical_position")
        layer_edges = [
            edge
            for edge in dig.edges
            if edge[0] in layer_nodes and edge[1] in next_layer_nodes
        ]
        if verbose:
            print(f"Edges between layers {prev_lay} and {next_lay}: {layer_edges}")
        crossing_edges = [
            (edge_a, edge_b)
            for edge_a, edge_b in itertools.combinations(layer_edges, 2)
            if edges_cross(dig, edge_a, edge_b)
        ]
        if verbose:
            print(f"Crossing edge pairs: {crossing_edges}")
        n_crossing += len(crossing_edges)
    return n_crossing


def apply_barycenter_crossing_reduction_heuristic(
    dig: nx.DiGraph, from_the_left: bool = True, verbose: bool = False
):
    """Apply crossing reduction technique

    Heuristic for crossing reduction:
    changing position of nodes in layer one layer l according to the barycenter of the connected nodes in the adjacent layer (l-1 or l+1)

    Args:
        from_the_left: a boolean, True if position in a layer is changed on the basis of previous layer (left layer).
            If so, we start from the leftmost layer
    """
    #
    layers = get_layers(dig)
    if verbose:
        if from_the_left:
            print("From the left")
        else:
            print("From the right")
    if not from_the_left:
        layers = layers[::-1]

    for lay, other_lay in zip(layers[1:], layers[:-1]):
        if verbose:
            print(
                f"Changing vertical position in layer {lay} ",
                "based on connected nodes in layer {other_lay}",
            )
        layer_nodes = get_layer_nodes(dig, lay, key_name="vertical_position")
        other_layer_nodes = get_layer_nodes(
            dig, other_lay, key_name="vertical_position"
        )
        if from_the_left:
            layer_edges = [
                edge
                for edge in dig.edges
                if edge[1] in layer_nodes and edge[0] in other_layer_nodes
            ]
        else:
            layer_edges = [
                edge
                for edge in dig.edges
                if edge[0] in layer_nodes and edge[1] in other_layer_nodes
            ]
        if verbose:
            print(layer_edges)
        relative_values = []
        for node in layer_nodes:
            if from_the_left:
                connected_nodes = [edge[0] for edge in layer_edges if edge[1] == node]
            else:
                connected_nodes = [edge[1] for edge in layer_edges if edge[0] == node]
            connected_values = [
                dig.nodes[cn]["vertical_position"] for cn in connected_nodes
            ]
            relative_values.append(np.mean(connected_values))
        # add current vertical position with small weight to avoid equal values
        eps = 0.1 / len(layer_nodes)
        relative_values = np.array(relative_values) + eps * np.array(
            [dig.nodes[node]["vertical_position"] for node in layer_nodes]
        )

        if verbose:
            rel_val_dict = dict(zip(layer_nodes, relative_values))
            print(f"Relative values: {rel_val_dict}")

        # sort values, that is those that are not null
        sorted_values = sorted(relative_values)

        non_null_ids = [
            i_val for i_val, val in enumerate(relative_values) if ~np.isnan(val)
        ]
        non_null_vals = [
            val for i_val, val in enumerate(relative_values) if ~np.isnan(val)
        ]
        sorted_values = sorted(non_null_vals)
        new_values = []
        for i, val in enumerate(relative_values):
            if ~np.isnan(val):
                new_value = non_null_ids[sorted_values.index(val)]
            else:
                new_value = i
            new_values.append(new_value)
        new_val_dict = dict(zip(layer_nodes, new_values))
        if verbose:
            print(f"New relative values: {new_val_dict}")
        for i_node, node in enumerate(layer_nodes):
            dig.nodes[node]["vertical_position"] = new_values[i_node]


def sweep_barycenter_crossing_reduction(
    dig: nx.DiGraph, n_sweep_min: int = 2, n_sweep_max: int = 5, verbose: bool = False
) -> None:
    """Apply barycenter crossing reduction a number of times in each direction

    Apply it at least n_sweep_min times, then as long as the number of crossings
    is reduced up to n_sweep_max

    Args:
        dig
        n_sweep_min: the minimum number of times the crossing reduction heuristic is applied
        n_sweep_max: the maximum number of times the crossing reduction heuristic is applied

    Returns:
        None, dig is modified in place
    """
    n_cross_before = count_crossing_edges(dig)
    print(f"Edge crossing before: {n_cross_before}")
    for i_sweep in range(n_sweep_max):
        try:
            apply_barycenter_crossing_reduction_heuristic(
                dig, from_the_left=(i_sweep % 2 == 0), verbose=verbose
            )
            n_cross_after = count_crossing_edges(dig)
            print(f"Edge crossing after: {n_cross_after}")
            if n_cross_after >= n_cross_before and i_sweep >= n_sweep_min:
                break
            n_cross_before = n_cross_after
        except Exception as excep:
            print(f"Failed applying barycenter edge crossing reduction! {excep}")
            draw.plot_node_positions(dig, pos_var="vertical_position")
            apply_barycenter_crossing_reduction_heuristic(
                dig, from_the_left=(i_sweep % 2 == 0), verbose=verbose
            )


def assign_absolute_vertical_position(dig: nx.DiGraph) -> None:
    """Assign vertical position for each node based on relative vertical position

    Args:
        dig: a directed graph with the node attribute "vertical_position"

    Returns:
        None, dig is modified in place
    """

    layers = get_layers(dig)

    layer_node_dict = {
        lay: get_layer_nodes(dig, lay, key_name="vertical_position") for lay in layers
    }

    for lay in layers:
        node_y = 0
        layer_nodes = layer_node_dict[lay]
        for i_ln, node in enumerate(layer_nodes):
            if i_ln == 0:
                node_y = dig.nodes[node]["max_value"] / 2
            else:
                prev_n = layer_nodes[i_ln - 1]
                node_y += dig.nodes[prev_n]["max_value"] + dig.nodes[node]["max_value"]
            dig.nodes[node]["y"] = node_y


def process_directed_graph(
    dig: nx.DiGraph, layout_config: Optional[LayoutConfig] = None
):
    """Process directed graph to prepare Sankey diagram

    Args:
        dig: a directed graph where each node has a "max_value" attribute
        layout_method
    """

    if layout_config is None:
        layout_config = LayoutConfig()

    assign_layers(dig, method=layout_config)
    # reintroduce cycle edges
    if hasattr(dig, "cycle_edges"):
        for edge, edge_attrs in dig.cycle_edges.items():
            dig.add_edge(*edge, **edge_attrs)

    # recalculate node values after reintroducing cycle edges
    calculate_node_values(dig)
    add_dummy_nodes(dig)

    vertical_pos_method = layout_config.vertical_positioning
    initialize_relative_vertical_position(dig)
    if vertical_pos_method in ["barycenter_heuristic", "lp"]:
        n_sweep_min = layout_config.barycenter_heuristic_n_sweep_min
        n_sweep_max = layout_config.barycenter_heuristic_n_sweep_max
        sweep_barycenter_crossing_reduction(
            dig, n_sweep_min=n_sweep_min, n_sweep_max=n_sweep_max
        )

    if vertical_pos_method == "barycenter_heuristic":
        assign_absolute_vertical_position(dig)
    elif vertical_pos_method == "lp":
        optim.optimize_absolute_vertical_position_lp(dig)
    elif vertical_pos_method == "milp":
        optim.optimize_vertical_position_milp(dig)
    else:
        raise ValueError("Unknown method")
