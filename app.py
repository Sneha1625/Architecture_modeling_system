"""
FINAL APP.PY (WITH MULTI-FILE + 12 FEATURES INCLUDING AI CODE REVIEW BOT)
"""

import streamlit as st
import sys
import os
import tempfile
import networkx as nx
from dotenv import load_dotenv

# ───── LOAD ENV ─────
load_dotenv()

# ───── PATH FIX ─────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "features"))

# ───── IMPORTS ─────
from src.parser import parse_file, read_file, get_summary
from src.analyzer import analyze_parsed_result
from src.architect import build_graph, draw_graph
from src.embedder import embed_parsed_result

from features.testgenerator import generate_tests_for_file, get_test_summary
from features.refactorsuggestor import refactor_all_functions
from features.docgenerator import generate_readme, build_complexity_report

from src.dependency import build_dependency_graph, draw_dependency_graph
from features.aiexplainer import explain_code
from features.aicodeviewer import review_code   # ✅ NEW FEATURE

# ───── UI ─────
st.set_page_config(page_title="AI Code Analyzer", layout="wide")
st.title("🧠 AI Code Analyzer (12 Features)")

# ───── FILE UPLOAD ─────
uploaded_files = st.file_uploader(
    "Upload Python files (multiple supported)",
    type=["py"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("Upload at least one Python file")
    st.stop()

# ───── SAVE TEMP FILES ─────
file_paths = []

for file in uploaded_files:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp.write(file.getvalue())
    tmp.close()
    file_paths.append(tmp.name)

# ───── PARSE FILES ─────
parsed_files = []
all_sources = []

for path in file_paths:
    try:
        parsed_files.append(parse_file(path))
        all_sources.append(read_file(path))
    except Exception as e:
        st.error(f"Error parsing file: {e}")

# ───── SUMMARY ─────
total_functions = sum(get_summary(p)["total_functions"] for p in parsed_files)
total_classes = sum(get_summary(p)["total_classes"] for p in parsed_files)
total_imports = sum(get_summary(p)["total_imports"] for p in parsed_files)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Functions", total_functions)
c2.metric("Classes", total_classes)
c3.metric("Imports", total_imports)
c4.metric("Files", len(file_paths))

st.divider()

# ───── TABS (12 FEATURES) ─────
tabs = st.tabs([
    "📄 Code",
    "🔍 AST",
    "🤖 AI Analysis",
    "🏗 Architecture",
    "🔗 Embeddings",
    "🧪 Tests",
    "♻️ Refactor",
    "📚 Docs",
    "📊 Dependency Graph",
    "🧠 Explain Code",
    "🌐 Multi-file Analysis",
    "👨‍💻 Code Review Bot"   # ✅ NEW
])

(t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12) = tabs


# ───── 1 CODE ─────
with t1:
    for i, code in enumerate(all_sources):
        st.subheader(f"File {i+1}")
        st.code(code, language="python")


# ───── 2 AST ─────
with t2:
    st.json(parsed_files)


# ───── 3 AI ANALYSIS ─────
with t3:
    if st.button("Run AI Analysis"):
        try:
            result = analyze_parsed_result(parsed_files[0], all_sources[0])
            st.write(result)
        except Exception as e:
            st.error(str(e))


# ───── 4 ARCHITECTURE ─────
with t4:
    if st.button("Generate Architecture"):
        G = build_graph(parsed_files)
        os.makedirs("outputs", exist_ok=True)
        path = "outputs/architecture.png"
        draw_graph(G, path)
        st.image(path)


# ───── 5 EMBEDDINGS ─────
with t5:
    if st.button("Generate Embeddings"):
        emb = embed_parsed_result(parsed_files[0])
        st.write(emb[:10])


# ───── 6 TESTS ─────
with t6:
    if st.button("Generate Tests"):
        tests = generate_tests_for_file(parsed_files[0], all_sources[0])
        st.code(tests)


# ───── 7 REFACTOR ─────
with t7:
    if st.button("Refactor Code"):
        res = refactor_all_functions(parsed_files[0], all_sources[0])
        for r in res:
            st.code(r["result"]["refactored_code"])


# ───── 8 DOCS ─────
with t8:
    if st.button("Generate Docs"):
        readme = generate_readme(parsed_files)
        report = build_complexity_report(parsed_files)
        st.markdown(readme + "\n\n" + report)


# ───── 9 DEPENDENCY GRAPH ─────
with t9:
    if st.button("Dependency Graph"):
        G = nx.DiGraph()

        for path in file_paths:
            sub = build_dependency_graph(path)
            G = nx.compose(G, sub)

        os.makedirs("outputs", exist_ok=True)
        path = "outputs/dependency.png"
        draw_dependency_graph(G, path)

        st.image(path)
        st.write("Nodes:", G.number_of_nodes())
        st.write("Edges:", G.number_of_edges())


# ───── 10 AI EXPLANATION ─────
with t10:
    if st.button("Explain Code"):
        try:
            explanation = explain_code(all_sources[0])
            st.write(explanation)
        except Exception as e:
            st.error(str(e))


# ───── 11 MULTI FILE ANALYSIS ─────
with t11:

    st.markdown("## 🌐 Multi-file Cross Module Analysis")

    if st.button("Run Full Project Analysis 🚀"):

        G = nx.DiGraph()

        for path in file_paths:
            sub = build_dependency_graph(path)
            G = nx.compose(G, sub)

        os.makedirs("outputs", exist_ok=True)
        path = "outputs/multifile.png"
        draw_dependency_graph(G, path)

        st.image(path)

        cycles = list(nx.simple_cycles(G))

        if cycles:
            st.error("Circular Dependencies Found!")
            for c in cycles:
                st.write(" ➜ ".join(c))
        else:
            st.success("No circular dependencies found")

        st.success(f"Files: {len(file_paths)} | Nodes: {G.number_of_nodes()} | Edges: {G.number_of_edges()}")


# ───── 12 AI CODE REVIEW BOT (NEW FEATURE) ─────
with t12:

    st.markdown("## 👨‍💻 AI Code Review Bot")
    st.caption("Acts like a senior developer reviewing your code")

    option = st.selectbox(
        "Choose code",
        ["Full Code", "Paste Custom Code"]
    )

    code_to_review = ""

    if option == "Full Code":
        code_to_review = all_sources[0]
    else:
        code_to_review = st.text_area("Paste your code here")

    if st.button("Review Code 🔍"):

        if code_to_review.strip() == "":
            st.warning("Please provide code")
        else:
            try:
                review = review_code(code_to_review)
                st.success("Review Generated")
                st.write(review)
            except Exception as e:
                st.error(str(e))


# ───── CLEANUP ─────
for path in file_paths:
    try:
        os.unlink(path)
    except:
        pass