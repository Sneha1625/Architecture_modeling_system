"""
FINAL APP.PY
AI Code Analyzer - 21 Features
Includes Interactive Animated Architecture Diagram, Clone Detection,
Module Boundary Detection, Logical Coupling Mining, Risk Prediction,
Static Execution Path Replay, Natural Language Code Search,
Change Impact / Ripple Effect Prediction, and Repository Overview
with Commit History
"""

# ─────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────
from features.coupling_miner import mine_logical_coupling
import streamlit as st
import sys
import os
import tempfile
import networkx as nx
import plotly.graph_objects as go
from git import Repo
from pathlib import Path
from features.clone_detector import summarize_clones
from features.community_detector import analyze_modularity
from features.risk_predictor import compute_risk_scores
from features.execution_tracer import trace_static_execution_path, draw_execution_step
from features.NIcodesearch import CodeSearchEngine
from features.impact_predictor import predict_change_impact
from features.ast_structural_clones import find_structural_clones
from dotenv import load_dotenv
from features.github_analyzer import (
    clone_github_repository,
    find_python_files,
    get_repository_info
)

# ─────────────────────────────────────────────────────────────
# LOAD ENVIRONMENT
# ─────────────────────────────────────────────────────────────

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_ENV = os.path.join(BASE_DIR, "src", ".env")

if os.path.exists(SRC_ENV):
    load_dotenv(SRC_ENV)


# ─────────────────────────────────────────────────────────────
# PATH FIX
# ─────────────────────────────────────────────────────────────

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "features"))


# ─────────────────────────────────────────────────────────────
# PROJECT IMPORTS
# ─────────────────────────────────────────────────────────────

from src.parser import (
    parse_file,
    read_file,
    get_summary
)

from src.analyzer import analyze_parsed_result

from src.architect import (
    build_graph,
    draw_graph
)

from src.embedder import embed_parsed_result

from features.testgenerator import generate_tests_for_file

from features.refactorsuggestor import refactor_all_functions

from features.docgenerator import (
    generate_readme,
    build_complexity_report
)

from src.dependency import (
    build_dependency_graph,
    draw_dependency_graph
)

from features.aiexplainer import explain_code

from features.aicodeviewer import review_code

from features.techdebt import calculate_technical_debt


# ─────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Code Analyzer",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI Code Analyzer")
st.caption(
    "Analyze code structure, architecture, dependencies, "
    "quality, documentation, and technical debt."
)


# ─────────────────────────────────────────────────────────────
# ANIMATED ARCHITECTURE FUNCTION
# ─────────────────────────────────────────────────────────────

