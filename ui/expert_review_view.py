"""Expert Review View: Governance workflow for proposing, validating, approving, and integrating rules."""

import streamlit as st
import pandas as pd
from datetime import datetime

from config import DOMAINS, STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED
from src.knowledge_base import KnowledgeBase
from src.expert_review import ExpertReviewManager
from ui.components import render_metric_card


def render_expert_review_view(kb: KnowledgeBase):
    st.markdown('<div class="main-header">🛡️ Expert Review & Knowledge-Base Learning</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Controlled rule governance, duplicate detection, expert approval, and active KB enrichment</div>', unsafe_allow_html=True)

    manager = ExpertReviewManager()

    tab_submit, tab_pending, tab_archive = st.tabs([
        "📝 Submit New Diagnostic Rule",
        f"⏳ Pending Review ({len(manager.get_proposals(status=STATUS_PENDING))})",
        "📂 Proposal Audit Archive"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: SUBMIT NEW RULE
    # -------------------------------------------------------------------------
    with tab_submit:
        st.subheader("Propose a Novel Diagnostic Rule")
        st.markdown("All submissions undergo input validation, duplicate detection, and expert peer approval before integration.")

        with st.form("rule_submission_form", clear_on_submit=False):
            col_id, col_dom = st.columns(2)
            with col_id:
                prop_rule_id = st.text_input("Rule ID (Unique):", placeholder="e.g. R-NET-EXP-002")
            with col_dom:
                prop_domain = st.selectbox("Domain:", options=DOMAINS)

            col_diag, col_author = st.columns(2)
            with col_diag:
                prop_diag = st.text_input("Diagnosis Name:", placeholder="e.g. High Latency Wi-Fi Roaming Thrashing")
            with col_author:
                prop_author = st.text_input("Proposer / Expert Name:", placeholder="e.g. Dr. Jane Doe (Network Specialist)")

            prop_explanation = st.text_area("Clinical / Technical Explanation:", placeholder="Why does this fault occur under these conditions?")
            prop_solution = st.text_area("Actionable Remediation Solution:", placeholder="1. Step one...\n2. Step two...")

            st.write("**Rule Conditions (Observable Symptoms):**")
            st.caption("Define at least 2 conditions for the diagnostic rule.")

            c_col1, c_col2, c_col3 = st.columns([3, 2, 4])
            with c_col1:
                cond1_fact = st.text_input("Condition #1 Fact ID:", placeholder="e.g. wifi_roaming_drops", key="c1_f")
            with c_col2:
                cond1_val = st.selectbox("Expected Value #1:", options=["YES", "NO"], key="c1_v")
            with c_col3:
                cond1_desc = st.text_input("Condition #1 Question Text:", placeholder="Does connection disconnect during roaming?", key="c1_d")

            c2_col1, c2_col2, c2_col3 = st.columns([3, 2, 4])
            with c2_col1:
                cond2_fact = st.text_input("Condition #2 Fact ID:", placeholder="e.g. ap_rssi_overlap_high", key="c2_f")
            with c2_col2:
                cond2_val = st.selectbox("Expected Value #2:", options=["YES", "NO"], key="c2_v")
            with c2_col3:
                cond2_desc = st.text_input("Condition #2 Question Text:", placeholder="Are dual APs transmitting on identical BSSID?", key="c2_d")

            submit_btn = st.form_submit_button("🚀 Submit Proposal for Expert Review", type="primary")

            if submit_btn:
                conditions = []
                if cond1_fact:
                    conditions.append({"fact": cond1_fact.strip().lower(), "expected_value": cond1_val, "description": cond1_desc or cond1_fact})
                if cond2_fact:
                    conditions.append({"fact": cond2_fact.strip().lower(), "expected_value": cond2_val, "description": cond2_desc or cond2_fact})

                payload = {
                    "rule_id": prop_rule_id,
                    "domain": prop_domain,
                    "diagnosis": prop_diag,
                    "conditions": conditions,
                    "explanation": prop_explanation,
                    "solution": prop_solution,
                    "author": prop_author
                }

                success, msg, prop_id = manager.submit_proposal(payload, kb)
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ Submission Rejected: {msg}")

    # -------------------------------------------------------------------------
    # TAB 2: PENDING REVIEW WORKFLOW
    # -------------------------------------------------------------------------
    with tab_pending:
        st.subheader("Proposals Awaiting Peer Review & Approval")
        pending_list = manager.get_proposals(status=STATUS_PENDING)

        if not pending_list:
            st.info("No proposals are currently pending review.")
        else:
            for prop in pending_list:
                with st.container():
                    st.markdown(f"""
                        <div class="rule-card" style="border-left: 4px solid #f59e0b;">
                            <div style="display:flex; justify-content:space-between;">
                                <b>{prop['rule_id']} &bull; {prop['diagnosis']}</b>
                                <span style="background-color:#fef3c7; color:#b45309; padding:0.2rem 0.5rem; border-radius:4px; font-size:0.75rem; font-weight:700;">
                                    PENDING REVIEW
                                </span>
                            </div>
                            <p style="font-size:0.85rem; color:#64748b; margin:0.3rem 0;">
                                <b>Proposal ID:</b> {prop['proposal_id']} | 
                                <b>Domain:</b> {prop['domain']} | 
                                <b>Author:</b> {prop['author']} ({prop['created_at']})
                            </p>
                            <p style="font-size:0.9rem; color:#334155;">{prop['explanation']}</p>
                            <b>Conditions:</b>
                            <ul>
                                {''.join([f"<li><code>{c['fact']}</code> == <b>{c['expected_value']}</b> (\"{c.get('description', '')}\")</li>" for c in prop['conditions']])}
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)

                    col_rev_name, col_rev_notes = st.columns([1, 2])
                    with col_rev_name:
                        approver_name = st.text_input("Reviewer Name:", placeholder="e.g. Chief Reviewer", key=f"rev_{prop['proposal_id']}")
                    with col_rev_notes:
                        review_notes = st.text_input("Review Notes / Justification:", placeholder="e.g. Verified valid edge-case", key=f"not_{prop['proposal_id']}")

                    col_appr, col_rej = st.columns(2)
                    with col_appr:
                        if st.button("✅ Approve & Integrate into KB", key=f"btn_app_{prop['proposal_id']}", type="primary"):
                            if not approver_name:
                                st.warning("Reviewer Name is required for audit trail.")
                            else:
                                app_succ, app_msg = manager.approve_proposal(
                                    proposal_id=prop['proposal_id'],
                                    approver_name=approver_name,
                                    review_notes=review_notes,
                                    kb=kb
                                )
                                if app_succ:
                                    st.success(app_msg)
                                    st.rerun()
                                else:
                                    st.error(app_msg)

                    with col_rej:
                        if st.button("❌ Reject Proposal", key=f"btn_rej_{prop['proposal_id']}"):
                            if not approver_name:
                                st.warning("Reviewer Name is required for audit trail.")
                            else:
                                rej_succ, rej_msg = manager.reject_proposal(
                                    proposal_id=prop['proposal_id'],
                                    reviewer_name=approver_name,
                                    rejection_reason=review_notes or "Did not meet domain specifications."
                                )
                                if rej_succ:
                                    st.info(rej_msg)
                                    st.rerun()
                                else:
                                    st.error(rej_msg)

    # -------------------------------------------------------------------------
    # TAB 3: PROPOSAL ARCHIVE & AUDIT TRAIL
    # -------------------------------------------------------------------------
    with tab_archive:
        st.subheader("Comprehensive Governance & Audit Log")
        all_props = manager.proposals
        if all_props:
            df_props = pd.DataFrame(all_props)
            cols_to_show = ["proposal_id", "rule_id", "domain", "diagnosis", "approval_status", "author", "reviewed_by", "created_at"]
            existing = [c for c in cols_to_show if c in df_props.columns]
            st.dataframe(df_props[existing], use_container_width=True, hide_index=True)
        else:
            st.info("No proposals logged yet.")
