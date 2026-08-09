"""
community_detector.py — Automatic Module Boundary Detection
VTU Major Project: AI-Driven Semantic Code Analysis and Automated Software Architecture Modeling System

Runs the Louvain community detection algorithm on the existing dependency graph
(src/dependency.py) to automatically suggest how a codebase should be split
into logical modules — functions/classes that call each other a lot end up
in the same suggested module, even if no one explicitly organized them that way.

Pure graph algorithm, no AI/LLM call, fully local and free.
"""

import networkx as nx

try:
    import community as community_louvain  # pip install python-louvain
    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False


def detect_communities(G: nx.DiGraph):
    """
    Runs Louvain community detection on a (possibly directed) dependency graph.
    Louvain requires an undirected graph, so we convert first — direction of
    a call doesn't matter for "these things belong together," only that a
    relationship exists.

    Returns: {
        "partition": {node_name: community_id, ...},
        "communities": {community_id: [node names], ...},
        "modularity": float (0-1, higher = cleaner/more natural clustering),
        "num_communities": int
    }
    """
    if not HAS_LOUVAIN:
        return {"error": "python-louvain not installed. Run: pip install python-louvain"}

    if G.number_of_nodes() == 0:
        return {"error": "Graph is empty — nothing to cluster."}

    undirected = G.to_undirected()

    # Isolated nodes (no edges at all) break Louvain's modularity calc in some
    # versions — keep them but they'll each form their own singleton community.
    partition = community_louvain.best_partition(undirected)

    communities = {}
    for node, comm_id in partition.items():
        communities.setdefault(comm_id, []).append(node)

    modularity = community_louvain.modularity(partition, undirected)

    return {
        "partition": partition,
        "communities": communities,
        "modularity": round(modularity, 4),
        "num_communities": len(communities)
    }


def suggest_module_names(communities: dict, G: nx.DiGraph):
    """
    Gives each detected community a human-friendly suggested name based on
    its most "central" node (the one with the most connections within the
    cluster) — e.g. community containing [validate_user, hash_password,
    check_session] might get named after validate_user if it's most central.

    This is a simple heuristic, not AI — degree centrality within the subgraph.
    """
    named = {}
    for comm_id, nodes in communities.items():
        subgraph = G.subgraph(nodes)
        if len(nodes) == 0:
            continue
        degrees = dict(subgraph.degree())
        anchor = max(degrees, key=degrees.get) if degrees else nodes[0]
        named[comm_id] = {
            "suggested_name": f"{anchor}_module",
            "members": nodes,
            "size": len(nodes)
        }
    return named


def analyze_modularity(G: nx.DiGraph):
    """
    High-level entry point used by the UI. Returns communities plus
    suggested names plus a plain-language interpretation of the modularity score.
    """
    result = detect_communities(G)
    if "error" in result:
        return result

    named = suggest_module_names(result["communities"], G)

    mod_score = result["modularity"]
    if mod_score > 0.4:
        interpretation = "Strong natural modularity — this codebase already has clear, well-separated logical groupings."
    elif mod_score > 0.2:
        interpretation = "Moderate modularity — some grouping exists but boundaries are a bit blurry."
    else:
        interpretation = "Weak modularity — this codebase is highly interconnected with no clear natural module boundaries; consider refactoring toward looser coupling."

    return {
        "modularity_score": mod_score,
        "interpretation": interpretation,
        "num_communities": result["num_communities"],
        "suggested_modules": named
    }


if __name__ == "__main__":
    G = nx.DiGraph()
    G.add_edges_from([
        ("login", "check_password"), ("login", "create_session"),
        ("check_password", "hash_password"), ("create_session", "check_password")
    ])
    G.add_edges_from([
        ("generate_report", "fetch_data"), ("generate_report", "format_output"),
        ("fetch_data", "format_output")
    ])
    G.add_edge("login", "generate_report")

    result = analyze_modularity(G)
    print(f"Modularity score: {result['modularity_score']}")
    print(f"Interpretation: {result['interpretation']}")
    print(f"Detected {result['num_communities']} suggested modules:\n")
    for comm_id, info in result["suggested_modules"].items():
        print(f"  Module '{info['suggested_name']}' ({info['size']} members): {info['members']}")