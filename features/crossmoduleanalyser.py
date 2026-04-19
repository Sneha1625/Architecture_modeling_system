"""
cross_module_analyzer.py — Multi-file Cross-Module Dependency Analyzer
VTU Major Project Feature 3: Analyzes multiple Python files together,
builds cross-file call graphs, detects circular dependencies, and
identifies shared functions/classes across modules.

Usage in app.py:
    from cross_module_analyzer import analyze_project, get_cross_module_graph
"""

import os
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict
from typing import List, Dict


def analyze_project(parsed_results: List[Dict]) -> Dict:
    """
    Analyze multiple parsed files together as a single project.
    Returns cross-module relationships, shared symbols, and dependency info.
    """
    project = {
        "files": [],
        "all_functions": {},
        "all_classes": {},
        "all_imports": defaultdict(list),
        "cross_calls": [],
        "circular_deps": [],
        "shared_imports": [],
        "dependency_matrix": {}
    }

    # Index all symbols by file
    for parsed in parsed_results:
        fname = os.path.basename(parsed["file"])
        project["files"].append(fname)

        for fn in parsed.get("functions", []):
            project["all_functions"][fn["name"]] = {
                "file": fname,
                "line": fn["line"],
                "complexity": fn.get("complexity", 1)
            }

        for cls in parsed.get("classes", []):
            project["all_classes"][cls["name"]] = {
                "file": fname,
                "line": cls["line"]
            }

        for imp in parsed.get("imports", []):
            project["all_imports"][imp].append(fname)

    # Detect cross-file calls
    for parsed in parsed_results:
        src_file = os.path.basename(parsed["file"])
        call_graph = parsed.get("call_graph", {})
        for caller, callees in call_graph.items():
            for callee in callees:
                if callee in project["all_functions"]:
                    callee_file = project["all_functions"][callee]["file"]
                    if callee_file != src_file:
                        project["cross_calls"].append({
                            "from_file":     src_file,
                            "from_function": caller,
                            "to_file":       callee_file,
                            "to_function":   callee
                        })

    # Detect shared imports (used in 2+ files)
    project["shared_imports"] = [
        {"module": mod, "used_in": files}
        for mod, files in project["all_imports"].items()
        if len(files) > 1
    ]

    # Build file dependency matrix
    for f in project["files"]:
        project["dependency_matrix"][f] = {
            other: 0 for other in project["files"]
        }
    for call in project["cross_calls"]:
        project["dependency_matrix"][call["from_file"]][call["to_file"]] += 1

    # Detect circular dependencies using NetworkX
    G = nx.DiGraph()
    for call in project["cross_calls"]:
        G.add_edge(call["from_file"], call["to_file"])
    try:
        cycles = list(nx.simple_cycles(G))
        project["circular_deps"] = cycles
    except Exception:
        project["circular_deps"] = []

    return project


