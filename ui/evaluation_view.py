"""Evaluation Benchmark View: Authentic test dataset evaluation, baseline vs updated comparison, and charts."""

import streamlit as st
import pandas as pd

from config import DOMAINS, DOMAIN_ICONS
from src.knowledge_base import KnowledgeBase
from src.evaluation_engine import EvaluationBenchmarkEngine
from src.visualizer import create_accuracy_comparison_chart
from ui.components import render_metric_card


def render_evaluation_view(kb: KnowledgeBase):
    st.markdown('<div class="main-header">📈 Evaluation & Diagnostic Benchmark</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Empirical performance evaluation comparing Baseline Knowledge Base vs. Updated Active Knowledge Base</div>', unsafe_allow_html=True)

    eval_engine = EvaluationBenchmarkEngine()

    col_btn, col_info = st.columns([2, 5])
    with col_btn:
        run_benchmark = st.button("🚀 Run Comparative Benchmark Now", type="primary", use_container_width=True)
    with col_info:
        st.caption("Executes all 28 authentic test cases across both the factory Baseline KB and the Expert-Enriched Active KB to measure true accuracy delta.")

    if run_benchmark or "last_benchmark" not in st.session_state:
        with st.spinner("Executing multi-domain backward-chaining evaluation..."):
            benchmark_summary = eval_engine.run_comparative_benchmark()
            st.session_state.last_benchmark = benchmark_summary

    summary = st.session_state.last_benchmark

    # Top Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        base_acc = summary["baseline"]["accuracy"]
        render_metric_card("Baseline Accuracy", f"{base_acc}%", f"{summary['baseline']['correct']}/{summary['baseline']['total']} correct")
    with c2:
        upd_acc = summary["updated"]["accuracy"]
        render_metric_card("Updated KB Accuracy", f"{upd_acc}%", f"{summary['updated']['correct']}/{summary['updated']['total']} correct")
    with c3:
        delta = summary["accuracy_delta"]
        sign = "+" if delta >= 0 else ""
        render_metric_card("Accuracy Improvement", f"{sign}{delta}%", "Real measured delta")
    with c4:
        render_metric_card("Newly Resolved Cases", summary["newly_resolved_count"], "Via approved expert rules")

    st.markdown("---")

    # Interactive Comparison Chart
    st.subheader("Performance Comparison Across Troubleshooting Domains")
    chart = create_accuracy_comparison_chart(summary)
    st.plotly_chart(chart, use_container_width=True)

    st.markdown("---")

    # Domain Breakdown Table
    st.subheader("Domain-by-Domain Accuracy Breakdown")
    domain_rows = []
    for d in DOMAINS:
        b_d = summary["baseline"]["domain_stats"].get(d, {})
        u_d = summary["updated"]["domain_stats"].get(d, {})
        d_delta = round(u_d.get("accuracy", 0.0) - b_d.get("accuracy", 0.0), 2)
        sign_d = "+" if d_delta >= 0 else ""

        domain_rows.append({
            "Domain": f"{DOMAIN_ICONS.get(d, '')} {d}",
            "Test Cases": b_d.get("total", 0),
            "Baseline Correct": b_d.get("correct", 0),
            "Baseline Accuracy": f"{b_d.get('accuracy', 0.0):.1f}%",
            "Updated Correct": u_d.get("correct", 0),
            "Updated Accuracy": f"{u_d.get('accuracy', 0.0):.1f}%",
            "Delta": f"{sign_d}{d_delta}%"
        })

    st.dataframe(pd.DataFrame(domain_rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Detailed Test Case Results Explorer
    st.subheader("Authentic Diagnostic Test Case Results")
    filter_choice = st.radio(
        "Filter Test Results:",
        options=["All Cases", "Newly Resolved Cases by Expert Learning", "Failed / Edge Cases"],
        horizontal=True
    )

    cases_to_show = summary["updated_detailed"]
    if filter_choice == "Newly Resolved Cases by Expert Learning":
        resolved_ids = {c["test_id"] for c in summary["newly_resolved_cases"]}
        cases_to_show = [c for c in cases_to_show if c["test_id"] in resolved_ids]
    elif filter_choice == "Failed / Edge Cases":
        cases_to_show = [c for c in cases_to_show if not c["is_match"]]

    if cases_to_show:
        df_cases = pd.DataFrame(cases_to_show)
        show_cols = ["test_id", "name", "domain", "category", "expected", "predicted", "is_match", "coverage"]
        existing = [c for c in show_cols if c in df_cases.columns]
        st.dataframe(df_cases[existing], use_container_width=True, hide_index=True)
    else:
        st.info("No test cases match this filter.")

    # Historical Benchmark Runs
    st.markdown("---")
    with st.expander("📜 Historical Evaluation Log"):
        history = eval_engine.load_benchmark_history()
        if history:
            st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
        else:
            st.write("No historical runs saved.")
