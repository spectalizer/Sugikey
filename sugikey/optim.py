"""Optimization-based layout functions

Optimization of the vertical position of each node formulated as a linear problem.
"""

import itertools
from typing import Dict

import networkx as nx
import pulp

from . import processing


def var_name(node_name: str) -> str:
    """Get a variable name valid for pulp

    Args:
        node_name: a string or other hashable type

    Returns:
        a modified node name without special characters
    """
    node_name = str(node_name)

    replace_dict = {
        "-": "(hyphen)",
        ",": "(comma)",
        "+": "(plus)",
        "[": "(leftBracket)",
        "]": "(rightBracket)",
        " ": "(space)",
        ">": "(greaterThan)",
        "/": "(slash)",
    }
    for to_repl, replacement in replace_dict.items():
        node_name = node_name.replace(to_repl, replacement)

    return node_name


def add_bendiness_objective(
    prob: pulp.LpProblem, dig: nx.DiGraph, node_pos_dict: Dict[str, float]
):
    """Add bendiness to the objective function

    Args:
        prob: the PuLP problem
        dig: the directed graph
        node_pos_dict: a dictionary of node positions

    Returns:
        the bendiness sum variable
    """
    bendiness_vars = []
    for n_from, n_to in dig.edges:
        edge_bendiness = pulp.LpVariable(
            "bendiness_" + var_name(n_from) + "_" + var_name(n_to)
        )
        bendiness_vars.append(edge_bendiness)
        prob += (
            node_pos_dict[n_from] - node_pos_dict[n_to]
        ) <= edge_bendiness, f"y_from - y_to <= Edge bendiness {n_from} {n_to}"
        prob += (
            node_pos_dict[n_to] - node_pos_dict[n_from]
        ) <= edge_bendiness, f"y_to - y_from <= Edge bendiness {n_from} {n_to}"

    bendiness_sum = pulp.LpVariable("sumBendiness")
    prob += bendiness_sum == pulp.lpSum(bend_var for bend_var in bendiness_vars)
    return bendiness_sum


def add_distance_to_center(
    prob: pulp.LpProblem, node_pos_dict: Dict[str, float], node: str
):
    """Add a variable corresponding to the absolute distance to 0

    Args:
        prob: the PuLP problem
        node_pos_dict: a dictionary of node positions
        node: the node name

    Returns:
        the absolute node position variable
    """
    abs_node_pos = pulp.LpVariable("abs(" + var_name(node) + ")")
    prob += node_pos_dict[node] <= abs_node_pos, f"x <= |x| for {node}"
    prob += -node_pos_dict[node] <= abs_node_pos, f"-x <= |x| for {node}"
    return abs_node_pos


def optimize_absolute_vertical_position_lp(dig: nx.DiGraph):
    """Optimize absolute position of nodes, where relative position is already fixed

    The formulation minimizes the distances of nodes to center (y=0)
    and the vertical distances between nodes joined by an edge

    Args:
        dig: the directed graph

    Returns:
        None. The node positions ("y" attribute) are updated in the graph
    """
    # Create the 'prob' variable to contain the problem data
    prob = pulp.LpProblem("SugiyamaLP", pulp.LpMinimize)

    # Variables
    layers = processing.get_layers(dig)

    layer_node_dict = {
        lay: processing.get_layer_nodes(dig, lay, key_name="vertical_position")
        for lay in layers
    }

    node_pos_dict = {}
    center_distances = []
    for lay in layers:
        layer_nodes = layer_node_dict[lay]

        for i_n, node in enumerate(layer_nodes):
            node_pos_dict[node] = pulp.LpVariable(var_name(node))
            abs_node_pos = add_distance_to_center(prob, node_pos_dict, node)
            center_distances.append(abs_node_pos)

            if i_n > 0:
                prev_n = layer_nodes[i_n - 1]
                prob += (
                    node_pos_dict[prev_n] + dig.nodes[prev_n]["max_value"]
                    <= node_pos_dict[node] - dig.nodes[node]["max_value"] / 2
                ), f"Minimum distance between nodes {prev_n} {node}"

    center_dist_sum = pulp.LpVariable("sumDistancesToCenter")
    prob += center_dist_sum == pulp.lpSum(cent_dist for cent_dist in center_distances)

    bendiness_sum = add_bendiness_objective(prob, dig, node_pos_dict)

    lambda_bendiness = 2.0
    prob += (
        center_dist_sum + lambda_bendiness * bendiness_sum,
        "Minimize sum of distances to center plus bendiness",
    )

    # The problem is solved using PuLP's choice of Solver
    prob.solve(pulp.PULP_CBC_CMD(msg=1))

    for node, opt_var in node_pos_dict.items():
        dig.nodes[node]["y"] = opt_var.varValue


