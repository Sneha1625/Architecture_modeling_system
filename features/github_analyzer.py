import os
import shutil
import tempfile
from git import Repo


def clone_github_repository(github_url):
    """
    Clone a public GitHub repository into a temporary directory.
    """

    if not github_url:
        raise ValueError("GitHub URL cannot be empty.")

    if not github_url.startswith(
        ("https://github.com/", "http://github.com/")
    ):
        raise ValueError("Please enter a valid GitHub repository URL.")

    # Remove trailing slash
    github_url = github_url.rstrip("/")

    # Remove .git if present
    repo_name = github_url.split("/")[-1]

    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    temp_dir = tempfile.mkdtemp(
        prefix="github_analyzer_"
    )

    repo_path = os.path.join(
        temp_dir,
        repo_name
    )

    try:
        Repo.clone_from(
            github_url,
            repo_path
        )

        return repo_path

    except Exception as e:
        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        raise RuntimeError(
            f"Could not clone repository: {e}"
        )


def find_python_files(repo_path):
    """
    Find all Python files in the cloned repository.
    """

    python_files = []

    ignored_directories = {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".env",
        "dist",
        "build"
    }

    for root, dirs, files in os.walk(repo_path):

        # Prevent scanning unnecessary directories
        dirs[:] = [
            d for d in dirs
            if d not in ignored_directories
        ]

        for filename in files:

            if filename.endswith(".py"):

                full_path = os.path.join(
                    root,
                    filename
                )

                python_files.append(
                    full_path
                )

    return python_files


def get_repository_info(repo_path):
    """
    Get basic information about the cloned repository.
    """

    python_files = find_python_files(
        repo_path
    )

    total_lines = 0

    for file_path in python_files:

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                total_lines += len(
                    f.readlines()
                )

        except Exception:
            continue

    return {
        "python_files": len(python_files),
        "total_lines": total_lines,
        "repository_path": repo_path
    }