"""Diagnosis History View: Browse, inspect, filter, and export previous diagnostic sessions."""

import streamlit as st
import pandas as pd
import json

from config import DOMAINS
from src.history_manager import DiagnosisHistoryManager
from ui.components import render_metric_card


def render_history_view():
    st.markdown('<div class="main-header">📜 Diagnosis Session History</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Persistent audit log of diagnostic sessions, observed symptoms, and outcomes</div>', unsafe_allow_html=True)

    mgr = DiagnosisHistoryManager()
    records = mgr.load_history()

    # Filter row
    col_domain, col_status, col_clear = st.columns([3, 3, 2])
    with col_domain:
        domain_filter = st.selectbox("Filter Domain:", options=["All Domains"] + DOMAINS)
    with col_status:
        status_filter = st.selectbox(
            "Filter Status:",
            options=["All Statuses", "CONFIRMED", "POSSIBLE", "INSUFFICIENT_EVIDENCE", "CONFLICTING_EVIDENCE", "NO_MATCH"]
        )
    with col_clear:
        st.write("")
        st.write("")
        if st.button("🗑️ Clear History Log"):
            mgr.clear_history()
            st.success("History cleared.")
            st.rerun()

    filtered_records = mgr.get_records(domain_filter=domain_filter, status_filter=status_filter)

    # Top metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Total Sessions Logged", len(records))
    with c2:
        render_metric_card("Matching Sessions", len(filtered_records))
    with c3:
        confirmed_count = len([r for r in filtered_records if r.get("status") == "CONFIRMED"])
        render_metric_card("Confirmed Diagnoses", confirmed_count)

    st.markdown("---")

    if not filtered_records:
        st.info("No diagnostic sessions match the selected filter.")
        return

    # Table preview
    df_table = pd.DataFrame(filtered_records)
    cols = ["timestamp", "domain", "status", "primary_diagnosis", "facts_answered_count", "user_notes"]
    existing_cols = [c for c in cols if c in df_table.columns]
    st.dataframe(df_table[existing_cols], use_container_width=True, hide_index=True)

    # Export options
    col_dl_json, col_dl_csv = st.columns(2)
    with col_dl_json:
        json_data = json.dumps(filtered_records, indent=2)
        st.download_button(
            "📥 Download Filtered Log (JSON)",
            data=json_data,
            file_name="diagnosis_history.json",
            mime="application/json",
            use_container_width=True
        )
    with col_dl_csv:
        csv_data = df_table[existing_cols].to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Filtered Log (CSV)",
            data=csv_data,
            file_name="diagnosis_history.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("Detailed Session Inspector")

    for rec in filtered_records[:10]:  # Show top 10
        with st.expander(f"Session {rec['session_id']} &bull; {rec['timestamp']} &bull; {rec['primary_diagnosis']}"):
            st.markdown(f"**Domain:** {rec['domain']} | **Status:** `{rec['status']}`")
            if rec.get("user_notes"):
                st.markdown(f"**Notes:** *{rec['user_notes']}*")

            col_facts, col_derived = st.columns(2)
            with col_facts:
                st.write("**Observed User Symptoms:**")
                facts = rec.get("user_facts", {})
                for k, v in facts.items():
                    st.write(f"- `{k}`: **{v}**")

            with col_derived:
                st.write("**Derived Intermediate Facts:**")
                derived = rec.get("derived_facts", {})
                if derived:
                    for k, v in derived.items():
                        st.write(f"- `{k}`: **{v}**")
                else:
                    st.write("None derived.")

            if rec.get("primary_solution"):
                st.write("**Recommended Solution:**")
                st.info(rec["primary_solution"])
