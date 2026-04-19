"""
NlCodesearch.py — Natural Language Code Search Engine
VTU Major Project Feature: Search your codebase using plain English.
Uses SentenceTransformers (no API needed) for semantic vector search.
"""

import os
import json
import math
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


class CodeSearchEngine:
    """
    Semantic code search engine using SentenceTransformer embeddings.
    Indexes all functions and classes from parsed AST results.
    """

    def __init__(self):
        self.index: List[Dict] = []
        self.is_built = False

    def _make_description(self, item: Dict, item_type: str) -> str:
        """Build a rich semantic description for embedding."""
        if item_type == "function":
            args = ", ".join(
                f"{a['name']}: {a['type']}" if a.get("type") else a["name"]
                for a in item.get("args", [])
            )
            ret      = item.get("return_type", "")
            doc      = item.get("docstring", "")
            calls    = ", ".join(item.get("calls", []))
            cx       = item.get("complexity_label", "low")
            is_async = "async " if item.get("is_async") else ""
            return (
                f"{is_async}Python function named {item['name']} "
                f"that takes parameters ({args or 'none'}) "
                f"and returns {ret or 'nothing'}. "
                f"Complexity is {cx}. "
                f"Calls: {calls or 'no internal calls'}. "
                f"{doc}"
            ).strip()

        elif item_type == "class":
            methods = ", ".join(m["name"] for m in item.get("methods", []))
            bases   = ", ".join(item.get("bases", []))
            doc     = item.get("docstring", "")
            return (
                f"Python class named {item['name']} "
                f"that inherits from ({bases or 'object'}) "
                f"and has methods: {methods or 'none'}. "
                f"{doc}"
            ).strip()

        return f"{item_type} {item.get('name', '')}"

    def build_index(self, parsed_results: List[Dict]) -> int:
        """Build the search index from a list of parsed file results."""
        self.index = []
        for parsed in parsed_results:
            file_name = os.path.basename(parsed["file"])

            for fn in parsed.get("functions", []):
                desc = self._make_description(fn, "function")
                self.index.append({
                    "type":        "function",
                    "name":        fn["name"],
                    "file":        file_name,
                    "line":        fn["line"],
                    "complexity":  fn.get("complexity", 1),
                    "cx_label":    fn.get("complexity_label", "low"),
                    "return_type": fn.get("return_type", ""),
                    "is_async":    fn.get("is_async", False),
                    "docstring":   fn.get("docstring", ""),
                    "description": desc,
                    "embedding":   model.encode(desc).tolist()
                })

            for cls in parsed.get("classes", []):
                desc = self._make_description(cls, "class")
                self.index.append({
                    "type":        "class",
                    "name":        cls["name"],
                    "file":        file_name,
                    "line":        cls["line"],
                    "methods":     [m["name"] for m in cls.get("methods", [])],
                    "docstring":   cls.get("docstring", ""),
                    "description": desc,
                    "embedding":   model.encode(desc).tolist()
                })

        self.is_built = True
        return len(self.index)

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot   = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x ** 2 for x in a))
        mag_b = math.sqrt(sum(x ** 2 for x in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_type: Optional[str] = None,
        filter_complexity: Optional[str] = None,
        min_similarity: float = 0.1
    ) -> List[Dict]:
        """Search the index using a natural language query."""
        if not self.is_built or not self.index:
            return []

        query_vec = model.encode(query).tolist()
        results   = []

        for item in self.index:
            if filter_type and item["type"] != filter_type:
                continue
            if filter_complexity and item.get("cx_label") != filter_complexity:
                continue
            sim = self._cosine_similarity(query_vec, item["embedding"])
            if sim >= min_similarity:
                results.append({**item, "similarity": round(sim, 4)})

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def get_complexity_hotspots(self, top_k: int = 5) -> List[Dict]:
        """Return the most complex functions in the codebase."""
        fns = [item for item in self.index if item["type"] == "function"]
        return sorted(fns, key=lambda x: x["complexity"], reverse=True)[:top_k]

    def get_undocumented(self) -> List[Dict]:
        """Return all functions and classes missing docstrings."""
        return [item for item in self.index if not item.get("docstring")]

    def get_stats(self) -> Dict:
        """Return index statistics."""
        fns = [i for i in self.index if i["type"] == "function"]
        cls = [i for i in self.index if i["type"] == "class"]
        return {
            "total_indexed":    len(self.index),
            "functions":        len(fns),
            "classes":          len(cls),
            "async_fns":        sum(1 for f in fns if f.get("is_async")),
            "undocumented":     len(self.get_undocumented()),
            "high_complexity":  sum(1 for f in fns if f.get("cx_label") == "high")
        }