def create_animated_architecture(G):
    """
    Create an interactive and animated software architecture
    diagram using Plotly and NetworkX.
    """

    if G.number_of_nodes() == 0:
        st.warning("No architecture nodes found.")
        return

    pos = nx.spring_layout(
        G,
        seed=42,
        k=2.0,
        iterations=100
    )

    nodes = list(G.nodes())

    edge_x = []
    edge_y = []

    for source, target in G.edges():

        if source not in pos or target not in pos:
            continue

        x0, y0 = pos[source]
        x1, y1 = pos[target]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1.5),
        hoverinfo="none"
    )

    node_x = []
    node_y = []
    node_text = []
    node_hover = []

    for node in nodes:

        x, y = pos[node]

        node_x.append(x)
        node_y.append(y)
        node_text.append(str(node))

        degree = G.degree(node)

        node_hover.append(
            f"<b>{node}</b><br>Connections: {degree}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        hovertext=node_hover,
        hoverinfo="text",
        marker=dict(size=28, line=dict(width=2))
    )

    frames = []

    for step in range(1, len(nodes) + 1):

        visible_nodes = nodes[:step]

        visible_node_x = []
        visible_node_y = []
        visible_node_text = []
        visible_node_hover = []

        for node in visible_nodes:

            x, y = pos[node]

            visible_node_x.append(x)
            visible_node_y.append(y)
            visible_node_text.append(str(node))

            visible_node_hover.append(
                f"<b>{node}</b><br>Connections: {G.degree(node)}"
            )

        visible_edge_x = []
        visible_edge_y = []

        visible_set = set(visible_nodes)

        for source, target in G.edges():

            if source in visible_set and target in visible_set:

                x0, y0 = pos[source]
                x1, y1 = pos[target]

                visible_edge_x.extend([x0, x1, None])
                visible_edge_y.extend([y0, y1, None])

        frame = go.Frame(
            name=f"frame{step}",
            data=[
                go.Scatter(
                    x=visible_edge_x,
                    y=visible_edge_y,
                    mode="lines",
                    line=dict(width=1.5),
                    hoverinfo="none"
                ),
                go.Scatter(
                    x=visible_node_x,
                    y=visible_node_y,
                    mode="markers+text",
                    text=visible_node_text,
                    textposition="top center",
                    hovertext=visible_node_hover,
                    hoverinfo="text",
                    marker=dict(size=28, line=dict(width=2))
                )
            ]
        )

        frames.append(frame)

    fig = go.Figure(
        data=[edge_trace, node_trace],
        frames=frames
    )

    fig.update_layout(

        title=dict(
            text="🏗️ Interactive Software Architecture",
            x=0.5,
            xanchor="center"
        ),

        showlegend=False,
        hovermode="closest",
        height=700,

        margin=dict(b=20, l=20, r=20, t=100),

        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),

        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0.01,
                y=1.12,
                buttons=[
                    dict(
                        label="▶ Build Architecture",
                        method="animate",
                        args=[
                            [f"frame{i}" for i in range(1, len(nodes) + 1)],
                            {
                                "frame": {"duration": 700, "redraw": True},
                                "transition": {"duration": 400},
                                "fromcurrent": True,
                                "mode": "immediate"
                            }
                        ]
                    ),
                    dict(
                        label="⏹ Show Complete",
                        method="animate",
                        args=[
                            [f"frame{len(nodes)}"],
                            {
                                "frame": {"duration": 500, "redraw": True},
                                "transition": {"duration": 300}
                            }
                        ]
                    )
                ]
            )
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Modules", G.number_of_nodes())
    col2.metric("Dependencies", G.number_of_edges())

    density = nx.density(G) if G.number_of_nodes() > 0 else 0

    col3.metric("Graph Density", f"{density:.2f}")

    st.info(
        "💡 Click 'Build Architecture' to see the architecture "
        "appear step-by-step. Hover over modules to inspect "
        "their connections. You can also zoom and drag the diagram."
    )


# ─────────────────────────────────────────────────────────────
# GITHUB REPOSITORY HELPERS (repo overview + commit history)
# ─────────────────────────────────────────────────────────────

def get_github_repository_overview(repo_path, github_url):
    """Return basic repository information (name, owner, branch, commit count)."""
    repo = Repo(repo_path)

    repo_name = Path(repo_path).name

    clean_url = github_url.strip().rstrip("/")
    if clean_url.endswith(".git"):
        clean_url = clean_url[:-4]

    parts = clean_url.split("/")
    owner = "Unknown"
    if len(parts) >= 2 and "github.com" in clean_url.lower():
        owner = parts[-2]
        repo_name = parts[-1] or repo_name

    try:
        branch = repo.active_branch.name
    except TypeError:
        branch = "Detached HEAD"
    except Exception:
        branch = "Unknown"

    return {
        "name": repo_name,
        "owner": owner,
        "branch": branch,
        "url": github_url.strip(),
        "commit_count": sum(1 for _ in repo.iter_commits("--all")),
    }


def get_recent_commits(repo_path, limit=10):
    """Return recent commits with author, date, message and changed files."""
    repo = Repo(repo_path)
    commits = []

    for commit in repo.iter_commits("--all", max_count=limit):
        changed_files = set()

        try:
            if commit.parents:
                parent = commit.parents[0]
                for diff in parent.diff(commit, create_patch=False):
                    if diff.a_path:
                        changed_files.add(diff.a_path)
                    if diff.b_path:
                        changed_files.add(diff.b_path)
            else:
                for item in commit.tree.traverse():
                    if item.type == "blob":
                        changed_files.add(item.path)
        except Exception:
            changed_files = set()

        commits.append({
            "hash": commit.hexsha[:7],
            "message": commit.message.strip().splitlines()[0] if commit.message.strip() else "No commit message",
            "author": commit.author.name or "Unknown",
            "date": commit.committed_datetime.strftime("%Y-%m-%d %H:%M"),
            "files_changed": len(changed_files),
            "changed_files": sorted(changed_files),
        })

    return commits


