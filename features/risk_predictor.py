"""
risk_predictor.py — Defect/Risk Hotspot Predictor
VTU Major Project: AI-Driven Semantic Code Analysis and Automated Software Architecture Modeling System

Based on real empirical software engineering research (Nagappan & Ball, Microsoft
Research): files that are BOTH highly complex AND frequently changed are the
strongest predictors of future bugs — stronger than either signal alone.

Combines:
  1. Cyclomatic complexity (already computed by src/parser.py)
  2. Change frequency / "churn" (from git history)
  3. Historical bugfix-commit frequency (commits whose message contains
     fix/bug/patch/error keywords touching this file)

into a single risk score per file. No LLM call — standard software metrics,
fully local and free.
"""

import re
from collections import defaultdict

try:
    import git
    HAS_GITPYTHON = True
except ImportError:
    HAS_GITPYTHON = False

BUGFIX_KEYWORDS = re.compile(
    r"\b(fix|fixed|fixes|bug|bugfix|patch|error|issue|crash|broken|resolve)\b",
    re.IGNORECASE
)


def compute_git_churn_and_bugfixes(repo_path, max_commits=500):
    """
    Walks git history once and computes, per file:
      - churn: how many commits touched this file
      - bugfix_count: how many of those commits had a bugfix-sounding message
    """
    if not HAS_GITPYTHON:
        return {"error": "GitPython not installed. Run: pip install GitPython"}

    try:
        repo = git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        return {"error": f"{repo_path} is not a git repository."}

    churn = defaultdict(int)
    bugfix_count = defaultdict(int)

    for commit in repo.iter_commits(max_count=max_commits):
        is_bugfix = bool(BUGFIX_KEYWORDS.search(commit.message))
        try:
            files = list(commit.stats.files.keys())
        except Exception:
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            churn[f] += 1
            if is_bugfix:
                bugfix_count[f] += 1

    return {"churn": dict(churn), "bugfix_count": dict(bugfix_count)}


def compute_complexity_per_file(parsed_files):
    """
    Sums cyclomatic complexity across all functions/methods per file, using
    the complexity values src/parser.py already calculates.
    """
    complexity_map = {}
    for parsed in parsed_files:
        total = sum(f.get("complexity", 1) for f in parsed.get("functions", []))
        for cls in parsed.get("classes", []):
            total += sum(m.get("complexity", 1) for m in cls.get("methods", []))
        complexity_map[parsed.get("file", "unknown")] = total
    return complexity_map


def _normalize(value, max_value):
    """Scales a raw count to a 0-1 range for fair weighting across metrics."""
    if max_value == 0:
        return 0.0
    return min(value / max_value, 1.0)


def compute_risk_scores(parsed_files, repo_path=".", max_commits=500,
                         weights=(0.4, 0.3, 0.3)):
    """
    Combines complexity + churn + bugfix history into a single 0-100 risk
    score per file. Weights: (complexity_weight, churn_weight, bugfix_weight).

    Returns a list of dicts sorted highest-risk first:
    {file, complexity, churn, bugfix_count, risk_score, risk_label}
    """
    complexity_map = compute_complexity_per_file(parsed_files)
    git_data = compute_git_churn_and_bugfixes(repo_path, max_commits)

    if "error" in git_data:
        # Degrade gracefully — still rank by complexity alone if no git repo
        results = []
        max_complexity = max(complexity_map.values(), default=1)
        for file, comp in complexity_map.items():
            score = round(_normalize(comp, max_complexity) * 100, 1)
            results.append({
                "file": file, "complexity": comp, "churn": None, "bugfix_count": None,
                "risk_score": score,
                "risk_label": _risk_label(score),
                "note": git_data["error"]
            })
        results.sort(key=lambda x: x["risk_score"], reverse=True)
        return results

    churn = git_data["churn"]
    bugfix = git_data["bugfix_count"]

    max_complexity = max(complexity_map.values(), default=1)
    max_churn = max(churn.values(), default=1)
    max_bugfix = max(bugfix.values(), default=1)

    w_complexity, w_churn, w_bugfix = weights
    results = []

    all_files = set(complexity_map.keys())
    for f in churn.keys():
        all_files.add(f)

    for file in all_files:
        comp = complexity_map.get(file, 0)
        base = file.split("/")[-1]
        matched_churn = churn.get(file) or next(
            (v for k, v in churn.items() if k.endswith(base)), 0
        )
        matched_bugfix = bugfix.get(file) or next(
            (v for k, v in bugfix.items() if k.endswith(base)), 0
        )

        score = (
            w_complexity * _normalize(comp, max_complexity) +
            w_churn * _normalize(matched_churn, max_churn) +
            w_bugfix * _normalize(matched_bugfix, max_bugfix)
        ) * 100

        results.append({
            "file": file,
            "complexity": comp,
            "churn": matched_churn,
            "bugfix_count": matched_bugfix,
            "risk_score": round(score, 1),
            "risk_label": _risk_label(score)
        })

    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results


def _risk_label(score):
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"