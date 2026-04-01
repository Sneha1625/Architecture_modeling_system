"""
app.py — Streamlit Frontend
"""

import streamlit as st
import sys
import os
import tempfile
import networkx as nx

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from parser import parse_file, read_file, get_summary
from analyzer import analyze_parsed_result
from architect import build_graph, draw_graph
from embedder import embed_parsed_result, find_similar, build_similarity_matrix

# ─── Page config ─────────────────────────────────────────
st.set_page_config(page_title="AI Code Analyzer", page_icon="🧠", layout="wide")

st.title("🧠 AI Code Analyzer")
st.divider()

# ─── Upload ──────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload Python file", type=["py"])

if not uploaded_file:
    st.stop()

with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as tmp:
    tmp.write(uploaded_file.getvalue().decode("utf-8"))
    temp_path = tmp.name

source_code = read_file(temp_path)
parsed = parse_file(temp_path)
summary = get_summary(parsed)

if "error" in parsed:
    st.error(parsed["error"])
    st.stop()

# ─── Overview ────────────────────────────────────────────
st.subheader("📊 Overview")
c1, c2, c3 = st.columns(3)
c1.metric("Functions", summary.get("total_functions", 0))
c2.metric("Classes", summary.get("total_classes", 0))
c3.metric("Complexity", summary.get("avg_complexity", 0))

st.divider()

# ─── Tabs ────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Code",
    "🌳 AST",
    "🤖 AI",
    "🏗️ Graph"
])

# ═══════════════════════════════
# TAB 1
# ═══════════════════════════════
with tab1:
    st.code(source_code, language="python", line_numbers=True)

# ═══════════════════════════════
# TAB 2 (AST)
# ═══════════════════════════════
with tab2:
    st.subheader("Functions")

    for fn in parsed.get("functions", []):
        with st.expander(
            f"{fn.get('name','unknown')} — line {fn.get('line','N/A')}"
        ):
            st.write(fn)

    st.subheader("Classes")

    for cls in parsed.get("classes", []):
        with st.expander(
            f"{cls.get('name','unknown')} — line {cls.get('line','N/A')}"
        ):
            st.write(cls)

# ═══════════════════════════════
# TAB 3 (AI)
# ═══════════════════════════════
with tab3:
    if st.button("Run AI Analysis"):
        analysis = analyze_parsed_result(parsed, source_code)
        st.session_state["analysis"] = analysis

    if "analysis" in st.session_state:
        analysis = st.session_state["analysis"]

        # FUNCTIONS
        st.subheader("Function Analysis")

        for fn in analysis.get("functions", []):
            with st.expander(
                f"⚙️ `{fn.get('name','unknown')}()` — line {fn.get('line','N/A')}"
            ):
                st.write(fn.get("analysis", {}))

        # CLASSES
        st.subheader("Class Analysis")

        for cls in analysis.get("classes", []):
            with st.expander(
                f"🏛️ `{cls.get('name','unknown')}` — line {cls.get('line','N/A')}"
            ):
                st.write(cls.get("analysis", {}))

# ═══════════════════════════════
# TAB 4 (GRAPH)
# ═══════════════════════════════
with tab4:
    if st.button("Generate Graph"):
        G = build_graph([parsed])

        os.makedirs("outputs", exist_ok=True)
        path = os.path.join("outputs", "graph.png")

        draw_graph(G, output_path=path)

        st.image(path)

        st.write("Nodes:", G.number_of_nodes())
        st.write("Edges:", G.number_of_edges())

# ─── Cleanup ─────────────────────────────────────────────
try:
    os.unlink(temp_path)
except:
    pass