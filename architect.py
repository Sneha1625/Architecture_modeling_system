import networkx as nx
import matplotlib.pyplot as plt
import os


def build_graph(parsed_results):
    G = nx.DiGraph()

    for result in parsed_results:
        file_name = os.path.basename(result["file"])

        # Add file as a node
        G.add_node(file_name, type="file")

        # Add classes as nodes and connect to file
        for cls in result["classes"]:
            class_node = f"{cls['name']}"
            G.add_node(class_node, type="class")
            G.add_edge(file_name, class_node)

        # Add functions as nodes and connect to file
        for func in result["functions"]:
            func_node = f"{func['name']}()"
            G.add_node(func_node, type="function")
            G.add_edge(file_name, func_node)

        # Add imports as nodes and connect to file
        for imp in result["imports"]:
            if imp:
                G.add_node(imp, type="import")
                G.add_edge(file_name, imp)

    return G


def draw_graph(G, output_path="outputs/architecture.png"):
    os.makedirs("outputs", exist_ok=True)

    plt.figure(figsize=(14, 10))

    # Separate nodes by type for coloring
    file_nodes    = [n for n, d in G.nodes(data=True) if d.get("type") == "file"]
    class_nodes   = [n for n, d in G.nodes(data=True) if d.get("type") == "class"]
    func_nodes    = [n for n, d in G.nodes(data=True) if d.get("type") == "function"]
    import_nodes  = [n for n, d in G.nodes(data=True) if d.get("type") == "import"]

    pos = nx.spring_layout(G, seed=42, k=2)

    # Draw each node type with different colors
    nx.draw_networkx_nodes(G, pos, nodelist=file_nodes,   node_color="#4A90D9", node_size=2000)
    nx.draw_networkx_nodes(G, pos, nodelist=class_nodes,  node_color="#27AE60", node_size=1500)
    nx.draw_networkx_nodes(G, pos, nodelist=func_nodes,   node_color="#F39C12", node_size=1200)
    nx.draw_networkx_nodes(G, pos, nodelist=import_nodes, node_color="#9B59B6", node_size=1000)

    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20,
                           edge_color="#888888", width=1.5)
    nx.draw_networkx_labels(G, pos, font_size=9, font_color="white", font_weight="bold")

    # Legend
    legend = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#4A90D9", markersize=12, label="File"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#27AE60", markersize=12, label="Class"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#F39C12", markersize=12, label="Function"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#9B59B6", markersize=12, label="Import"),
    ]
    plt.legend(handles=legend, loc="upper left", fontsize=10)
    plt.title("Software Architecture Graph", fontsize=16, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"\nArchitecture diagram saved to: {output_path}")


# Test it
if __name__ == "__main__":
    from parser import parse_folder

    parsed = parse_folder("../samples")
    G = build_graph(parsed)

    print(f"Nodes in graph: {G.number_of_nodes()}")
    print(f"Edges in graph: {G.number_of_edges()}")
    print(f"\nNodes: {list(G.nodes())}")

    draw_graph(G)