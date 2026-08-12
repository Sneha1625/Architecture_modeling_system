import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise Exception("❌ GROQ API KEY NOT FOUND")

client = Groq(api_key=api_key)


# ─────────────────────────────────────────────────────────────
# 3. AI ANALYSIS
# ─────────────────────────────────────────────────────────────

if page == "🤖 AI Analysis":
    require_uploaded_files()

    st.header("🤖 AI Code Analysis")
    st.caption(
        "AI-powered analysis of syntax, semantics, logic, runtime risks, "
        "quality and possible improvements."
    )

    # ---------------------------------------------------------
    # FILE SELECTION
    # ---------------------------------------------------------

    file_names = [item["name"] for item in uploaded_files]

    selected_index = st.selectbox(
        "📄 Select file to analyze",
        range(len(file_names)),
        format_func=lambda i: file_names[i],
        key="ai_selected_file",
    )

    selected_file = file_names[selected_index]
    selected_code = all_sources[selected_index]
    selected_parsed = parsed_files[selected_index]

    st.markdown(
        f"""
        <div class="ai-file-card">
            <div class="ai-file-title">📄 {selected_file}</div>
            <div class="ai-file-subtitle">
                Ready for intelligent analysis
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # ANALYSIS BUTTON
    # ---------------------------------------------------------

    analyze_ai = st.button(
        "🤖 Run Complete AI Analysis",
        use_container_width=True,
        type="primary",
        key="run_complete_ai_analysis",
    )

    if analyze_ai:

        with st.spinner("🧠 AI is analyzing your code..."):

            try:
                result = analyze_parsed_result(
                    selected_parsed,
                    selected_code
                )

                # Store result so it remains available
                # during Streamlit reruns.
                st.session_state["ai_analysis_result"] = result
                st.session_state["ai_analysis_file"] = selected_file

            except Exception as e:
                st.error(
                    f"❌ AI analysis failed: {e}"
                )
                st.stop()

    # ---------------------------------------------------------
    # SHOW RESULT
    # ---------------------------------------------------------

    if "ai_analysis_result" not in st.session_state:

        st.info(
            "👆 Click **Run Complete AI Analysis** to analyze "
            "the selected Python file."
        )

        st.markdown("### 🔍 What will be analyzed")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("### 🧠 Semantics")
            st.caption(
                "Understand what the code is trying to do "
                "and identify meaning-related problems."
            )

        with c2:
            st.markdown("### ⚠️ Problems")
            st.caption(
                "Identify possible syntax, runtime, logical "
                "and quality issues."
            )

        with c3:
            st.markdown("### 💡 Improvements")
            st.caption(
                "Get AI-generated suggestions for cleaner "
                "and more maintainable code."
            )

        st.stop()

    result = st.session_state["ai_analysis_result"]

    # ---------------------------------------------------------
    # RESULT HEADER
    # ---------------------------------------------------------

    st.success(
        f"✅ Analysis completed for `{selected_file}`"
    )

    st.markdown("## 📊 Analysis Overview")

    # ---------------------------------------------------------
    # NORMALIZE AI RESULT
    # ---------------------------------------------------------

    if isinstance(result, dict):

        # Try to obtain common fields from different
        # possible analyzer response formats.

        summary = result.get(
            "summary",
            result.get("analysis", "")
        )

        issues = result.get(
            "issues",
            result.get("errors", [])
        )

        suggestions = result.get(
            "suggestions",
            result.get("recommendations", [])
        )

        explanation = result.get(
            "explanation",
            result.get("details", "")
        )

    else:

        # If the existing analyzer returns plain text,
        # don't break the UI.

        summary = str(result)
        issues = []
        suggestions = []
        explanation = ""

    # ---------------------------------------------------------
    # SCORE / STATUS CARDS
    # ---------------------------------------------------------

    total_issues = len(issues) if isinstance(issues, list) else 0
    total_suggestions = (
        len(suggestions)
        if isinstance(suggestions, list)
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🔍 Issues",
            total_issues
        )

    with c2:
        st.metric(
            "💡 Suggestions",
            total_suggestions
        )

    with c3:
        st.metric(
            "📄 Lines",
            len(selected_code.splitlines())
        )

    with c4:
        st.metric(
            "📦 File",
            selected_file
        )

    st.divider()

    # ---------------------------------------------------------
    # EXECUTIVE SUMMARY
    # ---------------------------------------------------------

    st.subheader("🧠 AI Summary")

    if summary:

        if isinstance(summary, (dict, list)):
            st.json(summary)
        else:
            st.markdown(str(summary))

    else:
        st.info(
            "The AI did not return a separate summary."
        )

    # ---------------------------------------------------------
    # ISSUES
    # ---------------------------------------------------------

    st.subheader("🚨 Issues Detected")

    if issues:

        if isinstance(issues, list):

            for i, issue in enumerate(issues, 1):

                if isinstance(issue, dict):

                    issue_type = issue.get(
                        "type",
                        issue.get(
                            "category",
                            "Issue"
                        )
                    )

                    severity = issue.get(
                        "severity",
                        "Medium"
                    )

                    line = issue.get(
                        "line",
                        issue.get(
                            "line_number",
                            "N/A"
                        )
                    )

                    description = issue.get(
                        "description",
                        issue.get(
                            "problem",
                            str(issue)
                        )
                    )

                    fix = issue.get(
                        "fix",
                        issue.get(
                            "suggestion",
                            ""
                        )
                    )

                    with st.expander(
                        f"🚨 Issue {i} — {issue_type} | "
                        f"{severity} | Line {line}"
                    ):

                        st.markdown(
                            f"**Problem:** {description}"
                        )

                        if fix:
                            st.markdown(
                                f"**💡 Suggested Fix:** {fix}"
                            )

                else:

                    with st.expander(
                        f"🚨 Issue {i}"
                    ):
                        st.write(issue)

        else:
            st.write(issues)

    else:

        st.success(
            "✅ No structured issues were returned by the AI."
        )

    # ---------------------------------------------------------
    # SUGGESTIONS
    # ---------------------------------------------------------

    st.subheader("💡 AI Improvement Suggestions")

    if suggestions:

        if isinstance(suggestions, list):

            for i, suggestion in enumerate(
                suggestions,
                1
            ):

                if isinstance(suggestion, dict):

                    title = suggestion.get(
                        "title",
                        f"Suggestion {i}"
                    )

                    description = suggestion.get(
                        "description",
                        suggestion.get(
                            "suggestion",
                            str(suggestion)
                        )
                    )

                    with st.expander(
                        f"💡 {title}"
                    ):
                        st.write(description)

                else:

                    st.markdown(
                        f"**{i}.** {suggestion}"
                    )

        else:
            st.write(suggestions)

    else:

        st.info(
            "No structured improvement suggestions "
            "were returned."
        )

    # ---------------------------------------------------------
    # CODE EXPLANATION
    # ---------------------------------------------------------

    if explanation:

        st.subheader("📖 AI Explanation")

        with st.expander(
            "Show detailed explanation",
            expanded=True
        ):
            if isinstance(
                explanation,
                (dict, list)
            ):
                st.json(explanation)
            else:
                st.markdown(
                    str(explanation)
                )

    # ---------------------------------------------------------
    # SOURCE CODE
    # ---------------------------------------------------------

    st.subheader("💻 Analyzed Source Code")

    with st.expander(
        "View source code"
    ):
        st.code(
            selected_code,
            language="python"
        )

    # ---------------------------------------------------------
    # RUN AGAIN
    # ---------------------------------------------------------

    st.divider()

    if st.button(
        "🔄 Clear AI Analysis & Run Again",
        key="clear_ai_analysis"
    ):

        st.session_state.pop(
            "ai_analysis_result",
            None
        )

        st.rerun()