# ─────────────────────────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────────────────────────

uploaded_files = st.file_uploader(
    "📂 Upload Python files (multiple files supported)",
    type=["py"],
    accept_multiple_files=True
)


if not uploaded_files:
    st.info("Upload at least one Python file to start the analysis.")
    st.stop()


# ─────────────────────────────────────────────────────────────
# SAVE UPLOADED FILES
# ─────────────────────────────────────────────────────────────

file_paths = []

for uploaded_file in uploaded_files:

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
    tmp.write(uploaded_file.getvalue())
    tmp.close()

    file_paths.append(tmp.name)


# ─────────────────────────────────────────────────────────────
# PARSE FILES
# ─────────────────────────────────────────────────────────────

parsed_files = []
all_sources = []

for path in file_paths:
    parsed_files.append(parse_file(path))
    all_sources.append(read_file(path))


# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────

total_functions = sum(get_summary(parsed)["total_functions"] for parsed in parsed_files)
total_classes = sum(get_summary(parsed)["total_classes"] for parsed in parsed_files)
total_imports = sum(get_summary(parsed)["total_imports"] for parsed in parsed_files)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Functions", total_functions)
c2.metric("Classes", total_classes)
c3.metric("Imports", total_imports)
c4.metric("Files", len(file_paths))

st.divider()


# ─────────────────────────────────────────────────────────────
# 21 FEATURES
# ─────────────────────────────────────────────────────────────

tabs = st.tabs([
    "💻 Code",
    "🤖 AI Analysis",
    "🏗️ Architecture",
    "🔢 Embeddings",
    "🧪 Tests",
    "🔧 Refactor",
    "📚 Docs",
    "🔗 Dependency Graph",
    "💡 Explain Code",
    "🌐 Multi-file Analysis",
    "👨‍💻 Code Review Bot",
    "💰 Technical Debt",
    "🐙 GitHub Repository",
    "🔀 Logical Coupling",
    "🧬 Clone Detection",
    "🧩 Module Boundaries",
    "🔥 Risk Hotspots",
    "▶️ Execution Replay",
    "🔎 NL Code Search",
    "⚡ Change Impact"
])

(
    t1, t2, t3, t4, t5, t6, t7, t8, t9, t10,
    t11, t12, t13, t14, t15, t16, t17, t18, t19, t20
) = tabs


# ─────────────────────────────────────────────────────────────
# 1. CODE VIEWER
# ─────────────────────────────────────────────────────────────

with t1:
    st.header("💻 Source Code")

    for i, code in enumerate(all_sources):
        st.subheader(f"File {i + 1}")
        st.code(code, language="python")


# ─────────────────────────────────────────────────────────────
# 2. AI ANALYSIS
# ─────────────────────────────────────────────────────────────

with t2:
    st.header("🤖 AI Code Analysis")

    if st.button("Run AI Analysis", key="ai_analysis"):
        result = analyze_parsed_result(parsed_files[0], all_sources[0])
        st.write(result)


# ─────────────────────────────────────────────────────────────
# 3. INTERACTIVE ARCHITECTURE
# ─────────────────────────────────────────────────────────────

with t3:
    st.header("🏗️ Interactive Software Architecture")
    st.write("Generate an interactive architecture map of your codebase.")

    if st.button("🚀 Generate Architecture", key="architecture"):
        G = build_graph(parsed_files)
        create_animated_architecture(G)


# ─────────────────────────────────────────────────────────────
# 4. EMBEDDINGS
# ─────────────────────────────────────────────────────────────

with t4:
    st.header("🔢 Semantic Embeddings")

    if st.button("Generate Embeddings", key="embeddings"):
        emb = embed_parsed_result(parsed_files[0])
        st.write(emb[:10])


# ─────────────────────────────────────────────────────────────
# 5. TEST GENERATION
# ─────────────────────────────────────────────────────────────