def get_cross_module_graph(parsed_results: List[Dict], output_path: str = "outputs/cross_module.png") -> nx.DiGraph:
    """
    Build and draw a cross-module architecture graph showing file-level dependencies.
    """
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "outputs", exist_ok=True)

    G = nx.DiGraph()
    project = analyze_project(parsed_results)

    # Add file nodes with metadata
    for parsed in parsed_results:
        fname = os.path.basename(parsed["file"])
        G.add_node(fname,
                   type="file",
                   functions=len(parsed.get("functions", [])),
                   classes=len(parsed.get("classes", [])))

    # Add shared import nodes
    for item in project["shared_imports"]:
        G.add_node(item["module"], type="shared_import")
        for f in item["used_in"]:
            G.add_edge(f, item["module"], edge_type="imports")

    # Add cross-call edges
    for call in project["cross_calls"]:
        if G.has_edge(call["from_file"], call["to_file"]):
            G[call["from_file"]][call["to_file"]]["weight"] = \
                G[call["from_file"]][call["to_file"]].get("weight", 0) + 1
        else:
            G.add_edge(call["from_file"], call["to_file"],
                       edge_type="cross_call", weight=1)

    # Draw
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    pos = nx.spring_layout(G, seed=42, k=3.0)

    file_nodes   = [n for n, d in G.nodes(data=True) if d.get("type") == "file"]
    import_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "shared_import"]
    call_edges   = [(u, v) for u, v, d in G.edges(data=True) if d.get("edge_type") == "cross_call"]
    import_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("edge_type") == "imports"]
    weights      = [G[u][v].get("weight", 1) * 1.5 for u, v in call_edges]

    nx.draw_networkx_nodes(G, pos, nodelist=file_nodes,
                           node_color="#4A90D9", node_size=2500, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=import_nodes,
                           node_color="#9B59B6", node_size=1200, ax=ax)
    if call_edges:
        nx.draw_networkx_edges(G, pos, edgelist=call_edges,
                               edge_color="#F39C12", width=weights,
                               arrows=True, arrowsize=20,
                               connectionstyle="arc3,rad=0.2", ax=ax)
    if import_edges:
        nx.draw_networkx_edges(G, pos, edgelist=import_edges,
                               edge_color="#9B59B6", width=1, style="dashed",
                               arrows=True, arrowsize=14, ax=ax)

    # Labels with function count
    labels = {}
    for n, d in G.nodes(data=True):
        if d.get("type") == "file":
            fns = d.get("functions", 0)
            cls = d.get("classes", 0)
            labels[n] = f"{n}\n{fns}fn {cls}cls"
        else:
            labels[n] = n
    nx.draw_networkx_labels(G, pos, labels=labels,
                            font_size=8, font_color="white",
                            font_weight="bold", ax=ax)

    legend = [
        mpatches.Patch(color="#4A90D9", label="Python file"),
        mpatches.Patch(color="#9B59B6", label="Shared import"),
        plt.Line2D([0],[0], color="#F39C12", linewidth=2, label="Cross-file call"),
        plt.Line2D([0],[0], color="#9B59B6", linewidth=1,
                   linestyle="dashed", label="Import dependency"),
    ]
    ax.legend(handles=legend, loc="upper left", fontsize=9,
              facecolor="#2d3748", labelcolor="white", edgecolor="#4a5568")

    # Circular dep warning
    if project["circular_deps"]:
        warning = f"⚠ Circular deps: {len(project['circular_deps'])} detected"
        ax.text(0.5, 0.02, warning, transform=ax.transAxes,
                fontsize=9, color="#fc8181", ha="center",
                bbox=dict(boxstyle="round", facecolor="#3d1515", alpha=0.8))

    ax.set_title("Cross-Module Architecture Graph\nAI-Driven Code Analysis System",
                 fontsize=14, fontweight="bold", color="white", pad=16)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()
    print(f"Cross-module graph saved: {output_path}")
    return G


def get_project_summary(project: Dict) -> Dict:
    """Return high-level project summary from cross-module analysis."""
    return {
        "total_files":        len(project["files"]),
        "total_functions":    len(project["all_functions"]),
        "total_classes":      len(project["all_classes"]),
        "cross_file_calls":   len(project["cross_calls"]),
        "shared_imports":     len(project["shared_imports"]),
        "circular_deps":      len(project["circular_deps"]),
        "has_circular_deps":  len(project["circular_deps"]) > 0
    }


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from src.parser import parse_folder

    results = parse_folder("../samples")
    project = analyze_project(results)
    summary = get_project_summary(project)

    print("=== Cross-Module Analysis ===")
    print(f"Files:           {summary['total_files']}")
    print(f"Functions:       {summary['total_functions']}")
    print(f"Cross-file calls:{summary['cross_file_calls']}")
    print(f"Shared imports:  {summary['shared_imports']}")
    print(f"Circular deps:   {summary['circular_deps']}")

    get_cross_module_graph(results, "outputs/cross_module.png")