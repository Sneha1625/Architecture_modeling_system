"""
architect.py — Automated Software Architecture Graph Generator
VTU Major Project: AI-Driven Semantic Code Analysis and Automated Software Architecture Modeling System
"""

import networkx as nx
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for Streamlit
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os


# Node color scheme
NODE_COLORS = {
    "file":     "#4A90D9",   # Blue
    "class":    "#27AE60",   # Green
    "function": "#F39C12",   # Orange
    "method":   "#E67E22",   # Dark orange
    "import":   "#9B59B6",   # Purple
}

NODE_SIZES = {
    "file":     3000,
    "class":    2000,
    "function": 1400,
    "method":   1200,
    "import":   900,
}


def build_graph(parsed_results):
    """
    Build a directed graph from parsed AST results.
    Includes: file → class → method, file → function, file → import,
    and function → function call edges from the call graph.
    """
    G = nx.DiGraph()

    for result in parsed_results:
        file_name = os.path.basename(result["file"])

        # File node
        G.add_node(file_name, type="file", label=file_name)

        # Class nodes + method nodes
        for cls in result.get("classes", []):
            class_node = f"{cls['name']}"
            G.add_node(class_node, type="class", label=cls["name"],
                       line=cls["line"])
            G.add_edge(file_name, class_node, edge_type="contains")

            for method in cls.get("methods", []):
                method_node = f"{cls['name']}.{method['name']}()"
                G.add_node(method_node, type="method", label=method["name"],
                           line=method["line"])
                G.add_edge(class_node, method_node, edge_type="has_method")

        # Function nodes
        for func in result.get("functions", []):
            func_node = f"{func['name']}()"
            G.add_node(func_node, type="function", label=func["name"]+"()",
                       line=func["line"],
                       complexity=func.get("complexity", 1))
            G.add_edge(file_name, func_node, edge_type="contains")

        # Call graph edges (function → called function)
        call_graph = result.get("call_graph", {})
        all_func_nodes = {f["name"] for f in result.get("functions", [])}
        for caller, callees in call_graph.items():
            caller_node = f"{caller}()"
            if caller_node in G.nodes:
                for callee in callees:
                    callee_node = f"{callee}()"
                    if callee_node in G.nodes:
                        G.add_edge(caller_node, callee_node, edge_type="calls")

        # Import nodes (top 8 only to avoid clutter)
        for imp in result.get("imports", [])[:8]:
            if imp:
                G.add_node(imp, type="import", label=imp)
                G.add_edge(file_name, imp, edge_type="imports")

    return G


def get_hierarchical_layout(G):
    """
    Create a layered layout:
    - Layer 0: file nodes (top)
    - Layer 1: classes and top-level functions
    - Layer 2: methods
    - Layer 3: imports (bottom)
    """
    layers = {"file": [], "class": [], "function": [],
              "method": [], "import": []}

    for node, data in G.nodes(data=True):
        t = data.get("type", "function")
        if t in layers:
            layers[t].append(node)

    pos = {}
    layer_y = {"file": 1.0, "class": 0.65, "function": 0.65,
               "method": 0.3, "import": -0.05}

    for layer_name, nodes in layers.items():
        if not nodes:
            continue
        y = layer_y[layer_name]
        n = len(nodes)
        for i, node in enumerate(nodes):
            x = (i - (n - 1) / 2) * (1.8 / max(n, 1))
            pos[node] = (x, y)

    return pos