def optimize_vertical_position_milp(dig: nx.DiGraph, verbose: bool = False) -> None:
    """Optimize absolute and relative position of nodes

    The formulation minimizes the distances of nodes to center (y=0)
    and the vertical distances between nodes joined by an edge

    Args:
        dig: the directed graph
        verbose: whether to print the problem

    Returns:
        None. The node positions ("y" attribute) are updated in the graph
    """
    # Parameters
    lambda_bendiness = 2.0
    lambda_crossings = 200.0
    min_dist_between_nodes = 5
    # Create the 'prob' variable to contain the problem data
    prob = pulp.LpProblem("SugiyamaLP", pulp.LpMinimize)

    # Variables
    layers = processing.get_layers(dig)

    layer_node_dict = {lay: processing.get_layer_nodes(dig, lay) for lay in layers}

    node_pos_dict = {}
    node_rel_pos_dict = {}
    crossing_vars = []

    center_distances = []

    for lay in layers:
        src_layer_nodes = layer_node_dict[lay]

        for node in src_layer_nodes:
            node_pos_dict[node] = pulp.LpVariable(var_name(node))
            abs_node_pos = add_distance_to_center(prob, node_pos_dict, node)
            center_distances.append(abs_node_pos)

        for i_n1, i_n2 in itertools.permutations(range(len(src_layer_nodes)), 2):
            n_1 = src_layer_nodes[i_n1]
            n_2 = src_layer_nodes[i_n2]
            node_rel_pos_dict[(n_1, n_2)] = pulp.LpVariable(
                var_name(n_1) + "_above_" + var_name(n_2), cat="Binary"
            )

            # if n1 is above n2, yn1 - yn2 should be above 0 and larger than some distance
            prob += (
                node_pos_dict[n_1]
                - node_pos_dict[n_2]
                - dig.nodes[n_1]["max_value"] / 2
                - dig.nodes[n_2]["max_value"] / 2
                - min_dist_between_nodes
                + 1000 * (1 - node_rel_pos_dict[(n_1, n_2)])
                >= 0
            )

        # constraint: n1 above n2 or n2 above n1 for any pair of nodes n1, n2
        for i_n1, i_n2 in itertools.combinations(range(len(src_layer_nodes)), 2):
            n_1 = src_layer_nodes[i_n1]
            n_2 = src_layer_nodes[i_n2]
            prob += node_rel_pos_dict[(n_1, n_2)] + node_rel_pos_dict[(n_2, n_1)] == 1

    # crossings
    for src_lay, next_lay in zip(layers[:-1], layers[1:]):
        src_layer_nodes = processing.get_layer_nodes(dig, src_lay)
        next_layer_nodes = processing.get_layer_nodes(dig, next_lay)
        layer_edges = [
            edge
            for edge in dig.edges
            if edge[0] in src_layer_nodes and edge[1] in next_layer_nodes
        ]
        for i_e1, i_e2 in itertools.combinations(range(len(layer_edges)), 2):
            n1a, n1b = layer_edges[i_e1]
            n2a, n2b = layer_edges[i_e2]

            if not (n1a == n2a) and not (n1b == n2b):
                cross_var_name = (
                    var_name(n1a)
                    + "_"
                    + var_name(n1b)
                    + "_crosses_"
                    + var_name(n2a)
                    + "_"
                    + var_name(n2b)
                )
                cross_var = pulp.LpVariable(
                    cross_var_name,
                    cat="Binary",
                )  # 1 if the two edges cross
                prob += (
                    cross_var
                    >= node_rel_pos_dict[(n1a, n2a)] + node_rel_pos_dict[(n2b, n1b)] - 1
                )
                prob += (
                    cross_var
                    >= node_rel_pos_dict[(n2a, n1a)] + node_rel_pos_dict[(n1b, n2b)] - 1
                )
                crossing_vars.append(cross_var)

    center_dist_sum = pulp.LpVariable("sumDistancesToCenter")
    prob += center_dist_sum == pulp.lpSum(cent_dist for cent_dist in center_distances)

    n_crossings = pulp.LpVariable("numberOfEdgeCrossings")
    prob += n_crossings == pulp.lpSum(cr for cr in crossing_vars)

    bendiness_sum = add_bendiness_objective(prob, dig, node_pos_dict)

    prob += (
        center_dist_sum
        + lambda_bendiness * bendiness_sum
        + lambda_crossings * n_crossings,
        "Minimize sum of crossings plus distances to center plus bendiness",
    )

    # The problem is solved using PuLP's choice of Solver
    # prob.solve()
    prob.solve(pulp.PULP_CBC_CMD(msg=1))

    if verbose:
        # Each of the variables is printed with it's resolved optimum value
        for opt_var in prob.variables():
            print(opt_var.name, "=", opt_var.varValue)

    for node, opt_var in node_pos_dict.items():
        dig.nodes[node]["y"] = opt_var.varValue
        dig.nodes[node]["vertical_position"] = 0

    for lay in layers:
        src_layer_nodes = layer_node_dict[lay]
        for i_n1, i_n2 in itertools.permutations(range(len(src_layer_nodes)), 2):
            n_1 = src_layer_nodes[i_n1]
            n_2 = src_layer_nodes[i_n2]
            dig.nodes[n_1]["vertical_position"] += node_rel_pos_dict[
                (n_1, n_2)
            ].varValue
            if verbose:
                print((n_1, n_2, node_rel_pos_dict[(n_1, n_2)].varValue))

    return prob