with t5:
    st.header("🧪 Test Generator")

    if st.button("Generate Tests", key="tests"):
        tests = generate_tests_for_file(parsed_files[0], all_sources[0])
        st.code(tests, language="python")


# ─────────────────────────────────────────────────────────────
# 6. REFACTOR
# ─────────────────────────────────────────────────────────────

with t6:
    st.header("🔧 Refactoring Suggestions")

    if st.button("Refactor Code", key="refactor"):
        results = refactor_all_functions(parsed_files[0], all_sources[0])

        if not results:
            st.info("No refactoring suggestions found.")
        else:
            for result in results:
                if "result" in result:
                    refactored = result["result"]
                    if isinstance(refactored, dict) and "refactored_code" in refactored:
                        st.code(refactored["refactored_code"], language="python")
                    else:
                        st.write(refactored)


# ─────────────────────────────────────────────────────────────
# 7. DOCUMENTATION
# ─────────────────────────────────────────────────────────────

with t7:
    st.header("📚 Documentation Generator")

    if st.button("Generate Documentation", key="documentation"):
        readme = generate_readme(parsed_files)
        report = build_complexity_report(parsed_files)

        st.markdown(readme)
        st.divider()
        st.markdown(report)


# ─────────────────────────────────────────────────────────────
# 8. DEPENDENCY GRAPH
# ─────────────────────────────────────────────────────────────

with t8:
    st.header("🔗 Dependency Graph")

    if st.button("Generate Dependency Graph", key="dependency"):
        G = nx.DiGraph()

        for path in file_paths:
            subgraph = build_dependency_graph(path)
            G = nx.compose(G, subgraph)

        os.makedirs("outputs", exist_ok=True)
        output_path = os.path.join("outputs", "dependency.png")

        draw_dependency_graph(G, output_path)

        st.image(output_path)
        st.write("Nodes:", G.number_of_nodes())
        st.write("Edges:", G.number_of_edges())


# ─────────────────────────────────────────────────────────────
# 9. AI CODE EXPLANATION
# ─────────────────────────────────────────────────────────────

with t9:
    st.header("💡 AI Code Explanation")

    if st.button("Explain Code", key="explain"):
        explanation = explain_code(all_sources[0])
        st.write(explanation)


# ─────────────────────────────────────────────────────────────
# 10. MULTI-FILE ANALYSIS
# ─────────────────────────────────────────────────────────────

with t10:
    st.header("🌐 Multi-file Cross Module Analysis")

    if st.button("🚀 Run Full Project Analysis", key="multifile"):
        G = nx.DiGraph()

        for path in file_paths:
            subgraph = build_dependency_graph(path)
            G = nx.compose(G, subgraph)

        os.makedirs("outputs", exist_ok=True)
        output_path = os.path.join("outputs", "multifile.png")

        draw_dependency_graph(G, output_path)
        st.image(output_path)

        cycles = list(nx.simple_cycles(G))

        if cycles:
            st.error("⚠️ Circular Dependencies Found!")
            for cycle in cycles:
                st.write(" ➜ ".join(cycle))
        else:
            st.success("✅ No circular dependencies found.")

        st.success(
            f"Files: {len(file_paths)} | "
            f"Nodes: {G.number_of_nodes()} | "
            f"Edges: {G.number_of_edges()}"
        )


# ─────────────────────────────────────────────────────────────
# 11. AI CODE REVIEW BOT
# ─────────────────────────────────────────────────────────────

with t11:
    st.header("👨‍💻 AI Code Review Bot")

    option = st.selectbox("Choose code to review", ["Full Code", "Paste Custom Code"])

    if option == "Full Code":
        code_to_review = all_sources[0]
    else:
        code_to_review = st.text_area("Paste code here", height=300)

    if st.button("🔍 Review Code", key="code_review"):
        if not code_to_review.strip():
            st.warning("Please provide code to review.")
        else:
            review = review_code(code_to_review)
            st.write(review)


# ─────────────────────────────────────────────────────────────
# 12. TECHNICAL DEBT
# ─────────────────────────────────────────────────────────────

