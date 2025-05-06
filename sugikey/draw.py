"""Draw (Sankey diagram or node link diagrams)"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def get_default_text_kwargs(label_category: str, library: str) -> Dict[str, Any]:
    """Get default keyword arguments.

    Args:
        label_category: The category of the label.
            One of "node_label" or "edge_label".
        library: The library being used
            "matplotlib" or "bokeh"

    Returns:
        A dictionary with the default keyword argument, e.g. {"fontsize": 10}.
    """
    if label_category == "node_label":
        font_size: Union[int, str] = 10
    elif label_category == "edge_label":
        font_size = 8
    else:
        raise NotImplementedError("Unknown label category")

    if library.lower() == "matplotlib":
        font_size_attr = "fontsize"
        ha_attr = "ha"
    elif library.lower() == "bokeh":
        font_size_attr = "text_font_size"
        font_size = f"{font_size}px"
        ha_attr = "text_align"
    else:
        raise NotImplementedError(
            "Unknown library, currently implemented are Matplotlib and Bokeh."
        )

    txt_kwargs = {font_size_attr: font_size, ha_attr: "center"}
    return txt_kwargs


@dataclass
class DrawConfig:
    """Options for drawing

    Args:
        n_segments
        dx_node: node half width
        dx_arrow
    """

    n_segments: int = 100
    link_geometry: str = "cubic_spline"
    write_node_names: bool = True
    node_name_dy_frac: float = (
        0.1  # vertical distance between node center and node label, as a fraction of dy_node
    )
    library: str = "Matplotlib"
    node_label_kwargs: Optional[Dict[str, Any]] = None
    write_edge_values: bool = True
    edge_label_kwargs: Optional[Dict[str, Any]] = None
    edge_label_format: str = "{}"
    dx_node: float = 0.2
    dx_arrow: float = 0.1
    edge_edge_kw: Optional[Dict[str, Any]] = None
    node_edge_kw: Optional[Dict[str, Any]] = None
    edge_fill_kw: Optional[Dict[str, Any]] = None
    node_fill_kw: Optional[Dict[str, Any]] = None
    debug_visuals: bool = False
    link_color_attribute: Optional[str] = None

    def __post_init__(self):
        """Default kwargs in post-init"""
        if self.edge_edge_kw is None:
            self.edge_edge_kw = {"color": "gray"}
        if self.node_edge_kw is None:
            self.node_edge_kw = {"color": "gray"}
        if self.edge_fill_kw is None:
            self.edge_fill_kw = {"color": "deeppink", "alpha": 0.2, "lw": 0}
        if self.node_fill_kw is None:
            self.node_fill_kw = {"color": "deeppink", "alpha": 0.2, "lw": 0}
        if self.node_label_kwargs is None:
            self.node_label_kwargs = get_default_text_kwargs("node_label", self.library)
        if self.edge_label_kwargs is None:
            self.edge_label_kwargs = get_default_text_kwargs("edge_label", self.library)


def plot_node_positions(dig: nx.DiGraph, pos_var="y"):
    """Plot node positions

    Args:
        dig: a directed graph with node attributes "layer" and pos_var (by default "y")
        pos_var: a string determining which node attribute to use as y-coordinate
    """

    plt.figure()
    color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    node_colors = [
        color_cycle[dig.nodes[node]["layer"] % len(color_cycle)] for node in dig.nodes
    ]
    node_positions = {
        node: (dig.nodes[node]["layer"], dig.nodes[node][pos_var]) for node in dig.nodes
    }
    nx.draw(dig, node_color=node_colors, pos=node_positions, with_labels=True)

    for node in dig.nodes:
        x_node = dig.nodes[node]["layer"]
        y_node = dig.nodes[node][pos_var]
        dy_node = dig.nodes[node]["max_value"]
        plt.plot(
            [x_node, x_node], [y_node - dy_node / 2, y_node + dy_node / 2], color="gray"
        )


def cubic_spline_link(
    x_from_to: Optional[np.ndarray] = None,
    y_from_to: Optional[np.ndarray] = None,
    n_segments: int = 100,
):
    """Draw a (horizontally oriented) cubic spline with 0 slope from a point to another point

    Args:
        x_from_to: a numpy array with two x coordinates
        y_from_to: a numpy array with two y coordinates
        n_segments: number of straight segments with which to draw the spline

    Returns:
        two numpy arrays
    """
    if x_from_to is None:
        x_from_to = np.array([0, 1])
    if y_from_to is None:
        y_from_to = np.array([0, 1])

    assert n_segments >= 1, "There should be at least one segment"
    x_t = np.linspace(0, 1, n_segments + 1)
    y_coord = y_from_to[0] + (y_from_to[1] - y_from_to[0]) * (x_t**2 * (3 - 2 * x_t))
    x_coord = x_from_to[0] + (x_from_to[1] - x_from_to[0]) * x_t

    return x_coord, y_coord


def get_node_position(dig: nx.DiGraph, node: str) -> tuple:
    """Get node position

    Args:
        dig
        node

    Returns:
        node_x: node center x coordinate
        node_y: node (bottom) y coordinate
        d_y: node height
    """
    node_x = dig.nodes[node]["layer"]
    d_y = dig.nodes[node]["max_value"]
    node_y = dig.nodes[node]["y"] - d_y / 2
    return node_x, node_y, d_y


@dataclass
class Polyline:
    """A polyline or broken line"""

    x_list: List[float]
    y_list: List[float]
    name: str = ""
    color_attribute_value: Optional[str] = None

    @property
    def n_points(self):
        """Number of points"""
        n_x = len(self.x_list)
        n_y = len(self.y_list)
        if n_x == n_y:
            return n_x
        else:
            raise ValueError(
                "x and y-coordinates do not have the same number of points"
            )

    @property
    def is_empty(self):
        """Check whether polyline has no point"""
        return self.n_points == 0

    @property
    def coordinate_range(self):
        """Min and max or x- and y-coordinates"""
        x_range = min(self.x_list), max(self.x_list)
        y_range = min(self.y_list), max(self.y_list)
        return x_range, y_range

    def start_touches_end(self, other):
        """Does this polyline start where the other polyline ends"""
        return (self.x_list[0] == other.x_list[-1]) and (
            self.y_list[0] == other.y_list[-1]
        )

    def append_to(self, other):
        """Append this polyline to another one"""
        return Polyline(
            other.x_list + self.x_list,
            other.y_list + self.y_list,
            other.name + " + " + self.name,
        )

    def get_center(self):
        """Return coordinates of polyline barycenter"""
        x_center = np.mean(np.array(self.x_list))
        y_center = np.mean(np.array(self.y_list))
        return x_center, y_center


def concatenate_polylines(polylines: List[Polyline]) -> List[Polyline]:
    """Concatenate polylines, if their ends touch

    Args:
        polylines: to concatenate

    Returns:
        new_plines: list of polylines, fewer than the original one
    """
    new_plines = []
    candidate_pline = None
    polylines = [pline for pline in polylines if not pline.is_empty]
    for pline in polylines:
        if candidate_pline is None:
            # first polyline
            candidate_pline = pline
        elif not pline.start_touches_end(candidate_pline):
            # disjoint polylines: add candidate_pline to list, make new one candidate
            new_plines.append(candidate_pline)
            candidate_pline = pline
        else:
            candidate_pline = pline.append_to(candidate_pline)
    assert candidate_pline is not None
    new_plines.append(candidate_pline)
    return new_plines


def get_polygon(polylines: List[Polyline]) -> Polyline:
    """Concatenate polylines even if their ends do not touch (for filling)"""
    polygon = polylines[0]
    for pline in polylines[1:]:
        polygon = pline.append_to(polygon)
    return polygon


@dataclass
class Label:
    """A text element in the diagram"""

    x_txt: float
    y_txt: float
    text: str
    category: str = ""


@dataclass
class Diagram:
    """A container for the elements of a diagram, independently of the plotting library

    Attributes:
        lines: polylines, not filled
        filled: polylines, filled
        labels: text labels
    """

    lines: List[Polyline] = field(default_factory=lambda: [])
    filled: List[Polyline] = field(default_factory=lambda: [])
    labels: List[Label] = field(default_factory=lambda: [])
    color_dict: Dict[str, str] = field(default_factory=lambda: {})

    @property
    def coordinate_range(self):
        """Min and max or x- and y-coordinates"""
        (x_min, x_max), (y_min, y_max) = self.lines[0].coordinate_range
        for pline in self.lines[1:]:
            (pl_x_min, pl_x_max), (pl_y_min, pl_y_max) = pline.coordinate_range
            x_min = min(x_min, pl_x_min)
            x_max = max(x_max, pl_x_max)
            y_min = min(y_min, pl_y_min)
            y_max = max(y_max, pl_y_max)

        x_range = (x_min, x_max)
        y_range = (y_min, y_max)
        return x_range, y_range


def out_arrow_coordinates(dig, node, draw_config):
    """Get coordinates of out-flow arrow"""
    node_x, node_y, d_y = get_node_position(dig, node)
    dx_node, dx_arrow = draw_config.dx_node, draw_config.dx_arrow
    draw_out_arrow = dig.out_degree(node) == 0 and dx_arrow > 0

    if draw_out_arrow:
        x_arrow_out = [
            node_x + dx_node,
            node_x + dx_node + dx_arrow,
            node_x + dx_node,
        ]
        y_arrow_out = [node_y, node_y + d_y / 2, node_y + d_y]
    else:
        x_arrow_out = []
        y_arrow_out = []
    return Polyline(x_arrow_out, y_arrow_out, name="outflow arrow")


def in_arrow_coordinates(dig, node, draw_config):
    """Get coordinates of in-flow arrow"""
    node_x, node_y, d_y = get_node_position(dig, node)
    dx_node, dx_arrow = draw_config.dx_node, draw_config.dx_arrow
    draw_in_arrow = dig.in_degree(node) == 0 and dx_arrow > 0
    if draw_in_arrow:
        x_arrow_in = [
            node_x - dx_node,
            node_x - dx_node + dx_arrow,
            node_x - dx_node,
        ]
        y_arrow_in = [node_y + d_y, node_y + d_y / 2, node_y]

    else:
        x_arrow_in = []
        y_arrow_in = []
    return Polyline(x_arrow_in, y_arrow_in, name="inflow arrow")


@dataclass
class NodeRepresentation:
    """Geometric representation of a node"""

    polylines: List[Polyline]  # edges
    polygon: Optional[Polyline]  # filled
    label: Optional[Label]
    color_attribute_value: Optional[str] = None

    def __post_init__(self):
        col_attr_val = self.color_attribute_value
        if self.polygon is not None and col_attr_val is not None:
            for poly in self.polylines:
                poly.color_attribute_value = col_attr_val
            self.polygon.color_attribute_value = col_attr_val


def node_dx(draw_config: nx.DiGraph, node: str):
    """Get node width"""
    dx_node = draw_config.dx_node
    if "dummy" in str(node).lower():
        dx_node = 0
    return dx_node


def get_node_geometry(
    dig: nx.DiGraph, node: str, draw_config: DrawConfig, color_attribute_value=None
) -> NodeRepresentation:
    """Get geometry of a Sankey diagram for one node

    Args:
        dig
        node: node identifier, typically a str
    """
    node_x, node_y, _ = get_node_position(dig, node)

    dx_node = node_dx(draw_config, node)

    node_label = None
    if dx_node > 0 and dig.nodes[node]["max_value"] > 0:
        # plot "node", if any width
        bottom_line = Polyline(
            [node_x - dx_node, node_x + dx_node], [node_y, node_y], "bottom line"
        )
        y_top = node_y + dig.nodes[node]["max_value"]
        top_line = Polyline(
            [node_x + dx_node, node_x - dx_node], [y_top, y_top], "top line"
        )

        out_arrow = out_arrow_coordinates(dig, node, draw_config=draw_config)
        in_arrow = in_arrow_coordinates(dig, node, draw_config=draw_config)

        node_plines = [bottom_line, out_arrow, top_line, in_arrow]
        plot_plines = concatenate_polylines(node_plines)

        fill_poly = get_polygon(plot_plines)
        fill_poly.name = str(node)

        if draw_config.write_node_names and "dummy" not in str(node).lower():
            y_label = (
                dig.nodes[node]["y"]
                + dig.nodes[node]["max_value"] * draw_config.node_name_dy_frac
            )
            node_label = Label(node_x, y_label, str(node), "node_label")

    else:
        plot_plines, fill_poly = [], None
    return NodeRepresentation(
        plot_plines, fill_poly, node_label, color_attribute_value=color_attribute_value
    )


@dataclass
class LinkRepresentation:
    """Geometric representation of a link"""

    polylines: List[Polyline]  # edges
    polygon: Polyline  # filled
    label: Optional[Label]
    value: float
    color_attribute_value: Optional[str] = None

    def __post_init__(self):
        col_attr_val = self.color_attribute_value
        if col_attr_val is not None:
            for poly in self.polylines:
                poly.color_attribute_value = col_attr_val
            self.polygon.color_attribute_value = col_attr_val


def get_edge_color_value(dig, edge, draw_config):
    """Get color value of an edge"""
    if draw_config.link_color_attribute is not None:
        edge_color_val = dig.edges[edge][draw_config.link_color_attribute]
    else:
        edge_color_val = None
    return edge_color_val


def backward_link_curve(
    x_from_to,
    y_from_to,
    edge_val: float,
    below: bool,
    draw_config: Optional[DrawConfig] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Get geometry of backward link (as arises in the case of cycles)

    One half-ellipse to turn backwards, a spline and another half-ellipse to get forward into the node again

    Args:
        x_from_to: x coordinates of the two nodes
        y_from_to: y coordinates of the two nodes
        edge_val: Sankey diagram edge value
            the ellipse height will be proportional to it
        below: true for the lower edge of the link, false for the upper edge
    """
    if draw_config is None:
        draw_config = DrawConfig()
    if below:
        x_radius = 0.4
        y_radius = 2.0 * edge_val
    else:
        x_radius = 0.2
        y_radius = 1.0 * edge_val
    angle = np.linspace(-np.pi / 2, np.pi / 2, draw_config.n_segments)
    x_first_half_circle = x_from_to[0] + x_radius * np.cos(angle)
    y_first_half_circle = y_from_to[0] + y_radius * (1 + np.sin(angle))
    x_second_half_circle = x_from_to[1] - x_radius * np.cos(angle)
    y_second_half_circle = y_from_to[1] + y_radius * (1 + np.sin(angle[::-1]))
    x_link, y_link = cubic_spline_link(
        np.array([x_first_half_circle[-1], x_second_half_circle[0]]),
        np.array([y_first_half_circle[-1], y_second_half_circle[0]]),
        n_segments=draw_config.n_segments,
    )
    x_curve = np.concatenate([x_first_half_circle, x_link, x_second_half_circle])

    y_curve = np.concatenate([y_first_half_circle, y_link, y_second_half_circle])
    if not below:
        y_curve = y_curve + edge_val
    return x_curve, y_curve


