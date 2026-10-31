"""Plotly visualization helpers for diagnostic evaluations, reasoning traces, and rule metrics."""

from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px

from config import DOMAINS, DOMAIN_ICONS


def create_accuracy_comparison_chart(benchmark_summary: Dict[str, Any]) -> go.Figure:
    """
    Creates a side-by-side bar chart comparing Baseline KB vs Updated KB accuracy
    across all four troubleshooting domains.
    """
    baseline_stats = benchmark_summary["baseline"]["domain_stats"]
    updated_stats = benchmark_summary["updated"]["domain_stats"]

    domain_labels = [f"{DOMAIN_ICONS.get(d, '')} {d.replace(' Troubleshooting', '')}" for d in DOMAINS]
    baseline_accs = [round(baseline_stats.get(d, {}).get("accuracy", 0.0), 1) for d in DOMAINS]
    updated_accs = [round(updated_stats.get(d, {}).get("accuracy", 0.0), 1) for d in DOMAINS]

    fig = go.Figure()

    # Baseline bars
    fig.add_trace(go.Bar(
        name="Baseline KB",
        x=domain_labels,
        y=baseline_accs,
        marker_color="#64748b",
        text=[f"{v}%" for v in baseline_accs],
        textposition="auto"
    ))

    # Updated bars
    fig.add_trace(go.Bar(
        name="Updated (Expert-Enriched) KB",
        x=domain_labels,
        y=updated_accs,
        marker_color="#2563eb",
        text=[f"{v}%" for v in updated_accs],
        textposition="auto"
    ))

    fig.update_layout(
        title="<b>Diagnostic Accuracy Benchmark: Baseline vs. Updated Knowledge Base</b>",
        barmode="group",
        yaxis=dict(title="Accuracy (%)", range=[0, 105]),
        xaxis=dict(title="Troubleshooting Domain"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(l=40, r=40, t=80, b=40),
        height=380
    )

    return fig


def create_hypothesis_coverage_chart(hypotheses: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """
    Creates a horizontal bar chart of candidate diagnostic hypotheses ranked by evidence coverage.
    """
    if not hypotheses:
        return None

    # Take top 6 hypotheses
    top_hypotheses = hypotheses[:6]
    labels = [h["diagnosis"][:35] + ("..." if len(h["diagnosis"]) > 35 else "") for h in top_hypotheses]
    coverages = [round(h["evidence_coverage"] * 100, 1) for h in top_hypotheses]

    # Invert for top-down display
    labels.reverse()
    coverages.reverse()

    colors = ["#22c55e" if c >= 100 else ("#f59e0b" if c >= 50 else "#94a3b8") for c in coverages]

    fig = go.Figure(go.Bar(
        x=coverages,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{c}%" for c in coverages],
        textposition="outside"
    ))

    fig.update_layout(
        title="<b>Candidate Hypotheses by Evidence Coverage</b>",
        xaxis=dict(title="Verified Evidence Coverage (%)", range=[0, 115]),
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
        margin=dict(l=10, r=30, t=40, b=30),
        height=280
    )

    return fig


def create_domain_distribution_chart(domain_counts: Dict[str, int]) -> go.Figure:
    """Creates a donut chart representing rule distribution across the 4 domains."""
    labels = [f"{DOMAIN_ICONS.get(d, '')} {d.replace(' Troubleshooting', '')}" for d in domain_counts.keys()]
    values = list(domain_counts.values())

    colors = ["#3b82f6", "#10b981", "#f97316", "#8b5cf6"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.45,
        marker=dict(colors=colors)
    )])

    fig.update_layout(
        title="<b>Knowledge Base Rule Distribution</b>",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )

    return fig