with t12:
    st.header("💰 Technical Debt Calculator")
    st.write("Estimate technical debt based on code structure and complexity.")

    if st.button("Calculate Technical Debt", key="technical_debt"):
        result = calculate_technical_debt(parsed_files)

        c1, c2 = st.columns(2)
        c1.metric("Estimated Hours", f"{result['estimated_hours']} hrs")
        c2.metric("Estimated Cost", f"₹{result['estimated_cost']}")

        st.divider()
        st.subheader("Breakdown")

        st.write(f"Functions: {result['functions']}")
        st.write(f"Classes: {result['classes']}")
        st.write(f"Complexity Penalty: {result['complexity_penalty']} hrs")
        st.write(f"Long Function Penalty: {result['long_function_penalty']} hrs")


# ─────────────────────────────────────────────────────────────
# 13. GITHUB REPOSITORY ANALYZER
# ─────────────────────────────────────────────────────────────

with t13:
    st.markdown("## 🐙 GitHub Repository Analyzer")

    st.write(
        "Enter a public GitHub repository URL. "
        "The repository will be cloned and analyzed."
    )

    github_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repository"
    )

    if st.button("🚀 Analyze GitHub Repository"):

        if not github_url.strip():
            st.warning("Please enter a GitHub repository URL.")
        else:
            try:
                with st.spinner("Cloning GitHub repository..."):
                    repo_path = clone_github_repository(github_url.strip())

                # Save the cloned path so OTHER tabs (Logical Coupling,
                # Risk Hotspots, Change Impact) can reuse it — without this,
                # a fresh click on another tab has no idea a repo was ever
                # cloned, since plain Python variables don't persist across
                # Streamlit reruns.
                st.session_state["github_repo_path"] = repo_path
                st.session_state["github_repo_url"] = github_url.strip()

                st.success("✅ Repository cloned successfully!")

                # ── Repository overview ──────────────────────────
                info = get_repository_info(repo_path)
                overview = get_github_repository_overview(repo_path, github_url)

                st.markdown("### 📊 Repository Overview")

                o1, o2, o3, o4 = st.columns(4)
                o1.metric("Repository", overview["name"])
                o2.metric("Owner", overview["owner"])
                o3.metric("Branch", overview["branch"])
                o4.metric("Total Commits", overview["commit_count"])

                st.write(f"**GitHub URL:** {overview['url']}")

                c1, c2 = st.columns(2)
                c1.metric("Python Files", info["python_files"])
                c2.metric("Total Lines", info["total_lines"])

                # ── Recent commit history ────────────────────────
                st.markdown("### 🕐 Recent Commit History")
                st.caption(
                    "Recent commits from the GitHub repository, "
                    "including author, date, and number of files changed."
                )

                recent_commits = get_recent_commits(repo_path, limit=10)

                if not recent_commits:
                    st.info("No commit history was found in this repository.")
                else:
                    for commit in recent_commits:
                        with st.expander(f"{commit['hash']} — {commit['message']}"):
                            cc1, cc2, cc3 = st.columns(3)
                            cc1.write(f"**Author:** {commit['author']}")
                            cc2.write(f"**Date:** {commit['date']}")
                            cc3.write(f"**Files Changed:** {commit['files_changed']}")

                            if commit["changed_files"]:
                                st.write("**Changed Files:**")
                                for changed_file in commit["changed_files"]:
                                    st.write(f"📄 {changed_file}")
                            else:
                                st.write("No changed-file information available.")

                # ── Python files list ────────────────────────────
                python_files = find_python_files(repo_path)

                st.markdown("### 📁 Python Files Found")

                if not python_files:
                    st.info("No Python files were found in this repository.")
                else:
                    for file_path in python_files:
                        relative_path = os.path.relpath(file_path, repo_path)
                        st.write(f"📄 {relative_path}")

            except Exception as e:
                st.error(f"❌ Repository analysis failed: {e}")


# ─────────────────────────────────────────────────────────────
# 14. LOGICAL COUPLING (git history mining)
# ─────────────────────────────────────────────────────────────

