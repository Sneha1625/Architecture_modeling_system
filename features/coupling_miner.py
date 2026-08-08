import os
from collections import Counter
from itertools import combinations

from git import Repo


def mine_logical_coupling(repo_path, min_commits=2):
    """
    Analyze Git history and find files that frequently
    change together.

    Returns a list of file pairs with coupling statistics.
    """

    if not os.path.exists(os.path.join(repo_path, ".git")):
        raise ValueError("The selected folder is not a Git repository.")

    repo = Repo(repo_path)

    pair_counter = Counter()
    file_counter = Counter()

    commits_analyzed = 0

    # Walk through Git history
    for commit in repo.iter_commits():

        changed_files = set()

        try:
            # Initial commit has no parent
            if not commit.parents:
                for item in commit.tree.traverse():
                    if item.type == "blob":
                        changed_files.add(item.path)

            else:
                parent = commit.parents[0]

                diffs = parent.diff(commit)

                for diff in diffs:

                    if diff.a_path:
                        changed_files.add(diff.a_path)

                    if diff.b_path:
                        changed_files.add(diff.b_path)

        except Exception:
            continue

        # Ignore commits that don't contain useful file changes
        if len(changed_files) < 2:
            continue

        commits_analyzed += 1

        # Count how often each file appears
        for file_path in changed_files:
            file_counter[file_path] += 1

        # Count file pairs that change together
        for file_a, file_b in combinations(
            sorted(changed_files),
            2
        ):
            pair_counter[(file_a, file_b)] += 1

    results = []

    for (file_a, file_b), together_count in pair_counter.items():

        file_a_count = file_counter[file_a]
        file_b_count = file_counter[file_b]

        # Ignore very weak relationships
        if together_count < min_commits:
            continue

        # Jaccard-style coupling score
        union_count = (
            file_a_count
            + file_b_count
            - together_count
        )

        if union_count == 0:
            continue

        coupling_score = (
            together_count / union_count
        ) * 100

        results.append({
            "file_a": file_a,
            "file_b": file_b,
            "co_change_count": together_count,
            "file_a_commits": file_a_count,
            "file_b_commits": file_b_count,
            "coupling_score": round(coupling_score, 2)
        })

    # Strongest relationships first
    results.sort(
        key=lambda x: (
            x["coupling_score"],
            x["co_change_count"]
        ),
        reverse=True
    )

    return {
        "commits_analyzed": commits_analyzed,
        "files_analyzed": len(file_counter),
        "couplings": results
    }