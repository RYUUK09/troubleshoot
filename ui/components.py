"""Reusable UI components and custom CSS styling for the Streamlit interface."""

from typing import Any
import streamlit as st

def apply_custom_css():
    """Applies modern, polished CSS styling for university presentation standards."""
    st.markdown("""
        <style>
        /* General page layout */
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #64748b;
            margin-bottom: 1.5rem;
        }
        
        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 1.2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            text-align: center;
        }
        .metric-value {
            font-size: 1.9rem;
            font-weight: 700;
            color: #2563eb;
            margin-top: 0.2rem;
        }
        .metric-label {
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
        }

        /* Status Pills */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.025em;
        }
        .status-confirmed {
            background-color: #dcfce7;
            color: #15803d;
            border: 1px solid #86efac;
        }
        .status-possible {
            background-color: #fef3c7;
            color: #b45309;
            border: 1px solid #fde68a;
        }
        .status-ruled-out {
            background-color: #fee2e2;
            color: #b91c1c;
            border: 1px solid #fca5a5;
        }
        .status-insufficient {
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
        }
        .status-conflict {
            background-color: #fae8ff;
            color: #86198f;
            border: 1px solid #f0abfc;
        }

        /* Card container */
        .rule-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.8rem;
            transition: all 0.2s ease;
        }
        .rule-card:hover {
            border-color: #93c5fd;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07);
        }

        /* Question Box */
        .question-box {
            background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%);
            border: 1px solid #bae6fd;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value: Any, subtext: str = ""):
    """Renders a styled metric card."""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {"<div style='font-size:0.75rem; color:#94a3b8; margin-top:0.3rem;'>" + subtext + "</div>" if subtext else ""}
        </div>
    """, unsafe_allow_html=True)


def get_status_badge_html(status: str) -> str:
    """Generates HTML badge for diagnostic statuses."""
    css_class = "status-insufficient"
    if status == "CONFIRMED":
        css_class = "status-confirmed"
    elif status == "POSSIBLE":
        css_class = "status-possible"
    elif status == "RULED_OUT":
        css_class = "status-ruled-out"
    elif status == "CONFLICTING_EVIDENCE":
        css_class = "status-conflict"

    return f'<span class="status-badge {css_class}">{status}</span>'