def get_link_geometry(
    dig: nx.DiGraph, node, next_node, y_from, draw_config: DrawConfig
) -> LinkRepresentation:
    """Geometry of link between two nodes as part of a Sankey diagram"""

    dx_node = node_dx(draw_config, node)
    dx_node_next = node_dx(draw_config, next_node)
    x_mid, _, _ = get_node_position(dig, node)

    edge_val = dig.edges[node, next_node]["value"]
    x_next = dig.nodes[next_node]["layer"]
    y_next = dig.nodes[next_node]["y_in"]

    x_from_to = np.array([x_mid + dx_node, x_next - dx_node_next])
    y_from_to = np.array([y_from, y_next])
    if x_from_to[1] < x_from_to[0]:
        # special case of backward link
        x_below, y_below = backward_link_curve(
            x_from_to, y_from_to, edge_val, below=True, draw_config=draw_config
        )
        x_above, y_above = backward_link_curve(
            x_from_to, y_from_to, edge_val, below=False, draw_config=draw_config
        )
        # y_above = y_below + edge_val
    elif draw_config.link_geometry == "line":
        x_below = x_from_to
        y_below = y_from_to
        y_above = y_from_to + edge_val
        x_above = x_below
    elif draw_config.link_geometry == "cubic_spline":
        x_below, y_below = cubic_spline_link(
            x_from_to, y_from_to, n_segments=draw_config.n_segments
        )
        y_above = y_below + edge_val
        x_above = x_below

    x_fill = np.concatenate([x_below, x_above[::-1]])
    y_fill = np.concatenate([y_below, y_above[::-1]])

    edge_plines = [
        Polyline(x_below.tolist(), y_below.tolist()),
        Polyline(x_above.tolist(), y_above.tolist()),
    ]
    edge_name = f"{node} -> {next_node}"
    edge_poly = Polyline(x_fill.tolist(), y_fill.tolist(), name=edge_name)

    dig.nodes[next_node]["y_in"] += edge_val

    if draw_config.write_edge_values:
        label_str = draw_config.edge_label_format.format(edge_val)
        edge_label = Label(np.mean(x_fill), np.mean(y_fill), label_str, "edge_label")
    else:
        edge_label = None

    edge_color_val = get_edge_color_value(dig, (node, next_node), draw_config)

    return LinkRepresentation(
        edge_plines,
        edge_poly,
        edge_label,
        edge_val,
        color_attribute_value=edge_color_val,
    )


