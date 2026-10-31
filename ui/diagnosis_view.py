"""Diagnosis View: Interactive step-by-step diagnostic reasoning session."""

import streamlit as st
from datetime import datetime

from config import (
    DOMAINS,
    DOMAIN_ICONS,
    FACT_YES,
    FACT_NO,
    FACT_UNKNOWN,
    STATUS_CONFIRMED,
    STATUS_POSSIBLE,
    STATUS_RULED_OUT,
    STATUS_INSUFFICIENT_EVIDENCE,
    STATUS_CONFLICTING_EVIDENCE,
    STATUS_NO_MATCH,
)
from src.knowledge_base import KnowledgeBase
from src.inference_engine import BackwardChainingEngine
from src.question_selector import MinSplitQuestionSelector
from src.conflict_detector import ConflictDetector
from src.history_manager import DiagnosisHistoryManager
from src.visualizer import create_hypothesis_coverage_chart
from ui.components import get_status_badge_html


def render_diagnosis_view(kb: KnowledgeBase):
    st.markdown('<div class="main-header">🔍 Interactive Troubleshooting Diagnosis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Goal-driven backward chaining inference with heuristic question selection</div>', unsafe_allow_html=True)

    # Initialize Session State
    if "diag_domain" not in st.session_state:
        st.session_state.diag_domain = DOMAINS[0]
    if "user_facts" not in st.session_state:
        st.session_state.user_facts = {}
    if "session_complete" not in st.session_state:
        st.session_state.session_complete = False

    engine = BackwardChainingEngine(kb)
    selector = MinSplitQuestionSelector(kb, engine)
    history_mgr = DiagnosisHistoryManager()

    # Domain Selection Bar
    col_domain, col_reset = st.columns([4, 1])
    with col_domain:
        selected_domain = st.selectbox(
            "Select Diagnostic Domain:",
            options=DOMAINS,
            index=DOMAINS.index(st.session_state.diag_domain),
            key="domain_selector"
        )
        if selected_domain != st.session_state.diag_domain:
            st.session_state.diag_domain = selected_domain
            st.session_state.user_facts = {}
            st.session_state.session_complete = False
            st.rerun()

    with col_reset:
        st.write("")
        st.write("")
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.user_facts = {}
            st.session_state.session_complete = False
            st.rerun()

    domain = st.session_state.diag_domain
    user_facts = st.session_state.user_facts

    # Run inference on current facts
    current_result = engine.diagnose_domain(domain, user_facts)

    # Check if a diagnosis is already confirmed or questions exhausted
    next_question = selector.select_next_question(domain, user_facts)
    all_observable = kb.get_all_observable_conditions(domain)
    total_observable_count = len(all_observable)
    answered_count = len(user_facts)

    # Progress bar
    progress_val = min(1.0, answered_count / max(1, total_observable_count))
    st.progress(progress_val, text=f"Diagnostic Exploration Progress: {answered_count}/{total_observable_count} symptoms evaluated")

    # If diagnosis confirmed OR no more questions -> Session Complete
    if current_result.status == STATUS_CONFIRMED or next_question is None:
        st.session_state.session_complete = True

    # ---------------------------------------------------------
    # ACTIVE QUESTION FLOW (IF NOT COMPLETED)
    # ---------------------------------------------------------
    if not st.session_state.session_complete and next_question is not None:
        col_q, col_side = st.columns([3, 2])

        with col_q:
            st.markdown(f"""
                <div class="question-box">
                    <span style="font-size: 0.85rem; font-weight: 700; color: #0284c7; text-transform: uppercase;">
                        Question #{answered_count + 1} &bull; Min-Split Score: {next_question.min_split_score}
                    </span>
                    <h3 style="margin-top: 0.4rem; color: #0f172a;">{next_question.description}</h3>
                    <p style="font-size: 0.85rem; color: #475569; margin-bottom: 0;">
                        <b>Internal Fact ID:</b> <code>{next_question.fact}</code><br>
                        <b>Active Rules Impacted:</b> {next_question.total_rules_impacted} 
                        (Requires YES: {next_question.yes_count} | Requires NO: {next_question.no_count})
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Three Answer Options: YES, NO, NOT SURE / SKIP
            col_yes, col_no, col_skip = st.columns(3)
            with col_yes:
                if st.button("✅ Yes (Verified True)", use_container_width=True, type="primary"):
                    st.session_state.user_facts[next_question.fact] = FACT_YES
                    st.rerun()

            with col_no:
                if st.button("❌ No (Verified False)", use_container_width=True):
                    st.session_state.user_facts[next_question.fact] = FACT_NO
                    st.rerun()

            with col_skip:
                if st.button("❓ Not Sure / Skip", use_container_width=True):
                    st.session_state.user_facts[next_question.fact] = FACT_UNKNOWN
                    st.rerun()

            with st.expander("ℹ️ Why this question was chosen (Min-Split Heuristic)"):
                st.markdown(f"""
                The **Information-Gain Min-Split Heuristic** calculates:
                $$\\text{{Score}} = \\min(\\text{{yes\\_count}}, \\text{{no\\_count}}) = \\min({next_question.yes_count}, {next_question.no_count}) = {next_question.min_split_score}$$
                - Rules expecting **Yes**: `{next_question.yes_count}`
                - Rules expecting **No**: `{next_question.no_count}`
                
                This question divides the remaining hypotheses as evenly as possible, 
                minimizing the expected number of inquiries needed to reach a conclusion.
                """)

        with col_side:
            st.subheader("Candidate Hypotheses")
            if current_result.possible_hypotheses:
                possible_dicts = [h.to_dict() for h in current_result.possible_hypotheses]
                chart = create_hypothesis_coverage_chart(possible_dicts)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)

                st.write("**Top Leading Hypothesis:**")
                top = current_result.possible_hypotheses[0]
                st.info(f"**{top.diagnosis}**\n\nEvidence Coverage: **{top.coverage_display}**")
            else:
                st.write("Evaluating initial symptoms...")

    # ---------------------------------------------------------
    # FINAL DIAGNOSTIC RESULTS
    # ---------------------------------------------------------
    else:
        st.markdown("---")
        # Final Diagnosis Banner
        status_badge = get_status_badge_html(current_result.status)

        if current_result.status == STATUS_CONFIRMED:
            banner_color = "#f0fdf4"
            border_color = "#86efac"
            header_icon = "🎉"
            title_text = "Diagnostic Fault Confirmed"
        elif current_result.status == STATUS_INSUFFICIENT_EVIDENCE:
            banner_color = "#f8fafc"
            border_color = "#cbd5e1"
            header_icon = "⚠️"
            title_text = "Inconclusive: Insufficient Evidence"
        elif current_result.status == STATUS_CONFLICTING_EVIDENCE:
            banner_color = "#fdf4ff"
            border_color = "#f0abfc"
            header_icon = "⚡"
            title_text = "Logical Contradiction Detected"
        else:
            banner_color = "#fffbeb"
            border_color = "#fde68a"
            header_icon = "🔍"
            title_text = "Differential Hypotheses Remaining"

        st.markdown(f"""
            <div style="background-color: {banner_color}; border: 2px solid {border_color}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #0f172a;">{header_icon} {title_text}</h3>
                    {status_badge}
                </div>
                <h2 style="color: #1e3a8a; margin-top: 0.5rem; margin-bottom: 0.3rem;">{current_result.primary_diagnosis}</h2>
                <p style="font-size: 0.95rem; color: #334155;"><b>Domain:</b> {domain}</p>
            </div>
        """, unsafe_allow_html=True)

        # Recommended Actionable Solution
        if current_result.primary_solution:
            st.subheader("💡 Recommended Solution & Safe Remediation")
            st.success(current_result.primary_solution)

        # Tabbed Details: Supporting Evidence, Ruled Out, Full Trace
        tab_evidence, tab_ruled_out, tab_trace = st.tabs([
            "📋 Evidence & Hypotheses",
            f"🚫 Ruled-Out Diagnoses ({len(current_result.ruled_out_hypotheses)})",
            "🔬 Backward Chaining Trace"
        ])

        with tab_evidence:
            col_supp, col_miss = st.columns(2)
            with col_supp:
                st.markdown("#### ✅ Confirmed Evidence")
                if current_result.confirmed_hypotheses:
                    for h in current_result.confirmed_hypotheses:
                        st.markdown(f"**Rule `{h.rule_id}`:** {h.coverage_display}")
                        for cond in h.satisfied_conditions:
                            st.write(f"- {cond.description or cond.fact} = **{cond.expected_value}**")
                elif current_result.possible_hypotheses:
                    top_h = current_result.possible_hypotheses[0]
                    st.markdown(f"**Leading Hypothesis (`{top_h.rule_id}`):** {top_h.coverage_display}")
                    for cond in top_h.satisfied_conditions:
                        st.write(f"- {cond.description or cond.fact} = **{cond.expected_value}**")
                else:
                    st.write("No positive symptoms confirmed.")

            with col_miss:
                st.markdown("#### ⏳ Missing or Skipped Conditions")
                if current_result.possible_hypotheses:
                    top_h = current_result.possible_hypotheses[0]
                    if top_h.missing_conditions:
                        for cond in top_h.missing_conditions:
                            st.write(f"- {cond.description or cond.fact} *(Required: {cond.expected_value})*")
                    else:
                        st.write("None missing.")
                else:
                    st.write("No active pending hypotheses.")

        with tab_ruled_out:
            st.markdown("#### Eliminated Hypotheses (Ruled Out by Contradiction)")
            ruled_out_summary = ConflictDetector.get_ruled_out_summary(current_result)
            if ruled_out_summary:
                for item in ruled_out_summary:
                    with st.container():
                        st.markdown(f"""
                            <div class="rule-card" style="border-left: 4px solid #ef4444;">
                                <div style="display:flex; justify-content:space-between;">
                                    <b>{item['diagnosis']}</b>
                                    <code>{item['rule_id']}</code>
                                </div>
                                <p style="font-size:0.85rem; color:#475569; margin: 0.3rem 0;">
                                    <b>Contradicted Condition:</b> {item['condition_description']}<br>
                                    <b>Expected:</b> <code>{item['expected_value']}</code> | 
                                    <b>User's Answer:</b> <code>{item['actual_value']}</code>
                                </p>
                                <span style="font-size:0.8rem; color:#dc2626;">{item['elimination_reason']}</span>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No candidate hypotheses were ruled out during this session.")

        with tab_trace:
            st.markdown("#### Complete Multi-Level Backward Chaining Reasoning Log")
            st.text("\n".join(current_result.full_trace))

        # Save to History
        st.markdown("---")
        col_notes, col_save = st.columns([3, 1])
        with col_notes:
            notes = st.text_input("Session Notes (Optional):", placeholder="e.g. Demonstration Case #3 during Viva")
        with col_save:
            st.write("")
            st.write("")
            if st.button("💾 Save Session to History", use_container_width=True):
                current_result.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history_mgr.log_session(current_result, user_notes=notes)
                st.success("Session saved successfully to persistent history!")
