"""
analyzer.py — AI-Powered Semantic Code Analyzer
VTU Major Project: AI-Driven Semantic Code Analysis and Automated Software Architecture Modeling System
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found! Check src/.env file.")

client = Groq(api_key=api_key)
MODEL  = "llama-3.3-70b-versatile"


def _call(prompt: str, max_tokens: int = 600) -> str:
    """Helper to call Groq API and return text."""
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def _parse_json(raw: str, fallback: dict) -> dict:
    """Clean and parse JSON from LLM response."""
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        fallback["responsibility"] = raw[:200]
        return fallback


def analyze_function(func: dict, source_code: str, file_path: str) -> dict:
    """Analyze a single function using Groq AI."""
    args_str = ", ".join(
        f"{a['name']}: {a['type']}" if a.get("type") else a["name"]
        for a in func.get("args", [])
    )
    return_type      = func.get("return_type", "")
    docstring        = func.get("docstring", "No docstring provided")
    complexity       = func.get("complexity", 1)
    complexity_label = func.get("complexity_label", "low")
    calls            = func.get("calls", [])
    is_async         = func.get("is_async", False)
    decorators       = func.get("decorators", [])

    prompt = f"""You are an expert Python code reviewer for a VTU major project on AI-driven code analysis.

File: {file_path}
Function: {'async ' if is_async else ''}def {func['name']}({args_str}){' -> ' + return_type if return_type else ''}
Line: {func['line']}
Cyclomatic Complexity: {complexity} ({complexity_label})
Calls: {', '.join(calls) if calls else 'none'}
Decorators: {', '.join(decorators) if decorators else 'none'}
Docstring: {docstring}

Source code:
```python
{source_code[:3000]}
```

Analyze ONLY the function '{func['name']}' and return a JSON object with this exact structure:
{{
  "responsibility": "one clear sentence describing what this function does",
  "issues": ["issue 1", "issue 2"],
  "suggestions": ["suggestion 1", "suggestion 2"],
  "tags": ["pure or side-effect or io or utility or entry-point or recursive or async"],
  "quality_score": 85,
  "missing_docstring": true,
  "missing_type_hints": false,
  "error_handling": "none or partial or good"
}}

Return ONLY valid JSON. No explanation. No markdown fences."""

    raw = _call(prompt, 600)
    return _parse_json(raw, {
        "responsibility": "",
        "issues": [],
        "suggestions": [],
        "tags": [],
        "quality_score": 50,
        "missing_docstring": not func.get("docstring"),
        "missing_type_hints": False,
        "error_handling": "none"
    })


def analyze_class(cls: dict, source_code: str, file_path: str) -> dict:
    """Analyze a class using Groq AI."""
    bases     = cls.get("bases", [])
    methods   = [m["name"] for m in cls.get("methods", [])]
    docstring = cls.get("docstring", "No docstring provided")

    prompt = f"""You are an expert Python code reviewer for a VTU major project.

File: {file_path}
Class: {cls['name']}({', '.join(bases) if bases else 'object'})
Line: {cls['line']}
Methods: {', '.join(methods) if methods else 'none'}
Docstring: {docstring}

Analyze the class '{cls['name']}' from this source:
```python
{source_code[:3000]}
```

Return ONLY this JSON:
{{
  "responsibility": "one sentence describing what this class represents",
  "design_pattern": "detected pattern or none",
  "issues": ["issue 1"],
  "suggestions": ["suggestion 1"],
  "quality_score": 80,
  "srp_compliant": true
}}

Return ONLY valid JSON. No explanation. No markdown fences."""

    raw = _call(prompt, 400)
    return _parse_json(raw, {
        "responsibility": "",
        "design_pattern": "none",
        "issues": [],
        "suggestions": [],
        "quality_score": 50,
        "srp_compliant": True
    })


def analyze_architecture(parsed: dict, source_code: str) -> dict:
    """High-level architecture analysis of the entire file."""
    fn_names   = [f["name"] for f in parsed.get("functions", [])]
    cls_names  = [c["name"] for c in parsed.get("classes", [])]
    imports    = parsed.get("imports", [])
    call_graph = parsed.get("call_graph", {})

    prompt = f"""You are a software architect reviewing a Python file for a VTU major project.

File: {parsed['file']}
Functions: {', '.join(fn_names) if fn_names else 'none'}
Classes: {', '.join(cls_names) if cls_names else 'none'}
Imports: {', '.join(imports) if imports else 'none'}
Call graph: {json.dumps(call_graph)}

Source:
```python
{source_code[:2000]}
```

Return ONLY this JSON:
{{
  "summary": "2-3 sentence overview of the module",
  "architecture_pattern": "MVC or Pipeline or Event-driven or Functional or OOP or Script or Utility",
  "layers": ["layer1", "layer2"],
  "coupling": "low or medium or high",
  "cohesion": "low or medium or high",
  "overall_quality": 80,
  "recommendations": [
    {{"priority": "high or medium or low", "title": "short title", "detail": "explanation"}}
  ]
}}

Return ONLY valid JSON. No explanation. No markdown fences."""

    raw = _call(prompt, 600)
    return _parse_json(raw, {
        "summary": "",
        "architecture_pattern": "Script",
        "layers": [],
        "coupling": "medium",
        "cohesion": "medium",
        "overall_quality": 60,
        "recommendations": []
    })


def analyze_parsed_result(parsed: dict, source_code: str) -> dict:
    """Main entry point. Analyzes all functions, classes, and overall architecture."""
    result = {
        "file":         parsed["file"],
        "functions":    [],
        "classes":      [],
        "architecture": {}
    }

    for func in parsed.get("functions", []):
        analysis = analyze_function(func, source_code, parsed["file"])
        result["functions"].append({
            "name":             func["name"],
            "line":             func["line"],
            "complexity":       func.get("complexity", 1),
            "complexity_label": func.get("complexity_label", "low"),
            "args":             func.get("args", []),
            "return_type":      func.get("return_type", ""),
            "docstring":        func.get("docstring", ""),
            "analysis":         analysis
        })

    for cls in parsed.get("classes", []):
        analysis = analyze_class(cls, source_code, parsed["file"])
        result["classes"].append({
            "name":     cls["name"],
            "line":     cls["line"],
            "methods":  cls.get("methods", []),
            "bases":    cls.get("bases", []),
            "analysis": analysis
        })

    result["architecture"] = analyze_architecture(parsed, source_code)
    return result