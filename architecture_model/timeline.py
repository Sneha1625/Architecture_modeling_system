from typing import List, Dict, Any

from architecture_model.diff import compare_architectures


# ============================================================
# SNAPSHOT METRICS
# ============================================================

def get_snapshot_metrics(snapshot) -> Dict[str, int]:
    """
    Extract basic architecture metrics from a snapshot.
    """

    metrics = getattr(
        snapshot,
        "metrics",
        {}
    ) or {}

    components = getattr(
        snapshot,
        "components",
        []
    ) or []

    relationships = getattr(
        snapshot,
        "relationships",
        []
    ) or []

    # Use snapshot metrics when available.
    total_components = metrics.get(
        "total_components",
        len(components)
    )

    total_relationships = metrics.get(
        "total_relationships",
        len(relationships)
    )

    total_files = metrics.get(
        "total_files",
        sum(
            len(getattr(c, "files", []) or [])
            for c in components
        )
    )

    return {
        "components": total_components,
        "relationships": total_relationships,
        "files": total_files
    }


# ============================================================
# SNAPSHOT TIMELINE ENTRY
# ============================================================

def create_timeline_entry(
    snapshot
) -> Dict[str, Any]:
    """
    Create one timeline entry for an architecture snapshot.
    """

    metrics = get_snapshot_metrics(
        snapshot
    )

    commit_hash = getattr(
        snapshot,
        "commit_hash",
        "unknown"
    )

    timestamp = getattr(
        snapshot,
        "timestamp",
        None
    )

    return {
        "commit_hash": commit_hash,
        "timestamp": timestamp,
        "components": metrics["components"],
        "relationships": metrics["relationships"],
        "files": metrics["files"]
    }


# ============================================================
# ARCHITECTURE TIMELINE
# ============================================================

def build_architecture_timeline(
    snapshots: List[Any]
) -> List[Dict[str, Any]]:
    """
    Build a chronological architecture timeline.

    Each snapshot represents the architecture at one Git commit.
    """

    if not snapshots:
        return []

    timeline = []

    for snapshot in snapshots:

        entry = create_timeline_entry(
            snapshot
        )

        timeline.append(
            entry
        )

    return timeline


# ============================================================
# SORT TIMELINE
# ============================================================

def sort_timeline(
    snapshots: List[Any]
) -> List[Any]:
    """
    Sort snapshots chronologically when timestamps are available.

    If timestamps are unavailable, preserve the original order.
    """

    if not snapshots:
        return []

    def get_timestamp(snapshot):

        timestamp = getattr(
            snapshot,
            "timestamp",
            None
        )

        if timestamp is None:
            return ""

        return str(timestamp)

    try:

        return sorted(
            snapshots,
            key=get_timestamp
        )

    except Exception:

        return snapshots


# ============================================================
# EVOLUTION ANALYSIS
# ============================================================

def analyze_architecture_evolution(
    snapshots: List[Any]
) -> List[Dict[str, Any]]:
    """
    Compare consecutive architecture snapshots.

    Example:

        Snapshot A → Snapshot B

    detects:

        added components
        removed components
        added relationships
        removed relationships
        changed layers
        changed metrics
    """

    if not snapshots:
        return []

    ordered_snapshots = sort_timeline(
        snapshots
    )

    evolution = []

    for index in range(
        1,
        len(ordered_snapshots)
    ):

        previous_snapshot = (
            ordered_snapshots[index - 1]
        )

        current_snapshot = (
            ordered_snapshots[index]
        )

        try:

            diff = compare_architectures(
                previous_snapshot,
                current_snapshot
            )

        except Exception as e:

            diff = {
                "error": str(e)
            }

        previous_commit = getattr(
            previous_snapshot,
            "commit_hash",
            "unknown"
        )

        current_commit = getattr(
            current_snapshot,
            "commit_hash",
            "unknown"
        )

        evolution.append(
            {
                "from_commit": previous_commit,
                "to_commit": current_commit,
                "diff": diff
            }
        )

    return evolution


# ============================================================
# COMPLETE EVOLUTION REPORT
# ============================================================

def build_evolution_report(
    snapshots: List[Any]
) -> Dict[str, Any]:
    """
    Build a complete architecture evolution report.

    Returns:

        timeline
        evolution
        total_snapshots
    """

    ordered_snapshots = sort_timeline(
        snapshots
    )

    timeline = build_architecture_timeline(
        ordered_snapshots
    )

    evolution = analyze_architecture_evolution(
        ordered_snapshots
    )

    return {
        "timeline": timeline,
        "evolution": evolution,
        "total_snapshots": len(
            ordered_snapshots
        )
    }


# ============================================================
# SUMMARY
# ============================================================

def summarize_evolution(
    snapshots: List[Any]
) -> Dict[str, Any]:
    """
    Generate a compact summary of architecture evolution.
    """

    if not snapshots:

        return {
            "total_snapshots": 0,
            "components_added": 0,
            "components_removed": 0,
            "relationships_added": 0,
            "relationships_removed": 0,
            "layers_changed": 0
        }

    evolution = analyze_architecture_evolution(
        snapshots
    )

    components_added = 0
    components_removed = 0
    relationships_added = 0
    relationships_removed = 0
    layers_changed = 0

    for item in evolution:

        diff = item.get(
            "diff",
            {}
        )

        if not isinstance(diff, dict):
            continue

        components_added += len(
            diff.get(
                "added_components",
                []
            )
        )

        components_removed += len(
            diff.get(
                "removed_components",
                []
            )
        )

        relationships_added += len(
            diff.get(
                "added_relationships",
                []
            )
        )

        relationships_removed += len(
            diff.get(
                "removed_relationships",
                []
            )
        )

        layers_changed += len(
            diff.get(
                "changed_layers",
                []
            )
        )

    return {
        "total_snapshots": len(
            snapshots
        ),
        "components_added": components_added,
        "components_removed": components_removed,
        "relationships_added": relationships_added,
        "relationships_removed": relationships_removed,
        "layers_changed": layers_changed
    }