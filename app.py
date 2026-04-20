"""
app.py — FINAL CLEAN VERSION (FUNCTION-LEVEL DEPENDENCY GRAPH FIXED)
Run: python -m streamlit run app.py
"""

import streamlit as st
import sys
import os
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "features"))

# ───────────────── CORE IMPORTS ─────────────────
from src.parser import parse_file, read_file, get_summary
from src.analyzer import analyze_parsed_result
from src.architect import build_graph, draw_graph
from src.embedder import embed_parsed_result
from features.testgenerator import generate_tests_for_file, get_test_summary
from features.refactorsuggestor import refactor_all_functions, get_refactor_summary
from features.docgenerator import generate_readme, build_complexity_report

# ───────────────── FUNCTION DEPENDENCY MODULE ─────────────────
from src.dependency import build_dependency_graph, draw_dependency_graph


# ───────────────── PAGE CONFIG ─────────────────
st.set_page_config(page_title="AI Code Analyzer", layout="wide")

st.title("🧠 AI-Driven Semantic Code Analyzer")
st.caption("Architecture + AI + Function Dependency + Refactoring System")


# ───────────────── FILE UPLOAD ─────────────────
uploaded_file = st.file_uploader("Upload Python file", type=["py"])

if uploaded_file:

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp.write(uploaded_file.getvalue())
    tmp.close()

    file_path = tmp.name

else:
    st.info("Upload a Python file to start analysis")
    st.stop()


# ───────────────── PARSE FILE ─────────────────
source_code = read_file(file_path)
parsed = parse_file(file_path)
summary = get_summary(parsed)


# ───────────────── METRICS ─────────────────
c1, c2, c3, c4 = st.columns(4)

c1.metric("Functions", summary["total_functions"])
c2.metric("Classes", summary["total_classes"])
c3.metric("Imports", summary["total_imports"])
c4.metric("Complexity", summary["avg_complexity"])

st.divider()


# ───────────────── TABS ─────────────────
tabs = st.tabs([
    "📄 Code",
    "🔍 AST",
    "🤖 AI Analysis",
    "🏗 Architecture",
    "🔗 Embeddings",
    "🧪 Tests",
    "♻️ Refactor",
    "📚 Docs",
    "📊 Dependency Graph"
])

(t1, t2, t3, t4, t5, t6, t7, t8, t9) = tabs


# ───────────────── TAB 1: CODE ─────────────────
with t1:
    st.code(source_code, language="python")


# ───────────────── TAB 2: AST ─────────────────
with t2:
    st.json(parsed)


# ───────────────── TAB 3: AI ANALYSIS ─────────────────
with t3:
    if st.button("Run AI Analysis"):
        result = analyze_parsed_result(parsed, source_code)
        st.write(result)


# ───────────────── TAB 4: ARCHITECTURE ─────────────────
with t4:
    if st.button("Generate Architecture Graph"):

        G = build_graph([parsed])

        os.makedirs("outputs", exist_ok=True)
        path = "outputs/architecture.png"

        draw_graph(G, output_path=path)

        st.image(path)

        st.success(f"Nodes: {G.number_of_nodes()} | Edges: {G.number_of_edges()}")


# ───────────────── TAB 5: EMBEDDINGS ─────────────────
with t5:
    if st.button("Generate Embeddings"):
        emb = embed_parsed_result(parsed)
        st.write(emb[:10])


# ───────────────── TAB 6: TESTS ─────────────────
with t6:
    if st.button("Generate Tests"):
        tests = generate_tests_for_file(parsed, source_code)
        summary = get_test_summary(tests)

        st.write(summary)
        st.code(tests)


# ───────────────── TAB 7: REFACTOR ─────────────────
with t7:
    if st.button("Refactor Code"):
        result = refactor_all_functions(parsed, source_code)

        for r in result:
            st.code(r["result"]["refactored_code"])


# ───────────────── TAB 8: DOCS ─────────────────
with t8:
    if st.button("Generate Docs"):
        readme = generate_readme([parsed])
        report = build_complexity_report([parsed])

        st.markdown(readme + "\n\n" + report)


# ───────────────── TAB 9: FUNCTION DEPENDENCY GRAPH (FIXED FINAL) ─────────────────
with t9:

    st.markdown("### 🔥 Function / Method Dependency Graph")
    st.caption("Shows which function/method calls which function")

    st.info("""
    ✔ Node = Function or Class  
    ✔ Arrow A → B = A calls B  
    ✔ Blue = Function  
    ✔ Orange = Class  
    """)

    if st.button("Generate Dependency Graph"):

        # IMPORTANT FIX:
        # Use ONLY uploaded file (NOT BASE_DIR, NOT PROJECT ROOT)
        G = build_dependency_graph(file_path)

        os.makedirs("outputs", exist_ok=True)
        path = "outputs/dependency.png"

        draw_dependency_graph(G, path)

        st.image(path, use_container_width=True)

        st.success(f"""
        Functions/Classes: {G.number_of_nodes()}  
        Call Dependencies: {G.number_of_edges()}
        """)


# ───────────────── CLEANUP ─────────────────
try:
    os.unlink(file_path)
except:
    pass