def get_sankey_diagram(dig: nx.DiGraph, draw_config=None) -> Diagram:
    """Determine the diagram geometry"""

    def node_y_position(nod):
        """Node vertical position"""
        return dig.nodes[nod]["vertical_position"]

    def node_layer_and_y_position(nod):
        """Node vertical position"""
        return (-dig.nodes[nod]["layer"], dig.nodes[nod]["vertical_position"])

    if draw_config is None:
        draw_config = DrawConfig()

    for node in dig.nodes:
        dig.nodes[node]["y_in"] = dig.nodes[node]["y"] - dig.nodes[node]["in_value"] / 2

    sorted_nodes = sorted(
        dig.nodes,
        key=node_layer_and_y_position,
    )
    diagram = Diagram()
    color_attribute_values = []
    for node in sorted_nodes:
        node_color_attribute_values = []

        x, node_y, dy = get_node_position(dig, node)

        sorted_successors = sorted(dig.successors(node), key=node_y_position)
        for n_next in sorted_successors:
            link_repr = get_link_geometry(
                dig,
                node,
                n_next,
                node_y,
                draw_config,
            )
            node_y += link_repr.value
            diagram.lines.extend(link_repr.polylines)
            diagram.filled.append(link_repr.polygon)
            if link_repr.label is not None:
                diagram.labels.append(link_repr.label)

            if link_repr.color_attribute_value is not None:
                color_attribute_values.append(link_repr.color_attribute_value)
                node_color_attribute_values.append(link_repr.color_attribute_value)

        predecessors = dig.predecessors(node)
        for node_pred in predecessors:
            edge_color_val = get_edge_color_value(dig, (node_pred, node), draw_config)
            if edge_color_val is not None:
                node_color_attribute_values.append(edge_color_val)

        node_color_attribute_values = list(set(node_color_attribute_values))
        # we give node a color if all incoming and outcoming edges have the same color
        if len(node_color_attribute_values) == 1:
            node_color_value = node_color_attribute_values[0]
        elif dig.out_degree(node) > 0 and dig.in_degree(node) > 0:
            # non-terminal node, allow to have color
            node_color_value = "node"
        else:
            # terminal node, melt with edge
            node_color_value = None

        node_repr = get_node_geometry(
            dig, node, draw_config, color_attribute_value=node_color_value
        )

        diagram.lines.extend(node_repr.polylines)
        if node_repr.polygon is not None:
            diagram.filled.append(node_repr.polygon)
        if node_repr.label is not None:
            diagram.labels.append(node_repr.label)

    if draw_config.link_color_attribute is not None:
        color_attribute_values = sorted(list(set(color_attribute_values)))
        color_cycler = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        diagram.color_dict = {
            attr_val: color_cycler[i_val]
            for i_val, attr_val in enumerate(color_attribute_values)
        }

    return diagram