with t14:
    st.markdown("## 🔀 Git History — Logical Coupling")

    st.write(
        "Find files that frequently change together "
        "even when they have no direct dependency."
    )

    coupling_target = st.session_state.get("github_repo_path", BASE_DIR)

    if "github_repo_path" in st.session_state:
        st.caption(f"Analyzing cloned repo: `{coupling_target}`")
    else:
        st.caption(
            "No GitHub repo cloned yet — analyzing this tool's own repo as a fallback. "
            "Clone a repo in the 'GitHub Repository' tab first for meaningful results."
        )

    if st.button("Analyze Git History 🔍"):
        try:
            result = mine_logical_coupling(coupling_target)

            st.metric("Commits Analyzed", result["commits_analyzed"])
            st.metric("Files Analyzed", result["files_analyzed"])

            couplings = result["couplings"]

            if not couplings:
                st.info("No significant logical coupling found.")
            else:
                st.write("### 🔗 Strongest Hidden Relationships")

                for coupling in couplings[:20]:
                    score = coupling["coupling_score"]

                    st.markdown(
                        f"""
                        **{coupling['file_a']}**
                        ↔
                        **{coupling['file_b']}**

                        - Coupling Score: **{score}%**
                        - Changed Together: **{coupling['co_change_count']} times**
                        - {coupling['file_a']} commits: **{coupling['file_a_commits']}**
                        - {coupling['file_b']} commits: **{coupling['file_b_commits']}**
                        """
                    )

                    st.divider()

        except Exception as e:
            st.error(f"Git history analysis failed: {e}")


# ─────────────────────────────────────────────────────────────
# 15. CLONE DETECTION (semantic, embedding-based)
# ─────────────────────────────────────────────────────────────

with t15:
    st.markdown("## 🧬 Code Clone Detection")
    st.caption(
        "Finds duplicate code two different ways: **Semantic** mode catches code "
        "that MEANS the same thing but is written differently (using embeddings). "
        "**Structural** mode catches code that's an exact or near-exact copy with "
        "renamed variables (using AST fingerprinting) — a case embeddings can miss."
    )

    detection_mode = st.radio(
        "Detection mode",
        ["Semantic (meaning-based)", "Structural (exact/renamed copies)"],
        horizontal=True
    )

    if detection_mode == "Semantic (meaning-based)":
        threshold = st.slider("Similarity threshold", 0.70, 0.99, 0.85, 0.01)

        if st.button("Detect Semantic Clones"):
            with st.spinner("Comparing every function pair across all files..."):
                summary = summarize_clones(parsed_files, threshold=threshold)

            c1, c2 = st.columns(2)
            c1.metric("Functions/Classes Scanned", summary["total_functions_classes"])
            c2.metric("Duplication %", f"{summary['duplication_percentage']}%")

            st.divider()
            st.write("### Clone Pairs")

            if not summary["clone_pairs"]:
                st.success("No near-duplicate functions found above this threshold.")

            for p in summary["clone_pairs"]:
                st.warning(
                    f"**{p['a_name']}** ({p['a_file']}:{p['a_line']}) ↔ "
                    f"**{p['b_name']}** ({p['b_file']}:{p['b_line']}) — "
                    f"similarity {p['similarity']}"
                )

            if summary["clone_families"].get("clusters"):
                st.write("### Clone Families (3+ similar functions)")
                for i, family in enumerate(summary["clone_families"]["clusters"], 1):
                    names = ", ".join(f"{m['name']} ({m['file']})" for m in family)
                    st.info(f"Family {i}: {names}")

    else:
        st.caption(
            "Finds functions that are structurally identical — same logic, "
            "different names — using normalized AST fingerprinting."
        )

        if st.button("Detect Structural Clones"):
            with st.spinner("Fingerprinting every function's AST structure..."):
                source_lookup = {
                    parsed.get("file", ""): source
                    for parsed, source in zip(parsed_files, all_sources)
                }
                result = find_structural_clones(parsed_files, source_lookup)

            st.metric("Structural Clone Groups Found", result["total_clone_groups"])

            if result["total_clone_groups"] == 0:
                st.success("No exact structural duplicates found.")

            for i, group in enumerate(result["clone_groups"], 1):
                names = ", ".join(f"{m['name']} ({m['file']}:{m['line']})" for m in group)
                st.warning(f"Clone group {i}: {names}")


