"""Tests for sugikey.processing"""

import networkx as nx

from sugikey import examples, processing, sankey
from sugikey.optim import optimize_vertical_position_milp


def test_layer_assignment():
    """Test that layer assignment works"""
    height = 3
    dig = examples.balanced_tree(branching_factor=2, height=height)
    processing.assign_layers(dig)

    assert all(
        "layer" in node_data for node, node_data in dig.nodes(data=True)
    ), "Layer attribute should be assigned for all nodes"
    node_layers_dict = {
        node: node_data["layer"] for node, node_data in dig.nodes(data=True)
    }
    layer_list = sorted(list(set(node_layers_dict.values())))
    assert layer_list == sorted(processing.get_layers(dig))
    assert max(layer_list) - min(layer_list) == height + 1


def test_dummy_node_addition():
    """Test that dummy node addition results in edges being located in adjacent layers"""
    tree = nx.full_rary_tree(2, 9, create_using=nx.DiGraph)
    dig = examples.get_digraph_with_edge_values_from_tree(tree)
    processing.assign_layers(dig)
    processing.add_dummy_nodes(dig)
    for edge in dig.edges:
        edge_width = abs(dig.nodes[edge[0]]["layer"] - dig.nodes[edge[1]]["layer"])
        assert edge_width == 1


def test_assign_absolute_vertical_position():
    """Test assign_absolute_vertical_position"""

    dig = examples.balanced_tree(branching_factor=2, height=3)
    processing.calculate_node_values(dig)
    processing.assign_layers(dig)
    processing.add_dummy_nodes(dig)
    processing.initialize_relative_vertical_position(dig)
    processing.sweep_barycenter_crossing_reduction(dig)
    processing.assign_absolute_vertical_position(dig)
    assert all("y" in dig.nodes[node] for node in dig.nodes)


def test_calculate_node_values():
    """Test calculate_node_values"""

    dig = examples.balanced_tree(branching_factor=2, height=3)
    processing.calculate_node_values(dig)
    assert all("in_value" in dig.nodes[node] for node in dig.nodes)
    assert all("out_value" in dig.nodes[node] for node in dig.nodes)
    assert all("max_value" in dig.nodes[node] for node in dig.nodes)
    assert all(
        dig.nodes[node]["in_value"] <= dig.nodes[node]["max_value"]
        for node in dig.nodes
    )
    assert all(
        dig.nodes[node]["out_value"] <= dig.nodes[node]["max_value"]
        for node in dig.nodes
    )


def test_sankey_from_df():
    """Test sankey_from_df"""
    dig = examples.balanced_tree(branching_factor=2, height=3)
    flow_df = processing.get_df_from_graph(dig)
    sankey.sankey_from_df(flow_df)


def test_get_flow_df():
    """Test get_flow_df"""
    dig = examples.balanced_tree(branching_factor=2, height=3)
    flow_df = processing.get_df_from_graph(dig)
    assert all(col in flow_df.columns for col in ["source", "target", "value"])
    assert len(flow_df) == len(dig.edges)

    dig_from_df = processing.get_graph_from_df(flow_df)
    assert nx.is_isomorphic(dig, dig_from_df)


def test_no_crossing_milp():
    for exp_fun in examples.example_fun_list_no_crossing:
        dig = exp_fun()
        processing.check_digraph_before_processing(dig)
        processing.calculate_node_values(dig)
        processing.assign_layers(dig)
        processing.add_dummy_nodes(dig)
        processing.initialize_relative_vertical_position(dig)

        optimize_vertical_position_milp(dig)
        n_crossings_after = processing.count_crossing_edges(dig)
        assert n_crossings_after == 0, (
            "Crossing edges should be removed but some were left for "
            + exp_fun.__name__
        )


def test_drawing_all_examples():
    for exp_fun in examples.example_fun_list:
        dig = exp_fun()
        sankey.sankey_from_dig(dig)
