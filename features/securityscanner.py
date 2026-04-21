import ast
import re


DANGEROUS_IMPORTS = ["pickle", "subprocess", "eval", "exec", "os.system"]

HARDCODED_SECRET_PATTERNS = [
    r'password\s*=\s*["\'].+["\']',
    r'secret\s*=\s*["\'].+["\']',
    r'api_key\s*=\s*["\'].+["\']',
    r'token\s*=\s*["\'].+["\']',
]

SQL_PATTERNS = [
    r'execute\s*\(\s*["\'].*%s',
    r'execute\s*\(\s*f["\']',
    r'cursor\.execute\s*\(.*\+',
]


def scan_security(source_code: str) -> dict:
    """Scans Python source code for security vulnerabilities"""

    vulnerabilities = []
    lines = source_code.splitlines()
    tree = ast.parse(source_code)

    # 1. Dangerous imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in DANGEROUS_IMPORTS:
                    vulnerabilities.append({
                        "type": "Dangerous Import",
                        "severity": "HIGH",
                        "line": node.lineno,
                        "detail": f"'{alias.name}' can be exploited if misused",
                        "emoji": "☠️"
                    })

        if isinstance(node, ast.Call):
            func = getattr(node.func, 'id', '')
            if func in ['eval', 'exec']:
                vulnerabilities.append({
                    "type": "Code Injection Risk",
                    "severity": "CRITICAL",
                    "line": node.lineno,
                    "detail": f"'{func}()' executes arbitrary code — never use with user input",
                    "emoji": "💣"
                })

    # 2. Hardcoded secrets
    for i, line in enumerate(lines, 1):
        for pattern in HARDCODED_SECRET_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                vulnerabilities.append({
                    "type": "Hardcoded Secret",
                    "severity": "CRITICAL",
                    "line": i,
                    "detail": f"Secret found in code — use .env file instead",
                    "emoji": "🔑"
                })
                break

    # 3. SQL Injection
    for i, line in enumerate(lines, 1):
        for pattern in SQL_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                vulnerabilities.append({
                    "type": "SQL Injection Risk",
                    "severity": "CRITICAL",
                    "line": i,
                    "detail": "String-formatted SQL query — use parameterized queries",
                    "emoji": "💉"
                })
                break

    # 4. Assert used for security
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            vulnerabilities.append({
                "type": "Assert Used for Security",
                "severity": "MEDIUM",
                "line": node.lineno,
                "detail": "assert statements are disabled in optimized mode (-O flag)",
                "emoji": "⚠️"
            })

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    vulnerabilities.sort(key=lambda x: severity_order.get(x["severity"], 99))

    return {
        "vulnerabilities": vulnerabilities,
        "total": len(vulnerabilities),
        "rating": get_security_rating(vulnerabilities)
    }


def get_security_rating(vulns: list) -> str:
    critical = sum(1 for v in vulns if v["severity"] == "CRITICAL")
    high = sum(1 for v in vulns if v["severity"] == "HIGH")

    if critical > 0:
        return "🔴 CRITICAL RISK"
    elif high > 0:
        return "🟠 HIGH RISK"
    elif len(vulns) > 0:
        return "🟡 MEDIUM RISK"
    else:
        return "🟢 SECURE"