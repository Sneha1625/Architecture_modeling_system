from architecture_model.model import (
    Component,
    Relationship,
    ArchitectureSnapshot
)

from architecture_model.timeline import (
    build_architecture_timeline,
    analyze_architecture_evolution,
    build_evolution_report,
    summarize_evolution
)


print("=" * 60)
print("ARCHITECTURE EVOLUTION TIMELINE TEST")
print("=" * 60)


# ============================================================
# SNAPSHOT 1
# ============================================================

component_a_old = Component(
    id="component_a",
    name="A",
    responsibility="A functionality",
    layer="core",
    files=["a.py"],
    dependencies=[]
)

component_b_old = Component(
    id="component_b",
    name="B",
    responsibility="B functionality",
    layer="service",
    files=["b.py"],
    dependencies=["component_a"]
)

relationship_old = Relationship(
    source="component_b",
    target="component_a",
    type="depends_on"
)

snapshot_old = ArchitectureSnapshot(
    version="1.0",
    commit_hash="commit_old",
    components=[
        component_a_old,
        component_b_old
    ],
    relationships=[
        relationship_old
    ],
    metrics={
        "total_components": 2,
        "total_relationships": 1,
        "total_files": 2
    },
    violations=[]
)


# ============================================================
# SNAPSHOT 2
# ============================================================

component_a_new = Component(
    id="component_a",
    name="A",
    responsibility="A functionality",
    layer="service",
    files=["a.py"],
    dependencies=[
        "component_c"
    ]
)

component_b_new = Component(
    id="component_b",
    name="B",
    responsibility="B functionality",
    layer="service",
    files=["b.py"],
    dependencies=[
        "component_a"
    ]
)

component_c_new = Component(
    id="component_c",
    name="C",
    responsibility="C functionality",
    layer="data",
    files=["c.py"],
    dependencies=[]
)

relationship_ba = Relationship(
    source="component_b",
    target="component_a",
    type="depends_on"
)

relationship_ac = Relationship(
    source="component_a",
    target="component_c",
    type="depends_on"
)

snapshot_new = ArchitectureSnapshot(
    version="1.0",
    commit_hash="commit_new",
    components=[
        component_a_new,
        component_b_new,
        component_c_new
    ],
    relationships=[
        relationship_ba,
        relationship_ac
    ],
    metrics={
        "total_components": 3,
        "total_relationships": 2,
        "total_files": 3
    },
    violations=[]
)


# ============================================================
# TIMELINE
# ============================================================

snapshots = [
    snapshot_old,
    snapshot_new
]


timeline = build_architecture_timeline(
    snapshots
)


print()
print("TIMELINE")
print("-" * 60)

for entry in timeline:

    print(
        f"Commit: {entry['commit_hash']}"
    )

    print(
        f"Components: {entry['components']}"
    )

    print(
        f"Relationships: {entry['relationships']}"
    )

    print(
        f"Files: {entry['files']}"
    )

    print("-" * 60)


# ============================================================
# EVOLUTION
# ============================================================

evolution = analyze_architecture_evolution(
    snapshots
)


print()
print("ARCHITECTURE EVOLUTION")
print("-" * 60)

for item in evolution:

    print(
        f"From: {item['from_commit']}"
    )

    print(
        f"To: {item['to_commit']}"
    )

    print(
        f"Diff: {item['diff']}"
    )

    print("-" * 60)


# ============================================================
# COMPLETE REPORT
# ============================================================

report = build_evolution_report(
    snapshots
)


print()
print("EVOLUTION REPORT")
print("-" * 60)

print(
    "Total snapshots:",
    report["total_snapshots"]
)

print(
    "Timeline:",
    report["timeline"]
)

print(
    "Evolution:",
    report["evolution"]
)


# ============================================================
# SUMMARY
# ============================================================

summary = summarize_evolution(
    snapshots
)


print()
print("SUMMARY")
print("-" * 60)

print(
    summary
)

print()
print("=" * 60)
print("ARCHITECTURE TIMELINE TEST COMPLETED")
print("=" * 60)