"""
FINAL APP.PY
AI Code Analyzer - 13 Features
Includes Interactive Animated Architecture Diagram
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

# Also try loading src/.env if it exists
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

    # ---------------------------------------------------------
    # CHECK GRAPH
    # ---------------------------------------------------------

    if G.number_of_nodes() == 0:
        st.warning("No architecture nodes found.")
        return

    # ---------------------------------------------------------
    # GENERATE GRAPH POSITIONS
    # ---------------------------------------------------------

    pos = nx.spring_layout(
        G,
        seed=42,
        k=2.0,
        iterations=100
    )

    nodes = list(G.nodes())

    # ---------------------------------------------------------
    # CREATE EDGES
    # ---------------------------------------------------------

    edge_x = []
    edge_y = []

    for source, target in G.edges():

        if source not in pos or target not in pos:
            continue

        x0, y0 = pos[source]
        x1, y1 = pos[target]

        edge_x.extend([
            x0,
            x1,
            None
        ])

        edge_y.extend([
            y0,
            y1,
            None
        ])

    # ---------------------------------------------------------
    # EDGE TRACE
    # ---------------------------------------------------------

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(
            width=1.5
        ),
        hoverinfo="none"
    )

    # ---------------------------------------------------------
    # NODE DATA
    # ---------------------------------------------------------

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
            f"<b>{node}</b><br>"
            f"Connections: {degree}"
        )

    # ---------------------------------------------------------
    # NODE TRACE
    # ---------------------------------------------------------

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        hovertext=node_hover,
        hoverinfo="text",
        marker=dict(
            size=28,
            line=dict(
                width=2
            )
        )
    )

    # ---------------------------------------------------------
    # CREATE ANIMATION FRAMES
    # ---------------------------------------------------------

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
                f"<b>{node}</b><br>"
                f"Connections: {G.degree(node)}"
            )

        # Show only edges where both nodes are already visible
        visible_edge_x = []
        visible_edge_y = []

        visible_set = set(visible_nodes)

        for source, target in G.edges():

            if source in visible_set and target in visible_set:

                x0, y0 = pos[source]
                x1, y1 = pos[target]

                visible_edge_x.extend([
                    x0,
                    x1,
                    None
                ])

                visible_edge_y.extend([
                    y0,
                    y1,
                    None
                ])

        frame = go.Frame(
            name=f"frame{step}",
            data=[
                go.Scatter(
                    x=visible_edge_x,
                    y=visible_edge_y,
                    mode="lines",
                    line=dict(
                        width=1.5
                    ),
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
                    marker=dict(
                        size=28,
                        line=dict(
                            width=2
                        )
                    )
                )
            ]
        )

        frames.append(frame)

    # ---------------------------------------------------------
    # CREATE FIGURE
    # ---------------------------------------------------------

    fig = go.Figure(
        data=[
            edge_trace,
            node_trace
        ],
        frames=frames
    )

    # ---------------------------------------------------------
    # LAYOUT
    # ---------------------------------------------------------

    fig.update_layout(

        title=dict(
            text="🏗️ Interactive Software Architecture",
            x=0.5,
            xanchor="center"
        ),

        showlegend=False,

        hovermode="closest",

        height=700,

        margin=dict(
            b=20,
            l=20,
            r=20,
            t=100
        ),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),

        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),

        # -----------------------------------------------------
        # ANIMATION BUTTON
        # -----------------------------------------------------

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
                            [f"frame{i}" for i in range(
                                1,
                                len(nodes) + 1
                            )],
                            {
                                "frame": {
                                    "duration": 700,
                                    "redraw": True
                                },
                                "transition": {
                                    "duration": 400
                                },
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
                                "frame": {
                                    "duration": 500,
                                    "redraw": True
                                },
                                "transition": {
                                    "duration": 300
                                }
                            }
                        ]
                    )
                ]
            )
        ]
    )

    # ---------------------------------------------------------
    # DISPLAY GRAPH
    # ---------------------------------------------------------

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------------------------------------------------
    # EXPLANATION
    # ---------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Modules",
        G.number_of_nodes()
    )

    col2.metric(
        "Dependencies",
        G.number_of_edges()
    )

    if G.number_of_nodes() > 0:

        density = nx.density(G)

    else:

        density = 0

    col3.metric(
        "Graph Density",
        f"{density:.2f}"
    )

    st.info(
        "💡 Click 'Build Architecture' to see the architecture "
        "appear step-by-step. Hover over modules to inspect "
        "their connections. You can also zoom and drag the diagram."
    )


# ─────────────────────────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────────────────────────

uploaded_files = st.file_uploader(
    "📂 Upload Python files (multiple files supported)",
    type=["py"],
    accept_multiple_files=True
)


if not uploaded_files:

    st.info(
        "Upload at least one Python file to start the analysis."
    )

    st.stop()


# ─────────────────────────────────────────────────────────────
# SAVE UPLOADED FILES
# ─────────────────────────────────────────────────────────────

file_paths = []

for uploaded_file in uploaded_files:

    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".py"
    )

    tmp.write(
        uploaded_file.getvalue()
    )

    tmp.close()

    file_paths.append(
        tmp.name
    )


# ─────────────────────────────────────────────────────────────
# PARSE FILES
# ─────────────────────────────────────────────────────────────

parsed_files = []
all_sources = []

for path in file_paths:

    parsed_files.append(
        parse_file(path)
    )

    all_sources.append(
        read_file(path)
    )


# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────

total_functions = sum(
    get_summary(parsed)["total_functions"]
    for parsed in parsed_files
)

total_classes = sum(
    get_summary(parsed)["total_classes"]
    for parsed in parsed_files
)

total_imports = sum(
    get_summary(parsed)["total_imports"]
    for parsed in parsed_files
)


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Functions",
    total_functions
)

c2.metric(
    "Classes",
    total_classes
)

c3.metric(
    "Imports",
    total_imports
)

c4.metric(
    "Files",
    len(file_paths)
)


st.divider()


# ─────────────────────────────────────────────────────────────
# 13 FEATURES
# ─────────────────────────────────────────────────────────────

tabs = st.tabs([

    "💻 Code",

    "🌳 AST",

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

     "🔀 Logical Coupling"

])


(
    t1,
    t2,
    t3,
    t4,
    t5,
    t6,
    t7,
    t8,
    t9,
    t10,
    t11,
    t12,
    t13,
    t14,
    t15
) = tabs


# ─────────────────────────────────────────────────────────────
# 1. CODE VIEWER
# ─────────────────────────────────────────────────────────────

with t1:

    st.header("💻 Source Code")

    for i, code in enumerate(all_sources):

        st.subheader(
            f"File {i + 1}"
        )

        st.code(
            code,
            language="python"
        )


# ─────────────────────────────────────────────────────────────
# 2. AST
# ─────────────────────────────────────────────────────────────

with t2:

    st.header("🌳 Abstract Syntax Tree")

    st.json(
        parsed_files
    )


# ─────────────────────────────────────────────────────────────
# 3. AI ANALYSIS
# ─────────────────────────────────────────────────────────────

with t3:

    st.header("🤖 AI Code Analysis")

    if st.button(
        "Run AI Analysis",
        key="ai_analysis"
    ):

        result = analyze_parsed_result(
            parsed_files[0],
            all_sources[0]
        )

        st.write(
            result
        )


# ─────────────────────────────────────────────────────────────
# 4. INTERACTIVE ARCHITECTURE
# ─────────────────────────────────────────────────────────────

with t4:

    st.header(
        "🏗️ Interactive Software Architecture"
    )

    st.write(
        "Generate an interactive architecture map of your codebase."
    )

    if st.button(
        "🚀 Generate Architecture",
        key="architecture"
    ):

        G = build_graph(
            parsed_files
        )

        create_animated_architecture(
            G
        )


# ─────────────────────────────────────────────────────────────
# 5. EMBEDDINGS
# ─────────────────────────────────────────────────────────────

with t5:

    st.header("🔢 Semantic Embeddings")

    if st.button(
        "Generate Embeddings",
        key="embeddings"
    ):

        emb = embed_parsed_result(
            parsed_files[0]
        )

        st.write(
            emb[:10]
        )


# ─────────────────────────────────────────────────────────────
# 6. TEST GENERATION
# ─────────────────────────────────────────────────────────────

with t6:

    st.header("🧪 Test Generator")

    if st.button(
        "Generate Tests",
        key="tests"
    ):

        tests = generate_tests_for_file(
            parsed_files[0],
            all_sources[0]
        )

        st.code(
            tests,
            language="python"
        )


# ─────────────────────────────────────────────────────────────
# 7. REFACTOR
# ─────────────────────────────────────────────────────────────

with t7:

    st.header("🔧 Refactoring Suggestions")

    if st.button(
        "Refactor Code",
        key="refactor"
    ):

        results = refactor_all_functions(
            parsed_files[0],
            all_sources[0]
        )

        if not results:

            st.info(
                "No refactoring suggestions found."
            )

        else:

            for result in results:

                if "result" in result:

                    refactored = result["result"]

                    if isinstance(
                        refactored,
                        dict
                    ) and "refactored_code" in refactored:

                        st.code(
                            refactored["refactored_code"],
                            language="python"
                        )

                    else:

                        st.write(
                            refactored
                        )


# ─────────────────────────────────────────────────────────────
# 8. DOCUMENTATION
# ─────────────────────────────────────────────────────────────

with t8:

    st.header("📚 Documentation Generator")

    if st.button(
        "Generate Documentation",
        key="documentation"
    ):

        readme = generate_readme(
            parsed_files
        )

        report = build_complexity_report(
            parsed_files
        )

        st.markdown(
            readme
        )

        st.divider()

        st.markdown(
            report
        )


# ─────────────────────────────────────────────────────────────
# 9. DEPENDENCY GRAPH
# ─────────────────────────────────────────────────────────────

with t9:

    st.header(
        "🔗 Dependency Graph"
    )

    if st.button(
        "Generate Dependency Graph",
        key="dependency"
    ):

        G = nx.DiGraph()

        for path in file_paths:

            subgraph = build_dependency_graph(
                path
            )

            G = nx.compose(
                G,
                subgraph
            )

        os.makedirs(
            "outputs",
            exist_ok=True
        )

        output_path = os.path.join(
            "outputs",
            "dependency.png"
        )

        draw_dependency_graph(
            G,
            output_path
        )

        st.image(
            output_path
        )

        st.write(
            "Nodes:",
            G.number_of_nodes()
        )

        st.write(
            "Edges:",
            G.number_of_edges()
        )


# ─────────────────────────────────────────────────────────────
# 10. AI CODE EXPLANATION
# ─────────────────────────────────────────────────────────────

with t10:

    st.header(
        "💡 AI Code Explanation"
    )

    if st.button(
        "Explain Code",
        key="explain"
    ):

        explanation = explain_code(
            all_sources[0]
        )

        st.write(
            explanation
        )


# ─────────────────────────────────────────────────────────────
# 11. MULTI-FILE ANALYSIS
# ─────────────────────────────────────────────────────────────

with t11:

    st.header(
        "🌐 Multi-file Cross Module Analysis"
    )

    if st.button(
        "🚀 Run Full Project Analysis",
        key="multifile"
    ):

        G = nx.DiGraph()

        for path in file_paths:

            subgraph = build_dependency_graph(
                path
            )

            G = nx.compose(
                G,
                subgraph
            )

        os.makedirs(
            "outputs",
            exist_ok=True
        )

        output_path = os.path.join(
            "outputs",
            "multifile.png"
        )

        draw_dependency_graph(
            G,
            output_path
        )

        st.image(
            output_path
        )

        cycles = list(
            nx.simple_cycles(G)
        )

        if cycles:

            st.error(
                "⚠️ Circular Dependencies Found!"
            )

            for cycle in cycles:

                st.write(
                    " ➜ ".join(cycle)
                )

        else:

            st.success(
                "✅ No circular dependencies found."
            )

        st.success(
            f"Files: {len(file_paths)} | "
            f"Nodes: {G.number_of_nodes()} | "
            f"Edges: {G.number_of_edges()}"
        )


# ─────────────────────────────────────────────────────────────
# 12. AI CODE REVIEW BOT
# ─────────────────────────────────────────────────────────────

with t12:

    st.header(
        "👨‍💻 AI Code Review Bot"
    )

    option = st.selectbox(
        "Choose code to review",
        [
            "Full Code",
            "Paste Custom Code"
        ]
    )

    if option == "Full Code":

        code_to_review = all_sources[0]

    else:

        code_to_review = st.text_area(
            "Paste code here",
            height=300
        )

    if st.button(
        "🔍 Review Code",
        key="code_review"
    ):

        if not code_to_review.strip():

            st.warning(
                "Please provide code to review."
            )

        else:

            review = review_code(
                code_to_review
            )

            st.write(
                review
            )


# ─────────────────────────────────────────────────────────────
# 13. TECHNICAL DEBT
# ─────────────────────────────────────────────────────────────

with t13:

    st.header(
        "💰 Technical Debt Calculator"
    )

    st.write(
        "Estimate technical debt based on code structure "
        "and complexity."
    )

    if st.button(
        "Calculate Technical Debt",
        key="technical_debt"
    ):

        result = calculate_technical_debt(
            parsed_files
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "Estimated Hours",
            f"{result['estimated_hours']} hrs"
        )

        c2.metric(
            "Estimated Cost",
            f"₹{result['estimated_cost']}"
        )

        st.divider()

        st.subheader(
            "Breakdown"
        )

        st.write(
            f"Functions: {result['functions']}"
        )

        st.write(
            f"Classes: {result['classes']}"
        )

        st.write(
            f"Complexity Penalty: "
            f"{result['complexity_penalty']} hrs"
        )

        st.write(
            f"Long Function Penalty: "
            f"{result['long_function_penalty']} hrs"
        )

# ───── 14 GITHUB REPOSITORY ANALYZER ─────

with t14:

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

            st.warning(
                "Please enter a GitHub repository URL."
            )

        else:

            try:

                with st.spinner(
                    "Cloning GitHub repository..."
                ):

                    repo_path = clone_github_repository(
                        github_url.strip()
                    )

                st.success(
                    "✅ Repository cloned successfully!"
                )

                # Repository information
                info = get_repository_info(
                    repo_path
                )

                st.markdown(
                    "### 📊 Repository Overview"
                )

                c1, c2 = st.columns(2)

                c1.metric(
                    "Python Files",
                    info["python_files"]
                )

                c2.metric(
                    "Total Lines",
                    info["total_lines"]
                )

                # List Python files
                python_files = find_python_files(
                    repo_path
                )

                st.markdown(
                    "### 📁 Python Files Found"
                )

                for file_path in python_files:

                    relative_path = os.path.relpath(
                        file_path,
                        repo_path
                    )

                    st.write(
                        f"📄 {relative_path}"
                    )

            except Exception as e:

                st.error(
                    f"❌ Repository analysis failed: {e}"
                )
with t15:
    st.markdown("## 🔀 Git History — Logical Coupling")

st.write(
    "Find files that frequently change together "
    "even when they have no direct dependency."
)

if st.button("Analyze Git History 🔍"):

    try:

        result = mine_logical_coupling(
            BASE_DIR
        )

        st.metric(
            "Commits Analyzed",
            result["commits_analyzed"]
        )

        st.metric(
            "Files Analyzed",
            result["files_analyzed"]
        )

        couplings = result["couplings"]

        if not couplings:

            st.info(
                "No significant logical coupling found."
            )

        else:

            st.write(
                "### 🔗 Strongest Hidden Relationships"
            )

            for coupling in couplings[:20]:

                score = coupling["coupling_score"]

                st.markdown(
                    f"""
                    **{coupling['file_a']}**
                    ↔
                    **{coupling['file_b']}**

                    - Coupling Score: **{score}%**
                    - Changed Together: **{coupling['co_change_count']} times**
                    - {coupling['file_a']} commits:
                      **{coupling['file_a_commits']}**
                    - {coupling['file_b']} commits:
                      **{coupling['file_b_commits']}**
                    """
                )

                st.divider()

    except Exception as e:

        st.error(
            f"Git history analysis failed: {e}"
        )

# ─────────────────────────────────────────────────────────────
# CLEANUP TEMPORARY FILES
# ─────────────────────────────────────────────────────────────

for path in file_paths:

    try:

        os.unlink(path)

    except Exception:

        pass