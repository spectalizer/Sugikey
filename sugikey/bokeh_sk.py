"""Drawing Sankey diagrams with Bokeh

Bokeh allows interactions to be included in plots: zooming, panning, showing things on hover etc.
"""

from typing import Any, Dict, Optional

import networkx as nx
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

from . import draw


def get_bokeh_kwargs(pyplot_kwargs: Dict[str, Any]) -> dict:
    """Translate pyplot keyword arguments in bokeh keyword arguments

    Args:
        pyplot_kwargs (Dict[str, Any]): A dictionary of pyplot keyword arguments.

    Returns:
        bk_kwargs: A dictionary of bokeh keyword arguments.
    """
    bk_kwargs = {}
    kw_translate_dict = {"lw": "line_width"}
    for plt_kw, kw_val in pyplot_kwargs.items():
        bk_kw = kw_translate_dict.get(plt_kw, plt_kw)
        bk_kwargs[bk_kw] = kw_val
    return bk_kwargs


def draw_sankey_bokeh(dig: nx.DiGraph, draw_config: Optional[draw.DrawConfig] = None):
    """The actual drawing of a Sankey plot in bokeh

    Args:
        dig
        draw_config

    Returns:
        figure
    """

    if draw_config is None:
        draw_config = draw.DrawConfig()

    diagram = draw.get_sankey_diagram(dig, draw_config)

    x_range, y_range = diagram.coordinate_range

    plot = figure(
        width=800,
        height=300,
        title="",
        tools="",
        toolbar_location=None,
        match_aspect=True,
        x_range=x_range,
        y_range=y_range,
    )

    for pline in diagram.lines:
        plot.line(
            pline.x_list, pline.y_list, **get_bokeh_kwargs(draw_config.edge_edge_kw)
        )

    filled_df = pd.DataFrame(
        {"x": pline.x_list, "y": pline.y_list, "name": pline.name}
        for pline in diagram.filled
    )
    filled_source = ColumnDataSource(filled_df)
    fill_renderer = plot.patches(
        source=filled_source,
        xs="x",
        ys="y",
        **get_bokeh_kwargs(draw_config.edge_fill_kw)
    )
    fill_hover = HoverTool(renderers=[fill_renderer], tooltips=[("", "@name")])
    plot.add_tools(fill_hover)

    node_label_df = pd.DataFrame(
        [
            {"x": label.x_txt, "y": label.y_txt, "text": label.text}
            for label in diagram.labels
            if label.category == "node_label"
        ]
    )
    node_label_source = ColumnDataSource(node_label_df)
    plot.text(
        source=node_label_source,
        x="x",
        y="y",
        text="text",
        **draw_config.node_label_kwargs
    )

    edge_label_df = pd.DataFrame(
        [
            {"x": label.x_txt, "y": label.y_txt, "text": label.text}
            for label in diagram.labels
            if label.category == "edge_label"
        ]
    )
    edge_label_source = ColumnDataSource(edge_label_df)
    plot.text(
        source=edge_label_source,
        x="x",
        y="y",
        text="text",
        **draw_config.edge_label_kwargs
    )

    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.axis.visible = False
    return plot
