import os
import json
import subprocess

from src.parser import parse_folder
from architecture_model.recovery import recover_architecture


# --------------------------------------------------
# Get current Git commit
# --------------------------------------------------

def get_git_commit_hash():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True
        ).strip()

    except Exception:
        return "unknown"


# --------------------------------------------------
# 1. Parse the project
# --------------------------------------------------

project_path = os.getcwd()

print("Parsing project:")
print(project_path)

parsed_results = parse_folder(project_path)

print()
print(f"Files parsed: {len(parsed_results)}")


# --------------------------------------------------
# 2. Get Git commit
# --------------------------------------------------

commit_hash = get_git_commit_hash()

print()
print(f"Git commit: {commit_hash}")


# --------------------------------------------------
# 3. Recover architecture
# --------------------------------------------------

snapshot = recover_architecture(
    parsed_results,
    commit_hash=commit_hash
)


# --------------------------------------------------
# 4. Display recovered architecture
# --------------------------------------------------

print()
print("Architecture recovered successfully!")
print()

print("Components:")

for component in snapshot.components:

    print(
        f"- {component.name} "
        f"| Layer: {component.layer} "
        f"| Files: {len(component.files)}"
    )


print()
print("Relationships:")

for relationship in snapshot.relationships:

    print(
        f"- {relationship.source} "
        f"--[{relationship.type}]--> "
        f"{relationship.target}"
    )


print()
print("Metrics:")

print(
    json.dumps(
        snapshot.metrics,
        indent=4
    )
)


# --------------------------------------------------
# 5. Save persistent architecture snapshot
# --------------------------------------------------

output_directory = "architecture_snapshots"

os.makedirs(
    output_directory,
    exist_ok=True
)

output_file = os.path.join(
    output_directory,
    f"{commit_hash}.json"
)


snapshot.save_json(output_file)


print()
print("Architecture snapshot saved:")
print(output_file)