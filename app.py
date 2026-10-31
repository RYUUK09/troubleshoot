"""AI-Based Intelligent Troubleshooting Expert System
Streamlit Main Application Entry Point
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    VERSION,
    DOMAINS,
    ACTIVE_KB_PATH,
    BASELINE_KB_PATH,
)
from src.knowledge_base import KnowledgeBase
from ui.components import apply_custom_css
from ui.dashboard_view import render_dashboard_view
from ui.diagnosis_view import render_diagnosis_view
from ui.kb_explorer_view import render_kb_explorer_view
from ui.expert_review_view import render_expert_review_view
from ui.history_view import render_history_view
from ui.evaluation_view import render_evaluation_view
from ui.about_view import render_about_view


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global CSS styling
apply_custom_css()

# Initialize Knowledge Base in session state
if "kb" not in st.session_state:
    st.session_state.kb = KnowledgeBase(ACTIVE_KB_PATH)

kb: KnowledgeBase = st.session_state.kb


# Sidebar Navigation
st.sidebar.markdown(f"## 🧠 Expert System v{VERSION}")
st.sidebar.caption("Intelligent Multi-Domain Diagnostics")

menu_choice = st.sidebar.radio(
    "Navigation Menu",
    options=[
        "📊 Dashboard",
        "🔍 Diagnosis",
        "📚 Knowledge Base Explorer",
        "🛡️ Expert Review",
        "📜 Diagnosis History",
        "📈 Evaluation Benchmark",
        "🎓 About & Viva Guide",
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ System Controls")
st.sidebar.info(f"**Active Rules:** {len(kb.rules)}\n\n**KB Version:** {kb.version}")

if st.sidebar.button("🔄 Reset KB to Factory Baseline"):
    kb.reset_to_baseline()
    st.sidebar.success("Active KB successfully restored to factory baseline.")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("BTech Final Year Project &bull; 100% Offline AI")


# Main Router
if menu_choice == "📊 Dashboard":
    render_dashboard_view(kb)

elif menu_choice == "🔍 Diagnosis":
    render_diagnosis_view(kb)

elif menu_choice == "📚 Knowledge Base Explorer":
    render_kb_explorer_view(kb)

elif menu_choice == "🛡️ Expert Review":
    render_expert_review_view(kb)

elif menu_choice == "📜 Diagnosis History":
    render_history_view()

elif menu_choice == "📈 Evaluation Benchmark":
    render_evaluation_view(kb)

elif menu_choice == "🎓 About & Viva Guide":
    render_about_view()
