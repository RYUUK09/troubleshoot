"""Knowledge Base Explorer View: Search, filter, inspect rules, conditions, and solutions."""

import streamlit as st
import pandas as pd

from config import DOMAINS, DOMAIN_ICONS
from src.knowledge_base import KnowledgeBase
from ui.components import render_metric_card


def render_kb_explorer_view(kb: KnowledgeBase):
    st.markdown('<div class="main-header">📚 Knowledge Base Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Inspect expert rules, intermediate derivations, condition sets, and remediation procedures</div>', unsafe_allow_html=True)

    # Filter controls
    col_domain, col_type, col_search = st.columns([2, 2, 3])

    with col_domain:
        domain = st.selectbox("Select Domain:", options=["All Domains"] + DOMAINS)

    with col_type:
        rule_type = st.selectbox("Rule Classification:", options=["All Types", "Final Diagnostic Rules", "Intermediate Fact Derivations"])

    with col_search:
        search_query = st.text_input("🔍 Search Rule ID, Condition, or Diagnosis:", placeholder="e.g. DNS, battery, R-IOT...")

    # Filter rules
    rules = kb.rules
    if domain != "All Domains":
        rules = [r for r in rules if r.domain == domain]

    if rule_type == "Final Diagnostic Rules":
        rules = [r for r in rules if not r.is_intermediate_rule]
    elif rule_type == "Intermediate Fact Derivations":
        rules = [r for r in rules if r.is_intermediate_rule]

    if search_query:
        q = search_query.strip().lower()
        rules = [
            r for r in rules
            if q in r.rule_id.lower()
            or (r.diagnosis and q in r.diagnosis.lower())
            or (r.intermediate_fact and q in r.intermediate_fact.lower())
            or any(q in c.fact.lower() or q in c.description.lower() for c in r.conditions)
        ]

    # Metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Displayed Rules", len(rules), f"Out of {len(kb.rules)} total in KB")
    with c2:
        diagnostic_cnt = len([r for r in rules if not r.is_intermediate_rule])
        render_metric_card("Diagnostic Rules", diagnostic_cnt)
    with c3:
        inter_cnt = len([r for r in rules if r.is_intermediate_rule])
        render_metric_card("Intermediate Rules", inter_cnt)

    st.markdown("---")

    # Integrity Check Button
    with st.expander("🛠️ Knowledge Base Integrity & Graph Verification"):
        integrity = kb.validate_integrity()
        if integrity["valid"]:
            st.success(f"✅ Knowledge Base graph is consistent. All {integrity['total_rules']} rules validated without circular deadlocks or orphaned conditions.")
        else:
            st.error(f"❌ Consistency issues detected: {integrity['issues']}")

    # Render Rule Cards
    st.subheader(f"Rules Catalog ({len(rules)})")

    if not rules:
        st.info("No rules match the current filter criteria.")
        return

    for r in rules:
        with st.container():
            is_inter = r.is_intermediate_rule
            badge_color = "#3b82f6" if not is_inter else "#8b5cf6"
            rule_kind = "FINAL DIAGNOSIS" if not is_inter else "INTERMEDIATE DERIVATION"

            st.markdown(f"""
                <div class="rule-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:700; font-size:1.1rem; color:#1e293b;">{r.rule_id}</span>
                        <span style="background-color:{badge_color}22; color:{badge_color}; padding:0.2rem 0.6rem; border-radius:6px; font-weight:700; font-size:0.75rem;">
                            {rule_kind}
                        </span>
                    </div>
                    <div style="font-size:0.85rem; color:#64748b; margin:0.3rem 0;">
                        <b>Domain:</b> {r.domain} | <b>Author:</b> {r.author}
                    </div>
                    <h4 style="color:#0f172a; margin:0.4rem 0;">
                        {r.diagnosis if not is_inter else 'Derives: ' + (r.intermediate_fact or '')}
                    </h4>
                    <p style="font-size:0.9rem; color:#334155;">{r.explanation}</p>
                </div>
            """, unsafe_allow_html=True)

            with st.expander(f"View Conditions & Solution for {r.rule_id}"):
                st.write("**Conditions Required:**")
                for c in r.conditions:
                    inter_marker = " *(Intermediate Fact)*" if c.is_intermediate else ""
                    st.write(f"- `{c.fact}` must be **{c.expected_value}** — *\"{c.description}\"*{inter_marker}")

                if not is_inter and r.solution:
                    st.write("**Recommended Solution:**")
                    st.info(r.solution)