def draw_sankey(dig, ax=None, draw_config=None):
    """The actual drawing in Matplotlib

    Args:
        dig: ready-to-plot networkx.DiGraph
        ax: a matplotlib axis

    """

    if draw_config is None:
        draw_config = DrawConfig()

    diagram = get_sankey_diagram(dig, draw_config)

    if ax is None:
        _, ax = plt.subplots()

    for pline in diagram.lines:
        edge_edge_kw = dict(draw_config.edge_edge_kw)
        if pline.color_attribute_value is not None:
            if pline.color_attribute_value == "node":
                edge_edge_kw = dict(draw_config.node_edge_kw)
            else:
                edge_edge_kw["color"] = diagram.color_dict[pline.color_attribute_value]
        ax.plot(pline.x_list, pline.y_list, **edge_edge_kw)

    for pline in diagram.filled:
        fill_kw = dict(draw_config.edge_fill_kw)
        if pline.color_attribute_value is not None:
            if pline.color_attribute_value == "node":
                fill_kw = dict(draw_config.node_fill_kw)
            else:
                fill_kw["color"] = diagram.color_dict[pline.color_attribute_value]

        ax.fill(pline.x_list, pline.y_list, **fill_kw)

    for label in diagram.labels:
        if label.category == "node_label":
            label_kwargs = draw_config.node_label_kwargs
        elif label.category == "edge_label":
            label_kwargs = draw_config.edge_label_kwargs
        else:
            raise ValueError("Unknown label category {label.category}")
        ax.text(label.x_txt, label.y_txt, label.text, **label_kwargs)

    # legend
    if draw_config.link_color_attribute is not None:
        for col_val, color in diagram.color_dict.items():
            edge_fill_kw = dict(draw_config.edge_fill_kw)
            edge_fill_kw["color"] = color
            ax.fill([], [], label=col_val, **edge_fill_kw)

        ax.legend(bbox_to_anchor=(0.5, -0.1), loc="upper center", ncol=2)

    ax.axis(False)
    return ax


