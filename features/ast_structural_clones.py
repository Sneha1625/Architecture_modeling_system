"""
ast_structural_clones.py — Structural (Type-1/Type-2) Code Clone Detector
VTU Major Project: AI-Driven Semantic Code Analysis and Automated Software Architecture Modeling System

Code clone research defines four types:
  Type-1: identical code, differing only in whitespace/comments
  Type-2: identical structure, differing in variable/function names and literals
  Type-3: near-miss clones with small structural edits
  Type-4: semantically equivalent code with completely different structure/wording

features/clone_detector.py (embeddings + cosine similarity) catches Type-3/4 —
code that MEANS the same thing but reads differently.

This module catches Type-1/2 — code that IS structurally the same, which is
actually a case embeddings can miss, since two structurally-identical
functions with different names/formatting don't always score as neatly
similar on meaning alone.

Together, both modules give full Type-1 through Type-4 clone coverage,
which no single existing tool (including generic AI code assistants) does
in one pass, since it requires walking the real AST, not just reading text.
"""

import ast
import hashlib
from collections import defaultdict


class _Normalizer(ast.NodeTransformer):
    """
    Strips out everything that makes Type-2 clones LOOK different on paper
    (variable names, function names, literal values) while preserving the
    actual structural shape of the code — the sequence and nesting of
    operations. Two functions that do the same thing with different names
    end up with identical normalized structure.
    """

    def visit_Name(self, node):
        node.id = "VAR"
        return node

    def visit_arg(self, node):
        node.arg = "ARG"
        return node

    def visit_FunctionDef(self, node):
        node.name = "FUNC"
        self.generic_visit(node)
        return node

    def visit_Constant(self, node):
        # Normalize all literal values (numbers, strings) to a placeholder —
        # keeps the STRUCTURE (a comparison exists) without caring about the
        # exact value being compared.
        node.value = "LITERAL"
        return node


def _structural_fingerprint(func_node):
    """
    Produces a hash representing a function's normalized AST shape.
    Two functions with the same fingerprint are Type-1/Type-2 clones —
    structurally identical regardless of naming.
    """
    normalized = _Normalizer().visit(ast.parse(ast.unparse(func_node)))
    dump = ast.dump(normalized, annotate_fields=False)
    return hashlib.sha256(dump.encode()).hexdigest()


def find_structural_clones(parsed_files, source_lookup):
    """
    parsed_files: list of parse_file() outputs (for names/line numbers)
    source_lookup: dict mapping file path -> raw source code string,
                   needed to re-parse real ast.FunctionDef nodes
                   (parse_file() only returns a summary, not the tree itself)

    Returns clone groups: functions sharing an identical structural
    fingerprint, grouped together — each group is a Type-1/2 clone family.
    """
    fingerprints = defaultdict(list)

    for parsed in parsed_files:
        file = parsed.get("file", "unknown")
        source = source_lookup.get(file, "")
        if not source:
            continue

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    fp = _structural_fingerprint(node)
                except Exception:
                    continue
                fingerprints[fp].append({
                    "name": node.name,
                    "file": file,
                    "line": node.lineno
                })

    # Only fingerprints shared by 2+ functions are actual clone groups
    clone_groups = [
        members for members in fingerprints.values()
        if len(members) >= 2
    ]

    clone_groups.sort(key=len, reverse=True)

    return {
        "total_clone_groups": len(clone_groups),
        "clone_groups": clone_groups
    }


if __name__ == "__main__":
    # Demo: two functions with different names/variable names but
    # IDENTICAL structure — the kind of clone embeddings can be inconsistent
    # on, but AST fingerprinting catches with certainty.
    source_a = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item
    return total
"""
    source_b = """
def sum_values(numbers):
    result = 0
    for num in numbers:
        result = result + num
    return result
"""
    source_c = """
def unrelated_function(x):
    return x * 2 + 1
"""

    parsed_files = [
        {"file": "a.py"}, {"file": "b.py"}, {"file": "c.py"}
    ]
    source_lookup = {"a.py": source_a, "b.py": source_b, "c.py": source_c}

    result = find_structural_clones(parsed_files, source_lookup)
    print(f"Structural clone groups found: {result['total_clone_groups']}")
    for group in result["clone_groups"]:
        names = ", ".join(f"{m['name']} ({m['file']})" for m in group)
        print(f"  Clone group: {names}")