from typing import Any, Dict, List

import networkx as nx
import matplotlib.pyplot as plt


# ============================================================
# HELPER
# ============================================================

def _get_value(obj: Any, key: str, default=None):
    """
    Safely get a value from either an object or dictionary.
    """

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(
        obj,
        key,
        default
    )


# ============================================================
# BUILD ARCHITECTURE GRAPH
# ============================================================

def build_architecture_graph(
    snapshot: Any
) -> nx.DiGraph:
    """
    Build a directed architecture graph from a snapshot.

    Nodes:
        Architecture components

    Edges:
        Component relationships
    """

    graph = nx.DiGraph()

    components = _get_value(
        snapshot,
        "components",
        []
    ) or []

    relationships = _get_value(
        snapshot,
        "relationships",
        []
    ) or []

    # --------------------------------------------------------
    # Add components
    # --------------------------------------------------------

    for component in components:

        component_id = str(
            _get_value(
                component,
                "id",
                _get_value(
                    component,
                    "name",
                    "unknown"
                )
            )
        )

        component_name = str(
            _get_value(
                component,
                "name",
                component_id
            )
        )

        layer = str(
            _get_value(
                component,
                "layer",
                "unknown"
            )
        )

        graph.add_node(
            component_id,
            name=component_name,
            layer=layer
        )

    # --------------------------------------------------------
    # Add relationships
    # --------------------------------------------------------

    for relationship in relationships:

        source = str(
            _get_value(
                relationship,
                "source",
                ""
            )
        )

        target = str(
            _get_value(
                relationship,
                "target",
                ""
            )
        )

        relationship_type = str(
            _get_value(
                relationship,
                "type",
                "depends_on"
            )
        )

        if source and target:

            graph.add_edge(
                source,
                target,
                type=relationship_type
            )

    return graph


# ============================================================
# FIND GRAPH CHANGES
# ============================================================

def compare_graphs(
    old_graph: nx.DiGraph,
    new_graph: nx.DiGraph
) -> Dict[str, List]:
    """
    Compare two architecture graphs.

    Returns added/removed nodes and edges.
    """

    old_nodes = set(
        old_graph.nodes()
    )

    new_nodes = set(
        new_graph.nodes()
    )

    old_edges = set(
        old_graph.edges()
    )

    new_edges = set(
        new_graph.edges()
    )

    return {

        "added_nodes":
            sorted(
                new_nodes - old_nodes
            ),

        "removed_nodes":
            sorted(
                old_nodes - new_nodes
            ),

        "added_edges":
            sorted(
                new_edges - old_edges
            ),

        "removed_edges":
            sorted(
                old_edges - new_edges
            )
    }


# ============================================================
# DRAW SINGLE GRAPH
# ============================================================

def draw_architecture_graph(
    graph: nx.DiGraph,
    title: str,
    output_path: str = None
):
    """
    Draw one architecture graph.
    """

    plt.figure(
        figsize=(10, 7)
    )

    if len(graph.nodes()) == 0:

        plt.text(
            0.5,
            0.5,
            "No architecture components",
            ha="center",
            va="center"
        )

        plt.title(title)

        plt.axis("off")

        if output_path:
            plt.savefig(
                output_path,
                bbox_inches="tight"
            )

        plt.show()

        return

    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    position = nx.spring_layout(
        graph,
        seed=42
    )

    # --------------------------------------------------------
    # Node labels
    # --------------------------------------------------------

    labels = {}

    for node in graph.nodes():

        name = graph.nodes[
            node
        ].get(
            "name",
            node
        )

        layer = graph.nodes[
            node
        ].get(
            "layer",
            "unknown"
        )

        labels[node] = (
            f"{name}\n"
            f"[{layer}]"
        )

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    nx.draw_networkx_nodes(
        graph,
        position,
        node_size=2200
    )

    nx.draw_networkx_edges(
        graph,
        position,
        arrows=True,
        arrowsize=20,
        width=2
    )

    nx.draw_networkx_labels(
        graph,
        position,
        labels=labels,
        font_size=10
    )

    edge_labels = nx.get_edge_attributes(
        graph,
        "type"
    )

    nx.draw_networkx_edge_labels(
        graph,
        position,
        edge_labels=edge_labels,
        font_size=8
    )

    plt.title(title)

    plt.axis("off")

    plt.tight_layout()

    if output_path:

        plt.savefig(
            output_path,
            bbox_inches="tight"
        )

    plt.show()


# ============================================================
# BEFORE / AFTER VISUALIZATION
# ============================================================

def draw_before_after(
    old_snapshot: Any,
    new_snapshot: Any,
    old_output_path: str = None,
    new_output_path: str = None
):
    """
    Draw the old and new architecture graphs.

    Returns graph comparison information.
    """

    old_graph = build_architecture_graph(
        old_snapshot
    )

    new_graph = build_architecture_graph(
        new_snapshot
    )

    changes = compare_graphs(
        old_graph,
        new_graph
    )

    draw_architecture_graph(
        old_graph,
        "Architecture - BEFORE",
        old_output_path
    )

    draw_architecture_graph(
        new_graph,
        "Architecture - AFTER",
        new_output_path
    )

    return {
        "old_graph": old_graph,
        "new_graph": new_graph,
        "changes": changes
    }