def draw_edges(
    dig: nx.DiGraph,
    pos: Dict[Any, Tuple[float, float]],
    ax=None,
    plot_kwargs=None,
    draw_config: Optional[DrawConfig] = None,
    x_node_width: float = 0.0,
):
    """Draw edges of a directed graph, by default using cubic splines"""
    if ax is None:
        _, ax = plt.subplots()
    if plot_kwargs is None:
        plot_kwargs = {"color": "k"}
    if draw_config is None:
        draw_config = DrawConfig()
    for edge in dig.edges:
        p0 = pos[edge[0]]
        p1 = pos[edge[1]]
        x_from_to = np.array([p0[0] + x_node_width, p1[0] - x_node_width])
        y_from_to = np.array([p0[1], p1[1]])

        if edge[0] == edge[1]:
            edge_xs, edge_ys = backward_link_curve(
                x_from_to,
                y_from_to,
                edge_val=0.5,
                draw_config=draw_config,
                below=True,
            )
        elif draw_config.link_geometry == "line":
            edge_xs, edge_ys = x_from_to, y_from_to
        else:
            edge_xs, edge_ys = cubic_spline_link(
                x_from_to, y_from_to, n_segments=draw_config.n_segments
            )
        ax.plot(edge_xs, edge_ys, **plot_kwargs)