def draw_graph(G, output_path="outputs/architecture.png"):
    """
    Draw and save the architecture graph as a high-quality PNG.
    """
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "outputs", exist_ok=True)

    if G.number_of_nodes() == 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No nodes to display", ha="center", va="center",
                fontsize=14, color="gray")
        ax.axis("off")
        plt.savefig(output_path, dpi=150, bbox_inches="tight",
                    facecolor="#1a1a2e")
        plt.close()
        return

    fig, ax = plt.subplots(figsize=(16, 11))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    # Layout
    try:
        pos = get_hierarchical_layout(G)
        # Fill any missing nodes with spring layout
        missing = [n for n in G.nodes() if n not in pos]
        if missing:
            sub = G.subgraph(missing)
            sp = nx.spring_layout(sub, seed=42)
            pos.update(sp)
    except Exception:
        pos = nx.spring_layout(G, seed=42, k=2.5)

    # Separate nodes by type
    node_groups = {}
    for node, data in G.nodes(data=True):
        t = data.get("type", "function")
        node_groups.setdefault(t, []).append(node)

    # Separate edges by type
    call_edges = [(u, v) for u, v, d in G.edges(data=True)
                  if d.get("edge_type") == "calls"]
    other_edges = [(u, v) for u, v, d in G.edges(data=True)
                   if d.get("edge_type") != "calls"]

    # Draw structural edges
    nx.draw_networkx_edges(
        G, pos, edgelist=other_edges,
        arrows=True, arrowsize=18,
        edge_color="#4a5568", width=1.5,
        connectionstyle="arc3,rad=0.05", ax=ax
    )

    # Draw call edges (dashed, different color)
    if call_edges:
        nx.draw_networkx_edges(
            G, pos, edgelist=call_edges,
            arrows=True, arrowsize=14,
            edge_color="#f6ad55", width=1.2, style="dashed",
            connectionstyle="arc3,rad=0.15", ax=ax
        )

    # Draw nodes by type
    for node_type, nodes in node_groups.items():
        if not nodes:
            continue
        nx.draw_networkx_nodes(
            G, pos, nodelist=nodes,
            node_color=NODE_COLORS.get(node_type, "#888"),
            node_size=NODE_SIZES.get(node_type, 1000),
            alpha=0.95, ax=ax
        )

    # Labels — short display names
    labels = {}
    for node, data in G.nodes(data=True):
        lbl = data.get("label", node)
        labels[node] = lbl if len(lbl) <= 18 else lbl[:16] + "…"

    nx.draw_networkx_labels(
        G, pos, labels=labels,
        font_size=8, font_color="white",
        font_weight="bold", ax=ax
    )

    # Layer labels
    for label, y in [("File", 1.0), ("Classes / Functions", 0.65),
                     ("Methods", 0.3), ("Imports", -0.05)]:
        ax.text(-1.35, y, label, fontsize=9, color="#718096",
                va="center", ha="right", style="italic")

    # Legend
    legend_handles = [
        mpatches.Patch(color=NODE_COLORS["file"],     label="File"),
        mpatches.Patch(color=NODE_COLORS["class"],    label="Class"),
        mpatches.Patch(color=NODE_COLORS["function"], label="Function"),
        mpatches.Patch(color=NODE_COLORS["method"],   label="Method"),
        mpatches.Patch(color=NODE_COLORS["import"],   label="Import"),
        plt.Line2D([0],[0], color="#4a5568", linewidth=2,  label="Contains"),
        plt.Line2D([0],[0], color="#f6ad55", linewidth=2,
                   linestyle="dashed", label="Calls"),
    ]
    ax.legend(
        handles=legend_handles, loc="upper right",
        fontsize=9, facecolor="#2d3748", labelcolor="white",
        edgecolor="#4a5568", framealpha=0.9
    )

    ax.set_title(
        "Software Architecture Graph\nAI-Driven Semantic Code Analysis System",
        fontsize=14, fontweight="bold", color="white", pad=16
    )

    # Stats annotation
    stats = (f"Nodes: {G.number_of_nodes()}  |  "
             f"Edges: {G.number_of_edges()}  |  "
             f"Call edges: {len(call_edges)}")
    ax.text(0, -0.18, stats, transform=ax.transData,
            fontsize=8, color="#718096", ha="center")

    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="#1a1a2e")
    plt.close()
    print(f"Architecture diagram saved: {output_path}")


if __name__ == "__main__":
    from parser import parse_file

    parsed = parse_file("../samples/sample.py")
    G = build_graph([parsed])

    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Node list: {list(G.nodes())}")

    draw_graph(G, "outputs/architecture.png")