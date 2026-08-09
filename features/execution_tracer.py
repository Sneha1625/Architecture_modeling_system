"""
execution_tracer.py — Static Execution Path Tracer (Step-by-Step Replay)
VTU Major Project: AI-Driven Semantic Code Analysis and Automated Software Architecture Modeling System

Walks the existing dependency/call graph starting from a chosen entry
function, using breadth-first traversal, to produce an ORDERED sequence of
call steps. The UI then lets the user step through this sequence one call
at a time, highlighting the current node/edge on the architecture diagram —
like a replay button for how the program is structured to run.

This is the SAFE version: no code is actually executed, so there is no
sandboxing risk. It reuses the graph you already build in src/dependency.py.
(A real dynamic version using sys.settrace() inside a Docker sandbox is a
separate, higher-effort feature to add later.)
"""

import networkx as nx


def trace_static_execution_path(G: nx.DiGraph, entry_point: str, max_steps=50):
    """
    Performs a breadth-first traversal of the call graph starting at
    `entry_point`, returning an ordered list of steps:
    [{"step": 1, "from": "login", "to": "check_password"}, ...]

    This approximates "what probably happens when this function runs" by
    following the graph edges in call order — it's a structural approximation,
    not a guarantee of true runtime order (loops/conditionals aren't resolved).
    """
    if entry_point not in G.nodes:
        return {"error": f"'{entry_point}' not found in the call graph."}

    visited_edges = set()
    steps = []
    queue = [entry_point]
    visited_nodes = {entry_point}

    while queue and len(steps) < max_steps:
        current = queue.pop(0)
        for neighbor in G.successors(current):
            edge = (current, neighbor)
            if edge in visited_edges:
                continue
            visited_edges.add(edge)
            steps.append({
                "step": len(steps) + 1,
                "from": current,
                "to": neighbor
            })
            if neighbor not in visited_nodes:
                visited_nodes.add(neighbor)
                queue.append(neighbor)

    return {
        "entry_point": entry_point,
        "total_steps": len(steps),
        "steps": steps,
        "nodes_reached": list(visited_nodes)
    }


def draw_execution_step(G: nx.DiGraph, steps: list, current_step: int, output_path: str):
    """
    Renders the graph with the current step's edge highlighted in red and
    all previously-visited edges highlighted in orange, so a user stepping
    through with a slider sees the "trail" build up over time.
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.8, seed=42)  # fixed seed = stable layout across redraws

    visited_edges = {(s["from"], s["to"]) for s in steps[:current_step]}
    current_edge = (steps[current_step - 1]["from"], steps[current_step - 1]["to"]) if current_step > 0 else None

    edge_colors = []
    for edge in G.edges():
        if edge == current_edge:
            edge_colors.append("red")
        elif edge in visited_edges:
            edge_colors.append("orange")
        else:
            edge_colors.append("lightgray")

    node_colors = []
    touched_nodes = set()
    for s in steps[:current_step]:
        touched_nodes.add(s["from"])
        touched_nodes.add(s["to"])
    for node in G.nodes():
        node_colors.append("gold" if node in touched_nodes else "lightblue")

    nx.draw(
        G, pos, with_labels=True, node_color=node_colors, node_size=2500,
        font_size=9, arrows=True, edge_color=edge_colors, width=2
    )
    plt.title(f"Execution Path — Step {current_step}/{len(steps)}")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    G = nx.DiGraph()
    G.add_edges_from([
        ("main", "login"), ("login", "check_password"),
        ("login", "create_session"), ("create_session", "log_activity")
    ])

    result = trace_static_execution_path(G, "main")
    print(f"Entry point: {result['entry_point']}")
    print(f"Total steps: {result['total_steps']}\n")
    for s in result["steps"]:
        print(f"  Step {s['step']}: {s['from']} → calls → {s['to']}")