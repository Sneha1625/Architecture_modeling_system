import os
from typing import List, Dict, Any

from git import Repo

from src.parser import parse_folder
from architecture_model.recovery import recover_architecture
from architecture_model.model import ArchitectureSnapshot


def get_commit_history(repo_path: str, max_commits: int = 30):
    """
    Return recent Git commits from the repository.
    """

    repo = Repo(repo_path)

    commits = []

    for commit in repo.iter_commits("HEAD", max_count=max_commits):
        commits.append({
            "hash": commit.hexsha,
            "short_hash": commit.hexsha[:7],
            "message": commit.message.strip(),
            "author": str(commit.author),
            "date": commit.committed_datetime.isoformat()
        })

    return commits


def checkout_commit(repo_path: str, commit_hash: str):
    """
    Checkout a specific Git commit.

    Returns the commit hash that was active before checkout.
    """

    repo = Repo(repo_path)

    current_commit = repo.head.commit.hexsha

    repo.git.checkout(
        commit_hash,
        force=True
    )

    return current_commit


def restore_commit(repo_path: str, commit_hash: str):
    """
    Restore the repository to a specific commit.
    """

    repo = Repo(repo_path)

    repo.git.checkout(
        commit_hash,
        force=True
    )


def recover_commit_architecture(
    repo_path: str,
    commit_hash: str
) -> ArchitectureSnapshot:
    """
    Checkout a Git commit, parse its Python files,
    and recover its architecture.
    """

    repo = Repo(repo_path)

    original_commit = repo.head.commit.hexsha

    try:

        # Checkout requested commit
        repo.git.checkout(
            commit_hash,
            force=True
        )

        # Parse the repository at this commit
        parsed_results = parse_folder(repo_path)

        # Recover architecture
        snapshot = recover_architecture(
            parsed_results,
            commit_hash=commit_hash
        )

        return snapshot

    finally:

        # Always restore original commit
        repo.git.checkout(
            original_commit,
            force=True
        )


def compare_architectures(
    snapshot_a: ArchitectureSnapshot,
    snapshot_b: ArchitectureSnapshot
):
    """
    Compare two architecture snapshots.

    Detects:
    - Added components
    - Removed components
    - Added relationships
    - Removed relationships
    - Component count change
    - Relationship count change
    - File count change
    """

    components_a = {
        component.name
        for component in snapshot_a.components
    }

    components_b = {
        component.name
        for component in snapshot_b.components
    }

    added_components = sorted(
        components_b - components_a
    )

    removed_components = sorted(
        components_a - components_b
    )

    relationships_a = {
        (
            relationship.source,
            relationship.target,
            relationship.type
        )
        for relationship in snapshot_a.relationships
    }

    relationships_b = {
        (
            relationship.source,
            relationship.target,
            relationship.type
        )
        for relationship in snapshot_b.relationships
    }

    added_relationships = sorted(
        relationships_b - relationships_a
    )

    removed_relationships = sorted(
        relationships_a - relationships_b
    )

    return {
        "added_components": added_components,

        "removed_components": removed_components,

        "added_relationships": added_relationships,

        "removed_relationships": removed_relationships,

        "component_count_change": (
            len(snapshot_b.components)
            - len(snapshot_a.components)
        ),

        "relationship_count_change": (
            len(snapshot_b.relationships)
            - len(snapshot_a.relationships)
        ),

        "file_count_change": (
            snapshot_b.metrics.get("total_files", 0)
            - snapshot_a.metrics.get("total_files", 0)
        )
    }


def save_snapshot(
    snapshot: ArchitectureSnapshot,
    output_directory: str = "architecture_snapshots"
):
    """
    Save an architecture snapshot as JSON.
    """

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    filename = (
        f"{snapshot.commit_hash[:7]}"
        f"_architecture.json"
    )

    output_path = os.path.join(
        output_directory,
        filename
    )

    snapshot.save_json(
        output_path
    )

    return output_path