# ─────────────────────────────────────────────────────────────
# 16. MODULE BOUNDARY DETECTION (Louvain community detection)
# ─────────────────────────────────────────────────────────────

with t16:
    st.markdown("## 🧩 Automatic Module Boundary Detection")
    st.caption(
        "Uses Louvain community detection on the dependency graph to "
        "suggest how to split this codebase into logical modules."
    )

    if st.button("Detect Module Boundaries"):
        G = nx.DiGraph()

        for path in file_paths:
            sub = build_dependency_graph(path)
            G = nx.compose(G, sub)

        result = analyze_modularity(G)

        if "error" in result:
            st.error(result["error"])
        else:
            c1, c2 = st.columns(2)
            c1.metric("Modularity Score", result["modularity_score"])
            c2.metric("Suggested Modules", result["num_communities"])
            st.info(result["interpretation"])

            st.divider()
            st.write("### Suggested Modules")

            for comm_id, info in result["suggested_modules"].items():
                st.write(
                    f"**{info['suggested_name']}** ({info['size']} members): "
                    f"{', '.join(info['members'])}"
                )


# ─────────────────────────────────────────────────────────────
# 17. RISK HOTSPOT PREDICTION
# ─────────────────────────────────────────────────────────────

with t17:
    st.markdown("## 🔥 Defect Risk Hotspot Prediction")
    st.caption(
        "Combines complexity + git churn + bugfix-commit history to "
        "flag the files most likely to contain bugs."
    )

    risk_target = st.session_state.get("github_repo_path", None)

    if not risk_target:
        st.warning(
            "This feature needs full git history. Clone a repo in the "
            "'GitHub Repository' tab first, then come back here."
        )
    else:
        st.caption(f"Analyzing cloned repo: `{risk_target}`")

        if st.button("Compute Risk Scores"):
            with st.spinner("Analyzing complexity and git history..."):
                results = compute_risk_scores(parsed_files, repo_path=risk_target, max_commits=300)

            for r in results[:25]:
                if r["risk_label"] == "HIGH":
                    color = "error"
                elif r["risk_label"] == "MEDIUM":
                    color = "warning"
                else:
                    color = "success"

                getattr(st, color)(
                    f"**{r['file']}** — risk score {r['risk_score']}/100 "
                    f"[{r['risk_label']}] (complexity: {r['complexity']}, "
                    f"churn: {r['churn']}, bugfix commits: {r['bugfix_count']})"
                )


# ─────────────────────────────────────────────────────────────
# 18. EXECUTION PATH REPLAY (static, safe — no code is run)
# ─────────────────────────────────────────────────────────────

with t18:
    st.markdown("## ▶️ Execution Path Replay (Static)")
    st.caption(
        "Walks the call graph from a chosen entry point and lets you step "
        "through the likely execution order — no code is actually run, so "
        "this is safe even on untrusted uploads."
    )

    G = nx.DiGraph()

    for path in file_paths:
        sub = build_dependency_graph(path)
        G = nx.compose(G, sub)

    if G.number_of_nodes() == 0:
        st.info("No functions found to trace.")
    else:
        entry_point = st.selectbox("Choose entry function", sorted(G.nodes))

        if entry_point:
            result = trace_static_execution_path(G, entry_point)

            if "error" in result:
                st.error(result["error"])
            elif result["total_steps"] == 0:
                st.info(f"'{entry_point}' doesn't call any other tracked functions.")
            else:
                step = st.slider("Step", 0, result["total_steps"], 0)

                os.makedirs("outputs", exist_ok=True)
                output_path = os.path.join("outputs", "exec_step.png")

                draw_execution_step(G, result["steps"], step, output_path)
                st.image(output_path)

                if step > 0:
                    s = result["steps"][step - 1]
                    st.info(f"Step {step}: **{s['from']}** calls **{s['to']}**")


# ─────────────────────────────────────────────────────────────
# 19. NATURAL LANGUAGE CODE SEARCH
# ─────────────────────────────────────────────────────────────

