"""
app.py — Complete Streamlit Frontend with All Features
VTU Major Project: AI-Driven Semantic Code Analysis and Automated Software Architecture Modeling System
Run: streamlit run app.py
"""

import streamlit as st
import sys
import os
import tempfile
import networkx as nx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "features"))

from src.parser               import parse_file, read_file, get_summary
from src.analyzer             import analyze_parsed_result
from src.architect            import build_graph, draw_graph
from src.embedder             import embed_parsed_result, find_similar, build_similarity_matrix
from features.testgenerator            import generate_tests_for_file, get_test_summary
from features.refactorsuggestor        import refactor_all_functions, get_refactor_summary
from features.crossmoduleanalyser      import analyze_project, get_cross_module_graph, get_project_summary
from features.NIcodesearch             import CodeSearchEngine
from features.docgenerator             import generate_full_documentation, generate_readme, build_complexity_report

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Analyzer — VTU Major Project",
    page_icon="🧠", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header{font-size:2rem;font-weight:700;background:linear-gradient(90deg,#4A90D9,#9B59B6);
-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.tag{display:inline-block;padding:2px 10px;border-radius:12px;font-size:11px;margin:2px}
.tag-blue{background:#1a365d;color:#90cdf4}.tag-green{background:#1c4532;color:#9ae6b4}
.tag-amber{background:#44370a;color:#fbd38d}.tag-red{background:#3d1515;color:#fc8181}
.tag-purple{background:#2d1b69;color:#d6bcfa}
.feature-badge{background:linear-gradient(90deg,#6c8ff7,#a78bfa);color:white;
padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600}
</style>""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🧠 AI-Driven Semantic Code Analyzer</div>', unsafe_allow_html=True)
st.caption("VTU Major Project · AI-Driven Semantic Code Analysis and Automated Software Architecture Modeling System")
st.markdown('<span class="feature-badge">9 Tabs</span> &nbsp; <span class="feature-badge">Claude claude-opus-4-6</span> &nbsp; <span class="feature-badge">AST + Embeddings + Graph</span>', unsafe_allow_html=True)
st.divider()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    analyze_classes = st.toggle("AI: Analyze Classes",  value=True)
    show_embeddings = st.toggle("Semantic Embeddings",  value=True)
    show_call_graph = st.toggle("Show Call Graph",      value=True)
    multi_file_mode = st.toggle("Multi-file Mode",      value=False)
    st.divider()
    st.markdown("**Stack**")
    st.caption("Python `ast` · Claude claude-opus-4-6 · NetworkX · SentenceTransformers · Streamlit")
    st.divider()
    st.markdown("**VTU B.E. Computer Science · 2024–25**")

# ─── File Upload ──────────────────────────────────────────────────────────────
if multi_file_mode:
    uploaded_files = st.file_uploader("Upload Python files (.py)", type=["py"], accept_multiple_files=True)
    uploaded_file  = uploaded_files[0] if uploaded_files else None
else:
    uploaded_file  = st.file_uploader("Upload a Python file (.py)", type=["py"])
    uploaded_files = [uploaded_file] if uploaded_file else []

if not uploaded_file:
    st.info("👆 Upload a Python file to get started.")
    st.stop()

# ─── Parse all uploaded files ────────────────────────────────────────────────
all_parsed  = []
all_sources = {}
temp_paths  = []

for uf in uploaded_files:
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(uf.getvalue().decode("utf-8"))
        tp = tmp.name
    temp_paths.append(tp)
    src = read_file(tp)
    with st.spinner(f"Parsing {uf.name}..."):
        parsed = parse_file(tp)
    if "error" not in parsed:
        all_parsed.append(parsed)
        all_sources[tp] = src

if not all_parsed:
    st.error("❌ Could not parse uploaded file(s).")
    st.stop()

# Primary file
parsed      = all_parsed[0]
source_code = all_sources[temp_paths[0]]
summary     = get_summary(parsed)

# ─── Top Metrics ─────────────────────────────────────────────────────────────
st.subheader("📊 Code Structure Overview")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Functions",      summary["total_functions"])
c2.metric("Classes",        summary["total_classes"])
c3.metric("Methods",        summary["total_methods"])
c4.metric("Imports",        summary["total_imports"])
c5.metric("Avg Complexity", summary["avg_complexity"])
c6.metric("Files",          len(all_parsed))
st.divider()

# ─── All 9 Tabs ───────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📄 Source Code",
    "🔍 AST Structure",
    "🤖 AI Analysis",
    "🏗️ Architecture Graph",
    "🔗 Embeddings & Search",
    "🧪 Test Generator",
    "♻️ Code Refactoring",
    "🌐 Multi-file Analysis",
    "📚 Documentation",
])
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = tabs

# ════════════════════════════════════════════════
# TAB 1 — SOURCE CODE
# ════════════════════════════════════════════════
with tab1:
    st.markdown(f"**File:** `{uploaded_file.name}` · {len(source_code.splitlines())} lines")
    st.code(source_code, language="python", line_numbers=True)

# ════════════════════════════════════════════════
# TAB 2 — AST STRUCTURE
# ════════════════════════════════════════════════
with tab2:
    st.markdown("### 🌳 AST-Extracted Structure")
    st.caption("Parsed using Python's `ast` module — real semantic data, not regex.")

    st.markdown(f"---\n#### ⚙️ Functions ({len(parsed['functions'])})")
    for fn in parsed["functions"]:
        cx       = fn.get("complexity", 1)
        cx_label = fn.get("complexity_label", "low")
        cx_icon  = "🟢" if cx_label == "low" else "🟡" if cx_label == "medium" else "🔴"
        args_str = ", ".join(
            f"{a['name']}: {a['type']}" if a.get("type") else a["name"]
            for a in fn.get("args", [])
        )
        with st.expander(f"{'⚡' if fn.get('is_async') else '⚙️'}  {fn['name']}()  — line {fn['line']}  |  {cx_icon} complexity {cx} ({cx_label})"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Args:** `{args_str or 'none'}`")
                st.markdown(f"**Returns:** `{fn.get('return_type') or 'not annotated'}`")
                st.markdown(f"**Async:** {'✅' if fn.get('is_async') else '❌'}")
                if fn.get("decorators"):
                    st.markdown("**Decorators:** " + " ".join(f"`@{d}`" for d in fn["decorators"]))
                if fn.get("calls"):
                    st.markdown("**Calls:** " + " ".join(f"`{c}()`" for c in fn["calls"]))
            with col2:
                st.markdown("**Cyclomatic Complexity**")
                st.progress(min(cx / 10, 1.0))
                st.caption(f"Score: {cx} → {cx_label}  (Low≤3, Medium≤7, High>7)")
            st.markdown("**Docstring:**")
            if fn.get("docstring"):
                st.success(fn["docstring"])
            else:
                st.warning("⚠️ No docstring")

    st.markdown(f"---\n#### 🏛️ Classes ({len(parsed['classes'])})")
    for cls in parsed["classes"]:
        with st.expander(f"🏛️  {cls['name']}  — line {cls['line']}  |  {len(cls.get('methods', []))} methods"):
            col1, col2 = st.columns(2)
            with col1:
                bases = "`, `".join(cls.get("bases", [])) or "object"
                st.markdown(f"**Inherits:** `{bases}`")
            with col2:
                for m in cls.get("methods", []):
                    mcx   = m.get("complexity", 1)
                    micon = "🟢" if mcx <= 3 else "🟡" if mcx <= 7 else "🔴"
                    st.markdown(f"{micon} `{m['name']}()` — line {m['line']} — cx `{mcx}`")
            if cls.get("docstring"):
                st.success(cls["docstring"])
            else:
                st.warning("⚠️ No docstring")

    st.markdown(f"---\n#### 📦 Imports ({len(parsed['imports'])})")
    cols = st.columns(3)
    for i, imp in enumerate(parsed["imports"]):
        cols[i % 3].markdown(f"• `{imp}`")

    if show_call_graph and any(parsed.get("call_graph", {}).values()):
        st.markdown("---\n#### 🔗 Call Graph")
        for caller, callees in parsed.get("call_graph", {}).items():
            if callees:
                st.markdown(f"**`{caller}()`** → " + " · ".join(f"`{c}()`" for c in callees))

    if parsed.get("global_vars"):
        st.markdown("---\n#### 🌐 Global Variables")
        for v in parsed["global_vars"]:
            st.markdown(f"• `{v['name']}` — line {v['line']}")

# ════════════════════════════════════════════════
# TAB 3 — AI ANALYSIS
# ════════════════════════════════════════════════
with tab3:
    st.markdown("### 🤖 AI Semantic Analysis")
    st.caption("Claude claude-opus-4-6 analyzes each function and class for quality, issues, tags, and suggestions.")

    if st.button("🚀 Run AI Analysis", type="primary", use_container_width=True, key="ai_btn"):
        with st.spinner("Claude is analyzing — 30–60 seconds..."):
            analysis = analyze_parsed_result(parsed, source_code)
            st.session_state["analysis"] = analysis
        st.success("✅ Done!")

    if "analysis" in st.session_state:
        analysis = st.session_state["analysis"]
        arch = analysis.get("architecture", {})
        if arch:
            st.markdown("---\n#### 🏗️ Architecture Overview")
            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Pattern",  arch.get("architecture_pattern", "—"))
            a2.metric("Coupling", arch.get("coupling", "—").capitalize())
            a3.metric("Cohesion", arch.get("cohesion", "—").capitalize())
            a4.metric("Quality",  f"{arch.get('overall_quality', 0)}/100")
            if arch.get("summary"):
                st.info(arch["summary"])
            for rec in arch.get("recommendations", []):
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.get("priority", "low"), "⚪")
                with st.expander(f"{icon} [{rec['priority'].upper()}] {rec['title']}"):
                    st.write(rec["detail"])

        st.markdown(f"---\n#### ⚙️ Function Analysis ({len(analysis.get('functions', []))})")
        for fn in analysis.get("functions", []):
            a       = fn.get("analysis", {})
            q       = a.get("quality_score", 0)
            q_icon  = "🟢" if q >= 80 else "🟡" if q >= 60 else "🔴"
            cx_icon = "🟢" if fn.get("complexity_label") == "low" else "🟡" if fn.get("complexity_label") == "medium" else "🔴"
            with st.expander(f"⚙️ `{fn['name']}()` — line {fn['line']} | {q_icon} Quality: {q}/100 | {cx_icon} cx: {fn.get('complexity', 1)}"):
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"**🎯 Responsibility:** {a.get('responsibility', '—')}")
                    tags = a.get("tags", [])
                    if tags:
                        tag_map = {"pure": "tag-green", "io": "tag-blue", "side-effect": "tag-amber",
                                   "utility": "tag-blue", "entry-point": "tag-purple",
                                   "async": "tag-purple", "recursive": "tag-amber"}
                        st.markdown(" ".join(
                            f'<span class="tag {tag_map.get(t, "tag-blue")}">{t}</span>'
                            for t in tags), unsafe_allow_html=True)
                    err = a.get("error_handling", "none")
                    st.markdown(f"**🛡️ Error handling:** {'✅' if err == 'good' else '🟡' if err == 'partial' else '❌'} `{err}`")
                    if a.get("missing_docstring"):  st.warning("⚠️ Missing docstring")
                    if a.get("missing_type_hints"): st.warning("⚠️ Missing type hints")
                with col2:
                    st.markdown("**📊 Quality Score**")
                    st.markdown(f"## {q_icon} {q}/100")
                    st.progress(q / 100)
                for issue in a.get("issues", []):      st.error(f"• {issue}")
                for sug   in a.get("suggestions", []): st.success(f"• {sug}")

        if analyze_classes:
            for cls in analysis.get("classes", []):
                a      = cls.get("analysis", {})
                q      = a.get("quality_score", 0)
                q_icon = "🟢" if q >= 80 else "🟡" if q >= 60 else "🔴"
                with st.expander(f"🏛️ `{cls['name']}` | {q_icon} Quality: {q}/100"):
                    st.markdown(f"**Responsibility:** {a.get('responsibility', '—')}")
                    if a.get("design_pattern", "none") != "none":
                        st.success(f"🎨 Design Pattern: **{a['design_pattern']}**")
                    st.markdown(f"**SRP:** {'✅' if a.get('srp_compliant') else '❌'}")
                    for issue in a.get("issues", []):      st.error(f"• {issue}")
                    for sug   in a.get("suggestions", []): st.success(f"• {sug}")
    else:
        st.info("Click **Run AI Analysis** to start.")

# ════════════════════════════════════════════════
# TAB 4 — ARCHITECTURE GRAPH
# ════════════════════════════════════════════════
with tab4:
    st.markdown("### 🏗️ Software Architecture Graph")
    st.caption("Auto-generated from AST using NetworkX. Hierarchical layout with call edges.")

    if st.button("🏗️ Generate Graph", type="primary", use_container_width=True, key="graph_btn"):
        with st.spinner("Building graph..."):
            G = build_graph([parsed])
            os.makedirs("outputs", exist_ok=True)
            gpath = f"outputs/arch_{uploaded_file.name}.png"
            draw_graph(G, output_path=gpath)
            st.session_state["graph_path"] = gpath
            st.session_state["graph_G"]    = G
        st.success("✅ Done!")

    if "graph_path" in st.session_state:
        st.image(st.session_state["graph_path"], use_container_width=True)
        G = st.session_state["graph_G"]
        g1, g2, g3 = st.columns(3)
        g1.metric("Nodes",   G.number_of_nodes())
        g2.metric("Edges",   G.number_of_edges())
        g3.metric("Density", f"{nx.density(G):.3f}" if G.number_of_nodes() > 1 else "—")
        with open(st.session_state["graph_path"], "rb") as f:
            st.download_button("⬇️ Download PNG", f.read(),
                               file_name=f"arch_{uploaded_file.name}.png", mime="image/png")

# ════════════════════════════════════════════════
# TAB 5 — EMBEDDINGS & NL SEARCH
# ════════════════════════════════════════════════
with tab5:
    st.markdown("### 🔗 Semantic Embeddings & Natural Language Search")
    st.caption("384-dim vectors via MiniLM-L6-v2. Search your code using plain English.")

    if st.button("🔗 Build Search Index", type="primary", use_container_width=True, key="emb_btn"):
        with st.spinner("Generating embeddings..."):
            engine = CodeSearchEngine()
            count  = engine.build_index(all_parsed)
            st.session_state["search_engine"] = engine
            st.session_state["embeddings"]    = embed_parsed_result(parsed)
        st.success(f"✅ Indexed {count} symbols!")

    if "search_engine" in st.session_state:
        engine = st.session_state["search_engine"]
        stats  = engine.get_stats()
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Indexed",      stats["total_indexed"])
        s2.metric("Functions",    stats["functions"])
        s3.metric("Undocumented", stats["undocumented"])
        s4.metric("High cx",      stats["high_complexity"])

        st.markdown("---\n#### 🔍 Natural Language Search")
        col1, col2, col3 = st.columns([3, 1, 1])
        query = col1.text_input("Search your code in plain English:",
                                placeholder="e.g. 'function that loads data from a file'")
        ftype = col2.selectbox("Filter type", ["all", "function", "class"])
        fcx   = col3.selectbox("Complexity",  ["all", "low", "medium", "high"])

        if query:
            results = engine.search(
                query, top_k=5,
                filter_type=None if ftype == "all" else ftype,
                filter_complexity=None if fcx == "all" else fcx
            )
            if results:
                for r in results:
                    icon = "⚙️" if r["type"] == "function" else "🏛️"
                    st.markdown(f"{icon} **`{r['name']}`** ({r['file']}, line {r['line']}) — similarity `{r['similarity']:.4f}`")
                    st.progress(float(r["similarity"]))
                    if r.get("docstring"):
                        st.caption(r["docstring"][:100])
            else:
                st.warning("No results found. Try a different query.")

        st.markdown("---\n#### 🔴 Complexity Hotspots")
        for fn in engine.get_complexity_hotspots(5):
            icon = "🔴" if fn["cx_label"] == "high" else "🟡" if fn["cx_label"] == "medium" else "🟢"
            st.markdown(f"{icon} `{fn['name']}()` — complexity `{fn['complexity']}` ({fn['cx_label']}) — {fn['file']}")

# ════════════════════════════════════════════════
# TAB 6 — TEST GENERATOR
# ════════════════════════════════════════════════
with tab6:
    st.markdown("### 🧪 Automatic Test Case Generator")
    st.caption("Claude claude-opus-4-6 generates pytest test cases for every function.")
    st.info("🚀 **Beyond ChatGPT:** Uses cyclomatic complexity and type hints to write smarter, branch-aware tests.")

    if st.button("🧪 Generate Test Cases", type="primary", use_container_width=True, key="test_btn"):
        with st.spinner("Generating pytest test cases with Claude..."):
            test_code    = generate_tests_for_file(parsed, source_code)
            test_summary = get_test_summary(test_code)
            st.session_state["test_code"]    = test_code
            st.session_state["test_summary"] = test_summary
        st.success(f"✅ Generated {test_summary['total_tests']} test cases!")

    if "test_code" in st.session_state:
        ts = st.session_state["test_summary"]
        t1, t2, t3 = st.columns(3)
        t1.metric("Total Tests",     ts["total_tests"])
        t2.metric("Exception Tests", ts["exception_tests"])
        t3.metric("Async Tests",     ts["async_tests"])
        st.markdown("---\n#### Generated Test File")
        st.code(st.session_state["test_code"], language="python", line_numbers=True)
        st.download_button("⬇️ Download Test File",
                           st.session_state["test_code"],
                           file_name=f"test_{uploaded_file.name}",
                           mime="text/plain")
    else:
        st.info("Click **Generate Test Cases** to start.")

# ════════════════════════════════════════════════
# TAB 7 — CODE REFACTORING
# ════════════════════════════════════════════════
with tab7:
    st.markdown("### ♻️ AI Code Refactoring Engine")
    st.caption("Claude claude-opus-4-6 rewrites each function with better docstrings, type hints, error handling, and reduced complexity.")
    st.info("🚀 **Beyond ChatGPT:** Before/after comparison with improvement score and exact changes made.")

    if st.button("♻️ Refactor All Functions", type="primary", use_container_width=True, key="refactor_btn"):
        with st.spinner("Refactoring with Claude — this takes ~1 min..."):
            results   = refactor_all_functions(parsed, source_code)
            summary_r = get_refactor_summary(results)
            st.session_state["refactor_results"] = results
            st.session_state["refactor_summary"] = summary_r
        st.success("✅ Refactoring complete!")

    if "refactor_results" in st.session_state:
        sr = st.session_state["refactor_summary"]
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Functions Refactored", sr["functions_refactored"])
        r2.metric("Total Changes",        sr["total_changes_applied"])
        r3.metric("Avg Improvement",      f"{sr['avg_improvement_score']}/100")
        r4.metric("Complexity Reduced",   sr["complexity_reductions"])

        for item in st.session_state["refactor_results"]:
            result    = item["result"]
            imp       = result.get("improvement_score", 0)
            q_icon    = "🟢" if imp >= 80 else "🟡" if imp >= 60 else "🔴"
            cx_before = result.get("complexity_before", "—")
            cx_after  = result.get("complexity_after",  "—")
            with st.expander(f"♻️ `{item['name']}()` | {q_icon} Improvement: {imp}/100 | Complexity: {cx_before} → {cx_after}"):
                st.markdown("**Changes Applied:**")
                for change in result.get("changes", []):
                    st.success(f"✅ {change}")
                st.markdown("**Refactored Code:**")
                st.code(result.get("refactored_code", ""), language="python")
    else:
        st.info("Click **Refactor All Functions** to start.")

# ════════════════════════════════════════════════
# TAB 8 — MULTI-FILE ANALYSIS
# ════════════════════════════════════════════════
with tab8:
    st.markdown("### 🌐 Multi-file Cross-Module Analysis")
    st.caption("Upload multiple .py files, analyze cross-file dependencies, detect circular imports, and build a project-level architecture graph.")
    st.info("🚀 **Beyond ChatGPT:** Detects circular dependencies and cross-module call relationships automatically.")

    if len(all_parsed) > 1:
        if st.button("🌐 Analyze Project", type="primary", use_container_width=True, key="multi_btn"):
            with st.spinner("Analyzing cross-module dependencies..."):
                project  = analyze_project(all_parsed)
                proj_sum = get_project_summary(project)
                gpath    = "outputs/cross_module.png"
                get_cross_module_graph(all_parsed, gpath)
                st.session_state["project"]     = project
                st.session_state["proj_sum"]    = proj_sum
                st.session_state["cross_graph"] = gpath
            st.success("✅ Cross-module analysis complete!")

        if "project" in st.session_state:
            ps = st.session_state["proj_sum"]
            p1, p2, p3, p4, p5 = st.columns(5)
            p1.metric("Files",          ps["total_files"])
            p2.metric("Functions",      ps["total_functions"])
            p3.metric("Cross-calls",    ps["cross_file_calls"])
            p4.metric("Shared imports", ps["shared_imports"])
            p5.metric("Circular deps",  ps["circular_deps"])

            if ps["has_circular_deps"]:
                st.error(f"⚠️ Circular dependencies: {st.session_state['project']['circular_deps']}")
            else:
                st.success("✅ No circular dependencies found!")

            project = st.session_state["project"]
            if project["cross_calls"]:
                st.markdown("#### 🔗 Cross-file Calls")
                for call in project["cross_calls"]:
                    st.markdown(f"• `{call['from_file']}::{call['from_function']}()` → `{call['to_file']}::{call['to_function']}()`")

            if project["shared_imports"]:
                st.markdown("#### 📦 Shared Imports")
                for imp in project["shared_imports"]:
                    st.markdown(f"• `{imp['module']}` used in: {', '.join(imp['used_in'])}")

            if "cross_graph" in st.session_state:
                st.image(st.session_state["cross_graph"],
                         use_container_width=True, caption="Cross-module Architecture Graph")
    else:
        st.info("Enable **Multi-file Mode** in the sidebar and upload 2+ Python files to use this feature.")

# ════════════════════════════════════════════════
# TAB 9 — DOCUMENTATION GENERATOR
# ════════════════════════════════════════════════
with tab9:
    st.markdown("### 📚 AI Documentation Generator")
    st.caption("Generates a complete Markdown documentation file: README, API docs, complexity report, and module descriptions.")
    st.info("🚀 **Beyond ChatGPT:** One click generates submission-ready documentation with complexity tables, API reference, and tech stack.")

    if st.button("📚 Generate Documentation", type="primary", use_container_width=True, key="doc_btn"):
        with st.spinner("Generating documentation..."):
            readme    = generate_readme(all_parsed)
            cx_report = build_complexity_report(all_parsed)
            full_doc  = readme + "\n\n---\n\n" + cx_report
            st.session_state["documentation"] = full_doc
        st.success("✅ Documentation generated!")

    if "documentation" in st.session_state:
        doc = st.session_state["documentation"]
        st.markdown("---")
        st.markdown(doc)
        st.markdown("---")
        st.download_button(
            "⬇️ Download documentation.md", doc,
            file_name=f"documentation_{uploaded_file.name.replace('.py', '')}.md",
            mime="text/markdown"
        )
        st.download_button(
            "⬇️ Download as .txt", doc,
            file_name=f"documentation_{uploaded_file.name.replace('.py', '')}.txt",
            mime="text/plain"
        )
    else:
        st.info("Click **Generate Documentation** to start.")

# ─── Cleanup ─────────────────────────────────────────────────────────────────
for tp in temp_paths:
    try:
        os.unlink(tp)
    except Exception:
        pass