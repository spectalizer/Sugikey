"""Example data to test and showcase the package"""

import copy
from typing import Dict

import networkx as nx
import pandas as pd


def balanced_tree(branching_factor: int = 2, height: int = 3):
    """Balanced tree"""
    tree = nx.balanced_tree(branching_factor, height, create_using=nx.DiGraph)
    dig = get_digraph_with_edge_values_from_tree(tree)
    return dig


def siamese_balanced_tree(branching_factor=2, height=3):
    """Balanced tree with mirrored copy"""
    tree = nx.balanced_tree(branching_factor, height, create_using=nx.DiGraph)
    dig = get_digraph_with_edge_values_from_tree(tree)
    dig = get_mirrored_graph(dig)
    return dig


def balanced_tree_with_cross_edge(branching_factor=2, height=3):
    """Balanced tree with an additional cross edge"""
    tree = nx.balanced_tree(branching_factor, height, create_using=nx.DiGraph)
    dig = get_digraph_with_edge_values_from_tree(tree)
    cross_edge, edge_value = (2, 4), 20
    add_cross_edge(dig, cross_edge, edge_value)
    return dig


example_fun_list_no_crossing = [
    balanced_tree,
    balanced_tree_with_cross_edge,
    siamese_balanced_tree,
]

example_fun_list = list(example_fun_list_no_crossing)


def get_example_with_simple_cycle():
    """A tree and an added cycle"""
    dig = balanced_tree()
    dig.add_edge(4, 1, value=5)

    dig.edges[(0, 1)]["value"] = dig.edges[(0, 1)]["value"] - 5
    dig.edges[(4, 10)]["value"] = dig.edges[(4, 10)]["value"] - 5
    return dig


def get_example_with_node_cycle():
    """A tree with an added cycle from one node to itself"""
    dig = balanced_tree()
    dig.add_edge(4, 4, value=2)
    return dig


example_fun_list.extend([get_example_with_simple_cycle, get_example_with_node_cycle])  # type: ignore


def get_digraph_with_edge_values_from_tree(tree: nx.DiGraph):
    """Get a directed graph with edge values based on a tree

    Args:
        tree: a directed graph
    """

    dig = tree.copy()

    def get_value_of_tree_node(node):
        if dig.out_degree(node) == 0:
            if isinstance(node, str):
                value = 1
            else:
                value = node
        elif "value" in dig.nodes[node]:
            value = dig.nodes[node]["value"]
        else:
            value = sum(
                get_value_of_tree_node(child_node)
                for child_node in dig.successors(node)
            )
        dig.nodes[node]["value"] = value
        return value

    for node in dig:
        get_value_of_tree_node(node)

    nx.get_node_attributes(dig, "value")

    for edge in dig.edges:
        dig.edges[edge]["value"] = dig.nodes[edge[1]]["value"]

    nx.get_edge_attributes(dig, "value")
    return dig


def add_cross_edge(dig: nx.DiGraph, cross_edge: tuple, edge_value: float):
    """Add an edge to a directed graph

    After adding the edge, the added value is propagated
    on the left and right
    """
    dig.add_edge(cross_edge[0], cross_edge[1])
    dig.edges[cross_edge]["value"] = edge_value
    right_node = cross_edge[1]
    while dig.out_degree(right_node) > 0:
        after_node = list(dig.successors(right_node))[0]
        dig.edges[(right_node, after_node)]["value"] += edge_value
        right_node = after_node
    left_node = cross_edge[0]
    while dig.in_degree(left_node) > 0:
        before_node = list(dig.predecessors(left_node))[0]
        dig.edges[(before_node, left_node)]["value"] += edge_value
        left_node = before_node


def get_mirrored_graph(dig: nx.DiGraph, mirror_over_leaves: bool = True):
    """Get double graph by mirroring over leaves or root

    Args:
        dig: a directed graph to mirror
        mirror_over_leaves: whether to mirror over leaves or root(s)
    """
    siamese_dig = copy.deepcopy(dig)

    if mirror_over_leaves:

        def stays_constant(node_id):
            return dig.out_degree(node_id) == 0

    else:

        def stays_constant(node_id):
            return dig.in_degree(node_id) == 0

    def mirror_node(node_id):
        if stays_constant(node_id):
            return node_id
        return f"mirror_{node_id}"

    for node in dig.nodes:
        if not stays_constant(node) > 0:
            siamese_dig.add_node(mirror_node(node))
    for edge in dig.edges:
        parent_mirror = mirror_node(edge[0])
        child_mirror = mirror_node(edge[1])
        siamese_dig.add_edge(
            child_mirror, parent_mirror, value=dig.edges[edge]["value"]
        )
    return siamese_dig


def translate_iea_energy_balance(iea_df, year: int = 2020):
    """Translate energy balance data from IEA World Energy Balances

    See https://www.iea.org/data-and-statistics/data-product/world-energy-balances-highlights

    Example use:


    iea_df_full = pd.read_excel(iea_xlsx_path, sheet_name="TimeSeries_1971-2021", skiprows=1)
    country = "France"
    year = 2020
    iea_df = iea_df_full[iea_df_full["Country"]==country]
    flow_df = translate_iea_energy_balance(iea_df, year)

    Args:
        iea_df: a dataframe from the world energy balance highlights dataset
        year: year to visualize
    """
    flow_dict = {}  # type: Dict[str, Dict[str, float]]
    for product, flow, value in zip(iea_df["Product"], iea_df["Flow"], iea_df[year]):
        translate_iea_balance_item(product, flow, value, flow_dict)

    flow_df = pd.DataFrame(flow_dict).transpose()

    for carrier in [
        "Electricity",
        "Electricity, CHP and heat plants",
        "Oil products",
        "Heat",
    ]:
        carrier_in = flow_df.loc[flow_df["target"] == carrier, "value"].sum()
        carrier_out = flow_df.loc[flow_df["source"] == carrier, "value"].sum()
        carrier_losses = carrier_in - carrier_out
        if carrier_losses < 0:
            print(f"Gains for {carrier}?! Should not be")
        elif carrier_losses > carrier_in * 0.05:
            flow_df.loc[f"{carrier} losses"] = {
                "source": carrier,
                "target": "Losses (recalculated)",
                "value": carrier_losses,
            }
    return flow_df


def translate_iea_balance_item(product, flow, value, flow_dict):
    """Translate item data from product/flow to source/target structure"""
    flow = flow.split(" (")[0]
    flow_name = f"{product}: {flow}"
    ignore = product == "Total"
    try:
        value = float(value)
    except ValueError:
        print(f"Value for {flow_name} not valid: {value}")
        ignore = True
        # print(flow_name)

    if flow in ["Production", "Imports"]:
        source = f"{product} {flow}"
        target = product
        if flow == "Imports":
            # additional flow
            pass  # flow_dict[flow_name+" import"] = {"source": "Imports", "target": f"{product} {flow}", "value": value}
    elif flow in [
        "Exports",
        "Industry",
        "Transport",
        "Residential",
        "Commercial and public services",
        "Other final consumption",
    ]:
        if flow == "Exports":
            value = -value

        source = product
        target = flow  # f"{product} {flow}"
    elif flow in [
        "Oil refineries, transformation",
        "Electricity, CHP and heat plants",
    ]:
        if value > 0:
            target = product
            source = flow
        else:
            value = -value
            source = product
            target = flow
    elif flow in ["Total final consumption", "Total energy supply"]:
        ignore = True
    else:
        print(f"Unknown flow type {flow}")
        ignore = True
    if value == 0:
        ignore = True
    if not ignore:
        flow_dict[flow_name] = {"source": source, "target": target, "value": value}
