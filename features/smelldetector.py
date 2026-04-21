import ast


def detect_smells(source_code: str) -> dict:
    """Detects code smells in Python source code"""

    smells = []
    tree = ast.parse(source_code)
    lines = source_code.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):

            # Long function
            length = node.end_lineno - node.lineno
            if length > 30:
                smells.append({
                    "smell": "Long Function",
                    "severity": "HIGH",
                    "location": f"Function '{node.name}' at line {node.lineno}",
                    "detail": f"{length} lines — split into smaller functions",
                    "emoji": "📏"
                })

            # Too many parameters
            params = len(node.args.args)
            if params > 5:
                smells.append({
                    "smell": "Too Many Parameters",
                    "severity": "MEDIUM",
                    "location": f"Function '{node.name}' at line {node.lineno}",
                    "detail": f"{params} parameters — use a config object instead",
                    "emoji": "⚙️"
                })

            # Single letter variable names inside function
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and len(child.id) == 1 and child.id != '_':
                    smells.append({
                        "smell": "Bad Variable Name",
                        "severity": "LOW",
                        "location": f"Variable '{child.id}' in function '{node.name}'",
                        "detail": "Single letter names are hard to understand",
                        "emoji": "🔤"
                    })
                    break  # one per function is enough

        # Dead code: functions that are defined but never called
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            call_count = sum(
                1 for n in ast.walk(tree)
                if isinstance(n, ast.Call) and
                isinstance(getattr(n, 'func', None), ast.Name) and
                n.func.id == func_name
            )
            if call_count == 0 and not func_name.startswith("_"):
                smells.append({
                    "smell": "Dead Code",
                    "severity": "MEDIUM",
                    "location": f"Function '{func_name}' at line {node.lineno}",
                    "detail": "Function is never called anywhere",
                    "emoji": "💀"
                })

    # Duplicate lines check
    stripped = [l.strip() for l in lines if l.strip()]
    seen = set()
    for line in stripped:
        if line in seen and len(line) > 10:
            smells.append({
                "smell": "Duplicate Code",
                "severity": "HIGH",
                "location": f"Line: '{line[:50]}...'",
                "detail": "Same code repeated — extract into a function",
                "emoji": "👯"
            })
            break
        seen.add(line)

    # Score: 100 - penalty per smell
    penalty = {"HIGH": 20, "MEDIUM": 10, "LOW": 5}
    score = max(0, 100 - sum(penalty[s["severity"]] for s in smells))

    return {
        "smells": smells,
        "total_smells": len(smells),
        "smell_score": score,
        "rating": get_smell_rating(score)
    }


def get_smell_rating(score: int) -> str:
    if score >= 90:
        return "🟢 EXCELLENT"
    elif score >= 70:
        return "🟡 GOOD"
    elif score >= 50:
        return "🟠 NEEDS WORK"
    else:
        return "🔴 POOR"