with t19:
    st.markdown("## 🔎 Natural Language Code Search")
    st.caption(
        "Search your codebase in plain English — e.g. 'function that validates "
        "user login' or 'class that handles database connections'. Runs on local "
        "semantic embeddings, no API call needed."
    )

    if (
        "search_engine" not in st.session_state
        or st.session_state.get("search_files_count") != len(parsed_files)
    ):
        with st.spinner("Building semantic search index..."):
            engine = CodeSearchEngine()
            count = engine.build_index(parsed_files)
            st.session_state["search_engine"] = engine
            st.session_state["search_files_count"] = len(parsed_files)
        st.success(f"Indexed {count} functions/classes.")

    engine = st.session_state["search_engine"]

    query = st.text_input(
        "Search query",
        placeholder="e.g. function that connects to database"
    )

    col1, col2 = st.columns(2)

    filter_type = col1.selectbox(
        "Filter by type",
        [None, "function", "class"],
        format_func=lambda x: x or "Any"
    )

    filter_complexity = col2.selectbox(
        "Filter by complexity",
        [None, "low", "medium", "high"],
        format_func=lambda x: x or "Any"
    )

    if query:
        results = engine.search(
            query, top_k=10,
            filter_type=filter_type,
            filter_complexity=filter_complexity
        )

        if not results:
            st.info("No matches found. Try a different phrasing.")

        for r in results:
            st.markdown(
                f"**{r['name']}** ({r['type']}) — `{r['file']}:{r['line']}` "
                f"— similarity {r['similarity']}"
            )
            if r.get("docstring"):
                st.caption(r["docstring"])
            st.divider()

    st.markdown("### 📊 Codebase Stats")

    stats = engine.get_stats()

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Indexed items", stats["total_indexed"])
    sc2.metric("Undocumented", stats["undocumented"])
    sc3.metric("High complexity", stats["high_complexity"])
    sc4.metric("Async functions", stats["async_fns"])

    if st.button("Show Complexity Hotspots"):
        hotspots = engine.get_complexity_hotspots(top_k=5)
        for h in hotspots:
            st.warning(f"**{h['name']}** ({h['file']}:{h['line']}) — complexity {h['complexity']}")


# ─────────────────────────────────────────────────────────────
# 20. CHANGE IMPACT / RIPPLE EFFECT PREDICTOR
# ─────────────────────────────────────────────────────────────

with t20:
    st.markdown("## ⚡ Change Impact / Ripple Predictor")
    st.caption(
        "Pick a file you're about to change — see everything likely to be "
        "affected, both structurally connected AND historically coupled, "
        "ranked by risk. Combines the dependency graph, logical coupling "
        "history, and risk scores into one answer."
    )

    impact_target = st.session_state.get("github_repo_path", None)

    if not impact_target:
        st.warning(
            "This feature needs full git history. Clone a repo in the "
            "'GitHub Repository' tab first, then come back here."
        )
    else:
        G = nx.DiGraph()
        for path in file_paths:
            sub = build_dependency_graph(path)
            G = nx.compose(G, sub)

        if G.number_of_nodes() == 0:
            st.info("No files to analyze.")
        else:
            target_file = st.selectbox("File you're about to change", sorted(G.nodes))

            if st.button("Predict Impact"):
                with st.spinner("Combining structural graph, coupling history, and risk scores..."):
                    result = predict_change_impact(target_file, G, impact_target, parsed_files)

                st.metric("Files Likely Affected", result["total_impacted_files"])

                if result["total_impacted_files"] == 0:
                    st.success("No related files detected — this file appears isolated.")

                for item in result["impacted_files"]:
                    label = item["risk_label"]
                    if label == "HIGH":
                        color = "error"
                    elif label == "MEDIUM":
                        color = "warning"
                    else:
                        color = "success"

                    reasons = "; ".join(item["reasons"])
                    score_text = f"risk {item['risk_score']}/100" if item["risk_score"] is not None else "risk unknown"
                    getattr(st, color)(f"**{item['file']}** ({score_text}) — {reasons}")


# ─────────────────────────────────────────────────────────────
# CLEANUP TEMPORARY FILES
# ─────────────────────────────────────────────────────────────

for path in file_paths:
    try:
        os.unlink(path)
    except Exception:
        pass