import ast
import os


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_file(file_path):
    source_code = read_file(file_path)
    tree = ast.parse(source_code)

    result = {
        "file": file_path,
        "functions": [],
        "classes": [],
        "imports": []
    }

    for node in ast.walk(tree):

        # Extract functions
        if isinstance(node, ast.FunctionDef):
            result["functions"].append({
                "name": node.name,
                "line": node.lineno,
                "args": [arg.arg for arg in node.args.args]
            })

        # Extract classes
        elif isinstance(node, ast.ClassDef):
            result["classes"].append({
                "name": node.name,
                "line": node.lineno
            })

        # Extract imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            result["imports"].append(node.module)

    return result


def parse_folder(folder_path):
    all_results = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                parsed = parse_file(full_path)
                all_results.append(parsed)

    return all_results

if __name__ == "__main__":
    import json

    sample_code = """
import os
import sys
from pathlib import Path

class MyApp:
    def __init__(self):
        self.name = "test"

    def run(self):
        pass

def helper_function(x, y):
    return x + y
"""

    # Save sample file
    os.makedirs("../samples", exist_ok=True)
    with open("../samples/sample.py", "w") as f:
        f.write(sample_code)

    # Parse it
    result = parse_file("../samples/sample.py")

    # Print nicely
    print(json.dumps(result, indent=2))
