import json
import os
from typing import List, Optional

from architecture_model.model import ArchitectureSnapshot


# ============================================================
# SNAPSHOT SERIALIZATION
# ============================================================

def snapshot_to_dict(
    snapshot: ArchitectureSnapshot
) -> dict:
    """
    Convert an ArchitectureSnapshot into a dictionary.
    """

    if hasattr(snapshot, "__dict__"):
        data = dict(snapshot.__dict__)
    else:
        data = {}

    # Convert components
    components = []

    for component in getattr(
        snapshot,
        "components",
        []
    ):

        if hasattr(component, "__dict__"):
            components.append(
                dict(component.__dict__)
            )
        else:
            components.append(component)

    data["components"] = components

    # Convert relationships
    relationships = []

    for relationship in getattr(
        snapshot,
        "relationships",
        []
    ):

        if hasattr(relationship, "__dict__"):
            relationships.append(
                dict(relationship.__dict__)
            )
        else:
            relationships.append(relationship)

    data["relationships"] = relationships

    return data


# ============================================================
# SAVE SNAPSHOT
# ============================================================

def save_snapshot(
    snapshot: ArchitectureSnapshot,
    directory: str = "architecture_snapshots"
) -> str:
    """
    Save an architecture snapshot as JSON.
    """

    os.makedirs(
        directory,
        exist_ok=True
    )

    commit_hash = getattr(
        snapshot,
        "commit_hash",
        "unknown"
    )

    filename = f"{commit_hash}.json"

    path = os.path.join(
        directory,
        filename
    )

    data = snapshot_to_dict(
        snapshot
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            default=str
        )

    return path


# ============================================================
# LIST SNAPSHOTS
# ============================================================

def list_snapshot_files(
    directory: str = "architecture_snapshots"
) -> List[str]:
    """
    Return all stored snapshot files.
    """

    if not os.path.exists(directory):
        return []

    files = []

    for filename in os.listdir(directory):

        if filename.endswith(".json"):

            files.append(
                os.path.join(
                    directory,
                    filename
                )
            )

    return sorted(files)


# ============================================================
# CHECK SNAPSHOT
# ============================================================

def snapshot_exists(
    commit_hash: str,
    directory: str = "architecture_snapshots"
) -> bool:
    """
    Check whether a snapshot already exists.
    """

    path = os.path.join(
        directory,
        f"{commit_hash}.json"
    )

    return os.path.exists(path)