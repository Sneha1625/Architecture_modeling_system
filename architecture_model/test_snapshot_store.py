from architecture_model.model import (
    Component,
    Relationship,
    ArchitectureSnapshot
)

from architecture_model.snapshot_store import (
    save_snapshot,
    snapshot_exists
)


print("=" * 60)
print("ARCHITECTURE SNAPSHOT STORE TEST")
print("=" * 60)


component_a = Component(
    id="component_a",
    name="A",
    responsibility="A functionality",
    layer="core",
    files=["a.py"],
    dependencies=[]
)

component_b = Component(
    id="component_b",
    name="B",
    responsibility="B functionality",
    layer="service",
    files=["b.py"],
    dependencies=["component_a"]
)

relationship = Relationship(
    source="component_b",
    target="component_a",
    type="depends_on"
)


snapshot = ArchitectureSnapshot(
    version="1.0",
    commit_hash="test_commit",
    components=[
        component_a,
        component_b
    ],
    relationships=[
        relationship
    ],
    metrics={
        "total_components": 2,
        "total_relationships": 1,
        "total_files": 2
    },
    violations=[]
)


path = save_snapshot(
    snapshot,
    directory="test_snapshots"
)


print()
print("Snapshot saved:")
print(path)

print()
print("Snapshot exists:")
print(
    snapshot_exists(
        "test_commit",
        directory="test_snapshots"
    )
)

print()
print("=" * 60)
print("SNAPSHOT STORE TEST COMPLETED")
print("=" * 60)