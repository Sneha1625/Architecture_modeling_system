import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from parser import parse_file, read_file
from analyzer import analyze_parsed_result
from architect import build_graph, draw_graph

st.set_page_config(
    page_title="AI Code Analyzer",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI-Driven Semantic Code Analyzer")
st.markdown("Upload a Python file to analyze its structure, get AI feedback, and view the architecture graph.")

uploaded_file = st.file_uploader("Upload a Python file", type=["py"])

if uploaded_file:
    # Save uploaded file temporarily
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(uploaded_file.getvalue().decode("utf-8"))

    source_code = read_file(temp_path)

    st.subheader("📄 Source Code")
    st.code(source_code, language="python")

    with st.spinner("Parsing code structure..."):
        parsed = parse_file(temp_path)

    # Show parsed structure
    st.subheader("🔍 Parsed Structure")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Functions", len(parsed["functions"]))
        for f in parsed["functions"]:
            st.write(f"• `{f['name']}()` — line {f['line']}")

    with col2:
        st.metric("Classes", len(parsed["classes"]))
        for c in parsed["classes"]:
            st.write(f"• `{c['name']}` — line {c['line']}")

    with col3:
        st.metric("Imports", len(parsed["imports"]))
        for i in parsed["imports"]:
            st.write(f"• `{i}`")

    # AI Analysis
    st.subheader("🤖 AI Analysis")
    with st.spinner("Analyzing with AI..."):
        results = analyze_parsed_result(parsed, source_code)

    for item in results:
        with st.expander(f"Function: {item['name']} (line {item['line']})"):
            st.markdown(item["analysis"])

    # Architecture Graph
    st.subheader("🏗️ Architecture Graph")
    with st.spinner("Building architecture graph..."):
        G = build_graph([parsed])
        graph_path = "outputs/architecture.png"
        draw_graph(G, output_path=graph_path)

    st.image(graph_path, caption="Software Architecture Graph", use_container_width=True)

    # Cleanup
    os.remove(temp_path)

    st.success("✅ Analysis complete!")