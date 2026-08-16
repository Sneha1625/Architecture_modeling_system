from architecture_model.model import (
    Component,
    Relationship,
    ArchitectureSnapshot
)

from architecture_model.graph_diff import (
    build_architecture_graph,
    compare_graphs,
    draw_before_after
)


print("=" * 60)
print("ARCHITECTURE BEFORE / AFTER GRAPH TEST")
print("=" * 60)


# ============================================================
# OLD ARCHITECTURE
# ============================================================

old_a = Component(
    id="component_a",
    name="A",
    responsibility="A functionality",
    layer="core",
    files=["a.py"],
    dependencies=[]
)

old_b = Component(
    id="component_b",
    name="B",
    responsibility="B functionality",
    layer="service",
    files=["b.py"],
    dependencies=["component_a"]
)

old_relationship = Relationship(
    source="component_a",
    target="component_b",
    type="depends_on"
)

old_snapshot = ArchitectureSnapshot(
    version="1.0",
    commit_hash="commit_old",
    components=[
        old_a,
        old_b
    ],
    relationships=[
        old_relationship
    ],
    metrics={
        "total_components": 2,
        "total_relationships": 1,
        "total_files": 2
    },
    violations=[]
)


# ============================================================
# NEW ARCHITECTURE
# ============================================================

new_a = Component(
    id="component_a",
    name="A",
    responsibility="A functionality",
    layer="service",
    files=["a.py"],
    dependencies=[]
)

new_b = Component(
    id="component_b",
    name="B",
    responsibility="B functionality",
    layer="service",
    files=["b.py"],
    dependencies=["component_a"]
)

new_c = Component(
    id="component_c",
    name="C",
    responsibility="C functionality",
    layer="data",
    files=["c.py"],
    dependencies=[]
)

new_relationship_1 = Relationship(
    source="component_a",
    target="component_b",
    type="depends_on"
)

new_relationship_2 = Relationship(
    source="component_a",
    target="component_c",
    type="depends_on"
)

new_snapshot = ArchitectureSnapshot(
    version="1.0",
    commit_hash="commit_new",
    components=[
        new_a,
        new_b,
        new_c
    ],
    relationships=[
        new_relationship_1,
        new_relationship_2
    ],
    metrics={
        "total_components": 3,
        "total_relationships": 2,
        "total_files": 3
    },
    violations=[]
)


# ============================================================
# BUILD GRAPHS
# ============================================================

old_graph = build_architecture_graph(
    old_snapshot
)

new_graph = build_architecture_graph(
    new_snapshot
)


print()
print("BEFORE GRAPH")
print("-" * 60)

print(
    "Nodes:",
    list(old_graph.nodes())
)

print(
    "Edges:",
    list(old_graph.edges())
)


print()
print("AFTER GRAPH")
print("-" * 60)

print(
    "Nodes:",
    list(new_graph.nodes())
)

print(
    "Edges:",
    list(new_graph.edges())
)


# ============================================================
# GRAPH DIFFERENCE
# ============================================================

changes = compare_graphs(
    old_graph,
    new_graph
)


print()
print("GRAPH CHANGES")
print("-" * 60)

print(
    "Added Nodes:",
    changes["added_nodes"]
)

print(
    "Removed Nodes:",
    changes["removed_nodes"]
)

print(
    "Added Edges:",
    changes["added_edges"]
)

print(
    "Removed Edges:",
    changes["removed_edges"]
)


# ============================================================
# DRAW
# ============================================================

print()
print("Opening BEFORE architecture graph...")

draw_before_after(
    old_snapshot,
    new_snapshot
)


print()
print("=" * 60)
print("ARCHITECTURE GRAPH TEST COMPLETED")
print("=" * 60)