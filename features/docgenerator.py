"""
docgenerator.py — AI-Powered Documentation Generator
VTU Major Project Feature: Generates complete project documentation using Groq AI.
"""

import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, "src", ".env"))

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found! Check src/.env file.")

client = Groq(api_key=api_key)
MODEL  = "llama-3.3-70b-versatile"


def generate_module_description(parsed: dict, source_code: str) -> str:
    """Generate a module-level description using Groq AI."""
    file_name = os.path.basename(parsed["file"])
    fn_names  = [f["name"] for f in parsed.get("functions", [])]
    cls_names = [c["name"] for c in parsed.get("classes", [])]

    prompt = f"""Write a professional module description for a Python file in a VTU major project.

File: {file_name}
Functions: {', '.join(fn_names) or 'none'}
Classes: {', '.join(cls_names) or 'none'}

Source (first 1000 chars):
```python
{source_code[:1000]}
```

Write 3-4 sentences describing what this module does, its key responsibilities,
and how it fits in the overall system. Return only the description text, no headings."""

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def build_complexity_report(parsed_results: List[Dict]) -> str:
    """Build a markdown complexity report table for all functions."""
    lines = [
        "## Cyclomatic Complexity Report\n",
        "| File | Function | Complexity | Level | Lines |",
        "|------|----------|------------|-------|-------|"
    ]
    all_fns = []
    for parsed in parsed_results:
        fname = os.path.basename(parsed["file"])
        for fn in parsed.get("functions", []):
            all_fns.append((fname, fn))

    all_fns.sort(key=lambda x: x[1].get("complexity", 1), reverse=True)

    for fname, fn in all_fns:
        cx    = fn.get("complexity", 1)
        label = fn.get("complexity_label", "low")
        icon  = "🔴" if label == "high" else "🟡" if label == "medium" else "🟢"
        start = fn.get("line", 0)
        end   = fn.get("end_line", start)
        lines.append(f"| `{fname}` | `{fn['name']}()` | {cx} | {icon} {label} | {start}–{end} |")

    high   = sum(1 for _, fn in all_fns if fn.get("complexity_label") == "high")
    medium = sum(1 for _, fn in all_fns if fn.get("complexity_label") == "medium")
    low    = sum(1 for _, fn in all_fns if fn.get("complexity_label") == "low")
    avg    = (sum(fn.get("complexity", 1) for _, fn in all_fns) / len(all_fns)) if all_fns else 0

    lines += [
        f"\n**Total functions:** {len(all_fns)}",
        f"**🔴 High complexity:** {high}",
        f"**🟡 Medium:** {medium}",
        f"**🟢 Low:** {low}",
        f"**Average complexity:** {avg:.2f}"
    ]
    return "\n".join(lines)


def generate_readme(parsed_results: List[Dict], project_name: str = "AI Code Analyzer") -> str:
    """Generate a professional README.md for the project."""
    total_fns = sum(len(p.get("functions", [])) for p in parsed_results)
    total_cls = sum(len(p.get("classes",   [])) for p in parsed_results)
    total_imp = sum(len(p.get("imports",   [])) for p in parsed_results)

    return f"""# {project_name}

> AI-Driven Semantic Code Analysis and Automated Software Architecture Modeling System

**VTU Major Project | B.E. Computer Science | 2024–25**

---

## Overview

This project automatically analyzes Python source code using:
- **Python AST module** for structural parsing
- **Groq API (LLaMA 3.3 70B)** for semantic AI analysis
- **NetworkX + Matplotlib** for architecture graph generation
- **SentenceTransformers** for semantic code embeddings

---

## Features

| Feature | Description |
|---------|-------------|
| AST Parsing | Extracts functions, classes, imports, complexity, call graph |
| AI Analysis | Groq LLaMA rates quality, finds issues, suggests improvements |
| Architecture Graph | Hierarchical graph: File → Class → Method → Function → Import |
| Semantic Search | Natural language search across your codebase |
| Test Generation | Auto-generates pytest test cases for every function |
| Code Refactoring | AI rewrites functions with improvements applied |
| Multi-file Analysis | Analyzes multiple files, detects circular dependencies |
| Documentation | Auto-generates README, API docs, complexity report |

---

## Analyzed Files

| File | Functions | Classes | Imports |
|------|-----------|---------|---------|
{chr(10).join(f'| `{os.path.basename(p["file"])}` | {len(p.get("functions",[]))} | {len(p.get("classes",[]))} | {len(p.get("imports",[]))} |' for p in parsed_results)}
| **Total** | **{total_fns}** | **{total_cls}** | **{total_imp}** |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Web UI |
| Parsing | Python `ast` | Syntax tree analysis |
| AI | Groq API — LLaMA 3.3 70B | Semantic analysis |
| Graph | NetworkX + Matplotlib | Architecture visualization |
| Embeddings | SentenceTransformers (MiniLM-L6-v2) | Semantic vectors |
| Env | python-dotenv | Secure API key management |

---

## Algorithms Used

1. **AST Tree Traversal** — O(N) using `ast.walk()`
2. **McCabe's Cyclomatic Complexity** — `1 + decision points`
3. **Call Graph Extraction** — directed adjacency list from `ast.Call` nodes
4. **Cosine Similarity** — `dot(A,B) / (|A| x |B|)` for semantic search
5. **Transformer Embeddings** — 384-dim vectors via MiniLM-L6-v2
6. **Hierarchical Graph Layout** — custom layered positioning
7. **LLM Inference** — structured JSON prompting via Groq LLaMA 3.3 70B

---

## Installation

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > src/.env
streamlit run app.py
```

---

*Generated by AI-Driven Semantic Code Analyzer on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""


def generate_full_documentation(
    parsed_results: List[Dict],
    source_codes: Dict[str, str],
    output_path: str = "outputs/documentation.md"
) -> str:
    """Generate complete project documentation as a single Markdown file."""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "outputs", exist_ok=True)

    sections = []
    sections.append(generate_readme(parsed_results))
    sections.append("\n---\n")
    sections.append(build_complexity_report(parsed_results))

    full_doc = "\n".join(sections)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_doc)

    print(f"Documentation saved: {output_path}")
    return full_doc