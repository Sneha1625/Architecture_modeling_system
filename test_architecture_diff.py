from architecture_model.diff import compare_architectures

from architecture_model.model import (
    Component,
    Relationship,
    ArchitectureSnapshot
)


# ============================================================
# OLD SNAPSHOT
# ============================================================

old_component_a = Component(
    id="component_a",
    name="A",
    responsibility="A functionality",
    layer="core",
    files=["a.py"],
    dependencies=[]
)

old_component_b = Component(
    id="component_b",
    name="B",
    responsibility="B functionality",
    layer="service",
    files=["b.py"],
    dependencies=[]
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
        old_component_a,
        old_component_b
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
# NEW SNAPSHOT
# ============================================================

new_component_a = Component(
    id="component_a",
    name="A",
    responsibility="A functionality",
    layer="service",
    files=["a.py"],
    dependencies=[]
)

new_component_b = Component(
    id="component_b",
    name="B",
    responsibility="B functionality",
    layer="service",
    files=["b.py"],
    dependencies=[]
)

new_component_c = Component(
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
        new_component_a,
        new_component_b,
        new_component_c
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
# COMPARE
# ============================================================

diff = compare_architectures(
    old_snapshot,
    new_snapshot
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 60)
print("ARCHITECTURE DIFF TEST")
print("=" * 60)

print()

print("Old Commit:")
print(diff["old_commit"])

print()

print("New Commit:")
print(diff["new_commit"])

print()

print("Added Components:")
print(diff["added_components"])

print()

print("Removed Components:")
print(diff["removed_components"])

print()

print("Added Relationships:")
print(diff["added_relationships"])

print()

print("Removed Relationships:")
print(diff["removed_relationships"])

print()

print("Changed Layers:")
print(diff["changed_layers"])

print()

print("Changed Metrics:")
print(diff["changed_metrics"])

print()

print("Summary:")
print(diff["summary"])

print()

print("Architecture Changed:")
print(diff["architecture_changed"])

print()

print("Architecture Change Score:")
print(
    f"{diff['change_score']} / 100"
)

print()

print("Change Level:")
print(
    diff["change_level"]
)

print()

print("Score Breakdown:")
print(
    diff["change_score_breakdown"]
)

print()
print("=" * 60)